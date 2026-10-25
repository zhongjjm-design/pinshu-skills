"""Build a source-checked local WeChat layout trial from a Markdown handoff."""
from __future__ import annotations

import argparse
import hashlib
import html
import json
import re
import sys
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
        if block.find("img") or block.has_attr("data-video-slot"):
            continue
        if block.name in {"ul", "ol"}:
            result.extend(li.get_text(" ", strip=True) for li in block.find_all("li", recursive=False))
        elif block.name == "table":
            result.extend(" ".join(c.get_text(" ", strip=True) for c in tr.find_all(["th", "td"])) for tr in block.find_all("tr"))
        else:
            result.append(block.get_text(" ", strip=True))
    return result


def row_cells(line: str) -> int:
    """Number of cells a Markdown table source line declares (unescaped pipes, outer pipes ignored)."""
    line = line.strip()
    if line.startswith("|"):
        line = line[1:]
    if line.endswith("|") and not line.endswith("\\|"):
        line = line[:-1]
    return len(re.split(r"(?<!\\)\|", line))


def check_tables(raw: str) -> None:
    """markdown-it silently drops cells beyond the header width; fail loudly instead."""
    lines = raw.split("\n")
    for token in MarkdownIt("commonmark").enable("table").parse(raw):
        if token.type != "table_open" or not token.map:
            continue
        start, end = token.map
        width = row_cells(lines[start])
        for number in range(start + 2, end):
            if row_cells(lines[number]) != width:
                raise ValueError("Table row has %d cells but the header has %d (cells would be dropped): %s" % (row_cells(lines[number]), width, lines[number].strip()))


def check_cards_and_tables(soup) -> None:
    """Prompt cards and tables are plain text: links, nested quotes and code blocks would lose content, so refuse them."""
    for table in soup.find_all("table"):
        if table.find("a"):
            raise ValueError("Links inside a table lose their address; put the link in body text or write it as plain text")
    for quote in soup.find_all("blockquote", recursive=False):
        if not quote.get_text().lstrip().startswith("【"):
            continue
        if quote.find("a"):
            raise ValueError("Links inside a prompt card lose their address; write the address as plain text")
        for child in quote.find_all(recursive=False):
            if child.name not in {"p", "ul", "ol"}:
                raise ValueError("A prompt card only supports paragraphs and lists, found <%s>" % child.name)
        if quote.find(["blockquote", "pre"]) or any(li.find(["ul", "ol"]) for li in quote.find_all("li")):
            raise ValueError("A prompt card cannot contain nested quotes, code blocks or nested lists")


def check_heading_split(value, h2_titles: list[str]) -> dict:
    if not isinstance(value, dict):
        raise ValueError('heading_split must be an object: {"full heading": ["big", "small"]}')
    for title, parts in value.items():
        if title not in h2_titles:
            raise ValueError("heading_split key is not an H2 heading of the article: " + str(title))
        if not (isinstance(parts, list) and len(parts) == 2 and all(isinstance(x, str) and x.strip() for x in parts)):
            raise ValueError('heading_split value must be two non-empty strings ["big", "small"]: ' + title)
    return value


KNOWN_HANDOFF_KEYS = {"source_md", "image_manifest", "author", "digest", "title", "cover_landscape", "cover_square",
                      "body_images", "body_videos", "lead_image", "emphasis", "article_state", "heading_split"}
VIDEO_MARKER_RE = re.compile(r"^【此处(?:在后台)?插入视频：(.+)】$")
NUMBERED_H2_RE = re.compile(r"^\s*\d{1,2}\s*[|｜:：.、-]\s*")


def parse_markdown(path: Path) -> tuple[str, list[Tag]]:
    raw = path.read_text(encoding="utf-8-sig").replace("\r\n", "\n")
    if re.search(r"(?m)^===EDITOR NOTES===\s*$", raw):
        raise ValueError("Editor notes are not article body; export the selected draft with pinshu-write/scripts/export_article.py")
    _, body = split_header(path.read_bytes())
    raw = body.decode("utf-8-sig").replace("\r\n", "\n")
    if any(t.type in {"html_block", "html_inline"} for t in MarkdownIt("commonmark", {"html": True}).parse(raw)):
        raise ValueError("Raw HTML needs a separate source-faithful review")
    check_tables(raw)
    soup = BeautifulSoup(MarkdownIt("commonmark", {"html": False}).enable("table").render(raw), "html.parser")
    blocks = [node for node in soup.contents if isinstance(node, Tag)]
    if not blocks or blocks[0].name != "h1" or len(soup.find_all("h1")) != 1:
        raise ValueError("Expected one leading H1 article title")
    allowed = {"p", "h2", "h3", "h4", "ul", "ol", "blockquote", "hr", "table"}
    unexpected = [b.name for b in blocks[1:] if b.name not in allowed]
    if unexpected:
        raise ValueError("Unsupported Markdown blocks: " + ", ".join(unexpected))
    for heading in soup.find_all("h2", recursive=False):
        text = heading.get_text(" ", strip=True)
        if NUMBERED_H2_RE.match(text):
            raise ValueError("H2 already contains a chapter-number prefix; remove it or disable template numbering: " + text)
    check_cards_and_tables(soup)
    for table in soup.find_all("table"):
        # Phone width: 2 to 4 columns only; a fifth column would squeeze every cell into a vertical strip.
        columns = len(table.find("tr").find_all(["th", "td"]))
        if not 2 <= columns <= 4:
            raise ValueError("Tables need 2 to 4 columns for a phone screen, found %d" % columns)
        for cell in table.find_all(["th", "td"]):
            cell.attrs = {}
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
    unknown = sorted(set(handoff) - KNOWN_HANDOFF_KEYS)
    if unknown:
        print("Warning: unknown handoff keys ignored (typo?): " + ", ".join(unknown), file=sys.stderr)
    chapter_count = sum(b.name == "h2" and b.get_text(" ", strip=True) not in {"参考文章", "资料来源", "参考资料"} for b in blocks)
    paragraphs = [b for b in blocks if b.name == "p"]
    marker_video_labels = []
    for paragraph in paragraphs:
        match = VIDEO_MARKER_RE.fullmatch(paragraph.get_text(" ", strip=True))
        if match:
            marker_video_labels.append(match.group(1).strip())
    if marker_video_labels and handoff.get("body_videos"):
        raise ValueError("Use either article video markers or body_videos, not both")
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
    # Handoff video entries become reader-safe cards in the renderer. Operator instructions stay outside article HTML.
    video_slots = []
    for item in handoff.get("body_videos", []):
        prefix, label = item["after_prefix"], str(item.get("label", "")).strip()
        matches = [p for p in paragraphs if p.get_text(" ", strip=True).startswith(prefix)]
        if len(matches) != 1:
            raise ValueError("Video anchor must match one paragraph: " + prefix)
        if id(matches[0]) in anchored:
            raise ValueError("An image or video already follows this paragraph: " + prefix)
        anchored.add(id(matches[0]))
        video_slots.append((matches[0], label))
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
    for anchor, label in video_slots:
        slot = BeautifulSoup("<p></p>", "html.parser").p
        slot["data-video-slot"] = label or "视频"
        anchor.insert_after(slot)
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
    layout = {}
    if emphasis:
        layout["emphasis"] = emphasis
    if "heading_split" in handoff:
        h2_titles = [b.get_text(" ", strip=True) for b in blocks if b.name == "h2"]
        layout["headingSplit"] = check_heading_split(handoff["heading_split"], h2_titles)
    if layout:
        layout_path = out / "layout.json"
        layout_path.write_text(json.dumps(layout, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    render_preview(source_html, out / "fields.json", layout_path, preview)
    report = {
        "status": "trial", "version": "0.4.0-rc.3",
        "templates": ["松绿双线", "青灰手记", "暖纸杂志", "橙线手记", "蓝白专题", "首席品牌官经典版", "数字分栏"],
        "default_template": "青灰手记", "template_selection_status": "pending-per-article", "source_md": str(source),
        "source_sha256": sha(source), "image_manifest": str(manifest_path),
        "images_verified": [{"path": str(p), "sha256": sha(p)} for p in image_files.values()],
        "body_images": list(placements), "body_videos": marker_video_labels + [label or "视频" for _, label in video_slots], "chapter_count": chapter_count,
        "preview": str(preview), "preview_sha256": sha(preview),
        "source_text_blocks_preserved": True, "digest_supplied": bool(fields["digest"]),
        "source_editorial_state": handoff.get("article_state", "未提供"),
        "image_aesthetic_accepted": False, "wechat_phone_tested": False, "article_accepted": False,
    }
    (out / "试排记录.json").write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return preview


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="品叔公众号七款版式公开试用排版")
    parser.add_argument("--handoff", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()
    print(run(args.handoff, args.output_dir.resolve()))
