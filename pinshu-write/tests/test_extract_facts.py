"""extract_facts.py: every checkable sentence lands on the sheet, numbered like the reviewers number paragraphs."""
from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import extract_facts as ef  # noqa: E402

DRAFT = """# 资生堂两年亏了500亿日元

很多人以为大牌不会倒。这句话没有数字。

## 第一节

2024 年它亏了 108 亿日元。社长说"过剩库存是负资产"。CPB 卖 540 元。

三个人里两个这么想。日常描写不算事实。

## 参考文章

- 界面新闻 2024 年 6 月
"""


class ExtractFactsTests(unittest.TestCase):
    def test_flags_numbers_quotes_latin_and_title(self):
        rows = ef.extract(DRAFT)
        sentences = [r["sentence"] for r in rows]
        self.assertEqual(rows[0]["paragraph"], "标题")
        self.assertIn("2024 年它亏了 108 亿日元。", sentences)
        self.assertIn('社长说"过剩库存是负资产"。', sentences)
        self.assertIn("CPB 卖 540 元。", sentences)
        self.assertNotIn("这句话没有数字。", sentences)
        self.assertNotIn("日常描写不算事实。", sentences)

    def test_paragraph_numbers_skip_headings_and_stop_at_references(self):
        rows = ef.extract(DRAFT)
        by_sentence = {r["sentence"]: r["paragraph"] for r in rows}
        self.assertEqual(by_sentence["2024 年它亏了 108 亿日元。"], 2)
        self.assertEqual(by_sentence["三个人里两个这么想。"], 3)
        self.assertFalse(any("界面新闻" in r["sentence"] for r in rows))

    def test_cli_writes_a_sheet_with_empty_source_and_status(self):
        with tempfile.TemporaryDirectory() as tmp:
            draft = Path(tmp) / "draft.md"
            draft.write_text(DRAFT, encoding="utf-8")
            out = Path(tmp) / "sheet.md"
            self.assertEqual(ef.main([str(draft), "--out", str(out)]), 0)
            sheet = out.read_text(encoding="utf-8")
            self.assertIn("| # | 内容类型 | 原句（段落号） | 出处 | 状态 |", sheet)
            self.assertIn("CPB 卖 540 元。（2） |  |  |", sheet)

    def test_colon_quotes_and_rough_counts_are_flagged(self):
        draft = "# 题目\n\n中内功说得更干脆：价格由消费者决定。他常说：先有顾客。成城石井有一百多种奶酪。普通的一句话。\n"
        sentences = [r["sentence"] for r in ef.extract(draft)]
        self.assertIn("中内功说得更干脆：价格由消费者决定。", sentences)
        self.assertIn("他常说：先有顾客。", sentences)
        self.assertIn("成城石井有一百多种奶酪。", sentences)
        self.assertNotIn("普通的一句话。", sentences)

    def test_previous_sheet_marks_new_changed_and_old(self):
        old_draft = "# 题目\n\n2024 年它亏了 108 亿日元。社长说\"过剩库存是负资产\"。\n"
        new_draft = "# 题目\n\n2024 年它亏了 108 亿日元。社长那年说\"过剩库存是负资产\"。CPB 卖 540 元。\n"
        with tempfile.TemporaryDirectory() as tmp:
            old, new = Path(tmp) / "v1.md", Path(tmp) / "v2.md"
            old.write_text(old_draft, encoding="utf-8")
            new.write_text(new_draft, encoding="utf-8")
            sheet1, sheet2 = Path(tmp) / "s1.md", Path(tmp) / "s2.md"
            self.assertEqual(ef.main([str(old), "--out", str(sheet1)]), 0)
            self.assertEqual(ef.main([str(new), "--previous", str(sheet1), "--out", str(sheet2)]), 0)
            sheet = sheet2.read_text(encoding="utf-8")
        self.assertIn("2024 年它亏了 108 亿日元。（1） |  |  | 旧 |", sheet)
        self.assertIn('社长那年说"过剩库存是负资产"。（1） |  |  | 改 |', sheet)
        self.assertIn("CPB 卖 540 元。（1） |  |  | 新 |", sheet)
        self.assertIn("新 1 / 改 1 / 旧 1。", sheet)

    def test_previous_sentences_follow_the_header_of_any_sheet(self):
        merged = "| 内容 | 原句（段落号）| 出处 | 状态 |\n|---|---|---|---|\n| 收入 | 2024 年收入 100 亿元。（3） | 年报 | 有出处 |\n"
        checker = "| # | 原句（段落号） | 内容 | 拆出的点 | 出处 | 状态 | 说明 |\n|---|---|---|---|---|---|---|\n| 1 | 2024 年收入 100 亿元。（3） | 数字 | 多少 | 年报 | 有出处 | 一样 |\n"
        for sheet in (merged, checker):
            self.assertEqual(ef.previous_sentences(sheet), ["2024 年收入 100 亿元。"])

    def test_missing_previous_sheet_is_an_error(self):
        with tempfile.TemporaryDirectory() as tmp:
            draft = Path(tmp) / "draft.md"
            draft.write_text(DRAFT, encoding="utf-8")
            self.assertEqual(ef.main([str(draft), "--previous", str(Path(tmp) / "none.md")]), 2)

    def test_missing_file_is_an_error(self):
        self.assertEqual(ef.main(["/nonexistent/draft.md"]), 2)


if __name__ == "__main__":
    unittest.main()
