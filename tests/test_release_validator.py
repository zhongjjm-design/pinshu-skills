#!/usr/bin/env python3
"""Negative controls for the public release validator."""
from __future__ import annotations

import importlib.util
import tempfile
import unittest
from pathlib import Path
from unittest import mock

VALIDATOR_PATH = Path(__file__).resolve().parents[1] / "scripts" / "validate_release.py"
SPEC = importlib.util.spec_from_file_location("pinshu_release_validator", VALIDATOR_PATH)
if SPEC is None or SPEC.loader is None:
    raise RuntimeError(f"Cannot load release validator: {VALIDATOR_PATH}")
VALIDATOR = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(VALIDATOR)


class ReleaseValidatorNegativeControls(unittest.TestCase):
    def run_scan(self, root: Path) -> list[str]:
        with mock.patch.object(VALIDATOR, "ROOT", root), mock.patch.object(
            VALIDATOR, "EXPECTED_SKILLS", set()
        ):
            VALIDATOR.errors.clear()
            setattr(VALIDATOR, "checked_files", 0)
            VALIDATOR.scan_tree()
            return list(VALIDATOR.errors)

    def test_rejects_east_asian_script(self):
        with tempfile.TemporaryDirectory(prefix="pinshu-release-validator-") as tmp:
            root = Path(tmp)
            (root / "bad.md").write_text("forbidden: \u4e2d\u6587", encoding="utf-8")
            self.assertTrue(
                any("East Asian script in text" in item for item in self.run_scan(root))
            )

    def test_rejects_personal_absolute_paths(self):
        with tempfile.TemporaryDirectory(prefix="pinshu-release-validator-") as tmp:
            root = Path(tmp)
            personal = "/" + "Users/private/Documents/secret.txt"
            (root / "bad.md").write_text(personal, encoding="utf-8")
            self.assertTrue(
                any("personal absolute path" in item for item in self.run_scan(root))
            )

    def test_rejects_symlinks(self):
        with tempfile.TemporaryDirectory(prefix="pinshu-release-validator-") as tmp:
            root = Path(tmp)
            target = root / "target.txt"
            target.write_text("safe", encoding="utf-8")
            (root / "link.txt").symlink_to(target)
            self.assertTrue(
                any("symlink is not allowed" in item for item in self.run_scan(root))
            )


if __name__ == "__main__":
    unittest.main()
