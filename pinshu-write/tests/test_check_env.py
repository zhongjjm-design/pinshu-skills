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


class StyleAssetTests(unittest.TestCase):
    """WRITE-04: on another computer the voice drifts when the profile and materials are not there."""

    def test_reports_each_missing_style_asset(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "profile.md").write_text("x", encoding="utf-8")
            (root / "lib").mkdir()
            cfg = root / "c.yaml"
            cfg.write_text("accounts:\n  - name: A\n    reader: r\n    profile: profile.md\n"
                           "    good_article_standard: ~/definitely-not-here-1012/std.md  # comment\n"
                           "author_style_profile: missing-style.md\nmaterial_folders:\n  - lib\n  - gone-folder\n"
                           "style_card_folders: []\ndrafts_folder: d\nready_folder: r\n", encoding="utf-8")
            named = check_env.style_asset_paths(cfg.read_text(encoding="utf-8"))
            self.assertIn(("material_folders", "gone-folder"), named)
            self.assertIn(("profile", "profile.md"), named)
            item = check_env.check_style_assets(root / "skill", cfg, env={}, cwd=root)
            self.assertEqual(item["status"], "OPTIONAL-MISSING")
            for part in ("std.md", "missing-style.md", "gone-folder"):
                self.assertIn(part, item["detail"])
            self.assertNotIn("profile: profile.md", item["detail"])
            self.assertIn("3 of 5", item["detail"])

    def test_all_present_is_ok_and_never_core_failure(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "p.md").write_text("x", encoding="utf-8")
            cfg = root / "c.yaml"
            cfg.write_text(f"accounts:\n  - name: A\n    reader: r\n    profile: {root / 'p.md'}\n", encoding="utf-8")
            self.assertEqual(check_env.check_style_assets(root / "skill", cfg, env={}, cwd=root)["status"], "OK")
            cfg.write_text("accounts:\n  - name: A\n    profile: nowhere.md\n", encoding="utf-8")
            items, core_ok = check_env.run(root / "skill", cfg, search_path=tmp, env={}, cwd=root)
            self.assertTrue(any(i["what"] == "style assets" and i["status"] == "OPTIONAL-MISSING" for i in items))


class InlineListTests(unittest.TestCase):
    def test_flow_style_list_is_checked(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp); (root / "p.md").write_text("x", encoding="utf-8")
            cfg = root / "c.yaml"
            cfg.write_text("accounts:\n  - name: A\n    profile: p.md\nmaterial_folders: [missing-folder, 'p.md']\n", encoding="utf-8")
            item = check_env.check_style_assets(root / "skill", cfg, env={}, cwd=root)
            self.assertEqual(item["status"], "OPTIONAL-MISSING")
            self.assertIn("missing-folder", item["detail"])
            self.assertIn("1 of 3", item["detail"])


# The first account's private configuration (2026-10-11) uses this older layout; paths here are synthetic.
LEGACY_CONFIG = """# comment line
account:
  name: Example (WeChat)
  profile_authority: profile.md  # the authority
  reader: people who use AI at work
  banned_words_file: gone/banned.txt
  banned_words: [a, b]
paths:
  material_folders:
    - lib
    - notes
  drafts_folder: drafts
model_routing:
  writer:
    command: claude -p "<brief>" --model x
  red_team_and_floor:
    - command: agy -p "<brief>"
    - note: a note with a colon: inside
style:
  voice_profile: voice.md
"""


class LegacyLayoutTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        for name in ("profile.md", "voice.md"):
            (self.root / name).write_text("x", encoding="utf-8")
        for name in ("lib", "notes", "drafts"):
            (self.root / name).mkdir()
        self.cfg = self.root / "pinshu-write.yaml"
        self.cfg.write_text(LEGACY_CONFIG, encoding="utf-8")

    def tearDown(self):
        self.tmp.cleanup()

    def test_account_and_paths_are_read(self):
        item = check_env.check_config(self.root / "skill", self.cfg, env={}, cwd=self.root)
        self.assertEqual(item["status"], "OPTIONAL-MISSING")
        self.assertNotIn("accounts", item["detail"].split("Read with")[0])
        self.assertNotIn("drafts_folder", item["detail"].split("Read with")[0])
        self.assertIn("ready_folder", item["detail"])
        self.assertIn("--ready-dir", item["detail"])
        self.assertIn("older layout", item["detail"])

    def test_filled_legacy_config_is_ok(self):
        self.cfg.write_text(LEGACY_CONFIG.replace("  drafts_folder: drafts\n", "  drafts_folder: drafts\n  ready_folder: ready\n"), encoding="utf-8")
        item = check_env.check_config(self.root / "skill", self.cfg, env={}, cwd=self.root)
        self.assertEqual(item["status"], "OK")
        self.assertIn("older layout", item["detail"])

    def test_nested_style_assets_are_checked(self):
        named = check_env.style_asset_paths(LEGACY_CONFIG)
        for pair in (("profile", "profile.md"), ("author_style_profile", "voice.md"), ("material_folders", "lib"),
                     ("material_folders", "notes"), ("banned_words_file", "gone/banned.txt")):
            self.assertIn(pair, named)
        item = check_env.check_style_assets(self.root / "skill", self.cfg, env={}, cwd=self.root)
        self.assertEqual(item["status"], "OPTIONAL-MISSING")
        self.assertIn("gone/banned.txt", item["detail"])
        self.assertIn("1 of 5", item["detail"])

    def test_template_layout_wins_when_both_present(self):
        config, notes = check_env.load_config("accounts:\n  - name: A\n    reader: r\naccount:\n  name: B\n")
        self.assertEqual(config["accounts"][0]["name"], "A")
        self.assertEqual(notes, [])


class SeedSourceTests(unittest.TestCase):
    """references/seed-discovery.md, step 2: which route an author with no seed gets."""

    TODAY = check_env.datetime.date(2026, 10, 15)

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self.cfg = self.root / "conf" / "pinshu-write.yaml"
        self.cfg.parent.mkdir()

    def tearDown(self):
        self.tmp.cleanup()

    def check(self, text):
        self.cfg.write_text(GOOD_CONFIG + text, encoding="utf-8")
        # cwd elsewhere: relative paths must resolve from the configuration's folder
        return check_env.check_seed_sources(self.root / "skill", self.cfg, env={}, cwd=self.root, today=self.TODAY)

    def pool(self, name, header):
        path = self.cfg.parent / name
        path.write_text(header + "\n- lead one\n", encoding="utf-8")
        return path

    def test_no_sources_uses_public_map(self):
        item = self.check("")
        self.assertEqual(item["status"], "OPTIONAL-MISSING")
        self.assertIn("route 3", item["detail"])
        self.assertIn("public source map", item["detail"])

    def test_no_web_and_no_sources_stops(self):
        item = self.check("web_access: none\n")
        self.assertIn("will stop", item["detail"])
        self.assertIn("not affected", item["detail"])

    def test_fresh_pool_is_route_1(self):
        self.pool("pool.md", "# Topic pool\ngenerated: 2026-10-13")
        item = self.check("topic_pool: pool.md\n")
        self.assertEqual(item["status"], "OK")
        self.assertIn("route 1", item["detail"])
        self.assertIn("2 day(s) ago", item["detail"])

    def test_stale_or_undated_pool_is_historical(self):
        self.pool("old.md", "生成时间：2026-09-01")
        item = self.check("topic_pool: old.md\n")
        self.assertEqual(item["status"], "OPTIONAL-MISSING")
        self.assertIn("route 3", item["detail"])
        self.assertIn("historical leads", item["detail"])
        self.pool("undated.md", "# just leads")
        item = self.check("topic_pool: undated.md\n")
        self.assertIn("states no generation time", item["detail"])

    def test_file_time_is_not_a_generation_time(self):
        path = self.pool("touched.md", "generated: 2026-08-01")
        path.touch()  # modified today; content is still from August
        self.assertIn("historical", self.check("topic_pool: touched.md\n")["detail"])

    def test_pool_folder_reads_newest_stated_file(self):
        folder = self.cfg.parent / "pools"
        folder.mkdir()
        (folder / "a.json").write_text('{"generated_at": "2026-10-14T11:58:18Z", "items": []}', encoding="utf-8")
        (folder / "b.md").write_text("扫描时间：2026-10-02 22:00", encoding="utf-8")
        item = self.check("topic_pool: pools\n")
        self.assertEqual(item["status"], "OK")
        self.assertIn("a.json", item["detail"])

    def test_source_list_is_route_2_and_stale_pool_still_flagged(self):
        (self.cfg.parent / "sources.md").write_text("- a podcast\n", encoding="utf-8")
        self.pool("old.md", "updated: 2026-01-01")
        item = self.check("source_list: sources.md\ntopic_pool: old.md\n")
        self.assertEqual(item["status"], "OK")
        self.assertIn("route 2", item["detail"])
        self.assertIn("historical", item["detail"])

    def test_missing_named_paths_fall_through(self):
        item = self.check("source_list: nowhere.md\ntopic_pool: ~/definitely-not-here-1015/pool.md\n")
        self.assertIn("route 3", item["detail"])
        self.assertIn("not on this computer", item["detail"])

    def test_chinese_and_slash_dates_are_read(self):
        self.pool("cn.md", "生成时间：2026年10月14日")
        self.assertIn("route 1", self.check("topic_pool: cn.md\n")["detail"])
        self.pool("slash.md", "generated: 2026/10/13")
        self.assertIn("route 1", self.check("topic_pool: slash.md\n")["detail"])

    def test_only_generation_markers_count(self):
        self.pool("cand.md", "# Candidate: 2026-10-14 notes")  # "date" inside a word is no marker
        self.assertIn("states no generation time", self.check("topic_pool: cand.md\n")["detail"])
        self.pool("event.md", "generated: 2026-10-13\n- launch, event date: 2026-12-01")  # a lead's own date
        self.assertIn("route 1", self.check("topic_pool: event.md\n")["detail"])
        self.pool("plain.md", "date: 2026-10-12")  # a bare date key at the start of a line counts
        self.assertIn("route 1", self.check("topic_pool: plain.md\n")["detail"])

    def test_lead_dates_never_refresh_an_old_pool(self):
        # Second review, 2026-10-15: leads below an old header made the pool look fresh.
        self.pool("a.md", "generated: 2026-09-01\n- date: 2026-10-14 some lead")
        self.assertIn("historical", self.check("topic_pool: a.md\n")["detail"])
        self.pool("b.md", "generated: 2026-09-01\n- OpenAI updated 2026-10-14 its policy")
        self.assertIn("historical", self.check("topic_pool: b.md\n")["detail"])
        self.pool("c.md", "本池更新于 2026年10月13日")
        self.assertIn("route 1", self.check("topic_pool: c.md\n")["detail"])

    def test_offline_rules(self):
        self.pool("pool.md", "generated: 2026-10-14")
        item = self.check("web_access: none\ntopic_pool: pool.md\n")
        self.assertIn("route 1", item["detail"])
        self.assertIn("not rechecked", item["detail"])
        self.pool("old.md", "generated: 2026-08-01")
        item = self.check("web_access: none\ntopic_pool: old.md\n")
        self.assertIn("will stop", item["detail"])
        item = self.check("web_access: none\nsource_list: https://example.com/list\n")
        self.assertIn("will stop", item["detail"])

    def test_lists_and_urls(self):
        (self.cfg.parent / "a.md").write_text("- x\n", encoding="utf-8")
        item = self.check("source_list:\n  - nowhere.md\n  - a.md\n")
        self.assertIn("route 2", item["detail"])
        item = self.check("source_list: https://example.com/list\n")
        self.assertIn("route 2", item["detail"])
        self.assertIn("read over the web", item["detail"])

    def test_never_a_core_failure(self):
        self.cfg.write_text(GOOD_CONFIG + "web_access: none\n", encoding="utf-8")
        items, core_ok = check_env.run(CheckEnvTests.make_skill(None, self.root), self.cfg, search_path=self.tmp.name,
                                       env={}, cwd=self.root, today=self.TODAY)
        self.assertTrue(core_ok)
        self.assertTrue(any(i["what"] == "seed-discovery sources" for i in items))


class TolerantReaderTests(unittest.TestCase):
    """One unusual line must not hide the keys around it (1.5 read line by line; 1.6 keeps that tolerance)."""

    def read(self, text):
        config, _ = check_env.load_config(text)
        return config

    def test_unusual_lines_are_skipped(self):
        base = GOOD_CONFIG
        for extra in ("---\n", "\ufeff", "note: |\n  free text: with a colon\n  more\n", "账号: 中文键\n",
                      "\"quoted\": 1\n", "weird line without colon\n", "list: [a,\n  b]\n"):
            text = extra + base if extra in ("---\n", "\ufeff") else base + extra
            config = self.read(text)
            self.assertIsNotNone(config, repr(extra))
            self.assertEqual(check_env._config_problems(config), [], repr(extra))
        self.assertEqual(self.read("账号: 中文键\n")["账号"], "中文键")
        self.assertEqual(self.read('"quoted": 1\n')["quoted"], "1")

    def test_tabs_and_comments(self):
        config = self.read("accounts:\n\t- name: A\n\t  reader: r\ndrafts_folder: d\nready_folder: ~/Bob's drafts/  # comment\n")
        self.assertEqual(config["ready_folder"], "~/Bob's drafts/")
        self.assertEqual(config["accounts"][0]["name"], "A")
        self.assertEqual(self.read("x: '#not a comment'  # comment\n")["x"], "#not a comment")

    def test_quoted_hash_is_not_a_comment(self):
        # Second review, 2026-10-15: a quoted path holding " #" was cut at the hash.
        self.assertEqual(self.read('ready_folder: "~/a #1/b"  # comment\n')["ready_folder"], "~/a #1/b")
        self.assertEqual(self.read("ready_folder: '~/a #1/b'\n")["ready_folder"], "~/a #1/b")
        self.assertEqual(self.read("accounts:\n  - name: 'A #1'  # c\n    reader: r\n")["accounts"][0]["name"], "A #1")

    def test_flow_list_over_several_lines_is_not_a_path(self):
        config = self.read("material_folders: [a,\n  b]\ndrafts_folder: d\n")
        self.assertEqual(config["material_folders"], "")
        self.assertEqual(config["drafts_folder"], "d")

    def test_flow_list_keeps_quoted_commas(self):
        self.assertEqual(self.read('material_folders: ["a, b", c]\n')["material_folders"], ["a, b", "c"])


if __name__ == "__main__":
    unittest.main()
