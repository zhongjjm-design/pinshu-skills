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
        self.assertEqual((ROOT / "VERSION").read_text().strip(), "0.4.0-rc.1")
        self.assertEqual(
            [p.name for p in sorted((ROOT / "assets" / "chapter").glob("*.png"))],
            [f"{n:02}.png" for n in range(1, 7)],
        )

    def test_public_preview_has_no_internal_or_ranked_template_label(self):
        shell = (ROOT / "assets" / "preview.html").read_text()
        self.assertIn("公开试用版 v0.4.0-rc.1", shell)
        self.assertIn("六款同级可选", shell)
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
            for name in ("青灰手记", "暖纸杂志", "青绿刊页", "橙线手记", "蓝白专题", "首席品牌官经典版"):
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


if __name__ == "__main__":
    unittest.main()
