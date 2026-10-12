#!/usr/bin/env python3
"""Read-only article checks, local lightweight preview, and stage timing.

Consumes already rendered HTML; never rewrites the manuscript or publish images.
Text comparison supports plain paragraphs, headings, lists and inline links/bold.
Complex Markdown must be reviewed separately, never silently marked PASS.
Requires ImageMagick only for preview raster transforms and ink-bound estimates.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import fcntl
import hashlib
import html
from html.parser import HTMLParser
import json
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile
from urllib.parse import unquote, urlparse


class CheckError(ValueError):
    pass


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def normalized(text):
    return re.sub(r"\s+", " ", text).strip()


def manuscript_blocks(text):
    if text.startswith("---\n"):
        _, _, text = text.partition("\n---\n")
    blocks = []
    for chunk in re.split(r"\n\s*\n", text.strip()):
        if chunk.strip() in {"---", "***", "___"} or re.match(r"^#\s", chunk):
            continue  # H1 belongs to the cover/title, not article body.
        if re.search(r"^\s*(?:```|~~~|>|\||!\[)", chunk, re.M):
            raise CheckError("Unsupported Markdown block; use an explicit source-faithful renderer/check.")
        lines = chunk.splitlines()
        list_block = all(re.match(r"^\s*(?:[-*+] |\d+[.)] )", line) for line in lines)
        for part in lines if list_block else [chunk]:
            part = re.sub(r"^#{2,6}\s+|^\s*(?:[-*+] |\d+[.)] )", "", part)
            part = re.sub(r"\[([^\]]+)\]\([^\n)]+\)", r"\1", part)
            part = re.sub(r"\*\*([^*]+)\*\*|__([^_]+)__", lambda m: m[1] or m[2], part)
            blocks.append(normalized(part))
    return blocks


class ArticleHTML(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.blocks, self.images, self.links = [], [], []
        self.active, self.text, self.in_body = None, [], False

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag == "body":
            self.in_body = True
        if tag in {"script", "iframe", "object", "embed"}:
            raise CheckError(f"Active content is not supported: {tag}")
        if tag in {"p", "h2", "h3", "h4", "li"} and self.in_body:
            if self.active:
                raise CheckError("Nested text blocks require separate verification.")
            self.active, self.text = tag, []
        if tag == "img":
            self.images.append(a.get("src", ""))
        if tag == "a":
            self.links.append(a.get("href", ""))
        if tag == "br" and self.active:
            self.text.append(" ")

    def handle_data(self, data):
        if self.active:
            self.text.append(data)

    def handle_endtag(self, tag):
        if tag == self.active:
            text = normalized("".join(self.text))
            if text:
                self.blocks.append(text)
            self.active = None
        if tag == "body":
            self.in_body = False


def parse_html(text):
    parser = ArticleHTML()
    parser.feed(text)
    return parser


def command(*args):
    return subprocess.check_output(args, text=True, stderr=subprocess.PIPE).strip()


def build(args):
    source, rendered = args.source.resolve(), args.html.resolve()
    before = {str(p): digest(p) for p in [source, rendered]}
    raw = rendered.read_text(encoding="utf-8")
    parsed = parse_html(raw)
    expected = manuscript_blocks(source.read_text(encoding="utf-8"))
    if expected != parsed.blocks:
        first = next((i for i, (a, b) in enumerate(zip(expected, parsed.blocks)) if a != b), min(len(expected), len(parsed.blocks)))
        raise CheckError(f"Body/source mismatch at block {first + 1}; no preview written.")
    if not parsed.images:
        raise CheckError("No body images found.")
    magick = shutil.which("magick")
    if not magick:
        raise CheckError("ImageMagick magick is required.")
    output = args.output_dir.resolve()
    if output.exists():
        raise CheckError("Refusing to overwrite an existing preview directory.")
    input_images = []
    for src in dict.fromkeys(parsed.images):
        url = urlparse(src)
        if url.scheme or url.netloc or not src or url.query or url.fragment:
            raise CheckError("Preview requires local image paths, no Base64/remote resources.")
        path = (rendered.parent / unquote(url.path)).resolve()
        if not path.is_file():
            raise CheckError(f"Missing image: {path}")
        input_images.append((src, path, digest(path)))
    output.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(dir=output.parent, prefix=".article-preview-") as temp:
        staging = Path(temp)
        (staging / "images").mkdir()
        metrics, replacements = [], {}
        for i, (src, path, sha) in enumerate(input_images, 1):
            w, h = map(int, command(magick, "identify", "-format", "%w %h", str(path)).split())
            jpg = staging / "images" / f"{i:02d}.jpg"
            command(magick, str(path), "-auto-orient", "-resize", f"{args.width}x>", "-background", "white", "-alpha", "remove", "-strip", "-quality", "82", str(jpg))
            pw, ph = map(int, command(magick, "identify", "-format", "%w %h", str(jpg)).split())
            # Detect dark ink on near-white paper. This is not object occupancy or aesthetic QA.
            bbox = command(magick, str(path), "-background", "white", "-alpha", "remove", "-colorspace", "gray", "-threshold", "95%", "-format", "%@", "info:")
            match = re.fullmatch(r"(\d+)x(\d+)\+(\d+)\+(\d+)", bbox)
            ink = None if not match else dict(zip(["width", "height", "left", "top"], map(int, match.groups())))
            metrics.append({"source": str(path), "sha256": sha, "source_size": [w, h], "preview_size": [pw, ph], "preview_bytes": jpg.stat().st_size, "dark_ink_bounds_estimate": ink, "top_blank_ratio_estimate": None if not ink else round(ink["top"] / h, 4), "measurement_scope": "near-white paper only; no automatic crop or aesthetic pass", "human_visual_review": "pending"})
            replacements[src] = (f"images/{i:02d}.jpg", pw, ph)

        image_index = 0
        def replace_tag(match):
            nonlocal image_index
            image_index += 1
            tag = match[0]
            one = parse_html(tag)
            src = one.images[0]
            new, w, h = replacements[src]
            tag = re.sub(r"\s(?:src|width|height|loading|decoding)\s*=\s*(?:\"[^\"]*\"|'[^']*'|[^\s>]+)", "", tag, flags=re.I)
            tag = tag.rstrip(" >/")
            loading = "eager" if image_index == 1 else "lazy"
            decoding = "sync" if image_index == 1 else "async"
            return f'{tag} src="{html.escape(new, quote=True)}" width="{w}" height="{h}" loading="{loading}" decoding="{decoding}">'

        preview = re.sub(r"<img\b[^>]*>", replace_tag, raw, flags=re.I)
        after = parse_html(preview)
        if after.blocks != parsed.blocks or after.links != parsed.links:
            raise CheckError("Preview changed visible text or links.")
        for p in [source, rendered]:
            if before[str(p)] != digest(p):
                raise CheckError("Input changed during preview build.")
        if any(digest(path) != sha for _, path, sha in input_images):
            raise CheckError("Image changed during preview build.")
        (staging / "preview.html").write_text(preview, encoding="utf-8")
        report = {"status": "TEXT_AND_RESOURCE_CHECK_PASS", "source_sha256": before[str(source)], "rendered_html": str(rendered), "rendered_sha256": before[str(rendered)], "visible_blocks": len(expected), "punctuation_unchanged": True, "links_unchanged": True, "inputs_unchanged": True, "body_image_count": len(parsed.images), "unique_body_image_count": len(input_images), "images": metrics, "preview_bytes_total": len(preview.encode()) + sum(x["preview_bytes"] for x in metrics), "first_image_loading": "eager; decoding sync", "remaining_image_loading": "lazy; decoding async", "browser_open_scroll_check": "pending", "design_and_user_acceptance": "pending", "backend_action": "none"}
        (staging / "preview-report.json").write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n")
        staging.rename(output)
    print(json.dumps({"preview": str(output / "preview.html"), "report": str(output / "preview-report.json"), "blocks": len(expected), "images": len(parsed.images)}, ensure_ascii=False))


def timing(args):
    stages = {"design", "generation", "review", "revision", "user-wait"}
    if args.stage not in stages:
        raise CheckError("Unknown timing stage.")
    args.log.parent.mkdir(parents=True, exist_ok=True)
    with args.log.open("a+", encoding="utf-8") as log:
        fcntl.flock(log, fcntl.LOCK_EX)
        log.seek(0)
        rows = [json.loads(line) for line in log if line.strip()]
        matching = [r for r in rows if r["id"] == args.id]
        if args.action == "start" and matching:
            raise CheckError("Timing id already exists; use a new id.")
        if args.action == "end" and (len(matching) != 1 or matching[0]["action"] != "start" or matching[0]["stage"] != args.stage):
            raise CheckError("No matching open stage; no timing event written.")
        now = datetime.now(timezone.utc)
        event = {"id": args.id, "stage": args.stage, "action": args.action, "at": now.isoformat(), "note": args.note}
        if args.action == "end":
            event["seconds"] = round((now - datetime.fromisoformat(matching[0]["at"])).total_seconds(), 3)
        log.write(json.dumps(event, ensure_ascii=False) + "\n")
        print(json.dumps(event, ensure_ascii=False))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    p = sub.add_parser("build")
    p.add_argument("--source", required=True, type=Path)
    p.add_argument("--html", required=True, type=Path)
    p.add_argument("--output-dir", required=True, type=Path)
    p.add_argument("--width", type=int, default=1000)
    p = sub.add_parser("time")
    p.add_argument("action", choices=["start", "end"])
    p.add_argument("--id", required=True)
    p.add_argument("--stage", required=True)
    p.add_argument("--log", required=True, type=Path)
    p.add_argument("--note", default="")
    args = parser.parse_args()
    try:
        if args.command == "build":
            if args.width < 375 or args.width > 1600:
                raise CheckError("Preview width must be between 375 and 1600.")
            build(args)
        else:
            timing(args)
    except (CheckError, OSError, subprocess.CalledProcessError, json.JSONDecodeError) as exc:
        print(f"FAIL: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
