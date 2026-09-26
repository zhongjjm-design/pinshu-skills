#!/usr/bin/env python3
"""Deterministic warnings for one course lesson; semantic depth follows the selected profile."""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path

FRONTMATTER = re.compile(r"\A---\s*\n.*?\n---\s*\n", re.S)
PLACEHOLDERS = re.compile(
    r"\u5f85\u8865|TODO|TBD|\[\u5f85\u786e\u8ba4\]|to be added|\[(?:to confirm|unconfirmed)\]|<[^>]{1,80}>",
    re.I,
)
AI_PHRASES = [
    "\u7efc\u4e0a\u6240\u8ff0", "\u503c\u5f97\u6ce8\u610f\u7684\u662f", "\u4e0d\u96be\u53d1\u73b0", "\u663e\u800c\u6613\u89c1",
    "in conclusion", "it is worth noting that", "it is not difficult to see that", "obviously",
]
ALLOWED_COVERAGE_STATUS = {"retained", "merged", "noise", "uncertain"}


def read(path: Path) -> str:
    text = path.read_text(encoding="utf-8")
    return text.replace("\r\n", "\n")


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def body(text: str) -> str:
    return FRONTMATTER.sub("", text, count=1).strip()


def nonspace_len(text: str) -> int:
    return len(re.sub(r"\s+", "", text))


def paragraph_lengths(text: str) -> list[int]:
    return [nonspace_len(p) for p in re.split(r"\n\s*\n", text) if p.strip() and not p.lstrip().startswith("#")]


def inspect(name: str, text: str) -> dict:
    b = body(text)
    n = max(nonspace_len(b), 1)
    paras = paragraph_lengths(b)
    bold_chars = sum(len(x) for x in re.findall(r"\*\*(.+?)\*\*", b, re.S))
    em_dash_count = len(re.findall(r"\u2014{1,2}", b))
    return {
        "name": name,
        "chars": n,
        "headings": len(re.findall(r"(?m)^#{1,6}\s+", b)),
        "em_dash_count": em_dash_count,
        "em_dash_per_1000": round(em_dash_count * 1000 / n, 2),
        "bold_ratio": round(bold_chars / n, 4),
        "max_paragraph_chars": max(paras or [0]),
        "paragraphs_over_500": sum(x > 500 for x in paras),
        "placeholder_hits": sorted(set(PLACEHOLDERS.findall(b))),
        "ai_phrase_hits": {x: b.count(x) for x in AI_PHRASES if x in b},
    }


def load_json_input(name: str, path: Path, errors: list[str]) -> dict | None:
    if not path.is_file():
        errors.append(f"missing file: {name}={path}")
        return None
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except UnicodeDecodeError:
        errors.append(f"not utf-8: {name}={path}")
        return None
    except json.JSONDecodeError as exc:
        errors.append(f"invalid json: {name}={path}: {exc}")
        return None
    if not isinstance(data, dict):
        errors.append(f"invalid json root: {name} must be an object")
        return None
    return data


def inspect_coverage(data: dict, errors: list[str]) -> dict:
    blocks = data.get("blocks")
    if not isinstance(blocks, list) or not blocks:
        errors.append("coverage.blocks must be a non-empty list")
        return {"block_count": 0, "status_counts": {}}
    ids = [x.get("id") for x in blocks if isinstance(x, dict)]
    if len(ids) != len(blocks) or any(not x for x in ids):
        errors.append("coverage.blocks contains a non-object or missing id")
    elif len(set(ids)) != len(ids):
        errors.append("coverage.blocks contains duplicate ids")
    statuses = [x.get("status") for x in blocks if isinstance(x, dict)]
    invalid = sorted({x for x in statuses if x not in ALLOWED_COVERAGE_STATUS}, key=str)
    if invalid:
        errors.append(f"coverage.blocks contains invalid status: {invalid}")
    actual = {s: statuses.count(s) for s in ALLOWED_COVERAGE_STATUS if statuses.count(s)}
    if "block_count" in data and data["block_count"] != len(blocks):
        errors.append(f"coverage.block_count mismatch: declared={data['block_count']} actual={len(blocks)}")
    declared = data.get("status_summary")
    if declared is not None:
        if not isinstance(declared, dict):
            errors.append("coverage.status_summary must be an object")
        else:
            for status in ALLOWED_COVERAGE_STATUS:
                if int(declared.get(status, 0)) != actual.get(status, 0):
                    errors.append(
                        f"coverage.status_summary mismatch for {status}: "
                        f"declared={declared.get(status, 0)} actual={actual.get(status, 0)}"
                    )
    return {"block_count": len(blocks), "status_counts": actual}


def inspect_uncertainties(data: dict, errors: list[str]) -> dict:
    aliases = {
        "confirmed_corrections": ("confirmed_corrections", "stt_corrections_confirmed"),
        "variant_entries": ("variants",),
        "unresolved": ("unresolved", "pending_items"),
    }
    actual: dict[str, int] = {}
    for summary_key, fields in aliases.items():
        for field in fields:
            if field in data:
                if not isinstance(data[field], list):
                    errors.append(f"uncertainties.{field} must be a list")
                else:
                    actual[summary_key] = len(data[field])
                break
    summary = data.get("summary")
    if summary is not None:
        if not isinstance(summary, dict):
            errors.append("uncertainties.summary must be an object")
        else:
            for key, count in actual.items():
                if key in summary and int(summary[key]) != count:
                    errors.append(
                        f"uncertainties.summary mismatch for {key}: "
                        f"declared={summary[key]} actual={count}"
                    )
    return actual


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--source", required=True)
    p.add_argument("--faithful", required=True)
    p.add_argument("--lecture", required=True)
    p.add_argument("--profile", choices=["fast", "standard", "strict"], default="fast")
    p.add_argument("--coverage")
    p.add_argument("--uncertainties", required=True)
    p.add_argument("--json-out")
    args = p.parse_args()
    paths = {k: Path(getattr(args, k)) for k in ("source", "faithful", "lecture")}
    errors, warnings = [], []
    texts = {}
    for name, path in paths.items():
        if not path.is_file():
            errors.append(f"missing file: {name}={path}")
            continue
        try:
            texts[name] = read(path)
        except UnicodeDecodeError:
            errors.append(f"not utf-8: {name}={path}")
    metrics = {k: inspect(k, v) for k, v in texts.items()}
    coverage = None
    if args.coverage:
        coverage = load_json_input("coverage", Path(args.coverage), errors)
    elif args.profile == "strict":
        errors.append("strict profile requires --coverage")
    uncertainties = load_json_input("uncertainties", Path(args.uncertainties), errors)
    if coverage is not None:
        metrics["coverage"] = inspect_coverage(coverage, errors)
    if uncertainties is not None:
        metrics["uncertainties"] = inspect_uncertainties(uncertainties, errors)
    if len(texts) == 3:
        src = metrics["source"]["chars"]
        ratio = metrics["faithful"]["chars"] / max(src, 1)
        metrics["faithful_to_source_ratio"] = round(ratio, 4)
        if ratio < 0.55: warnings.append("The faithful edit is unusually short relative to the source; review meaning block by block. The ratio alone is not a failure.")
        if ratio > 1.35: warnings.append("The faithful edit is unusually long relative to the source; check for unsupported expansion. The ratio alone is not a failure.")
        for name in ("faithful", "lecture"):
            m = metrics[name]
            if m["paragraphs_over_500"]: warnings.append(f"{name} contains an unusually long paragraph; check for a wall of text")
            if m["bold_ratio"] > 0.12: warnings.append(f"{name} has a high proportion of bold text")
            if m["em_dash_per_1000"] > 3: warnings.append(f"{name} has a high em-dash density")
            if m["placeholder_hits"]: warnings.append(f"{name} contains placeholders or unconfirmed markers")
            if m["ai_phrase_hits"]: warnings.append(f"{name} contains potentially formulaic AI phrasing; compare it with the source")
    report = {
        "schema_version": 1,
        "profile": args.profile,
        "mechanical_pass": not errors,
        "semantic_pass": None,
        "input_sha256": {
            "source": sha256_file(paths["source"]) if paths["source"].is_file() else None,
            "faithful": sha256_file(paths["faithful"]) if paths["faithful"].is_file() else None,
            "lecture": sha256_file(paths["lecture"]) if paths["lecture"].is_file() else None,
            "uncertainties": sha256_file(Path(args.uncertainties)) if Path(args.uncertainties).is_file() else None,
            **({"coverage": sha256_file(Path(args.coverage))} if args.coverage and Path(args.coverage).is_file() else {}),
        },
        "errors": errors,
        "warnings": warnings,
        "metrics": metrics,
    }
    rendered = json.dumps(report, ensure_ascii=False, indent=2) + "\n"
    if args.json_out:
        out = Path(args.json_out); out.parent.mkdir(parents=True, exist_ok=True); out.write_text(rendered, encoding="utf-8")
    print(rendered, end="")
    return 0 if not errors else 1

if __name__ == "__main__":
    raise SystemExit(main())
