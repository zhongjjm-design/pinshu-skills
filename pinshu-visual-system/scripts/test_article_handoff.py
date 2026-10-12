"""Regression for source identity and the real installed layout consumer."""
import copy
import hashlib
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest

from PIL import Image

from prepare_article_handoff import prepare, load_layout, export_capture_requests
from frame_screenshot import frame

SKILLS = Path(__file__).resolve().parents[2]
LAYOUT = SKILLS / "pinshu-wechat-layout"


_WRITER_EXPORT=Path(__file__).resolve().parents[2]/'pinshu-write/scripts/export_article.py'
_NEEDS_WRITER=unittest.skipUnless(_WRITER_EXPORT.exists(),'SKIP: needs pinshu-write scripts/export_article.py (trial mode only)')

class ArticleHandoffTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.source = self.root / "source.md"
        self.source.write_text("# 测试文章\n\n第一段说明。\n\n第二段说明。\n\n第三段说明。\n", encoding="utf-8")
        self.image = self.root / "source.png"
        Image.new("RGB", (80, 40), "navy").save(self.image)
        self.asset = {"role": "body", "asset_kind": "real-photo", "file": str(self.image),
                      "purpose": "合成夹具测试；不是实拍验收", "original_file": str(self.image),
                      "attribution": "测试夹具", "after_prefix": "第一段", "caption": ""}
        self.plan = {"source_md": str(self.source),
                     "article_sha256": self.sha(self.source), "assets": [self.asset]}

    @staticmethod
    def sha(path):
        return hashlib.sha256(path.read_bytes()).hexdigest()

    def run_plan(self, plan=None):
        path = self.root / "plan.json"
        path.write_text(json.dumps(plan or self.plan, ensure_ascii=False), encoding="utf-8")
        return prepare(path, self.root / "prepared", LAYOUT)

    def test_real_consumer_and_source_preservation(self):
        before = self.source.read_bytes(), self.image.read_bytes()
        handoff = self.run_plan()
        layout = load_layout(LAYOUT)
        preview = layout.run(handoff, self.root / "layout")
        self.assertTrue(preview.is_file())
        self.assertEqual(before, (self.source.read_bytes(), self.image.read_bytes()))
        self.assertIn('data-caption=""', (preview.parent / "source.html").read_text())

    def test_layout_choices_survive_visual_handoff(self):
        self.plan.update(emphasis=["第一段说明"], lead_image=False)
        handoff = json.loads(self.run_plan().read_text())
        self.assertEqual(handoff["emphasis"], ["第一段说明"])
        self.assertIs(handoff["lead_image"], False)

    def test_stale_source_stops_before_output(self):
        self.source.write_text(self.source.read_text()+"改稿了。", encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "Source changed"):
            self.run_plan()
        self.assertFalse((self.root / "prepared").exists())

    def test_duplicate_paragraph_and_ambiguous_prefix(self):
        second = copy.deepcopy(self.asset)
        second["filename"] = "second.png"
        self.plan["assets"].append(second)
        with self.assertRaisesRegex(ValueError, "one image per paragraph"):
            self.run_plan()
        self.plan["assets"] = [self.asset]
        self.asset["after_prefix"] = "第"
        with self.assertRaisesRegex(ValueError, "one paragraph"):
            self.run_plan()

    def test_path_escape_and_nonboolean_frame(self):
        self.asset["filename"] = "../escape.png"
        with self.assertRaisesRegex(ValueError, "nonlocal"):
            self.run_plan()
        self.asset.pop("filename")
        self.asset["frame_baked"] = "false"
        with self.assertRaisesRegex(ValueError, "Boolean"):
            self.run_plan()

    def test_screenshot_origin_and_source_url(self):
        self.asset.update(asset_kind="evidence-screenshot", acquisition="reused", source_url="javascript:alert(1)", captured_at="2026-10-10")
        with self.assertRaisesRegex(ValueError, "HTTP"):
            self.run_plan()
        self.asset["source_url"] = "https://example.com/post"
        self.asset.pop("captured_at")
        with self.assertRaisesRegex(ValueError, "capture date"):
            self.run_plan()

    def test_unframed_screenshot_default_reaches_actual_layout(self):
        self.asset.update(asset_kind="evidence-screenshot", acquisition="reused", source_url="https://example.com/post",
                          captured_at="2026-10-10")
        self.assertNotIn("frame_baked", self.asset)
        handoff = self.run_plan()
        data = json.loads(handoff.read_text())
        manifest = json.loads((handoff.parent / "配图清单.json").read_text())
        self.assertIs(data["body_images"][0]["frame_baked"], False)
        self.assertIs(manifest["files"][0]["frame_baked"], False)
        preview = load_layout(LAYOUT).run(handoff, self.root / "layout")
        self.assertTrue(preview.is_file())

    def test_missing_acquisition_with_frame_rejected(self):
        self.asset.update(asset_kind="evidence-screenshot", frame_baked=True)
        with self.assertRaisesRegex(ValueError, "explicitly"):
            self.run_plan()

    def test_unknown_acquisition_with_frame_rejected(self):
        self.asset.update(asset_kind="evidence-screenshot", acquisition="unknown", frame_baked=True)
        with self.assertRaisesRegex(ValueError, "unframed"):
            self.run_plan()

    def test_framed_reused_requires_bound_old_receipt(self):
        self.asset.update(asset_kind="evidence-screenshot", acquisition="reused", frame_baked=True,
                          source_url="https://example.com/post", captured_at="2026-10-09")
        with self.assertRaisesRegex(ValueError, "hash-bound"):
            self.run_plan()
        self.asset["capture_receipt"] = {"captured_at":"2026-10-09", "delivery_sha256":self.sha(self.image)}
        data = json.loads(self.run_plan().read_text())
        self.assertIs(data["body_images"][0]["frame_baked"], True)

    def capture_plan(self):
        self.asset.update(asset_kind="evidence-screenshot", acquisition="reused", source_url="https://example.com/post",
                          filename="03-原帖原话.png", capture_region="原帖卡片；从‘开头原话’到‘结尾原话’，含作者",
                          after_paragraph="第一段说明。", review_state="capture-pending")
        self.asset.pop("file")
        path = self.root / "plan.json"
        path.write_text(json.dumps(self.plan, ensure_ascii=False))
        return path

    def test_capture_requests_without_browser_images_or_layout_dependencies(self):
        from unittest.mock import patch
        path = self.capture_plan()
        with patch("prepare_article_handoff.load_layout", side_effect=AssertionError("must not load layout")):
            result = export_capture_requests(path, self.root / "capture")
        data = json.loads((result.parent / "待截图清单.json").read_text())
        item = data["requests"][0]
        self.assertIs(item["frame_baked"], False)
        self.assertEqual(item["after_paragraph"], "第一段说明。")
        self.assertEqual(item["review_state"], "capture-pending")
        self.assertNotIn("captured_at", item)
        self.assertNotIn("file", item)
        self.assertFalse((result.parent / "排版交接.json").exists())
        self.assertIn("原帖卡片", result.read_text())

    def test_capture_requests_reject_wrong_anchor_and_stale_article(self):
        path = self.capture_plan()
        self.plan["assets"][0]["after_paragraph"] = "不存在的段落"
        path.write_text(json.dumps(self.plan, ensure_ascii=False))
        with self.assertRaisesRegex(ValueError, "after_paragraph"):
            export_capture_requests(path, self.root / "capture")
        self.assertFalse((self.root / "capture").exists())
        self.source.write_text(self.source.read_text() + "改稿。")
        with self.assertRaisesRegex(ValueError, "Source changed"):
            export_capture_requests(path, self.root / "capture")

    def test_changed_delivered_image_is_rejected_by_layout(self):
        handoff = self.run_plan()
        Image.new("RGB", (80, 40), "red").save(handoff.parent / self.image.name)
        with self.assertRaisesRegex(ValueError, "Image differs"):
            load_layout(LAYOUT).run(handoff, self.root / "layout")

    @_NEEDS_WRITER

    def test_editor_notes_export_is_exact_and_layout_stops(self):
        draft = b'# Title\r\n\r\nBody.\r\n\r\nSources.\r\n===EDITOR NOTES===\r\nPrivate notes.\r\n'
        self.source.write_bytes(draft)
        with self.assertRaisesRegex(ValueError, "Editor notes"):
            load_layout(LAYOUT).parse_markdown(self.source)
        spec = importlib.util.spec_from_file_location("article_export", SKILLS / "pinshu-write/scripts/export_article.py")
        exporter = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(exporter)
        target = exporter.export(self.source, self.root / "export")
        self.assertEqual(target.read_bytes(), draft.split(b"===EDITOR NOTES===")[0])
        self.assertEqual(self.source.read_bytes(), draft)
        with self.assertRaises(FileExistsError):
            exporter.export(self.source, self.root / "export")

    def test_frame_keeps_original_and_reports_content_check(self):
        before = self.image.read_bytes()
        result = frame(self.image, self.root / "frame", width=400)
        report = json.loads((result.parent / "边框记录.json").read_text())
        self.assertEqual(before, self.image.read_bytes())
        self.assertEqual(report["resized_content_pixel_difference_ae"], 0)
        self.assertIsNone(report["crop"])
        with Image.open(result) as image:
            self.assertEqual(image.width, 400)
        with self.assertRaises(FileExistsError):
            frame(self.image, self.root / "frame", width=400)

    def rendered_asset(self):
        editable = self.root / "chart.svg"
        editable.write_text('<svg xmlns="http://www.w3.org/2000/svg"/>')
        receipt = self.root / "render.json"
        receipt.write_text(json.dumps({"source_sha256": self.sha(editable),
                                      "output_sha256": self.sha(self.image), "renderer": "synthetic-test",
                                      "image_model": None}))
        self.asset.update(asset_kind="rendered-graphic", editable_source=str(editable),
                          renderer="synthetic-test", render_receipt=str(receipt),
                          image_function="explanation", message="测试来源绑定", feedback_ids=["fixture"])
        return editable, receipt

    def test_rendered_graphic_real_consumer_and_metadata(self):
        self.rendered_asset()
        handoff = self.run_plan()
        manifest = json.loads((handoff.parent / "配图清单.json").read_text())
        item = manifest['files'][0]
        self.assertIsNone(item['image_model'])
        self.assertEqual(item['message'], '测试来源绑定')
        self.assertEqual(item['feedback_ids'], ['fixture'])
        self.assertTrue(load_layout(LAYOUT).run(handoff, self.root / "layout").is_file())

    def test_rendered_graphic_changed_source_or_output_stops(self):
        editable, receipt = self.rendered_asset()
        before = editable.read_bytes()
        editable.write_text('changed')
        with self.assertRaisesRegex(ValueError, 'receipt'):
            self.run_plan()
        editable.write_bytes(before)
        Image.new('RGB', (80, 40), 'red').save(self.image)
        with self.assertRaisesRegex(ValueError, 'receipt'):
            self.run_plan()

    def test_generated_cannot_bypass_cleaning_as_rendered_without_receipt(self):
        self.asset['asset_kind'] = 'rendered-graphic'
        with self.assertRaises(KeyError):
            self.run_plan()
        self.asset['asset_kind'] = 'generated-visual'
        with self.assertRaises(KeyError):
            self.run_plan()


if __name__ == "__main__":
    unittest.main()
