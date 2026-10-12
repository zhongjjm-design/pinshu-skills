#!/usr/bin/env python3
"""Legacy opt-in framing utility; new article screenshots are unframed by default."""
from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path

from PIL import Image, ImageChops, ImageDraw, ImageFilter


def frame(source: Path, out: Path, width=1080, padding=14, radius=30) -> Path:
    if width < 300 or padding < 1 or radius < 0 or 2 * (padding + radius) >= width:
        raise ValueError("Invalid frame dimensions")
    source = source.resolve()
    original_hash = hashlib.sha256(source.read_bytes()).hexdigest()
    with Image.open(source) as opened:
        if getattr(opened, "n_frames", 1) != 1:
            raise ValueError("Expected one screenshot, not an animation")
        original = opened.convert("RGBA")
    # A white safety inset protects source corners instead of masking away evidence.
    inset = math.ceil(radius * (1 - 1 / math.sqrt(2))) + 1 if radius else 0
    inner_width = width - 2 * (padding + inset)
    resized = original.resize((inner_width, max(1, round(original.height * inner_width / original.width))), Image.Resampling.LANCZOS)
    white = Image.new("RGBA", resized.size, "white")
    resized = Image.alpha_composite(white, resized)
    card_size = (resized.width + 2 * inset, resized.height + 2 * inset)
    height = card_size[1] + 2 * padding
    # Low saturation four-corner gradient sampled from the Oct 10 candidate output.
    colors = [(177, 199, 203), (196, 197, 199), (196, 212, 208), (217, 188, 172)]
    small = Image.new("RGB", (64, 64))
    pixels = small.load()
    for y in range(64):
        for x in range(64):
            u, v = x / 63, y / 63
            pixels[x, y] = tuple(round(colors[0][c]*(1-u)*(1-v)+colors[1][c]*u*(1-v)
                                      +colors[2][c]*(1-u)*v+colors[3][c]*u*v) for c in range(3))
    canvas = small.resize((width, height), Image.Resampling.BICUBIC).convert("RGBA")
    box = (padding, padding, width-padding-1, height-padding-1)
    mask = Image.new("L", canvas.size, 0)
    ImageDraw.Draw(mask).rounded_rectangle(box, radius=radius, fill=255)
    shadow_mask = Image.new("L", canvas.size, 0)
    ImageDraw.Draw(shadow_mask).rounded_rectangle((box[0], box[1]+3, box[2], box[3]+3), radius=radius, fill=36)
    shadow_mask = shadow_mask.filter(ImageFilter.GaussianBlur(6))
    shadow = Image.new("RGBA", canvas.size, (35, 45, 50, 0))
    shadow.putalpha(shadow_mask)
    canvas = Image.alpha_composite(canvas, shadow)
    card = Image.new("RGBA", canvas.size, "white")
    content_box = (padding+inset, padding+inset,
                   padding+inset+resized.width, padding+inset+resized.height)
    card.paste(resized, content_box[:2])
    canvas = Image.composite(card, canvas, mask).convert("RGB")
    if ImageChops.difference(canvas.crop(content_box), resized.convert("RGB")).getbbox():
        raise ValueError("Frame masked source content; no output written")
    if hashlib.sha256(source.read_bytes()).hexdigest() != original_hash:
        raise ValueError("Source changed while framing")
    out = out.resolve()
    out.mkdir(parents=True, exist_ok=False)
    final = out / "截图成图.png"
    canvas.save(final)
    (out / "边框记录.json").write_text(json.dumps({
        "preset": "thin-grayblue-apricot-candidate", "source": str(source),
        "source_sha256": original_hash, "output": str(final),
        "output_sha256": hashlib.sha256(final.read_bytes()).hexdigest(),
        "width": width, "height": height, "padding": padding, "radius": radius,
        "source_content_box": content_box, "source_resized_to": resized.size,
        "crop": None, "resized_content_pixel_difference_ae": 0,
        "frame_baked": True, "human_acceptance": "待看图确认；不是 CleanShot 等价复刻",
    }, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return final


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="旧任务/明确指定的细框工具；新文章截图默认不调用，交由排版统一加框")
    parser.add_argument("--source", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--width", type=int, default=1080)
    parser.add_argument("--padding", type=int, default=14)
    parser.add_argument("--radius", type=int, default=30)
    args = parser.parse_args()
    print(frame(args.source, args.output_dir, args.width, args.padding, args.radius))
