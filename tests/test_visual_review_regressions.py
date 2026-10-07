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
import zipfile

ROOT = Path(__file__).resolve().parents[1]
for package in ["pinshu-visual-system", "pinshu-infographic", "pinshu-business-graphics"]:
    sys.path.insert(0, str(ROOT / package / "scripts"))
from plan_infographic import compile_infographic
from plan_business_graphic import check_dataset
from visual_compiler import compile_plan
from publish_image import CHECKS, WORKFLOW_CHECKS, prepare, reviewed_editable_source
from prepare_publish_images import residual_provenance, PublishPrepError
from visual_contracts import anchor
from render_editable import render, native_inventory


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
            {"text": "\u56e2\u961f\u5de5\u4f5c\u53f0", "approved_by": "human fixture", "reason": "requested editorial heading", "user_quote": "Use this requested editorial heading"}])
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

    def font_file(self):
        candidates = [Path("/System/Library/Fonts/STHeiti Light.ttc"), Path("/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc")]
        for candidate in candidates:
            if candidate.is_file():
                return candidate
        self.skipTest("The documented CJK test font is not installed")

    def bind_native(self, root, native, image, qa):
        receipt = render(native, self.font_file(), "wechat-article", image)
        rp = root / "render-receipt.json"; rp.write_text(json.dumps(receipt))
        review = json.loads(qa.read_text())
        review["source_sha256"] = hashlib.sha256(image.read_bytes()).hexdigest()
        review["editable_source"] = {"path": native.name, "sha256": hashlib.sha256(native.read_bytes()).hexdigest(),
            "rendered_image_sha256": review["source_sha256"], "render_receipt": rp.name}
        qa.write_text(json.dumps(review))
        return review

    @unittest.skipUnless(shutil.which("magick"), "ImageMagick 7 is required")
    def test_native_chart_evidence_accepts_values_and_rejects_tampering(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp); native = root / "chart.svg"
            native.write_text('<svg xmlns="http://www.w3.org/2000/svg" width="1600" height="900"><text x="50" y="100">Sales</text><text x="50" y="200">2025</text><text x="50" y="300">1,200</text></svg>')
            image = root / "image.png"; qp = root / "qa.json"; qp.write_text('{}')
            qa = self.bind_native(root, native, image, qp)
            qa["additional_text_review"] = [{"text": "1,200", "origin": "dataset-value", "reason": "reviewed value"}]
            plan = {"rendering": {"strategy": "editable-chart-final"}, "visible_labels": ["Sales"],
                    "visual_card": {"platform": "wechat-article"},
                    "structured_content": {"dataset": {"rows": [{"label": "2025", "value": 1200}]}}}
            result = reviewed_editable_source(plan, qa, qp, qa["source_sha256"], image)
            self.assertEqual(result["re_render_pixel_difference_ae"], 0)
            plan["structured_content"]["dataset"]["rows"][0]["value"] = 1300
            with self.assertRaisesRegex(ValueError, "dataset labels and values"):
                reviewed_editable_source(plan, qa, qp, qa["source_sha256"], image)
            native.write_text('<svg xmlns="http://www.w3.org/2000/svg"><text>changed</text></svg>')
            with self.assertRaisesRegex(ValueError, "hash does not match"):
                reviewed_editable_source(plan, qa, qp, qa["source_sha256"], image)

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
                "sha256": hashlib.sha256(native.read_bytes()).hexdigest(), "rendered_image_sha256": review["source_sha256"], "render_receipt": "receipt.json"}
            (root / "receipt.json").write_text("{}")
            qa.write_text(json.dumps(review))
            with self.assertRaisesRegex(ValueError, "missing native labels"):
                prepare(image, pp, qa, root / "delivery")

    def test_compound_units_suffixes_and_metric_context(self):
        for text, value, unit in [("\u51fa\u53e3\u989d\u8fbe\u5230300\u4ebf\u7f8e\u5143", 300, "\u4ebf\u7f8e\u5143"),
                                  ("\u9500\u91cf\u8fbe\u5230120\u4e07\u8f86", 120, "\u4e07\u8f86"),
                                  ("Revenue reached $1.2B", 1.2, "B"), ("Volume reached 1.2 billion units", 1.2, "billion units")]:
            data = {"source": "fixture", "period": "2025", "units": unit, "methodology": "fixture", "verified_by": "fixture", "status": "verified",
                    "rows": [{"label": "metric", "value": value, "source_excerpt": text}]}
            with self.subTest(text=text):
                self.assertEqual(check_dataset(data, text), data)
        for text, value, unit in [("300\u4ebf\u5143", 300, "\u4ebf\u5143"), ("\u5e74\u4efd2025\u5e74", 2025, "%")]:
            data["units"] = unit; data["rows"] = [{"label": "metric", "value": value, "source_excerpt": text}]
            with self.subTest(text=text), self.assertRaises(ValueError):
                check_dataset(data, text)

    def test_agent_approval_and_nested_typo_are_rejected(self):
        args = dict(content="Actual source text", platform="wechat-article", mode_id="warm-paper", structure="single-claim")
        with self.assertRaisesRegex(ValueError, "human approval"):
            compile_plan(**args, exact_text=["Unverified"], approved_external_text=[
                {"text": "Unverified", "approved_by": "agent", "reason": "estimate", "user_quote": "made up"}])
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp); path = self.write_brief(root); data = json.loads(path.read_text())
            data["units"][0]["lable"] = "typo"; path.write_text(json.dumps(data))
            with self.assertRaisesRegex(ValueError, "Unknown brief fields"):
                compile_infographic(path)

    def test_linked_pptx_chart_data_is_native_editable_evidence(self):
        with tempfile.TemporaryDirectory() as tmp:
            p = Path(tmp) / "chart.pptx"
            with zipfile.ZipFile(p, "w") as z:
                z.writestr("ppt/slides/slide1.xml", '<p:sld xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main" xmlns:c="http://schemas.openxmlformats.org/drawingml/2006/chart" xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships"><c:chart r:id="rId1"/></p:sld>')
                z.writestr("ppt/slides/_rels/slide1.xml.rels", '<Relationships><Relationship Id="rId1" Target="../charts/chart1.xml"/></Relationships>')
                z.writestr("ppt/charts/chart1.xml", '<c:chartSpace xmlns:c="http://schemas.openxmlformats.org/drawingml/2006/chart"><c:ser><c:cat><c:strCache><c:pt idx="0"><c:v>Revenue</c:v></c:pt></c:strCache></c:cat><c:val><c:numCache><c:pt idx="0"><c:v>1200</c:v></c:pt></c:numCache></c:val></c:ser></c:chartSpace>')
            inventory = native_inventory(p)
            self.assertEqual(str(inventory["chart_points"][0][1]), "1200")
            self.assertEqual(inventory["chart_points"][0][0], "Revenue")
            with zipfile.ZipFile(p, "a") as z:
                z.writestr("ppt/presentation.xml", '<p:presentation xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main" xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships"><p:sldIdLst><p:sldId r:id="second"/><p:sldId r:id="first"/></p:sldIdLst></p:presentation>')
                z.writestr("ppt/_rels/presentation.xml.rels", '<Relationships><Relationship Id="first" Target="slides/slide1.xml"/><Relationship Id="second" Target="slides/slide2.xml"/></Relationships>')
                z.writestr("ppt/slides/slide2.xml", '<p:sld xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main" xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main"><a:p><a:r><a:t>Second slide</a:t></a:r></a:p></p:sld>')
            self.assertEqual(native_inventory(p, 1)["texts"], ["Second slide"])
            self.assertEqual(native_inventory(p, 2)["chart_points"][0][0], "Revenue")

    @unittest.skipUnless(shutil.which("magick"), "ImageMagick 7 is required")
    def test_actual_rerender_rejects_stale_preview_hidden_and_substring_labels(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp); image, pp, qa = self.delivery_inputs(root, editable=True)
            title = json.loads(pp.read_text())["visible_labels"][0]
            native = root / "native.svg"
            native.write_text('<svg xmlns="http://www.w3.org/2000/svg" width="1600" height="900"><text x="70" y="150" font-size="60">' + title + '</text></svg>')
            review = self.bind_native(root, native, image, qa)
            self.assertEqual(prepare(image, pp, qa, root / "good-delivery")["editable_source"]["re_render_pixel_difference_ae"], 0)
            # Modify layout, update declarations honestly, but deliberately keep the old PNG.
            native.write_text(native.read_text().replace('x="70"', 'x="270"'))
            receipt_path = root / "render-receipt.json"; receipt = json.loads(receipt_path.read_text())
            receipt["source_sha256"] = hashlib.sha256(native.read_bytes()).hexdigest(); receipt_path.write_text(json.dumps(receipt))
            review["editable_source"]["sha256"] = receipt["source_sha256"]; qa.write_text(json.dumps(review))
            with self.assertRaisesRegex(ValueError, "re-render differs"):
                prepare(image, pp, qa, root / "stale")
            native.write_text(native.read_text().replace(title, "NOT " + title))
            review["editable_source"]["sha256"] = hashlib.sha256(native.read_bytes()).hexdigest(); qa.write_text(json.dumps(review))
            with self.assertRaisesRegex(ValueError, "whole text segments"):
                prepare(image, pp, qa, root / "substring")
            native.write_text(native.read_text().replace('<text ', '<text opacity="0" '))
            with self.assertRaisesRegex(ValueError, "hidden or transparent"):
                native_inventory(native)

    @unittest.skipUnless(shutil.which("magick"), "ImageMagick 7 is required")
    def test_unplanned_native_text_needs_actual_review(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp); image, pp, qa = self.delivery_inputs(root, editable=True)
            title = json.loads(pp.read_text())["visible_labels"][0]
            native = root / "native.svg"
            native.write_text('<svg xmlns="http://www.w3.org/2000/svg" width="1600" height="900"><text x="70" y="150">' + title + '</text><text x="70" y="300">Supplemental note</text></svg>')
            review = self.bind_native(root, native, image, qa)
            with self.assertRaisesRegex(ValueError, "Unreviewed additional native text"):
                prepare(image, pp, qa, root / "unreviewed")
            review["additional_text_review"] = [{"text": "Supplemental note", "origin": "structural-label", "reason": "Reviewed nonfactual annotation label"}]
            qa.write_text(json.dumps(review))
            self.assertEqual(prepare(image, pp, qa, root / "reviewed")["editable_source"]["additional_text_review"][0]["text"], "Supplemental note")

    def test_percent_words_fullwidth_digits_and_agent_alias(self):
        for text, value, unit in [("Revenue grew 18 percent", 18, "%"), ("Revenue grew 18 percentage", 18, "percent"),
                                  ("\u5458\u5de5\uff11\uff18\uff10\uff10\u4eba", 1800, "\u4eba")]:
            data = {"source": "fixture", "period": "2025", "units": unit, "methodology": "fixture", "verified_by": "fixture", "status": "verified",
                    "rows": [{"label": "metric", "value": value, "source_excerpt": text}]}
            self.assertEqual(check_dataset(data, text), data)
        with self.assertRaisesRegex(ValueError, "human approval"):
            compile_plan(content="Actual source", platform="wechat-article", mode_id="warm-paper", structure="single-claim", exact_text=["Extra"],
                         approved_external_text=[{"text": "Extra", "approved_by": "the agent", "reason": "estimate", "user_quote": "invented"}])

    @unittest.skipUnless(shutil.which("magick"), "ImageMagick 7 is required")
    def test_svg_low_opacity_small_invisible_and_clipped_labels_stop(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp); native = root / "label.svg"
            for attrs, text, error in [("opacity=\"0.01\"", "Required label", "opacity"),
                                       ("font-size=\"1\"", "Required label", "font size|rendered label height"),
                                       ("fill=\"white\"", "Required label", "pixel contribution"),
                                       ("x=\"2400\"", "Required label", "pixel contribution|clipped"),
                                       ("x=\"1500\"", "Required long label", "clipped")]:
                with self.subTest(attrs=attrs), self.assertRaisesRegex(ValueError, error):
                    native.write_text('<svg xmlns="http://www.w3.org/2000/svg" width="1600" height="900"><rect width="1600" height="900" fill="white"/><text y="100" ' + attrs + '>' + text + '</text></svg>')
                    render(native, self.font_file(), "wechat-article", root / "image.png")
            native.write_text('<svg xmlns="http://www.w3.org/2000/svg" width="1600" height="900"><text x="80" y="100" font-size="36"><tspan>Required</tspan><tspan x="80" dy="50">label</tspan></text></svg>')
            self.assertEqual(render(native, self.font_file(), "wechat-article", root / "image.png")["svg_label_checks"]["checked_labels"], 1)

    @unittest.skipUnless(shutil.which("magick"), "ImageMagick 7 is required")
    def test_extra_numeric_claims_and_truncated_conditions_stop(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp); image, pp, qp = self.delivery_inputs(root, editable=True)
            plan = json.loads(pp.read_text()); title = plan["visible_labels"][0]
            original = root / "source.md"; original.write_text(title + "\nOnly approved candidates enter export")
            plan["source"] = {"path": str(original), "file_sha256": hashlib.sha256(original.read_bytes()).hexdigest()}
            native = root / "extra.svg"
            for extra, origin, expected in [("Efficiency improved 300%", "structural-label", "nonnumeric"),
                                             ("35%", "dataset-value", "this plan"),
                                             ("\u6548\u7387\u63d0\u5347\u4e09\u500d", "structural-label", "nonnumeric"),
                                             ("candidates enter export", None, "Unreviewed")]:
                with self.subTest(extra=extra):
                    native.write_text('<svg xmlns="http://www.w3.org/2000/svg" width="1600" height="900"><text x="80" y="100" font-size="36">' + title + '</text><text x="80" y="200" font-size="36">' + extra + '</text></svg>')
                    qa = self.bind_native(root, native, image, qp)
                    qa["additional_text_review"] = [{"text": extra, "origin": origin, "reason": "layout"}] if origin else []
                    with self.assertRaisesRegex(ValueError, expected):
                        reviewed_editable_source(plan, qa, qp, qa["source_sha256"], image)

    def test_percentage_points_are_distinct_from_percent(self):
        for text, unit, allowed in [("Support rose 18 percentage points in 2025", "%", False),
                                    ("Support rose 18 percentage point", "percent", False),
                                    ("Support rose 18 percent points", "%", False),
                                    ("Support rose 18 percentage-points", "%", False),
                                    ("Support rose 18 percentage points", "percentage points", True),
                                    ("Support rose 18 percent", "%", True),
                                    ("Support rose 18 percentage", "%", True),
                                    ("Support rose 18%", "%", True)]:
            data = {"source": "fixture", "period": "2025", "units": unit, "methodology": "fixture", "verified_by": "fixture", "status": "verified",
                    "rows": [{"label": "Support", "value": 18, "source_excerpt": text}]}
            with self.subTest(text=text, unit=unit):
                if allowed:
                    self.assertEqual(check_dataset(data, text), data)
                else:
                    with self.assertRaisesRegex(ValueError, "units or scale"):
                        check_dataset(data, text)

    def test_chinese_numeric_claims_and_approvers(self):
        from publish_image import numeric_annotation
        for text in ["\u6548\u7387\u63d0\u5347\u4e09\u500d", "\u589e\u957f\u4e24\u6210", "\u767e\u5206\u4e4b\u4e09\u5341", "\u7ffb\u4e00\u756a", "\u7ffb\u500d", "\u534a\u500d"]:
            with self.subTest(text=text):
                self.assertTrue(numeric_annotation(text))
        for text in ["\u4e0a\u9762\u4e24\u5c42", "\u4e0b\u9762\u4e24\u5c42", "Direction and execution"]:
            self.assertFalse(numeric_annotation(text))
        for who in ["\u667a\u80fd\u4f53\u52a9\u624b", "\u4eba\u5de5\u667a\u80fd", "\u673a\u5668\u4eba", "the agent"]:
            with self.subTest(who=who), self.assertRaisesRegex(ValueError, "human approval"):
                compile_plan(content="Actual source", platform="wechat-article", mode_id="warm-paper", structure="single-claim", exact_text=["Extra"],
                             approved_external_text=[{"text": "Extra", "approved_by": who, "reason": "estimate", "user_quote": "invented"}])

    @unittest.skipUnless(shutil.which("magick"), "ImageMagick 7 is required")
    def test_svg_effective_scale_and_pt_positive_negative_cases(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp); native = root / "label.svg"
            for viewbox, transform, size in [("0 0 160 90", "", "5.6"), ("0 0 1600 900", "scale(10)", "5.6"), ("0 0 1600 900", "", "42pt")]:
                with self.subTest(viewbox=viewbox, transform=transform, size=size):
                    x, y = (8, 10) if size == "5.6" else (80, 100)
                    native.write_text(f'<svg xmlns="http://www.w3.org/2000/svg" width="1600" height="900" viewBox="{viewbox}"><g transform="{transform}"><text x="{x}" y="{y}" font-size="{size}">Required label</text></g></svg>')
                    self.assertEqual(render(native, self.font_file(), "wechat-article", root / "image.png")["svg_label_checks"]["checked_labels"], 1)
            # Equivalent absolute units must produce the same actual pixels, not merely pass.
            from prepare_publish_images import pixel_difference, is_zero_pixel_difference
            for size in ["42pt", "56px"]:
                native.write_text(f'<svg xmlns="http://www.w3.org/2000/svg" width="1600" height="900"><text x="80" y="100" font-size="{size}">Required label</text></svg>')
                render(native, self.font_file(), "wechat-article", root / (size + ".png"))
            self.assertTrue(is_zero_pixel_difference(pixel_difference("magick", root / "42pt.png", root / "56px.png")))
            # Keep the negative well below 8 rendered pixels for both Heiti and Noto.
            # At size 10 Noto's 12px glyph scales to exactly 8px and correctly passes.
            for viewbox, transform, size in [("0 0 2400 1350", "", "6"), ("0 0 1600 900", "scale(.1)", "60")]:
                with self.subTest(viewbox=viewbox, transform=transform), self.assertRaisesRegex(ValueError, "rendered label height"):
                    native.write_text(f'<svg xmlns="http://www.w3.org/2000/svg" width="1600" height="900" viewBox="{viewbox}"><g transform="{transform}"><text x="100" y="200" font-size="{size}">Required label</text></g></svg>')
                    render(native, self.font_file(), "wechat-article", root / "image.png")

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
