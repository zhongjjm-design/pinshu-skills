from __future__ import annotations

import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from visual_compiler import ROOT, compile_plan, compile_method_candidate, load_configs
from publish_image import CHECKS, prepare
from prepare_publish_images import is_zero_pixel_difference


class PublicVisualTests(unittest.TestCase):
    def test_pixel_difference_must_be_exactly_zero(self):
        for metric in ["0", "0 (0)", "0.0"]:
            self.assertTrue(is_zero_pixel_difference(metric))
        for metric in ["0.1", "0.0001 (0.0001)", "1", "NaN", "", "invalid"]:
            self.assertFalse(is_zero_pixel_difference(metric))

    def plan(self, **kwargs):
        args = dict(content="Compare the source, check names, then inspect the thumbnail.",
                    platform="wechat-article", mode_id="notebook-knowledge-explainer", structure="process")
        args.update(kwargs)
        return compile_plan(**args)

    def test_no_identity_and_no_aesthetic_claim_by_default(self):
        plan = self.plan()
        self.assertEqual(plan["visual_card"]["character"], "none")
        self.assertIsNone(plan["identity_reference"])
        self.assertFalse(plan["acceptance"]["production_claim"])
        self.assertIsNone(plan["rendering"]["actual_model"])

    def test_every_registered_card_and_platform_is_portable(self):
        registry, profiles = load_configs()
        self.assertEqual(len(registry["modes"]), 12)
        self.assertEqual(len(profiles), 11)
        self.assertEqual(len(registry["layouts"]), 18)
        for mode in registry["modes"]:
            self.assertTrue((ROOT / mode["mode_card"]).is_file())

    def test_candidates_require_explicit_test(self):
        with self.assertRaisesRegex(ValueError, "candidate-test"):
            self.plan(mode_id="lively-vector")
        self.assertEqual(self.plan(mode_id="lively-vector", candidate_test=True)["mode_status"], "candidate")

    def test_method_candidates_are_separate_and_explicit(self):
        args = dict(content="Original paper craft concept.", platform="xiaohongshu",
                    method_id="oriental-material-craft", structure="single-claim")
        with self.assertRaisesRegex(ValueError, "candidate-test"):
            compile_method_candidate(**args)
        plan = compile_method_candidate(**args, candidate_test=True)
        self.assertIsNone(plan["visual_card"]["mode"])
        self.assertEqual(plan["method_status"], "candidate-reference")
        self.assertEqual(plan["workflow"]["kind"], "pinshu-visual-method-test")
        self.assertFalse(plan["acceptance"]["production_claim"])
        with self.assertRaisesRegex(ValueError, "single-claim"):
            compile_method_candidate(**dict(args, structure="process"), candidate_test=True)
        with self.assertRaisesRegex(ValueError, "platform"):
            compile_method_candidate(**dict(args, platform="wechat-article"), candidate_test=True)

    def test_method_cli_never_silently_accepts_other_mode_arguments(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp); source = root / "source.md"; source.write_text("Original craft concept.")
            command = [sys.executable, "-B", str(ROOT / "scripts/visual_compiler.py"),
                       "--content-file", str(source), "--platform", "xiaohongshu",
                       "--method-candidate", "oriental-material-craft", "--structure", "single-claim",
                       "--candidate-test", "--output-dir", str(root / "plan")]
            result = subprocess.run(command + ["--exact-text", "unsupported exact label"], capture_output=True, text=True)
            self.assertNotEqual(result.returncode, 0)
            self.assertFalse((root / "plan").exists())
            result = subprocess.run(command, capture_output=True, text=True)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(json.loads((root / "plan/route-plan.json").read_text())["method_status"], "candidate-reference")

    def test_frozen_candidate_remains_blocked(self):
        with self.assertRaisesRegex(ValueError, "frozen"):
            self.plan(mode_id="handwritten-documentary-card", structure="single-claim", candidate_test=True)

    def test_platform_and_structure_limits(self):
        with self.assertRaisesRegex(ValueError, "blocked"):
            self.plan(mode_id="literary-crayon-editorial", structure="single-claim")
        with self.assertRaisesRegex(ValueError, "structure"):
            self.plan(mode_id="airy-architectural-watercolor")
        with self.assertRaisesRegex(ValueError, "density"):
            self.plan(units=6)
        with self.assertRaisesRegex(ValueError, "two main scenes"):
            self.plan(mode_id="hand-drawn-comparison-comic")

    def test_dedicated_vertical_layout(self):
        self.assertEqual(self.plan(platform="xiaohongshu")["visual_card"]["layout"], "vertical-scene-flow")
        with self.assertRaisesRegex(ValueError, "dedicated vertical"):
            self.plan(platform="xiaohongshu", layout="linear-steps")

    def test_true_loop_has_return_path_instead_of_spokes(self):
        plan = self.plan(mode_id="warm-paper", structure="true-loop")
        self.assertEqual(plan["visual_card"]["layout"], "linear-steps")
        self.assertIn("return path from the last step to the first", plan["prompt"])

    def test_exact_text_routes_to_editable_layer(self):
        labels = ["Review the source", "Check names and numbers"]
        plan = self.plan(exact_text=labels)
        self.assertEqual(plan["text_route"], "editable-text-layer")
        for label in labels:
            self.assertIn(label, plan["prompt"])
        self.assertEqual(self.plan(mode_id="archive-tabletop-editorial")["text_route"], "editable-text-layer")

    def test_character_reference_mode_pairing_and_anatomical_hand(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            asset = root / "identity.png"
            asset.write_bytes(b"fixture identity")
            profile = root / "character.json"
            data = {"id": "team-editor", "status": "approved", "identity_asset": "identity.png",
                    "tested_modes": ["character-presenter"], "dominant_hand": "right", "constraints": ["Keep the supplied face."]}
            profile.write_text(json.dumps(data))
            plan = self.plan(mode_id="character-presenter", character_profile=profile)
            self.assertEqual(plan["identity_reference"]["sha256"], hashlib.sha256(asset.read_bytes()).hexdigest())
            self.assertIn("anatomical right hand", plan["prompt"])
            with self.assertRaisesRegex(ValueError, "excludes fixed characters"):
                self.plan(mode_id="warm-paper", character_profile=profile)
            with self.assertRaisesRegex(ValueError, "combination"):
                self.plan(character_profile=profile)
            asset.unlink()
            with self.assertRaisesRegex(ValueError, "asset is missing"):
                self.plan(mode_id="character-presenter", character_profile=profile)

    def test_presenter_rejects_absent_reference(self):
        with self.assertRaisesRegex(ValueError, "requires"):
            self.plan(mode_id="character-presenter")

    def make_delivery_inputs(self, root: Path):
        image = root / "rendered.png"
        image.write_bytes(b"test image")
        plan = root / "route-plan.json"
        plan.write_text(json.dumps(self.plan()))
        qa = root / "qa.json"
        qa.write_text(json.dumps({"source_sha256": hashlib.sha256(image.read_bytes()).hexdigest(),
                                  "plan_sha256": hashlib.sha256(plan.read_bytes()).hexdigest(),
                                  "reviewer": "test reviewer", "notes": "Test fixture; no aesthetic claim.",
                                  "checks": {key: "pass" for key in CHECKS}}))
        return image, plan, qa

    def test_delivery_rejects_review_for_another_image(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            image, plan, qa = self.make_delivery_inputs(root)
            image.write_bytes(b"changed image")
            with self.assertRaisesRegex(ValueError, "does not match"):
                prepare(image, plan, qa, root / "delivery")
            self.assertFalse((root / "delivery").exists())

    def test_plan_cannot_remove_required_visual_checks(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            image, plan, qa = self.make_delivery_inputs(root)
            data = json.loads(plan.read_text()); data["required_checks"] = []
            plan.write_text(json.dumps(data))
            data = json.loads(qa.read_text()); data["checks"] = {}
            data["plan_sha256"] = hashlib.sha256(plan.read_bytes()).hexdigest()
            qa.write_text(json.dumps(data))
            with self.assertRaisesRegex(ValueError, "incomplete"):
                prepare(image, plan, qa, root / "delivery")

    def test_export_failure_never_delivers_original(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            image, plan, qa = self.make_delivery_inputs(root)
            with mock.patch("publish_image.subprocess.run", return_value=subprocess.CompletedProcess([], 1, "", "export failed")):
                with self.assertRaisesRegex(ValueError, "no source-image fallback"):
                    prepare(image, plan, qa, root / "delivery")
            self.assertFalse((root / "delivery/delivery-report.json").exists())
            self.assertTrue(image.is_file())

    @unittest.skipUnless(shutil.which("magick"), "ImageMagick 7 is not installed")
    def test_real_export_preserves_source_and_pixel_identical_copy(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            image, plan, qa = self.make_delivery_inputs(root)
            subprocess.run(["magick", "-size", "1024x512", "xc:#faf7f1", str(image)], check=True)
            data = json.loads(qa.read_text()); data["source_sha256"] = hashlib.sha256(image.read_bytes()).hexdigest()
            qa.write_text(json.dumps(data))
            before = image.read_bytes()
            report = prepare(image, plan, qa, root / "delivery")
            self.assertEqual(report["status"], "candidate-ready-for-review")
            self.assertEqual(report["platform_export"]["output_geometry"], "1600x900")
            self.assertEqual(report["publish_copy"]["status"], "PASS")
            self.assertEqual(image.read_bytes(), before)
            self.assertFalse(report["aesthetic_approval"])


if __name__ == "__main__":
    unittest.main()
