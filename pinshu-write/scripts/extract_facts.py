#!/usr/bin/env python3
"""Pull every checkable sentence out of a draft into a fact sheet (references/5-review.md, step 5).

The writer never makes this sheet: a writer that invented a number would leave it off a list it made itself.
The script lists every sentence holding a number, a date, a percentage, a quote mark, a colon after a verb of
saying ("说：", "写过：", "说得更干脆：") or a Latin-script name, with its body paragraph number (the title and
subheads are not counted, the same numbering the reviewers use).
With --previous, each line is marked against the previous sheet (step 8): 旧 when the sentence is identical,
改 when a previous sentence is close to it, 新 otherwise; only 新 and 改 lines go to the fact checker.
People, companies and events written only in Chinese characters are added by a model afterwards
(prompts.md, "Fact sheet: names"); the script judges nothing.

Usage:
  python3 extract_facts.py draft.md
  python3 extract_facts.py draft.md --out tmp/fact-sheet.md
  python3 extract_facts.py draft-v2.md --previous tmp/fact-sheet.md --out tmp/fact-sheet-v2.md
"""
from __future__ import annotations

import argparse
import difflib
import re
import sys
from pathlib import Path

STOP_HEADINGS = ("## 参考文章", "===EDITOR NOTES===")
SENTENCE_END = re.compile(r"(?<=[。！？；!?;])")
CHINESE_NUMBER = "零一二三四五六七八九十百千万亿两半"
PATTERNS = (
    ("number", re.compile(r"[0-9０-９]")),
    ("number", re.compile(rf"[{CHINESE_NUMBER}]+多?(?:个|家|位|名|年|月|日|倍|成|万|亿|元|岁|次|款|期|天|小时|分钟|篇|条|项|种)")),
    ("percent", re.compile(r"[%％]|百分之")),
    ("quote", re.compile(r"[“”「」『』\"]")),
    ("quote", re.compile(r"(?:说|写过|写道|讲过|表示|提到)[^。！？；：:]{0,6}[：:]")),
    ("latin", re.compile(r"[A-Za-z][A-Za-z0-9.&'\-]+")),
)


def body_paragraphs(text: str) -> list[tuple[int, str]]:
    """Return (paragraph number, text) for body paragraphs, stopping at the references block or editor notes."""
    paragraphs = []
    number = 0
    for block in re.split(r"\n\s*\n", text):
        block = block.strip()
        if not block:
            continue
        if block.startswith(STOP_HEADINGS):
            break
        if block.startswith("#"):
            continue
        number += 1
        paragraphs.append((number, " ".join(line.strip() for line in block.splitlines())))
    return paragraphs


def title_of(text: str) -> str:
    for line in text.splitlines():
        if line.startswith("# "):
            return line[2:].strip()
    return ""


def _counts(kind: str, pattern: re.Pattern, sentence: str) -> bool:
    if kind == "number" and pattern is PATTERNS[1][1]:
        # "一家""一个" are everyday words, not facts; "三家""一百个" stay.
        return any(not re.fullmatch(r"一.", m.group(0)) for m in pattern.finditer(sentence))
    return bool(pattern.search(sentence))


def kinds_in(sentence: str) -> list[str]:
    found = []
    for kind, pattern in PATTERNS:
        if kind not in found and _counts(kind, pattern, sentence):
            found.append(kind)
    return found


def extract(text: str) -> list[dict]:
    rows = []
    title = title_of(text)
    if title and kinds_in(title):
        rows.append({"paragraph": "标题", "sentence": title, "kinds": kinds_in(title)})
    for number, paragraph in body_paragraphs(text):
        for sentence in SENTENCE_END.split(paragraph):
            sentence = sentence.strip()
            if not sentence:
                continue
            kinds = kinds_in(sentence)
            if kinds:
                rows.append({"paragraph": number, "sentence": sentence, "kinds": kinds})
    return rows


KIND_LABEL = {"number": "数字", "percent": "百分比", "quote": "引语", "latin": "外文名"}
CLOSE_ENOUGH = 0.6  # a revised sentence keeping most of its words counts as 改, not 新


def previous_sentences(sheet: str) -> list[str]:
    """Sentences of an earlier sheet, paragraph marks stripped.

    The sentence column is found by its header ("原句"), so this reads the script's own sheet, the merged
    four-column sheet and a fact checker's output alike.
    """
    found = []
    column = None
    for line in sheet.splitlines():
        if not line.strip().startswith("|"):
            continue
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        headers = [i for i, c in enumerate(cells) if c.startswith("原句")]
        if headers:
            column = headers[0]
            continue
        if column is None or len(cells) <= column or set("".join(cells)) <= set("-: "):
            continue
        sentence = re.sub(r"[（(][^（）()]*[）)]$", "", cells[column]).replace("｜", "|").strip()
        if sentence:
            found.append(sentence)
    return found


def mark(rows: list[dict], previous: list[str]) -> list[dict]:
    """Return copies of rows, each with mark 旧, 改 or 新 against the previous sheet."""
    marked = []
    for row in rows:
        if row["sentence"] in previous:
            label = "旧"
        elif any(difflib.SequenceMatcher(None, row["sentence"], old).ratio() >= CLOSE_ENOUGH for old in previous):
            label = "改"
        else:
            label = "新"
        marked.append({**row, "mark": label})
    return marked


def render(rows: list[dict], source: str) -> str:
    with_marks = bool(rows) and "mark" in rows[0]
    lines = [
        f"# 核对表（从 {source} 机械抽取）",
        "",
        "写手不改这张表。人名、公司、机构、事件只写汉字的，由模型另外补（prompts.md，Fact sheet: names）。",
        "出处和状态两栏留给核查官。",
    ]
    if with_marks:
        lines.append("新／改／旧对的是上一张表：旧行带上次的状态，不再核；新和改的行发给核查官。")
    lines.append("")
    if with_marks:
        lines += ["| # | 内容类型 | 原句（段落号） | 出处 | 状态 | 新／改／旧 |", "|---|---|---|---|---|---|"]
    else:
        lines += ["| # | 内容类型 | 原句（段落号） | 出处 | 状态 |", "|---|---|---|---|---|"]
    for i, row in enumerate(rows, 1):
        kinds = "、".join(KIND_LABEL[k] for k in row["kinds"])
        sentence = row["sentence"].replace("|", "｜")
        line = f"| {i} | {kinds} | {sentence}（{row['paragraph']}） |  |  |"
        lines.append(line + (f" {row['mark']} |" if with_marks else ""))
    lines.append("")
    lines.append(f"共 {len(rows)} 条。")
    if with_marks:
        counts = {k: sum(r["mark"] == k for r in rows) for k in ("新", "改", "旧")}
        lines.append(f"新 {counts['新']} / 改 {counts['改']} / 旧 {counts['旧']}。")
    return "\n".join(lines) + "\n"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("draft")
    parser.add_argument("--out", help="write the sheet here instead of printing it")
    parser.add_argument("--previous", help="the sheet of the previous version; marks each line 新, 改 or 旧")
    args = parser.parse_args(argv)
    path = Path(args.draft)
    if not path.is_file():
        print(f"not found: {path}", file=sys.stderr)
        return 2
    rows = extract(path.read_text(encoding="utf-8"))
    if args.previous:
        previous = Path(args.previous)
        if not previous.is_file():
            print(f"not found: {previous}", file=sys.stderr)
            return 2
        rows = mark(rows, previous_sentences(previous.read_text(encoding="utf-8")))
    sheet = render(rows, path.name)
    if args.out:
        Path(args.out).write_text(sheet, encoding="utf-8")
        print(f"wrote {args.out}")
    else:
        sys.stdout.write(sheet)
    return 0


if __name__ == "__main__":
    sys.exit(main())
