#!/usr/bin/env python3
"""Convert straight double quotes in Chinese text to curly pairs.

Rules: inside a paragraph that contains Chinese characters, straight quotes alternate
open (“) / close (”). The count restarts at each blank line, heading, list item,
block quote and table row. Skipped untouched: the YAML header, fenced code blocks,
inline code, URLs and HTML tags. Everything else stays byte-identical.

Usage: fix_quotes.py <file> [--write]   (default: only list the changes)
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

OPEN, CLOSE = "“", "”"
CJK = re.compile(r"[㐀-鿿＀-￯　-〿]")
# Segments that must never be touched: inline code, URLs, HTML tags.
PROTECTED = re.compile(r"`+[^`]*`+|https?://[^\s\"“”<>)）]+|<[^<>\n]*>")
BLOCK_START = re.compile(r"\s{0,3}(#{1,6}\s|[-*+]\s|\d+[.)]\s|>|\|)")
FENCE = re.compile(r"\s{0,3}(```|~~~)")


def _split_lines(data: str):
    return data.splitlines(keepends=True)


def _yaml_end(lines) -> int:
    """Index of the first line after a leading YAML block (0 when there is none)."""
    if lines and lines[0].lstrip("﻿").rstrip("\r\n") == "---":
        for index, line in enumerate(lines[1:], 1):
            if line.rstrip("\r\n") == "---":
                return index + 1
    return 0


def _convert_line(line: str, state: list):
    """Convert quotes in one line; state[0] is True when the next quote opens."""
    out, pos = [], 0
    def plain(segment: str) -> str:
        pieces = []
        for ch in segment:
            if ch == '"':
                pieces.append(OPEN if state[0] else CLOSE)
                state[0] = not state[0]
            else:
                pieces.append(ch)
        return "".join(pieces)
    for match in PROTECTED.finditer(line):
        out.append(plain(line[pos:match.start()]))
        out.append(match.group(0))
        pos = match.end()
    out.append(plain(line[pos:]))
    return "".join(out)


def fix(data: str):
    """Return (new_text, changes, warnings); changes is a list of (line_no, old, new)."""
    lines = _split_lines(data)
    start = _yaml_end(lines)
    paragraphs, current, in_fence = [], [], False
    def flush():
        nonlocal current
        if current:
            paragraphs.append(current)
            current = []
    for index in range(start, len(lines)):
        line = lines[index]
        if FENCE.match(line):
            flush()
            in_fence = not in_fence
            continue
        if in_fence:
            continue
        if not line.strip():
            flush()
            continue
        if BLOCK_START.match(line):
            flush()
        current.append(index)
    flush()
    changes, warnings = [], []
    result = list(lines)
    for para in paragraphs:
        if not CJK.search("".join(lines[i] for i in para)):
            continue
        state = [True]
        for i in para:
            new = _convert_line(lines[i], state)
            if new != lines[i]:
                result[i] = new
                changes.append((i + 1, lines[i].rstrip("\r\n"), new.rstrip("\r\n")))
        if not state[0]:
            warnings.append(f"Odd number of straight quotes in the paragraph at line {para[0] + 1}; check it by hand")
    return "".join(result), changes, warnings


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description="Convert straight double quotes in Chinese text to curly pairs")
    parser.add_argument("file", type=Path)
    parser.add_argument("--write", action="store_true", help="rewrite the file in place (default: only list changes)")
    args = parser.parse_args(argv)
    data = args.file.read_bytes().decode("utf-8")
    new, changes, warnings = fix(data)
    for number, old, updated in changes:
        print(f"L{number}:\n  - {old}\n  + {updated}")
    for warning in warnings:
        print("WARNING:", warning)
    print(f"{len(changes)} line(s) changed" + ("; written" if args.write and changes else ""))
    if args.write and changes:
        args.file.write_bytes(new.encode("utf-8"))
    return 0


if __name__ == "__main__":
    sys.exit(main())
