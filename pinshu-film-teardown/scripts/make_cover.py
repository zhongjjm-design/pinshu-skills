#!/usr/bin/env python3
"""Covers from one strong frame of the original film: a horizontal 16:9 cover and a vertical 3:4 cover (WeChat Channels
crops profile tiles to 3:4).

Rules learned the hard way: a text-only cover over a blurred background has no pull; use a frame with a face and an
emotion, bright; put a hook (a number or a question) in empty space beside the face, never over it; bold type (thin type
does not hold against a photo); crop each aspect ratio separately around the face. The script refuses to write a cover
whose text box overlaps the face box you give it.

Spec:
COVER = {
  "frame": 9.8,                      # second in the original film (wide/assets/tvc.mp4)
  "face": [900, 220, 1360, 700],     # face box in the 1920x1080 frame (x0, y0, x1, y1), forehead to chin: look and measure
  "kicker": "...",                   # small red label
  "lines": [[["8...", "white"]], [["...", "white"], ["...", "yellow"]]],   # each line: [text, colour] parts
  "sizes": [140, 140, 104],          # font size per line (horizontal cover)
  "byline": "...",                   # optional, horizontal cover only
  "h": {"zoom": 1.15, "x": 0.0, "y": 0.0, "text_side": "left"},          # horizontal: zoom, crop position 0..1, text side
  "v": {"x": 0.4, "sizes": [150, 150, 118]},                              # vertical 3:4: crop position 0..1, text at the bottom
}
Usage: python3 make_cover.py   -> wide/renders/cover_16x9.png, wide/renders/cover_3x4.png
"""
import os
import subprocess
import sys

from PIL import Image, ImageDraw, ImageFont

import common as C

H = C.project_dir(); SPEC = C.load_spec(H); CV = SPEC.COVER; FF = C.ffmpeg()
OUT = f"{H}/wide/renders"; os.makedirs(OUT, exist_ok=True)
COLORS = {"white": (255, 255, 255), "yellow": (255, 214, 64), "red": (232, 50, 44)}
SANS = next((p for p in (os.environ.get("PINSHU_COVER_FONT"), f"{H}/wide/assets/fonts/HiraginoSansGB.ttc", "/System/Library/Fonts/Hiragino Sans GB.ttc") if p and os.path.isfile(p)), None)
if not SANS: sys.exit("No bold CJK sans font found. Set PINSHU_COVER_FONT=/path/to/font (Hiragino Sans GB W6 on macOS).")


def F(size, bold=True):
    if SANS.endswith(".ttc"):  # Hiragino Sans GB: index 2 is W6 (bold), 0 is W3
        return ImageFont.truetype(SANS, size, index=2 if bold else 0)
    return ImageFont.truetype(SANS, size)


src_png = f"{OUT}/_cover_src.png"
subprocess.run([FF, "-v", "error", "-y", "-ss", str(CV["frame"]), "-i", f"{H}/wide/assets/tvc.mp4", "-frames:v", "1", src_png], check=True)
SRC = Image.open(src_png).convert("RGB"); os.remove(src_png)


def fit(zoom, W, Hh, fx, fy):
    """Scale the frame to cover W x Hh (times zoom), crop at fx/fy (0..1); returns the image and a mapper for frame coords."""
    s = max(W / SRC.width, Hh / SRC.height) * zoom
    im = SRC.resize((round(SRC.width * s), round(SRC.height * s)), Image.LANCZOS)
    x = round((im.width - W) * fx); y = round((im.height - Hh) * fy)
    return im.crop((x, y, x + W, y + Hh)), (lambda bx: (bx[0] * s - x, bx[1] * s - y, bx[2] * s - x, bx[3] * s - y))


def shade(im, side, strength=0.88, span=0.55):
    W, Hh = im.size; g = Image.new("L", (W, Hh), 0); d = ImageDraw.Draw(g)
    n = int((W if side in ("left", "right") else Hh) * span)
    for k in range(n):
        a = int(255 * strength * (1 - k / n) ** 1.3)
        if side == "left": d.line([(k, 0), (k, Hh)], fill=a)
        elif side == "right": d.line([(W - 1 - k, 0), (W - 1 - k, Hh)], fill=a)
        else: d.line([(0, Hh - 1 - k), (W, Hh - 1 - k)], fill=a)
    return Image.composite(Image.new("RGB", (W, Hh)), im, g)


def block_height(sizes, byline=False):
    return max(40, sizes[0] // 3) + 44 + sum(int(s * 1.2) for s in sizes) - int(sizes[-1] * 0.2) + (80 if byline else 0)


def draw_text(im, x0, y0, sizes, byline=None):
    """Draw kicker, lines and byline; return one box per line (a whole-block box would flag empty corners)."""
    d = ImageDraw.Draw(im); fk = F(max(40, sizes[0] // 3)); boxes = []
    w = d.textlength(CV["kicker"], font=fk); d.rectangle([x0, y0, x0 + w + 44, y0 + fk.size + 28], fill=COLORS["red"])
    d.text((x0 + 22, y0 + 12), CV["kicker"], font=fk, fill=COLORS["white"]); boxes.append((x0, y0, x0 + w + 44, y0 + fk.size + 28))
    y = y0 + fk.size + 44
    for parts, size in zip(CV["lines"], sizes):
        f = F(size); x = x0
        for text, color in parts:
            d.text((x, y), text, font=f, fill=COLORS.get(color, COLORS["white"]), stroke_width=2, stroke_fill=(0, 0, 0)); x += d.textlength(text, font=f)
        boxes.append((x0, y, x, y + size)); y += int(size * 1.2)
    if byline:
        f = F(40, False); d.text((x0, y + 20), byline, font=f, fill=(235, 235, 235)); boxes.append((x0, y + 20, x0 + d.textlength(byline, font=f), y + 60))
    return boxes


def hits_face(box, face):
    """True when the rectangle touches the ellipse inscribed in the face box (faces are round; box corners are not face)."""
    cx, cy = (face[0] + face[2]) / 2, (face[1] + face[3]) / 2; rx, ry = (face[2] - face[0]) / 2, (face[3] - face[1]) / 2
    nx = min(max(cx, box[0]), box[2]); ny = min(max(cy, box[1]), box[3])  # nearest point of the box to the face centre
    return ((nx - cx) / rx) ** 2 + ((ny - cy) / ry) ** 2 < 1


def make(kind, W, Hh):
    o = CV.get(kind, {})
    if kind == "h":
        im, mapf = fit(o.get("zoom", 1.0), W, Hh, o.get("x", 0.5), o.get("y", 0.5)); side = o.get("text_side", "left")
        im = shade(im, side); sizes = CV["sizes"]
        est_w = max(sum(len(t) for t, _ in parts) * sz for parts, sz in zip(CV["lines"], sizes))
        x0 = 90 if side == "left" else W - 90 - est_w
        boxes = draw_text(im, x0, (Hh - block_height(sizes, bool(CV.get("byline")))) // 2, sizes, CV.get("byline"))
    else:
        im, mapf = fit(o.get("zoom", 1.0), W, Hh, o.get("x", 0.5), o.get("y", 0.0))
        im = shade(im, "bottom", 0.9, 0.55); sizes = o.get("sizes", CV["sizes"])
        boxes = draw_text(im, 70, Hh - 110 - block_height(sizes), sizes)
    face = tuple(round(v) for v in mapf(CV["face"]))
    print(f"{kind}: text lines {[tuple(round(v) for v in b) for b in boxes]}, face {face}")
    if any(hits_face(b, face) for b in boxes): sys.exit(f"{kind}: the text covers the face - change text_side / crop position / zoom / sizes")
    return im


make("h", 1920, 1080).save(f"{OUT}/cover_16x9.png")
make("v", 1080, 1440).save(f"{OUT}/cover_3x4.png")
print("ok", f"{OUT}/cover_16x9.png", f"{OUT}/cover_3x4.png", "- look at both before publishing")
