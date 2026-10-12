"""Tests for scripts/check_env.py."""
from __future__ import annotations

import contextlib
import importlib.util
import io
import json
import shutil
import tempfile
import unittest
from pathlib import Path

SKILL = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("check_env", SKILL / "scripts" / "check_env.py")
check_env = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(check_env)


def run_main(args):
    out = io.StringIO()
    with contextlib.redirect_stdout(out):
        code = check_env.main(args)
    return code, out.getvalue()


class CheckEnvTests(unittest.TestCase):
    def make_skill(self, root: Path) -> Path:
        skill = root / "skills" / "pinshu-write"
        shutil.copytree(SKILL / "scripts", skill / "scripts", ignore=shutil.ignore_patterns("__pycache__"))
        return skill

    def test_exit_0_when_only_optional_missing(self):
        with tempfile.TemporaryDirectory() as tmp:
            skill = self.make_skill(Path(tmp))
            config = Path(tmp) / "cfg.yaml"
            config.write_text("accounts: []\n", encoding="utf-8")
            items, core_ok = check_env.run(skill, config, search_path=tmp)  # empty PATH: no model CLI
            self.assertTrue(core_ok)
            statuses = {item["what"]: item["status"] for item in items}
            self.assertEqual(statuses["second-vendor model CLI"], "OPTIONAL-MISSING")
            self.assertEqual(statuses["visual Skill"], "OPTIONAL-MISSING")
            code, text = run_main(["--skill-dir", str(skill), "--config", str(config)])
            self.assertEqual(code, 0)
            self.assertIn("OPTIONAL-MISSING", text)

    def test_missing_config_is_optional(self):
        # Without a config the Skill still runs: it asks for account, reader and folders at the start.
        with tempfile.TemporaryDirectory() as tmp:
            skill = self.make_skill(Path(tmp))
            code, text = run_main(["--skill-dir", str(skill)])
            self.assertEqual(code, 0)
            self.assertIn("OPTIONAL-MISSING: configuration file", text)

    def test_exit_1_when_script_missing(self):
        with tempfile.TemporaryDirectory() as tmp:
            skill = self.make_skill(Path(tmp))
            (skill / "scripts" / "fix_quotes.py").unlink()
            config = Path(tmp) / "cfg.yaml"
            config.write_text("x: 1\n", encoding="utf-8")
            code, _ = run_main(["--skill-dir", str(skill), "--config", str(config)])
            self.assertEqual(code, 1)

    def test_old_python_is_core_failure(self):
        self.assertEqual(check_env.check_python((3, 8, 10))["status"], "MISSING")
        self.assertEqual(check_env.check_python((3, 9, 0))["status"], "OK")

    def test_json_output(self):
        with tempfile.TemporaryDirectory() as tmp:
            skill = self.make_skill(Path(tmp))
            config = Path(tmp) / "cfg.yaml"
            config.write_text("x: 1\n", encoding="utf-8")
            code, text = run_main(["--skill-dir", str(skill), "--config", str(config), "--json"])
            data = json.loads(text)
            self.assertEqual(code, 0)
            self.assertTrue(data["core_ok"])
            self.assertTrue(all({"status", "what", "detail"} <= set(item) for item in data["items"]))


GOOD_CONFIG = (
    "accounts:\n  - name: A\n    reader: \"people who use AI\"  # who reads\n"
    "drafts_folder: ~/w/drafts/\nready_folder: ~/w/ready/\n"
)


def fake_cli(directory: Path, *names):
    for name in names:
        path = directory / name
        path.write_text("#!/bin/sh\nexit 1\n", encoding="utf-8")  # present but never works
        path.chmod(0o755)


class ModelTests(unittest.TestCase):
    def test_single_vendor_is_not_a_second_vendor(self):
        with tempfile.TemporaryDirectory() as tmp:
            fake_cli(Path(tmp), "claude")
            item = check_env.check_models(tmp)
            self.assertEqual(item["status"], "OPTIONAL-MISSING")
            self.assertIn("one vendor", item["detail"])

    def test_two_vendors_found_but_unverified(self):
        with tempfile.TemporaryDirectory() as tmp:
            fake_cli(Path(tmp), "claude", "gemini")
            item = check_env.check_models(tmp)
            self.assertEqual(item["status"], "UNVERIFIED")
            self.assertIn("not verified", item["detail"])

    def test_agy_alone_counts_as_two_vendors(self):
        with tempfile.TemporaryDirectory() as tmp:
            fake_cli(Path(tmp), "agy")
            self.assertEqual(check_env.check_models(tmp)["status"], "UNVERIFIED")

    def test_unverified_does_not_fail_core(self):
        with tempfile.TemporaryDirectory() as tmp:
            skill = CheckEnvTests.make_skill(None, Path(tmp))
            fake_cli(Path(tmp), "claude", "gemini")
            _, core_ok = check_env.run(skill, search_path=tmp, env={}, cwd=Path(tmp))
            self.assertTrue(core_ok)


class ScreenshotTests(unittest.TestCase):
    def test_capture_script_presence(self):
        with tempfile.TemporaryDirectory() as tmp:
            skill = Path(tmp) / "skills" / "pinshu-write"
            skill.mkdir(parents=True)
            self.assertEqual(check_env.check_screenshots(skill)["status"], "OPTIONAL-MISSING")
            script = skill.parent / check_env.VISUAL_SKILL / "scripts" / "capture_evidence.py"
            script.parent.mkdir(parents=True)
            script.write_text("", encoding="utf-8")
            item = check_env.check_screenshots(skill)
            self.assertEqual(item["status"], "UNVERIFIED")
            self.assertIn("browser", item["detail"])


class ConfigTests(unittest.TestCase):
    def check(self, tmp, text, **kw):
        cfg = Path(tmp) / "c.yaml"
        cfg.write_text(text, encoding="utf-8")
        return check_env.check_config(Path(tmp) / "skill", cfg, env={}, cwd=Path(tmp), **kw)

    def test_filled_config_is_ok(self):
        with tempfile.TemporaryDirectory() as tmp:
            self.assertEqual(self.check(tmp, GOOD_CONFIG)["status"], "OK")

    def test_template_itself_is_ok(self):
        # The shipped example has every required key filled with example values.
        with tempfile.TemporaryDirectory() as tmp:
            text = (SKILL / "templates" / "config.example.yaml").read_text(encoding="utf-8")
            self.assertEqual(self.check(tmp, text)["status"], "OK")

    def test_missing_keys_named(self):
        with tempfile.TemporaryDirectory() as tmp:
            item = self.check(tmp, "x: 1\n")
            self.assertEqual(item["status"], "OPTIONAL-MISSING")
            for key in ("accounts", "drafts_folder", "ready_folder"):
                self.assertIn(key, item["detail"])
            item = self.check(tmp, GOOD_CONFIG.replace('reader: "people who use AI"', "reader:").replace("ready_folder: ~/w/ready/", "ready_folder:"))
            self.assertIn("reader", item["detail"])
            self.assertIn("ready_folder", item["detail"])
            self.assertNotIn("drafts_folder", item["detail"])

    def test_not_understood_is_not_ok(self):
        with tempfile.TemporaryDirectory() as tmp:
            item = self.check(tmp, "\n\n- just a list\n")
            self.assertEqual(item["status"], "UNVERIFIED")
            self.assertIn("content not checked", item["detail"])

    def test_search_order(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            skill = root / "skill"
            skill.mkdir()
            cwd = root / "cwd"
            cwd.mkdir()
            (skill / check_env.CONFIG_NAME).write_text("a: 1\n", encoding="utf-8")
            self.assertEqual(check_env.find_config(skill, None, {}, cwd)[0], skill / check_env.CONFIG_NAME)
            (cwd / check_env.CONFIG_NAME).write_text("a: 1\n", encoding="utf-8")
            self.assertEqual(check_env.find_config(skill, None, {}, cwd)[0], cwd / check_env.CONFIG_NAME)
            envfile = root / "env.yaml"
            envfile.write_text("a: 1\n", encoding="utf-8")
            self.assertEqual(check_env.find_config(skill, None, {check_env.CONFIG_ENV: str(envfile)}, cwd)[0], envfile)
            flag = root / "flag.yaml"
            flag.write_text("a: 1\n", encoding="utf-8")
            self.assertEqual(check_env.find_config(skill, flag, {check_env.CONFIG_ENV: str(envfile)}, cwd)[0], flag)

    def test_not_found_advice(self):
        with tempfile.TemporaryDirectory() as tmp:
            item = check_env.check_config(Path(tmp) / "skill", None, env={}, cwd=Path(tmp))
            self.assertEqual(item["status"], "OPTIONAL-MISSING")
            self.assertIn("--config", item["detail"])
            self.assertIn("Do not copy private paths", item["detail"])


if __name__ == "__main__":
    unittest.main()
