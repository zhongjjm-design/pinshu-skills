from __future__ import annotations

import hashlib
import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PIPE = ROOT / "pinshu-course-capture" / "scripts" / "course_pipeline.py"


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write_json(path: Path, data: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")


class Harness:
    def __init__(self, root: Path, course_id: str = "foundation", count: int = 1, profile: str = "strict") -> None:
        self.root = root
        self.course = root / "course"
        self.runtime = root / "runtime"
        self.state = self.runtime / "course-state.json"
        self.manifest = root / "manifest.json"
        self.course.mkdir(parents=True)
        self.runtime.mkdir(parents=True)
        data = {
            "schema_version": 1,
            "course_id": course_id,
            "course_title": "Foundation Course",
            "lecturer": "Example Lecturer",
            "course_root": str(self.course),
            "runtime_dir": str(self.runtime),
            "source_adapter": "local",
            "output_language": "en-US",
            "course_purpose": ["systematic_learning"],
            "purpose_decision_basis": "Test the public production foundation.",
            "assurance_mode": profile,
            "assurance_decision_basis": "Tests require explicit evidence.",
            "optional_extensions": {"active_recall": False, "learning_training": False, "horizontal_topics": False},
            "external_use": {"enabled": False, "intended_uses": []},
            "intake_confirmation": {"confirmed": True, "confirmed_by": "tester", "confirmed_at": "2026-10-07T00:00:00Z"},
            "budgets": {"max_tokens_per_lesson": 10000, "max_wall_minutes_per_lesson": 100,
                        "max_agent_calls_per_lesson": 20, "max_reworks_per_lesson": 1,
                        "max_qa_rounds_per_lesson": 5},
            "sample_gate": {"lesson_no": 1, "approved": False},
            "naming_template": "Lesson-{lesson_no:02d}-{title}.md",
            "path_templates": {
                "source": "00_Source_Transcripts/{filename}",
                "official_faithful": "01_Faithful_Edits/{filename}",
                "official_lecture": "02_Structured_Lectures/{filename}",
                "course_map": "00_Course_Map.md"
            },
            "promotion_hygiene": {"source_link_fields": ["source"],
                                  "forbidden_draft_markers": ["DRAFT ONLY", "PENDING QA"],
                                  "require_source_backlink": True},
            "writer_model": "writer-model",
            "qa_model": "qa-model",
            "strong_model": "strong-model",
            "gold_samples": [],
            "lessons": [{"lesson_no": n, "title": f"Topic-{n}", "source_video": f"{n}.mp4",
                         "source_path": str(root / f"{n}.mp4")} for n in range(1, count + 1)]
        }
        write_json(self.manifest, data)
        self.run("init", "--manifest", str(self.manifest), "--state", str(self.state))

    def run(self, *args: str, expect: int = 0, cwd: Path | None = None) -> subprocess.CompletedProcess[str]:
        cp = subprocess.run([sys.executable, str(PIPE), *args], cwd=cwd or self.root,
                            text=True, capture_output=True)
        if cp.returncode != expect:
            raise AssertionError(f"expected {expect}, got {cp.returncode}: {' '.join(args)}\nOUT:{cp.stdout}\nERR:{cp.stderr}")
        return cp

    def transition(self, lesson: int, target: str, artifacts: dict[str, Path] | None = None,
                   expect: int = 0, severity: str | None = None) -> subprocess.CompletedProcess[str]:
        args = ["transition", "--state", str(self.state), "--lesson", str(lesson), "--to", target,
                "--reason", "test"]
        if target in {"DRAFTED", "SEMANTIC_QA_PASS", "FIX_REQUIRED", "ESCALATED"}:
            args.extend(["--wall-minutes-used", "1", "--tokens-used", "10"])
        if severity:
            args.extend(["--severity", severity])
        for key, path in (artifacts or {}).items():
            args.extend(["--artifact", f"{key}={path.resolve()}"])
        return self.run(*args, expect=expect)

    def state_data(self) -> dict:
        return json.loads(self.state.read_text(encoding="utf-8"))

    def lesson(self, lesson_no: int = 1) -> dict:
        return next(item for item in self.state_data()["lessons"] if item["lesson_no"] == lesson_no)

    def make_drafts(self, lesson_no: int = 1) -> dict[str, Path]:
        lesson_dir = self.runtime / f"lesson-{lesson_no}"
        lesson_dir.mkdir(parents=True, exist_ok=True)
        rendered = json.loads(self.run("paths", "--state", str(self.state), "--lesson", str(lesson_no)).stdout)["paths"]
        source = Path(rendered["source"])
        source.parent.mkdir(parents=True, exist_ok=True)
        faithful = lesson_dir / "faithful.md"
        lecture = lesson_dir / "lecture.md"
        uncertainties = lesson_dir / "uncertainties.json"
        coverage = lesson_dir / "coverage.json"
        source.write_text("Opening evidence. Middle case 42. Ending boundary.\n", encoding="utf-8")
        header = f"---\nsource: {source.resolve()}\n---\n\n"
        faithful.write_text(header + "# Faithful\n\nOpening evidence. Middle case 42. Ending boundary.\n", encoding="utf-8")
        lecture.write_text(header + "# Lecture\n\n## Method\n\nOpening evidence. Middle case 42. Ending boundary.\n", encoding="utf-8")
        write_json(uncertainties, {"confirmed_corrections": [], "variants": [], "unresolved": [],
                                   "summary": {"confirmed_corrections": 0, "variant_entries": 0, "unresolved": 0}})
        write_json(coverage, {"block_count": 1, "status_summary": {"retained": 1, "merged": 0, "noise": 0, "uncertain": 0},
                              "blocks": [{"id": "B01", "status": "retained"}]})
        return {"source": source, "faithful": faithful, "lecture": lecture,
                "uncertainties": uncertainties, "coverage": coverage}

    def qa_report(self, lesson_no: int, scope: str = "full", round_no: int | None = None,
                  hashes: dict[str, str] | None = None, path: Path | None = None) -> Path:
        lesson = self.lesson(lesson_no)
        path = path or self.runtime / f"lesson-{lesson_no}" / "qa.json"
        hashes = hashes or {k: v for k, v in lesson["artifact_sha256"].items()
                            if k in {"source", "faithful", "lecture", "uncertainties", "coverage"}}
        round_no = round_no or lesson["attempts"]["qa"] + 1
        write_json(path, {
            "schema_version": 2, "report_type": "qa_report",
            "course_id": self.state_data()["course_id"], "lesson_no": lesson_no,
            "reviewer_kind": "independent_qa", "reviewer_model": "qa-model",
            "assurance_mode": lesson["effective_policy"]["assurance_mode"],
            "review_round": round_no, "review_scope": scope,
            "decision": "pass", "recommended_state": "SEMANTIC_QA_PASS",
            "source_identity": {"passed": True, "notes": []},
            "coverage": {"passed": True, "opening_checked": True, "middle_checked": True,
                         "ending_checked": True, "longest_case_checked": True,
                         "high_risk_anchors_checked": True},
            "input_sha256": hashes, "issues": [], "notes": [], "requires_strong_model": False
        })
        return path

    def accept(self, lesson_no: int = 1, course_map_text: str | None = None) -> dict[str, Path]:
        files = self.make_drafts(lesson_no)
        self.transition(lesson_no, "CAPTURED", {"source": files["source"]})
        self.transition(lesson_no, "SOURCE_VERIFIED")
        self.transition(lesson_no, "DRAFTED", {k: files[k] for k in ("faithful", "lecture", "uncertainties", "coverage")})
        self.run("preflight", "--state", str(self.state), "--lesson", str(lesson_no))
        qa = self.qa_report(lesson_no)
        self.transition(lesson_no, "SEMANTIC_QA_PASS", {"qa_report": qa})
        paths = json.loads(self.run("paths", "--state", str(self.state), "--lesson", str(lesson_no)).stdout)["paths"]
        official_f = Path(paths["official_faithful"])
        official_l = Path(paths["official_lecture"])
        course_map = Path(paths["course_map"])
        official_f.parent.mkdir(parents=True, exist_ok=True)
        official_l.parent.mkdir(parents=True, exist_ok=True)
        course_map.parent.mkdir(parents=True, exist_ok=True)
        official_f.write_bytes(files["faithful"].read_bytes())
        official_l.write_bytes(files["lecture"].read_bytes())
        course_map.write_text(course_map_text or f"# Course Map\n\n- Lesson {lesson_no}\n", encoding="utf-8")
        self.transition(lesson_no, "PROMOTED", {"official_faithful": official_f, "official_lecture": official_l})
        self.transition(lesson_no, "ACCEPTED", {"course_map": course_map})
        return {**files, "qa_report": qa, "official_faithful": official_f,
                "official_lecture": official_l, "course_map": course_map}

    def revision_report(self, lesson_no: int, path: Path, fake_equivalence: bool = False) -> Path:
        state = self.state_data()
        lesson = next(item for item in state["lessons"] if item["lesson_no"] == lesson_no)
        revision = lesson["revision"]
        source = Path(lesson["artifacts"]["source"])
        official_f = Path(lesson["artifacts"]["official_faithful"])
        official_l = Path(lesson["artifacts"]["official_lecture"])
        uncertainties = Path(lesson["artifacts"]["uncertainties"])
        coverage = Path(lesson["artifacts"]["coverage"])
        shared = state["shared_artifacts"]["course_map"]
        new_hashes = {"source": digest(source), "faithful": digest(official_f), "lecture": digest(official_l),
                      "uncertainties": digest(uncertainties), "coverage": digest(coverage),
                      "course_map": digest(Path(shared["path"]))}
        report = {"schema_version": 1, "report_type": "revision_report", "course_id": state["course_id"],
                  "lesson_no": lesson_no, "revision_id": revision["revision_id"],
                  "revision_type": revision["type"], "reason": "documented test revision",
                  "baseline_sha256": revision["baseline_sha256"], "new_sha256": new_hashes}
        if fake_equivalence:
            report["semantic_equivalent"] = True
        write_json(path, report)
        return path


class ProductionFoundationTests(unittest.TestCase):
    def test_work_order_filters_case_library_and_never_guesses_a_path(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            h = Harness(Path(td), profile="fast")
            unresolved = json.loads(h.run("work-order", "--state", str(h.state), "--lesson", "1").stdout)
            self.assertEqual(unresolved["case_library"]["status"], "unresolved")
            library = h.root / "cases.json"
            write_json(library, {"cases": [
                {"status": "confirmed", "expires_at": "2099-01-01", "triggers": [], "scopes": ["fast"],
                 "principle": "Check identity before transformation.", "check_method": "Compare the registered identifiers."},
                {"status": "draft", "triggers": [], "scopes": ["fast"],
                 "principle": "Do not inject this.", "check_method": "None."},
                {"status": "confirmed", "expires_at": "2000-01-01", "triggers": [], "scopes": ["fast"],
                 "principle": "Expired.", "check_method": "None."}
            ]})
            state = h.state_data(); state["production"]["case_library"] = {"path": str(library)}; write_json(h.state, state)
            resolved = json.loads(h.run("work-order", "--state", str(h.state), "--lesson", "1").stdout)
            self.assertEqual(resolved["case_library"]["status"], "resolved")
            self.assertEqual(len(resolved["case_library"]["cases"]), 1)
            self.assertNotIn("expires_at", resolved["case_library"]["cases"][0])

    def test_preflight_generates_v2_report_and_binds_it(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            h = Harness(Path(td))
            files = h.make_drafts()
            h.transition(1, "CAPTURED", {"source": files["source"]})
            h.transition(1, "SOURCE_VERIFIED")
            h.transition(1, "DRAFTED", {k: files[k] for k in ("faithful", "lecture", "uncertainties", "coverage")})
            result = json.loads(h.run("preflight", "--state", str(h.state), "--lesson", "1").stdout)
            report = json.loads(Path(result["report"]).read_text())
            self.assertEqual(report["report_type"], "mechanical_report")
            self.assertEqual(report["algorithm_version"], "pinshu-mechanical-2026-10-v2")
            self.assertIsNone(report["semantic_pass"])
            self.assertEqual(h.lesson()["status"], "MECHANICAL_PASS")

    def test_self_rework_changes_hash_without_consuming_qa_and_is_bounded(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            h = Harness(Path(td))
            files = h.make_drafts()
            h.transition(1, "CAPTURED", {"source": files["source"]})
            h.transition(1, "SOURCE_VERIFIED")
            h.transition(1, "DRAFTED", {k: files[k] for k in ("faithful", "lecture", "uncertainties", "coverage")})
            changed = h.runtime / "lesson-1" / "faithful-v2.md"
            changed.write_text(files["faithful"].read_text() + "\nA restored sentence.\n", encoding="utf-8")
            h.run("self-rework", "--state", str(h.state), "--lesson", "1", "--reason", "writer found omission",
                  "--artifact", f"faithful={changed.resolve()}", "--tokens-used", "5", "--wall-minutes-used", "1", "--agent-calls", "1")
            lesson = h.lesson()
            self.assertEqual(lesson["attempts"]["qa"], 0)
            self.assertEqual(lesson["attempts"]["rework"], 1)
            changed2 = h.runtime / "lesson-1" / "faithful-v3.md"
            changed2.write_text(changed.read_text() + "Again\n", encoding="utf-8")
            rejected = h.run("self-rework", "--state", str(h.state), "--lesson", "1", "--reason", "again",
                             "--artifact", f"faithful={changed2.resolve()}", expect=2)
            self.assertIn("budget exhausted", rejected.stderr)

    def test_targeted_recheck_registers_the_actual_qa_report(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            h = Harness(Path(td))
            files = h.make_drafts()
            h.transition(1, "CAPTURED", {"source": files["source"]})
            h.transition(1, "SOURCE_VERIFIED")
            h.transition(1, "DRAFTED", {k: files[k] for k in ("faithful", "lecture", "uncertainties", "coverage")})
            h.run("preflight", "--state", str(h.state), "--lesson", "1")
            first = h.qa_report(1, "full")
            h.transition(1, "SEMANTIC_QA_PASS", {"qa_report": first})
            # Simulate a legal targeted round from MECHANICAL_PASS without changing the reviewed inputs.
            state = h.state_data(); lesson = state["lessons"][0]; lesson["status"] = "MECHANICAL_PASS"
            write_json(h.state, state)
            second = h.qa_report(1, "targeted_recheck", round_no=2, path=h.runtime / "lesson-1" / "qa-round-2.json")
            h.transition(1, "SEMANTIC_QA_PASS", {"qa_report": second})
            evidence = h.lesson()["semantic_evidence_history"][-1]
            self.assertEqual(evidence["kind"], "qa_report")
            self.assertEqual(evidence["review_scope"], "targeted_recheck")
            self.assertEqual(Path(evidence["path"]).resolve(), second.resolve())

    def test_legacy_relative_artifact_resolves_from_wrong_cwd(self) -> None:
        with tempfile.TemporaryDirectory() as td, tempfile.TemporaryDirectory() as wrong:
            root = Path(td)
            h = Harness(root, profile="fast")
            legacy_dir = h.runtime / "lesson-1"
            legacy_dir.mkdir(parents=True, exist_ok=True)
            source = legacy_dir / "source.md"; source.write_text("legacy source", encoding="utf-8")
            state = h.state_data(); state.pop("path_context", None)
            lesson = state["lessons"][0]
            lesson["status"] = "CAPTURED"; lesson["artifacts"] = {"source": "runtime/lesson-1/source.md"}
            lesson["artifact_sha256"] = {"source": digest(source)}
            write_json(h.state, state)
            audit = json.loads(h.run("audit", "--state", str(h.state), cwd=Path(wrong)).stdout)
            self.assertTrue(audit["ok"])
            order = json.loads(h.run("work-order", "--state", str(h.state), "--lesson", "1", cwd=Path(wrong)).stdout)
            self.assertEqual(Path(order["artifacts"]["source"]), source.resolve())

    def test_report_missing_field_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            h = Harness(Path(td))
            files = h.make_drafts()
            h.transition(1, "CAPTURED", {"source": files["source"]}); h.transition(1, "SOURCE_VERIFIED")
            h.transition(1, "DRAFTED", {k: files[k] for k in ("faithful", "lecture", "uncertainties", "coverage")})
            h.run("preflight", "--state", str(h.state), "--lesson", "1")
            qa = h.qa_report(1); data = json.loads(qa.read_text()); data.pop("reviewer_kind"); write_json(qa, data)
            rejected = h.transition(1, "SEMANTIC_QA_PASS", {"qa_report": qa}, expect=2)
            self.assertIn("missing fields", rejected.stderr)

    def test_audit_detects_old_qa_binding_and_formal_drift(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            h = Harness(Path(td)); files = h.accept()
            files["official_faithful"].write_text(files["official_faithful"].read_text() + "\nChanged after acceptance.\n", encoding="utf-8")
            result = json.loads(h.run("audit", "--state", str(h.state), expect=1).stdout)
            self.assertIn("qa_binding_mismatch", result["categories"])
            self.assertIn("formal_candidate_drift", result["categories"])

    def test_broken_source_backlink_is_detected(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            h = Harness(Path(td)); files = h.accept()
            text = files["official_lecture"].read_text().replace(str(files["source"].resolve()), "/missing/source.md")
            files["official_lecture"].write_text(text, encoding="utf-8")
            result = json.loads(h.run("audit", "--state", str(h.state), expect=1).stdout)
            self.assertIn("promotion_hygiene", result["categories"])

    def test_shared_course_map_uses_latest_baseline(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            h = Harness(Path(td), count=2)
            h.accept(1, "# Course Map\n\n- Lesson 1\n")
            h.accept(2, "# Course Map\n\n- Lesson 1\n- Lesson 2\n")
            result = json.loads(h.run("audit", "--state", str(h.state)).stdout)
            self.assertTrue(result["ok"], result)

    def test_revision_types_and_false_equivalence_guards(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            h = Harness(Path(td)); files = h.accept()
            # Metadata/link-only: a frontmatter-only edit closes deterministically.
            h.run("revision-open", "--state", str(h.state), "--lesson", "1", "--type", "metadata_link_only", "--reason", "metadata")
            original = files["official_faithful"].read_text()
            files["official_faithful"].write_text(
                original.replace(f"source: {files['source'].resolve()}\n", f"source: {files['source'].resolve()}\nstatus: accepted\n", 1),
                encoding="utf-8")
            report = h.revision_report(1, h.runtime / "metadata-revision.json")
            h.run("revision-close", "--state", str(h.state), "--lesson", "1", "--revision-report", str(report))
            self.assertTrue(json.loads(h.run("audit", "--state", str(h.state)).stdout)["ok"])

            # Formatting: whitespace-only edit has the same conservative fingerprint.
            h.run("revision-open", "--state", str(h.state), "--lesson", "1", "--type", "formatting", "--reason", "spacing")
            files["official_lecture"].write_text(files["official_lecture"].read_text().replace("\n## Method", "\n\n## Method"), encoding="utf-8")
            report = h.revision_report(1, h.runtime / "format-revision.json")
            h.run("revision-close", "--state", str(h.state), "--lesson", "1", "--revision-report", str(report))

            # A self-declared semantic-equivalence flag is never trusted.
            h.run("revision-open", "--state", str(h.state), "--lesson", "1", "--type", "formatting", "--reason", "fake")
            files["official_lecture"].write_text(files["official_lecture"].read_text() + "\n\nNew claim 99.\n", encoding="utf-8")
            fake = h.revision_report(1, h.runtime / "fake-revision.json", fake_equivalence=True)
            rejected = h.run("revision-close", "--state", str(h.state), "--lesson", "1", "--revision-report", str(fake), expect=2)
            self.assertIn("may not self-declare", rejected.stderr)

    def test_content_revision_requires_current_hash_bound_qa(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            h = Harness(Path(td)); files = h.accept()
            h.run("revision-open", "--state", str(h.state), "--lesson", "1", "--type", "content", "--reason", "correction")
            files["official_faithful"].write_text(files["official_faithful"].read_text() + "\nCorrected source-backed sentence.\n", encoding="utf-8")
            report = h.revision_report(1, h.runtime / "content-revision.json")
            missing = h.run("revision-close", "--state", str(h.state), "--lesson", "1", "--revision-report", str(report), expect=2)
            self.assertIn("requires independent", missing.stderr)
            state = h.state_data(); lesson = state["lessons"][0]
            current = json.loads(report.read_text())["new_sha256"]
            qa = h.qa_report(1, "revision_content", round_no=lesson["attempts"]["qa"] + 1,
                             hashes={k: v for k, v in current.items() if k != "course_map"},
                             path=h.runtime / "content-qa.json")
            wrong = json.loads(qa.read_text()); wrong["input_sha256"]["faithful"] = "0" * 64; write_json(qa, wrong)
            rejected = h.run("revision-close", "--state", str(h.state), "--lesson", "1", "--revision-report", str(report),
                             "--qa-report", str(qa), expect=2)
            self.assertIn("does not match reviewed artifacts", rejected.stderr)
            h.qa_report(1, "revision_content", round_no=lesson["attempts"]["qa"] + 1,
                        hashes={k: v for k, v in current.items() if k != "course_map"}, path=qa)
            h.run("revision-close", "--state", str(h.state), "--lesson", "1", "--revision-report", str(report),
                  "--qa-report", str(qa), "--tokens-used", "7", "--wall-minutes-used", "1", "--agent-calls", "1")
            self.assertTrue(json.loads(h.run("audit", "--state", str(h.state)).stdout)["ok"])
            usage = h.lesson()["usage"]
            self.assertEqual(usage["tokens"], sum(bucket["tokens"] for bucket in usage["phases"].values()))
            self.assertEqual(usage["agent_calls"], sum(bucket["agent_calls"] for bucket in usage["phases"].values()))

    def test_substantive_formatting_revision_requires_qa(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            h = Harness(Path(td)); files = h.accept()
            h.run("revision-open", "--state", str(h.state), "--lesson", "1", "--type", "formatting", "--reason", "claimed formatting")
            files["official_lecture"].write_text(files["official_lecture"].read_text() + "\nNew number 73.\n", encoding="utf-8")
            report = h.revision_report(1, h.runtime / "substantive-format.json")
            rejected = h.run("revision-close", "--state", str(h.state), "--lesson", "1",
                             "--revision-report", str(report), expect=2)
            self.assertIn("requires independent", rejected.stderr)

    def test_revision_open_is_an_audit_failure(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            h = Harness(Path(td)); h.accept()
            h.run("revision-open", "--state", str(h.state), "--lesson", "1", "--type", "metadata_link_only", "--reason", "open")
            result = json.loads(h.run("audit", "--state", str(h.state), expect=1).stdout)
            self.assertIn("revision_open", result["categories"])


if __name__ == "__main__":
    unittest.main()
