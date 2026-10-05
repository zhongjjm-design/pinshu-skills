#!/usr/bin/env python3
"""Mechanical checks for course learning assets.

This script verifies structure, source paths, body cleanliness and the separate
per-item metadata index. It does not replace semantic QA or real rendering in
the target reading interface.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

FM_RE = re.compile(r"\A---\s*\n(.*?)\n---\s*\n", re.S)
H1_RE = re.compile(r"(?m)^#\s+\S")
CARD_RE = re.compile(r"(?mi)^#{2,4}\s+(?:\u5361(?:\u7247)?|Card)\s*\d+\b")
QUESTION_HEADING_RE = re.compile(r"(?mi)^#{2,4}\s+(?:\u9898|Question)\s*\d+\b")
QUESTION_PROMPT_RE = re.compile(r"(?mi)^\*\*(?:\u95ee\u9898|\u95ee|Question)\s*[\uff1a:]?\*\*\s*[\uff1a:]?")
CARD_ANSWER_RE = re.compile(r"(?mi)^>\s*\[!question\]-\s*(?:\u7b54\u6848|Answer)\s*$")
QUESTION_ANSWER_RE = re.compile(r"(?mi)^>\s*\[!question\]-\s*(?:\u53c2\u8003\u7b54\u6848|Reference answer)\s*$")
FORBIDDEN_BODY_RE = re.compile(r"<details|</details|<!--|-->|<[^>]+>|^\s*%%|\b(?:card_id|q_id)\s*:", re.M)
VISIBLE_META_RE = re.compile(r"(?mi)^\*\*(?:\u5c5e\u6027|\u9898\u578b|\u7c7b\u578b|\u72b6\u6001|\u52a8\u4f5c|Attributes?|Type|Status|Action|ID)\*\*\s*[\uff1a:]")
NESTED_ITEM_META_RE = re.compile(r"(?m)^(?:cards|questions)\s*:\s*$|^\s+-\s+(?:card_id|q_id)\s*:")
CLUE_RE = re.compile(r"(?mi)^#{2,4}\s+(?:\u7ebf\u7d22|Clue)(?:\s*[\u4e00\u4e8c\u4e09\u56db\u4e94\u516d\u4e03\u516b\u4e5d\u5341\u767e]+|\s*\d+)")
VALID_STATES = {"\u672c\u8bfe\u5019\u9009", "\u540e\u8bfe\u4f0f\u7b14", "\u8de8\u8bfe\u5df2\u9a8c\u8bc1", "\u5b89\u5168\u6cbb\u7406\u5019\u9009", "current-lesson candidate", "later-lesson foreshadowing", "verified across lessons", "safety-governance candidate"}
FRONTMATTER_LINE_LIMIT = 20


def split_document(text: str) -> tuple[dict[str, str], str, str]:
    match = FM_RE.search(text)
    if not match:
        return {}, "", text
    raw = match.group(1)
    data: dict[str, str] = {}
    for line in raw.splitlines():
        if ":" not in line or line[:1].isspace():
            continue
        key, value = line.split(":", 1)
        data[key.strip()] = value.strip().strip("'\"")
    return data, raw, text[match.end() :]


def as_int(data: dict[str, str], key: str, errors: list[str]) -> int | None:
    value = data.get(key)
    if value is None:
        errors.append(f"frontmatter missing: {key}")
        return None
    try:
        return int(value)
    except ValueError:
        errors.append(f"frontmatter {key} is not an integer: {value}")
        return None


def resolve_from(owner: Path, raw: str) -> Path:
    target = Path(raw.split("#", 1)[0].strip()).expanduser()
    return target if target.is_absolute() else (owner.parent / target).resolve()


def check_source(path: Path, data: dict[str, str], key: str, errors: list[str]) -> None:
    value = data.get(key)
    if not value:
        errors.append(f"frontmatter missing: {key}")
        return
    if not resolve_from(path, value).exists():
        errors.append(f"unresolvable {key}: {value}")


def common(path: Path, text: str) -> tuple[list[str], dict[str, str], str, str]:
    errors: list[str] = []
    data, raw_frontmatter, body = split_document(text)
    if not raw_frontmatter:
        errors.append("frontmatter missing")
    if len(H1_RE.findall(body)) != 1:
        errors.append(f"expected one body H1, found {len(H1_RE.findall(body))}")
    return errors, data, raw_frontmatter, body


def check_human_facing_body(raw_frontmatter: str, body: str, errors: list[str]) -> None:
    if FORBIDDEN_BODY_RE.search(body):
        errors.append("user-facing body contains HTML, %% comments, or per-item IDs")
    if VISIBLE_META_RE.search(body):
        errors.append("visible engineering metadata remains in user-facing body")
    if NESTED_ITEM_META_RE.search(raw_frontmatter):
        errors.append("per-item cards/questions metadata must move to an independent JSON index")
    lines = len(raw_frontmatter.splitlines())
    if lines > FRONTMATTER_LINE_LIMIT:
        errors.append(f"frontmatter is too large for a reading document: {lines} lines > {FRONTMATTER_LINE_LIMIT}")


def load_index(path: Path, data: dict[str, str], expected_type: str, id_field: str,
               expected_count: int, errors: list[str]) -> None:
    raw = data.get("metadata_index")
    if not raw:
        errors.append("frontmatter missing: metadata_index")
        return
    index_path = resolve_from(path, raw)
    if not index_path.exists():
        errors.append(f"unresolvable metadata_index: {raw}")
        return
    try:
        payload = json.loads(index_path.read_text(encoding="utf-8"))
    except Exception as exc:
        errors.append(f"cannot parse metadata_index JSON: {exc}")
        return
    if payload.get("asset_type") != expected_type:
        errors.append(f"metadata_index asset_type must be {expected_type}")
    source_document = payload.get("source_document")
    if not source_document:
        errors.append("metadata_index missing: source_document")
    elif resolve_from(index_path, str(source_document)) != path.resolve():
        errors.append("metadata_index source_document does not point back to this Markdown file")
    items = payload.get("items")
    if not isinstance(items, list):
        errors.append("metadata_index items must be a list")
        return
    if len(items) != expected_count:
        errors.append(f"metadata_index items={len(items)}, actual units={expected_count}")
    ids: list[str] = []
    positions: list[int] = []
    for number, item in enumerate(items, 1):
        if not isinstance(item, dict):
            errors.append(f"metadata_index item {number} is not an object")
            continue
        item_id = item.get(id_field)
        if not isinstance(item_id, str) or not item_id.strip():
            errors.append(f"metadata_index item {number} missing: {id_field}")
        else:
            ids.append(item_id)
        position = item.get("position")
        if not isinstance(position, int):
            errors.append(f"metadata_index item {number} position is not an integer")
        else:
            positions.append(position)
    if len(ids) != len(set(ids)):
        errors.append(f"metadata_index {id_field} values are not unique")
    if len(positions) != len(items) or positions != list(range(1, len(items) + 1)):
        errors.append("metadata_index positions must follow body order from 1 without gaps")


def validate_lecture(path: Path, text: str) -> list[str]:
    errors, data, _, _ = common(path, text)
    check_source(path, data, "source_transcript", errors)
    return errors


def validate_cards(path: Path, text: str) -> list[str]:
    errors, data, raw_frontmatter, body = common(path, text)
    check_human_facing_body(raw_frontmatter, body, errors)
    if re.search(r"(?m)^questions\s*:\s*$", raw_frontmatter):
        errors.append("active-recall card frontmatter must not use questions")
    check_source(path, data, "source_lecture", errors)
    check_source(path, data, "source_transcript", errors)
    counts = {
        "card headings": len(CARD_RE.findall(body)),
        "questions": len(QUESTION_PROMPT_RE.findall(body)),
        "answers": len(CARD_ANSWER_RE.findall(body)),
    }
    if len(set(counts.values())) != 1:
        errors.append("card unit counts disagree: " + ", ".join(f"{k}={v}" for k, v in counts.items()))
    total = as_int(data, "card_count_total", errors)
    actual = counts["card headings"]
    if total is not None and total != actual:
        errors.append(f"card_count_total={total}, actual={actual}")
    load_index(path, data, "active_recall_cards", "card_id", actual, errors)
    return errors


def validate_questions(path: Path, text: str) -> list[str]:
    errors, data, raw_frontmatter, body = common(path, text)
    check_human_facing_body(raw_frontmatter, body, errors)
    if re.search(r"(?m)^cards\s*:\s*$", raw_frontmatter):
        errors.append("training-question frontmatter must not use cards")
    check_source(path, data, "source_lecture", errors)
    counts = {
        "question headings": len(QUESTION_HEADING_RE.findall(body)),
        "questions": len(QUESTION_PROMPT_RE.findall(body)),
        "answers": len(QUESTION_ANSWER_RE.findall(body)),
    }
    if len(set(counts.values())) != 1:
        errors.append("question unit counts disagree: " + ", ".join(f"{k}={v}" for k, v in counts.items()))
    total = as_int(data, "question_count_total", errors)
    actual = counts["question headings"]
    if total is not None and total != actual:
        errors.append(f"question_count_total={total}, actual={actual}")
    load_index(path, data, "training_questions", "q_id", actual, errors)
    return errors


def clue_blocks(text: str) -> list[str]:
    matches = list(CLUE_RE.finditer(text))
    return [text[m.start() : matches[i + 1].start() if i + 1 < len(matches) else len(text)] for i, m in enumerate(matches)]


def field_value(block: str, field: str) -> str | None:
    match = re.search(rf"(?m)^(?:[-*]\s*)?(?:\*\*)?{re.escape(field)}(?:\*\*)?\s*[\uff1a:]\s*(.+)$", block)
    return match.group(1).strip() if match else None


def validate_clues(path: Path, text: str) -> list[str]:
    errors, _, _, body = common(path, text)
    blocks = clue_blocks(body)
    if not blocks:
        errors.append("no clue headings found")
        return errors
    for index, block in enumerate(blocks, 1):
        required = ["\u77e5\u8bc6\u5bf9\u8c61", "\u672c\u8bfe\u65b0\u589e", "\u8de8\u8bfe\u7406\u7531", "\u540e\u7eed\u89e6\u53d1", "\u8bc1\u636e\u72b6\u6001", "\u672c\u8bfe\u6765\u6e90"] if block.lstrip().startswith(("## \u7ebf\u7d22", "### \u7ebf\u7d22", "#### \u7ebf\u7d22")) else ["Knowledge object", "Current-lesson contribution", "Cross-lesson rationale", "Later trigger", "Evidence state", "Current-lesson source"]
        values = {field: field_value(block, field) for field in required}
        missing = [field for field, value in values.items() if not value]
        if missing:
            errors.append(f"clue {index} missing fields: {', '.join(missing)}")
            continue
        state = values[required[4]]
        if state not in VALID_STATES:
            errors.append(f"clue {index} invalid evidence state: {state}")
        if state in ("\u8de8\u8bfe\u5df2\u9a8c\u8bc1", "verified across lessons") and not field_value(block, "\u7b2c\u4e8c\u6765\u6e90" if required[4] == "\u8bc1\u636e\u72b6\u6001" else "Second source"):
            errors.append(f"clue {index} is cross-course verified but has no second source")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--kind", required=True, choices=["lecture", "cards", "questions", "clues"])
    parser.add_argument("paths", nargs="+", type=Path)
    args = parser.parse_args()
    validators = {
        "lecture": validate_lecture,
        "cards": validate_cards,
        "questions": validate_questions,
        "clues": validate_clues,
    }
    failed = False
    for path in args.paths:
        try:
            text = path.read_text(encoding="utf-8")
        except Exception as exc:
            print(f"FAIL {path}\n  - cannot read UTF-8: {exc}")
            failed = True
            continue
        errors = validators[args.kind](path, text)
        if errors:
            failed = True
            print(f"FAIL {path}")
            for error in errors:
                print(f"  - {error}")
        else:
            print(f"PASS {path} (structural only; target-interface rendering still required)")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
