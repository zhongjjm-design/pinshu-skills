"""check_fact_notes.py: a 有出处 line whose note admits a difference is caught across the whole table."""
from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import check_fact_notes as cfn  # noqa: E402

TABLE = """统计在下面。

| # | 原句（段落号） | 内容 | 拆出的点 | 出处 | 状态 | 说明 |
|---|---|---|---|---|---|---|
| 1 | 营业利润掉了一半多（47） | 数字 | 多少 | 年报 | 有出处 | 注：前后口径一为单体一连结 |
| 2 | 会长正垣泰彦降价（21） | 头衔 | 谁 | 官网 | 有出处 | 一样，官网沿革 |
| 3 | 那年下半年（29） | 时间 | 什么时候 | 月报 | 对不上 | 但出处写的是 8 月以后 |
| 4 | 很常见（10） | 程度 | 程度 | 报道 | 有出处 | 大体如此 |
| 5 | 关注度很高（12） | 程度 | 程度 | 报道 | 有出处 | 报道写了关注度很高 |
"""


class CheckFactNotesTests(unittest.TestCase):
    def test_flags_only_sourced_lines_whose_note_admits_a_difference(self):
        flagged = cfn.flagged_lines(TABLE)
        notes = [note for _, _, note in flagged]
        self.assertEqual(len(flagged), 2)
        self.assertIn("注：前后口径一为单体一连结", notes)
        self.assertIn("大体如此", notes)

    def test_no_table_is_reported(self):
        self.assertIsNone(cfn.flagged_lines("只有文字，没有表。"))

    def test_cli_exit_codes(self):
        with tempfile.TemporaryDirectory() as tmp:
            bad = Path(tmp) / "out.md"
            bad.write_text(TABLE, encoding="utf-8")
            self.assertEqual(cfn.main([str(bad)]), 1)
            clean = Path(tmp) / "clean.md"
            clean.write_text(TABLE.split("| 1 |")[0] + "| 2 | 句（1） | 头衔 | 谁 | 官网 | 有出处 | 一样 |\n", encoding="utf-8")
            self.assertEqual(cfn.main([str(clean)]), 0)
            self.assertEqual(cfn.main([str(Path(tmp) / "none.md")]), 2)


if __name__ == "__main__":
    unittest.main()
