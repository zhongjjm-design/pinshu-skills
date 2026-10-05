#!/usr/bin/env python3
"""Fail-closed release checks for the public Pinshu Skills bundle."""
from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import stat
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EXPECTED_SKILLS = {
    "pinshu-course-capture",
    "pinshu-content-assets",
    "pinshu-course",
    "pinshu-distill",
    "pinshu-md2pdf",
    "pinshu-study",
    "pinshu-transcript",
}
TEXT_SUFFIXES = {
    ".bash", ".cfg", ".css", ".csv", ".html", ".ini", ".js", ".json",
    ".jsonl", ".md", ".markdown", ".py", ".sh", ".toml", ".ts", ".tsv",
    ".txt", ".xml", ".yaml", ".yml",
}
EAST_ASIAN_RE = re.compile(
    "[\u2e80-\u2fff\u3000-\u303f\u3040-\u30ff\u3100-\u312f\u31f0-\u31ff"
    "\u3400-\u4dbf\u4e00-\u9fff\uf900-\ufaff\uac00-\ud7af\uff01-\uff65]"
)
PERSONAL_PATH_RES = (
    re.compile("/" + r"Users/[^/\s\"']+/"),
    re.compile("/" + r"home/[^/\s\"']+/"),
    re.compile(r"[A-Za-z]:\\\\" + r"Users\\\\[^\\\s\"']+\\\\"),
)
EMAIL_RE = re.compile(r"(?i)\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b")
PRIVATE_KEY_RE = re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----")
SECRET_RES = (
    re.compile(r"\b(?:gh[pousr]_[A-Za-z0-9_]{20,}|github_pat_[A-Za-z0-9_]{20,})\b"),
    re.compile(r"\bsk-(?:proj-)?[A-Za-z0-9_-]{20,}\b"),
    re.compile(r"\bAKIA[0-9A-Z]{16}\b"),
)
SENSITIVE_FILENAMES = {".env", ".netrc", ".npmrc", ".pypirc", "auth.json", "cookies.json", "credentials.json"}
errors: list[str] = []
warnings: list[str] = []
checked_files = 0


def fail(message: str) -> None:
    errors.append(message)


def visible_markdown(text: str) -> str:
    lines: list[str] = []
    fence: str | None = None
    for line in text.splitlines():
        marker = re.match(r"^\s*(```|~~~)", line)
        if marker:
            fence = None if fence else marker.group(1)
            continue
        if fence is None:
            lines.append(line)
    return "\n".join(lines)


def text_kind(path: Path) -> bool:
    return path.suffix.lower() in TEXT_SUFFIXES or path.name in {"LICENSE", "NOTICE"}


def run_check(label: str, command: list[str], *, timeout: int = 180) -> None:
    try:
        result = subprocess.run(
            command,
            cwd=ROOT,
            capture_output=True,
            text=True,
            timeout=timeout,
            env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1"},
        )
    except (OSError, subprocess.TimeoutExpired) as exc:
        fail(f"{label}: could not run ({exc})")
        return
    if result.returncode != 0:
        detail = (result.stdout + "\n" + result.stderr).strip()
        fail(f"{label}: failed\n{detail[-4000:]}")


def scan_tree() -> None:
    global checked_files
    discovered_skills = {
        path.name for path in ROOT.iterdir()
        if path.is_dir() and path.name.startswith("pinshu-")
    }
    if discovered_skills != EXPECTED_SKILLS:
        fail(
            "package roster mismatch: expected {} but found {}".format(
                sorted(EXPECTED_SKILLS), sorted(discovered_skills)
            )
        )

    for path in sorted(ROOT.rglob("*")):
        if ".git" in path.parts or "__pycache__" in path.parts:
            continue
        rel = path.relative_to(ROOT).as_posix()
        if EAST_ASIAN_RE.search(rel):
            fail(f"East Asian script in path: {rel}")
        if path.is_symlink():
            fail(f"symlink is not allowed in the release tree: {rel}")
            continue
        try:
            mode = path.lstat().st_mode
        except OSError as exc:
            fail(f"cannot stat {rel}: {exc}")
            continue
        if not (stat.S_ISDIR(mode) or stat.S_ISREG(mode)):
            fail(f"special file is not allowed: {rel}")
            continue
        if not path.is_file():
            continue
        checked_files += 1
        if path.name.lower() in SENSITIVE_FILENAMES or path.suffix.lower() in {".key", ".pem", ".p12", ".pfx"}:
            fail(f"sensitive filename is not allowed: {rel}")
        if path.name == ".DS_Store" or path.suffix.lower() in {".pyc", ".pyo"}:
            fail(f"generated file is not allowed: {rel}")
        if not text_kind(path):
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            fail(f"declared text file is not UTF-8: {rel}")
            continue
        if EAST_ASIAN_RE.search(text):
            fail(f"East Asian script in text: {rel}")
        if any(pattern.search(text) for pattern in PERSONAL_PATH_RES):
            fail(f"personal absolute path in text: {rel}")
        if PRIVATE_KEY_RE.search(text):
            fail(f"private-key material in text: {rel}")
        if any(pattern.search(text) for pattern in SECRET_RES):
            fail(f"credential-like token in text: {rel}")
        for match in EMAIL_RE.finditer(text):
            if not match.group(0).lower().endswith(".invalid"):
                fail(f"email address in public text: {rel}")
                break

        suffix = path.suffix.lower()
        if suffix == ".json":
            try:
                json.loads(text)
            except json.JSONDecodeError as exc:
                fail(f"invalid JSON: {rel}:{exc.lineno} ({exc.msg})")
        elif suffix == ".jsonl":
            for number, line in enumerate(text.splitlines(), 1):
                if not line.strip():
                    continue
                try:
                    json.loads(line)
                except json.JSONDecodeError as exc:
                    fail(f"invalid JSONL: {rel}:{number} ({exc.msg})")
        elif suffix in {".yaml", ".yml"} and "\t" in text:
            fail(f"YAML contains tab indentation: {rel}")
        elif suffix == ".py":
            try:
                compile(text, rel, "exec")
            except SyntaxError as exc:
                fail(f"Python compile failed: {rel}:{exc.lineno} ({exc.msg})")


def check_skill_contracts() -> None:
    for name in sorted(EXPECTED_SKILLS):
        skill = ROOT / name
        main = skill / "SKILL.md"
        if not main.is_file():
            fail(f"{name}: missing SKILL.md")
            continue
        text = main.read_text(encoding="utf-8")
        if not re.search(r"(?m)^name:\s*" + re.escape(name) + r"\s*$", text):
            fail(f"{name}: frontmatter name mismatch or missing")
        if len(re.findall(r"(?m)^#\s+\S", visible_markdown(text))) != 1:
            fail(f"{name}: expected one visible H1")
        interface = skill / "agents" / "openai.yaml"
        if not interface.is_file():
            fail(f"{name}: missing agents/openai.yaml")
        for ref in re.findall(r"`(references/[^`]+)`", text):
            if not (skill / ref).is_file():
                fail(f"{name}: missing referenced file {ref}")
        references = skill / "references"
        if references.is_dir():
            for ref_file in references.glob("*.md"):
                ref_text = ref_file.read_text(encoding="utf-8")
                if re.search(r"(?m)\bread\s+`references/[^`]+`", ref_text, re.I):
                    fail(f"{name}: reference routes another reference: {ref_file.name}")


def run_executable_gates(full: bool) -> None:
    shell_files = sorted(
        path for path in ROOT.rglob("*")
        if path.is_file() and path.suffix.lower() in {".sh", ".bash"} and ".git" not in path.parts
    )
    for path in shell_files:
        run_check(f"bash syntax {path.relative_to(ROOT)}", ["bash", "-n", str(path)])

    run_check(
        "release-validator negative controls",
        [sys.executable, "-m", "unittest", "tests/test_release_validator.py", "-v"],
    )
    run_check(
        "course-capture self-test",
        [sys.executable, "pinshu-course-capture/scripts/self_test.py"],
    )
    run_check(
        "content-assets route self-test",
        [sys.executable, "-m", "unittest", "discover", "-s", "pinshu-content-assets/tests", "-v"],
    )
    run_check(
        "learning-asset validator self-test",
        [sys.executable, "pinshu-course/tests/self_test_validate_learning_assets.py"],
    )
    run_check(
        "runtime-contract self-test",
        [sys.executable, "pinshu-course/tests/self_test_runtime_contracts.py"],
    )
    run_check(
        "Markdown converter security tests",
        [sys.executable, "-m", "unittest", "discover", "-s", "pinshu-md2pdf/tests", "-v"],
        timeout=240,
    )
    if full:
        run_check("installer negative controls", ["bash", "tests/test_installer.sh"], timeout=240)

    gitleaks = shutil.which("gitleaks")
    if gitleaks:
        with tempfile.NamedTemporaryFile(suffix=".json") as report:
            run_check(
                "gitleaks current-tree scan",
                [
                    gitleaks, "dir", str(ROOT), "--no-banner", "--redact",
                    "--report-format", "json", "--report-path", report.name,
                ],
                timeout=240,
            )
    else:
        warnings.append("gitleaks is unavailable; current-tree secret scan skipped")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--quick",
        action="store_true",
        help="skip the isolated installer lifecycle; all static and package tests still run",
    )
    args = parser.parse_args()

    scan_tree()
    check_skill_contracts()
    run_executable_gates(full=not args.quick)

    if errors:
        print("RELEASE FAIL")
        for error in errors:
            print(f"- {error}")
        for warning in warnings:
            print(f"- Warning: {warning}")
        return 1
    print(
        f"RELEASE PASS: {len(EXPECTED_SKILLS)} Pinshu Skill packages, "
        f"{checked_files} files, and executable negative controls checked"
    )
    for warning in warnings:
        print(f"Warning: {warning}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
