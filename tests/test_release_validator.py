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

CHECKER_PATH = VALIDATOR_PATH.with_name("release_check.py")
CHECKER_SPEC = importlib.util.spec_from_file_location("pinshu_manifest_checker", CHECKER_PATH)
CHECKER = importlib.util.module_from_spec(CHECKER_SPEC)
CHECKER_SPEC.loader.exec_module(CHECKER)


class ReleaseValidatorNegativeControls(unittest.TestCase):
    def run_scan(self, root: Path) -> list[str]:
        with mock.patch.object(VALIDATOR, "ROOT", root), mock.patch.object(
            VALIDATOR, "EXPECTED_SKILLS", set()
        ):
            VALIDATOR.errors.clear()
            setattr(VALIDATOR, "checked_files", 0)
            VALIDATOR.scan_tree()
            return list(VALIDATOR.errors)

    def test_allows_east_asian_public_text(self):
        with tempfile.TemporaryDirectory(prefix="pinshu-release-validator-") as tmp:
            root = Path(tmp)
            (root / "good.md").write_text("公开中文说明可以进入候选包。", encoding="utf-8")
            self.assertFalse(self.run_scan(root))

    def test_allows_east_asian_public_path(self):
        with tempfile.TemporaryDirectory(prefix="pinshu-release-validator-") as tmp:
            root = Path(tmp)
            (root / "中文.md").write_text("safe content", encoding="utf-8")
            self.assertFalse(self.run_scan(root))

    def test_rejects_sensitive_filename_even_with_public_language_path(self):
        with tempfile.TemporaryDirectory(prefix="pinshu-release-validator-") as tmp:
            root = Path(tmp)
            nested = root / "中文配置"
            nested.mkdir()
            (nested / ".env").write_text("PLACEHOLDER=safe", encoding="utf-8")
            self.assertTrue(
                any("sensitive filename" in item for item in self.run_scan(root))
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

    def test_rejects_credential_like_token(self):
        with tempfile.TemporaryDirectory(prefix="pinshu-release-validator-") as tmp:
            root = Path(tmp)
            marker = "ghp_" + "A" * 36
            (root / "bad.md").write_text(marker, encoding="utf-8")
            self.assertTrue(
                any("credential-like token" in item for item in self.run_scan(root))
            )

    def test_rejects_sensitive_filename(self):
        with tempfile.TemporaryDirectory(prefix="pinshu-release-validator-") as tmp:
            root = Path(tmp)
            (root / ".env").write_text("PLACEHOLDER=safe", encoding="utf-8")
            self.assertTrue(
                any("sensitive filename" in item for item in self.run_scan(root))
            )

    def test_audit_marker_exception_is_exact_and_keeps_real_path_checks(self):
        with tempfile.TemporaryDirectory(prefix="pinshu-release-rules-") as tmp:
            root = Path(tmp)
            rule = root / "pinshu-visual-system/scripts/audit_public_bundle.py"
            rule.parent.mkdir(parents=True)
            marker = "MyAI" + "Clone"
            rule.write_text("PATTERN = " + repr(marker), encoding="utf-8")
            with mock.patch.object(CHECKER, "ROOT", root):
                failures = []
                CHECKER.static_checks(failures)
                self.assertEqual(failures, [])
                rule.write_text("PATH = " + repr("/" + "Users/private/data/file"), encoding="utf-8")
                CHECKER.static_checks(failures)
                self.assertTrue(any("private absolute path" in x for x in failures))

    def test_audit_marker_exception_does_not_apply_to_other_files(self):
        with tempfile.TemporaryDirectory(prefix="pinshu-release-rules-") as tmp:
            root = Path(tmp)
            (root / "audit_public_bundle.py").write_text(
                "PATTERN = " + repr("MyAI" + "Clone"), encoding="utf-8")
            with mock.patch.object(CHECKER, "ROOT", root):
                failures = []
                CHECKER.static_checks(failures)
                self.assertTrue(any("private workspace marker" in x for x in failures))

    def test_audit_marker_exception_keeps_independent_secret_scan(self):
        with tempfile.TemporaryDirectory(prefix="pinshu-release-rules-") as tmp:
            root = Path(tmp)
            rule = root / "pinshu-visual-system/scripts/audit_public_bundle.py"
            rule.parent.mkdir(parents=True)
            rule.write_text("TOKEN = " + repr("ghp_" + "A" * 36), encoding="utf-8")
            self.assertTrue(any("credential-like token" in x for x in self.run_scan(root)))


if __name__ == "__main__":
    unittest.main()
