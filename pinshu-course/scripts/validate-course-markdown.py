#!/usr/bin/env python3
"""Validate course Markdown before promotion to the formal knowledge base.

Checks UTF-8 readability, NUL bytes, unique H1, blank lines after H1/H2/H3/H4,
relative image targets, and caller-supplied required/forbidden terms. Optional
long-course profiles add paragraph, emphasis, learning-document, and source-noise gates.
Exit 0 only when every file passes.
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

HEADING_RE = re.compile(r"^(#{1,4})\s+\S")
IMAGE_RE = re.compile(r"!\[[^\]]*\]\(([^)]+)\)")
WIKI_IMAGE_RE = re.compile(r"!?\[\[([^\]|#]+\.(?:png|jpe?g|gif|webp|svg))(?:[|#][^\]]*)?\]\]", re.IGNORECASE)
ORDERED_LIST_RE = re.compile(r"^\d+[.)]\s+")
BOLD_RE = re.compile(r"\*\*.+?\*\*")
LEADING_PUNCT_RE = re.compile(r"^[\uff0c\u3002\uff01\uff1f\uff1b\uff1a\u3001,.!?;:\uff09\u3011\u300b”’]")
BAD_CJK_SPACING_RE = re.compile(r"(?<=[\u3400-\u9fff\uff0c\u3002\uff01\uff1f\uff1b\uff1a\u3001])[ \t]{2,}(?=[\u3400-\u9fff])")
FRAGMENT_END_RE = re.compile(r"[\uff0c\u3001\uff1b,;]$")
ORPHAN_CUE_RE = re.compile(r"^(?:\u597d[\uff0c,]|\u8c22\u8c22|\u968f\u540e|\u7136\u540e|\u6240\u4ee5|\u90a3\u4e48|\u53bb\u5173\u6ce8|\u4e5f\u5c31\u662f|\u8fd9\u4e2a(?:\u662f|\u5c31))")
SENTENCE_END_RE = re.compile(r"[\u3002\uff01\uff1f!?]")
TYPE_DIR_MARKERS = ("\u539f\u59cb\u8f6c\u5199", "\u5fe0\u5b9e\u7cbe\u7f16\u7a3f", "\u6821\u5bf9\u7cbe\u7f16\u7a3f", "\u7ed3\u6784\u5316\u8bb2\u4e49")
REDUNDANT_TITLE_TYPE_LABELS = (
    "\u9010\u5b57\u7a3f",
    "\u5fe0\u5b9e\u7cbe\u7f16\u7a3f",
    "\u6821\u5bf9\u7cbe\u7f16\u7a3f",
    "\u7ed3\u6784\u5316\u8bb2\u4e49",
    "\u6e05\u6d17\u7a3f",
    "\u6574\u7406\u7a3f",
    "\u9605\u8bfb\u7248",
    "\u5b8c\u6574\u7248",
    "\u603b\u7a3f",
)


def strip_code_for_image_scan(text: str) -> str:
    """Remove fenced and inline code before checking image targets.

    Course notes often preserve literal Markdown image syntax inside Prompt/code
    examples. Those examples are not document embeds and must not be resolved as
    files on disk.
    """
    output: list[str] = []
    fence_char: str | None = None
    fence_len = 0
    for line in text.splitlines():
        stripped = line.strip()
        marker = re.match(r"^(`{3,}|~{3,})", stripped)
        if fence_char is None and marker:
            token = marker.group(1)
            fence_char = token[0]
            fence_len = len(token)
            output.append("")
            continue
        if fence_char is not None:
            closing = re.match(rf"^{re.escape(fence_char)}{{{fence_len},}}\s*$", stripped)
            if closing:
                fence_char = None
                fence_len = 0
            output.append("")
            continue
        output.append(re.sub(r"`[^`\n]*`", "", line))
    return "\n".join(output)


def strip_nonvisible_contract_content(text: str) -> str:
    """Remove metadata and code that must not satisfy visible-document contracts."""
    text = re.sub(r"\A---\s*\n.*?\n---\s*\n", "", text, flags=re.DOTALL)
    text = re.sub(r"<!--.*?-->", "", text, flags=re.DOTALL)
    text = re.sub(r"(?m)^\s*>.*$", "", text)
    text = strip_code_for_image_scan(text)
    return re.sub(r"(?m)^(?: {4}|\t).*$", "", text)


# Propagation assets are validated independently by pinshu-content-assets.
# Course notes retain only their learning-document contract.
COMMON_REQUIRED = ["\u672c\u8bfe\u6838\u5fc3"]
FAITHFUL_FILLERS = ["\u5462", "\u90a3\u4e2a", "\u5c31\u662f\u8bf4", "\u7136\u540e\u5462", "\u5927\u5bb6\u597d", "hello", "\u597d\u5427"]


def validate(path: Path, required: list[str], forbidden: list[str], profile: str | None) -> list[str]:
    errors: list[str] = []
    try:
        raw = path.read_bytes()
        text = raw.decode("utf-8")
    except Exception as exc:
        return [f"cannot read as UTF-8: {exc}"]

    scan_text = strip_nonvisible_contract_content(text)

    if b"\x00" in raw:
        errors.append("contains NUL bytes")

    lines = text.splitlines()
    in_fence = False
    in_frontmatter = bool(lines and lines[0].strip() == "---")
    h1_lines: list[int] = []
    h2_lines: list[int] = []
    long_120: list[int] = []
    long_180: list[int] = []
    leading_punct: list[int] = []
    bad_spacing: list[int] = []
    short_fragments: list[int] = []
    hanging_fragments: list[int] = []
    long_blocks_120: list[int] = []
    long_blocks_180: list[int] = []
    prose_blocks: list[tuple[int, str, int]] = []
    list_runs: list[tuple[int, int]] = []
    for i, line in enumerate(lines):
        stripped = line.strip()
        if in_frontmatter:
            if i > 0 and stripped == "---":
                in_frontmatter = False
            continue
        if stripped.startswith("```") or stripped.startswith("~~~"):
            in_fence = not in_fence
            continue
        if in_fence:
            continue
        match = HEADING_RE.match(line)
        if not match:
            continue
        if len(match.group(1)) == 1:
            h1_lines.append(i + 1)
        if len(match.group(1)) == 2:
            h2_lines.append(i + 1)
        if i + 1 >= len(lines) or lines[i + 1].strip():
            errors.append(f"line {i + 1}: heading is not followed by a blank line")

        continue

    if profile:
        in_fence = False
        in_frontmatter = bool(lines and lines[0].strip() == "---")
        section_id = 0
        block_start = 0
        block_parts: list[str] = []
        list_start = 0
        list_count = 0

        def flush_block() -> None:
            nonlocal block_start, block_parts
            if block_parts:
                prose_blocks.append((block_start, "".join(block_parts), section_id))
                block_start = 0
                block_parts = []

        def flush_list() -> None:
            nonlocal list_start, list_count
            if list_count:
                list_runs.append((list_start, list_count))
                list_start = 0
                list_count = 0

        for i, line in enumerate(lines):
            stripped = line.strip()
            if in_frontmatter:
                if i > 0 and stripped == "---":
                    in_frontmatter = False
                continue
            if stripped.startswith("```") or stripped.startswith("~~~"):
                flush_block()
                flush_list()
                in_fence = not in_fence
                continue
            if in_fence:
                continue
            if not stripped:
                flush_block()
                flush_list()
                continue

            content = stripped
            ordered = ORDERED_LIST_RE.match(content)
            bulleted = content.startswith(("- ", "* ", "+ "))
            if ordered:
                content = ORDERED_LIST_RE.sub("", content, count=1).strip()
            elif bulleted:
                content = content[2:].strip()

            if content and LEADING_PUNCT_RE.match(content):
                leading_punct.append(i + 1)
            if BAD_CJK_SPACING_RE.search(content):
                bad_spacing.append(i + 1)

            if stripped.startswith("#"):
                flush_block()
                flush_list()
                section_id += 1
                continue
            if stripped.startswith(("---", "|", ">")):
                flush_block()
                flush_list()
                continue
            if ordered or bulleted:
                flush_block()
                if not list_count:
                    list_start = i + 1
                list_count += 1
                continue

            flush_list()
            if not block_parts:
                block_start = i + 1
            block_parts.append(stripped)
            if len(stripped) > 120:
                long_120.append(i + 1)
            if len(stripped) > 180:
                long_180.append(i + 1)

        flush_block()
        flush_list()

        for start, block, _ in prose_blocks:
            compact = re.sub(r"\s+", "", block)
            if len(compact) > 120:
                long_blocks_120.append(start)
            if len(compact) > 180:
                long_blocks_180.append(start)
            if (
                len(compact) <= 12
                and re.search(r"[\u3400-\u9fff]", compact)
                and ORPHAN_CUE_RE.search(compact)
            ):
                short_fragments.append(start)
            if len(compact) < 80 and FRAGMENT_END_RE.search(compact):
                hanging_fragments.append(start)

    if len(h1_lines) != 1:
        errors.append(f"expected exactly one H1, found {len(h1_lines)} at {h1_lines}")

    type_context = next(
        (
            marker
            for parent in path.parents
            for marker in TYPE_DIR_MARKERS
            if marker in parent.name
        ),
        None,
    )
    if type_context:
        h1_text = ""
        if len(h1_lines) == 1:
            h1_text = lines[h1_lines[0] - 1].lstrip("#").strip()
        for label in REDUNDANT_TITLE_TYPE_LABELS:
            if label in path.stem:
                errors.append(
                    f"filename repeats document type already expressed by parent directory "
                    f"({type_context}): {label}"
                )
            if h1_text and label in h1_text:
                errors.append(
                    f"H1 repeats document type already expressed by parent directory "
                    f"({type_context}): {label}"
                )

    for term in required:
        if term not in scan_text:
            errors.append(f"required term missing: {term}")
    for term in forbidden:
        count = scan_text.count(term)
        if count:
            errors.append(f"forbidden term remains: {term} x{count}")

    if profile:
        profile_required = list(COMMON_REQUIRED)
        if profile == "long-course-notes":
            profile_required.append("\u4e8b\u5b9e\u6838\u9a8c\u4e0e\u8fb9\u754c\u8bf4\u660e")
        for term in profile_required:
            if term not in scan_text:
                errors.append(f"profile required term missing: {term}")

        for dash in ("——", "—"):
            count = scan_text.count(dash)
            if count:
                errors.append(f"profile forbidden dash remains: {dash} x{count}")

        bold_count = len(BOLD_RE.findall(scan_text))
        if len(raw) >= 7000 and bold_count < 5:
            errors.append(f"long-course scan layer too weak: bold spans {bold_count}, expected at least 5")
        if bold_count > 10:
            errors.append(f"too many bold spans: {bold_count}, maximum 10")

        if long_120:
            errors.append(f"prose lines over 120 chars: {len(long_120)} at {long_120[:12]}")
        if long_180:
            errors.append(f"prose lines over 180 chars: {len(long_180)} at {long_180[:12]}")
        if long_blocks_120:
            errors.append(f"prose paragraphs over 120 chars: {len(long_blocks_120)} at {long_blocks_120[:12]}")
        if long_blocks_180:
            errors.append(f"prose paragraphs over 180 chars: {len(long_blocks_180)} at {long_blocks_180[:12]}")
        if leading_punct:
            errors.append(f"paragraph/list content starts with punctuation: {len(leading_punct)} at {leading_punct[:12]}")
        if bad_spacing:
            errors.append(f"abnormal CJK spacing: {len(bad_spacing)} at {bad_spacing[:12]}")
        if short_fragments:
            errors.append(f"orphan prose fragments (<=12 chars): {len(short_fragments)} at {short_fragments[:12]}")
        if hanging_fragments:
            errors.append(f"prose fragments end with comma/semicolon: {len(hanging_fragments)} at {hanging_fragments[:12]}")

        by_section: dict[int, list[tuple[int, str]]] = {}
        for start, block, section in prose_blocks:
            by_section.setdefault(section, []).append((start, re.sub(r"\s+", "", block)))
        sparse_runs: list[int] = []
        for blocks in by_section.values():
            run: list[int] = []
            for start, block in blocks:
                if len(block) < 45:
                    run.append(start)
                    if len(run) == 5:
                        sparse_runs.append(run[0])
                else:
                    run = []
        if sparse_runs:
            errors.append(f"mechanically fragmented prose: runs of 5+ short paragraphs at {sparse_runs[:12]}")

        long_lists = [(start, count) for start, count in list_runs if count > 7]
        if long_lists:
            errors.append(f"ungrouped root lists over 7 items: {long_lists[:8]}")

        if profile == "long-course-faithful":
            if h2_lines:
                errors.append(
                    "faithful heading hierarchy uses H2; use H3 for green section headings "
                    f"under Obsidian Nord: {h2_lines[:12]}"
                )
            for filler in FAITHFUL_FILLERS:
                count = scan_text.count(filler)
                if count:
                    errors.append(f"faithful filler requires review: {filler} x{count}")

        if profile == "long-course-notes":
            for fact_type in ("A ·", "C ·", "D ·", "E ·"):
                if fact_type not in scan_text:
                    errors.append(f"fact boundary type missing: {fact_type}")

            match = re.search(
                r"^## \u672c\u8bfe\u8981\u70b9\u901f\u89c8\s*$\n(.*?)(?=^## |^---\s*$|\Z)",
                scan_text,
                flags=re.MULTILINE | re.DOTALL,
            )
            if match:
                items = re.split(r"\n(?=\d+[.)]\s+)", match.group(1).strip())
                bad_takeaways: list[tuple[int, int]] = []
                for item in items:
                    item_match = ORDERED_LIST_RE.match(item)
                    if not item_match:
                        continue
                    number = int(re.match(r"\d+", item).group())
                    sentence_count = len(SENTENCE_END_RE.findall(item))
                    if not 3 <= sentence_count <= 5:
                        bad_takeaways.append((number, sentence_count))
                if bad_takeaways:
                    errors.append(f"takeaway items must contain 3-5 sentences: {bad_takeaways[:12]}")

    image_scan_text = strip_code_for_image_scan(text)
    for match in IMAGE_RE.finditer(image_scan_text):
        target = match.group(1).strip()
        if target.startswith(("http://", "https://", "data:")):
            continue
        target = target.split("#", 1)[0]
        if target and not (path.parent / target).resolve().exists():
            errors.append(f"missing relative image: {target}")

    vault_root = next(
        (parent for parent in (path.parent, *path.parents) if (parent / ".obsidian").is_dir()),
        None,
    )
    for match in WIKI_IMAGE_RE.finditer(image_scan_text):
        target = match.group(1).strip()
        if target.startswith(("./", "../")):
            resolved = (path.parent / target).resolve()
        elif vault_root is not None:
            resolved = (vault_root / target).resolve()
        else:
            resolved = (path.parent / target).resolve()
        if not resolved.exists():
            errors.append(f"missing Obsidian image: {target}")

    return errors


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("paths", nargs="+", type=Path)
    parser.add_argument("--require", action="append", default=[])
    parser.add_argument("--forbid", action="append", default=[])
    parser.add_argument(
        "--profile",
        choices=["long-course-faithful", "long-course-notes"],
        default=None,
    )
    args = parser.parse_args()

    failed = False
    for path in args.paths:
        errors = validate(path, args.require, args.forbid, args.profile)
        if errors:
            failed = True
            print(f"FAIL {path}")
            for error in errors:
                print(f"  - {error}")
        else:
            print(f"PASS {path}")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
