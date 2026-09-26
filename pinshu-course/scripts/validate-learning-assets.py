#!/usr/bin/env python3
"""Mechanical checks for professional learning assets.

This script verifies counts, frontmatter, source paths, and the documented
English or legacy Chinese structural labels. It does not replace semantic QA
against the faithful transcript. The source stays ASCII-only; legacy labels are
represented with Unicode escapes.
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

FM_RE = re.compile(r"\A---\s*\n(.*?)\n---\s*\n", re.S)
H1_RE = re.compile(r"(?m)^#\s+\S")
CARD_EN_RE = re.compile(r"(?mi)^#{2,4}\s+Card\s*\d+\b")
CARD_ZH_RE = re.compile(r"(?m)^#{2,4}\s+\u5361(?:\u7247)?\s*\d+|^#{2,4}\s+\u5361\d+")
CARD_ID_RE = re.compile(r"\bcard_id\s*:\s*([A-Za-z0-9_-]+)")
QUESTION_EN_RE = re.compile(r"(?mi)^\*\*Question(?::)?\*\*\s*:?[ \t]*")
QUESTION_ZH_RE = re.compile(r"(?m)^\*\*(?:\u95ee\u9898|\u95ee)(?:[\uff1a:])?\*\*\s*[\uff1a:]?[ \t]*")
ANSWER_EN_RE = re.compile(r"<summary>\s*Answer\s*</summary>", re.I)
ANSWER_ZH_RE = re.compile(r"<summary>\s*\u7b54\u6848\s*</summary>")
CLUE_EN_RE = re.compile(r"(?mi)^#{2,4}\s+Clue\s*\d+\b")
CLUE_ZH_RE = re.compile(
    r"(?m)^#{2,4}\s+\u7ebf\u7d22"
    r"(?:\s*[\u4e00\u4e8c\u4e09\u56db\u4e94\u516d\u4e03\u516b\u4e5d\u5341\u767e]+|\s*\d+)"
)
VISIBLE_META_RE = re.compile(
    r"(?mi)^\*\*(?:Attributes?|Type|Status|\u5c5e\u6027|\u9898\u578b|\u7c7b\u578b|\u72b6\u6001)\*\*\s*[:\uff1a]"
)

CANONICAL_CLUE_FIELDS = (
    "knowledge_object",
    "current_lesson_contribution",
    "cross_lesson_rationale",
    "later_trigger",
    "evidence_state",
    "current_lesson_source",
)
FIELD_ALIASES = {
    "knowledge_object": {
        "en": "Knowledge object",
        "zh": "\u77e5\u8bc6\u5bf9\u8c61",
    },
    "current_lesson_contribution": {
        "en": "Current-lesson contribution",
        "zh": "\u672c\u8bfe\u65b0\u589e",
    },
    "cross_lesson_rationale": {
        "en": "Cross-lesson rationale",
        "zh": "\u8de8\u8bfe\u7406\u7531",
    },
    "later_trigger": {
        "en": "Later trigger",
        "zh": "\u540e\u7eed\u89e6\u53d1",
    },
    "evidence_state": {
        "en": "Evidence state",
        "zh": "\u8bc1\u636e\u72b6\u6001",
    },
    "current_lesson_source": {
        "en": "Current-lesson source",
        "zh": "\u672c\u8bfe\u6765\u6e90",
    },
    "second_source": {
        "en": "Second source",
        "zh": "\u7b2c\u4e8c\u6765\u6e90",
    },
}
CANONICAL_STATES = {
    "current-lesson candidate",
    "later-lesson foreshadowing",
    "verified across lessons",
    "safety-governance candidate",
}
STATE_ALIASES = {
    **{state: state for state in CANONICAL_STATES},
    "\u672c\u8bfe\u5019\u9009": "current-lesson candidate",
    "\u540e\u8bfe\u4f0f\u7b14": "later-lesson foreshadowing",
    "\u8de8\u8bfe\u5df2\u9a8c\u8bc1": "verified across lessons",
    "\u5b89\u5168\u6cbb\u7406\u5019\u9009": "safety-governance candidate",
}
STATE_LOCALES = {
    **{state: "en" for state in CANONICAL_STATES},
    "\u672c\u8bfe\u5019\u9009": "zh",
    "\u540e\u8bfe\u4f0f\u7b14": "zh",
    "\u8de8\u8bfe\u5df2\u9a8c\u8bc1": "zh",
    "\u5b89\u5168\u6cbb\u7406\u5019\u9009": "zh",
}


def frontmatter(text: str) -> dict[str, str]:
    match = FM_RE.search(text)
    if not match:
        return {}
    data: dict[str, str] = {}
    for line in match.group(1).splitlines():
        if ":" not in line or line[:1].isspace():
            continue
        key, value = line.split(":", 1)
        data[key.strip()] = value.strip().strip("'\"")
    return data


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


def check_source(path: Path, data: dict[str, str], key: str, errors: list[str]) -> None:
    value = data.get(key)
    if not value:
        errors.append(f"frontmatter missing: {key}")
        return
    raw = value.split("#", 1)[0].strip()
    target = Path(raw).expanduser()
    if not target.is_absolute():
        target = (path.parent / target).resolve()
    if not target.exists():
        errors.append(f"unresolvable {key}: {value}")


def common(path: Path, text: str) -> list[str]:
    errors: list[str] = []
    if len(H1_RE.findall(text)) != 1:
        errors.append(f"expected one H1, found {len(H1_RE.findall(text))}")
    return errors


def validate_lecture(path: Path, text: str) -> list[str]:
    errors = common(path, text)
    check_source(path, frontmatter(text), "source_transcript", errors)
    return errors


def validate_cards(path: Path, text: str) -> list[str]:
    errors = common(path, text)
    data = frontmatter(text)
    check_source(path, data, "source_lecture", errors)
    check_source(path, data, "source_transcript", errors)

    locale_counts = {
        "en": {
            "card headings": len(CARD_EN_RE.findall(text)),
            "questions": len(QUESTION_EN_RE.findall(text)),
            "answers": len(ANSWER_EN_RE.findall(text)),
        },
        "zh": {
            "card headings": len(CARD_ZH_RE.findall(text)),
            "questions": len(QUESTION_ZH_RE.findall(text)),
            "answers": len(ANSWER_ZH_RE.findall(text)),
        },
    }
    active_locales = {locale for locale, counts in locale_counts.items() if any(counts.values())}
    if len(active_locales) != 1:
        errors.append("card structural labels must use one documented label set per file")
    locale = next(iter(active_locales), "en")
    counts = {
        **locale_counts[locale],
        "card ids": len(CARD_ID_RE.findall(text)),
    }
    if len(set(counts.values())) != 1:
        errors.append("card unit counts disagree: " + ", ".join(f"{key}={value}" for key, value in counts.items()))
    ids = CARD_ID_RE.findall(text)
    if len(ids) != len(set(ids)):
        errors.append("card_id values are not unique")

    total = as_int(data, "card_count_total", errors)
    core = as_int(data, "core_card_count", errors)
    optional = as_int(data, "optional_card_count", errors)
    atomic = as_int(data, "atomic_card_count", errors)
    integrative = as_int(data, "integrative_card_count", errors)
    real_total = counts["card ids"]
    if total is not None and total != real_total:
        errors.append(f"card_count_total={total}, actual={real_total}")
    if None not in (total, core, optional) and total != core + optional:
        errors.append("core_card_count + optional_card_count != card_count_total")
    if None not in (total, atomic, integrative) and total != atomic + integrative:
        errors.append("atomic_card_count + integrative_card_count != card_count_total")
    if VISIBLE_META_RE.search(text):
        errors.append("visible card metadata remains in user-facing body")
    return errors


def clue_matches(text: str) -> list[tuple[int, str]]:
    matches = [(match.start(), "en") for match in CLUE_EN_RE.finditer(text)]
    matches.extend((match.start(), "zh") for match in CLUE_ZH_RE.finditer(text))
    return sorted(matches)


def clue_blocks(text: str) -> list[tuple[str, str]]:
    matches = clue_matches(text)
    return [
        (text[start : matches[index + 1][0] if index + 1 < len(matches) else len(text)], locale)
        for index, (start, locale) in enumerate(matches)
    ]


def raw_field_value(block: str, label: str) -> str | None:
    match = re.search(
        rf"(?m)^(?:[-*]\s*)?(?:"
        rf"\*\*{re.escape(label)}\*\*\s*[:\uff1a]\s*|"
        rf"\*\*{re.escape(label)}[:\uff1a]\*\*\s*|"
        rf"{re.escape(label)}\s*[:\uff1a]\s*)"
        rf"(.+)$",
        block,
    )
    return match.group(1).strip() if match else None


def field_value(block: str, field: str) -> tuple[str | None, str | None]:
    found = [
        (raw_field_value(block, label), locale)
        for locale, label in FIELD_ALIASES[field].items()
        if raw_field_value(block, label) is not None
    ]
    if len(found) != 1:
        return None, "mixed" if len(found) > 1 else None
    return found[0]


def normalize_evidence_state(value: str) -> str | None:
    """Normalize English and legacy Chinese values to one internal state enum."""
    return STATE_ALIASES.get(value.strip())


def evidence_state_locale(value: str) -> str | None:
    return STATE_LOCALES.get(value.strip())


def validate_clues(path: Path, text: str) -> list[str]:
    errors = common(path, text)
    blocks = clue_blocks(text)
    if not blocks:
        errors.append("no clue headings found")
        return errors
    for index, (block, heading_locale) in enumerate(blocks, 1):
        parsed = {field: field_value(block, field) for field in CANONICAL_CLUE_FIELDS}
        missing = [field for field, (value, _) in parsed.items() if not value]
        if missing:
            errors.append(f"clue {index} missing fields: {', '.join(missing)}")
            continue
        locales = {locale for _, locale in parsed.values() if locale}
        if "mixed" in locales or locales != {heading_locale}:
            errors.append(f"clue {index} mixes documented label sets")
            continue
        raw_state = parsed["evidence_state"][0]
        state = normalize_evidence_state(raw_state or "")
        if state is None:
            errors.append(f"clue {index} invalid evidence state: {raw_state}")
            continue
        if evidence_state_locale(raw_state or "") != heading_locale:
            errors.append(f"clue {index} mixes documented label sets")
            continue
        second_source, second_locale = field_value(block, "second_source")
        if second_source and second_locale != heading_locale:
            errors.append(f"clue {index} mixes documented label sets")
        if state == "verified across lessons" and not second_source:
            errors.append(f"clue {index} is verified across lessons but has no second source")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--kind", required=True, choices=["lecture", "cards", "clues"])
    parser.add_argument("paths", nargs="+", type=Path)
    args = parser.parse_args()
    validators = {"lecture": validate_lecture, "cards": validate_cards, "clues": validate_clues}
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
            print(f"PASS {path}")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
