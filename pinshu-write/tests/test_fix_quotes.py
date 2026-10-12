"""Tests for scripts/fix_quotes.py."""
from __future__ import annotations

import importlib.util
import tempfile
import unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "fix_quotes.py"
SPEC = importlib.util.spec_from_file_location("fix_quotes", SCRIPT)
fix_quotes = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(fix_quotes)


class FixQuotesTests(unittest.TestCase):
    def test_alternates_open_close(self):
        new, changes, warnings = fix_quotes.fix('他说"甲"和"乙"都对。\n')
        self.assertEqual(new, "他说“甲”和“乙”都对。\n")
        self.assertEqual(len(changes), 1)
        self.assertEqual(warnings, [])

    def test_restarts_each_paragraph(self):
        new, _, warnings = fix_quotes.fix('这是"一段\n\n另一段"结束"。\n')
        self.assertEqual(new, "这是“一段\n\n另一段“结束”。\n")
        self.assertEqual(len(warnings), 1)

    def test_skips_code_url_yaml_and_html(self):
        text = ('---\n账号: "品叔"\n---\n\n正文`print("x")`和"引用"，见"https://a.com/p"与<a href="u">链</a>。\n\n'
                '```\n中文 "代码"\n```\n\nPlain English "quote" only\n')
        new, _, _ = fix_quotes.fix(text)
        self.assertIn('账号: "品叔"', new)
        self.assertIn('`print("x")`', new)
        self.assertIn("“引用”", new)
        self.assertIn("“https://a.com/p”", new)
        self.assertIn('<a href="u">', new)
        self.assertIn('中文 "代码"', new)
        self.assertIn('Plain English "quote" only', new)

    def test_untouched_bytes_and_crlf(self):
        text = "无引号\r\n第二行\r\n"
        new, changes, _ = fix_quotes.fix(text)
        self.assertEqual(new, text)
        self.assertEqual(changes, [])
        new, _, _ = fix_quotes.fix('中文"好"\r\n')
        self.assertEqual(new, "中文“好”\r\n")

    def test_cli_default_does_not_write_and_write_does(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "a.md"
            path.write_text('他说"好"。\n', encoding="utf-8")
            self.assertEqual(fix_quotes.main([str(path)]), 0)
            self.assertEqual(path.read_text(encoding="utf-8"), '他说"好"。\n')
            self.assertEqual(fix_quotes.main([str(path), "--write"]), 0)
            self.assertEqual(path.read_text(encoding="utf-8"), "他说“好”。\n")


if __name__ == "__main__":
    unittest.main()
