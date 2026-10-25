#!/usr/bin/env python3
"""Scan a fact checker's table for lines marked 有出处 whose note admits a difference (references/5-review.md,
"Checking the fact checker's pass one").

A note that says 但, 注, 大体, 基本, 略有出入, 口径不同 or 两说 means the source and the sentence differ, so the line
cannot be 有出处. This reads the fact checker's output, not the draft: extract_facts.py pulls facts from a draft and
audit_draft.py checks a draft, so neither covers it. It judges nothing else.

Usage:
  python3 check_fact_notes.py tmp/06-fact1-<model>/out.md
Exit code 1 when any line is flagged, 0 when none, 2 when the table cannot be read.
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

ADMITS_DIFFERENCE = re.compile(r"但|(?<![关备标])注|大体|基本|略有出入|口径不同|两说")
SOURCED = "有出处"


def cells(line: str) -> list[str]:
    return [c.strip() for c in line.strip().strip("|").split("|")]


def flagged_lines(table: str) -> list[tuple[int, str, str]] | None:
    """Return (line number, status, note) for every 有出处 line whose note admits a difference.

    None when no table with both a 状态 and a 说明 column is found.
    """
    status_at = note_at = None
    found_header = False
    flagged = []
    for number, line in enumerate(table.splitlines(), 1):
        if not line.strip().startswith("|"):
            continue
        row = cells(line)
        if "状态" in row and "说明" in row:
            status_at, note_at, found_header = row.index("状态"), row.index("说明"), True
            continue
        if status_at is None or set("".join(row)) <= set("-: "):
            continue
        if len(row) <= max(status_at, note_at):
            continue
        status, note = row[status_at], row[note_at]
        if status.startswith(SOURCED) and ADMITS_DIFFERENCE.search(note):
            flagged.append((number, status, note))
    return flagged if found_header else None


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("output", help="the fact checker's output file")
    args = parser.parse_args(argv)
    path = Path(args.output)
    if not path.is_file():
        print(f"not found: {path}", file=sys.stderr)
        return 2
    flagged = flagged_lines(path.read_text(encoding="utf-8"))
    if flagged is None:
        print("no table with 状态 and 说明 columns", file=sys.stderr)
        return 2
    if not flagged:
        print("未发现：标了有出处的行，说明栏都没有写出入。")
        return 0
    print(f"{len(flagged)} 行标了有出处，说明栏却写了出入，这一遍不算过：")
    for number, status, note in flagged:
        print(f"- 第 {number} 行｜{status}｜{note}")
    return 1


if __name__ == "__main__":
    sys.exit(main())
