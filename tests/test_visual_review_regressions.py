"""Behavioral regressions from independent review, with self-made inputs."""
from pathlib import Path
import copy
import hashlib
import json
import shutil
import struct
import subprocess
import sys
import tempfile
import unittest
import zlib

ROOT = Path(__file__).resolve().parents[1]
for package in ["pinshu-visual-system", "pinshu-infographic", "pinshu-business-graphics"]:
    sys.path.insert(0, str(ROOT / package / "scripts"))
from plan_infographic import compile_infographic
from plan_business_graphic import check_dataset
from visual_compiler import compile_plan
from publish_image import CHECKS, WORKFLOW_CHECKS, prepare, reviewed_editable_source
from prepare_publish_images import residual_provenance, PublishPrepError
from visual_contracts import anchor


def chunk(kind, data):
    return struct.pack(">I", len(data)) + kind + data + struct.pack(">I", zlib.crc32(kind + data) & 0xffffffff)


def png(width, height, pixels=None, metadata=None):
    body = (b"\0" + b"\xff" * width * 4) * height if pixels is None else pixels
    return (b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", struct.pack(">IIBBBBB", width, height, 8, 6, 0, 0, 0))
            + (chunk(b"tEXt", metadata) if metadata else b"")
            + chunk(b"IDAT", zlib.compress(body, level=0)) + chunk(b"IEND", b""))


class ReviewRegressions(unittest.TestCase):
    def write_brief(self, root, **updates):
        example = ROOT / "pinshu-infographic/examples"
        (root / "source.md").write_text((example / "source.md").read_text())
        data = json.loads((example / "brief.json").read_text())
        data.update(updates)
        path = root / "brief.json"
        path.write_text(json.dumps(data, ensure_ascii=False))
        return path

    def test_chinese_number_context_and_thousands(self):
        for text, value, unit in [("\u540c\u6bd4\u589e\u957f18%", 18, "%"), ("\u5e02\u573a\u89c4\u6a21300\u4ebf\u5143", 300, "\u4ebf\u5143"),
                                  ("\u5458\u5de5\u7ea61.2\u4e07\u4eba", 1.2, "\u4e07\u4eba"), ("\u5ba1\u6838\u4e861,200\u5f20", 1200, "\u5f20")]:
            data = {"source": "fixture", "period": "2025", "units": unit, "methodology": "fixture",
                    "verified_by": "fixture", "status": "verified", "rows": [{"label": "\u6307\u6807", "value": value, "source_excerpt": text}]}
            with self.subTest(text=text):
                self.assertEqual(check_dataset(data, text), data)
                bad = copy.deepcopy(data); bad["rows"][0]["value"] = value + 1
                with self.assertRaisesRegex(ValueError, "exact data value"):
                    check_dataset(bad, text)

    def test_wrong_scale_and_bare_number_still_rejected(self):
        data = {"source": "fixture", "period": "2025", "units": "\u4eba", "methodology": "fixture",
                "verified_by": "fixture", "status": "verified", "rows": [{"label": "\u5458\u5de5", "value": 1.2, "source_excerpt": "\u5458\u5de5\u7ea61.2\u4e07\u4eba"}]}
        with self.assertRaisesRegex(ValueError, "units or scale"):
            check_dataset(data, "\u5458\u5de5\u7ea61.2\u4e07\u4eba")
        data["units"] = "%"; data["rows"] = [{"label": "\u589e\u957f", "value": 18, "source_excerpt": "18%"}]
        with self.assertRaisesRegex(ValueError, "context"):
            check_dataset(data, "\u540c\u6bd4\u589e\u957f18%")

    def test_relationships_typo_and_cross_package_fields_are_errors(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            for updates in [{"relationships": [], "structure": "comparison"}, {"mother": "data-journalism"}]:
                with self.subTest(updates=updates), self.assertRaisesRegex(ValueError, "Unknown brief fields"):
                    compile_infographic(self.write_brief(root, **updates))

    def test_chinese_units_trigger_editable_without_exact_text(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp); path = self.write_brief(root)
            data = json.loads(path.read_text())
            for i, unit in enumerate(data["units"]):
                unit["label"] = ["\u627e\u5230\u539f\u6587\u771f\u6b63\u652f\u6301\u7684\u4e3b\u8981\u4e3b\u5f20", "\u9009\u51fa\u8bfb\u8005\u9700\u8981\u7406\u89e3\u7684\u4fe1\u606f\u5173\u7cfb", "\u9010\u9879\u6838\u5bf9\u56fe\u4e2d\u6807\u7b7e\u548c\u7bad\u5934\u542b\u4e49"][i]
            path.write_text(json.dumps(data, ensure_ascii=False))
            plan, _ = compile_infographic(path)
            self.assertEqual(plan["text_route"], "editable-text-layer")
            self.assertIn(data["units"][0]["label"], plan["visible_labels"])

    def test_exact_text_needs_source_or_declared_approval(self):
        args = dict(content="\u771f\u5b9e\u539f\u6587\u8ba8\u8bba\u5ba1\u6838\u6d41\u7a0b\u3002", platform="wechat-article", mode_id="warm-paper", structure="single-claim")
        with self.assertRaisesRegex(ValueError, "absent from the source"):
            compile_plan(**args, exact_text=["\u6536\u51652026\u4e07\u5143"])
        plan = compile_plan(**args, exact_text=["\u56e2\u961f\u5de5\u4f5c\u53f0"], approved_external_text=[
            {"text": "\u56e2\u961f\u5de5\u4f5c\u53f0", "approved_by": "human fixture", "reason": "requested editorial heading"}])
        self.assertEqual(plan["exact_text_evidence"][0]["origin"], "declared-user-approval")

    def test_weak_excerpt_is_not_a_useful_anchor(self):
        for text in ["\uff0c", "\u7684"]:
            with self.subTest(text=text), self.assertRaisesRegex(ValueError, "meaningful context"):
                anchor(text, "\u539f\u6587\u7684\u5185\u5bb9\uff0c\u6709\u5b8c\u6574\u4e0a\u4e0b\u6587\u3002")

    def test_timeline_error_has_a_working_route(self):
        with tempfile.TemporaryDirectory() as tmp:
            for mode in ["warm-paper", "lively-vector", "character-presenter"]:
                with self.subTest(mode=mode), self.assertRaisesRegex(ValueError, "mother=strategic-map"):
                    compile_infographic(self.write_brief(Path(tmp), structure="timeline", mode=mode), candidate_test=True)

    def test_pixel_marker_is_not_metadata_but_real_metadata_is_detected(self):
        self.assertEqual(residual_provenance(png(1, 1, b"\0c2pa")), [])
        self.assertIn("c2pa", residual_provenance(png(1, 1, metadata=b"Comment\0c2pa")))
        with self.assertRaises(PublishPrepError):
            residual_provenance(png(1, 1)[:-3])

    def test_compressed_metadata_checks_keywords_and_has_safe_errors(self):
        base = png(1, 1)
        insert = lambda kind, body: base[:-12] + chunk(kind, body) + base[-12:]
        self.assertIn("c2pa", residual_provenance(insert(b"zTXt", b"c2pa\0\0" + zlib.compress(b"plain text"))))
        self.assertIn("c2pa", residual_provenance(insert(b"iTXt", b"Comment\0\1\0\0\0" + zlib.compress(b"c2pa"))))
        for kind, body in [(b"zTXt", b"missing separator"), (b"zTXt", b"Comment\0\0broken"),
                           (b"iTXt", b"Comment\0\1"), (b"iTXt", b"Comment\0\1\0\0\0broken")]:
            with self.subTest(kind=kind, body=body), self.assertRaises(PublishPrepError):
                residual_provenance(insert(kind, body))

    def test_native_chart_evidence_accepts_values_and_rejects_tampering(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp); native = root / "chart.svg"
            native.write_text('<svg xmlns="http://www.w3.org/2000/svg"><text>Sales</text><text>2025 1,200</text></svg>')
            plan = {"rendering": {"strategy": "editable-chart-final"}, "visible_labels": ["Sales"],
                    "structured_content": {"dataset": {"rows": [{"label": "2025", "value": 1200}]}}}
            qa = {"editable_source": {"path": "chart.svg", "sha256": hashlib.sha256(native.read_bytes()).hexdigest(),
                                      "rendered_image_sha256": "fixture-image-hash"}}
            result = reviewed_editable_source(plan, qa, root / "qa.json", "fixture-image-hash")
            self.assertEqual(result["native_labels_checked"], ["Sales"])
            plan["structured_content"]["dataset"]["rows"][0]["value"] = 1300
            with self.assertRaisesRegex(ValueError, "dataset labels and values"):
                reviewed_editable_source(plan, qa, root / "qa.json", "fixture-image-hash")
            native.write_text('<svg xmlns="http://www.w3.org/2000/svg"><text>changed</text></svg>')
            with self.assertRaisesRegex(ValueError, "hash does not match"):
                reviewed_editable_source(plan, qa, root / "qa.json", "fixture-image-hash")

    def delivery_inputs(self, root, size=(1600, 900), editable=False):
        plan = compile_plan("\u6807\u9898\u6765\u81ea\u771f\u5b9e\u539f\u6587", "wechat-article", "warm-paper", "single-claim", title="\u6807\u9898\u6765\u81ea\u771f\u5b9e\u539f\u6587")
        if editable:
            plan["text_route"] = "editable-text-layer"
        image = root / "image.png"; image.write_bytes(png(*size))
        pp = root / "plan.json"; pp.write_text(json.dumps(plan))
        qa = root / "qa.json"
        qa.write_text(json.dumps({"source_sha256": hashlib.sha256(image.read_bytes()).hexdigest(),
            "plan_sha256": hashlib.sha256(pp.read_bytes()).hexdigest(), "review_stage": "final-platform-image",
            "reviewer": "fixture", "notes": "Synthetic negative test, no aesthetic acceptance",
            "checks": {k: "pass" for k in CHECKS}}))
        return image, pp, qa

    def test_original_size_cannot_be_cropped_after_review(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp); image, pp, qa = self.delivery_inputs(root, (1024, 1024))
            with self.assertRaisesRegex(ValueError, "final platform dimensions"):
                prepare(image, pp, qa, root / "delivery")
            self.assertFalse((root / "delivery").exists())

    def test_editable_background_requires_native_source(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp); image, pp, qa = self.delivery_inputs(root, editable=True)
            with self.assertRaisesRegex(ValueError, "not only a background"):
                prepare(image, pp, qa, root / "delivery")
            native = root / "layer.svg"; native.write_text('<svg xmlns="http://www.w3.org/2000/svg"><text>\u65e0\u5173\u6587\u5b57</text></svg>')
            review = json.loads(qa.read_text()); review["editable_source"] = {"path": "layer.svg",
                "sha256": hashlib.sha256(native.read_bytes()).hexdigest(), "rendered_image_sha256": review["source_sha256"]}
            qa.write_text(json.dumps(review))
            with self.assertRaisesRegex(ValueError, "missing native labels"):
                prepare(image, pp, qa, root / "delivery")

    @unittest.skipUnless(shutil.which("magick"), "ImageMagick 7 is required")
    def test_contain_export_preserves_edge_content_and_cover_reports_crop(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp); image = root / "bands.png"
            subprocess.run(["magick", "-size", "1024x1024", "xc:white", "-fill", "red", "-draw", "rectangle 0,0 1023,99", str(image)], check=True)
            for fit in ["contain", "cover"]:
                out = root / fit
                subprocess.run([sys.executable, str(ROOT / "pinshu-visual-system/scripts/export_platform_image.py"),
                    "--source", str(image), "--platform", "wechat-article", "--fit", fit, "--output-dir", str(out)], check=True, capture_output=True)
                report = json.loads((out / "platform-export-report.json").read_text())
                self.assertAlmostEqual(report["crop_fraction"]["top"], 0 if fit == "contain" else .21875)
                histogram = subprocess.check_output(["magick", str(out / "platform-export.png"), "-format", "%c", "histogram:info:"], text=True)
                self.assertEqual("#FF0000" in histogram.upper(), fit == "contain")


if __name__ == "__main__":
    unittest.main()
