#!/usr/bin/env python3
"""Executable regression tests for validate-learning-assets.py."""
from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
COURSE_ROOT = HERE.parent
VALIDATOR = COURSE_ROOT / "scripts" / "validate-learning-assets.py"
FIXTURES = HERE / "fixtures" / "learning-assets.json"


def run(kind: str, path: Path, expected: int) -> subprocess.CompletedProcess[str]:
    result = subprocess.run(
        [sys.executable, str(VALIDATOR), "--kind", kind, str(path)],
        text=True,
        capture_output=True,
    )
    if result.returncode != expected:
        raise AssertionError(
            f"unexpected exit for {kind} {path.name}: {result.returncode}\n"
            f"stdout:\n{result.stdout}\nstderr:\n{result.stderr}"
        )
    return result


def load_validator_module():
    spec = importlib.util.spec_from_file_location("learning_asset_validator", VALIDATOR)
    if spec is None or spec.loader is None:
        raise AssertionError("cannot load validator module")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def main() -> int:
    FIXTURES.read_bytes().decode("ascii")
    VALIDATOR.read_bytes().decode("ascii")
    fixtures = json.loads(FIXTURES.read_text(encoding="utf-8"))
    validator = load_validator_module()
    assert validator.normalize_evidence_state("current-lesson candidate") == "current-lesson candidate"
    assert validator.normalize_evidence_state("\u672c\u8bfe\u5019\u9009") == "current-lesson candidate"

    with tempfile.TemporaryDirectory() as temp_dir:
        root = Path(temp_dir)
        transcript = root / "transcript.md"
        lecture = root / "lecture.md"
        second_source = root / "second-source.md"
        for path in (transcript, lecture, second_source):
            path.write_text("# Source\n\nEvidence.\n", encoding="utf-8")
        values = {
            "lecture": str(lecture),
            "transcript": str(transcript),
            "second_source": str(second_source),
        }

        passing = (
            ("cards", "english_cards"),
            ("cards", "chinese_cards"),
            ("clues", "english_clues"),
            ("clues", "chinese_clues"),
        )
        for kind, fixture_name in passing:
            path = root / f"{fixture_name}.md"
            path.write_text(fixtures[fixture_name].format(**values), encoding="utf-8")
            output = run(kind, path, 0)
            assert output.stdout.startswith("PASS ")

        failing = (
            ("malformed_state_clues", "invalid evidence state"),
            ("mixed_state_clues", "invalid evidence state"),
            ("mixed_label_clues", "mixes documented label sets"),
            ("mixed_locale_state_clues", "mixes documented label sets"),
        )
        for fixture_name, expected_message in failing:
            path = root / f"{fixture_name}.md"
            path.write_text(fixtures[fixture_name].format(**values), encoding="utf-8")
            output = run("clues", path, 1)
            assert expected_message in output.stdout

    print("validate_learning_assets self-test: PASS (4 valid, 4 rejected)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
