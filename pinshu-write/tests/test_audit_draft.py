"""Offline regression tests for pinshu-write/scripts/audit_draft.py."""
from __future__ import annotations

import importlib.util
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "audit_draft.py"
SPEC = importlib.util.spec_from_file_location("audit_draft", SCRIPT)
audit_draft = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(audit_draft)

FILLER = "\u7532\u65b9\u91c7\u8d2d\u6309\u4eba\u5934\u548c\u5929\u6570\u6bd4\u4ef7\uff0c\u8fd9\u5957\u7b97\u6cd5\u7528\u4e86\u5f88\u591a\u5e74\u3002" * 14
CLEAN = (
    "# \u522b\u8ba9\u7701\u4e0b\u7684\u94b1\u53d8\u6210\u6298\u6263\n\n"
    f"{FILLER}\n\n"
    "## \u7b2c\u4e00\u8282\n\n"
    f"{FILLER}\n\n"
    "## \u7b2c\u4e8c\u8282\n\n"
    f"{FILLER}\n\n"
    "\u8d44\u6599\u6765\u6e90\n\n- \u67d0\u62a5\u544a 2026-03\uff08\u6765\u6e90\u5217\u8868\u91cc\u7684\u62ec\u53f7\u4e0d\u7b97\uff09\n"
)


def run(text: str, **overrides):
    options = dict(banned=list(audit_draft.DEFAULT_BANNED), length=(100, 4000), hard_max=6000,
                   section_min=100, section_max=900, you_per_k=10.0, para_max=400, subhead_range=(3, 14))
    options.update(overrides)
    return audit_draft.audit(text, **options)


def rules(report, level=None):
    return [f["rule"] for f in report["findings"] if level is None or f["level"] == level]


class AuditDraftTests(unittest.TestCase):
    def test_clean_draft_has_no_blockers_or_fixes(self):
        report = run(CLEAN)
        self.assertEqual(report["counts"]["blocker"], 0, report["findings"])
        self.assertEqual(report["counts"]["fix"], 0, report["findings"])
        self.assertGreater(report["stats"]["body_characters"], 300)

    def test_sources_list_is_excluded_from_body(self):
        report = run(CLEAN)
        self.assertNotIn("move inline source to the end source list", rules(report))

    def test_em_dash_and_reversal_and_banned_word_are_blockers(self):
        text = CLEAN.replace("## \u7b2c\u4e00\u8282\n\n", "## \u7b2c\u4e00\u8282\n\n\u6548\u7387\u4e0d\u662f\u5356\u70b9\uff0c\u800c\u662f\u7b79\u7801\u2014\u2014\u9274\u4e8e\u6b64\u8981\u62c6\u5f00\u62a5\u3002\n\n")
        found = rules(run(text), "blocker")
        self.assertIn("no em dash", found)
        self.assertIn("banned word", found)
        self.assertTrue(any(r.startswith("single-sentence reversal") for r in found), found)

    def test_short_separated_reversal_is_allowed(self):
        text = CLEAN.replace("## \u7b2c\u4e00\u8282\n\n", "## \u7b2c\u4e00\u8282\n\n\u4ef7\u683c\u662f\u4e0d\u662f\u53ef\u4ee5\u5f80\u4e0b\u8c03\u4e00\u8c03\uff1f\u4e0d\u662f\u3002\u662f\u5148\u62c6\u5f00\u3002\n\n")
        self.assertFalse(any(r.startswith("single-sentence reversal") for r in rules(run(text))))

    def test_inline_source_bold_and_straight_quotes_need_fixing(self):
        text = CLEAN.replace("## \u7b2c\u4e8c\u8282\n\n", '## \u7b2c\u4e8c\u8282\n\n\u91c7\u8d2d\u8bf4"\u90a3\u5c31\u964d\u4ef7"\uff08\u67d0\u5468\u520a 2026-02\uff09\uff0c**\u8fd9\u5f88\u5173\u952e**\u3002\n\n')
        found = rules(run(text), "fix")
        self.assertIn("move inline source to the end source list", found)
        self.assertIn("no bold in body text", found)
        self.assertIn("use curly Chinese quotes \u201c \u201d", found)

    def test_two_h1_titles_block(self):
        self.assertIn("exactly one H1 title", rules(run("# \u4e00\n\n# \u4e8c\n\n\u6b63\u6587\u3002\n")))

    def test_extra_banned_words_and_hard_maximum(self):
        report = run(CLEAN, banned=["\u7b97\u6cd5"], hard_max=200)
        found = rules(report, "blocker")
        self.assertIn("banned word", found)
        self.assertTrue(any(r.startswith("body longer than the hard maximum") for r in found))

    def test_uneven_or_long_subheads_are_flagged(self):
        text = CLEAN.replace("## \u7b2c\u4e00\u8282", "## \u4eba\u4eba\u90fd\u5728\u7528\u4e86\u518d\u6bd4\u8c01\u7528\u5f97\u591a\u5c31\u6bd4\u51fa\u4e86\u770b\u7740\u50cf\u5e72\u5b8c\u4e86\u7684\u6d3b")
        found = rules(run(text))
        self.assertTrue(any(r.startswith("subhead length outside") for r in found), found)
        self.assertIn("subhead lengths differ by more than 5 characters", found)

    def test_even_plain_subheads_pass(self):
        text = CLEAN.replace("## \u7b2c\u4e00\u8282", "## \u521a\u5f00\u59cb\u63a8AI\u903c\u4e00\u903c\u662f\u5bf9\u7684").replace("## \u7b2c\u4e8c\u8282", "## \u6bd4\u8c01\u7528\u5f97\u591a\u6bd4\u51fa\u534a\u6210\u54c1")
        found = rules(run(text))
        self.assertFalse(any(r.startswith("subhead") for r in found), found)

    def test_hypothetical_opening_is_flagged(self):
        text = CLEAN.replace(FILLER + "\n\n## \u7b2c\u4e00\u8282", "\u5047\u8bbe\u4f60\u662f\u4e00\u5bb6\u516c\u53f8\u7684\u8001\u677f\u3002" + FILLER + "\n\n## \u7b2c\u4e00\u8282", 1)
        found = rules(run(text))
        self.assertTrue(any(r.startswith("opening uses a hypothetical scene") for r in found), found)

    def test_foreign_terms_are_listed_once(self):
        text = CLEAN.replace("## \u7b2c\u4e8c\u8282\n\n", "## \u7b2c\u4e8c\u8282\n\n\u636e The Information \u62a5\u9053\uff0cToken \u548c AI \u90fd\u5728\u6da8\uff0cToken \u53c8\u6da8\u4e86\u3002\n\n")
        terms = [f["detail"] for f in run(text)["findings"] if f["rule"].startswith("foreign term")]
        self.assertEqual(sorted(terms), ["The Information", "Token"])

    def test_prompt_colon_is_flagged(self):
        text = CLEAN.replace("## \u7b2c\u4e8c\u8282\n\n", "## \u7b2c\u4e8c\u8282\n\n\u505a\u8fd9\u7c7b\u6d3b\u6709\u4e2a\u5173\u952e\u95ee\u9898\uff1a\u5ba2\u6237\u6700\u62c5\u5fc3\u7684\u662f\u642d\u5b8c\u4e4b\u540e\u8c01\u6765\u7ba1\u3002\n\n")
        hits = [f["detail"] for f in run(text)["findings"] if f["rule"].startswith("prompt colon")]
        self.assertEqual(hits, ["\u95ee\u9898\uff1a"])

    def test_abrupt_comment_opening_is_flagged_but_linked_one_is_not(self):
        abrupt = "\u503c\u5f97\u6ce8\u610f\u7684\u662f\uff0c\u91c7\u8d2d\u53ea\u770b\u603b\u4ef7\u3002"
        linked = "\u4f46\u95ee\u9898\u5728\u4e8e\uff0c\u91c7\u8d2d\u53ea\u770b\u603b\u4ef7\u3002"
        found = rules(run(CLEAN.replace("## \u7b2c\u4e8c\u8282\n\n", "## \u7b2c\u4e8c\u8282\n\n" + abrupt + "\n\n")))
        self.assertIn("abrupt comment opens a paragraph without linking to the previous one", found)
        found = rules(run(CLEAN.replace("## \u7b2c\u4e8c\u8282\n\n", "## \u7b2c\u4e8c\u8282\n\n" + linked + "\n\n")))
        self.assertNotIn("abrupt comment opens a paragraph without linking to the previous one", found)

    def test_front_matter_is_not_read_as_body(self):
        report = run("---\ndate: 2026-10-07\nstatus: draft\n---\n\n" + CLEAN)
        self.assertEqual(report["counts"]["blocker"], 0, report["findings"])
        terms = [f["detail"] for f in report["findings"] if f["rule"].startswith("foreign term")]
        self.assertNotIn("date", terms)
        self.assertNotIn("status", terms)

    def test_rules_print_chinese_patterns_without_a_draft(self):
        done = subprocess.run([sys.executable, str(SCRIPT), "--rules"], capture_output=True, text=True)
        self.assertEqual(done.returncode, 0, done.stderr)
        for word in audit_draft.DEFAULT_BANNED:
            self.assertIn(word, done.stdout)
        self.assertIn("\u4e0d\u662f", done.stdout)

    def test_cli_exit_code_reflects_blockers(self):
        with tempfile.TemporaryDirectory() as tmp:
            good = Path(tmp, "good.md")
            bad = Path(tmp, "bad.md")
            good.write_text(CLEAN, encoding="utf-8")
            bad.write_text(CLEAN.replace("## \u7b2c\u4e00\u8282", "## \u7b2c\u4e00\u8282\u2014\u2014"), encoding="utf-8")
            ok = subprocess.run([sys.executable, str(SCRIPT), str(good), "--length", "100-4000"],
                                capture_output=True, text=True)
            ko = subprocess.run([sys.executable, str(SCRIPT), str(bad), "--length", "100-4000"],
                                capture_output=True, text=True)
        self.assertEqual(ok.returncode, 0, ok.stdout + ok.stderr)
        self.assertEqual(ko.returncode, 1, ko.stdout + ko.stderr)


if __name__ == "__main__":
    unittest.main()
