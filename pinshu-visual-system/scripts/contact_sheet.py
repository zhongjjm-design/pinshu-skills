#!/usr/bin/env python3
"""One page to look at every image of a batch before calling it done (meeting 2026-10-12 round 2:
"after drawing I could not see the pictures, whether the words in them were right was luck").

  python3 scripts/contact_sheet.py --plan <过程文件夹/配图任务.json>
  python3 scripts/contact_sheet.py --folder <一批图所在文件夹> --expect 5

Writes a new 看图墙_<时间>.html beside the plan (or in the folder) and never overwrites one.
Each card shows the picture (click for full size), file name, role, purpose, anchor paragraph,
review state, last change and short fingerprint. On top it counts planned against found and lists
problems: a missing file, a file outside the process folder, two names that are one file on
macOS/Windows. Looking at the page is the person's or Agent's job; the page only makes it possible.
Standard library only.
"""
from __future__ import annotations

import argparse
import hashlib
import html
import json
import struct
import time
import unicodedata
from pathlib import Path
from urllib.parse import quote

IMAGE_SUFFIXES = {".png", ".jpg", ".jpeg", ".webp", ".gif"}


def name_key(name: str) -> str:
    return unicodedata.normalize("NFC", name).casefold()


def image_size(path: Path):
    """Width and height for PNG, JPEG, GIF and WebP without Pillow; None when unknown."""
    try:
        data = path.read_bytes()[:65536]
        if data[:8] == b"\x89PNG\r\n\x1a\n":
            return struct.unpack(">II", data[16:24])
        if data[:6] in (b"GIF87a", b"GIF89a"):
            return struct.unpack("<HH", data[6:10])
        if data[:4] == b"RIFF" and data[8:12] == b"WEBP":
            if data[12:16] == b"VP8X":
                return int.from_bytes(data[24:27], "little") + 1, int.from_bytes(data[27:30], "little") + 1
            if data[12:16] == b"VP8 ":
                w, h = struct.unpack("<HH", data[26:30])
                return w & 0x3FFF, h & 0x3FFF
        if data[:2] == b"\xff\xd8":
            i = 2
            while i < len(data) - 9:
                if data[i] != 0xFF:
                    i += 1
                    continue
                marker = data[i + 1]
                if marker in (0xC0, 0xC1, 0xC2):
                    h, w = struct.unpack(">HH", data[i + 5:i + 9])
                    return w, h
                i += 2 + struct.unpack(">H", data[i + 2:i + 4])[0]
    except (OSError, struct.error):
        pass
    return None


def _resolve(base: Path, value: str) -> Path:
    path = Path(value).expanduser()
    return (path if path.is_absolute() else base / path).resolve()


def cards_from_plan(plan_path: Path):
    plan = json.loads(plan_path.read_text(encoding="utf-8"))
    process = plan_path.parent.resolve()
    cards = []
    for asset in plan.get("assets", []):
        file = _resolve(plan_path.parent, asset.get("file", "")) if asset.get("file") else None
        revisions = asset.get("revisions", [])
        cards.append({"file": file, "name": asset.get("filename") or (file.name if file else "（未指定文件）"),
                      "role": asset.get("role", ""), "kind": asset.get("asset_kind", ""), "purpose": asset.get("purpose", ""),
                      "anchor": asset.get("after_prefix", ""), "state": asset.get("review_state", "待确认"),
                      "change": (revisions[-1]["at"] + " " + revisions[-1]["by"] + "：" + revisions[-1]["reason"]) if revisions else "",
                      "outside": bool(file and not file.is_relative_to(process))})
    return cards, len(plan.get("assets", []))


def cards_from_folder(folder: Path):
    files = sorted(p for p in folder.iterdir() if p.is_file() and p.suffix.lower() in IMAGE_SUFFIXES)
    return [{"file": f.resolve(), "name": f.name, "role": "", "kind": "", "purpose": "", "anchor": "",
             "state": "待确认", "change": "", "outside": False} for f in files], None


def problems_of(cards, planned, expect):
    problems, seen = [], {}
    for card in cards:
        if card["file"] is None or not card["file"].is_file():
            problems.append(f"找不到文件：{card['name']}" + (f"（{card['file']}）" if card["file"] else ""))
        if card["outside"]:
            problems.append(f"不在本篇过程文件夹里：{card['name']}（{card['file']}）；修好的图要放回过程文件夹")
        key = name_key(card["name"])
        if key in seen:
            problems.append(f"同名冲突：{seen[key]} 和 {card['name']} 在 Mac/Windows 上是同一个文件，后写的会盖掉先写的")
        seen.setdefault(key, card["name"])
    found = sum(1 for c in cards if c["file"] and c["file"].is_file())
    target = expect if expect is not None else planned
    if target is not None and found != target:
        problems.append(f"应有 {target} 张，实际找到 {found} 张")
    return problems, found


def render(title: str, out: Path, cards, problems, found, planned, expect) -> str:
    target = expect if expect is not None else planned
    head = (f"应有 {target} 张，找到 {found} 张" if target is not None else f"找到 {found} 张") + "。"
    css = ("body{font-family:-apple-system,'PingFang SC',sans-serif;margin:24px;background:#f4f4f2;color:#222}"
           ".bad{background:#fde8e6;border:1px solid #e0a39c;padding:10px 14px;border-radius:6px}"
           ".ok{background:#e8f3ea;border:1px solid #9cc7a6;padding:10px 14px;border-radius:6px}"
           ".grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(300px,1fr));gap:16px;margin-top:16px}"
           ".card{background:#fff;border-radius:8px;padding:12px;box-shadow:0 1px 3px #0002}"
           ".card img{width:100%;border:1px solid #ddd;border-radius:4px}.card p{margin:4px 0;font-size:13px;line-height:1.5}"
           ".missing{height:160px;display:flex;align-items:center;justify-content:center;background:#fde8e6;color:#a33}")
    parts = [f"<!doctype html><html lang='zh-CN'><head><meta charset='utf-8'><title>看图墙：{html.escape(title)}</title><style>{css}</style></head><body>",
             f"<h1>看图墙：{html.escape(title)}</h1><p>{head}点图看原尺寸。这页只负责让人看得到；图里的字对不对、有没有遮挡，要逐张看过再登记。</p>"]
    parts.append("<div class='bad'><b>先处理这些：</b><ul>" + "".join(f"<li>{html.escape(p)}</li>" for p in problems) + "</ul></div>"
                 if problems else "<div class='ok'>数量对得上，没有缺图、同名冲突或放错地方的图。</div>")
    parts.append("<div class='grid'>")
    for i, card in enumerate(cards, 1):
        f = card["file"]
        if f and f.is_file():
            href = quote(f.relative_to(out.parent).as_posix()) if f.is_relative_to(out.parent) else f.as_uri()
            size = image_size(f)
            digest = hashlib.sha256(f.read_bytes()).hexdigest()[:12]
            picture = f"<a href='{href}' target='_blank'><img src='{href}' loading='lazy' alt='{html.escape(card['name'])}'></a>"
            meta = f"{size[0]}×{size[1]} 像素 · " if size else ""
            meta += f"{f.stat().st_size // 1024} KB · 指纹 {digest}"
        else:
            picture, meta = "<div class='missing'>没有这张图</div>", ""
        rows = [("文件", card["name"]), ("用途", card["purpose"]), ("类型", " / ".join(x for x in (card["role"], card["kind"]) if x)),
                ("放在", card["anchor"] and "「" + card["anchor"] + "」之后"), ("状态", card["state"]), ("最近修改", card["change"]), ("", meta)]
        parts.append(f"<div class='card'><p><b>{i:02d}</b></p>{picture}" +
                     "".join(f"<p>{html.escape(k + '：' if k else '')}{html.escape(v)}</p>" for k, v in rows if v) + "</div>")
    parts.append("</div></body></html>")
    return "".join(parts)


def build(plan: Path | None = None, folder: Path | None = None, expect: int | None = None, out: Path | None = None) -> dict:
    if bool(plan) == bool(folder):
        raise ValueError("Give exactly one of --plan or --folder")
    if plan:
        plan = plan.resolve()
        cards, planned = cards_from_plan(plan)
        base, title = plan.parent, plan.parent.name
    else:
        folder = folder.resolve()
        if not folder.is_dir():
            raise ValueError(f"Not a folder: {folder}")
        cards, planned = cards_from_folder(folder)
        base, title = folder, folder.name
    out = (out or base / f"看图墙_{time.strftime('%Y%m%d-%H%M%S')}.html").resolve()
    if out.exists():
        raise ValueError(f"Already exists, not overwritten: {out}")
    problems, found = problems_of(cards, planned, expect)
    out.write_text(render(title, out, cards, problems, found, planned, expect), encoding="utf-8")
    return {"page": str(out), "found": found, "planned": expect if expect is not None else planned, "problems": problems}


if __name__ == "__main__":
    from portable import ensure_utf8_mode
    ensure_utf8_mode()
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--plan", type=Path, help="the article's 配图任务.json")
    p.add_argument("--folder", type=Path, help="any folder holding one batch of images")
    p.add_argument("--expect", type=int, help="how many images this batch should have")
    p.add_argument("--output", type=Path, help="page path (default: 看图墙_<time>.html beside the plan or in the folder)")
    a = p.parse_args()
    try:
        result = build(a.plan, a.folder, a.expect, a.output)
    except ValueError as exc:
        p.exit(1, f"contact_sheet.py: {exc}\n")
    print(json.dumps(result, ensure_ascii=False, indent=2))
    raise SystemExit(1 if result["problems"] else 0)
