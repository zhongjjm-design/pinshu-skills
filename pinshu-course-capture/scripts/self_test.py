#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
PIPE = HERE / "course_pipeline.py"
VALIDATE = HERE / "validate_lesson.py"


def run(*args: str, expect: int = 0) -> subprocess.CompletedProcess:
    cp = subprocess.run([sys.executable, *args], text=True, capture_output=True)
    if cp.returncode != expect:
        raise AssertionError(f"command failed {args}: {cp.returncode}\n{cp.stdout}\n{cp.stderr}")
    return cp


def write_json(path: Path, data: object) -> None:
    path.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")


def transition(state: Path, lesson: int, target: str, artifacts: list[str] | None = None,
               severity: str | None = None, wall: str | None = None, tokens: str | None = None,
               expect: int = 0) -> subprocess.CompletedProcess:
    cmd = [str(PIPE), "transition", "--state", str(state), "--lesson", str(lesson),
           "--to", target, "--reason", "test"]
    if severity:
        cmd += ["--severity", severity]
    if wall is not None:
        cmd += ["--wall-minutes-used", wall]
    if tokens is not None:
        cmd += ["--tokens-used", tokens]
    for artifact in artifacts or []:
        cmd += ["--artifact", artifact]
    return run(*cmd, expect=expect)


def manifest(root: Path, course_id: str, count: int = 1, profile: str | None = "fast",
             gate_enabled: bool | None = None, output_language: str | None = "en-US") -> dict:
    data = {
        "schema_version": 1, "course_id": course_id, "course_title": "Test Course", "lecturer": "Lecturer",
        "course_root": str(root), "runtime_dir": str(root / f"{course_id}-runtime"), "source_adapter": "local",
        "course_purpose": ["systematic_learning"], "purpose_decision_basis": "Used for systematic learning",
        "assurance_mode": profile or "strict", "assurance_decision_basis": "Test selection",
        "optional_extensions": {"active_recall": True, "learning_training": True, "horizontal_topics": False},
        "external_use": {"enabled": False, "intended_uses": []},
        "intake_confirmation": {"confirmed": True, "confirmed_by": "test-user", "confirmed_at": "2026-09-24T00:00:00+08:00"},
        "budgets": {"max_reworks_per_lesson": 1, "max_qa_rounds_per_lesson": 2,
                    "max_tokens_per_lesson": 1000, "max_wall_minutes_per_lesson": 20},
        "sample_gate": {"lesson_no": 1, "approved": False},
        "path_templates": {"active_recall": "03_\u590d\u4e60/{filename}"},
        "writer_model": "cheap-a", "qa_model": "cheap-b", "strong_model": "strong",
        "gold_samples": [],
        "lessons": [{"lesson_no": n, "title": f"Lesson {n}", "source_video": f"{n}.mp4", "source_path": f"/{n}.mp4"}
                    for n in range(1, count + 1)],
    }
    if profile is not None:
        data["production_profile"] = profile
    if gate_enabled is not None:
        data["sample_gate"]["enabled"] = gate_enabled
    if output_language is not None:
        data["output_language"] = output_language
    return data


def lesson_input_hashes(state_path: Path, lesson_no: int = 1) -> dict[str, str]:
    state_data = json.loads(state_path.read_text(encoding="utf-8"))
    lesson = next(x for x in state_data["lessons"] if int(x["lesson_no"]) == lesson_no)
    return {k: v for k, v in lesson.get("artifact_sha256", {}).items() if k in {"source", "faithful", "lecture", "uncertainties", "coverage"}}


def qa_report(path: Path, decision: str, round_no: int, scope: str, issues: list[dict] | None = None,
              course_id: str = "test", input_sha256: dict[str, str] | None = None,
              reviewer_model: str = "cheap-b", profile: str = "fast") -> None:
    write_json(path, {
        "schema_version": 1, "course_id": course_id, "lesson_no": 1,
        "reviewer_model": reviewer_model, "production_profile": profile,
        "review_round": round_no, "review_scope": scope, "decision": decision,
        "recommended_state": {"pass": "SEMANTIC_QA_PASS", "fix_required": "FIX_REQUIRED", "escalated": "ESCALATED"}[decision],
        "source_identity": {"passed": decision == "pass", "notes": []},
        "coverage": {"passed": decision == "pass", "opening_checked": True, "middle_checked": True,
                     "ending_checked": True, "longest_case_checked": True, "high_risk_anchors_checked": True},
        "input_sha256": input_sha256 or {},
        "issues": issues or [], "notes": [], "requires_strong_model": decision == "escalated",
    })


def main() -> int:
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        raw = root / "raw.md"; faithful = root / "faithful.md"; lecture = root / "lecture.md"
        coverage = root / "coverage.json"; uncertainties = root / "uncertainties.json"
        mech = root / "mechanical.json"; qa = root / "qa.json"
        for p, text in ((raw, "The lecturer's source statement. A case and conclusion."),
                        (faithful, "# Lesson One\n\nThe lecturer's source statement. A case and conclusion."),
                        (lecture, "# Structured Lecture\n\n## Method\n\nA case and conclusion.")):
            p.write_text(text, encoding="utf-8")
        write_json(coverage, {"block_count": 1, "status_summary": {"retained": 1, "merged": 0, "noise": 0, "uncertain": 0},
                              "blocks": [{"id": "B01", "status": "retained"}]})
        write_json(uncertainties, {"confirmed_corrections": [], "variants": [], "unresolved": [],
                                   "summary": {"confirmed_corrections": 0, "variant_entries": 0, "unresolved": 0}})

        # Happy path: optional fast coverage, validated QA report, immutable sample hashes, safe archive.
        manifest_path = root / "manifest.json"; state = root / "state.json"
        write_json(manifest_path, manifest(root, "test"))
        run(str(PIPE), "init", "--manifest", str(manifest_path), "--state", str(state))
        agreement = json.loads(run(str(PIPE), "agreement", "--state", str(state)).stdout)
        assert agreement["course_purpose"][0]["label"] == "Systematic learning/review"
        assert agreement["fixed_outputs"] == ["Source transcript", "Faithful edit", "Structured lecture", "Course map"]
        assert agreement["assurance"]["label"] == "Lightweight evidence"
        assert agreement["output_language"] == "en-US"
        assert agreement["output_language_defaulted"] is False
        assert agreement["intake_confirmation"]["confirmed"] is True
        generated = json.loads(run(str(PIPE), "paths", "--state", str(state), "--lesson", "1").stdout)
        assert generated["paths"]["official_faithful"].endswith("01_\u5fe0\u5b9e\u7cbe\u7f16\u7a3f/\u7b2c01\u8bfe\u00b7Lesson 1.md")
        assert generated["paths"]["active_recall"].endswith("03_\u590d\u4e60/\u7b2c01\u8bfe\u00b7Lesson 1.md")
        assert json.loads(run(str(PIPE), "summary", "--state", str(state)).stdout)["output_language"] == "en-US"

        # Public example renders English paths; legacy defaults above remain unchanged.
        example = json.loads((HERE.parent / "templates/course-manifest.example.json").read_text(encoding="utf-8"))
        example["course_root"] = str(root / "example-course")
        example["runtime_dir"] = str(root / "example-runtime")
        example["intake_confirmation"] = {"confirmed": True, "confirmed_by": "test-user", "confirmed_at": "2026-09-24T00:00:00+08:00"}
        example["writer_model"] = "test-writer"
        example["qa_model"] = "test-reviewer"
        example_manifest = root / "example-manifest.json"; example_state = root / "example-state.json"
        write_json(example_manifest, example)
        run(str(PIPE), "init", "--manifest", str(example_manifest), "--state", str(example_state))
        example_paths = json.loads(run(str(PIPE), "paths", "--state", str(example_state), "--lesson", "1").stdout)["paths"]
        assert example_paths["source"].endswith("00_Source_Transcripts/Lesson-01-Official Title.md")
        assert example_paths["course_map"].endswith("00_Course_Map.md")
        assert example_paths["active_recall"].endswith("03_Review_and_Practice/01_Active_Recall/Lesson-01-Official Title.md")
        assert example_paths["learning_progress"].endswith("04_Learning_Records/00_Progress.md")
        missing = transition(state, 1, "CAPTURED", expect=2)
        assert "missing artifact key source" in missing.stderr
        transition(state, 1, "CAPTURED", [f"source={raw}"])
        transition(state, 1, "SOURCE_VERIFIED")
        no_usage = transition(state, 1, "DRAFTED", [f"faithful={faithful}", f"lecture={lecture}", f"uncertainties={uncertainties}"], expect=2)
        assert "requires --wall-minutes-used" in no_usage.stderr
        transition(state, 1, "DRAFTED", [f"faithful={faithful}", f"lecture={lecture}", f"uncertainties={uncertainties}"], wall="1", tokens="100")
        run(str(VALIDATE), "--profile", "fast", "--source", str(raw), "--faithful", str(faithful), "--lecture", str(lecture),
            "--uncertainties", str(uncertainties), "--json-out", str(mech))
        bad_coverage_data = {"block_count": 9, "status_summary": {"retained": 9}, "blocks": [{"id": "B01", "status": "retained"}]}
        write_json(coverage, bad_coverage_data)
        bad_coverage = run(str(VALIDATE), "--profile", "strict", "--source", str(raw), "--faithful", str(faithful), "--lecture", str(lecture),
                           "--coverage", str(coverage), "--uncertainties", str(uncertainties), expect=1)
        assert "coverage.block_count mismatch" in bad_coverage.stdout
        write_json(coverage, {"block_count": 1, "status_summary": {"retained": 1, "merged": 0, "noise": 0, "uncertain": 0},
                              "blocks": [{"id": "B01", "status": "retained"}]})
        transition(state, 1, "MECHANICAL_PASS", [f"mechanical_report={mech}"])
        empty_qa = root / "empty-qa.json"; write_json(empty_qa, {})
        invalid_qa = transition(state, 1, "SEMANTIC_QA_PASS", [f"qa_report={empty_qa}"], wall="1", expect=2)
        assert "qa_report" in invalid_qa.stderr
        note_rework = transition(state, 1, "FIX_REQUIRED", [f"qa_report={empty_qa}"], severity="note", wall="1", expect=2)
        assert "requires --severity high" in note_rework.stderr
        qa_report(qa, "pass", 1, "full", input_sha256=lesson_input_hashes(state))
        transition(state, 1, "SEMANTIC_QA_PASS", [f"qa_report={qa}"], wall="1", tokens="50")
        official_f = Path(generated["paths"]["official_faithful"])
        official_l = Path(generated["paths"]["official_lecture"])
        course_map = Path(generated["paths"]["course_map"])
        for path in (official_f, official_l, course_map):
            path.parent.mkdir(parents=True, exist_ok=True)
        official_f.write_text(faithful.read_text(encoding="utf-8"), encoding="utf-8")
        official_l.write_text(lecture.read_text(encoding="utf-8"), encoding="utf-8")
        course_map.write_text("# Course Map\n\n- Lesson 1\n", encoding="utf-8")
        transition(state, 1, "PROMOTED", [f"official_faithful={official_f}", f"official_lecture={official_l}"])
        transition(state, 1, "ACCEPTED", [f"course_map={course_map}"])
        assert json.loads(run(str(PIPE), "audit", "--state", str(state)).stdout)["ok"] is True
        mismatch = run(str(PIPE), "approve-sample", "--state", str(state), "--lesson", "999", "--faithful", str(official_f),
                       "--lecture", str(official_l), "--approved-by", "test-user", expect=2)
        assert "sample lesson mismatch" in mismatch.stderr
        arbitrary = root / "arbitrary.md"; arbitrary.write_text("x", encoding="utf-8")
        bad_paths = run(str(PIPE), "approve-sample", "--state", str(state), "--lesson", "1", "--faithful", str(arbitrary),
                        "--lecture", str(official_l), "--approved-by", "test-user", expect=2)
        assert "must match" in bad_paths.stderr
        run(str(PIPE), "approve-sample", "--state", str(state), "--lesson", "1", "--faithful", str(official_f),
            "--lecture", str(official_l), "--approved-by", "test-user")
        qa_archive = run(str(PIPE), "archive-artifact", "--state", str(state), "--lesson", "1", "--key", "qa_report",
                         "--sha256", hashlib.sha256(qa.read_bytes()).hexdigest(), "--reason", "must reject", expect=2)
        assert "cannot be archived" in qa_archive.stderr
        digest = hashlib.sha256(mech.read_bytes()).hexdigest()
        run(str(PIPE), "archive-artifact", "--state", str(state), "--lesson", "1", "--key", "mechanical_report",
            "--sha256", digest, "--reason", "test cleanup")
        mech.unlink()
        assert json.loads(run(str(PIPE), "audit", "--state", str(state)).stdout)["ok"] is True

        # Unconfirmed or unsupported intake decisions are rejected before initialization.
        invalid_manifest = root / "invalid-intake.json"
        invalid_state = root / "invalid-intake-state.json"
        invalid = manifest(root, "invalid-intake")
        invalid["intake_confirmation"]["confirmed"] = False
        write_json(invalid_manifest, invalid)
        rejected = run(str(PIPE), "init", "--manifest", str(invalid_manifest), "--state", str(invalid_state), expect=2)
        assert "must be confirmed" in rejected.stderr
        invalid = manifest(root, "invalid-purpose")
        invalid["course_purpose"] = ["unknown"]
        write_json(invalid_manifest, invalid)
        rejected = run(str(PIPE), "init", "--manifest", str(invalid_manifest), "--state", str(invalid_state), expect=2)
        assert "course_purpose" in rejected.stderr

        # A four-lesson batch cannot disable the sample gate.
        gate_manifest = root / "gate-manifest.json"; gate_state = root / "gate-state.json"
        write_json(gate_manifest, manifest(root, "gate", count=4, gate_enabled=False))
        run(str(PIPE), "init", "--manifest", str(gate_manifest), "--state", str(gate_state))
        gate_data = json.loads(gate_state.read_text(encoding="utf-8"))
        assert gate_data["sample_gate"]["enabled"] is True
        transition(gate_state, 2, "CAPTURED", [f"source={raw}"])
        transition(gate_state, 2, "SOURCE_VERIFIED")
        gate_block = transition(gate_state, 2, "DRAFTED", [f"faithful={faithful}", f"lecture={lecture}", f"uncertainties={uncertainties}"], wall="1", expect=2)
        assert "sample gate is not approved" in gate_block.stderr

        # Legacy manifests default to strict rather than silently downgrading to fast.
        legacy_manifest = root / "legacy-manifest.json"; legacy_state = root / "legacy-state.json"
        write_json(legacy_manifest, manifest(root, "legacy", profile=None, output_language=None))
        run(str(PIPE), "init", "--manifest", str(legacy_manifest), "--state", str(legacy_state))
        legacy_data = json.loads(legacy_state.read_text(encoding="utf-8"))
        assert legacy_data["production"]["profile"] == "strict"
        assert legacy_data["production"]["output_language"] == "match-user"
        assert legacy_data["production"]["output_language_defaulted"] is True
        legacy_agreement = json.loads(run(str(PIPE), "agreement", "--state", str(legacy_state)).stdout)
        assert legacy_agreement["output_language"] == "match-user"

        # Unsafe or overlong language values are rejected rather than normalized.
        for bad_language in ("../../en", "english", "en_US", "x" * 36):
            invalid_language_manifest = root / f"invalid-language-{len(bad_language)}.json"
            invalid_language_state = root / f"invalid-language-{len(bad_language)}-state.json"
            bad_data = manifest(root, f"bad-language-{len(bad_language)}", output_language=bad_language)
            write_json(invalid_language_manifest, bad_data)
            rejected = run(str(PIPE), "init", "--manifest", str(invalid_language_manifest),
                           "--state", str(invalid_language_state), expect=2)
            assert "output_language" in rejected.stderr

        # Persistent high-severity failure can always escalate after the bounded second QA.
        fail_manifest = root / "fail-manifest.json"; fail_state = root / "fail-state.json"
        fail_mech = root / "fail-mechanical.json"
        fail_data = manifest(root, "fail")
        fail_data["budgets"]["max_agent_calls_per_lesson"] = 10
        write_json(fail_manifest, fail_data)
        run(str(PIPE), "init", "--manifest", str(fail_manifest), "--state", str(fail_state))
        transition(fail_state, 1, "CAPTURED", [f"source={raw}"])
        transition(fail_state, 1, "SOURCE_VERIFIED")
        transition(fail_state, 1, "DRAFTED", [f"faithful={faithful}", f"lecture={lecture}", f"uncertainties={uncertainties}"], wall="1")
        run(str(VALIDATE), "--profile", "fast", "--source", str(raw), "--faithful", str(faithful), "--lecture", str(lecture),
            "--uncertainties", str(uncertainties), "--json-out", str(fail_mech))
        transition(fail_state, 1, "MECHANICAL_PASS", [f"mechanical_report={fail_mech}"])
        high_issue = [{"severity": "high", "type": "omission", "source_quote": "Evidence", "required_fix": "Restore it"}]
        qa_report(qa, "fix_required", 1, "full", high_issue, course_id="fail", input_sha256=lesson_input_hashes(fail_state))
        transition(fail_state, 1, "FIX_REQUIRED", [f"qa_report={qa}"], severity="high", wall="1")
        transition(fail_state, 1, "DRAFTED", wall="1")
        transition(fail_state, 1, "MECHANICAL_PASS")
        qa_report(qa, "fix_required", 2, "targeted_recheck", high_issue, course_id="fail", input_sha256=lesson_input_hashes(fail_state))
        transition(fail_state, 1, "FIX_REQUIRED", [f"qa_report={qa}"], severity="high", wall="1")
        transition(fail_state, 1, "ESCALATED")

    print("self_test: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
