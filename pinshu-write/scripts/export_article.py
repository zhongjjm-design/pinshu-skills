#!/usr/bin/env python3
"""Export the article before the exact editor-notes marker, preserving its bytes."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
from datetime import datetime
from pathlib import Path


def export(source: Path, out: Path) -> Path:
    source = source.resolve()
    data = source.read_bytes()
    # Preserve frontmatter, sources, punctuation, newlines and UTF-8 BOM exactly.
    lines = data.splitlines(keepends=True)
    markers = [i for i, line in enumerate(lines)
               if line.rstrip(b"\r\n") == b"===EDITOR NOTES==="]
    if len(markers) > 1:
        raise ValueError("Multiple editor-notes markers; select the authoritative draft first")
    body = b"".join(lines[:markers[0]]) if markers else data
    if not body.strip():
        raise ValueError("Empty article export")
    out = out.resolve()
    out.mkdir(parents=True, exist_ok=False)
    article = out / "正文.md"
    article.write_bytes(body)
    sha = lambda value: hashlib.sha256(value).hexdigest()
    (out / "正文导出记录.json").write_text(json.dumps({
        "draft_md": str(source), "draft_sha256": sha(data),
        "source_md": str(article), "article_sha256": sha(body),
        "editor_notes_separated": bool(markers),
        "article_bytes_preserved": True,
        "article_state": "待作者确认；导出不代表定稿",
    }, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return article


INFO_FIELDS = ("账号", "定稿日期", "写手模型", "过程文件夹", "配图排版进度")
PROGRESS_POINTER = "详见配对发布物料包的配图排版进度"


def info_block(account: str, date: str, writer: str, process_dir: Path) -> bytes:
    """Flat YAML header agreed with the visual and layout Skills: string fields, double-quoted values."""
    values = (account, date, writer, str(process_dir.resolve()), PROGRESS_POINTER)
    lines = ["---"] + [f"{key}: {json.dumps(value, ensure_ascii=False)}" for key, value in zip(INFO_FIELDS, values)] + ["---", ""]
    return ("\n".join(lines) + "\n").encode("utf-8")


def strip_info_block(body: bytes) -> bytes:
    """Drop a leading YAML block (LF or CRLF, with or without a UTF-8 BOM) so a draft's own
    frontmatter never ends up in the ready copy. Body content and its internal line breaks are kept;
    leading blank lines after the header are normalised (dropped here, the new header adds one)."""
    if body.startswith(b"\xef\xbb\xbf"):
        body = body[3:]
    lines = body.splitlines(keepends=True)
    if not lines or lines[0].rstrip(b"\r\n") != b"---":
        return body
    for index, line in enumerate(lines[1:], 1):
        if line.rstrip(b"\r\n") == b"---":
            rest = lines[index + 1:]
            while rest and not rest[0].strip():
                rest = rest[1:]
            return b"".join(rest)
    raise ValueError("Unclosed YAML block at the top of the draft")


APPROVAL_LOG = "\u5b9a\u7a3f\u786e\u8ba4\u8bb0\u5f55.jsonl"  # 定稿确认记录.jsonl, in the article's process folder
REPLACED_DIR = "\u5b9a\u7a3f\u66ff\u6362\u7559\u5e95"  # 定稿替换留底: older ready copies kept before a replacement
# Anything that can turn 定稿 into "not yet", "if" or "is it?" makes the quote unclear; unclear is refused
# (independent review 2026-10-12: 不是定稿, 是否定稿, 等改完再定稿 and 请不要直接定稿 slipped through a narrower list).
_UNCLEAR = ("\u4e0d", "\u6ca1", "\u522b", "\u672a", "\u5426", "\u5417", "\u4e48", "?", "\uff1f", "\u7b49",
            "\u518d", "\u5982\u679c", "\u8981\u662f", "\u5047\u5982", "\u8fd8", "\u5148", "\u5f85\u5b9a")  # 不 没 别 未 否 吗 么 ? ？ 等 再 如果 要是 假如 还 先 待定


def approval_problem(quote) -> str | None:
    """The ready folder holds only what the author called final. Returns None when the quote is an approval.

    Only the author's own plain sentence saying 定稿 counts; 可以, 继续, 还行, 满意 do not.
    Any negation, condition or question in the sentence (不是定稿, 是否定稿, 等改完再定稿) makes it unclear,
    and unclear is refused: ask the author again rather than guess."""
    text = (quote or "").strip()
    if not text:
        return "No --approval: paste the author's own words that call this version final (they must say 定稿)"
    if "\u5b9a\u7a3f" not in text:
        return ("--approval does not say 定稿. 可以, 继续, 还行 or 满意 are not a final approval; "
                "use --output-dir for a trial export, or ask the author")
    found = [w for w in _UNCLEAR if w in text]
    if found:
        return ("--approval is not a plain final approval (contains " + " ".join(found) +
                "): a negation, condition or question around 定稿 is refused. Ask the author for a plain 定稿")
    return None


def ready(source: Path, ready_dir: Path, account: str, date: str, writer: str, process_dir: Path,
          approval: str | None = None, replace: bool = False) -> Path:
    """Write the approved article into <ready_dir>/<account>/ as <date>_<title>.md with the agreed header.

    ready_dir is the ROOT of the ready area (the config value ready_folder). If its last path
    component already equals the account, it is used as is, so the account is never doubled.
    approval is the author's verbatim final approval (must say 定稿); it is appended to the process
    folder's approval log. An existing different ready copy is replaced only with replace=True, and
    is first kept in the process folder."""
    problem = approval_problem(approval)
    if problem:
        raise ValueError(problem)
    process_dir = Path(process_dir).resolve()
    if not process_dir.is_dir():
        raise ValueError(f"--process-dir is not an existing folder: {process_dir}")
    data = source.resolve().read_bytes()
    lines = data.splitlines(keepends=True)
    markers = [i for i, line in enumerate(lines) if line.rstrip(b"\r\n") == b"===EDITOR NOTES==="]
    if len(markers) > 1:
        raise ValueError("Multiple editor-notes markers; select the authoritative draft first")
    body = strip_info_block(b"".join(lines[:markers[0]]) if markers else data)
    titles = [line[2:].strip() for line in body.decode("utf-8").splitlines() if line.startswith("# ")]
    if b"\n---" in body[:200] and body.lstrip().startswith(b"---"):
        raise ValueError("A second YAML block is still at the top; check the draft")
    if len(titles) != 1:
        raise ValueError(f"Expected exactly one H1 title, found {len(titles)}")
    if len(date) != 10 or date[4] != "-" or date[7] != "-":
        raise ValueError("Date must be YYYY-MM-DD")
    if "/" in titles[0]:
        raise ValueError("Title contains '/', which cannot be a file name; ask the author")
    if not account or "/" in account:
        raise ValueError("Account must be a non-empty folder name without '/'")
    name = f"{date}_{titles[0]}.md"
    ready_dir = ready_dir.resolve()
    if ready_dir.name != account:
        ready_dir = ready_dir / account
    ready_dir.mkdir(parents=True, exist_ok=True)
    target = ready_dir / name
    # Body content and its internal line breaks are kept; leading blank lines after the header
    # are normalised (the header block ends with exactly one blank line).
    content = info_block(account, date, writer, process_dir) + body
    stamp = datetime.now().astimezone()
    kept = None
    # One export at a time per ready copy: the lock covers create, compare, keep-a-copy and replace
    # (independent review 2026-10-12: two sessions exporting at once could overwrite without --replace).
    lock = target.with_name("." + target.name + ".exporting")
    try:
        lock_fd = os.open(lock, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
    except FileExistsError:
        raise ValueError(f"Another export of this article is running (lock {lock}). Wait for it; if no export is running, "
                         "delete that lock file and re-run") from None
    try:
        try:
            with target.open("xb") as handle:  # first export: create only, never overwrite
                handle.write(content)
        except FileExistsError:
            if target.read_bytes() != content:
                if not replace:
                    raise ValueError(f"A different ready copy already exists: {target}. Ask the author before replacing it, "
                                     "then re-run with --replace (the old copy is kept in the process folder first)") from None
                kept = process_dir / REPLACED_DIR / f"{stamp:%Y%m%d-%H%M%S}_{name}"
                kept.parent.mkdir(exist_ok=True)
                try:
                    with kept.open("xb") as handle:
                        handle.write(target.read_bytes())
                except FileExistsError:
                    raise ValueError(f"Backup name already taken, try again in a second: {kept}") from None
                temporary = target.with_name("." + target.name + ".new")
                temporary.write_bytes(content)
                os.replace(temporary, target)
    finally:
        os.close(lock_fd)
        lock.unlink()
    digest = hashlib.sha256(content).hexdigest()
    record = {"time": stamp.isoformat(timespec="seconds"), "approval": approval.strip(), "ready_md": str(target),
              "article_sha256": digest, "draft_md": str(source.resolve()), "draft_sha256": hashlib.sha256(data).hexdigest(),
              "replaced_copy_kept_at": str(kept) if kept else None}
    with (process_dir / APPROVAL_LOG).open("a", encoding="utf-8") as log:
        log.write(json.dumps(record, ensure_ascii=False) + "\n")
    print(json.dumps({"ready_md": str(target), "article_sha256": digest,
                      "kit_md": str(ready_dir / f"{date}_{titles[0]}·发布物料包.md")}, ensure_ascii=False))
    return target


def approval_recorded(process_dir: Path, ready_md: Path, digest: str) -> bool:
    log = Path(process_dir).expanduser() / APPROVAL_LOG
    if not log.is_file():
        return False
    for line in log.read_text(encoding="utf-8").splitlines():
        try:
            entry = json.loads(line)
        except ValueError:
            continue
        if entry.get("article_sha256") == digest and Path(entry.get("ready_md", "")).resolve() == ready_md:
            return True
    return False


KIT_SUFFIX = "\u00b7\u53d1\u5e03\u7269\u6599\u5305.md"  # "·发布物料包.md"
NOTE_MARKERS = ("===EDITOR NOTES===", "===\u7f16\u8f91\u5907\u6ce8===")  # second one: ===编辑备注===
BAD_SOURCE_HEADINGS = ("\u8d44\u6599\u6765\u6e90", "\u53c2\u8003\u8d44\u6599", "\u4fe1\u606f\u6765\u6e90")  # 资料来源/参考资料/信息来源
SOURCE_HEADING = "\u53c2\u8003\u6587\u7ae0"  # 参考文章
MAX_SOURCES = 5  # not a quota: list as many complete long reads as the article really used; above this, warn to check for piling up
ANCHOR_COLUMN = "\u653e\u5728\u54ea\u6bb5\u540e"  # column header prefix: 放在哪段后
KIT_FIELDS = ("\u6b63\u6587\u8def\u5f84", "\u914d\u56fe\u4efb\u52a1\u8def\u5f84")  # 正文路径, 配图任务路径


def parse_flat_yaml(text: str):
    """Parse a leading flat YAML block of `key: "json string"` lines.
    Returns (pairs, rest_lines, problems); pairs is None when there is no block."""
    lines = text.lstrip("\ufeff").splitlines()
    if not lines or lines[0].strip() != "---":
        return None, lines, []
    problems = []
    pairs = []
    for index, line in enumerate(lines[1:], 1):
        if line.strip() == "---":
            return pairs, lines[index + 1:], problems
        key, sep, value = line.partition(":")
        value = value.strip()
        if not sep or not key.strip():
            problems.append(f"Header line is not 'key: \"value\"': {line!r}")
            continue
        try:
            parsed = json.loads(value)
            if not isinstance(parsed, str):
                raise ValueError
        except ValueError:
            problems.append(f"Value of {key.strip()} is not a double-quoted string: {value!r}")
            parsed = value
        pairs.append((key.strip(), parsed))
    return None, lines, problems + ["YAML block at the top is not closed"]


def _heading_text(line: str):
    stripped = line.strip()
    if not stripped.startswith("#"):
        return None
    level = len(stripped) - len(stripped.lstrip("#"))
    if level > 6 or not stripped[level:level + 1].isspace():
        return None
    return level, stripped[level:].strip().rstrip("\uff1a:").strip()


def _cells(line: str):
    return [cell.strip() for cell in line.strip().strip("|").split("|")]


def _squash(text: str) -> str:
    return re.sub(r"\s+", "", text)


def anchor_rows(kit_lines):
    """Return [(row label, anchor text)] from every kit table (images, videos) whose header has a
    column starting with the anchor column name. Empty list when there is no such table."""
    rows = []
    column = None
    in_table = False
    for line in kit_lines:
        if not line.strip().startswith("|"):
            column, in_table = None, False  # a table ended; look for the next one
            continue
        if in_table and column is None:
            continue  # a table without the anchor column
        in_table = True
        cells = _cells(line)
        if column is None:
            found = [i for i, cell in enumerate(cells) if cell.startswith(ANCHOR_COLUMN)]
            if found:
                column = found[0]
            continue
        if all(re.fullmatch(r":?-{2,}:?", cell) for cell in cells if cell):
            continue  # separator row
        # A row too short to have the anchor cell is reported as an empty anchor, never skipped.
        rows.append((cells[0], cells[column] if column < len(cells) else ""))
    return rows


def _clean_anchor(text: str) -> str:
    text = text.strip().strip("\"'\u201c\u201d\u2018\u2019\u300c\u300d\u300e\u300f` ")
    text = re.sub(r"^(?:\.{2,}|\u2026+)\s*|\s*(?:\.{2,}|\u2026+)$", "", text)
    return _squash(text.strip("\"'\u201c\u201d\u2018\u2019\u300c\u300d\u300e\u300f` "))


def check(path: Path, body_only: bool = False) -> dict:
    """Read-only check of a ready article and (unless body_only) its paired publishing kit. Never writes.

    body_only checks the article itself so it can run right after export, before the kit exists."""
    problems, warnings = [], []
    path = path.resolve()
    if not path.is_file():
        return {"ok": False, "problems": [f"File not found: {path}"], "warnings": []}
    text = path.read_bytes().decode("utf-8")
    pairs, body_lines, header_problems = parse_flat_yaml(text)
    problems.extend(header_problems)
    values = {}
    if pairs is None:
        problems.append("File does not start with a flat YAML block (---); a hand-made header such as '> \u8d26\u53f7\uff1a...' is not accepted")
    else:
        keys = [key for key, _ in pairs]
        if keys != list(INFO_FIELDS):
            problems.append("Header fields must be exactly, in order: " + ", ".join(INFO_FIELDS) + "; found: " + ", ".join(keys))
        values = dict(pairs)
        if values.get(INFO_FIELDS[4]) != PROGRESS_POINTER:
            problems.append(f"{INFO_FIELDS[4]} must be the fixed value {PROGRESS_POINTER!r}")
        date = values.get(INFO_FIELDS[1], "")
        if not (len(date) == 10 and date[4] == "-" and date[7] == "-"):
            problems.append(f"{INFO_FIELDS[1]} must be YYYY-MM-DD, found {date!r}")
        if values.get(INFO_FIELDS[0]) and path.parent.name != values[INFO_FIELDS[0]]:
            problems.append(f"Parent folder {path.parent.name!r} must equal {INFO_FIELDS[0]} {values[INFO_FIELDS[0]]!r}")
        process = values.get(INFO_FIELDS[3])
        if process and not Path(process).expanduser().is_dir():
            problems.append(f"{INFO_FIELDS[3]} is not an existing folder: {process}")
        elif process and not approval_recorded(Path(process), path, hashlib.sha256(path.read_bytes()).hexdigest()):
            warnings.append(f"No {APPROVAL_LOG} entry for this exact file in the process folder: it was not exported with "
                            "--approval (before 1.4, by hand, or edited afterwards). Confirm the author said 定稿 for this version")
    body_text = "\n".join(body_lines)
    titles = [line[2:].strip() for line in body_lines if line.startswith("# ")]
    if len(titles) != 1:
        problems.append(f"Expected exactly one H1 title, found {len(titles)}")
    elif values.get(INFO_FIELDS[1]) is not None:
        expected = f"{values[INFO_FIELDS[1]]}_{titles[0]}.md"
        if path.name != expected:
            problems.append(f"File name must be <\u5b9a\u7a3f\u65e5\u671f>_<H1 title>.md = {expected!r}, found {path.name!r}")
    for marker in NOTE_MARKERS:
        if marker in body_text:
            problems.append(f"Editor-notes marker {marker} is still in the file")
    # End-of-article source section.
    sections = []
    for index, line in enumerate(body_lines):
        found = _heading_text(line)
        if found:
            sections.append((index, found[0], found[1]))
    for index, level, name in sections:
        if name in BAD_SOURCE_HEADINGS:
            problems.append(f"Section named {name!r} must be called {SOURCE_HEADING!r}")
        if name == SOURCE_HEADING:
            end = next((j for j, lv, _ in sections if j > index and lv <= level), len(body_lines))
            entries = [l for l in body_lines[index + 1:end] if re.match(r"\s*([-*+]|\d+[.\u3001)])\s+\S", l)]
            if len(entries) > MAX_SOURCES:
                warnings.append(f"{SOURCE_HEADING} has {len(entries)} list entries; check each is a complete long read readers need, not a pile of every source")
    if body_only:
        return {"ok": not problems, "problems": problems, "warnings": warnings, "scope": "article only (kit not checked)"}
    # Paired kit.
    kit = path.with_name(path.stem + KIT_SUFFIX)
    if not kit.is_file():
        problems.append(f"Paired publishing kit not found beside the article: {kit.name}")
    else:
        kit_pairs, kit_lines, kit_problems = parse_flat_yaml(kit.read_bytes().decode("utf-8"))
        problems.extend(f"Kit: {p}" for p in kit_problems)
        if kit_pairs is None:
            problems.append("Kit does not open with a flat YAML block holding " + ", ".join(KIT_FIELDS))
        else:
            kit_values = dict(kit_pairs)
            for field in KIT_FIELDS:
                if not kit_values.get(field):
                    problems.append(f"Kit header lacks {field}")
            target = kit_values.get(KIT_FIELDS[0])
            if target and Path(target).expanduser().resolve() != path:
                problems.append(f"Kit {KIT_FIELDS[0]} does not resolve to this file: {target}")
            task = kit_values.get(KIT_FIELDS[1])
            if task and not Path(task).expanduser().is_file():
                problems.append(f"Kit {KIT_FIELDS[1]} is not an existing file: {task}")
            paragraphs = [_squash(l.lstrip("#>-*+ \t")) for l in body_lines]
            for label, raw in anchor_rows(kit_lines):
                anchor = _clean_anchor(raw)
                if not anchor:
                    problems.append(f"Kit row {label!r} has an empty anchor")
                elif not any(par.startswith(anchor) for par in paragraphs):
                    problems.append(f"Kit row {label!r}: anchor not found at the start of any paragraph: {raw.strip()!r}")
    return {"ok": not problems, "problems": problems, "warnings": warnings}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="只导出正文及来源，保留原稿和编辑备注")
    parser.add_argument("--source", type=Path)
    parser.add_argument("--check", type=Path, metavar="READY_MD", help="read-only check of a ready article and its kit; prints a JSON report, exit 1 on problems")
    parser.add_argument("--body-only", action="store_true", help="with --check: check only the ready article, not the kit (usable right after export)")
    parser.add_argument("--output-dir", type=Path, help="trial export: 正文.md plus an export record")
    parser.add_argument("--ready-dir", type=Path, help="ROOT of the ready area (config ready_folder); writes <ready-dir>/<account>/<date>_<title>.md with the info header")
    parser.add_argument("--account")
    parser.add_argument("--date", help="approval date, YYYY-MM-DD")
    parser.add_argument("--writer", help="the model that actually wrote the article")
    parser.add_argument("--process-dir", type=Path, help="the article's own process folder")
    parser.add_argument("--approval", help="with --ready-dir: the author's verbatim words calling this version final; must say 定稿 (可以/继续/还行 do not count)")
    parser.add_argument("--replace", action="store_true", help="with --ready-dir: replace a different existing ready copy (author asked); the old copy is kept in the process folder")
    args = parser.parse_args()
    if args.check:
        report = check(args.check, body_only=args.body_only)
        print(json.dumps(report, ensure_ascii=False, indent=2))
        raise SystemExit(0 if report["ok"] else 1)
    if args.body_only:
        parser.error("--body-only only works together with --check")
    if not args.source:
        parser.error("--source is required (unless --check is used)")
    if args.ready_dir:
        if not all((args.account, args.date, args.writer, args.process_dir)):
            parser.error("--ready-dir needs --account, --date, --writer and --process-dir")
        try:
            ready(args.source, args.ready_dir, args.account, args.date, args.writer, args.process_dir,
                  approval=args.approval, replace=args.replace)
        except ValueError as exc:
            parser.exit(1, f"export_article.py: refused: {exc}\n")
    elif args.output_dir:
        print(export(args.source, args.output_dir))
    else:
        parser.error("give --output-dir (trial export) or --ready-dir (approved article)")
