#!/usr/bin/env python3
"""Mechanical checks for a Chinese long-form article draft (pinshu-write).

The script counts and locates. It never rewrites text and never decides
whether an article is good: semantic review stays with independent reviewers
and the author. Exit code 1 means at least one blocker was found.

Usage:
  python3 audit_draft.py --rules            (print the Chinese rules once before writing)
  python3 audit_draft.py draft.md
  python3 audit_draft.py draft.md --banned-file my_banned_words.txt --length 2500-4000
  python3 audit_draft.py draft.md --json
"""
from __future__ import annotations

import argparse
import json
import re
import statistics
import sys
from pathlib import Path

SOURCES_HEADINGS = ("\u8d44\u6599\u6765\u6e90", "\u53c2\u8003\u8d44\u6599", "\u4fe1\u606f\u6765\u6e90")
NOTES_MARKERS = ("===EDITOR NOTES===", "===\u7f16\u8f91\u5907\u6ce8===")
DEFAULT_BANNED = (
    "\u9274\u4e8e", "\u7efc\u4e0a\u6240\u8ff0", "\u503c\u5f97\u6ce8\u610f\u7684\u662f", "\u4e0d\u96be\u53d1\u73b0", "\u663e\u800c\u6613\u89c1",
    "\u8d4b\u80fd", "\u98a0\u8986", "\u672a\u6765\u5df2\u6765", "\u91cd\u65b0\u5b9a\u4e49",
)
META_PHRASES = ("\u672c\u6587", "\u8fd9\u7bc7\u6587\u7ae0", "\u63a5\u4e0b\u6765\u6211\u4eec", "\u603b\u7ed3\u4e00\u4e0b", "\u4e0b\u9762\u6211\u4eec", "\u8ba9\u6211\u4eec\u4e00\u8d77")
SECOND_PERSON = "\u4f60"
CJK = re.compile(r"[\u4e00-\u9fff]")
REVERSALS = (
    ("single-sentence reversal: not X but Y", re.compile(r"\u4e0d\u662f[^\u3002\uff01\uff1f\uff1b\n]{1,40}?\u800c\u662f")),
    ("single-sentence reversal: not X, (it) is Y", re.compile(r"\u4e0d\u662f[^\u3002\uff01\uff1f\uff1b\n\uff0c]{1,30}\uff0c\u662f")),
    ("single-sentence reversal: lies not in X but in Y", re.compile(r"\u4e0d\u5728\u4e8e[^\u3002\uff01\uff1f\uff1b\n]{1,40}?\u800c\u5728\u4e8e")),
    ("single-sentence reversal: A rather than B", re.compile(r"\uff0c\u800c\u4e0d\u662f")),
)
DASH = re.compile(r"[\u2014\u2015]")
EMOJI = re.compile(r"[\U0001F300-\U0001FAFF\u2600-\u27bf]")
INLINE_SOURCE = re.compile(r"[\uff08(][^\uff09)\n]{0,30}(?:19|20)\d{2}[^\uff09)\n]{0,15}[\uff09)]")
NUMBER = re.compile(r"\d+(?:[.,]\d+)?%?")
ORDINAL_OPENERS = ("\u9996\u5148", "\u5176\u6b21")
HYPOTHETICAL_OPENERS = ("\u5047\u8bbe", "\u8bbe\u60f3")
LATIN_TERM = re.compile(r"[A-Za-z][A-Za-z0-9.'-]*(?: [A-Za-z][A-Za-z0-9.'-]*)*")
COMMON_LATIN = {"AI", "CEO", "PPT", "APP", "App", "app"}
# Prompt colons and abrupt paragraph-opening comments: patterns from the
# podcast-to-article check_style.py, based on lieflat-less-ai-tone (MIT).
# Human texts: about 0.08 prompt colons per 1000 characters, AI about 0.30;
# abrupt comment openings in 0.14% of non-first paragraphs, AI 0.62%.
# The human corpus is not public, so these baselines cannot be recomputed.
PROMPT_COLON = re.compile(r"(?:\u4e00\u53e5\u8bdd(?:\u603b\u7ed3|\u8bf4|\u6982\u62ec)|\u7b80\u5355\u8bf4|\u8bf4\u767d\u4e86|\u603b\u7ed3|\u5c0f\u7ed3|\u7ed3\u8bba|\u6838\u5fc3(?:\u662f|\u5728\u4e8e|\u89c2\u70b9)?|\u5173\u952e(?:\u662f|\u5728\u4e8e)?|\u91cd\u70b9(?:\u662f)?|\u539f\u56e0(?:\u5982\u4e0b|\u6709|\u5728\u4e8e)?|\u95ee\u9898(?:\u662f|\u5728\u4e8e)?|\u7b54\u6848(?:\u662f)?|\u672c\u8d28(?:\u662f|\u4e0a)?|\u5b9a\u4e49(?:\u662f)?|\u5177\u4f53(?:\u6765\u8bf4|\u5982\u4e0b|\u5305\u62ec)?|\u4e3e\u4f8b(?:\u6765\u8bf4)?|\u6362\u53e5\u8bdd\u8bf4|\u4e5f\u5c31\u662f\u8bf4|\u6211\u7684(?:\u89c2\u70b9|\u5224\u65ad|\u7ed3\u8bba)|\u5efa\u8bae(?:\u662f)?)[\uff1a:]")
COMMENT_OPENING = re.compile(r"^(?:\u542c\u8d77\u6765|\u770b\u8d77\u6765|\u770b\u4e0a\u53bb|\u542c\u4e0a\u53bb|\u8bf4\u767d\u4e86|\u8bf4\u5230\u5e95|\u6362\u53e5\u8bdd\u8bf4|\u610f\u5473\u7740|\u503c\u5f97\u6ce8\u610f|\u4e0d\u96be\u770b\u51fa|\u7ec6\u770b|\u518d\u770b|\u56de\u8fc7\u5934\u770b|\u95ee\u9898\u5728\u4e8e|\u539f\u56e0\u5728\u4e8e|\u7ed3\u679c\u662f|\u6709\u610f\u601d\u7684\u662f|\u66f4\u91cd\u8981\u7684\u662f|\u5173\u952e\u5728\u4e8e|\u771f\u6b63\u7684)")
ANAPHOR_OPENING = re.compile(r"^(?:\u8fd9|\u90a3|\u5176|\u6b64|\u4e0a\u9762|\u524d\u9762|\u521a\u624d|\u4ee5\u4e0a|\u8be5|\u5b83|\u4ed6|\u5979|\u5b83\u4eec|\u4ed6\u4eec|\u540c\u6837|\u7c7b\u4f3c|\u76f8\u6bd4|\u53cd\u8fc7\u6765|\u4f46|\u4e0d\u8fc7|\u6240\u4ee5|\u56e0\u6b64|\u4e8e\u662f|\u800c|\u53e6|\u9664\u6b64|\u4e0e\u6b64)")

RULES_TEXT = """
\u5199\u7a3f\u89c4\u77e9\uff08\u4e2d\u6587\u539f\u6837\uff0c\u4f9b\u5199\u7a3f\u548c\u5ba1\u7a3f\u7684\u6a21\u578b\u5bf9\u7167\uff09

\u4e0d\u7528\u7684\u8bcd\uff08\u9ed8\u8ba4\uff0c\u8d26\u53f7\u753b\u50cf\u91cc\u7684\u53e6\u52a0\uff09\uff1a
  {banned}

\u4e0d\u7528\u7684\u53e5\u5f0f\uff08\u8fde\u6210\u4e00\u53e5\u7684\u53cd\u8f6c\uff09\uff1a
  \u4e0d\u662f\u2026\u2026\u800c\u662f\u2026\u2026
  \u4e0d\u662f\u2026\u2026\uff0c\u662f\u2026\u2026
  \u4e0d\u5728\u4e8e\u2026\u2026\u800c\u5728\u4e8e\u2026\u2026
  \u2026\u2026\uff0c\u800c\u4e0d\u662f\u2026\u2026
  \u53ef\u4ee5\u5076\u5c14\u7528\u53e5\u53f7\u65ad\u5f00\u7684\u77ed\u53cd\u8f6c\uff1a\u201c\u4e0d\u662f A\u3002\u662f B\u3002\u201d

\u6807\u70b9\uff1a
  \u4e0d\u7528\u7834\u6298\u53f7\uff08\u2014\u2014\uff09\uff0c\u6539\u7528\u5192\u53f7\u3001\u62ec\u53f7\u6216\u62c6\u53e5
  \u4e2d\u6587\u6807\u70b9\u5168\u89d2\uff0c\u5f15\u53f7\u7528\u201c\u201d\uff0c\u4e0d\u7528\u82f1\u6587\u5f15\u53f7
  \u6b63\u6587\u4e0d\u52a0\u7c97\uff0c\u4e0d\u7528 emoji\uff0c\u5168\u6587\u53ea\u6709\u4e00\u4e2a\u4e00\u7ea7\u6807\u9898

\u4e0d\u5199\u5143\u89e3\u8bf4\uff1a
  {meta}

\u5c11\u7528\u63d0\u793a\u6027\u5192\u53f7\uff1a\u4e00\u53e5\u8bdd\u6982\u62ec\uff1a\u3001\u7b80\u5355\u8bf4\uff1a\u3001\u95ee\u9898\u662f\uff1a\u3001\u5173\u952e\u662f\uff1a\u3001\u7b54\u6848\u662f\uff1a\u8fd9\u7c7b\uff0c\u76f4\u63a5\u8bf4\uff08\u63d0\u9192\uff0c\u4e0d\u62e6\u7a3f\uff09
\u6bb5\u9996\u522b\u7a81\u5140\u70b9\u8bc4\uff1a\u503c\u5f97\u6ce8\u610f\u3001\u95ee\u9898\u5728\u4e8e\u3001\u5173\u952e\u5728\u4e8e\u3001\u66f4\u91cd\u8981\u7684\u662f\u3001\u8bf4\u5230\u5e95\u8fd9\u7c7b\u5f00\u5934\uff0c\u53c8\u6ca1\u7528\u8fd9\u3001\u90a3\u3001\u4f46\u3001\u6240\u4ee5\u63a5\u4e0a\u6587\u7684\uff08\u63d0\u9192\uff09

\u4e0d\u7528\u5217\u8868\u8154\u5f00\u5934\uff1a\u9996\u5148\u3001\u5176\u6b21\u3001\u6700\u540e

\u51fa\u5904\u653e\u6587\u672b\u201c\u8d44\u6599\u6765\u6e90\u201d\uff0c\u6b63\u6587\u4e0d\u5939\u62ec\u53f7\u51fa\u5904\uff1b\u4e00\u6bb5\u6700\u591a\u4e00\u4e2a\u4f8b\u5b50\u3001\u4e00\u7ec4\u6570\u5b57\u3002
\u4e0d\u7f16\u201c\u5f88\u591a\u4eba\u8bf4\u201d\u201c\u670b\u53cb\u8ddf\u6211\u8bf4\u201d\u8fd9\u7c7b\u6ca1\u51fa\u5904\u7684\u4eba\uff1b\u4e0d\u7f16\u6599\u91cc\u6ca1\u6709\u7684\u7ea6\u6570\uff08\u201c\u524d\u4e24\u5e74\u201d\u201c\u4e09\u5230\u56db\u6210\u201d\uff09\u3002
"""


def cjk_len(text: str) -> int:
    return len(CJK.findall(text))


def split_body(text: str) -> tuple[list[tuple[int, str]], int]:
    """Return numbered body lines (before sources/notes) and the cut line number."""
    lines = text.splitlines()
    body: list[tuple[int, str]] = []
    cut = len(lines)
    skip_until = 0
    if lines and lines[0].strip() == "---":
        for index, line in enumerate(lines[1:], 2):
            if line.strip() == "---":
                skip_until = index
                break
    for index, line in enumerate(lines, 1):
        if index <= skip_until:
            continue
        stripped = line.strip().lstrip("#").strip()
        if stripped in SOURCES_HEADINGS or any(line.strip().startswith(m) for m in NOTES_MARKERS):
            cut = index
            break
        body.append((index, line))
    while body and body[-1][1].strip() in {"", "---"}:
        body.pop()
    return body, cut


def excerpt(line: str, start: int, width: int = 36) -> str:
    left = max(0, start - 8)
    return line[left:left + width].strip()


def audit(text: str, banned: list[str], length: tuple[int, int], hard_max: int,
          section_min: int, section_max: int, you_per_k: float, para_max: int,
          subhead_range: tuple[int, int] = (8, 14)) -> dict:
    findings: list[dict] = []

    def add(level: str, rule: str, line_no: int | None, detail: str) -> None:
        findings.append({"level": level, "rule": rule, "line": line_no, "detail": detail})

    body, _ = split_body(text)
    h1 = [n for n, line in body if re.match(r"^#\s+\S", line)]
    if len(h1) != 1:
        add("blocker", "exactly one H1 title", h1[0] if h1 else None, f"found {len(h1)} H1 lines")

    paragraphs: list[tuple[int, str]] = []
    sections: list[dict] = [{"title": "(opening)", "line": 1, "chars": 0}]
    for number, line in body:
        stripped = line.strip()
        if not stripped or stripped == "---":
            continue
        if stripped.startswith("## "):
            sections.append({"title": stripped[3:].strip(), "line": number, "chars": 0})
            continue
        if stripped.startswith("#"):
            continue
        paragraphs.append((number, stripped))
        sections[-1]["chars"] += cjk_len(stripped)

    for number, line in body:
        for match in DASH.finditer(line):
            add("blocker", "no em dash", number, excerpt(line, match.start()))
        for label, pattern in REVERSALS:
            for match in pattern.finditer(line):
                add("blocker", label, number, match.group(0)[:40])
        for word in banned:
            if word and word in line:
                add("blocker", "banned word", number, word)
        for match in EMOJI.finditer(line):
            add("blocker", "no emoji", number, excerpt(line, match.start()))

    for number, para in paragraphs:
        if '"' in para and CJK.search(para):
            add("fix", "use curly Chinese quotes \u201c \u201d", number, excerpt(para, para.index('"')))
        if "**" in para:
            add("fix", "no bold in body text", number, excerpt(para, para.index("**")))
        for match in INLINE_SOURCE.finditer(para):
            add("fix", "move inline source to the end source list", number, match.group(0))
        for phrase in META_PHRASES:
            if phrase in para:
                add("warn", "meta narration", number, phrase)
        size = cjk_len(para)
        if size > para_max:
            add("warn", f"long paragraph (> {para_max} characters)", number, f"{size} characters")
        for match in PROMPT_COLON.finditer(para):
            add("warn", "prompt colon: say it plainly instead of announcing it", number, match.group(0))
        numbers = set(NUMBER.findall(para))
        if len(numbers) > 3:
            add("warn", "more than three numbers in one paragraph", number, ", ".join(sorted(numbers))[:60])

    for index, (number, para) in enumerate(paragraphs):
        if index and COMMENT_OPENING.match(para) and not ANAPHOR_OPENING.match(para):
            add("warn", "abrupt comment opens a paragraph without linking to the previous one", number, para[:20])

    openers = [n for n, p in paragraphs if p.startswith(ORDINAL_OPENERS)]
    if len(openers) >= 2:
        add("warn", "first/second ordinal paragraph openers read like a list", openers[0], f"{len(openers)} paragraphs")

    titles = [s for s in sections[1:]]
    if titles:
        lengths = [len(s["title"].replace(" ", "")) for s in titles]
        for s, size in zip(titles, lengths):
            if size < subhead_range[0] or size > subhead_range[1]:
                add("warn", f"subhead length outside {subhead_range[0]}-{subhead_range[1]} characters", s["line"],
                    f"{s['title'][:24]}: {size}")
        if len(lengths) >= 2 and max(lengths) - min(lengths) > 5:
            add("warn", "subhead lengths differ by more than 5 characters", None,
                f"shortest {min(lengths)}, longest {max(lengths)}")

    opening = [p for n, p in paragraphs if n < (sections[1]["line"] if len(sections) > 1 else 10**9)][:2]
    if any(p.startswith(HYPOTHETICAL_OPENERS) or (HYPOTHETICAL_OPENERS[0] + SECOND_PERSON) in p for p in opening):
        add("warn", "opening uses a hypothetical scene; check how recent articles opened and vary it", None,
            opening[0][:30] if opening else "")

    seen_terms: set[str] = set()
    for number, para in paragraphs:
        for match in LATIN_TERM.finditer(para):
            term = match.group(0).rstrip(".'-")
            if len(term) < 3 or term in COMMON_LATIN or term in seen_terms:
                continue
            seen_terms.add(term)
            add("warn", "foreign term: explain it in plain words at first use", number, term)

    total = sum(cjk_len(p) for _, p in paragraphs)
    if total > hard_max:
        add("blocker", f"body longer than the hard maximum {hard_max}", None, f"{total} characters")
    elif not length[0] <= total <= length[1]:
        add("warn", f"body outside the usual range {length[0]}-{length[1]}", None, f"{total} characters")

    you = sum(p.count(SECOND_PERSON) for _, p in paragraphs)
    density = you * 1000 / total if total else 0.0
    if density > you_per_k:
        add("warn", f"second person above {you_per_k:g} per 1000 characters", None, f"{you} uses, {density:.1f} per 1000")

    named = [s for s in sections[1:]]
    for section in named:
        if section["chars"] < section_min or section["chars"] > section_max:
            add("warn", f"section outside {section_min}-{section_max} characters", section["line"],
                f"{section['title'][:24]}: {section['chars']}")
    if len(named) >= 2:
        sizes = [s["chars"] for s in named if s["chars"]]
        if sizes and max(sizes) > 2.5 * max(1, min(sizes)):
            add("warn", "sections are unbalanced (largest > 2.5x smallest)", None,
                f"min {min(sizes)}, max {max(sizes)}, median {statistics.median(sizes):g}")

    order = {"blocker": 0, "fix": 1, "warn": 2}
    findings.sort(key=lambda f: (order[f["level"]], f["line"] or 0))
    return {
        "stats": {
            "body_characters": total,
            "paragraphs": len(paragraphs),
            "sections": [{"title": s["title"], "characters": s["chars"]} for s in sections],
            "second_person": you,
        },
        "counts": {level: sum(1 for f in findings if f["level"] == level) for level in order},
        "findings": findings,
    }


def parse_range(value: str) -> tuple[int, int]:
    low, _, high = value.partition("-")
    return int(low), int(high)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("draft", type=Path, nargs="?")
    parser.add_argument("--rules", action="store_true", help="print the Chinese rules this script enforces, then exit")
    parser.add_argument("--banned-file", type=Path, help="UTF-8 text file, one extra banned word per line")
    parser.add_argument("--no-default-banned", action="store_true", help="use only the banned-file list")
    parser.add_argument("--length", type=parse_range, default=(2500, 4000), help="usual body range, e.g. 2500-4000")
    parser.add_argument("--hard-max", type=int, default=6000)
    parser.add_argument("--section-min", type=int, default=300)
    parser.add_argument("--section-max", type=int, default=900)
    parser.add_argument("--para-max", type=int, default=200)
    parser.add_argument("--subhead", type=parse_range, default=(8, 14), help="usual subhead length, e.g. 8-14")
    parser.add_argument("--you-per-k", type=float, default=10.0)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    banned = [] if args.no_default_banned else list(DEFAULT_BANNED)
    if args.banned_file:
        for raw in args.banned_file.read_text(encoding="utf-8").splitlines():
            word = raw.strip()
            if word and not word.startswith("#"):
                banned.append(word)
    if args.rules:
        print(RULES_TEXT.format(banned="\u3001".join(banned), meta="\u3001".join(META_PHRASES)))
        return 0
    if args.draft is None:
        parser.error("a draft path is required unless --rules is given")
    text = args.draft.read_text(encoding="utf-8")
    report = audit(text, banned, args.length, args.hard_max, args.section_min,
                   args.section_max, args.you_per_k, args.para_max, args.subhead)
    if args.json:
        print(json.dumps(report, ensure_ascii=False, indent=2))
    else:
        stats = report["stats"]
        print(f"body characters: {stats['body_characters']}  paragraphs: {stats['paragraphs']}  "
              f"second person: {stats['second_person']}")
        for section in stats["sections"]:
            print(f"  section {section['characters']:>5}  {section['title']}")
        counts = report["counts"]
        print(f"blockers: {counts['blocker']}  fixes: {counts['fix']}  warnings: {counts['warn']}")
        for finding in report["findings"]:
            where = f"L{finding['line']}" if finding["line"] else "--"
            print(f"[{finding['level']}] {where} {finding['rule']}: {finding['detail']}")
    return 1 if report["counts"]["blocker"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
