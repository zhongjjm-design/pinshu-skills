#!/usr/bin/env python3
"""Read-only article checks, local lightweight preview, and stage timing.

Consumes already rendered HTML; never rewrites the manuscript or publish images.
Text comparison uses the sibling layout's real Markdown parser and checks the
renderer's semantic blocks, including tables and prompt cards, before previewing.
Requires ImageMagick only for preview raster transforms and ink-bound estimates.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
from portable import lock, ensure_utf8_mode
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


def _source_blocks(source, layout_skill=None):
    # One accepted Markdown language for handoff, layout and final comparison.
    # Keep text callers compatible, but use the real source Path in the pipeline.
    from prepare_article_handoff import load_layout
    layout = load_layout(layout_skill or Path(__file__).resolve().parents[2] / "pinshu-wechat-layout")
    if isinstance(source, str):
        text = source
        class TextSource:
            def read_bytes(self):
                return text.encode("utf-8")

            def read_text(self, encoding="utf-8"):
                return self.read_bytes().decode(encoding)
        source = TextSource()
    try:
        return layout, layout.parse_markdown(source)[1]
    except ValueError as exc:
        raise CheckError(str(exc)) from exc


def manuscript_blocks(source, layout_skill=None):
    layout, blocks = _source_blocks(source, layout_skill)
    return [normalized(value) for value in layout.visible(blocks)]


def _prompt_text(quote):
    """Plain-text projection of the renderer's validated prompt card, not Markdown parsing."""
    lines, previous = [], None
    for child in quote.find_all(recursive=False):
        if child.name == "p":
            if lines and previous == "p":
                lines.append("")
            lines.extend(x.strip() for x in child.get_text().splitlines() if x.strip())
        else:  # The layout parser only permits flat ul/ol here.
            for index, li in enumerate(child.find_all("li", recursive=False), 1):
                parts = [x.strip() for x in li.get_text().splitlines() if x.strip()]
                lines.extend([(f"{index}. " if child.name == "ol" else "- ") + parts[0], *parts[1:]])
        previous = child.name
    first, *lines = lines
    head = re.match(r"^【(.+?)】(.*)$", first)
    inner = head[1] if head else first
    hint = re.match(r"^(.*?)\s*[（(](.*)[）)]$", inner)
    title = hint[1] + hint[2] if hint else inner
    if head and head[2].strip():
        lines.insert(0, head[2].strip())
    return normalized(title), normalized(" ".join(lines))


def _reader_contract(blocks, source=False, heading_split=None):
    """Compare semantic blocks, including cards/tables that the renderer marks decorative.

    data-reading-role alone omits those blocks and double-counts nested lists/quotes.
    Only the renderer's explicit presentation transforms are projected here: prompt
    title brackets/hints, list markers, table time-range wrapping and heading splits.
    """
    from bs4 import BeautifulSoup
    result = []
    for block in blocks:
        if block.name in {"h1", "hr"} or block.has_attr("data-picture"):
            continue
        table = block if block.name == "table" else block.find("table")
        if table is not None:
            rows = []
            for row in table.find_all("tr"):
                cells = []
                for cell in row.find_all(["th", "td"]):
                    # cellHTML wraps only time ranges over two lines on phones.
                    text = normalized(cell.get_text())
                    text = re.sub(r"^(\d+[.:]\d+)\s*-\s*(\d+[.:]\d+)$", r"\1-\2", text)
                    cells.append(text)
                rows.append(tuple(cells))
            result.append(("table", tuple(rows)))
        elif block.name == "blockquote" and re.match(r"^【.+】", block.get_text().strip()):
            result.append(("prompt", *_prompt_text(block)))
        elif block.has_attr("data-prompt-card"):
            sections = block.find_all("section", recursive=False)
            if len(sections) != 2:
                raise CheckError("Rendered prompt card structure mismatch")
            # br separates prompt lines; inline label spans do not add spaces.
            body = BeautifulSoup(str(sections[1]), "html.parser")
            for br in body.find_all("br"):
                br.replace_with("\n")
            result.append(("prompt", normalized(sections[0].get_text()), normalized(body.get_text())))
        elif block.name in {"ul", "ol"}:
            result.append((block.name, tuple(normalized(li.get_text()) for li in block.find_all("li", recursive=False))))
        elif block.has_attr("data-chapter"):
            title = BeautifulSoup(str(block), "html.parser")
            for decoration in title.select("[data-decoration]"):
                decoration.decompose()
            result.append(("text", normalized(title.get_text())))
        elif block.has_attr("data-decoration") and not block.get_text(strip=True):
            continue  # Empty horizontal/source rules, never reader text.
        elif block.find("img"):
            continue
        else:
            text = normalized(block.get_text())
            if source and block.name == "h2" and text in (heading_split or {}):
                text = normalized("".join(heading_split[text]))
            result.append(("text", text))
    return result


def check_rendered_text(source, rendered, layout_skill=None, heading_split=None):
    """Fail closed on changed text in the actual rendered DOM, not browser metadata."""
    from bs4 import BeautifulSoup, Tag
    _, blocks = _source_blocks(source, layout_skill)
    expected = _reader_contract(blocks, source=True, heading_split=heading_split)
    soup = BeautifulSoup(rendered, "html.parser")
    root = soup.select_one("#article-body") or soup.body or soup
    paper = root.find(attrs={"data-paper": True}, recursive=False)
    if paper is not None:
        root = paper
    actual = _reader_contract([node for node in root.children if isinstance(node, Tag)])
    if actual != expected:
        raise CheckError("Rendered body/source mismatch; no completed preview")


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
    expected = manuscript_blocks(source)
    check_rendered_text(source, raw)
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
        check_rendered_text(source, preview)
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
        lock(log)
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
    ensure_utf8_mode()
    raise SystemExit(main())
