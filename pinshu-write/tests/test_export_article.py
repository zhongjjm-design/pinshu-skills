"""Tests for scripts/export_article.py: ready folder layout, byte stability, --check."""
from __future__ import annotations

import contextlib
import importlib.util
import io
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "export_article.py"
SPEC = importlib.util.spec_from_file_location("export_article", SCRIPT)
export_article = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(export_article)

ACCOUNT = "品叔"
DATE = "2026-10-12"
TITLE = "测试标题"
WRITER = "Writer X"
DRAFT = (
    "---\ntitle: old\n---\n\n\n# " + TITLE + "\n\n第一段。\n\n第二段。\n\n"
    "## 参考文章\n\n- 一\n- 二\n\n===EDITOR NOTES===\n\n备注\n"
)


def make_pair(root: Path, draft: str = DRAFT):
    """Export a draft with the script and write a valid paired kit; return (ready_md, kit_md)."""
    source = root / "draft.md"
    source.write_bytes(draft.encode("utf-8"))
    process = root / "process"
    process.mkdir(exist_ok=True)
    with contextlib.redirect_stdout(io.StringIO()):
        md = export_article.ready(source, root / "ready", ACCOUNT, DATE, WRITER, process)
    kit = md.with_name(md.stem + export_article.KIT_SUFFIX)
    (process / "配图任务.json").write_text("{}", encoding="utf-8")
    kit.write_text(f'---\n正文路径: "{md}"\n配图任务路径: "{process / "配图任务.json"}"\n---\n# kit\n', encoding="utf-8")
    return md, kit


class ReadyFolderTests(unittest.TestCase):
    def test_account_folder_added_once(self):
        with tempfile.TemporaryDirectory() as tmp:
            md, _ = make_pair(Path(tmp))
            self.assertEqual(md.parent.name, ACCOUNT)
            self.assertEqual(md.parent.parent.name, "ready")

    def test_account_not_doubled(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            source = root / "d.md"
            source.write_text(DRAFT, encoding="utf-8")
            target = root / "ready" / ACCOUNT
            with contextlib.redirect_stdout(io.StringIO()):
                md = export_article.ready(source, target, ACCOUNT, DATE, WRITER, root)
            self.assertEqual(md.parent, target.resolve())
            self.assertFalse((target / ACCOUNT).exists())

    def test_output_json_shape(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "d.md").write_text(DRAFT, encoding="utf-8")
            out = subprocess.run([sys.executable, str(SCRIPT), "--source", str(root / "d.md"), "--ready-dir", str(root / "r"),
                                  "--account", ACCOUNT, "--date", DATE, "--writer", WRITER, "--process-dir", str(root)],
                                 capture_output=True, text=True, check=True).stdout
            self.assertEqual(set(json.loads(out)), {"ready_md", "article_sha256", "kit_md"})

    def test_bytes_identical_to_previous_behaviour(self):
        with tempfile.TemporaryDirectory() as tmp:
            md, _ = make_pair(Path(tmp))
            process = str((Path(tmp) / "process").resolve())
            expected = (
                f'---\n账号: "{ACCOUNT}"\n定稿日期: "{DATE}"\n写手模型: "{WRITER}"\n过程文件夹: {json.dumps(process, ensure_ascii=False)}\n'
                '配图排版进度: "详见配对发布物料包的配图排版进度"\n---\n\n'
                "# 测试标题\n\n第一段。\n\n第二段。\n\n## 参考文章\n\n- 一\n- 二\n\n"
            )
            self.assertEqual(md.read_bytes(), expected.encode("utf-8"))


class CheckModeTests(unittest.TestCase):
    def test_passes_on_correct_pair(self):
        with tempfile.TemporaryDirectory() as tmp:
            md, _ = make_pair(Path(tmp))
            report = export_article.check(md)
            self.assertTrue(report["ok"], report)
            proc = subprocess.run([sys.executable, str(SCRIPT), "--check", str(md)], capture_output=True, text=True)
            self.assertEqual(proc.returncode, 0)
            self.assertTrue(json.loads(proc.stdout)["ok"])

    def test_fails_on_hand_made_header(self):
        with tempfile.TemporaryDirectory() as tmp:
            md, _ = make_pair(Path(tmp))
            body = md.read_text(encoding="utf-8").split("---\n\n", 1)[1]
            md.write_text("> 账号：品叔\n> 日期：2026-10-12\n\n" + body, encoding="utf-8")
            proc = subprocess.run([sys.executable, str(SCRIPT), "--check", str(md)], capture_output=True, text=True)
            self.assertEqual(proc.returncode, 1)
            self.assertFalse(json.loads(proc.stdout)["ok"])

    def test_wrong_folder_name_and_missing_kit(self):
        with tempfile.TemporaryDirectory() as tmp:
            md, kit = make_pair(Path(tmp))
            kit.unlink()
            problems = " ".join(export_article.check(md)["problems"])
            self.assertIn("kit", problems.lower())
            other = md.parent.parent / "other"
            other.mkdir()
            moved = other / md.name
            moved.write_bytes(md.read_bytes())
            self.assertIn("Parent folder", " ".join(export_article.check(moved)["problems"]))

    def test_kit_path_must_resolve_to_file(self):
        with tempfile.TemporaryDirectory() as tmp:
            md, kit = make_pair(Path(tmp))
            kit.write_text('---\n正文路径: "/somewhere/else.md"\n配图任务路径: "/x/y.json"\n---\n', encoding="utf-8")
            self.assertIn("does not resolve", " ".join(export_article.check(md)["problems"]))

    def test_marker_and_source_section_rules(self):
        with tempfile.TemporaryDirectory() as tmp:
            md, _ = make_pair(Path(tmp))
            text = md.read_text(encoding="utf-8")
            md.write_text(text.replace("## 参考文章", "## 资料来源") + "===编辑备注===\n", encoding="utf-8")
            problems = " ".join(export_article.check(md)["problems"])
            self.assertIn("资料来源", problems)
            self.assertIn("marker", problems)
        with tempfile.TemporaryDirectory() as tmp:
            md, _ = make_pair(Path(tmp), DRAFT.replace("- 二\n", "- 二\n- 三\n- 四\n- 五\n- 六\n"))
            report = export_article.check(md)
            self.assertTrue(report["ok"])  # a long list is a warning, never a failure
            self.assertIn("6 list entries", " ".join(report["warnings"]))

    def test_file_name_must_match_title(self):
        with tempfile.TemporaryDirectory() as tmp:
            md, kit = make_pair(Path(tmp))
            renamed = md.with_name("2026-10-12_别的标题.md")
            md.rename(renamed)
            self.assertIn("File name", " ".join(export_article.check(renamed)["problems"]))


def kit_with_table(md: Path, kit: Path, rows):
    """Rewrite the kit with an image table whose anchor column is the second one."""
    head = kit.read_text(encoding="utf-8").split("\n| 图")[0]
    table = "\n| 图 | 放在哪段后面（段落开头） | 说明 |\n|---|---|---|\n" + "".join(f"| {a} | {b} | x |\n" for a, b in rows)
    kit.write_text(head + table, encoding="utf-8")


class CheckContractTests(unittest.TestCase):
    def problems(self, md, **kw):
        return " ".join(export_article.check(md, **kw)["problems"])

    def test_anchor_must_start_a_paragraph(self):
        with tempfile.TemporaryDirectory() as tmp:
            md, kit = make_pair(Path(tmp))
            kit_with_table(md, kit, [("01 图", "\u201c第一段\u201d"), ("02 图", "第二段。\u2026")])
            self.assertTrue(export_article.check(md)["ok"], export_article.check(md))
            kit_with_table(md, kit, [("01 图", "第一段"), ("02 图", "正文里没有的句子")])
            problems = self.problems(md)
            self.assertIn("02 图", problems)
            self.assertNotIn("01 图", problems)
            kit_with_table(md, kit, [("03 图", "第 一 段")])  # whitespace is normalised
            self.assertTrue(export_article.check(md)["ok"])
            kit_with_table(md, kit, [("04 图", "段。")])  # a substring in the middle is not a paragraph start
            self.assertIn("04 图", self.problems(md))

    def test_source_count_rules(self):
        with tempfile.TemporaryDirectory() as tmp:
            md, _ = make_pair(Path(tmp))  # two entries: as many as the article used, no warning
            report = export_article.check(md)
            self.assertTrue(report["ok"])
            self.assertEqual(report["warnings"], [])
        with tempfile.TemporaryDirectory() as tmp:
            md, _ = make_pair(Path(tmp), DRAFT.replace("- 一\n- 二\n", "- 一\n- 二\n- 三\n"))
            report = export_article.check(md)
            self.assertTrue(report["ok"])
            self.assertEqual(report["warnings"], [])
        with tempfile.TemporaryDirectory() as tmp:
            md, _ = make_pair(Path(tmp), DRAFT.replace("## 参考文章\n\n- 一\n- 二\n\n", ""))
            report = export_article.check(md)
            self.assertTrue(report["ok"])
            self.assertEqual(report["warnings"], [])

    def test_paths_must_exist(self):
        with tempfile.TemporaryDirectory() as tmp:
            md, kit = make_pair(Path(tmp))
            (Path(tmp) / "process" / "配图任务.json").unlink()
            self.assertIn("配图任务路径", self.problems(md))
        with tempfile.TemporaryDirectory() as tmp:
            md, kit = make_pair(Path(tmp))
            (Path(tmp) / "process" / "配图任务.json").unlink()
            (Path(tmp) / "process").rmdir()
            problems = self.problems(md)
            self.assertIn("过程文件夹", problems)

    def test_body_only_skips_the_kit(self):
        with tempfile.TemporaryDirectory() as tmp:
            md, kit = make_pair(Path(tmp))
            kit.unlink()
            self.assertFalse(export_article.check(md)["ok"])
            self.assertTrue(export_article.check(md, body_only=True)["ok"])
            proc = subprocess.run([sys.executable, str(SCRIPT), "--check", str(md), "--body-only"], capture_output=True, text=True)
            self.assertEqual(proc.returncode, 0, proc.stdout)
            # the article's own problems still count
            md.write_text(md.read_text(encoding="utf-8") + "===EDITOR NOTES===\n", encoding="utf-8")
            self.assertFalse(export_article.check(md, body_only=True)["ok"])

    def test_body_only_needs_check(self):
        proc = subprocess.run([sys.executable, str(SCRIPT), "--body-only", "--source", "x"], capture_output=True, text=True)
        self.assertEqual(proc.returncode, 2)


if __name__ == "__main__":
    unittest.main()
