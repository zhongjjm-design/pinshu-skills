"""Tests for scripts/export_article.py: ready folder layout, byte stability, --check."""
from __future__ import annotations

import contextlib
import importlib.util
import io
import json
import shutil
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
APPROVAL = "这版定稿，可以进待发"
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
        md = export_article.ready(source, root / "ready", ACCOUNT, DATE, WRITER, process, approval=APPROVAL)
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
                md = export_article.ready(source, target, ACCOUNT, DATE, WRITER, root, approval=APPROVAL)
            self.assertEqual(md.parent, target.resolve())
            self.assertFalse((target / ACCOUNT).exists())

    def test_output_json_shape(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "d.md").write_text(DRAFT, encoding="utf-8")
            out = subprocess.run([sys.executable, str(SCRIPT), "--source", str(root / "d.md"), "--ready-dir", str(root / "r"),
                                  "--account", ACCOUNT, "--date", DATE, "--writer", WRITER, "--process-dir", str(root),
                                  "--approval", APPROVAL],
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

    def test_video_table_anchors_are_checked_too(self):
        """1.4: a second table (videos) after the image table is checked as well; a table
        without the anchor column in between is skipped."""
        with tempfile.TemporaryDirectory() as tmp:
            md, kit = make_pair(Path(tmp))
            kit_with_table(md, kit, [("01 图", "第一段")])
            base = kit.read_text(encoding="utf-8")
            other = "\n## 其他\n\n| 平台 | 转发语 |\n|---|---|\n| 微博 | 第二段之外的话 |\n"
            videos = "\n## 视频\n\n| 视频 | 放在哪段后面（段落开头） | 原始链接 |\n|---|---|---|\n| V1 Min Choi 原片 | {} | https://x.com/a |\n"
            kit.write_text(base + other + videos.format("第二段"), encoding="utf-8")
            self.assertTrue(export_article.check(md)["ok"], export_article.check(md))
            kit.write_text(base + other + videos.format("正文里没有的段落"), encoding="utf-8")
            problems = self.problems(md)
            self.assertIn("V1 Min Choi 原片", problems)
            self.assertNotIn("微博", problems)

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
            shutil.rmtree(Path(tmp) / "process")
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


class FinalApprovalGateTests(unittest.TestCase):
    """Meeting 2026-10-12: only the author's 定稿 puts an article in the ready folder; 可以/继续/还行 do not."""

    def cli(self, root: Path, *extra):
        source = root / "d.md"
        if not source.exists():
            source.write_text(DRAFT, encoding="utf-8")
        (root / "p").mkdir(exist_ok=True)
        return subprocess.run([sys.executable, str(SCRIPT), "--source", str(source), "--ready-dir", str(root / "r"),
                               "--account", ACCOUNT, "--date", DATE, "--writer", WRITER, "--process-dir", str(root / "p"), *extra],
                              capture_output=True, text=True)

    def test_casual_go_ahead_words_are_refused(self):
        for words in (None, "可以", "继续", "还行", "挺满意的，继续"):
            with self.subTest(words=words), tempfile.TemporaryDirectory() as tmp:
                root = Path(tmp)
                out = self.cli(root, *(["--approval", words] if words else []))
                self.assertEqual(out.returncode, 1, out.stdout)
                self.assertIn("refused", out.stderr)
                self.assertFalse((root / "r").exists())
                self.assertFalse((root / "p" / export_article.APPROVAL_LOG).exists())

    def test_negated_or_questioning_dinggao_is_refused(self):
        for words in ("先别定稿", "还没定稿", "这版能定稿吗", "不算定稿",
                      "不是定稿", "是否定稿", "等改完再定稿", "请不要直接定稿", "如果没问题就定稿", "待定稿"):
            with self.subTest(words=words):
                self.assertIsNotNone(export_article.approval_problem(words))

    def test_plain_dinggao_sentences_pass(self):
        for words in ("定稿", "这版定稿，可以进待发", "改完这版定稿", "可以，定稿"):
            with self.subTest(words=words):
                self.assertIsNone(export_article.approval_problem(words))

    def test_dinggao_exports_and_logs_the_exact_file(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            out = self.cli(root, "--approval", "定稿")
            self.assertEqual(out.returncode, 0, out.stderr)
            info = json.loads(out.stdout)
            log = [json.loads(l) for l in (root / "p" / export_article.APPROVAL_LOG).read_text(encoding="utf-8").splitlines()]
            self.assertEqual(len(log), 1)
            self.assertEqual(log[0]["approval"], "定稿")
            self.assertEqual(log[0]["article_sha256"], info["article_sha256"])
            md = Path(info["ready_md"])
            self.assertTrue(export_article.approval_recorded(root / "p", md.resolve(), info["article_sha256"]))

    def test_trial_export_still_works_without_approval(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "d.md").write_text(DRAFT, encoding="utf-8")
            out = subprocess.run([sys.executable, str(SCRIPT), "--source", str(root / "d.md"), "--output-dir", str(root / "trial")],
                                 capture_output=True, text=True)
            self.assertEqual(out.returncode, 0, out.stderr)
            record = json.loads((root / "trial" / "正文导出记录.json").read_text(encoding="utf-8"))
            self.assertIn("导出不代表定稿", record["article_state"])

    def test_different_ready_copy_is_never_silently_overwritten(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.assertEqual(self.cli(root, "--approval", "定稿").returncode, 0)
            target = next((root / "r" / ACCOUNT).glob("*.md"))
            first = target.read_bytes()
            (root / "d.md").write_text(DRAFT.replace("第一段。", "第一段改过。"), encoding="utf-8")
            out = self.cli(root, "--approval", "定稿")
            self.assertEqual(out.returncode, 1)
            self.assertIn("--replace", out.stderr)
            self.assertEqual(target.read_bytes(), first)
            out = self.cli(root, "--approval", "改完这版定稿", "--replace")
            self.assertEqual(out.returncode, 0, out.stderr)
            kept = list((root / "p" / export_article.REPLACED_DIR).glob("*.md"))
            self.assertEqual(len(kept), 1)
            self.assertEqual(kept[0].read_bytes(), first)
            self.assertIn("第一段改过。", target.read_text(encoding="utf-8"))
            entries = (root / "p" / export_article.APPROVAL_LOG).read_text(encoding="utf-8").splitlines()
            self.assertEqual(len(entries), 2)
            self.assertEqual(json.loads(entries[1])["replaced_copy_kept_at"], str(kept[0].resolve()))

    def test_same_bytes_re_export_needs_no_replace(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.assertEqual(self.cli(root, "--approval", "定稿").returncode, 0)
            self.assertEqual(self.cli(root, "--approval", "定稿").returncode, 0)
            self.assertFalse((root / "p" / export_article.REPLACED_DIR).exists())

    def test_check_warns_when_no_approval_record(self):
        with tempfile.TemporaryDirectory() as tmp:
            md, _ = make_pair(Path(tmp))
            self.assertTrue(export_article.check(md)["ok"])
            self.assertFalse(any("定稿确认记录" in w for w in export_article.check(md)["warnings"]))
            (Path(tmp) / "process" / export_article.APPROVAL_LOG).unlink()
            report = export_article.check(md)
            self.assertTrue(report["ok"])
            self.assertTrue(any("定稿确认记录" in w for w in report["warnings"]))


class ReviewFixes14Tests(unittest.TestCase):
    """Independent review of 1.4.0 (Codex, 2026-10-12)."""

    def test_running_export_lock_refuses_a_second_export(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "d.md").write_text(DRAFT, encoding="utf-8"); (root / "p").mkdir()
            target_dir = root / "r" / ACCOUNT; target_dir.mkdir(parents=True)
            lock = target_dir / f".{DATE}_{TITLE}.md.exporting"
            lock.write_text("", encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "Another export"):
                export_article.ready(root / "d.md", root / "r", ACCOUNT, DATE, WRITER, root / "p", approval="定稿")
            self.assertFalse((target_dir / f"{DATE}_{TITLE}.md").exists())
            lock.unlink()
            with contextlib.redirect_stdout(io.StringIO()):
                md = export_article.ready(root / "d.md", root / "r", ACCOUNT, DATE, WRITER, root / "p", approval="定稿")
            self.assertTrue(md.is_file())
            self.assertFalse(lock.exists())

    def test_kit_row_without_anchor_cell_is_reported(self):
        with tempfile.TemporaryDirectory() as tmp:
            md, kit = make_pair(Path(tmp))
            kit_with_table(md, kit, [("01 图", "第一段")])
            kit.write_text(kit.read_text(encoding="utf-8") + "\n| 视频 | 放在哪段后面（段落开头） |\n|---|---|\n| V1 |\n", encoding="utf-8")
            self.assertIn("V1", " ".join(export_article.check(md)["problems"]))


if __name__ == "__main__":
    unittest.main()
