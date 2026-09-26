#!/usr/bin/env python3
"""State manager for pinshu-course-capture runtime projects.

This script never calls a model and never edits course prose. It owns deterministic
state transitions, atomic persistence, next-work selection, and artifact audits.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import sys
import tempfile
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

SCHEMA_VERSION = 1
MAIN_FLOW = [
    "DISCOVERED", "CAPTURED", "SOURCE_VERIFIED", "DRAFTED",
    "MECHANICAL_PASS", "SEMANTIC_QA_PASS", "PROMOTED", "ACCEPTED",
]
EXCEPTION_STATES = {"FIX_REQUIRED", "ESCALATED", "BLOCKED", "SKIPPED"}
ALL_STATES = set(MAIN_FLOW) | EXCEPTION_STATES

ALLOWED = {
    "DISCOVERED": {"CAPTURED", "BLOCKED", "SKIPPED"},
    "CAPTURED": {"SOURCE_VERIFIED", "BLOCKED"},
    "SOURCE_VERIFIED": {"DRAFTED", "BLOCKED"},
    "DRAFTED": {"MECHANICAL_PASS", "FIX_REQUIRED", "BLOCKED"},
    "MECHANICAL_PASS": {"SEMANTIC_QA_PASS", "FIX_REQUIRED", "ESCALATED", "BLOCKED"},
    "SEMANTIC_QA_PASS": {"PROMOTED", "FIX_REQUIRED", "ESCALATED"},
    "PROMOTED": {"ACCEPTED", "FIX_REQUIRED", "BLOCKED"},
    "FIX_REQUIRED": {"DRAFTED", "ESCALATED", "BLOCKED"},
    "ESCALATED": {"DRAFTED", "BLOCKED", "SKIPPED"},
    "BLOCKED": {"DISCOVERED", "CAPTURED", "SOURCE_VERIFIED", "SKIPPED"},
    "SKIPPED": set(),
    "ACCEPTED": set(),
}

REQUIRED_MANIFEST = {
    "schema_version", "course_id", "course_title", "lecturer",
    "course_root", "runtime_dir", "source_adapter", "writer_model",
    "qa_model", "strong_model", "gold_samples", "lessons",
    "course_purpose", "purpose_decision_basis", "assurance_mode",
    "assurance_decision_basis", "optional_extensions", "external_use",
    "intake_confirmation",
}
PROFILES = {"fast", "standard", "strict"}
COURSE_PURPOSES = {
    "reference_archive", "systematic_learning", "training_certification",
    "practical_application", "content_asset",
}
PURPOSE_LABELS = {
    "reference_archive": "Reference/archive",
    "systematic_learning": "Systematic learning/review",
    "training_certification": "Training/certification/exam preparation",
    "practical_application": "Method transfer/real project",
    "content_asset": "Content asset/internal reuse",
}
ASSURANCE_LABELS = {"fast": "Lightweight evidence", "standard": "Standard evidence", "strict": "Full evidence"}
OPTIONAL_EXTENSION_KEYS = {"active_recall", "learning_training", "horizontal_topics"}
EXTERNAL_USE_CASES = {"publication", "public_content", "paid_course", "client_delivery", "academic", "real_decision"}
FIXED_OUTPUTS = ["Source transcript", "Faithful edit", "Structured lecture", "Course map"]
ALLOWED_OVERRIDE_KEYS = {"assurance_mode", "production_profile", "force_independent_qa", "external_use", "risk_flags", "adapters", "budgets"}
OUTPUT_LANGUAGE_SELECTORS = {"match-user", "match-source"}
OUTPUT_LANGUAGE_RE = re.compile(r"^[A-Za-z]{2,3}(?:-[A-Za-z0-9]{2,8}){0,2}$")
ALLOWED_RISK_FLAGS = {
    "source_identity", "source_incomplete", "severe_stt", "high_risk_content",
    "high_consequence_operation", "medical", "legal", "financial", "safety",
    "multi_speaker_conflict", "visual_evidence", "code_or_command", "key_number_conflict",
    "mechanical_semantic_warning", "recent_repeated_high",
}
BUDGET_KEYS = {"max_tokens_per_lesson", "max_wall_minutes_per_lesson", "max_agent_calls_per_lesson", "max_reworks_per_lesson", "max_qa_rounds_per_lesson"}


def now() -> str:
    return datetime.now(timezone.utc).isoformat()


def load_json(path: Path) -> dict:
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def atomic_write(path: Path, data: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(prefix=path.name + ".", dir=str(path.parent))
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
            f.write("\n")
            f.flush()
            os.fsync(f.fileno())
        os.replace(tmp, path)
    finally:
        if os.path.exists(tmp):
            os.unlink(tmp)


def resolved_course_profile(m: dict) -> str:
    return m.get("assurance_mode", m.get("production_profile", "strict"))


def resolved_output_language(m: dict) -> str:
    """Return the validated output-language policy, preserving explicit tags."""
    return m.get("output_language", "match-user")


def validate_output_language(value: object) -> None:
    if not isinstance(value, str) or len(value) > 35:
        raise ValueError("output_language must be a short BCP-47 tag, match-user, or match-source")
    if value not in OUTPUT_LANGUAGE_SELECTORS and not OUTPUT_LANGUAGE_RE.fullmatch(value):
        raise ValueError("output_language must be a short BCP-47 tag, match-user, or match-source")


def validate_positive_int(name: str, value: object) -> None:
    if isinstance(value, bool) or not isinstance(value, int) or value <= 0:
        raise ValueError(f"budget {name} must be a positive integer: {value}")


def validate_manifest(m: dict) -> None:
    missing = REQUIRED_MANIFEST - set(m)
    if missing:
        raise ValueError("manifest missing fields: " + ", ".join(sorted(missing)))
    if m["schema_version"] != SCHEMA_VERSION:
        raise ValueError(f"unsupported schema_version: {m['schema_version']}")
    validate_output_language(resolved_output_language(m))
    purposes = m.get("course_purpose")
    if (not isinstance(purposes, list) or not purposes or len(purposes) != len(set(purposes))
            or any(x not in COURSE_PURPOSES for x in purposes)):
        raise ValueError("course_purpose must be a non-empty unique list of supported purposes")
    for key in ("purpose_decision_basis", "assurance_decision_basis"):
        if not isinstance(m.get(key), str) or not m[key].strip():
            raise ValueError(f"{key} must explain the recommendation")
    extensions = m.get("optional_extensions")
    if (not isinstance(extensions, dict) or set(extensions) - OPTIONAL_EXTENSION_KEYS
            or any(not isinstance(v, bool) for v in extensions.values())):
        raise ValueError("optional_extensions must contain only supported boolean flags")
    external = m.get("external_use")
    if not isinstance(external, dict) or not isinstance(external.get("enabled"), bool):
        raise ValueError("external_use.enabled must be boolean")
    intended = external.get("intended_uses", [])
    if (not isinstance(intended, list) or len(intended) != len(set(intended))
            or any(x not in EXTERNAL_USE_CASES for x in intended)):
        raise ValueError("external_use.intended_uses contains unsupported values")
    if external["enabled"] and not intended:
        raise ValueError("external use requires at least one intended_uses value")
    confirmation = m.get("intake_confirmation")
    if (not isinstance(confirmation, dict) or confirmation.get("confirmed") is not True
            or not str(confirmation.get("confirmed_by", "")).strip()
            or not str(confirmation.get("confirmed_at", "")).strip()):
        raise ValueError("course production agreement must be confirmed before init")
    profile = resolved_course_profile(m)
    if profile not in PROFILES:
        raise ValueError(f"unknown assurance_mode: {profile}")
    if m.get("assurance_mode") and m.get("production_profile") and m["assurance_mode"] != m["production_profile"]:
        print("warning: assurance_mode overrides conflicting production_profile", file=sys.stderr)
    budgets = m.get("budgets", {})
    unknown_budgets = set(budgets) - BUDGET_KEYS
    if unknown_budgets:
        raise ValueError("unknown budget fields: " + ", ".join(sorted(unknown_budgets)))
    for key, value in budgets.items():
        validate_positive_int(key, value)
    path_templates = m.get("path_templates", {})
    if not isinstance(path_templates, dict):
        raise ValueError("path_templates must be an object")
    for key, value in path_templates.items():
        if not isinstance(key, str) or not re.fullmatch(r"[a-z][a-z0-9_]*", key):
            raise ValueError(f"invalid path template key: {key}")
        if not isinstance(value, str) or not value.strip():
            raise ValueError(f"path template must be a non-empty string: {key}")
    if not isinstance(m["lessons"], list) or not m["lessons"]:
        raise ValueError("manifest lessons must be a non-empty list")
    seen = set()
    for lesson in m["lessons"]:
        for key in ("lesson_no", "title", "source_video", "source_path"):
            if key not in lesson:
                raise ValueError(f"lesson missing field {key}: {lesson}")
        no = int(lesson["lesson_no"])
        if no in seen:
            raise ValueError(f"duplicate lesson_no: {no}")
        seen.add(no)
        overrides = lesson.get("overrides", {})
        if not isinstance(overrides, dict):
            raise ValueError(f"lesson overrides must be an object: {no}")
        unknown = set(overrides) - ALLOWED_OVERRIDE_KEYS
        if unknown:
            raise ValueError(f"lesson {no} has unknown override fields: {sorted(unknown)}")
        if overrides and not str(lesson.get("override_reason", "")).strip():
            raise ValueError(f"lesson {no} overrides require override_reason")
        override_profile = overrides.get("assurance_mode", overrides.get("production_profile", profile))
        if override_profile not in PROFILES:
            raise ValueError(f"lesson {no} has unknown assurance mode: {override_profile}")
        flags = overrides.get("risk_flags", [])
        if not isinstance(flags, list) or any(x not in ALLOWED_RISK_FLAGS for x in flags):
            raise ValueError(f"lesson {no} has unknown risk_flags")
        override_budgets = overrides.get("budgets", {})
        if set(override_budgets) - BUDGET_KEYS:
            raise ValueError(f"lesson {no} has unknown budget fields")
        for key, value in override_budgets.items():
            validate_positive_int(key, value)


def effective_policy(m: dict, item: dict, base_budgets: dict) -> dict:
    overrides = item.get("overrides", {})
    profile = overrides.get("assurance_mode", overrides.get("production_profile", resolved_course_profile(m)))
    budgets = dict(base_budgets)
    budgets.update(overrides.get("budgets", {}))
    external_default = bool(m.get("external_use", {}).get("enabled", False))
    adapters = dict(m.get("adapters", {"domain": ["generic"], "content": ["talk"]}))
    adapters.update(overrides.get("adapters", {}))
    return {
        "assurance_mode": profile,
        "force_independent_qa": bool(overrides.get("force_independent_qa", False)),
        "external_use": bool(overrides.get("external_use", external_default)),
        "risk_flags": list(overrides.get("risk_flags", [])),
        "adapters": adapters,
        "budgets": budgets,
        "override_reason": item.get("override_reason"),
    }


def initial_state(m: dict) -> dict:
    created = now()
    default_budgets = {
        "max_tokens_per_lesson": 300000,
        "max_wall_minutes_per_lesson": 20,
        "max_agent_calls_per_lesson": 3,
        "max_reworks_per_lesson": 1,
        "max_qa_rounds_per_lesson": 2,
    }
    default_budgets.update(m.get("budgets", {}))
    lessons = []
    for item in sorted(m["lessons"], key=lambda x: int(x["lesson_no"])):
        lessons.append({
            "lesson_no": int(item["lesson_no"]),
            "title": item["title"],
            "source_video": item["source_video"],
            "source_path": item["source_path"],
            "effective_policy": effective_policy(m, item, default_budgets),
            "status": "DISCOVERED",
            "attempts": {"capture": 0, "draft": 0, "qa": 0, "rework": 0, "strong_adjudication": 0},
            "usage": {"tokens": 0, "wall_minutes": 0.0, "agent_calls": 0},
            "artifacts": {},
            "artifact_sha256": {},
            "last_reason": "initialized",
            "updated_at": created,
            "history": [{"at": created, "from": None, "to": "DISCOVERED", "reason": "initialized"}],
        })
    sample_gate = dict(m.get("sample_gate", {"lesson_no": lessons[0]["lesson_no"], "approved": False}))
    sample_gate.setdefault("lesson_no", lessons[0]["lesson_no"])
    sample_gate.setdefault("approved", False)
    sample_gate["enabled"] = len(lessons) > 3
    if int(sample_gate["lesson_no"]) not in {x["lesson_no"] for x in lessons}:
        raise ValueError("sample_gate.lesson_no is not in lessons")
    return {
        "schema_version": SCHEMA_VERSION,
        "course_id": m["course_id"],
        "course_title": m["course_title"],
        "lecturer": m["lecturer"],
        "course_root": m["course_root"],
        "runtime_dir": m["runtime_dir"],
        "source_adapter": m["source_adapter"],
        "production": {
            "profile": resolved_course_profile(m),
            "assurance_label": ASSURANCE_LABELS[resolved_course_profile(m)],
            "assurance_decision_basis": m["assurance_decision_basis"],
            "course_purpose": list(m["course_purpose"]),
            "purpose_decision_basis": m["purpose_decision_basis"],
            "intake_confirmation": dict(m["intake_confirmation"]),
            "budgets": default_budgets,
            "adapters": m.get("adapters", {"domain": ["generic"], "content": ["talk"]}),
            "external_use": m["external_use"],
            "optional_extensions": m["optional_extensions"],
            "output_language": resolved_output_language(m),
            "output_language_defaulted": "output_language" not in m,
            "naming_template": m.get("naming_template", "\u7b2c{lesson_no:02d}\u8bfe\u00b7{title}.md"),
            "path_templates": m.get("path_templates", {
                "source": "00_\u539f\u59cb\u8f6c\u5199/{filename}",
                "official_faithful": "01_\u5fe0\u5b9e\u7cbe\u7f16\u7a3f/{filename}",
                "official_lecture": "02_\u7ed3\u6784\u5316\u8bb2\u4e49/{filename}",
                "course_map": "00_\u8bfe\u7a0b\u5730\u56fe.md",
            }),
        },
        "sample_gate": sample_gate,
        "models": {"writer": m["writer_model"], "qa": m["qa_model"], "strong": m["strong_model"]},
        "gold_samples": m["gold_samples"],
        "created_at": created,
        "updated_at": created,
        "lessons": lessons,
    }


def state_profile(state: dict, lesson: dict | None = None) -> str:
    if lesson:
        return lesson.get("effective_policy", {}).get("assurance_mode", state.get("production", {}).get("profile", "strict"))
    return state.get("production", {}).get("profile", "strict")


def sample_gate_valid(state: dict) -> bool:
    gate = state.get("sample_gate", {})
    if not gate.get("enabled", False):
        return True
    if not gate.get("approved", False):
        return False
    samples = [Path(x) for x in state.get("gold_samples", [])]
    hashes = gate.get("sample_sha256", {})
    return (
        len(samples) == 2
        and all(p.is_file() for p in samples)
        and hashes.get("faithful") == sha256_file(samples[0])
        and hashes.get("lecture") == sha256_file(samples[1])
    )


def qa_scope_for(state: dict, lesson: dict, review_round: int) -> str:
    if review_round > 1 or lesson.get("strong_adjudication_pending", False):
        return "targeted_recheck"
    profile = state_profile(state, lesson)
    ordered = sorted(state["lessons"], key=lambda x: int(x["lesson_no"]))
    sample_no = int(state.get("sample_gate", {}).get("lesson_no", ordered[0]["lesson_no"]))
    policy = lesson.get("effective_policy", {})
    if profile == "strict" or int(lesson["lesson_no"]) == sample_no:
        return "full"
    if policy.get("force_independent_qa") or policy.get("external_use") or policy.get("risk_flags"):
        return "full"
    digest = int(hashlib.sha256(f"{state.get('course_id')}:{lesson['lesson_no']}".encode()).hexdigest()[:8], 16)
    if profile == "standard" and digest % 2 == 0:
        return "full"
    if profile == "fast" and digest % 5 == 0:
        return "full"
    return "writer_self_check"


def requires_full_qa(state: dict, lesson: dict, review_round: int) -> bool:
    return qa_scope_for(state, lesson, review_round) == "full"


def bound_input_hashes(lesson: dict) -> dict[str, str]:
    hashes = lesson.get("artifact_sha256", {})
    return {k: hashes[k] for k in ("source", "faithful", "lecture", "uncertainties", "coverage") if k in hashes}


def verify_bound_artifacts(lesson: dict, keys: tuple[str, ...] | None = None) -> None:
    expected = lesson.get("artifact_sha256", {})
    for key in keys or tuple(expected):
        if key not in expected:
            continue
        value = lesson.get("artifacts", {}).get(key)
        if not value or not Path(value).is_file() or sha256_file(Path(value)) != expected[key]:
            raise ValueError(f"artifact integrity failed {key}")


def validate_input_hashes(data: dict, lesson: dict) -> None:
    declared = data.get("input_sha256")
    expected = bound_input_hashes(lesson)
    if not isinstance(declared, dict) or any(declared.get(k) != v for k, v in expected.items()):
        raise ValueError("report input_sha256 does not match reviewed artifacts")


def validate_mechanical_report(path: Path, state: dict, lesson: dict) -> None:
    data = load_json(path)
    if data.get("schema_version") != 1 or data.get("mechanical_pass") is not True:
        raise ValueError("mechanical_report must be a passing schema_version 1 report")
    if data.get("semantic_pass") is not None or data.get("errors") not in ([], None):
        raise ValueError("mechanical_report has invalid semantic_pass or errors")
    if data.get("profile") != state_profile(state, lesson):
        raise ValueError("mechanical_report profile mismatch")
    validate_input_hashes(data, lesson)


def validate_semantic_check(path: Path, state: dict, lesson: dict) -> None:
    data = load_json(path)
    if data.get("schema_version") != 1 or data.get("reviewer_kind") != "writer_self_check":
        raise ValueError("semantic_check must be a writer_self_check schema_version 1 report")
    if data.get("course_id") != state.get("course_id") or int(data.get("lesson_no", 0)) != int(lesson["lesson_no"]):
        raise ValueError("semantic_check course_id or lesson_no mismatch")
    if data.get("reviewer_model") != state.get("models", {}).get("writer"):
        raise ValueError("semantic_check reviewer_model mismatch")
    if data.get("assurance_mode", data.get("production_profile")) != state_profile(state, lesson):
        raise ValueError("semantic_check assurance_mode mismatch")
    if data.get("decision") != "pass" or data.get("recommended_state") != "SEMANTIC_QA_PASS":
        raise ValueError("semantic_check must recommend SEMANTIC_QA_PASS")
    if data.get("high_issues") not in ([], None):
        raise ValueError("semantic_check cannot pass with high issues")
    coverage = data.get("coverage")
    if not isinstance(coverage, dict) or coverage.get("passed") is not True:
        raise ValueError("semantic_check requires passing coverage evidence")
    for key in ("opening_checked", "middle_checked", "ending_checked", "high_risk_anchors_checked"):
        if coverage.get(key) is not True:
            raise ValueError("semantic_check requires opening/middle/ending/high-risk evidence")
    validate_input_hashes(data, lesson)


def validate_qa_report(path: Path, state: dict, lesson: dict, new_state: str) -> None:
    data = load_json(path)
    expected_decision = {
        "SEMANTIC_QA_PASS": "pass", "FIX_REQUIRED": "fix_required", "ESCALATED": "escalated",
    }[new_state]
    expected_round = int(lesson.get("attempts", {}).get("qa", 0)) + 1
    if data.get("course_id") != state.get("course_id") or int(data.get("lesson_no", 0)) != int(lesson["lesson_no"]):
        raise ValueError("qa_report course_id or lesson_no mismatch")
    if data.get("decision") != expected_decision:
        raise ValueError(f"qa_report decision must be {expected_decision}")
    if data.get("recommended_state") != new_state:
        raise ValueError("qa_report recommended_state mismatch")
    if data.get("production_profile", data.get("assurance_mode")) != state_profile(state, lesson):
        raise ValueError("qa_report assurance mode mismatch")
    if int(data.get("review_round", 0)) != expected_round:
        raise ValueError(f"qa_report review_round must be {expected_round}")
    strong_recovery = bool(lesson.get("strong_adjudication_pending", False))
    reviewer = data.get("reviewer_model")
    expected_reviewer = state.get("models", {}).get("strong" if strong_recovery else "qa")
    if reviewer != expected_reviewer:
        raise ValueError("qa_report reviewer_model mismatch")
    scope = data.get("review_scope")
    if expected_round > 1:
        if scope != "targeted_recheck":
            raise ValueError("second QA round must use targeted_recheck")
    elif requires_full_qa(state, lesson, expected_round):
        if scope != "full":
            raise ValueError("this lesson requires full QA")
    elif scope not in {"sampled", "full"}:
        raise ValueError("review_scope must be sampled or full")
    issues = data.get("issues")
    if not isinstance(issues, list) or any(not isinstance(x, dict) for x in issues):
        raise ValueError("qa_report issues must be a list of objects")
    allowed_severities = {"high", "note"}
    if any(x.get("severity") not in allowed_severities for x in issues):
        raise ValueError("qa_report issue severity must be high or note")
    high = [x for x in issues if x.get("severity") == "high"]
    if any(not x.get("source_quote") or not x.get("required_fix") for x in high):
        raise ValueError("high issues require source_quote and required_fix")
    source_identity = data.get("source_identity")
    coverage = data.get("coverage")
    if not isinstance(source_identity, dict) or not isinstance(coverage, dict):
        raise ValueError("qa_report requires source_identity and coverage objects")
    if new_state == "SEMANTIC_QA_PASS" and (source_identity.get("passed") is not True or coverage.get("passed") is not True):
        raise ValueError("passing QA requires source_identity.passed and coverage.passed")
    if new_state == "SEMANTIC_QA_PASS" and scope == "full":
        required_checks = ("opening_checked", "middle_checked", "ending_checked", "longest_case_checked", "high_risk_anchors_checked")
        if any(coverage.get(k) is not True for k in required_checks):
            raise ValueError("full QA requires all coverage evidence fields")
    if new_state == "SEMANTIC_QA_PASS" and scope == "sampled":
        required_checks = ("opening_checked", "middle_checked", "ending_checked", "high_risk_anchors_checked")
        if any(coverage.get(k) is not True for k in required_checks):
            raise ValueError("sampled QA requires opening/middle/ending/high-risk evidence")
    if new_state == "SEMANTIC_QA_PASS" and high:
        raise ValueError("qa_report cannot pass with unresolved high issues")
    if new_state == "FIX_REQUIRED" and not high:
        raise ValueError("fix_required requires at least one high issue")
    validate_input_hashes(data, lesson)


def get_lesson(state: dict, no: int) -> dict:
    for lesson in state["lessons"]:
        if int(lesson["lesson_no"]) == no:
            return lesson
    raise ValueError(f"lesson not found: {no}")


def cmd_init(args: argparse.Namespace) -> int:
    manifest_path, state_path = Path(args.manifest), Path(args.state)
    if state_path.exists():
        print(f"refusing to overwrite existing state: {state_path}", file=sys.stderr)
        return 2
    manifest = load_json(manifest_path)
    validate_manifest(manifest)
    state = initial_state(manifest)
    atomic_write(state_path, state)
    print(json.dumps({"created": str(state_path), "lessons": len(state["lessons"])}, ensure_ascii=False))
    return 0


def cmd_transition(args: argparse.Namespace) -> int:
    path = Path(args.state)
    state = load_json(path)
    lesson = get_lesson(state, args.lesson)
    old, new = lesson["status"], args.to
    if new not in ALL_STATES:
        raise ValueError(f"unknown state: {new}")
    if new not in ALLOWED[old]:
        raise ValueError(f"invalid transition: {old} -> {new}")

    production = state.get("production", {})
    budgets = lesson.get("effective_policy", {}).get("budgets", production.get("budgets", {}))
    gate = state.get("sample_gate", {})
    if new == "DRAFTED" and gate.get("enabled", False) and args.lesson != int(gate.get("lesson_no", args.lesson)) and not sample_gate_valid(state):
        raise ValueError("sample gate is not approved or sample hashes changed; only the sample lesson may be drafted")
    if new == "FIX_REQUIRED" and args.severity != "high":
        raise ValueError("FIX_REQUIRED requires --severity high; notes must not trigger rework")
    if old == "FIX_REQUIRED" and new == "DRAFTED":
        if lesson.get("attempts", {}).get("rework", 0) >= budgets.get("max_reworks_per_lesson", 1):
            raise ValueError("rework budget exhausted; escalate or stop instead of starting another rewrite")
    administrative_escalation = (
        old == "FIX_REQUIRED" and new == "ESCALATED"
        and lesson.get("attempts", {}).get("qa", 0) >= budgets.get("max_qa_rounds_per_lesson", 2)
    )
    strong_recovery = bool(lesson.get("strong_adjudication_pending", False))
    if old == "ESCALATED" and new == "DRAFTED" and lesson.get("attempts", {}).get("strong_adjudication", 0) >= 1:
        raise ValueError("strong-model adjudication budget exhausted")
    if new in {"SEMANTIC_QA_PASS", "FIX_REQUIRED", "ESCALATED"} and not administrative_escalation and not strong_recovery:
        if lesson.get("attempts", {}).get("qa", 0) >= budgets.get("max_qa_rounds_per_lesson", 2):
            raise ValueError("QA round budget exhausted")

    cost_bearing = new == "DRAFTED" or (new in {"SEMANTIC_QA_PASS", "FIX_REQUIRED", "ESCALATED"} and not administrative_escalation)
    if production and cost_bearing:
        if args.wall_minutes_used is None:
            raise ValueError("cost-bearing transition requires --wall-minutes-used")
        if args.wall_minutes_used < 0 or (args.tokens_used is not None and args.tokens_used < 0):
            raise ValueError("usage values must be non-negative")
        agent_calls = 1 if args.agent_calls is None else args.agent_calls
        if isinstance(agent_calls, bool) or agent_calls <= 0:
            raise ValueError("agent_calls must be a positive integer")
        usage = lesson.get("usage", {"tokens": 0, "wall_minutes": 0.0, "agent_calls": 0})
        projected_tokens = int(usage.get("tokens", 0)) + int(args.tokens_used or 0)
        projected_wall = float(usage.get("wall_minutes", 0.0)) + float(args.wall_minutes_used)
        projected_calls = int(usage.get("agent_calls", 0)) + int(agent_calls)
        if budgets.get("max_tokens_per_lesson", 0) and projected_tokens > budgets["max_tokens_per_lesson"]:
            raise ValueError("token budget exhausted")
        if budgets.get("max_wall_minutes_per_lesson", 0) and projected_wall > budgets["max_wall_minutes_per_lesson"]:
            raise ValueError("wall-clock budget exhausted")
        if budgets.get("max_agent_calls_per_lesson", 0) and projected_calls > budgets["max_agent_calls_per_lesson"]:
            raise ValueError("agent-call budget exhausted")

    candidate_artifacts = dict(lesson.get("artifacts", {}))
    if args.artifact:
        seen_artifact_keys = set()
        allowed_artifact_keys = {"source", "faithful", "lecture", "uncertainties", "coverage", "mechanical_report", "semantic_check", "qa_report", "official_faithful", "official_lecture", "course_map"}
        for item in args.artifact:
            if "=" not in item:
                raise ValueError("artifact must be key=/absolute/path")
            key, value = item.split("=", 1)
            if key in seen_artifact_keys:
                raise ValueError(f"duplicate artifact key: {key}")
            if key not in allowed_artifact_keys:
                raise ValueError(f"unknown artifact key: {key}")
            seen_artifact_keys.add(key)
            candidate_artifacts[key] = value

    profile = state_profile(state, lesson)
    for key in required_artifacts(new, profile):
        value = candidate_artifacts.get(key)
        if not value:
            raise ValueError(f"cannot enter {new}: missing artifact key {key}")
        if not Path(value).is_file():
            raise ValueError(f"cannot enter {new}: artifact not found {key}={value}")

    if new == "DRAFTED":
        is_sample = args.lesson == int(gate.get("lesson_no", args.lesson))
        if gate.get("enabled", False) and not is_sample and not sample_gate_valid(state):
            raise ValueError("cannot enter DRAFTED: approved gold_samples are missing or changed")
        if state.get("models", {}).get("writer") in {None, "", "unassigned"}:
            raise ValueError("cannot enter DRAFTED: writer model is unassigned")
        if requires_full_qa(state, lesson, int(lesson.get("attempts", {}).get("qa", 0)) + 1) and state.get("models", {}).get("qa") in {None, "", "unassigned"}:
            raise ValueError("cannot enter DRAFTED: selected independent QA requires a qa model")

    if new == "PROMOTED":
        verify_bound_artifacts(lesson, ("source", "faithful", "lecture", "uncertainties", "coverage"))
        expected_paths = render_paths(state, lesson)
        for official_key, draft_key in (("official_faithful", "faithful"), ("official_lecture", "lecture")):
            official_path = Path(candidate_artifacts[official_key]).resolve()
            if str(official_path) != str(Path(expected_paths[official_key]).resolve()):
                raise ValueError(f"{official_key} must match manifest-rendered path")
            if sha256_file(official_path) != sha256_file(Path(candidate_artifacts[draft_key])):
                raise ValueError(f"{official_key} content must match QA-validated {draft_key}")

    if new == "ACCEPTED":
        expected_map = Path(render_paths(state, lesson)["course_map"]).resolve()
        actual_map = Path(candidate_artifacts["course_map"]).resolve()
        if str(actual_map) != str(expected_map):
            raise ValueError("course_map must match manifest-rendered path")

    if new == "MECHANICAL_PASS":
        verify_bound_artifacts(lesson, ("source", "faithful", "lecture", "uncertainties", "coverage"))
        validate_mechanical_report(Path(candidate_artifacts["mechanical_report"]), state, lesson)

    if new in {"SEMANTIC_QA_PASS", "FIX_REQUIRED", "ESCALATED"} and not administrative_escalation:
        verify_bound_artifacts(lesson, ("source", "faithful", "lecture", "uncertainties", "coverage"))
        expected_round = int(lesson.get("attempts", {}).get("qa", 0)) + 1
        full_qa = requires_full_qa(state, lesson, expected_round) or new in {"FIX_REQUIRED", "ESCALATED"}
        if full_qa:
            qa_path = candidate_artifacts.get("qa_report")
            if not qa_path or not Path(qa_path).is_file():
                raise ValueError("independent QA decision requires qa_report artifact")
            validate_qa_report(Path(qa_path), state, lesson, new)
        else:
            if new != "SEMANTIC_QA_PASS":
                raise ValueError("writer self-check may only recommend SEMANTIC_QA_PASS")
            semantic_path = candidate_artifacts.get("semantic_check")
            if not semantic_path or not Path(semantic_path).is_file():
                raise ValueError("ordinary lesson requires semantic_check artifact")
            validate_semantic_check(Path(semantic_path), state, lesson)

    stamp = now()
    lesson["status"] = new
    lesson["artifacts"] = candidate_artifacts
    lesson["last_reason"] = args.reason
    lesson["updated_at"] = stamp
    lesson["history"].append({"at": stamp, "from": old, "to": new, "reason": args.reason})
    if new == "CAPTURED":
        lesson["attempts"]["capture"] += 1
        lesson.setdefault("artifact_sha256", {})["source"] = sha256_file(Path(candidate_artifacts["source"]))
    if new == "DRAFTED":
        lesson["attempts"]["draft"] += 1
        hashes = lesson.setdefault("artifact_sha256", {})
        for key in ("source", "faithful", "lecture", "uncertainties", "coverage"):
            value = candidate_artifacts.get(key)
            if value and Path(value).is_file():
                hashes[key] = sha256_file(Path(value))
    if new in {"SEMANTIC_QA_PASS", "FIX_REQUIRED", "ESCALATED"} and not administrative_escalation:
        lesson["attempts"]["qa"] += 1
    if old == "FIX_REQUIRED" and new == "DRAFTED": lesson["attempts"]["rework"] += 1
    if old == "ESCALATED" and new == "DRAFTED":
        lesson["attempts"]["strong_adjudication"] = lesson["attempts"].get("strong_adjudication", 0) + 1
        lesson["strong_adjudication_pending"] = True
    if new in {"SEMANTIC_QA_PASS", "FIX_REQUIRED", "ESCALATED"} and not administrative_escalation:
        evidence_key = "qa_report" if candidate_artifacts.get("qa_report") and (requires_full_qa(state, lesson, lesson["attempts"]["qa"]) or new in {"FIX_REQUIRED", "ESCALATED"}) else "semantic_check"
        lesson.setdefault("artifact_sha256", {})[evidence_key] = sha256_file(Path(candidate_artifacts[evidence_key]))
        lesson.setdefault("semantic_evidence_history", []).append({
            "at": stamp,
            "kind": evidence_key,
            "path": candidate_artifacts[evidence_key],
            "sha256": lesson["artifact_sha256"][evidence_key],
        })
        if strong_recovery:
            lesson["strong_adjudication_pending"] = False
    if new == "PROMOTED":
        hashes = lesson.setdefault("artifact_sha256", {})
        hashes["official_faithful"] = sha256_file(Path(candidate_artifacts["official_faithful"]))
        hashes["official_lecture"] = sha256_file(Path(candidate_artifacts["official_lecture"]))
    if new == "ACCEPTED":
        lesson.setdefault("artifact_sha256", {})["course_map"] = sha256_file(Path(candidate_artifacts["course_map"]))
    if production and cost_bearing:
        lesson.setdefault("usage", {"tokens": 0, "wall_minutes": 0.0, "agent_calls": 0})
        lesson["usage"]["tokens"] += int(args.tokens_used or 0)
        lesson["usage"]["wall_minutes"] += float(args.wall_minutes_used)
        lesson["usage"]["agent_calls"] = int(lesson["usage"].get("agent_calls", 0)) + int(1 if args.agent_calls is None else args.agent_calls)
    state["updated_at"] = stamp
    atomic_write(path, state)
    print(json.dumps({"lesson": args.lesson, "from": old, "to": new}, ensure_ascii=False))
    return 0


def render_paths(state: dict, lesson: dict) -> dict[str, str]:
    template = state.get("production", {}).get("naming_template", "\u7b2c{lesson_no:02d}\u8bfe\u00b7{title}.md")
    filename = template.format(lesson_no=int(lesson["lesson_no"]), title=lesson["title"])
    if not filename or Path(filename).name != filename or filename in {".", ".."}:
        raise ValueError("naming_template must render one safe filename")
    root = Path(state["course_root"]).resolve()
    templates = {
        "source": "00_\u539f\u59cb\u8f6c\u5199/{filename}",
        "official_faithful": "01_\u5fe0\u5b9e\u7cbe\u7f16\u7a3f/{filename}",
        "official_lecture": "02_\u7ed3\u6784\u5316\u8bb2\u4e49/{filename}",
        "course_map": "00_\u8bfe\u7a0b\u5730\u56fe.md",
    }
    templates.update(state.get("production", {}).get("path_templates", {}))
    result = {}
    for key, path_template in templates.items():
        try:
            rendered = path_template.format(
                filename=filename,
                lesson_no=int(lesson["lesson_no"]),
                title=lesson["title"],
            )
        except (KeyError, ValueError) as exc:
            raise ValueError(f"invalid path template {key}: {exc}") from exc
        rel = Path(rendered)
        if rel.is_absolute() or ".." in rel.parts:
            raise ValueError(f"unsafe path template: {key}")
        target = (root / rel).resolve()
        if root not in target.parents:
            raise ValueError(f"path escapes course_root: {key}")
        result[key] = str(target)
    return result


def cmd_agreement(args: argparse.Namespace) -> int:
    state = load_json(Path(args.state))
    production = state.get("production", {})
    purposes = production.get("course_purpose", [])
    agreement = {
        "course_id": state.get("course_id"),
        "course_title": state.get("course_title"),
        "course_purpose": [{"value": x, "label": PURPOSE_LABELS.get(x, x)} for x in purposes],
        "purpose_decision_basis": production.get("purpose_decision_basis"),
        "fixed_outputs": FIXED_OUTPUTS,
        "optional_extensions": production.get("optional_extensions", {}),
        "output_language": production.get("output_language", "match-user"),
        "output_language_defaulted": production.get("output_language_defaulted", True),
        "external_use": production.get("external_use", {}),
        "assurance": {
            "mode": production.get("profile"),
            "label": production.get("assurance_label", ASSURANCE_LABELS.get(production.get("profile"))),
            "decision_basis": production.get("assurance_decision_basis"),
        },
        "sample_gate": state.get("sample_gate", {}),
        "intake_confirmation": production.get("intake_confirmation", {}),
    }
    print(json.dumps(agreement, ensure_ascii=False, indent=2))
    return 0


def cmd_paths(args: argparse.Namespace) -> int:
    state = load_json(Path(args.state))
    lesson = get_lesson(state, args.lesson)
    print(json.dumps({"lesson_no": args.lesson, "paths": render_paths(state, lesson)}, ensure_ascii=False, indent=2))
    return 0


def cmd_next(args: argparse.Namespace) -> int:
    state = load_json(Path(args.state))
    priority = ["FIX_REQUIRED", "ESCALATED", "DISCOVERED", "CAPTURED", "SOURCE_VERIFIED", "DRAFTED", "MECHANICAL_PASS", "SEMANTIC_QA_PASS", "PROMOTED", "BLOCKED"]
    for status in priority:
        candidates = [x for x in state["lessons"] if x["status"] == status]
        if candidates:
            lesson = sorted(candidates, key=lambda x: x["lesson_no"])[0]
            usage = lesson.get("usage", {})
            budgets = state.get("production", {}).get("budgets", {})
            exhausted = (
                (budgets.get("max_tokens_per_lesson", 0) and usage.get("tokens", 0) >= budgets["max_tokens_per_lesson"])
                or (budgets.get("max_wall_minutes_per_lesson", 0) and usage.get("wall_minutes", 0) >= budgets["max_wall_minutes_per_lesson"])
                or (budgets.get("max_agent_calls_per_lesson", 0) and usage.get("agent_calls", 0) >= budgets["max_agent_calls_per_lesson"])
            )
            print(json.dumps({"lesson_no": lesson["lesson_no"], "title": lesson["title"], "status": status,
                              "budget_exhausted": bool(exhausted), "usage": usage}, ensure_ascii=False))
            return 0
    print(json.dumps({"done": True}, ensure_ascii=False))
    return 0


def required_artifacts(status: str, profile: str = "strict") -> set[str]:
    rank = MAIN_FLOW.index(status) if status in MAIN_FLOW else -1
    required = set()
    if rank >= MAIN_FLOW.index("CAPTURED"): required.add("source")
    if rank >= MAIN_FLOW.index("DRAFTED"):
        required.update({"faithful", "lecture", "uncertainties"})
        if profile == "strict":
            required.add("coverage")
    if rank >= MAIN_FLOW.index("MECHANICAL_PASS"): required.add("mechanical_report")
    if rank >= MAIN_FLOW.index("PROMOTED"): required.update({"official_faithful", "official_lecture"})
    if rank >= MAIN_FLOW.index("ACCEPTED"): required.add("course_map")
    return required


def valid_archived_entry(entry: object) -> bool:
    return isinstance(entry, dict) and all(entry.get(k) for k in ("path", "archived_at", "reason", "sha256"))


def cmd_audit(args: argparse.Namespace) -> int:
    state = load_json(Path(args.state))
    problems = []
    for lesson in state["lessons"]:
        profile = state_profile(state, lesson)
        status = lesson["status"]
        if status not in ALL_STATES:
            problems.append({"lesson": lesson["lesson_no"], "problem": f"unknown status {status}"})
            continue
        archived = lesson.get("artifacts_archived", {})
        for key in required_artifacts(status, profile):
            if key in archived:
                if status != "ACCEPTED" or key not in {"faithful", "lecture", "mechanical_report"} or not valid_archived_entry(archived[key]):
                    problems.append({"lesson": lesson["lesson_no"], "problem": f"invalid archived artifact {key}"})
                continue
            value = lesson.get("artifacts", {}).get(key)
            if not value:
                problems.append({"lesson": lesson["lesson_no"], "problem": f"missing artifact key {key}"})
            elif not Path(value).is_file():
                problems.append({"lesson": lesson["lesson_no"], "problem": f"artifact not found {key}: {value}"})
            elif key in {"qa_report", "official_faithful", "official_lecture"}:
                expected_hash = lesson.get("artifact_sha256", {}).get(key)
                if not expected_hash or sha256_file(Path(value)) != expected_hash:
                    problems.append({"lesson": lesson["lesson_no"], "problem": f"artifact integrity failed {key}"})
        if status in {"BLOCKED", "SKIPPED", "FIX_REQUIRED", "ESCALATED"} and not lesson.get("last_reason"):
            problems.append({"lesson": lesson["lesson_no"], "problem": f"{status} requires reason"})
    print(json.dumps({"ok": not problems, "problems": problems}, ensure_ascii=False, indent=2))
    return 0 if not problems else 1


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def cmd_approve_sample(args: argparse.Namespace) -> int:
    path = Path(args.state)
    state = load_json(path)
    gate = state.get("sample_gate", {})
    gate_lesson_no = int(gate.get("lesson_no", args.lesson))
    if args.lesson != gate_lesson_no:
        raise ValueError(f"sample lesson mismatch: expected {gate_lesson_no}")
    lesson = get_lesson(state, gate_lesson_no)
    if lesson["status"] != "ACCEPTED":
        raise ValueError("sample lesson must be ACCEPTED before user approval is recorded")
    expected = [lesson.get("artifacts", {}).get("official_faithful"), lesson.get("artifacts", {}).get("official_lecture")]
    if not all(expected):
        raise ValueError("accepted sample is missing official artifacts")
    samples = [Path(args.faithful).resolve(), Path(args.lecture).resolve()]
    if [str(p) for p in samples] != [str(Path(x).resolve()) for x in expected]:
        raise ValueError("approved sample paths must match the accepted lesson official artifacts")
    if any(not p.is_file() for p in samples):
        raise ValueError("approved sample files are missing")
    hashes = {"faithful": sha256_file(samples[0]), "lecture": sha256_file(samples[1])}
    gate.update({"approved": True, "approved_at": now(), "approved_by": args.approved_by, "sample_sha256": hashes})
    state["sample_gate"] = gate
    state["gold_samples"] = [str(p) for p in samples]
    state["updated_at"] = now()
    atomic_write(path, state)
    print(json.dumps({"sample_approved": lesson["lesson_no"], "gold_samples": state["gold_samples"]}, ensure_ascii=False))
    return 0


def cmd_archive_artifact(args: argparse.Namespace) -> int:
    path = Path(args.state)
    state = load_json(path)
    lesson = get_lesson(state, args.lesson)
    if lesson["status"] != "ACCEPTED":
        raise ValueError("artifacts may be archived only after ACCEPTED")
    allowed = {"faithful", "lecture", "mechanical_report"}
    if args.key not in allowed:
        raise ValueError(f"artifact cannot be archived: {args.key}")
    value = lesson.get("artifacts", {}).get(args.key)
    if not value or not Path(value).is_file():
        raise ValueError(f"artifact not found: {args.key}")
    digest = sha256_file(Path(value))
    if digest != args.sha256:
        raise ValueError("sha256 mismatch; refusing to archive")
    lesson.setdefault("artifacts_archived", {})[args.key] = {
        "path": value, "archived_at": now(), "reason": args.reason, "sha256": digest,
    }
    lesson["artifacts"].pop(args.key, None)
    state["updated_at"] = now()
    atomic_write(path, state)
    print(json.dumps({"lesson": args.lesson, "archived": args.key, "sha256": digest}, ensure_ascii=False))
    return 0


def cmd_summary(args: argparse.Namespace) -> int:
    state = load_json(Path(args.state))
    counts = Counter(x["status"] for x in state["lessons"])
    unresolved = [
        {"lesson_no": x["lesson_no"], "title": x["title"], "status": x["status"], "reason": x.get("last_reason")}
        for x in state["lessons"] if x["status"] not in {"ACCEPTED", "SKIPPED"}
    ]
    print(json.dumps({
        "course_id": state["course_id"],
        "output_language": state.get("production", {}).get("output_language", "match-user"),
        "counts": dict(sorted(counts.items())),
        "unresolved": unresolved,
    }, ensure_ascii=False, indent=2))
    return 0


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser()
    sub = p.add_subparsers(dest="command", required=True)
    q = sub.add_parser("init"); q.add_argument("--manifest", required=True); q.add_argument("--state", required=True); q.set_defaults(func=cmd_init)
    q = sub.add_parser("transition"); q.add_argument("--state", required=True); q.add_argument("--lesson", type=int, required=True); q.add_argument("--to", required=True); q.add_argument("--reason", required=True); q.add_argument("--severity", choices=["high", "note"]); q.add_argument("--tokens-used", type=int); q.add_argument("--wall-minutes-used", type=float); q.add_argument("--agent-calls", type=int); q.add_argument("--artifact", action="append"); q.set_defaults(func=cmd_transition)
    q = sub.add_parser("next"); q.add_argument("--state", required=True); q.set_defaults(func=cmd_next)
    q = sub.add_parser("agreement"); q.add_argument("--state", required=True); q.set_defaults(func=cmd_agreement)
    q = sub.add_parser("paths"); q.add_argument("--state", required=True); q.add_argument("--lesson", type=int, required=True); q.set_defaults(func=cmd_paths)
    q = sub.add_parser("audit"); q.add_argument("--state", required=True); q.set_defaults(func=cmd_audit)
    q = sub.add_parser("approve-sample"); q.add_argument("--state", required=True); q.add_argument("--lesson", type=int, required=True); q.add_argument("--faithful", required=True); q.add_argument("--lecture", required=True); q.add_argument("--approved-by", required=True); q.set_defaults(func=cmd_approve_sample)
    q = sub.add_parser("archive-artifact"); q.add_argument("--state", required=True); q.add_argument("--lesson", type=int, required=True); q.add_argument("--key", required=True); q.add_argument("--sha256", required=True); q.add_argument("--reason", required=True); q.set_defaults(func=cmd_archive_artifact)
    q = sub.add_parser("summary"); q.add_argument("--state", required=True); q.set_defaults(func=cmd_summary)
    return p


def main() -> int:
    try:
        parser = build_parser()
        args = parser.parse_args()
        return args.func(args)
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2

if __name__ == "__main__":
    raise SystemExit(main())
