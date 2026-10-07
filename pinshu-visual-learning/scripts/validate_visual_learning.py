#!/usr/bin/env python3
"""检查图解交付的结构、链接、SVG与可量化窄屏条件；不判定语义或审美。"""
from __future__ import annotations

import argparse
import json
import re
import xml.etree.ElementTree as ET
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlsplit

FORMAL_KIND = "图解学习"
FORMAL_STATUS = "正式"
DRAFT_STATUSES = {"候选", "待验收", FORMAL_STATUS}


class OfflineHTML(HTMLParser):
    def __init__(self):
        super().__init__()
        self.external, self.text, self.fragments, self.links = [], [], [], []
        self.hidden, self.images, self.h1 = 0, 0, 0
        self.ids = set()

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag in ("style", "script"):
            self.hidden += 1
        if tag == "h1":
            self.h1 += 1
        if tag in ("img", "svg"):
            self.images += 1
        if "id" in a:
            self.ids.add(a["id"])
        for key in ("src", "poster", "srcset"):
            if a.get(key) and not a[key].startswith(("data:", "#")):
                self.external.append(f"{tag}.{key}: {a[key]}")
        if tag == "link" and a.get("href") and a.get("rel") != "canonical":
            self.external.append(f'link.href: {a["href"]}')
        if tag == "a" and a.get("href"):
            href = a["href"]
            self.links.append(href)
            if href.startswith("#"):
                self.fragments.append(href[1:])
        if tag in ("iframe", "object", "embed"):
            self.external.append(f"不允许依赖嵌入页面: {tag}")

    def handle_endtag(self, tag):
        if tag in ("style", "script"):
            self.hidden = max(0, self.hidden - 1)

    def handle_data(self, data):
        if not self.hidden:
            self.text.append(data)


def parse_frontmatter(note: str) -> dict[str, str]:
    match = re.match(r"^---\n(.*?)\n---\n", note, re.S)
    if not match:
        return {}
    result = {}
    for line in match.group(1).splitlines():
        if ":" not in line or line.lstrip().startswith("#"):
            continue
        key, value = line.split(":", 1)
        result[key.strip()] = value.strip().strip('"\'')
    return result


def local_target(base: Path, raw: str) -> Path | None:
    url = raw.strip().strip("<>")
    split = urlsplit(url)
    if split.scheme or url.startswith("//") or url.startswith("#"):
        return None
    return (base / unquote(split.path)).resolve()


def svg_metrics(path: Path, mobile_content_width: float | None) -> tuple[list[str], dict]:
    errors = []
    try:
        root = ET.parse(path).getroot()
    except ET.ParseError as exc:
        return [f"SVG不是合法XML: {path.name}: {exc}"], {}
    viewbox = root.attrib.get("viewBox", "").replace(",", " ").split()
    width = None
    if len(viewbox) == 4:
        try:
            width = float(viewbox[2])
        except ValueError:
            pass
    if width is None:
        match = re.match(r"([0-9.]+)(?:px)?$", root.attrib.get("width", ""))
        if match:
            width = float(match.group(1))
    sizes = []
    for elem in root.iter():
        raw = elem.attrib.get("font-size")
        if raw:
            match = re.match(r"([0-9.]+)(?:px)?$", raw.strip())
            if match:
                sizes.append(float(match.group(1)))
        sizes += [float(x) for x in re.findall(r"font-size\s*:\s*([0-9.]+)(?:px)?", elem.attrib.get("style", ""), re.I)]
        if elem.tag.rsplit("}", 1)[-1] == "style" and elem.text:
            sizes += [float(x) for x in re.findall(r"font-size\s*:\s*([0-9.]+)(?:px)?", elem.text, re.I)]
    metrics = {"path": str(path), "intrinsic_width": width, "source_font_min": min(sizes) if sizes else None}
    if mobile_content_width is not None:
        if not width or width <= 0:
            errors.append(f"SVG缺少可计算的width/viewBox: {path.name}")
        elif not sizes:
            errors.append(f"SVG没有可计算的px字号: {path.name}")
        else:
            scale = min(1.0, mobile_content_width / width)
            displayed = min(sizes) * scale
            metrics.update({"mobile_content_width": mobile_content_width, "scale": scale,
                            "displayed_font_min": round(displayed, 2)})
            if displayed < 11:
                errors.append(f"SVG窄屏折算后最小字号低于11px: {path.name}={displayed:.2f}px")
    return errors, metrics


def check(md: Path, html: Path, *, formal: bool = False, mobile_content_width: float | None = None,
          link_base: Path | None = None):
    errors, warnings, image_paths, link_paths, svg_reports = [], [], [], [], []
    if not md.is_file() or not html.is_file():
        return {"kind": "visual_learning_mechanical", "passed": False,
                "errors": ["Markdown或HTML文件不存在"], "warnings": []}
    note = md.read_text(encoding="utf-8")
    markup = html.read_text(encoding="utf-8")
    frontmatter = parse_frontmatter(note)
    if not frontmatter:
        errors.append("Markdown缺少有效的文件级属性区")
    if formal:
        if frontmatter.get("kind") != FORMAL_KIND:
            errors.append(f"正式图解frontmatter.kind必须为{FORMAL_KIND}")
        if frontmatter.get("status") != FORMAL_STATUS:
            errors.append(f"正式图解frontmatter.status必须为{FORMAL_STATUS}")
    else:
        if "kind" in frontmatter and frontmatter["kind"] != FORMAL_KIND:
            warnings.append(f"候选稿kind={frontmatter['kind']}；正式提升前改为{FORMAL_KIND}")
        if "status" in frontmatter and frontmatter["status"] not in DRAFT_STATUSES:
            warnings.append(f"候选稿status={frontmatter['status']}；正式提升前改为{FORMAL_STATUS}")
        if "kind" not in frontmatter or "status" not in frontmatter:
            warnings.append("候选稿尚未补齐kind/status；正式提升前必须补齐")
    if len(re.findall(r"^# ", note, re.M)) != 1:
        errors.append("Markdown应有一个一级标题")

    for label, raw in re.findall(r"!\[([^\]]*)\]\(([^\n]*?)\)", note):
        target = local_target(md.parent, raw)
        if target is None:
            errors.append(f"图片必须在交付包内使用相对路径: {raw.strip()}")
            continue
        try:
            target.relative_to(md.parent.resolve())
        except ValueError:
            errors.append(f"图片路径离开交付包: {raw.strip()}")
            continue
        if not target.is_file():
            errors.append(f"图片不存在: {raw.strip()}")
        else:
            image_paths.append(str(target))
            if target.suffix.lower() != ".png":
                warnings.append(f"需实际确认阅读器支持图片类型: {target.suffix}")
        if not label.strip():
            errors.append(f"图片缺少内容说明: {raw.strip()}")

    source_base = link_base.resolve() if link_base else md.parent
    markdown_links = re.findall(r"(?<!!)\[([^\]]+)\]\(([^\n]*?)\)", note)
    for label, raw in markdown_links:
        if formal and Path(urlsplit(raw.strip().strip("<>")).path).is_absolute():
            errors.append(f"正式Markdown本地回链必须使用相对路径: {label} -> {raw.strip()}")
        target = local_target(source_base, raw)
        if target is not None:
            link_paths.append(str(target))
            if not target.exists():
                errors.append(f"Markdown相对链接不存在: {label} -> {raw.strip()}")
    for key, value in frontmatter.items():
        if key.startswith("source_") and value:
            if formal and Path(urlsplit(value).path).is_absolute():
                errors.append(f"正式frontmatter来源必须使用相对路径: {key}={value}")
            target = local_target(source_base, value)
            if target is not None and not target.exists():
                errors.append(f"frontmatter来源路径不存在: {key}={value}")

    if not image_paths:
        errors.append("Markdown没有可读图解图片")
    if re.search(r"\b(?:PID\s*\d+|F\d{3}|V\d{3}|SEMANTIC_QA_PASS|MANUAL_POLICY_SYNC)\b", note):
        errors.append("正文含内部证据或状态标记")

    svg_paths = []
    for image_value in image_paths:
        image = Path(image_value)
        paired = image.with_suffix(".svg")
        if not paired.is_file():
            errors.append(f"PNG缺少同名可编辑SVG图源: {image.name}")
        else:
            svg_paths.append(paired)
    for svg in sorted(set(svg_paths)):
        svg_errors, metrics = svg_metrics(svg, mobile_content_width)
        errors.extend(svg_errors)
        if metrics:
            svg_reports.append(metrics)

    h = OfflineHTML()
    h.feed(markup)
    errors += [f"HTML有非内嵌资源: {x}" for x in h.external]
    for token in re.findall(r"url\((.*?)\)", markup, re.I):
        if not token.strip(" \"'").startswith(("data:", "#")):
            errors.append(f"HTML样式依赖外部资源: {token}")
    if h.h1 != 1:
        errors.append("HTML应有一个一级标题")
    if not re.search(r"<meta[^>]+name=[\"']viewport", markup, re.I):
        errors.append("HTML缺少手机视口声明")
    if not h.images:
        errors.append("HTML没有图解图形")
    if not re.search(r"img\s*\{[^}]*max-width\s*:\s*100%", markup, re.I | re.S) and not re.search(
            r"<img[^>]+style=[\"'][^\"']*max-width\s*:\s*100%", markup, re.I):
        errors.append("HTML图片缺少max-width:100%窄屏约束")
    for fragment in h.fragments:
        if fragment not in h.ids:
            errors.append(f"HTML页内导航断链: #{fragment}")
    html_relative_links = 0
    for href in h.links:
        if formal and not urlsplit(href).scheme and Path(urlsplit(href).path).is_absolute():
            errors.append(f"正式HTML本地回链必须使用相对href: {href}")
        target = local_target(source_base, href)
        if target is not None:
            html_relative_links += 1
            if not target.exists():
                errors.append(f"HTML相对链接不存在: {href}")
    if markdown_links and html_relative_links == 0:
        errors.append("Markdown含来源回链，但HTML没有可点击的相对<a href>链接")

    visible = " ".join(h.text)
    for heading in re.findall(r"^## (.+)$", note, re.M):
        if heading not in visible:
            errors.append(f"Markdown章节未在同源HTML中出现: {heading}")
    return {
        "schema_version": 2, "kind": "visual_learning_mechanical", "passed": not errors,
        "formal": formal, "markdown": str(md.resolve()), "html": str(html.resolve()),
        "link_base": str(source_base.resolve()),
        "images": image_paths, "resolved_links": link_paths, "svg_metrics": svg_reports,
        "errors": errors, "warnings": warnings,
        "not_verified": ["图形语义", "内容完整性", "桌面视觉", "真实手机", "Obsidian阅读", "工作台图片路由", "用户批准"],
    }


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--md", required=True, type=Path)
    ap.add_argument("--html", required=True, type=Path)
    ap.add_argument("--formal", action="store_true", help="按正式提升稿的frontmatter要求检查")
    ap.add_argument("--mobile-content-width", type=float,
                    help="从真实目标页面测得的内容列宽；提供后折算每张SVG的实际显示字号")
    ap.add_argument("--link-base", type=Path,
                    help="候选稿按未来正式目录解析正文/来源回链；图片仍按候选稿自身目录解析")
    ap.add_argument("--json-out", type=Path)
    args = ap.parse_args()
    if args.mobile_content_width is not None and args.mobile_content_width <= 0:
        ap.error("--mobile-content-width must be positive")
    report = check(args.md, args.html, formal=args.formal, mobile_content_width=args.mobile_content_width,
                   link_base=args.link_base)
    if args.json_out:
        args.json_out.parent.mkdir(parents=True, exist_ok=True)
        args.json_out.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0 if report["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
