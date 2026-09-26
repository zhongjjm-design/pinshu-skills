#!/usr/bin/env python3
"""Executable consistency checks for language, paths, attribution, and routing."""
from __future__ import annotations

import re
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
PACKAGES = (
    "pinshu-course",
    "pinshu-study",
    "pinshu-course-capture",
    "pinshu-transcript",
    "pinshu-distill",
    "pinshu-md2pdf",
)
DOC_ROOTS = tuple(REPO / name for name in PACKAGES)
FORBIDDEN_PATHS = re.compile(
    r"(?:00[_-](?:course-map|Course-Map)|01_Faithfully-Edited-Transcripts|"
    r"02_Structured-Lectures|03[_-]cross-topic-knowledge-base|"
    r"03_Cross-Lesson-Methodology|04_Case-Library|05_Tools-and-Checklists|"
    r"06_Fact-Checking|07_Exercises-and-Assignments|assets/(?:Lesson|lesson)-XX)",
    re.I,
)
ATTRIBUTION_LINE = re.compile(
    r"^(?:- (?:Original work|Owner|Maintainer|Owner and maintainer)|"
    r"Aidan \(Pinshu\) (?:maintains|created and maintains))"
)


def markdown_files() -> list[Path]:
    files = [REPO / "README.md"]
    for root in DOC_ROOTS:
        files.extend(sorted(root.rglob("*.md")))
    return files


def main() -> int:
    errors: list[str] = []
    for path in markdown_files():
        text = path.read_text(encoding="utf-8")
        relative = path.relative_to(REPO)
        for line_no, line in enumerate(text.splitlines(), 1):
            if FORBIDDEN_PATHS.search(line):
                errors.append(f"{relative}:{line_no}: translated runtime path literal")
            if ("Aidan" in line or "Hermes" in line) and not ATTRIBUTION_LINE.match(line):
                errors.append(f"{relative}:{line_no}: non-attribution personal or agent name")

    contract_files = (
        REPO / "pinshu-course" / "SKILL.md",
        REPO / "pinshu-study" / "SKILL.md",
        REPO / "pinshu-course-capture" / "SKILL.md",
        REPO / "pinshu-transcript" / "SKILL.md",
        REPO / "pinshu-distill" / "SKILL.md",
    )
    for path in contract_files:
        text = path.read_text(encoding="utf-8")
        if "output_language" not in text:
            errors.append(f"{path.relative_to(REPO)}: missing output_language contract")
        if "manifest" not in text or "path" not in text:
            errors.append(f"{path.relative_to(REPO)}: missing manifest/path contract")

    optional_dependency_files = (
        REPO / "README.md",
        REPO / "pinshu-transcript" / "SKILL.md",
        REPO / "pinshu-distill" / "SKILL.md",
    )
    for path in optional_dependency_files:
        text = path.read_text(encoding="utf-8")
        if "pinshu-data-cleaning" not in text or not ("not bundled" in text or "not included" in text):
            errors.append(f"{path.relative_to(REPO)}: optional dependency is not explicit")

    if errors:
        print("runtime_contracts self-test: FAIL")
        for error in errors:
            print(f"  - {error}")
        return 1
    print(f"runtime_contracts self-test: PASS ({len(markdown_files())} Markdown files)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
