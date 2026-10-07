#!/usr/bin/env python3
"""Run the public course-foundation release gate without network access."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MANIFEST_NAME = "RELEASE_MANIFEST.json"
TEXT_SUFFIXES = {".md", ".py", ".json", ".yaml", ".yml", ".sh", ".txt", ".toml", ".ini", ".csv"}
PRIVATE_PATHS = (
    re.compile("/" + r"Users/[^/\s\"']+/"),
    re.compile("/" + r"home/[^/\s\"']+/"),
    re.compile(r"[A-Za-z]:" + r"\\Users\\[^\\\s\"']+\\"),
)
# Public documentation may discuss generic courses; these markers identify local-only
# workspace conventions rather than subject matter.
PRIVATE_MARKERS = ("MyAI" + "Clone", "00_shared" + "_config", "Hermes " + "workspace")


def files() -> list[Path]:
    return [path for path in sorted(ROOT.rglob("*"))
            if path.is_file() and ".git" not in path.parts and "__pycache__" not in path.parts
            and path.name != MANIFEST_NAME and path.suffix not in {".pyc", ".pyo"}]


def run(label: str, command: list[str], failures: list[str], timeout: int = 240) -> None:
    try:
        result = subprocess.run(command, cwd=ROOT, text=True, capture_output=True, timeout=timeout,
                                env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1"})
    except (OSError, subprocess.TimeoutExpired) as exc:
        failures.append(f"{label}: could not run: {exc}")
        return
    if result.returncode:
        failures.append(f"{label}: exit {result.returncode}\n{(result.stdout + result.stderr)[-5000:]}")
    else:
        print(f"PASS {label}")


def static_checks(failures: list[str]) -> tuple[int, int]:
    json_count = 0
    python_count = 0
    for path in files():
        rel = path.relative_to(ROOT).as_posix()
        if path.suffix == ".py":
            python_count += 1
            try:
                compile(path.read_text(encoding="utf-8"), rel, "exec")
            except (UnicodeDecodeError, SyntaxError) as exc:
                failures.append(f"Python compile failed: {rel}: {exc}")
        if path.suffix == ".json":
            json_count += 1
            try:
                json.loads(path.read_text(encoding="utf-8"))
            except (UnicodeDecodeError, json.JSONDecodeError) as exc:
                failures.append(f"JSON parse failed: {rel}: {exc}")
        if path.suffix.lower() not in TEXT_SUFFIXES and path.name not in {"LICENSE", "NOTICE"}:
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        if path.resolve() == Path(__file__).resolve():
            # This checker necessarily contains the private-path detection regexes.
            continue
        if any(pattern.search(text) for pattern in PRIVATE_PATHS):
            failures.append(f"private absolute path: {rel}")
        if any(marker in text for marker in PRIVATE_MARKERS):
            failures.append(f"private workspace marker: {rel}")
    if not failures:
        print(f"PASS static compile/JSON/privacy scan ({python_count} Python, {json_count} JSON)")
    return python_count, json_count


def write_manifest(path: Path) -> int:
    entries = []
    for item in files():
        entries.append({"path": item.relative_to(ROOT).as_posix(),
                        "sha256": hashlib.sha256(item.read_bytes()).hexdigest(),
                        "bytes": item.stat().st_size})
    payload = {"schema_version": 1, "algorithm": "sha256", "excludes": [".git/**", MANIFEST_NAME],
               "file_count": len(entries), "files": entries}
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"WROTE {path.relative_to(ROOT)} ({len(entries)} files; manifest excludes itself)")
    return len(entries)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write-manifest", action="store_true",
                        help=f"write {MANIFEST_NAME} after all checks pass")
    args = parser.parse_args()
    failures: list[str] = []
    static_checks(failures)
    gates = [
        ("course-capture self-test", [sys.executable, "pinshu-course-capture/scripts/self_test.py"]),
        ("course-foundation regressions", [sys.executable, "-m", "unittest", "discover", "-s", "pinshu-course-capture/tests", "-v"]),
        ("course learning-asset tests", [sys.executable, "pinshu-course/tests/self_test_validate_learning_assets.py"]),
        ("course runtime-contract tests", [sys.executable, "pinshu-course/tests/self_test_runtime_contracts.py"]),
        ("content-route tests", [sys.executable, "-m", "unittest", "discover", "-s", "pinshu-content-assets/tests", "-v"]),
        ("release-validator controls", [sys.executable, "-m", "unittest", "tests/test_release_validator.py", "-v"]),
    ]
    for label, command in gates:
        run(label, command, failures)
    if failures:
        print("RELEASE CHECK FAIL")
        for failure in failures:
            print(f"- {failure}")
        return 1
    if args.write_manifest:
        write_manifest(ROOT / MANIFEST_NAME)
    print("RELEASE CHECK PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
