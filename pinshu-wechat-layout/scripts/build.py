"""Build a source-checked local WeChat layout trial from a Markdown handoff."""
from __future__ import annotations

import argparse
import hashlib
import html
import json
import re
from pathlib import Path
from urllib.parse import urlparse

from bs4 import BeautifulSoup, Tag
from markdown_it import MarkdownIt

from engine import build as render_preview
from article_header import split_header


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def locate(base: Path, value: str) -> Path:
    path = Path(value).expanduser()
    return (path if path.is_absolute() else base / path).resolve()


def visible(blocks: list[Tag]) -> list[str]:
    result = []
    for block in blocks:
        if block.name == "hr":
            continue
        if block.find("img"):
            continue
        if block.name in {"ul", "ol"}:
            result.extend(li.get_text(" ", strip=True) for li in block.find_all("li", recursive=False))
        else:
            result.append(block.get_text(" ", strip=True))
    return result


def parse_markdown(path: Path) -> tuple[str, list[Tag]]:
    raw = path.read_text(encoding="utf-8-sig").replace("\r\n", "\n")
    if re.search(r"(?m)^===EDITOR NOTES===\s*$", raw):
        raise ValueError("Editor notes are not article body; export the selected draft with pinshu-write/scripts/export_article.py")
    _, body = split_header(path.read_bytes())
    raw = body.decode("utf-8-sig").replace("\r\n", "\n")
    if any(t.type in {"html_block", "html_inline"} for t in MarkdownIt("commonmark", {"html": True}).parse(raw)):
        raise ValueError("Raw HTML needs a separate source-faithful review")
    if any(token.type == "table_open" for token in MarkdownIt("commonmark").enable("table").parse(raw)):
        raise ValueError("Markdown tables are not supported in this trial")
    soup = BeautifulSoup(MarkdownIt("commonmark", {"html": False}).render(raw), "html.parser")
    blocks = [node for node in soup.contents if isinstance(node, Tag)]
    if not blocks or blocks[0].name != "h1" or len(soup.find_all("h1")) != 1:
        raise ValueError("Expected one leading H1 article title")
    allowed = {"p", "h2", "h3", "h4", "ul", "ol", "blockquote", "hr"}
    unexpected = [b.name for b in blocks[1:] if b.name not in allowed]
    if unexpected:
        raise ValueError("Unsupported Markdown blocks: " + ", ".join(unexpected))
    if soup.find("img"):
        raise ValueError("Use body_images in the handoff to place images; Markdown image syntax is not supported")
    return blocks[0].get_text(" ", strip=True), blocks[1:]


def run(handoff_path: Path, out: Path) -> Path:
    handoff_path = handoff_path.resolve()
    handoff = json.loads(handoff_path.read_text(encoding="utf-8"))
    source = locate(handoff_path.parent, handoff["source_md"])
    manifest_path = locate(handoff_path.parent, handoff["image_manifest"])
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    if locate(manifest_path.parent, manifest["article"]) != source or manifest["article_sha256"] != sha(source):
        raise ValueError("Source Markdown differs from image handoff")
    image_files = {}
    for entry in manifest.get("files", []):
        name = entry["filename"]
        if name in image_files or Path(name).name != name:
            raise ValueError("Duplicate or nonlocal image filename: " + name)
        file = locate(manifest_path.parent, name)
        if not file.is_file() or sha(file) != entry["sha256"]:
            raise ValueError("Image differs from handoff: " + name)
        image_files[name] = file
    title, blocks = parse_markdown(source)
    chapter_count = sum(b.name == "h2" for b in blocks)
    paragraphs = [b for b in blocks if b.name == "p"]
    placements = {}
    anchored = set()
    for item in handoff.get("body_images", []):
        filename, prefix = item["filename"], item["after_prefix"]
        if filename not in image_files or filename in placements:
            raise ValueError("Missing or duplicate body image: " + filename)
        matches = [p for p in paragraphs if p.get_text(" ", strip=True).startswith(prefix)]
        if len(matches) != 1:
            raise ValueError("Image anchor must match one paragraph: " + prefix)
        if id(matches[0]) in anchored:
            raise ValueError("Two images share one paragraph anchor: " + prefix)
        if type(item.get("frame_baked", False)) is not bool:
            raise ValueError("frame_baked must be a Boolean")
        url = item.get("source_url", "")
        if url and (urlparse(url).scheme not in {"http", "https"} or not urlparse(url).netloc):
            raise ValueError("Image source_url must be HTTP(S)")
        anchored.add(id(matches[0]))
        placements[filename] = (matches[0], item)
    covers = {}
    for key in ("cover_landscape", "cover_square"):
        filename = handoff.get(key)
        if filename:
            if filename not in image_files:
                raise ValueError("Cover is absent from image handoff: " + filename)
            covers[key] = {"file": str(image_files[filename])}
    before = visible(blocks)
    container = blocks[0].parent if blocks else None
    for filename, (anchor, item) in placements.items():
        fig = BeautifulSoup("<p><img></p>", "html.parser").p
        fig.img["src"] = str(image_files[filename])
        fig.img["alt"] = item.get("alt", "")
        if item.get("frame_baked", False):
            fig.img["data-frame-baked"] = "true"
        for key in ("caption", "source_url", "source_label"):
            if key in item:
                fig.img["data-" + key.replace("_", "-")] = item[key]
        anchor.insert_after(fig)
    # Lead image: the landscape cover sits under the title, before the first paragraph,
    # framed like body images and copied with the body (handoff "lead_image": false opts out).
    if covers.get("cover_landscape") and handoff.get("lead_image", True) and blocks:
        hero = BeautifulSoup("<p><img></p>", "html.parser").p
        hero.img["src"] = covers["cover_landscape"]["file"]
        hero.img["alt"] = handoff.get("title", title)
        hero.img["data-hero"] = "true"
        hero.img["data-caption"] = ""
        blocks[0].insert_before(hero)
    if container is not None:
        blocks = [node for node in container.contents if isinstance(node, Tag) and node.name != "h1"]
    if visible(blocks) != before:
        raise ValueError("Source text changed during image placement")
    if out.exists():
        raise FileExistsError("Output directory already exists: " + str(out))
    out.mkdir(parents=True)
    source_html = out / "source.html"
    source_html.write_text("<h1>" + html.escape(title) + "</h1>\n" + "\n".join(map(str, blocks)) + "\n", encoding="utf-8")
    fields = {"title": handoff.get("title", title), "author": handoff.get("author", ""), "digest": handoff.get("digest", ""), **covers}
    (out / "fields.json").write_text(json.dumps(fields, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    preview = out / "公众号图文排版预览.html"
    # Underlined key sentences: author-chosen exact body phrases, at most three, never auto-picked.
    emphasis = handoff.get("emphasis", [])
    if len(emphasis) > 3:
        raise ValueError("At most three emphasis phrases per article")
    body_text = "\n".join(visible(blocks))
    for phrase in emphasis:
        if body_text.count(phrase) != 1:
            raise ValueError("Emphasis phrase must appear exactly once in the body: " + phrase)
    layout_path = None
    if emphasis:
        layout_path = out / "layout.json"
        layout_path.write_text(json.dumps({"emphasis": emphasis}, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    render_preview(source_html, out / "fields.json", layout_path, preview)
    report = {
        "status": "trial", "version": "0.4.0-rc.1",
        "templates": ["青灰手记", "暖纸杂志", "青绿刊页", "橙线手记", "蓝白专题", "首席品牌官经典版"],
        "default_template": "青灰手记", "template_selection_status": "pending-per-article", "source_md": str(source),
        "source_sha256": sha(source), "image_manifest": str(manifest_path),
        "images_verified": [{"path": str(p), "sha256": sha(p)} for p in image_files.values()],
        "body_images": list(placements), "chapter_count": chapter_count,
        "preview": str(preview), "preview_sha256": sha(preview),
        "source_text_blocks_preserved": True, "digest_supplied": bool(fields["digest"]),
        "source_editorial_state": handoff.get("article_state", "未提供"),
        "image_aesthetic_accepted": False, "wechat_phone_tested": False, "article_accepted": False,
    }
    (out / "试排记录.json").write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return preview


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="品叔公众号六款版式公开试用排版")
    parser.add_argument("--handoff", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()
    print(run(args.handoff, args.output_dir.resolve()))
