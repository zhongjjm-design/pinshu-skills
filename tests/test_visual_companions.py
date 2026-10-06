"""Behavioral checks for the public visual three-piece set."""
from __future__ import annotations

import copy
import hashlib
import json
from pathlib import Path
import shutil
import struct
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "pinshu-infographic/scripts"))
sys.path.insert(0, str(ROOT / "pinshu-business-graphics/scripts"))
from plan_infographic import compile_infographic
from plan_business_graphic import compile_business, check_dataset
from visual_contracts import check_relations
from publish_image import CHECKS, WORKFLOW_CHECKS, prepare
from visual_compiler import compile_method_candidate


class CompanionTests(unittest.TestCase):
    def brief(self, root, package, **updates):
        example = ROOT / package / "examples"
        shutil.copy2(example / "source.md", root / "source.md")
        data = json.loads((example / "brief.json").read_text())
        data.update(updates)
        path = root / "brief.json"
        path.write_text(json.dumps(data))
        return path

    def test_infographic_requires_original_source(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = self.brief(Path(tmp), "pinshu-infographic", source_file="missing.md")
            with self.assertRaises(FileNotFoundError):
                compile_infographic(path)

    def test_changed_source_invalidates_anchors(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp); path = self.brief(root, "pinshu-infographic")
            (root / "source.md").write_text("A different article.")
            with self.assertRaisesRegex(ValueError, "verbatim"):
                compile_infographic(path)

    def test_infographic_records_provenance_without_semantic_approval(self):
        plan, source = compile_infographic(ROOT / "pinshu-infographic/examples/brief.json")
        self.assertEqual(plan["source"]["sha256"], hashlib.sha256(source.encode()).hexdigest())
        self.assertEqual(plan["structured_content"]["semantic_source_review"], "pending")
        self.assertEqual(plan["workflow"]["kind"], "pinshu-infographic")

    def test_slide_and_mode_limits_intersect(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp); path = self.brief(root, "pinshu-infographic", density="slide", platform="ppt-16x9")
            data = json.loads(path.read_text())
            unit = data["units"][0]
            data["units"] = [dict(unit, id=f"unit-{i}") for i in range(6)]
            path.write_text(json.dumps(data))
            with self.assertRaisesRegex(ValueError, "density"):
                compile_infographic(path)
            path = self.brief(root, "pinshu-infographic", platform="ppt-16x9")
            with self.assertRaisesRegex(ValueError, "slide density"):
                compile_infographic(path)

    def test_infographic_rejects_atmosphere_and_implicit_candidates(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            path = self.brief(root, "pinshu-infographic", mode="airy-architectural-watercolor")
            with self.assertRaisesRegex(ValueError, "infographic mode"):
                compile_infographic(path)
            path = self.brief(root, "pinshu-infographic", mode="lively-vector")
            with self.assertRaisesRegex(ValueError, "candidate-test"):
                compile_infographic(path)
            self.assertEqual(compile_infographic(path, candidate_test=True)[0]["mode_status"], "candidate")

    def test_missing_character_and_editable_exact_labels(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            path = self.brief(root, "pinshu-infographic", mode="character-presenter")
            with self.assertRaisesRegex(ValueError, "requires"):
                compile_infographic(path)
            path = self.brief(root, "pinshu-infographic", exact_text=["main claim", "information relationship"])
            self.assertEqual(compile_infographic(path)[0]["text_route"], "editable-text-layer")

    def test_arrows_need_valid_endpoints_and_source(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp); path = self.brief(root, "pinshu-infographic")
            data = json.loads(path.read_text()); data["relations"][0]["to"] = "missing"
            path.write_text(json.dumps(data))
            with self.assertRaisesRegex(ValueError, "endpoints"):
                compile_infographic(path)

    def test_loop_must_close_through_all_nodes(self):
        units = [{"id": x} for x in "abcd"]
        relation = lambda a, b: {"from": a, "to": b, "verb": "returns", "source_excerpt": "test"}
        with self.assertRaisesRegex(ValueError, "one closed cycle"):
            check_relations([relation("a", "b"), relation("b", "a"), relation("c", "d"), relation("d", "c")], units, "test", "true-loop")
        valid = [relation("a", "b"), relation("b", "c"), relation("c", "d"), relation("d", "a")]
        self.assertEqual(check_relations(valid, units, "test", "true-loop"), valid)

    def test_business_uses_mother_without_mixed_illustration_mode(self):
        plan, _ = compile_business(ROOT / "pinshu-business-graphics/examples/brief.json")
        self.assertIsNone(plan["visual_card"]["mode"])
        self.assertEqual(plan["visual_card"]["mother"], "engineering-blueprint-narrative")
        self.assertEqual(plan["structured_content"]["metaphor"]["status"], "proposed")

    def test_all_seven_business_cards_plan(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            for name in ["typographic-metaphor", "strategic-map", "structural-section", "editorial-collage", "engineering-blueprint-narrative", "chinese-modernism"]:
                path = self.brief(root, "pinshu-business-graphics", mother=name)
                self.assertEqual(compile_business(path)[0]["visual_card"]["mother"], name)
            path = self.data_brief(root)
            self.assertEqual(compile_business(path)[0]["visual_card"]["mother"], "data-journalism")

    def test_data_without_provenance_is_blocked(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = self.brief(Path(tmp), "pinshu-business-graphics", mother="data-journalism")
            with self.assertRaisesRegex(ValueError, "actual dataset"):
                compile_business(path)

    def data_brief(self, root):
        path = self.brief(root, "pinshu-business-graphics", mother="data-journalism", structure="components", relations=[])
        (root / "source.md").write_text((root / "source.md").read_text() + "\nTest fixture A: 12 units. Test fixture B: 8 units.\n")
        data = json.loads(path.read_text())
        data["dataset"] = {"source": "local source.md test fixture", "period": "test fixture", "units": "units",
                           "methodology": "synthetic regression values", "verified_by": "test fixture reviewer", "status": "verified",
                           "rows": [{"label": "A", "value": 12, "source_excerpt": "Test fixture A: 12 units."}]}
        path.write_text(json.dumps(data)); return path

    def test_data_forces_editable_and_rejects_unsourced_values(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp); path = self.data_brief(root)
            plan, _ = compile_business(path)
            self.assertEqual(plan["rendering"]["strategy"], "editable-chart-final")
            self.assertEqual(plan["structured_content"]["data_verification"], "declared-only")
            data = json.loads(path.read_text()); data["dataset"]["rows"][0]["value"] = 99
            path.write_text(json.dumps(data))
            with self.assertRaisesRegex(ValueError, "exact data value"):
                compile_business(path)

    def test_literal_metaphor_needs_source(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = self.brief(Path(tmp), "pinshu-business-graphics", metaphor={"description": "a ladder", "status": "source-literal", "source_excerpt": "absent ladder"})
            with self.assertRaisesRegex(ValueError, "verbatim"):
                compile_business(path)

    def test_numeric_substring_is_not_a_source_value(self):
        data = {"source": "fixture", "period": "fixture", "units": "units", "methodology": "fixture",
                "verified_by": "fixture", "status": "verified",
                "rows": [{"label": "A", "value": 12, "source_excerpt": "A: 120 units."}]}
        for excerpt in ["A: 120 units.", "A: -12 units."]:
            data["rows"][0]["source_excerpt"] = excerpt
            with self.subTest(excerpt=excerpt), self.assertRaisesRegex(ValueError, "exact data value"):
                check_dataset(data, excerpt)

    def delivery_inputs(self, root, plan):
        image = root / "image.png"; image.write_bytes(b"test fixture")
        pp = root / "plan.json"; pp.write_text(json.dumps(plan))
        qa = root / "qa.json"
        checks = CHECKS + WORKFLOW_CHECKS[plan["workflow"]["kind"]]
        record = {"source_sha256": hashlib.sha256(image.read_bytes()).hexdigest(),
                  "plan_sha256": hashlib.sha256(pp.read_bytes()).hexdigest(),
                  "reviewer": "fixture reviewer", "notes": "Test only; no aesthetic approval", "checks": {x: "pass" for x in checks}}
        qa.write_text(json.dumps(record)); return image, pp, qa

    def test_specialized_review_cannot_be_skipped(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp); plan, _ = compile_infographic(ROOT / "pinshu-infographic/examples/brief.json")
            plan["required_checks"] = list(CHECKS)
            image, pp, qa = self.delivery_inputs(root, plan)
            data = json.loads(qa.read_text()); del data["checks"]["information-relationships"]
            qa.write_text(json.dumps(data))
            with self.assertRaisesRegex(ValueError, "incomplete"):
                prepare(image, pp, qa, root / "delivery")
            self.assertFalse((root / "delivery").exists())

    def test_raster_cannot_be_delivered_as_precision_chart_final(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp); plan, _ = compile_business(self.data_brief(root))
            image, pp, qa = self.delivery_inputs(root, plan)
            with self.assertRaisesRegex(ValueError, "editable chart final"):
                prepare(image, pp, qa, root / "delivery")
            self.assertFalse((root / "delivery").exists())

    def test_missing_public_core_does_not_start_a_plan(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp); scripts = root / "pinshu-infographic/scripts"; scripts.mkdir(parents=True)
            shutil.copy2(ROOT / "pinshu-infographic/scripts/plan_infographic.py", scripts)
            result = subprocess.run([sys.executable, "-B", str(scripts / "plan_infographic.py"), "--help"], capture_output=True, text=True)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("public pinshu-visual-system", result.stderr)

    def test_older_public_core_has_an_actionable_dependency_error(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp); core = root / "pinshu-visual-system"; core.mkdir()
            (core / ".public-bundle").write_text("public")
            (core / "VERSION").write_text("0.1.0")
            for package, script in [("pinshu-infographic", "plan_infographic.py"), ("pinshu-business-graphics", "plan_business_graphic.py")]:
                scripts = root / package / "scripts"; scripts.mkdir(parents=True)
                shutil.copy2(ROOT / package / "scripts" / script, scripts)
                result = subprocess.run([sys.executable, "-B", str(scripts / script), "--help"], capture_output=True, text=True)
                self.assertNotEqual(result.returncode, 0)
                self.assertIn("upgrade the complete visual set", result.stderr)

    def test_method_review_cannot_omit_cultural_source_fit(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            plan = compile_method_candidate("Original fictional craft concept.", "xiaohongshu",
                                            "oriental-material-craft", "single-claim", candidate_test=True)
            image, pp, qa = self.delivery_inputs(root, plan)
            record = json.loads(qa.read_text()); del record["checks"]["cultural-source-fit"]
            qa.write_text(json.dumps(record))
            with self.assertRaisesRegex(ValueError, "incomplete"):
                prepare(image, pp, qa, root / "delivery")
            self.assertFalse((root / "delivery").exists())

    def test_public_example_hashes_and_dimensions_match_files(self):
        samples = [("pinshu-infographic", "source-faithful-diagram"),
                   ("pinshu-business-graphics", "review-workbench"),
                   ("pinshu-visual-system", "craft-paper"), ("pinshu-visual-system", "craft-fold")]
        digest = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
        for package, stem in samples:
            example = ROOT / package / "examples"
            evidence = json.loads((example / (stem + ".evidence.json")).read_text())
            self.assertEqual(digest(example / evidence["public_image"]), evidence["public_image_sha256"])
            self.assertEqual(digest(example / evidence["source_file"]), evidence["source_sha256"])
            self.assertEqual(digest(example / evidence["generation_record"]), evidence["generation_record_sha256"])
            generation = json.loads((example / evidence["generation_record"]).read_text())
            for operation in generation["operations"]:
                self.assertEqual(hashlib.sha256(operation["prompt"].encode()).hexdigest(), operation["prompt_sha256"])
            data = (example / evidence["public_image"]).read_bytes()
            self.assertEqual(data[:8], b"\x89PNG\r\n\x1a\n")
            width, height = struct.unpack(">II", data[16:24])
            self.assertEqual(f"{width}x{height}", evidence["mechanical_checks"]["output_geometry"])
            self.assertEqual(evidence["human_review"], "pending")
            self.assertFalse(evidence["aesthetic_approval"])

    def test_real_cli_both_companions_save_source_and_plan(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            for package, script in [("pinshu-infographic", "plan_infographic.py"), ("pinshu-business-graphics", "plan_business_graphic.py")]:
                output = root / package
                result = subprocess.run([sys.executable, "-B", str(ROOT / package / "scripts" / script), "--brief", str(ROOT / package / "examples/brief.json"), "--output-dir", str(output)], capture_output=True, text=True)
                self.assertEqual(result.returncode, 0, result.stderr)
                plan = json.loads((output / "route-plan.json").read_text())
                self.assertEqual(plan["source"]["sha256"], hashlib.sha256((output / "source-content.txt").read_bytes()).hexdigest())
                self.assertTrue((output / "prompt-final.txt").is_file())


if __name__ == "__main__":
    unittest.main()
