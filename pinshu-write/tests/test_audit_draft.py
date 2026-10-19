"""Offline regression tests for pinshu-write/scripts/audit_draft.py."""
from __future__ import annotations

import importlib.util
import json
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

    def test_inline_source_and_straight_quotes_need_fixing_and_bold_passes(self):
        text = CLEAN.replace("## \u7b2c\u4e8c\u8282\n\n", '## \u7b2c\u4e8c\u8282\n\n\u91c7\u8d2d\u8bf4"\u90a3\u5c31\u964d\u4ef7"\uff08\u67d0\u5468\u520a 2026-02\uff09\uff0c**\u8fd9\u5f88\u5173\u952e**\u3002\n\n')
        found = rules(run(text), "fix")
        self.assertIn("move inline source to the end source list", found)
        self.assertFalse(any("bold" in r for r in rules(run(text))))
        self.assertIn("use curly Chinese quotes \u201c \u201d", found)

    def test_two_h1_titles_block(self):
        self.assertIn("exactly one H1 title", rules(run("# \u4e00\n\n# \u4e8c\n\n\u6b63\u6587\u3002\n")))

    def test_first_draft_over_hard_maximum_is_a_reminder(self):
        draft = run(CLEAN, hard_max=200, first_draft=True)
        self.assertFalse(any(r.startswith("body longer than the hard maximum") for r in rules(draft)))
        self.assertTrue(any(r.startswith("first draft longer than the hard maximum") for r in rules(draft, "warn")))
        final = run(CLEAN, hard_max=200)
        self.assertTrue(any(r.startswith("body longer than the hard maximum") for r in rules(final, "blocker")))

    def test_same_word_opening_three_sentences_in_a_row(self):
        para = "\u6211\u4eec\u5148\u628a\u6750\u6599\u6574\u7406\u597d\u3002\u6211\u4eec\u518d\u53bb\u627e\u6848\u4f8b\u3002\u6211\u4eec\u6700\u540e\u5199\u521d\u7a3f\u3002"
        found = rules(run(f"# \u6807\u9898\u5728\u8fd9\u91cc\n\n{para}\n"), "warn")
        self.assertTrue(any("open with the same word" in r for r in found), found)
        varied = "\u6211\u4eec\u5148\u628a\u6750\u6599\u6574\u7406\u597d\u3002\u7136\u540e\u53bb\u627e\u6848\u4f8b\u3002\u6211\u4eec\u6700\u540e\u5199\u521d\u7a3f\u3002"
        self.assertFalse(any("open with the same word" in r for r in rules(run(f"# \u6807\u9898\u5728\u8fd9\u91cc\n\n{varied}\n"))))

    def test_sections_of_near_equal_length(self):
        def section(n):
            return "\u5ba2\u6237\u6309\u4eba\u5934\u6bd4\u4ef7\uff0c\u5c31\u4f1a\u538b\u4f4e\u62a5\u4ef7\u3002" * n
        even = "# \u6807\u9898\u5728\u8fd9\u91cc\n\n" + "".join(f"## \u5c0f\u6807\u9898{i}\n\n{section(10)}\n\n" for i in range(3))
        self.assertTrue(any(r.startswith("sections are nearly the same length") for r in rules(run(even), "warn")))
        uneven = ("# \u6807\u9898\u5728\u8fd9\u91cc\n\n## \u5c0f\u6807\u9898\u7532\n\n" + section(10) + "\n\n## \u5c0f\u6807\u9898\u4e59\n\n"
                  + section(16) + "\n\n## \u5c0f\u6807\u9898\u4e19\n\n" + section(12) + "\n")
        self.assertFalse(any(r.startswith("sections are nearly the same length") for r in rules(run(uneven))))

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

    def test_hypothetical_opening_must_be_fixed(self):
        text = CLEAN.replace(FILLER + "\n\n## \u7b2c\u4e00\u8282", "\u5047\u8bbe\u4f60\u662f\u4e00\u5bb6\u516c\u53f8\u7684\u8001\u677f\u3002" + FILLER + "\n\n## \u7b2c\u4e00\u8282", 1)
        found = rules(run(text), "fix")
        self.assertTrue(any(r.startswith("opening uses a hypothetical scene") for r in found), found)

    def test_real_event_opening_is_not_flagged(self):
        text = CLEAN.replace(FILLER + "\n\n## \u7b2c\u4e00\u8282", "\u4e0a\u5468\u4e09\uff0c\u4e00\u5bb6\u5e7f\u544a\u516c\u53f8\u63a5\u5230\u7532\u65b9\u7684\u538b\u4ef7\u90ae\u4ef6\u3002" + FILLER + "\n\n## \u7b2c\u4e00\u8282", 1)
        self.assertFalse(any(r.startswith("opening uses a hypothetical scene") for r in rules(run(text))))

    def test_even_paragraph_lengths_are_flagged(self):
        unit = "\u7532\u65b9\u91c7\u8d2d\u6309\u4eba\u5934\u6bd4\u4ef7\u3002"  # 9 CJK characters
        even = "\n\n".join(unit * 6 for _ in range(10))
        found = rules(run("# \u6807\u9898\n\n" + even + "\n"))
        self.assertIn("paragraph lengths are too even across the article", found)
        self.assertIn("5 paragraphs in a row have nearly the same length", found)

    def test_varied_paragraph_lengths_pass(self):
        unit = "\u7532\u65b9\u91c7\u8d2d\u6309\u4eba\u5934\u6bd4\u4ef7\u3002"
        varied = "\n\n".join(unit * n for n in (2, 9, 4, 14, 3, 7, 16, 2, 10, 5))
        found = rules(run("# \u6807\u9898\n\n" + varied + "\n"))
        self.assertNotIn("paragraph lengths are too even across the article", found)
        self.assertFalse(any("in a row have nearly the same length" in r for r in found), found)

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

    def test_card_mode_keeps_wording_rules_and_drops_article_shape(self):
        card = "# \u5224\u65ad\u5361\n\n\u5047\u8bbe\u4f60\u662f\u8001\u677f\u3002\u6548\u7387\u4e0d\u662f\u5356\u70b9\uff0c\u800c\u662f\u7b79\u7801\u3002\n\n## \u4e00\n\n\u77ed\u3002\n"
        found = rules(run(card, card=True))
        self.assertTrue(any(r.startswith("single-sentence reversal") for r in found), found)
        for skipped in ("opening uses", "section outside", "subhead length", "body outside", "single-sentence paragraphs"):
            self.assertFalse(any(r.startswith(skipped) for r in found), (skipped, found))

    def test_single_sentence_paragraphs_block_only_two_in_a_row(self):
        one = "\u8fd9\u4e00\u53e5\u8bdd\u81ea\u5df1\u5360\u4e86\u4e00\u6bb5\u3002"
        apart = CLEAN.replace("## \u7b2c\u4e00\u8282\n\n", "## \u7b2c\u4e00\u8282\n\n" + one + "\n\n")
        apart = apart.replace("## \u7b2c\u4e8c\u8282\n\n", "## \u7b2c\u4e8c\u8282\n\n" + one + "\n\n")
        self.assertFalse(any(r.startswith("single-sentence paragraphs") for r in rules(run(apart))))
        together = CLEAN.replace("## \u7b2c\u4e00\u8282\n\n", "## \u7b2c\u4e00\u8282\n\n" + one + "\n\n" + one + "\n\n")
        self.assertTrue(any(r.startswith("single-sentence paragraphs in a row") for r in rules(run(together), "blocker")))
        listed = CLEAN.replace("## \u7b2c\u4e00\u8282\n\n", "## \u7b2c\u4e00\u8282\n\n1. " + one + "\n2. " + one + "\n\n\u4e00\u3001" + one + "\n\n\u4e8c\u3001" + one + "\n\n")
        self.assertFalse(any(r.startswith("single-sentence paragraphs") for r in rules(run(listed))))

    def test_numbered_subhead_warns_and_plain_subhead_does_not(self):
        text = CLEAN.replace("## \u7b2c\u4e00\u8282", "## 01 \u4f1a\u7528\u8d8a\u6765\u8d8a\u5bb9\u6613")
        self.assertIn("numbered subhead: write the heading as a sentence without a number", rules(run(text)))
        plain = CLEAN.replace("## \u7b2c\u4e00\u8282", "## \u4e09\u4e2a\u4eba\u7684\u90e8\u95e8\uff0c\u600e\u4e48\u5206\u5de5")
        self.assertFalse(any(r.startswith("numbered subhead") for r in rules(run(plain))))

    def test_default_subhead_limit_is_sixteen_characters(self):
        heading = "\u4f1a\u7528\u8d8a\u6765\u8d8a\u5bb9\u6613\uff0c\u7528\u597d\u8d8a\u6765\u8d8a\u96be\u4e86\u554a"  # 15 characters
        text = CLEAN.replace("## \u7b2c\u4e00\u8282", "## " + heading).replace("## \u7b2c\u4e8c\u8282", "## " + heading)
        with tempfile.TemporaryDirectory() as tmp:
            draft = Path(tmp) / "d.md"
            draft.write_text(text, encoding="utf-8")
            done = subprocess.run([sys.executable, str(SCRIPT), str(draft), "--length", "100-4000", "--json"], capture_output=True, text=True)
        found = [f["rule"] for f in json.loads(done.stdout)["findings"]]
        self.assertFalse(any(r.startswith("subhead length outside") for r in found), found)

    def test_short_subhead_is_not_flagged_by_default(self):
        text = CLEAN.replace("## \u7b2c\u4e00\u8282", "## \u5148\u7b97\u8d26").replace("## \u7b2c\u4e8c\u8282", "## \u518d\u5b9a\u4ef7")
        with tempfile.TemporaryDirectory() as tmp:
            draft = Path(tmp) / "d.md"
            draft.write_text(text, encoding="utf-8")
            done = subprocess.run([sys.executable, str(SCRIPT), str(draft), "--length", "100-4000", "--json"], capture_output=True, text=True)
        found = [f["rule"] for f in json.loads(done.stdout)["findings"]]
        self.assertFalse(any(r.startswith("subhead length outside") for r in found), found)

    def test_rules_print_chinese_patterns_without_a_draft(self):
        done = subprocess.run([sys.executable, str(SCRIPT), "--rules"], capture_output=True, text=True)
        self.assertEqual(done.returncode, 0, done.stderr)
        for word in audit_draft.DEFAULT_BANNED:
            self.assertIn(word, done.stdout)
        self.assertIn("\u4e0d\u662f", done.stdout)

    def test_explained_foreign_terms_are_not_listed(self):
        para = "\u6a21\u578b\u6309 Token\uff08\u6a21\u578b\u6309\u5b57\u6570\u8ba1\u8d39\u7684\u5355\u4f4d\uff09\u6536\u94b1\u3002Duolingo \u662f\u4e00\u5bb6\u505a\u8bed\u8a00\u5b66\u4e60\u7684\u516c\u53f8\u3002\u591a\u90bb\u56fd\uff08Duolingo\uff09\u7684\u8001\u677f\u8bf4\u8fc7\u3002RAG\uff0c\u4e5f\u5c31\u662f\u5148\u67e5\u8d44\u6599\u518d\u56de\u7b54\u3002SaaS (\u6309\u6708\u4ed8\u8d39\u7684\u8f6f\u4ef6) \u4e5f\u4e00\u6837\u3002\u636e The Information \u62a5\u9053\uff0c\u4ef7\u683c\u53c8\u6da8\u4e86\u3002"
        text = CLEAN.replace("## \u7b2c\u4e8c\u8282\n\n", "## \u7b2c\u4e8c\u8282\n\n" + para + "\n\n")
        terms = [f["detail"] for f in run(text)["findings"] if f["rule"].startswith("foreign term")]
        self.assertEqual(terms, ["The Information"])

    def test_term_explained_only_later_is_still_listed_at_first_use(self):
        para = "Token \u53c8\u6da8\u4ef7\u4e86\u3002Token\uff08\u6a21\u578b\u6309\u5b57\u6570\u8ba1\u8d39\u7684\u5355\u4f4d\uff09\u662f\u6309\u91cf\u7b97\u7684\u3002"
        text = CLEAN.replace("## \u7b2c\u4e8c\u8282\n\n", "## \u7b2c\u4e8c\u8282\n\n" + para + "\n\n")
        terms = [f["detail"] for f in run(text)["findings"] if f["rule"].startswith("foreign term")]
        self.assertEqual(terms, ["Token"])

    def _terms(self, para, rule="foreign term"):
        text = CLEAN.replace("## \u7b2c\u4e8c\u8282\n\n", "## \u7b2c\u4e8c\u8282\n\n" + para + "\n\n")
        return [f["detail"] for f in run(text)["findings"] if f["rule"].startswith(rule)]

    def test_foreign_term_in_title_and_subhead_is_listed(self):
        text = CLEAN.replace("# ", "# \u7528 RAG \u505a\u8d44\u6599\u68c0\u7d22 ", 1).replace(
            "## \u7b2c\u4e00\u8282", "## \u5148\u628a Prompt \u5199\u6e05\u695a")
        found = [f for f in run(text)["findings"] if f["rule"].startswith("foreign term in a title")]
        self.assertEqual(sorted(f["detail"] for f in found), ["Prompt", "RAG"])

    def test_explained_term_in_subhead_is_not_listed(self):
        text = CLEAN.replace("## \u7b2c\u4e00\u8282", "## \u5148\u67e5\u8d44\u6599 RAG\uff08\u5148\u67e5\u8d44\u6599\u518d\u56de\u7b54\uff09")
        found = [f for f in run(text)["findings"] if f["rule"].startswith("foreign term in a title")]
        self.assertEqual(found, [])

    def test_empty_bracket_does_not_explain(self):
        self.assertEqual(self._terms("\u6a21\u578b\u6309 Token\uff08\uff09\u6536\u8d39\u3002"), ["Token"])

    def test_latin_only_bracket_does_not_explain(self):
        self.assertIn("Token", self._terms("\u6a21\u578b\u6309 Token\uff08API\uff09\u6536\u8d39\u3002"))

    def test_explanation_phrase_must_follow_the_term_closely(self):
        self.assertEqual(self._terms("SaaS \u5f88\u8d35\uff0c\u8fd9\u662f\u4e00\u79cd\u6210\u672c\u538b\u529b\u3002"), ["SaaS"])

    def test_explanation_phrase_right_after_the_term_counts(self):
        self.assertEqual(self._terms("SaaS\uff0c\u4e5f\u5c31\u662f\u6309\u6708\u4ed8\u8d39\u7684\u8f6f\u4ef6\uff0c\u8d8a\u6765\u8d8a\u8d35\u3002"), [])

    def test_short_name_before_the_term_counts(self):
        self.assertEqual(self._terms("\u68c0\u7d22\u589e\u5f3a\u751f\u6210\uff0c\u7b80\u79f0 RAG\uff0c\u73b0\u5728\u5f88\u5e38\u89c1\u3002"), [])

    def test_urls_and_markdown_links_are_not_terms(self):
        para = "\u539f\u6587\u5728 https://example.com/path \u53ef\u4ee5\u770b\u5230\uff0c[\u62a5\u544a](https://example.org/report-final)\u4e5f\u5728\u3002"
        self.assertEqual(self._terms(para), [])

    def test_link_text_is_still_checked(self):
        self.assertEqual(self._terms("\u89c1 [Anthropic \u7684\u8bf4\u660e](https://example.org/a)\u3002"), ["Anthropic"])

    def test_rules_print_title_examples(self):
        done = subprocess.run([sys.executable, str(SCRIPT), "--rules"], capture_output=True, text=True)
        self.assertEqual(done.returncode, 0, done.stderr)
        self.assertIn("\u6807\u9898\u8981\u6709\u7279\u8272", done.stdout)
        self.assertIn("\u4e09\u4e2a", done.stdout)
        self.assertNotIn("\u2014\u2014", done.stdout.split("\u6807\u9898\u8981\u6709\u7279\u8272")[1])

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


class QuestionFormTests(unittest.TestCase):
    def test_shi_bu_shi_question_is_not_a_reversal(self):
        text = CLEAN.replace(FILLER, FILLER + "\u6210\u679c\u662f\u4e0d\u662f\u7ecf\u5f97\u8d77\u68c0\u67e5\uff0c\u662f\u4e0d\u662f\u6709\u4ef7\u503c\uff1f", 1)
        self.assertNotIn("single-sentence reversal: not X, (it) is Y", rules(run(text)))

    def test_plain_not_x_is_y_still_flagged(self):
        text = CLEAN.replace(FILLER, FILLER + "\u8fd9\u4e0d\u662f\u5de5\u5177\u7684\u95ee\u9898\uff0c\u662f\u4eba\u7684\u95ee\u9898\u3002", 1)
        self.assertIn("single-sentence reversal: not X, (it) is Y", rules(run(text)))


EXPORT = Path(__file__).resolve().parents[1] / "scripts" / "export_article.py"


class ReadyExportTests(unittest.TestCase):
    def test_ready_copy_has_agreed_header_and_no_notes(self):
        with tempfile.TemporaryDirectory() as tmp:
            draft = Path(tmp) / "draft.md"
            draft.write_text("---\nstatus: v3\n---\n\n# \u6807\u9898\n\n\u6b63\u6587\u3002\n\n===EDITOR NOTES===\n\u5907\u6ce8\n", encoding="utf-8")
            out = subprocess.run([sys.executable, str(EXPORT), "--source", str(draft), "--ready-dir", str(Path(tmp) / "ready"),
                                  "--account", "\u54c1\u53d4", "--date", "2026-10-11", "--writer", "m1", "--process-dir", tmp,
                                  "--approval", "\u5b9a\u7a3f"],
                                 capture_output=True, text=True)
            self.assertEqual(out.returncode, 0, out.stderr)
            target = Path(tmp) / "ready" / "\u54c1\u53d4" / "2026-10-11_\u6807\u9898.md"
            text = target.read_text(encoding="utf-8")
            self.assertTrue(text.startswith('---\n\u8d26\u53f7: "\u54c1\u53d4"\n\u5b9a\u7a3f\u65e5\u671f: "2026-10-11"\n'))
            self.assertIn('\u914d\u56fe\u6392\u7248\u8fdb\u5ea6: "\u8be6\u89c1\u914d\u5bf9\u53d1\u5e03\u7269\u6599\u5305\u7684\u914d\u56fe\u6392\u7248\u8fdb\u5ea6"', text)
            self.assertNotIn("EDITOR NOTES", text)
            self.assertNotIn("status: v3", text)
            self.assertEqual(text.count("# \u6807\u9898"), 1)

    def test_ready_needs_all_header_fields(self):
        with tempfile.TemporaryDirectory() as tmp:
            draft = Path(tmp) / "draft.md"; draft.write_text("# T\n\nx\n", encoding="utf-8")
            out = subprocess.run([sys.executable, str(EXPORT), "--source", str(draft), "--ready-dir", tmp],
                                 capture_output=True, text=True)
            self.assertNotEqual(out.returncode, 0)


class SeedScopeEdgeTests(unittest.TestCase):
    SEED = "过去我们看他花了多少时间、读了多少书。这些当然仍然有价值。但也许我们还要看另外一些东西。"

    def flagged(self, text, seed=None):
        return bool(audit_draft.seed_scope_findings(text, seed or self.SEED))

    def test_former_misses_are_flagged(self):
        for text in ["工时已经说明不了什么。", "旧尺子失去了意义。", "现在改看留下了什么。",
                     "旧尺子的作用已经很有限。", "标准从投入工时转到解决问题。", "以后只看结果。",
                     "仅看结果。", "只剩结果说话。", "旧标准可以取代了。", "答案是唯一的。",
                     "工时不值钱了。", "只能退回旧办法。", "以后不看工时。"]:
            self.assertTrue(self.flagged(text), text)

    def test_negated_scope_words_keep_the_meaning(self):
        for text in ["新标准不能替代旧标准。", "旧标准并未过时。", "这并非唯一答案。",
                     "AI 不能代替人的判断。", "不能只看结果。", "这件事只有一个前提。"]:
            self.assertFalse(self.flagged(text), text)

    def test_double_negation_is_flagged(self):
        for text in ["旧标准不是不能替代，只是现在没必要。", "旧标准不是没有过时。", "这并不是不能替代旧标准。"]:
            self.assertTrue(self.flagged(text, "旧标准仍然有效，新标准只是补充，不能替代旧标准。"), text)

    def test_double_negation_cli_returns_2(self):
        with tempfile.TemporaryDirectory() as tmp:
            seed = Path(tmp) / "seed.md"; seed.write_text("旧标准仍然有效，新标准只是补充，不能替代旧标准。", encoding="utf-8")
            card = Path(tmp) / "card.md"; card.write_text("旧标准不是不能替代，只是现在没必要。\n", encoding="utf-8")
            out = subprocess.run([sys.executable, str(SCRIPT), str(card), "--card", "--seed", str(seed)],
                                 capture_output=True, text=True)
            self.assertEqual(out.returncode, 2)

    def test_double_negation_with_long_insert_is_flagged(self):
        seed = "旧标准仍然有效，新标准只是补充，不能替代旧标准。"
        for text in ["旧标准并不是在任何情况下都不能替代。", "旧标准并非在所有情况下都不能替代。"]:
            self.assertTrue(self.flagged(text, seed), text)

    def test_not_only_and_other_words_are_not_outer_negations(self):
        seed = "旧标准仍然有效，新标准只是补充，不能替代旧标准。"
        for text in ["不仅不能替代旧标准，还要继续保留。", "不但不能替代旧标准，还应继续使用。",
                     "不同工具不能替代人的判断。", "这不是重点。不能替代。"]:
            self.assertFalse(self.flagged(text, seed), text)

    def test_same_count_with_opposite_meaning_is_flagged(self):
        self.assertTrue(self.flagged("标准已经转向只看结果。", "旧尺子仍然有效，我们不是转向新标准。"))

    def test_quoted_seed_sentence_is_not_reported(self):
        seed = "最后卡住你的，往往已经不是软件会不会用，而是你到底知不知道什么才是好结果。旧办法不会被取代。"
        findings = audit_draft.seed_scope_findings("作者原话：旧办法不会被取代。判断：旧办法已经失灵。", seed)
        self.assertEqual(len(findings), 1)
        self.assertIn("失灵", findings[0]["detail"])

    def test_cli_exit_code_and_json_count(self):
        with tempfile.TemporaryDirectory() as tmp:
            seed = Path(tmp) / "seed.md"; seed.write_text(self.SEED, encoding="utf-8")
            card = Path(tmp) / "card.md"; card.write_text("第一行\n旧尺子已经失灵。\n", encoding="utf-8")
            out = subprocess.run([sys.executable, str(SCRIPT), str(card), "--card", "--seed", str(seed), "--json"],
                                 capture_output=True, text=True)
            self.assertEqual(out.returncode, 2)
            import json
            report = json.loads(out.stdout)
            self.assertEqual(report["counts"]["seed_flags"], 1)
            self.assertEqual([f["line"] for f in report["findings"] if "seed" in f["rule"]], [2])
            ok = Path(tmp) / "ok.md"; ok.write_text("旧尺子仍然算数，还要再看新的。\n", encoding="utf-8")
            out = subprocess.run([sys.executable, str(SCRIPT), str(ok), "--card", "--seed", str(seed)],
                                 capture_output=True, text=True)
            self.assertEqual(out.returncode, 0)

    def test_shi_fou_question_is_not_a_reversal(self):
        text = CLEAN.replace(FILLER, FILLER + "他问的不是效率，是否值得继续？", 1)
        self.assertNotIn("single-sentence reversal: not X, (it) is Y", rules(run(text)))


class ReadyExportLineEndingTests(unittest.TestCase):
    def export(self, raw: bytes):
        tmp = tempfile.mkdtemp()
        draft = Path(tmp) / "d.md"; draft.write_bytes(raw)
        out = subprocess.run([sys.executable, str(EXPORT), "--source", str(draft), "--ready-dir", str(Path(tmp) / "r"),
                              "--account", "a", "--date", "2026-10-11", "--writer", "m", "--process-dir", tmp,
                              "--approval", "\u5b9a\u7a3f"],
                             capture_output=True, text=True)
        self.assertEqual(out.returncode, 0, out.stderr)
        return next((Path(tmp) / "r" / "a").glob("*.md")).read_bytes()

    def test_crlf_draft_gets_one_header(self):
        data = self.export(b"---\r\nstatus: v3\r\n---\r\n\r\n# T\r\n\r\nbody\r\n\r\n===EDITOR NOTES===\r\nn\r\n")
        self.assertEqual(data.count(b"---"), 2)
        self.assertNotIn(b"status", data)
        self.assertNotIn(b"EDITOR NOTES", data)
        self.assertIn(b"# T\r\n", data)

    def test_bom_draft_gets_one_header(self):
        data = self.export(b"\xef\xbb\xbf---\nx: 1\n---\n\n# T\n\nbody\n")
        self.assertEqual(data.count(b"---"), 2)
        self.assertNotIn(b"x: 1", data)
        self.assertFalse(data.startswith(b"\xef\xbb\xbf"))


class SeedScopeTests(unittest.TestCase):
    SEED = "过去我们看他花了多少时间、读了多少书。这些当然仍然有价值。但也许我们还要看另外一些东西。AI 时代的努力，可能不再只是用了多少时间。"

    def flagged(self, text):
        return [f["rule"] for f in audit_draft.seed_scope_findings(text, self.SEED)]

    def test_faithful_judgment_is_not_flagged(self):
        self.assertEqual(self.flagged("旧尺子仍然算数，但光靠它们量不全了；还要再加一套新的。"), [])
        self.assertEqual(self.flagged("不仅看他花了多少工时，更看他能否解决真问题。"), [])

    def test_seed_phrase_not_only_is_allowed(self):
        self.assertEqual(self.flagged("努力不再只是用了多少时间。"), [])

    def test_no_longer_and_real_thing_are_flagged(self):
        rules = self.flagged("比拼工时已不再构成壁垒，真正的努力在于沉淀。")
        self.assertTrue(any("no longer" in r for r in rules))
        self.assertTrue(any("the real thing is" in r for r in rules))

    def test_turn_and_failed_are_flagged(self):
        self.assertTrue(any("turn from A to B" in r for r in self.flagged("标准正在从耗费工时，转向解决问题。")))
        self.assertTrue(any("has failed" in r for r in self.flagged("旧尺子已经失灵。")))

    def test_cli_seed_option_reports_fix(self):
        with tempfile.TemporaryDirectory() as tmp:
            seed = Path(tmp) / "seed.md"; seed.write_text(self.SEED, encoding="utf-8")
            card = Path(tmp) / "card.md"; card.write_text("旧尺子已经失灵，只看留下了什么。", encoding="utf-8")
            out = subprocess.run([sys.executable, str(SCRIPT), str(card), "--card", "--seed", str(seed)],
                                 capture_output=True, text=True)
            self.assertIn("scope wording not in the seed", out.stdout)


class SeedScopeRound5Tests(unittest.TestCase):
    OLD = "旧标准仍然有效，新标准只是补充，不能替代旧标准。"

    def flagged(self, text, seed=None):
        return bool(audit_draft.seed_scope_findings(text, seed or self.OLD))

    def test_table_cell_quote_is_not_flagged(self):
        seed = "旧标准已经过时。"
        self.assertFalse(self.flagged("| 旧标准已经过时 | 保留原意 |", seed))
        self.assertTrue(self.flagged("| 旧标准已经过时 | 新标准已经过时 |", seed))

    def test_short_author_sentences_are_not_flagged(self):
        for text, seed in [("只看结果。", "只看结果。"), ("唯一标准。", "唯一标准。"), ("不看工时。", "不看工时。")]:
            self.assertFalse(self.flagged(text, seed), text)
        self.assertTrue(self.flagged("只看结果。", "旧标准仍然有效。"))

    def test_modifiers_between_negation_and_scope_word(self):
        for text in ["新标准不能完全替代旧标准。", "没有任何工具能替代旧标准。", "新标准不能无条件替代旧标准。"]:
            self.assertFalse(self.flagged(text), text)
        self.assertTrue(self.flagged("旧标准不是不能完全替代，只是现在没必要。"))

    def test_ordinary_sense_words_are_not_flagged(self):
        for text in ["替代方案有三个。", "唯一标识要保持不变。", "这里只要看清来源就行。",
                     "这项工具已经过时，但旧尺子仍然有效。"]:
            self.assertFalse(self.flagged(text), text)
        self.assertTrue(self.flagged("旧尺子已经过时，新尺子更好。"))

    def test_comma_separated_clauses_do_not_link_negations(self):
        self.assertFalse(self.flagged("这不是工具的问题，AI 不能代替人的判断。"))
        self.assertTrue(self.flagged("旧标准并不是在任何情况下都不能替代。"))

    def test_more_outer_negation_phrasings(self):
        for text in ["谁说旧标准在任何情况下都不能替代。", "不能说旧标准在任何情况下都不能替代。",
                     "很难说旧标准在任何情况下都不能替代。"]:
            self.assertTrue(self.flagged(text), text)


class SourceAndTitleWordTests(unittest.TestCase):
    def run_audit(self, text):
        return audit_draft.audit(text, [], (0, 99999), 99999, 0, 99999, 99, 99999)

    def rules(self, text):
        return [f["rule"] for f in self.run_audit(text)["findings"]]

    def test_current_source_heading_is_cut_without_warning(self):
        text = "# 标题\n\n正文一段。\n\n## 参考文章\n\n- 甲\n- 乙\n- 丙\n"
        report = self.run_audit(text)
        self.assertFalse(any("source section" in f["rule"] for f in report["findings"]))
        self.assertFalse(any("lists more than" in f["rule"] for f in report["findings"]))

    def test_old_source_heading_warns(self):
        findings = self.run_audit("# 标题\n\n正文一段。\n\n## 资料来源\n\n- 甲\n")["findings"]
        hits = [f for f in findings if "source section" in f["rule"]]
        self.assertEqual(len(hits), 1)
        self.assertEqual(hits[0]["level"], "warn")

    def test_too_many_reading_list_entries_warn(self):
        items = "\n".join(f"- 文章{i}" for i in range(6))
        self.assertTrue(any("lists more than" in r for r in self.rules(f"# 标题\n\n正文。\n\n## 参考文章\n\n{items}\n")))

    def test_abstract_words_warn_in_titles_only(self):
        rules = self.rules("# 底层逻辑变了\n\n## 先练判断力\n\n正文里说认知和闭环不报。\n")
        self.assertEqual(sum("abstract word" in r for r in rules), 2)
        self.assertFalse(any("abstract word" in r for r in self.rules("# 标题\n\n## 小节\n\n正文里说认知和闭环。\n")))

    def test_new_warnings_in_json_and_exit_code(self):
        with tempfile.TemporaryDirectory() as tmp:
            art = Path(tmp) / "a.md"
            art.write_text("# 认知升级\n\n正文。\n\n## 资料来源\n\n- 甲\n", encoding="utf-8")
            out = subprocess.run([sys.executable, str(SCRIPT), str(art), "--json"], capture_output=True, text=True)
            report = json.loads(out.stdout)
            warns = [f for f in report["findings"] if f["level"] == "warn" and ("abstract" in f["rule"] or "source section" in f["rule"])]
            self.assertEqual(len(warns), 2)
            self.assertEqual(set(warns[0]), {"level", "rule", "line", "detail"})
            self.assertNotEqual(out.returncode, 2)


class SeedWholeSentenceTests(unittest.TestCase):
    def flagged(self, text, seed):
        return bool(audit_draft.seed_scope_findings(text, seed))

    def test_truncated_seed_sentence_is_flagged(self):
        self.assertTrue(self.flagged("旧标准已经过时。", "旧标准已经过时，但仍然需要保留。"))
        self.assertTrue(self.flagged("以后只看结果。", "作者说以后只看结果是否可靠，还要继续观察。"))

    def test_whole_sentence_copy_still_passes(self):
        self.assertFalse(self.flagged("旧标准已经过时，但仍然需要保留。", "旧标准已经过时，但仍然需要保留。"))
        self.assertFalse(self.flagged("作者说以后只看结果是否可靠，还要继续观察。", "前文。作者说以后只看结果是否可靠，还要继续观察。后文。"))
        self.assertFalse(self.flagged("- 旧标准已经过时，但仍然需要保留。", "旧标准已经过时，但仍然需要保留。"))

    def test_whole_table_cell_copy_passes(self):
        self.assertFalse(self.flagged("| 旧标准已经过时 | x |", "| 旧标准已经过时 | 保留 |"))
        self.assertTrue(self.flagged("| 旧标准已经过时 | x |", "| 旧标准已经过时了吗 | 保留 |"))


if __name__ == "__main__":
    unittest.main()
