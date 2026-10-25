from __future__ import annotations

import hashlib
import json
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
sys.path.insert(0, str(SCRIPTS))

import importlib.util

spec = importlib.util.spec_from_file_location("pinshu_wechat_build", SCRIPTS / "build.py")
assert spec and spec.loader
build = importlib.util.module_from_spec(spec)
spec.loader.exec_module(build)


# A real, decodable 1 x 1 PNG. The renderer embeds bytes; it does not resize it.
PNG = bytes.fromhex(
    "89504e470d0a1a0a0000000d49484452000000010000000108060000001f15c489"
    "0000000d49444154789c6360f8cff000000401010089990d1d0000000049454e44ae426082"
)


class WeChatLayoutReleaseTests(unittest.TestCase):
    def fixture(self, folder: Path, emphasis: list[str] | None = None) -> tuple[Path, Path, bytes]:
        article = folder / "article.md"
        article_bytes = (
            "---\n账号: \"测试账号\"\n定稿日期: \"2026-10-12\"\n写手模型: \"test\"\n"
            "过程文件夹: \"/portable/example\"\n配图排版进度: \"详见配对发布物料包的配图排版进度\"\n---\n\n"
            "# 测试文章\n\n开头原文，不得改写。\n\n## 第一章\n\n这里是作者选定的关键判断。\n\n"
            "参考文章\n\n- 《测试文章》，测试作者，测试平台，2026 年 10 月 12 日\n"
        ).encode()
        article.write_bytes(article_bytes)
        for name in ("hero.png", "body.png"):
            (folder / name).write_bytes(PNG)
        manifest = {
            "article": str(article),
            "article_sha256": hashlib.sha256(article_bytes).hexdigest(),
            "files": [
                {"filename": name, "sha256": hashlib.sha256(PNG).hexdigest()}
                for name in ("hero.png", "body.png")
            ],
        }
        (folder / "images.json").write_text(json.dumps(manifest, ensure_ascii=False), encoding="utf-8")
        handoff = {
            "source_md": str(article),
            "image_manifest": "images.json",
            "cover_landscape": "hero.png",
            "body_images": [
                {
                    "filename": "body.png",
                    "after_prefix": "开头原文",
                    "caption": "截图来源：测试",
                    "source_url": "https://example.invalid/source",
                    "frame_baked": False,
                }
            ],
            "author": "测试作者",
            "digest": "测试摘要",
            "emphasis": emphasis if emphasis is not None else ["这里是作者选定的关键判断"],
        }
        handoff_path = folder / "handoff.json"
        handoff_path.write_text(json.dumps(handoff, ensure_ascii=False), encoding="utf-8")
        return handoff_path, article, article_bytes

    def test_package_version_and_six_authorized_chapter_images(self):
        self.assertEqual((ROOT / "VERSION").read_text().strip(), "0.4.0-rc.3")
        self.assertEqual(
            [p.name for p in sorted((ROOT / "assets" / "chapter").glob("*.png"))],
            [f"{n:02}.png" for n in range(1, 7)],
        )

    def test_public_preview_has_no_internal_or_ranked_template_label(self):
        shell = (ROOT / "assets" / "preview.html").read_text()
        self.assertIn("公开试用版 v0.4.0-rc.3", shell)
        self.assertIn("七款同级可选", shell)
        for forbidden in ("内部试用", "已认可方向", "候选版式", "参考版式"):
            self.assertNotIn(forbidden, shell)

    def test_lead_and_body_figures_share_template_frame(self):
        renderer = (ROOT / "assets" / "renderer.js").read_text()
        self.assertIn("${framing?styles[t.figure]", renderer)
        self.assertNotIn("framing&&!hero", renderer)
        self.assertIn("border:1px solid", renderer)

    def test_reference_appendix_and_emphasis_contracts_are_present(self):
        reading = (ROOT / "assets" / "reading-base.js").read_text()
        renderer = (ROOT / "assets" / "renderer.js").read_text()
        self.assertIn("fontStyle:'italic'", reading)
        self.assertIn("sourceFont:'Georgia", reading)
        self.assertIn("border-bottom:1px solid", renderer)
        self.assertIn("data-emphasis", renderer)

    def test_real_build_preserves_input_and_reports_equal_status_templates(self):
        with tempfile.TemporaryDirectory() as td:
            folder = Path(td)
            handoff, article, before = self.fixture(folder)
            preview = build.run(handoff, folder / "out")
            self.assertTrue(preview.is_file())
            self.assertEqual(article.read_bytes(), before)
            page = preview.read_text()
            for name in ("松绿双线", "青灰手记", "暖纸杂志", "橙线手记", "蓝白专题", "首席品牌官经典版"):
                self.assertIn(name, page)
            source_html = (folder / "out" / "source.html").read_text()
            self.assertIn('data-hero="true"', source_html)
            self.assertIn('data-caption="截图来源：测试"', source_html)
            report = json.loads((folder / "out" / "试排记录.json").read_text())
            self.assertEqual(report["default_template"], "青灰手记")
            self.assertEqual(report["template_selection_status"], "pending-per-article")
            self.assertNotIn("approved_template", report)
            self.assertTrue(report["source_text_blocks_preserved"])
            build_record = json.loads(preview.with_suffix(".build.json").read_text())
            self.assertNotIn("approved_template", build_record)
            self.assertEqual(build_record["template_selection_status"], "pending-per-article")

    def test_more_than_three_emphasis_phrases_is_rejected(self):
        with tempfile.TemporaryDirectory() as td:
            folder = Path(td)
            handoff, _, _ = self.fixture(folder, ["一", "二", "三", "四"])
            with self.assertRaisesRegex(ValueError, "At most three emphasis"):
                build.run(handoff, folder / "out")

    def test_reference_h2_is_not_a_chapter_in_either_form(self):
        """LAYOUT-01: 1.3 drafts send `## 参考文章`; older ones a plain paragraph. Neither is a numbered chapter."""
        for heading in ("## 参考文章", "## 资料来源", "## 参考资料", "参考文章"):
            with self.subTest(heading=heading), tempfile.TemporaryDirectory() as td:
                folder = Path(td)
                handoff, article, _ = self.fixture(folder)
                text = article.read_text(encoding="utf-8").replace("参考文章\n", heading + "\n")
                article.write_text(text, encoding="utf-8")
                data = json.loads((folder / "images.json").read_text(encoding="utf-8"))
                data["article_sha256"] = hashlib.sha256(article.read_bytes()).hexdigest()
                (folder / "images.json").write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")
                build.run(handoff, folder / "out")
                report = json.loads((folder / "out" / "试排记录.json").read_text(encoding="utf-8"))
                self.assertEqual(report["chapter_count"], 1)
        renderer = (ROOT / "assets" / "renderer.js").read_text(encoding="utf-8")
        self.assertIn("参考文章", renderer)

    def test_windows_drive_path_is_a_local_image_not_a_url(self):
        """Colleague's Windows run 2026-10-13: E:\\... was read as URL scheme "e" and every image failed."""
        code = (SCRIPTS / "engine.py").read_text(encoding="utf-8")
        self.assertIn("[A-Za-z]:", code)
        import re as _re
        pattern = _re.search(r"re\.match\(r'(.+?)', src\)", code).group(1)
        for path in ("E:\\写作坊\\drafts\\a.png", "C:/fixtures/b.png"):
            self.assertIsNotNone(_re.match(pattern, path))
        for url in ("https://a.b/c.png", "file:///tmp/c.png", "relative/c.png"):
            self.assertIsNone(_re.match(pattern, url))


    def test_table_and_prompt_card_build_and_columns_are_capped(self):
        """2026-10-15: tables (2-4 columns) and 【…提示词…】 blockquotes are layout blocks, not errors."""
        def run_with(extra: str):
            td = tempfile.TemporaryDirectory()
            folder = Path(td.name)
            handoff, article, _ = self.fixture(folder)
            text = article.read_text(encoding="utf-8").replace("参考文章\n", extra + "\n参考文章\n", 1)
            article.write_text(text, encoding="utf-8")
            data = json.loads((folder / "images.json").read_text(encoding="utf-8"))
            data["article_sha256"] = hashlib.sha256(article.read_bytes()).hexdigest()
            (folder / "images.json").write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")
            return td, folder, handoff
        good = "\n\n| 时间 | 配音 | 画面 |\n| :--- | :--- | :--- |\n| 00.000 - 02.400 | 一句（音效） | 动作 |\n\n> 【测试提示词模板（可复制）】\n> 角色设定：你是导演。\n> 阶段规划：\n> - 第一段\n> 动效参数：慢。\n\n"
        td, folder, handoff = run_with(good)
        with td:
            build.run(handoff, folder / "out")
            page = (folder / "out" / "公众号图文排版预览.html").read_text(encoding="utf-8")
            renderer = (ROOT / "assets" / "renderer.js").read_text(encoding="utf-8")
            self.assertIn("<table>", (folder / "out" / "source.html").read_text(encoding="utf-8"))
            self.assertIn("function promptCard", page)
            self.assertIn("[22,38,40]", renderer.replace(" ", ""))
            self.assertNotIn("font-weight:600", renderer[renderer.index("function promptCard"):renderer.index("function chapter")])
        wide = "\n\n| a | b | c | d | e |\n| - | - | - | - | - |\n| 1 | 2 | 3 | 4 | 5 |\n\n"
        td, folder, handoff = run_with(wide)
        with td:
            with self.assertRaisesRegex(ValueError, "2 to 4 columns"):
                build.run(handoff, folder / "out")


    def _build_with(self, extra: str, handoff_extra: dict | None = None):
        td = tempfile.TemporaryDirectory()
        folder = Path(td.name)
        handoff, article, _ = self.fixture(folder)
        text = article.read_text(encoding="utf-8").replace("参考文章\n", extra + "\n参考文章\n", 1)
        article.write_text(text, encoding="utf-8")
        data = json.loads((folder / "images.json").read_text(encoding="utf-8"))
        data["article_sha256"] = hashlib.sha256(article.read_bytes()).hexdigest()
        (folder / "images.json").write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")
        if handoff_extra:
            h = json.loads(handoff.read_text(encoding="utf-8"))
            h.update(handoff_extra)
            handoff.write_text(json.dumps(h, ensure_ascii=False), encoding="utf-8")
        return td, folder, handoff

    def test_content_that_would_be_lost_is_refused_not_dropped(self):
        """2026-10-15 independent review: cells beyond the header, links in tables/cards and nested quotes were silently lost."""
        cases = {
            "Table row has 3 cells": "\n\n| a | b |\n| - | - |\n| 1 | 2 | 3 |\n\n",
            "Links inside a table": "\n\n| a | b |\n| - | - |\n| [x](http://u.example) | 2 |\n\n",
            "Links inside a prompt card": "\n\n> 【卡片】\n> 正文 [x](http://u.example)\n\n",
            "only supports paragraphs and lists": "\n\n> 【卡片】\n> > 嵌套引用\n\n",
        }
        for message, extra in cases.items():
            with self.subTest(message=message):
                td, folder, handoff = self._build_with(extra)
                with td, self.assertRaisesRegex(ValueError, message):
                    build.run(handoff, folder / "out")

    def test_heading_split_accepts_good_input_and_explains_bad_input(self):
        good = {"heading_split": {"第一章": ["第一", "章"]}}
        td, folder, handoff = self._build_with("", good)
        with td:
            build.run(handoff, folder / "out")
            layout = json.loads((folder / "out" / "layout.json").read_text(encoding="utf-8"))
            self.assertEqual(layout["headingSplit"], {"第一章": ["第一", "章"]})
        bad = {
            "not an H2 heading": {"heading_split": {"不存在的章": ["不", "存在的章"]}},
            "must be an object": {"heading_split": ["第一章"]},
            "two non-empty strings": {"heading_split": {"第一章": [1, 2]}},
            "must satisfy big": {"heading_split": {"第一章": ["第", "二章"]}},
        }
        for message, extra in bad.items():
            with self.subTest(message=message):
                td, folder, handoff = self._build_with("", extra)
                with td, self.assertRaisesRegex(ValueError, message):
                    build.run(handoff, folder / "out")

    def test_split_heading_has_no_layout_cells_for_video_to_enter(self):
        """A real WeChat replacement put a video into the next flex heading's number cell."""
        reading = (ROOT / "assets" / "reading-base.js").read_text(encoding="utf-8")
        start = reading.index("if(style==='split')")
        end = reading.index("if(style==='blue')", start)
        split = reading[start:end]
        self.assertNotIn("display:'flex'", split)
        self.assertNotIn("display:'grid'", split)
        self.assertNotIn("createElement('table')", split)
        self.assertNotIn("position:'relative'", split)
        self.assertNotIn("position:'absolute'", split)
        self.assertIn("display:'inline-block'", split)
        self.assertIn("borderRight:'1px solid #dfe1e4'", split)
        self.assertIn("whiteSpace:'nowrap'", split)
        self.assertIn("wordBreak:'keep-all'", split)
        self.assertIn("overflowWrap:'normal'", split)
        self.assertIn("width:'22%'", split)  # 2026-10-15: 22/78 after 25/75 left a visible gap before the rule; 22% is the floor for "01" on a 320px phone
        self.assertIn("width:'78%'", split)
        self.assertIn("padding:'0 12px 0 0'", split)
        self.assertIn("title.append(numberSpan,titleText)", split)


if __name__ == "__main__":
    unittest.main()
