#!/usr/bin/env python3
"""State manager for pinshu-course-capture runtime projects.

This script never calls a model and never edits course prose. It owns deterministic
state transitions, atomic persistence, next-work selection, and artifact audits.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
import re
import shutil
import subprocess
import sys
import tempfile
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import unquote

SCHEMA_VERSION = 1
REPORT_SCHEMA_VERSION = 2
MECHANICAL_ALGORITHM_VERSION = "pinshu-mechanical-2026-10-v2"
USAGE_PHASES = ("capture", "draft", "mechanical", "qa", "rework", "recheck", "promotion", "revision", "visual", "legacy")
REPORT_TYPES = {"mechanical_report", "semantic_check", "qa_report", "revision_report"}
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
VISUAL_LEARNING_KEYS = {"enabled", "pilot_lesson_no", "batch_approved", "status"}
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
PROMOTION_HYGIENE_KEYS = {"source_link_fields", "forbidden_draft_markers", "require_source_backlink"}


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


def absolute_from(base: Path, value: str) -> Path:
    path = Path(value).expanduser()
    return path.resolve() if path.is_absolute() else (base / path).resolve()


def build_path_context(manifest_path: Path, state_path: Path, manifest: dict) -> dict:
    """Freeze all path anchors so later commands never depend on process cwd."""
    manifest_dir = manifest_path.resolve().parent
    control_dir = state_path.resolve().parent
    return {
        "manifest_dir": str(manifest_dir),
        "control_dir": str(control_dir),
        "state_path": str(state_path.resolve()),
        "course_root": str(absolute_from(manifest_dir, str(manifest["course_root"]))),
        "runtime_dir": str(absolute_from(manifest_dir, str(manifest["runtime_dir"]))),
    }


def path_anchors(state: dict, state_path: Path) -> list[Path]:
    """Return only persisted/state-derived anchors, including legacy layouts."""
    context = state.get("path_context", {})
    state_dir = state_path.resolve().parent
    anchors: list[Path] = []
    for value in (
        context.get("control_dir"),
        context.get("runtime_dir"),
        state.get("runtime_dir"),
        context.get("course_root"),
        state.get("course_root"),
        state_dir,
    ):
        if not value:
            continue
        p = Path(value).expanduser()
        if not p.is_absolute():
            # Legacy state values are interpreted from the state directory, not cwd.
            p = state_dir / p
        p = p.resolve()
        if p not in anchors:
            anchors.append(p)
    return anchors


def resolve_state_path(state: dict, state_path: Path, value: str, *, must_exist: bool = False) -> Path:
    """Resolve a stored path without a cwd fallback.

    Historical states sometimes stored ``runtime/lesson-N/file`` while the state
    itself lived inside ``runtime``.  The parent-of-runtime candidate supports that
    shape using only persisted/state-derived anchors.
    """
    raw = Path(value).expanduser()
    if raw.is_absolute():
        candidates = [raw.resolve()]
    else:
        candidates = []
        anchors = path_anchors(state, state_path)
        for anchor in anchors:
            candidates.append((anchor / raw).resolve())
            if raw.parts and raw.parts[0] == anchor.name:
                candidates.append((anchor.parent / raw).resolve())
        unique: list[Path] = []
        for candidate in candidates:
            if candidate not in unique:
                unique.append(candidate)
        candidates = unique
    existing = [candidate for candidate in candidates if candidate.exists()]
    if len(existing) > 1:
        # Identical real paths are harmless; distinct matches are ambiguous.
        real = {str(candidate.resolve()) for candidate in existing}
        if len(real) > 1:
            raise ValueError(f"ambiguous stored path {value}: {sorted(real)}")
    if existing:
        return existing[0]
    if must_exist:
        raise ValueError(f"stored path not found without cwd fallback: {value}")
    if not candidates:
        raise ValueError(f"cannot resolve stored path: {value}")
    return candidates[0]


def artifact_path(state: dict, state_path: Path, lesson: dict, key: str, *, must_exist: bool = True) -> Path:
    value = lesson.get("artifacts", {}).get(key)
    if not value:
        raise ValueError(f"missing artifact key {key}")
    return resolve_state_path(state, state_path, str(value), must_exist=must_exist)


def new_usage() -> dict:
    return {
        "tokens": 0,
        "wall_minutes": 0.0,
        "agent_calls": 0,
        "phases": {phase: {"tokens": 0, "wall_minutes": 0.0, "agent_calls": 0} for phase in USAGE_PHASES},
    }


def normalize_usage(lesson: dict) -> dict:
    usage = lesson.setdefault("usage", {"tokens": 0, "wall_minutes": 0.0, "agent_calls": 0})
    if "phases" not in usage:
        usage["phases"] = {
            "legacy": {
                "tokens": int(usage.get("tokens", 0)),
                "wall_minutes": float(usage.get("wall_minutes", 0.0)),
                "agent_calls": int(usage.get("agent_calls", 0)),
            }
        }
    phases = usage["phases"]
    for phase in USAGE_PHASES:
        phases.setdefault(phase, {"tokens": 0, "wall_minutes": 0.0, "agent_calls": 0})
    return usage


def add_usage(lesson: dict, phase: str, tokens: int = 0, wall: float = 0.0, calls: int = 0) -> None:
    if phase not in USAGE_PHASES:
        raise ValueError(f"unknown usage phase: {phase}")
    if tokens < 0 or wall < 0 or calls < 0:
        raise ValueError("usage values must be non-negative")
    usage = normalize_usage(lesson)
    usage["tokens"] = int(usage.get("tokens", 0)) + int(tokens)
    usage["wall_minutes"] = float(usage.get("wall_minutes", 0.0)) + float(wall)
    usage["agent_calls"] = int(usage.get("agent_calls", 0)) + int(calls)
    bucket = usage["phases"][phase]
    bucket["tokens"] += int(tokens)
    bucket["wall_minutes"] += float(wall)
    bucket["agent_calls"] += int(calls)


def usage_consistent(lesson: dict) -> bool:
    usage = normalize_usage(lesson)
    phases = usage["phases"]
    # Legacy totals may predate phase tracking. Preserve them in an explicit bucket.
    sums = {
        "tokens": sum(int(x.get("tokens", 0)) for x in phases.values()),
        "wall_minutes": sum(float(x.get("wall_minutes", 0.0)) for x in phases.values()),
        "agent_calls": sum(int(x.get("agent_calls", 0)) for x in phases.values()),
    }
    return (sums["tokens"] == int(usage.get("tokens", 0))
            and abs(sums["wall_minutes"] - float(usage.get("wall_minutes", 0.0))) < 1e-9
            and sums["agent_calls"] == int(usage.get("agent_calls", 0)))


def validate_usage_delta(tokens: int, wall: float, calls: int) -> None:
    if tokens < 0 or not math.isfinite(wall) or wall < 0 or isinstance(calls, bool) or calls <= 0:
        raise ValueError("usage must be finite and non-negative with positive agent_calls")


def transition_budget_payload(args: argparse.Namespace) -> dict:
    return {
        "operation": "transition",
        "to": args.to,
        "reason": args.reason,
        "severity": args.severity,
        "tokens_used": int(args.tokens_used or 0),
        "wall_minutes_used": float(args.wall_minutes_used or 0),
        "agent_calls": int(1 if args.agent_calls is None else args.agent_calls),
        "phase": args.phase,
        "artifacts": sorted(args.artifact or []),
    }


def visual_budget_payload(args: argparse.Namespace) -> dict:
    return {
        "operation": "record-visual",
        "report": str(Path(args.report).expanduser().resolve()),
        "tokens_used": int(args.tokens_used),
        "wall_minutes_used": float(args.wall_minutes_used),
        "agent_calls": int(args.agent_calls),
        "artifacts": sorted(args.artifact or []),
    }


def budget_overages(usage: dict, budgets: dict) -> dict:
    mapping = {
        "tokens": "max_tokens_per_lesson",
        "wall_minutes": "max_wall_minutes_per_lesson",
        "agent_calls": "max_agent_calls_per_lesson",
    }
    return {
        key: {"used": usage.get(key, 0), "limit": budgets[cap]}
        for key, cap in mapping.items()
        if budgets.get(cap) and usage.get(key, 0) > budgets[cap]
    }


def block_for_budget(path: Path, state: dict, lesson: dict, *, phase: str, payload: dict,
                     prior_status: str, tokens: int, wall: float, calls: int, budgets: dict) -> None:
    add_usage(lesson, phase, tokens=tokens, wall=wall, calls=calls)
    stamp = now()
    event_id = hashlib.sha256(json.dumps({
        "course": state.get("course_id"),
        "lesson": lesson["lesson_no"],
        "at": stamp,
        "payload": payload,
    }, sort_keys=True, ensure_ascii=False).encode("utf-8")).hexdigest()[:16]
    lesson["budget_block"] = {
        "event_id": event_id,
        "at": stamp,
        "prior_status": prior_status,
        "phase": phase,
        "payload": payload,
        "overages": budget_overages(lesson["usage"], budgets),
        "usage_recorded": {"tokens": tokens, "wall_minutes": wall, "agent_calls": calls},
    }
    lesson["status"] = "BLOCKED"
    lesson["last_reason"] = "budget_exceeded"
    lesson["updated_at"] = state["updated_at"] = stamp
    lesson.setdefault("history", []).append({
        "at": stamp,
        "from": prior_status,
        "to": "BLOCKED",
        "reason": "budget_exceeded",
        "event_id": event_id,
    })
    atomic_write(path, state)
    raise ValueError(f"budget exceeded; real usage recorded and lesson BLOCKED (event {event_id})")


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
    if "visual_learning" in m:
        visual = m["visual_learning"]
        if not isinstance(visual, dict) or set(visual) - VISUAL_LEARNING_KEYS:
            raise ValueError("visual_learning contains unsupported fields")
        if not isinstance(visual.get("enabled"), bool):
            raise ValueError("visual_learning.enabled must be boolean")
        if visual.get("batch_approved") is not False:
            raise ValueError("visual_learning.batch_approved must remain false until a real pilot is approved")
        if visual.get("enabled") and int(visual.get("pilot_lesson_no", 0)) not in {int(x["lesson_no"]) for x in m["lessons"]}:
            raise ValueError("visual_learning.pilot_lesson_no is not in lessons")
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
    hygiene = m.get("promotion_hygiene")
    if hygiene is not None:
        if not isinstance(hygiene, dict) or set(hygiene) - PROMOTION_HYGIENE_KEYS:
            raise ValueError("promotion_hygiene contains unsupported fields")
        fields = hygiene.get("source_link_fields")
        markers = hygiene.get("forbidden_draft_markers")
        if not isinstance(fields, list) or not fields or any(not isinstance(x, str) or not x.strip() for x in fields):
            raise ValueError("promotion_hygiene.source_link_fields must be a non-empty string list")
        if not isinstance(markers, list) or any(not isinstance(x, str) or not x for x in markers):
            raise ValueError("promotion_hygiene.forbidden_draft_markers must be a string list")
        if hygiene.get("require_source_backlink") is not True:
            raise ValueError("promotion_hygiene.require_source_backlink must be true")
    case_library = m.get("case_library")
    if case_library is not None and not isinstance(case_library, (str, dict)):
        raise ValueError("case_library must be a path string or object")
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


def initial_state(m: dict, path_context: dict | None = None) -> dict:
    created = now()
    default_budgets = {
        "max_tokens_per_lesson": 300000,
        "max_wall_minutes_per_lesson": 20,
        "max_agent_calls_per_lesson": 6 if m.get("visual_learning", {}).get("enabled") else 3,
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
            "usage": new_usage(),
            "artifacts": {},
            "artifact_sha256": {},
            "revision": None,
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
        "course_root": (path_context or {}).get("course_root", m["course_root"]),
        "runtime_dir": (path_context or {}).get("runtime_dir", m["runtime_dir"]),
        "path_context": path_context,
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
            **({"visual_learning": dict(m["visual_learning"])} if "visual_learning" in m else {}),
            "output_language": resolved_output_language(m),
            "output_language_defaulted": "output_language" not in m,
            "naming_template": m.get("naming_template", "\u7b2c{lesson_no:02d}\u8bfe\u00b7{title}.md"),
            "path_templates": m.get("path_templates", {
                "source": "00_\u539f\u59cb\u8f6c\u5199/{filename}",
                "official_faithful": "01_\u5fe0\u5b9e\u7cbe\u7f16\u7a3f/{filename}",
                "official_lecture": "02_\u7ed3\u6784\u5316\u8bb2\u4e49/{filename}",
                "course_map": "00_\u8bfe\u7a0b\u5730\u56fe.md",
            }),
            "promotion_hygiene": m.get("promotion_hygiene"),
            "case_library": m.get("case_library"),
        },
        "sample_gate": sample_gate,
        "models": {"writer": m["writer_model"], "qa": m["qa_model"], "strong": m["strong_model"]},
        "gold_samples": m["gold_samples"],
        "created_at": created,
        "updated_at": created,
        "shared_artifacts": {},
        "lessons": lessons,
    }


def state_profile(state: dict, lesson: dict | None = None) -> str:
    if lesson:
        return lesson.get("effective_policy", {}).get("assurance_mode", state.get("production", {}).get("profile", "strict"))
    return state.get("production", {}).get("profile", "strict")


def sample_gate_valid(state: dict, state_path: Path) -> bool:
    gate = state.get("sample_gate", {})
    if not gate.get("enabled", False):
        return True
    if not gate.get("approved", False):
        return False
    samples = [resolve_state_path(state, state_path, x, must_exist=True) for x in state.get("gold_samples", [])]
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


def verify_bound_artifacts(state: dict, state_path: Path, lesson: dict, keys: tuple[str, ...] | None = None) -> None:
    expected = lesson.get("artifact_sha256", {})
    for key in keys or tuple(expected):
        if key not in expected:
            continue
        try:
            actual = artifact_path(state, state_path, lesson, key)
        except ValueError as exc:
            raise ValueError(f"artifact integrity failed {key}: {exc}") from exc
        if sha256_file(actual) != expected[key]:
            raise ValueError(f"artifact integrity failed {key}")


def validate_input_hashes(data: dict, lesson: dict, *, expected_hashes: dict[str, str] | None = None) -> None:
    declared = data.get("input_sha256")
    expected = expected_hashes if expected_hashes is not None else bound_input_hashes(lesson)
    if not isinstance(declared, dict) or any(not declared.get(k) or declared.get(k) != v for k, v in expected.items()):
        raise ValueError("report input_sha256 does not match reviewed artifacts")


def validate_report_envelope(data: dict, report_type: str, state: dict, lesson: dict) -> None:
    """Validate v2 strictly while retaining known-valid v1 public reports."""
    version = data.get("schema_version")
    if version not in {1, REPORT_SCHEMA_VERSION}:
        raise ValueError(f"unsupported {report_type} schema_version")
    if version == REPORT_SCHEMA_VERSION:
        required = {
            "report_type", "course_id", "lesson_no", "reviewer_kind", "reviewer_model",
            "assurance_mode", "review_round", "review_scope", "decision", "recommended_state",
            "source_identity", "coverage", "input_sha256",
        }
        missing = required - set(data)
        if missing:
            raise ValueError(f"{report_type} missing fields: {', '.join(sorted(missing))}")
        if data.get("report_type") != report_type:
            raise ValueError(f"report_type must be {report_type}")
    if data.get("course_id") not in (None, state.get("course_id")):
        raise ValueError(f"{report_type} course_id mismatch")
    if data.get("lesson_no") is not None and int(data["lesson_no"]) != int(lesson["lesson_no"]):
        raise ValueError(f"{report_type} lesson_no mismatch")


def validate_mechanical_report(path: Path, state: dict, lesson: dict) -> dict:
    data = load_json(path)
    if data.get("schema_version") == REPORT_SCHEMA_VERSION:
        validate_report_envelope(data, "mechanical_report", state, lesson)
        if data.get("reviewer_kind") != "deterministic_validator" or data.get("reviewer_model") != "none":
            raise ValueError("mechanical_report reviewer identity is invalid")
        if data.get("decision") != "mechanical_pass" or data.get("recommended_state") != "MECHANICAL_PASS":
            raise ValueError("mechanical_report decision is invalid")
        if data.get("algorithm_version") != MECHANICAL_ALGORITHM_VERSION or not data.get("statistics_definition"):
            raise ValueError("mechanical_report algorithm metadata is missing or unsupported")
    elif data.get("schema_version") != 1:
        raise ValueError("mechanical_report schema_version is invalid")
    if data.get("mechanical_pass") is not True:
        raise ValueError("mechanical_report must be passing")
    if data.get("semantic_pass") is not None or data.get("errors") not in ([], None):
        raise ValueError("mechanical_report has invalid semantic_pass or errors")
    if data.get("profile", data.get("assurance_mode")) != state_profile(state, lesson):
        raise ValueError("mechanical_report profile mismatch")
    validate_input_hashes(data, lesson)
    return data


def validate_semantic_check(path: Path, state: dict, lesson: dict) -> dict:
    data = load_json(path)
    validate_report_envelope(data, "semantic_check", state, lesson)
    if data.get("reviewer_kind") != "writer_self_check":
        raise ValueError("semantic_check must be a writer_self_check report")
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
    return data


def validate_qa_report(path: Path, state: dict, lesson: dict, new_state: str,
                       *, expected_round: int | None = None, allowed_scopes: set[str] | None = None,
                       expected_hashes: dict[str, str] | None = None) -> dict:
    data = load_json(path)
    validate_report_envelope(data, "qa_report", state, lesson)
    expected_decision = {
        "SEMANTIC_QA_PASS": "pass", "FIX_REQUIRED": "fix_required", "ESCALATED": "escalated",
    }[new_state]
    expected_round = expected_round or int(lesson.get("attempts", {}).get("qa", 0)) + 1
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
    if allowed_scopes is not None:
        if scope not in allowed_scopes:
            raise ValueError(f"qa_report review_scope must be one of {sorted(allowed_scopes)}")
    elif expected_round > 1:
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
    if any(x.get("severity") not in {"high", "note"} for x in issues):
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
    if new_state == "SEMANTIC_QA_PASS" and scope in {"full", "revision_content", "revision_formatting"}:
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
    validate_input_hashes(data, lesson, expected_hashes=expected_hashes)
    return data


def get_lesson(state: dict, no: int) -> dict:
    for lesson in state["lessons"]:
        if int(lesson["lesson_no"]) == no:
            return lesson
    raise ValueError(f"lesson not found: {no}")


def cmd_init(args: argparse.Namespace) -> int:
    manifest_path, state_path = Path(args.manifest).resolve(), Path(args.state).resolve()
    if state_path.exists():
        print(f"refusing to overwrite existing state: {state_path}", file=sys.stderr)
        return 2
    manifest = load_json(manifest_path)
    validate_manifest(manifest)
    context = build_path_context(manifest_path, state_path, manifest)
    state = initial_state(manifest, context)
    atomic_write(state_path, state)
    print(json.dumps({"created": str(state_path), "lessons": len(state["lessons"])}, ensure_ascii=False))
    return 0


def cmd_set_budget(args: argparse.Namespace) -> int:
    path = Path(args.state).resolve()
    state = load_json(path)
    lesson = get_lesson(state, args.lesson)
    validate_positive_int(args.key, args.value)
    if not args.reason.strip():
        raise ValueError("set-budget requires a reason")
    budgets = lesson.setdefault("effective_policy", {}).setdefault(
        "budgets", dict(state.get("production", {}).get("budgets", {}))
    )
    old = budgets.get(args.key)
    budgets[args.key] = args.value
    stamp = now()
    lesson.setdefault("budget_history", []).append({
        "at": stamp,
        "key": args.key,
        "old": old,
        "new": args.value,
        "reason": args.reason,
    })
    lesson["updated_at"] = state["updated_at"] = stamp
    atomic_write(path, state)
    print(json.dumps({"lesson": args.lesson, "key": args.key, "old": old, "new": args.value}, ensure_ascii=False))
    return 0


def cmd_resume_budget(args: argparse.Namespace) -> int:
    path = Path(args.state).resolve()
    state = load_json(path)
    lesson = get_lesson(state, args.lesson)
    block = lesson.get("budget_block")
    if lesson.get("status") != "BLOCKED" or not isinstance(block, dict):
        raise ValueError("resume-budget requires a budget-blocked lesson")
    if block.get("event_id") != args.event_id:
        raise ValueError("budget event id mismatch")
    budgets = lesson.get("effective_policy", {}).get("budgets", state.get("production", {}).get("budgets", {}))
    if budget_overages(normalize_usage(lesson), budgets):
        raise ValueError("budget is still below the recorded real usage")
    stamp = now()
    prior = block["prior_status"]
    lesson["status"] = prior
    lesson["budget_credit"] = block
    lesson.pop("budget_block", None)
    lesson["last_reason"] = args.reason
    lesson["updated_at"] = state["updated_at"] = stamp
    lesson.setdefault("history", []).append({
        "at": stamp,
        "from": "BLOCKED",
        "to": prior,
        "reason": args.reason,
        "event_id": args.event_id,
    })
    atomic_write(path, state)
    print(json.dumps({"lesson": args.lesson, "resumed_to": prior, "event_id": args.event_id}, ensure_ascii=False))
    return 0


FRONTMATTER_BLOCK = re.compile(r"\A---\s*\n(.*?)\n---\s*\n", re.S)
MARKDOWN_LINK = re.compile(r"!?\[([^\]]*)\]\(([^)]+)\)")


def frontmatter_values(text: str) -> dict[str, str]:
    match = FRONTMATTER_BLOCK.match(text.replace("\r\n", "\n"))
    if not match:
        return {}
    result: dict[str, str] = {}
    for line in match.group(1).splitlines():
        if ":" in line and not line[:1].isspace():
            key, value = line.split(":", 1)
            result[key.strip()] = value.strip().strip("'\"")
    return result


def local_link_targets(path: Path, text: str) -> list[Path]:
    targets: list[Path] = []
    for _label, raw in MARKDOWN_LINK.findall(text):
        raw = raw.strip().split("#", 1)[0]
        if not raw or re.match(r"^[a-z][a-z0-9+.-]*:", raw, re.I):
            continue
        targets.append((path.parent / raw).resolve())
    return targets


def validate_promotion_hygiene(state: dict, state_path: Path, lesson: dict,
                               candidate_artifacts: dict[str, str]) -> None:
    config = state.get("production", {}).get("promotion_hygiene")
    if not isinstance(config, dict):
        raise ValueError("promotion_hygiene is not configured; refusing to guess the frontmatter source schema")
    source = resolve_state_path(state, state_path, candidate_artifacts["source"], must_exist=True)
    runtime = resolve_state_path(state, state_path, state.get("runtime_dir", "."), must_exist=False)
    markers = list(config.get("forbidden_draft_markers", []))
    markers.extend(["awaiting independent QA", "pending independent QA", "FIX_REQUIRED"])
    for key in ("official_faithful", "official_lecture"):
        path = resolve_state_path(state, state_path, candidate_artifacts[key], must_exist=True)
        text = path.read_text(encoding="utf-8")
        if any(marker and marker in text for marker in markers):
            raise ValueError(f"promotion hygiene failed: forbidden draft marker in {key}")
        if str(runtime) in text or runtime.name + "/lesson-" in text:
            raise ValueError(f"promotion hygiene failed: runtime draft reference in {key}")
        if any(not target.is_file() for target in local_link_targets(path, text)):
            raise ValueError(f"promotion hygiene failed: broken local link in {key}")
        values = frontmatter_values(text)
        backlinks = [str(values[field]) for field in config.get("source_link_fields", []) if values.get(field)]
        if config.get("require_source_backlink") and not backlinks:
            raise ValueError(f"promotion hygiene failed: configured source backlink missing in {key}")
        if backlinks:
            resolved = [resolve_state_path(state, state_path, value, must_exist=True) if Path(value).is_absolute()
                        else (path.parent / value).resolve() for value in backlinks]
            if source.resolve() not in [item.resolve() for item in resolved] or any(not item.is_file() for item in resolved):
                raise ValueError(f"promotion hygiene failed: source backlink is broken or points to another source in {key}")


def cmd_transition(args: argparse.Namespace) -> int:
    path = Path(args.state).resolve()
    state = load_json(path)
    lesson = get_lesson(state, args.lesson)
    old, new = lesson["status"], args.to
    expected_round = int(lesson.get("attempts", {}).get("qa", 0)) + 1
    actual_evidence: tuple[str, Path, dict] | None = None
    if new not in ALL_STATES:
        raise ValueError(f"unknown state: {new}")
    if new not in ALLOWED[old]:
        raise ValueError(f"invalid transition: {old} -> {new}")

    production = state.get("production", {})
    budgets = lesson.get("effective_policy", {}).get("budgets", production.get("budgets", {}))
    gate = state.get("sample_gate", {})
    if new == "DRAFTED" and gate.get("enabled", False) and args.lesson != int(gate.get("lesson_no", args.lesson)) and not sample_gate_valid(state, path):
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
    payload = transition_budget_payload(args) if cost_bearing else None
    credit = lesson.get("budget_credit")
    if credit and credit.get("payload") != payload:
        raise ValueError("budget recovery is pending; retry the exact blocked transition")
    charge_tokens = 0 if credit else int(args.tokens_used or 0)
    charge_wall = 0.0 if credit else float(args.wall_minutes_used or 0)
    charge_calls = 0 if credit else int(1 if args.agent_calls is None else args.agent_calls)
    if production and cost_bearing:
        if args.wall_minutes_used is None:
            raise ValueError("cost-bearing transition requires --wall-minutes-used")
        if args.wall_minutes_used < 0 or (args.tokens_used is not None and args.tokens_used < 0):
            raise ValueError("usage values must be non-negative")
        agent_calls = 1 if args.agent_calls is None else args.agent_calls
        if isinstance(agent_calls, bool) or agent_calls <= 0:
            raise ValueError("agent_calls must be a positive integer")
        usage = lesson.get("usage", {"tokens": 0, "wall_minutes": 0.0, "agent_calls": 0})
        projected = {
            "tokens": int(usage.get("tokens", 0)) + charge_tokens,
            "wall_minutes": float(usage.get("wall_minutes", 0.0)) + charge_wall,
            "agent_calls": int(usage.get("agent_calls", 0)) + charge_calls,
        }
        if budget_overages(projected, budgets):
            phase = args.phase or ("draft" if new == "DRAFTED" else "qa")
            block_for_budget(path, state, lesson, phase=phase, payload=payload, prior_status=old,
                             tokens=charge_tokens, wall=charge_wall, calls=charge_calls, budgets=budgets)

    candidate_artifacts = dict(lesson.get("artifacts", {}))
    if args.artifact:
        seen_artifact_keys = set()
        allowed_artifact_keys = {"source", "faithful", "lecture", "uncertainties", "coverage", "mechanical_report", "semantic_check", "qa_report", "official_faithful", "official_lecture", "course_map", "official_visual_md", "official_visual_html"}
        for item in args.artifact:
            if "=" not in item:
                raise ValueError("artifact must be key=/absolute/path")
            key, value = item.split("=", 1)
            if key in seen_artifact_keys:
                raise ValueError(f"duplicate artifact key: {key}")
            if key not in allowed_artifact_keys:
                raise ValueError(f"unknown artifact key: {key}")
            if not Path(value).expanduser().is_absolute():
                raise ValueError("new artifact registrations require absolute paths")
            seen_artifact_keys.add(key)
            candidate_artifacts[key] = str(Path(value).expanduser().resolve())

    profile = state_profile(state, lesson)
    for key in required_artifacts(new, profile):
        value = candidate_artifacts.get(key)
        if not value:
            raise ValueError(f"cannot enter {new}: missing artifact key {key}")
        if not resolve_state_path(state, path, value, must_exist=True).is_file():
            raise ValueError(f"cannot enter {new}: artifact not found {key}={value}")

    if new == "DRAFTED":
        is_sample = args.lesson == int(gate.get("lesson_no", args.lesson))
        if gate.get("enabled", False) and not is_sample and not sample_gate_valid(state, path):
            raise ValueError("cannot enter DRAFTED: approved gold_samples are missing or changed")
        if state.get("models", {}).get("writer") in {None, "", "unassigned"}:
            raise ValueError("cannot enter DRAFTED: writer model is unassigned")
        if requires_full_qa(state, lesson, int(lesson.get("attempts", {}).get("qa", 0)) + 1) and state.get("models", {}).get("qa") in {None, "", "unassigned"}:
            raise ValueError("cannot enter DRAFTED: selected independent QA requires a qa model")

    if new == "PROMOTED":
        verify_bound_artifacts(state, path, lesson, ("source", "faithful", "lecture", "uncertainties", "coverage"))
        expected_paths = render_paths(state, lesson, path)
        for official_key, draft_key in (("official_faithful", "faithful"), ("official_lecture", "lecture")):
            official_path = resolve_state_path(state, path, candidate_artifacts[official_key], must_exist=True)
            if str(official_path) != str(Path(expected_paths[official_key]).resolve()):
                raise ValueError(f"{official_key} must match manifest-rendered path")
            draft_path = resolve_state_path(state, path, candidate_artifacts[draft_key], must_exist=True)
            if sha256_file(official_path) != sha256_file(draft_path):
                raise ValueError(f"{official_key} content must match QA-validated {draft_key}")
        validate_promotion_hygiene(state, path, lesson, candidate_artifacts)

    if new == "ACCEPTED":
        if visual_enabled(state):
            validate_visual_result(state, lesson, candidate_artifacts, formal=True, state_path=path)
        expected_map = Path(render_paths(state, lesson, path)["course_map"]).resolve()
        actual_map = resolve_state_path(state, path, candidate_artifacts["course_map"], must_exist=True)
        if str(actual_map) != str(expected_map):
            raise ValueError("course_map must match manifest-rendered path")

    if new == "MECHANICAL_PASS":
        verify_bound_artifacts(state, path, lesson, ("source", "faithful", "lecture", "uncertainties", "coverage"))
        validate_mechanical_report(resolve_state_path(state, path, candidate_artifacts["mechanical_report"], must_exist=True), state, lesson)

    if new in {"SEMANTIC_QA_PASS", "FIX_REQUIRED", "ESCALATED"} and not administrative_escalation:
        verify_bound_artifacts(state, path, lesson, ("source", "faithful", "lecture", "uncertainties", "coverage"))
        full_qa = expected_round > 1 or requires_full_qa(state, lesson, expected_round) or new in {"FIX_REQUIRED", "ESCALATED"}
        if full_qa:
            qa_path = candidate_artifacts.get("qa_report")
            if not qa_path:
                raise ValueError("independent QA decision requires qa_report artifact")
            report_path = resolve_state_path(state, path, qa_path, must_exist=True)
            report_data = validate_qa_report(report_path, state, lesson, new)
            actual_evidence = ("qa_report", report_path, report_data)
        else:
            if new != "SEMANTIC_QA_PASS":
                raise ValueError("writer self-check may only recommend SEMANTIC_QA_PASS")
            semantic_path = candidate_artifacts.get("semantic_check")
            if not semantic_path:
                raise ValueError("ordinary lesson requires semantic_check artifact")
            report_path = resolve_state_path(state, path, semantic_path, must_exist=True)
            report_data = validate_semantic_check(report_path, state, lesson)
            actual_evidence = ("semantic_check", report_path, report_data)

    stamp = now()
    lesson["status"] = new
    lesson["artifacts"] = candidate_artifacts
    lesson["last_reason"] = args.reason
    lesson["updated_at"] = stamp
    lesson["history"].append({"at": stamp, "from": old, "to": new, "reason": args.reason})
    if new == "CAPTURED":
        lesson["attempts"]["capture"] += 1
        lesson.setdefault("artifact_sha256", {})["source"] = sha256_file(
            resolve_state_path(state, path, candidate_artifacts["source"], must_exist=True)
        )
    if new == "DRAFTED":
        lesson["attempts"]["draft"] += 1
        hashes = lesson.setdefault("artifact_sha256", {})
        for key in ("source", "faithful", "lecture", "uncertainties", "coverage"):
            value = candidate_artifacts.get(key)
            if value:
                actual = resolve_state_path(state, path, value, must_exist=True)
                if actual.is_file():
                    hashes[key] = sha256_file(actual)
    if new in {"SEMANTIC_QA_PASS", "FIX_REQUIRED", "ESCALATED"} and not administrative_escalation:
        # The exact evidence selected and validated above is recorded before the QA
        # attempt counter changes; targeted round two therefore cannot be reclassified.
        if actual_evidence is None:
            raise ValueError("validated semantic evidence was not registered")
        evidence_key, evidence_path, evidence_data = actual_evidence
        digest = sha256_file(evidence_path)
        lesson.setdefault("artifact_sha256", {})[evidence_key] = digest
        lesson.setdefault("semantic_evidence_history", []).append({
            "at": stamp,
            "kind": evidence_key,
            "path": str(evidence_path),
            "sha256": digest,
            "review_round": int(evidence_data.get("review_round", expected_round)),
            "review_scope": evidence_data.get("review_scope"),
            "input_sha256": dict(evidence_data.get("input_sha256", {})),
            "reviewer_model": evidence_data.get("reviewer_model"),
            "decision": evidence_data.get("decision"),
        })
        lesson["attempts"]["qa"] += 1
        if strong_recovery:
            lesson["strong_adjudication_pending"] = False
    if old == "FIX_REQUIRED" and new == "DRAFTED":
        lesson["attempts"]["rework"] += 1
    if old == "ESCALATED" and new == "DRAFTED":
        lesson["attempts"]["strong_adjudication"] = lesson["attempts"].get("strong_adjudication", 0) + 1
        lesson["strong_adjudication_pending"] = True
    if new == "PROMOTED":
        hashes = lesson.setdefault("artifact_sha256", {})
        hashes["official_faithful"] = sha256_file(resolve_state_path(state, path, candidate_artifacts["official_faithful"], must_exist=True))
        hashes["official_lecture"] = sha256_file(resolve_state_path(state, path, candidate_artifacts["official_lecture"], must_exist=True))
        lesson["promotion_baseline"] = {
            "input_sha256": bound_input_hashes(lesson),
            "official_faithful": hashes["official_faithful"],
            "official_lecture": hashes["official_lecture"],
            "at": stamp,
        }
    if new == "ACCEPTED":
        if visual_enabled(state):
            for key in ("official_visual_md", "official_visual_html", "visual_report"):
                if key in candidate_artifacts:
                    lesson.setdefault("artifact_sha256", {})[key] = sha256_file(
                        resolve_state_path(state, path, candidate_artifacts[key], must_exist=True)
                    )
        map_path = resolve_state_path(state, path, candidate_artifacts["course_map"], must_exist=True)
        map_hash = sha256_file(map_path)
        lesson.setdefault("artifact_sha256", {})["course_map"] = map_hash
        state["shared_artifacts"] = {
            **state.get("shared_artifacts", {}),
            "course_map": {"path": str(map_path), "sha256": map_hash, "updated_at": stamp, "updated_by_lesson": args.lesson},
        }
    if production and cost_bearing:
        if new == "DRAFTED":
            phase = "rework" if old in {"FIX_REQUIRED", "ESCALATED"} else "draft"
        else:
            phase = "recheck" if expected_round > 1 else "qa"
        add_usage(lesson, args.phase or phase, charge_tokens, charge_wall, charge_calls)
        lesson.pop("budget_credit", None)
    state["updated_at"] = stamp
    atomic_write(path, state)
    print(json.dumps({"lesson": args.lesson, "from": old, "to": new}, ensure_ascii=False))
    return 0


def render_paths(state: dict, lesson: dict, state_path: Path | None = None) -> dict[str, str]:
    template = state.get("production", {}).get("naming_template", "\u7b2c{lesson_no:02d}\u8bfe\u00b7{title}.md")
    filename = template.format(lesson_no=int(lesson["lesson_no"]), title=lesson["title"])
    if not filename or Path(filename).name != filename or filename in {".", ".."}:
        raise ValueError("naming_template must render one safe filename")
    raw_root = Path(state["course_root"]).expanduser()
    if raw_root.is_absolute():
        root = raw_root.resolve()
    elif state_path is not None:
        root = resolve_state_path(state, state_path, state["course_root"], must_exist=False)
    else:
        raise ValueError("legacy relative course_root requires the state path")
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
    if visual_enabled(state):
        visual_template = templates.get("official_visual_md", "03_Visual_Learning/{filename}")
        rel = Path(visual_template.format(
            filename=filename,
            lesson_no=int(lesson["lesson_no"]),
            title=lesson["title"],
        ))
        if rel.is_absolute() or ".." in rel.parts or rel.suffix.lower() != ".md":
            raise ValueError("unsafe path template: official_visual_md")
        target = (root / rel).resolve()
        if root not in target.parents:
            raise ValueError("path escapes course_root: official_visual_md")
        runtime = resolve_state_path(state, state_path, state["runtime_dir"], must_exist=False) / f"lesson-{lesson['lesson_no']}"
        result.update({
            "official_visual_md": str(target),
            "official_visual_html": str(target.with_suffix(".html")),
            "visual_md": str(runtime / rel.name),
            "visual_html": str(runtime / rel.with_suffix(".html").name),
            "visual_report": str(runtime / "visual-result.json"),
        })
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
        **({"visual_learning": production["visual_learning"]} if "visual_learning" in production else {}),
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


def visual_learning_dependency_status() -> dict:
    root = Path(__file__).resolve().parents[2] / "pinshu-visual-learning"
    required = [root / "SKILL.md", root / "scripts" / "validate_visual_learning.py"]
    missing = [str(path.relative_to(root.parent)) for path in required if not path.is_file()]
    return {
        "available": not missing,
        "skill_root": str(root),
        "missing": missing,
        "public_candidate_member": False,
    }


def cmd_paths(args: argparse.Namespace) -> int:
    state_path = Path(args.state).resolve()
    state = load_json(state_path)
    lesson = get_lesson(state, args.lesson)
    print(json.dumps({"lesson_no": args.lesson, "paths": render_paths(state, lesson, state_path)}, ensure_ascii=False, indent=2))
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


def cmd_preflight(args: argparse.Namespace) -> int:
    state_path = Path(args.state).resolve()
    state = load_json(state_path)
    lesson = get_lesson(state, args.lesson)
    if lesson.get("status") != "DRAFTED":
        raise ValueError("preflight requires DRAFTED")
    required = ["source", "faithful", "lecture", "uncertainties"]
    if state_profile(state, lesson) == "strict":
        required.append("coverage")
    paths = {key: artifact_path(state, state_path, lesson, key) for key in required}
    visual = state.get("production", {}).get("visual_learning", {})
    if visual.get("enabled"):
        dependency = visual_learning_dependency_status()
        if not dependency["available"]:
            lesson.setdefault("dependency_blocks", {})["visual_learning"] = dependency
            lesson["last_reason"] = "visual_learning enabled but the public dependency is incomplete"
    report_arg = args.report or args.json_out
    if report_arg:
        report_path = Path(report_arg).expanduser()
        if not report_path.is_absolute():
            raise ValueError("--report/--json-out must be an absolute path")
        report_path = report_path.resolve()
    else:
        control = path_anchors(state, state_path)[0]
        report_path = control / f"lesson-{args.lesson}" / "mechanical-report.json"
    report_path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(suffix=".json", delete=False, dir=str(report_path.parent)) as handle:
        raw_report = Path(handle.name)
    try:
        command = [sys.executable, str(Path(__file__).with_name("validate_lesson.py")),
                   "--profile", state_profile(state, lesson),
                   "--source", str(paths["source"]), "--faithful", str(paths["faithful"]),
                   "--lecture", str(paths["lecture"]), "--uncertainties", str(paths["uncertainties"]),
                   "--json-out", str(raw_report)]
        if "coverage" in paths:
            command.extend(["--coverage", str(paths["coverage"])])
        result = subprocess.run(command, text=True, capture_output=True)
        mechanical = load_json(raw_report)
    finally:
        if raw_report.exists():
            raw_report.unlink()
    report = {
        **mechanical,
        "schema_version": REPORT_SCHEMA_VERSION,
        "report_type": "mechanical_report",
        "course_id": state.get("course_id"),
        "lesson_no": int(lesson["lesson_no"]),
        "reviewer_kind": "deterministic_validator",
        "reviewer_model": "none",
        "assurance_mode": state_profile(state, lesson),
        "review_round": int(lesson.get("attempts", {}).get("qa", 0)) + 1,
        "review_scope": "mechanical_only",
        "decision": "mechanical_pass" if result.returncode == 0 else "mechanical_fail",
        "recommended_state": "MECHANICAL_PASS" if result.returncode == 0 else "DRAFTED",
        "source_identity": {"passed": None, "mechanical_only": True},
        "coverage": {"passed": None, "mechanical_only": True, "statistics": mechanical.get("metrics", {})},
        "algorithm_version": MECHANICAL_ALGORITHM_VERSION,
        "statistics_definition": "UTF-8 text shape, placeholders, declared ledger counts, and SHA-256 bindings; no semantic judgment",
    }
    atomic_write(report_path, report)
    lesson.setdefault("artifacts", {})["mechanical_report"] = str(report_path)
    lesson.setdefault("artifact_sha256", {})["mechanical_report"] = sha256_file(report_path)
    stamp = now()
    if result.returncode == 0:
        validate_mechanical_report(report_path, state, lesson)
        lesson["history"].append({"at": stamp, "from": "DRAFTED", "to": "MECHANICAL_PASS", "reason": "deterministic preflight passed"})
        lesson["status"] = "MECHANICAL_PASS"
        lesson["last_reason"] = "deterministic preflight passed; semantic review remains pending"
    else:
        lesson["last_reason"] = "deterministic preflight failed; see bound report"
    lesson["updated_at"] = stamp
    state["updated_at"] = stamp
    atomic_write(state_path, state)
    print(json.dumps({"lesson": args.lesson, "mechanical_pass": result.returncode == 0,
                      "semantic_pass": None, "report": str(report_path)}, ensure_ascii=False))
    return 0 if result.returncode == 0 else 1


def parse_artifact_args(items: list[str] | None, allowed: set[str]) -> dict[str, str]:
    parsed: dict[str, str] = {}
    for item in items or []:
        if "=" not in item:
            raise ValueError("artifact must be key=/absolute/path")
        key, value = item.split("=", 1)
        if key not in allowed or key in parsed:
            raise ValueError(f"invalid or duplicate artifact key: {key}")
        path = Path(value).expanduser()
        if not path.is_absolute() or not path.is_file():
            raise ValueError(f"artifact must be an existing absolute file: {key}")
        parsed[key] = str(path.resolve())
    return parsed


def cmd_self_rework(args: argparse.Namespace) -> int:
    state_path = Path(args.state).resolve()
    state = load_json(state_path)
    lesson = get_lesson(state, args.lesson)
    old_status = lesson.get("status")
    if old_status not in {"DRAFTED", "MECHANICAL_PASS"}:
        raise ValueError("self-rework is allowed only from DRAFTED or MECHANICAL_PASS")
    if int(lesson.get("attempts", {}).get("qa", 0)) != 0 or lesson.get("semantic_evidence_history"):
        raise ValueError("self-rework is forbidden after independent or semantic QA begins")
    budget = lesson.get("effective_policy", {}).get("budgets", {}).get("max_reworks_per_lesson", 1)
    if int(lesson.get("attempts", {}).get("rework", 0)) >= int(budget):
        raise ValueError("self-rework budget exhausted")
    updates = parse_artifact_args(args.artifact, {"faithful", "lecture", "uncertainties", "coverage"})
    if not updates:
        raise ValueError("self-rework requires changed artifact files")
    before = dict(lesson.get("artifact_sha256", {}))
    after = dict(before)
    for key, value in updates.items():
        after[key] = sha256_file(Path(value))
    if not any(before.get(key) != after.get(key) for key in ("faithful", "lecture")):
        raise ValueError("self-rework requires a real faithful or lecture hash change")
    lesson.setdefault("artifacts", {}).update(updates)
    lesson["artifacts"].pop("mechanical_report", None)
    after.pop("mechanical_report", None)
    lesson["artifact_sha256"] = after
    lesson["status"] = "DRAFTED"
    lesson.setdefault("attempts", {})["rework"] = int(lesson.get("attempts", {}).get("rework", 0)) + 1
    stamp = now()
    lesson.setdefault("rework_history", []).append({
        "at": stamp, "phase": "writer_self_rework", "reason": args.reason,
        "before_sha256": before, "after_sha256": after,
        "count": lesson["attempts"]["rework"],
    })
    lesson["history"].append({"at": stamp, "from": old_status, "to": "DRAFTED",
                              "reason": args.reason, "phase": "writer_self_rework"})
    add_usage(lesson, "rework", int(args.tokens_used or 0), float(args.wall_minutes_used or 0), int(args.agent_calls or 0))
    lesson["updated_at"] = stamp
    state["updated_at"] = stamp
    atomic_write(state_path, state)
    print(json.dumps({"lesson": args.lesson, "status": "DRAFTED", "qa_rounds": lesson["attempts"].get("qa", 0),
                      "rework_count": lesson["attempts"]["rework"]}, ensure_ascii=False))
    return 0


def select_case_library(state: dict, state_path: Path, lesson: dict) -> dict:
    config = state.get("production", {}).get("case_library")
    if not config:
        return {"status": "unresolved", "reason": "case_library is not configured", "cases": []}
    if isinstance(config, str):
        library_path = resolve_state_path(state, state_path, config, must_exist=True)
    elif isinstance(config, dict) and isinstance(config.get("path"), str):
        library_path = resolve_state_path(state, state_path, config["path"], must_exist=True)
    else:
        return {"status": "unresolved", "reason": "case_library path is not configured", "cases": []}
    data = load_json(library_path)
    records = data.get("cases", []) if isinstance(data, dict) else []
    flags = set(lesson.get("effective_policy", {}).get("risk_flags", []))
    adapters = lesson.get("effective_policy", {}).get("adapters", {})
    scopes = {state_profile(state, lesson), *adapters.get("domain", []), *adapters.get("content", [])}
    selected = []
    today = datetime.now(timezone.utc).date().isoformat()
    for record in records:
        if not isinstance(record, dict) or record.get("status") != "confirmed":
            continue
        if record.get("expires_at") and str(record["expires_at"]) < today:
            continue
        triggers = set(record.get("triggers", []))
        record_scopes = set(record.get("scopes", []))
        if triggers and not (triggers & flags):
            continue
        if record_scopes and not (record_scopes & scopes):
            continue
        if not all(isinstance(record.get(k), str) and record[k].strip() for k in ("principle", "check_method")):
            continue
        selected.append({"principle": record["principle"], "triggers": sorted(triggers),
                         "check_method": record["check_method"]})
    return {"status": "resolved", "path": str(library_path), "cases": selected}


def cmd_work_order(args: argparse.Namespace) -> int:
    state_path = Path(args.state).resolve()
    state = load_json(state_path)
    lesson = get_lesson(state, args.lesson)
    result = {
        "course_id": state.get("course_id"), "lesson_no": args.lesson,
        "status": lesson.get("status"), "assurance_mode": state_profile(state, lesson),
        "output_language": state.get("production", {}).get("output_language", "match-user"),
        "paths": render_paths(state, lesson, state_path),
        "artifacts": {key: str(resolve_state_path(state, state_path, value, must_exist=False))
                      for key, value in lesson.get("artifacts", {}).items()},
        "usage": normalize_usage(lesson),
        "case_library": select_case_library(state, state_path, lesson),
    }
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


def markdown_visible_body(text: str) -> str:
    body = FRONTMATTER_BLOCK.sub("", text.replace("\r\n", "\n"), count=1)
    return MARKDOWN_LINK.sub(lambda match: match.group(1), body)


def conservative_semantic_fingerprint(text: str) -> str:
    body = FRONTMATTER_BLOCK.sub("", text.replace("\r\n", "\n"), count=1)
    tokens = re.findall(r"https?://[^\s)>]+|`[^`]*`|\d+(?:[.,]\d+)*|[A-Za-z]+(?:[-'][A-Za-z]+)*|[\u3400-\u9fff]", body)
    return hashlib.sha256("\n".join(tokens).encode("utf-8")).hexdigest()


def revision_hashes(state: dict, state_path: Path, lesson: dict) -> dict[str, str]:
    hashes = {"source": sha256_file(artifact_path(state, state_path, lesson, "source")),
              "faithful": sha256_file(artifact_path(state, state_path, lesson, "official_faithful")),
              "lecture": sha256_file(artifact_path(state, state_path, lesson, "official_lecture"))}
    if lesson.get("artifacts", {}).get("uncertainties"):
        hashes["uncertainties"] = sha256_file(artifact_path(state, state_path, lesson, "uncertainties"))
    if lesson.get("artifacts", {}).get("coverage"):
        hashes["coverage"] = sha256_file(artifact_path(state, state_path, lesson, "coverage"))
    shared_map = state.get("shared_artifacts", {}).get("course_map")
    if isinstance(shared_map, dict) and shared_map.get("path"):
        hashes["course_map"] = sha256_file(resolve_state_path(state, state_path, shared_map["path"], must_exist=True))
    return hashes


def cmd_revision_open(args: argparse.Namespace) -> int:
    state_path = Path(args.state).resolve()
    state = load_json(state_path)
    lesson = get_lesson(state, args.lesson)
    if lesson.get("status") != "ACCEPTED":
        raise ValueError("revision-open requires ACCEPTED")
    if isinstance(lesson.get("revision"), dict) and lesson["revision"].get("status") == "open":
        raise ValueError("a revision is already open")
    baseline = revision_hashes(state, state_path, lesson)
    stamp = now()
    control = Path(state.get("path_context", {}).get("control_dir", state_path.parent)).resolve()
    revision_id = re.sub(r"[^0-9]", "", stamp)[:20] + f"-lesson-{args.lesson}"
    snapshot_dir = control / "revisions" / revision_id
    snapshot_dir.mkdir(parents=True, exist_ok=False)
    snapshots = {}
    for key in ("official_faithful", "official_lecture"):
        src = artifact_path(state, state_path, lesson, key)
        dst = snapshot_dir / f"{key}-{src.name}"
        shutil.copy2(src, dst)
        snapshots[key] = {"path": str(dst), "sha256": sha256_file(dst)}
    state_snapshot = snapshot_dir / "course-state.json"
    atomic_write(state_snapshot, state)
    shared = state.get("shared_artifacts", {}).get("course_map")
    shared_snapshot = None
    if isinstance(shared, dict) and shared.get("path"):
        shared_path = resolve_state_path(state, state_path, shared["path"], must_exist=True)
        dst = snapshot_dir / "course-map.md"
        shutil.copy2(shared_path, dst)
        shared_snapshot = {"path": str(dst), "sha256": sha256_file(dst)}
    lesson["revision"] = {
        "status": "open", "revision_id": revision_id, "type": args.type, "reason": args.reason,
        "opened_at": stamp, "baseline_sha256": baseline, "snapshots": snapshots,
        "state_snapshot": {"path": str(state_snapshot), "sha256": sha256_file(state_snapshot)},
        "shared_course_map_snapshot": shared_snapshot,
    }
    state["updated_at"] = stamp
    atomic_write(state_path, state)
    print(json.dumps({"lesson": args.lesson, "revision_id": revision_id, "type": args.type,
                      "status": "open", "snapshot_dir": str(snapshot_dir)}, ensure_ascii=False))
    return 0


def markdown_revision_fingerprint(path: Path, *, ignore_metadata_and_links: bool) -> str:
    text = path.read_text(encoding="utf-8")
    if ignore_metadata_and_links:
        text = FRONTMATTER_BLOCK.sub("", text.replace("\r\n", "\n"), count=1)
        text = re.sub(r"!\[([^\]]*)\]\([^)]+\)", r"IMAGE[\1]", text)
        text = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", text)
        text = re.sub(r"!\[\[([^\]|]+)(?:\|[^\]]+)?\]\]", r"IMAGE[\1]", text)
        text = re.sub(r"\[\[([^\]|]+)(?:\|([^\]]+))?\]\]", lambda m: m.group(2) or m.group(1), text)
    text = re.sub(r"(?m)^\s{0,3}(?:#{1,6}|>|[-+*]\s|\d+[.)]\s)", "", text)
    text = text.replace("**", "").replace("__", "").replace("~~", "").replace("`", "")
    text = re.sub(r"[|]", "", text)
    text = re.sub(r"\s+", "", text)
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def revision_snapshot_file(revision: dict, key: str) -> Path:
    snapshots = revision.get("snapshots", {})
    if isinstance(snapshots, dict) and key in snapshots:
        path = Path(snapshots[key]["path"])
        if path.is_file():
            return path
    matches = [Path(item["path"]) for item in revision.get("snapshot_files", []) if item.get("key") == key]
    if len(matches) == 1 and matches[0].is_file():
        return matches[0]
    raise ValueError(f"revision snapshot is missing exactly one {key}")


def revision_hashes_for_artifacts(state: dict, state_path: Path, lesson: dict, artifacts: dict[str, str]) -> dict[str, str]:
    def digest(key: str) -> str:
        return sha256_file(resolve_state_path(state, state_path, artifacts[key], must_exist=True))

    hashes = {
        "source": sha256_file(artifact_path(state, state_path, lesson, "source")),
        "faithful": digest("official_faithful"),
        "lecture": digest("official_lecture"),
    }
    if artifacts.get("uncertainties"):
        hashes["uncertainties"] = digest("uncertainties")
    if artifacts.get("coverage"):
        hashes["coverage"] = digest("coverage")
    if artifacts.get("course_map"):
        hashes["course_map"] = digest("course_map")
    return hashes


def validate_revision_qa_report(path: Path, state: dict, lesson: dict,
                                current_inputs: dict[str, str]) -> dict:
    data = load_json(path)
    if data.get("schema_version") == REPORT_SCHEMA_VERSION or data.get("report_type") == "qa_report":
        return validate_qa_report(
            path,
            state,
            lesson,
            "SEMANTIC_QA_PASS",
            expected_round=int(lesson.get("attempts", {}).get("qa", 0)) + 1,
            allowed_scopes={"revision_content", "revision_formatting", "full", "targeted_recheck"},
            expected_hashes=current_inputs,
        )
    require_fields(data, {"schema_version", "kind", "course_id", "lesson_no", "reviewer_kind",
                          "reviewer_model", "review_scope", "decision", "source_identity", "coverage",
                          "issues", "input_sha256", "checked_at"}, "revision qa_report")
    if (data.get("schema_version") != 1 or data.get("kind") != "qa_report"
            or data.get("reviewer_kind") != "independent_qa" or data.get("decision") != "pass"):
        raise ValueError("revision QA must be a passing independent qa_report")
    if data.get("course_id") != state.get("course_id") or int(data.get("lesson_no", 0)) != int(lesson["lesson_no"]):
        raise ValueError("revision qa_report course_id or lesson_no mismatch")
    if data.get("reviewer_model") not in {state.get("models", {}).get("qa"), state.get("models", {}).get("strong")}:
        raise ValueError("revision qa_report reviewer_model mismatch")
    if data.get("review_scope") not in {"full", "targeted_recheck", "revision_content", "revision_formatting"}:
        raise ValueError("revision qa_report must use full or targeted_recheck scope")
    if data.get("input_sha256") != current_inputs:
        raise ValueError("revision qa_report does not bind the revised deliverables")
    if data.get("source_identity", {}).get("passed") is not True or data.get("coverage", {}).get("passed") is not True:
        raise ValueError("revision qa_report source identity and coverage must pass")
    unresolved = [x for x in data.get("issues", [])
                  if x.get("severity") == "high" and x.get("resolved") is not True]
    if unresolved:
        raise ValueError("revision qa_report cannot pass with unresolved high issues")
    return data


def validate_revision_report(path: Path, state: dict, lesson: dict, revision: dict,
                             new_hashes: dict[str, str]) -> dict:
    data = load_json(path)
    revision_id = revision.get("revision_id", revision.get("id"))
    if data.get("kind") == "revision_report":
        required = {"schema_version", "kind", "revision_id", "revision_type", "decision", "baseline_sha256", "input_sha256"}
        missing = required - set(data)
        if missing:
            raise ValueError("revision_report missing fields: " + ", ".join(sorted(missing)))
        if data.get("schema_version") != 1 or data.get("decision") != "pass":
            raise ValueError("revision_report must be a passing schema_version 1 revision_report")
        if data.get("revision_id") != revision_id or data.get("revision_type") != revision.get("type"):
            raise ValueError("revision_report identity mismatch")
        if data.get("baseline_sha256") != revision.get("baseline_sha256") or data.get("input_sha256") != new_hashes:
            raise ValueError("revision_report hashes do not bind the accepted baseline and revised files")
        return data
    if "semantic_equivalent" in data:
        raise ValueError("revision_report may not self-declare semantic_equivalent")
    required = {"schema_version", "report_type", "course_id", "lesson_no", "revision_id", "revision_type",
                "reason", "baseline_sha256", "new_sha256"}
    missing = required - set(data)
    if missing:
        raise ValueError("revision_report missing fields: " + ", ".join(sorted(missing)))
    if data.get("schema_version") != 1 or data.get("report_type") != "revision_report":
        raise ValueError("revision_report schema or report_type is invalid")
    if data.get("course_id") != state.get("course_id") or int(data.get("lesson_no", 0)) != int(lesson["lesson_no"]):
        raise ValueError("revision_report identity mismatch")
    if data.get("revision_id") != revision_id or data.get("revision_type") != revision.get("type"):
        raise ValueError("revision_report round or type mismatch")
    if data.get("baseline_sha256") != revision.get("baseline_sha256") or data.get("new_sha256") != new_hashes:
        raise ValueError("revision_report hash binding mismatch")
    return data


def cmd_revision_close(args: argparse.Namespace) -> int:
    state_path = Path(args.state).resolve()
    state = load_json(state_path)
    lesson = get_lesson(state, args.lesson)
    validate_usage_delta(int(args.tokens_used or 0), float(args.wall_minutes_used or 0), int(args.agent_calls or 1))
    revision = lesson.get("revision")
    if lesson.get("status") != "ACCEPTED" or not isinstance(revision, dict) or revision.get("status") != "open":
        raise ValueError("revision-close requires an open revision on ACCEPTED")
    report_path = Path(args.revision_report).expanduser()
    if not report_path.is_absolute() or not report_path.is_file():
        raise ValueError("--revision-report must be an existing absolute file")
    replacements = parse_artifact_args(
        args.artifact,
        {"official_faithful", "official_lecture", "course_map", "official_visual_md", "official_visual_html"},
    )
    candidate_artifacts = dict(lesson.get("artifacts", {}))
    candidate_artifacts.update(replacements)
    expected_paths = render_paths(state, lesson, state_path)
    for key in replacements:
        actual = resolve_state_path(state, state_path, candidate_artifacts[key], must_exist=True)
        if key in expected_paths and actual != Path(expected_paths[key]).resolve():
            raise ValueError(f"revision artifact must use the manifest-rendered path: {key}")
    new_hashes = revision_hashes_for_artifacts(state, state_path, lesson, candidate_artifacts)
    validate_revision_report(report_path, state, lesson, revision, new_hashes)
    baseline = revision["baseline_sha256"]
    revision_type = revision["type"]
    qa_required = revision_type == "content"
    if revision_type == "metadata_link_only":
        for key, official_key in (("official_faithful", "official_faithful"), ("official_lecture", "official_lecture")):
            old_text = revision_snapshot_file(revision, key).read_text(encoding="utf-8")
            current_path = resolve_state_path(state, state_path, candidate_artifacts[official_key], must_exist=True)
            new_text = current_path.read_text(encoding="utf-8")
            if markdown_visible_body(old_text) != markdown_visible_body(new_text):
                raise ValueError("metadata/link revision changed visible body text")
            if any(not target.is_file() for target in local_link_targets(current_path, new_text)):
                raise ValueError("metadata/link revision contains a broken local link")
        validate_promotion_hygiene(state, state_path, lesson, candidate_artifacts)
    elif revision_type == "formatting":
        for key, official_key in (("official_faithful", "official_faithful"), ("official_lecture", "official_lecture")):
            old_path = revision_snapshot_file(revision, key)
            new_path = resolve_state_path(state, state_path, candidate_artifacts[official_key], must_exist=True)
            old_text = old_path.read_text(encoding="utf-8")
            new_text = new_path.read_text(encoding="utf-8")
            if conservative_semantic_fingerprint(old_text) != conservative_semantic_fingerprint(new_text):
                qa_required = True
            if markdown_revision_fingerprint(old_path, ignore_metadata_and_links=False) != markdown_revision_fingerprint(new_path, ignore_metadata_and_links=False):
                qa_required = True
        validate_promotion_hygiene(state, state_path, lesson, candidate_artifacts)
    qa_path = None
    if qa_required:
        if not args.qa_report:
            raise ValueError(f"{revision_type} revision requires independent --qa-report")
        qa_path = Path(args.qa_report).expanduser()
        if not qa_path.is_absolute() or not qa_path.is_file():
            raise ValueError("--qa-report must be an existing absolute file")
        validate_revision_qa_report(qa_path, state, lesson, {k: v for k, v in new_hashes.items() if k != "course_map"})
    elif args.qa_report:
        raise ValueError("deterministically equivalent revision must not attach an unvalidated optional QA report")
    stamp = now()
    revision.update({"status": "closed", "closed_at": stamp, "new_sha256": new_hashes,
                     "revision_report": {"path": str(report_path.resolve()), "sha256": sha256_file(report_path)},
                     "qa_report": ({"path": str(qa_path.resolve()), "sha256": sha256_file(qa_path)} if qa_path else None),
                     "deterministic_equivalence": not qa_required})
    hashes = lesson.setdefault("artifact_sha256", {})
    lesson["artifacts"] = candidate_artifacts
    hashes["source"] = new_hashes["source"]
    hashes["official_faithful"] = new_hashes["faithful"]
    hashes["official_lecture"] = new_hashes["lecture"]
    if "course_map" in new_hashes and isinstance(state.get("shared_artifacts", {}).get("course_map"), dict):
        state["shared_artifacts"]["course_map"]["sha256"] = new_hashes["course_map"]
        state["shared_artifacts"]["course_map"]["updated_at"] = stamp
        lesson["artifact_sha256"]["course_map"] = new_hashes["course_map"]
    if qa_path:
        hashes["qa_report"] = sha256_file(qa_path)
        lesson.setdefault("semantic_evidence_history", []).append({
            "at": stamp, "kind": "qa_report", "path": str(qa_path.resolve()), "sha256": hashes["qa_report"],
            "review_round": int(lesson.get("attempts", {}).get("qa", 0)) + 1,
            "review_scope": f"revision_{revision_type}", "input_sha256": new_hashes,
            "reviewer_model": state.get("models", {}).get("qa"), "decision": "pass",
        })
        lesson["attempts"]["qa"] = int(lesson.get("attempts", {}).get("qa", 0)) + 1
    add_usage(lesson, "revision", int(args.tokens_used or 0), float(args.wall_minutes_used or 0), int(args.agent_calls or 0))
    lesson["updated_at"] = stamp
    state["updated_at"] = stamp
    atomic_write(state_path, state)
    print(json.dumps({"lesson": args.lesson, "revision_id": revision["revision_id"], "status": "closed",
                      "qa_bound": bool(qa_path), "new_sha256": new_hashes}, ensure_ascii=False))
    return 0


def visual_enabled(state: dict) -> bool:
    return state.get("production", {}).get("visual_learning", {}).get("enabled") is True


def markdown_images(path: Path) -> list[Path]:
    text = path.read_text(encoding="utf-8")
    refs = re.findall(r"!\[[^\]]*\]\(\s*(<[^>]+>|[^)]+)\)", text)
    refs += re.findall(r"!\[\[([^\]]+)\]\]", text)
    images: list[Path] = []
    for ref in refs:
        ref = ref.strip()
        if ref.startswith("<"):
            ref = ref[1:ref.index(">")]
        else:
            ref = re.split(r'\s+["\']', ref, maxsplit=1)[0]
        ref = unquote(ref.split("|", 1)[0])
        if re.match(r"^[a-zA-Z][\w+.-]*:", ref) or ref.startswith("//"):
            raise ValueError("visual Markdown must embed local PNG images")
        image = (path.parent / ref).resolve()
        if image.suffix.lower() != ".png" or not image.is_file():
            raise ValueError(f"visual Markdown image missing or not PNG: {ref}")
        images.append(image)
    if not images:
        raise ValueError("visual Markdown requires individually embedded PNG diagrams")
    return images


def run_visual_mechanical(md: Path, html: Path, *, formal: bool, mobile_content_width: float,
                          link_base: Path | None = None) -> None:
    validator = Path(__file__).resolve().parents[2] / "pinshu-visual-learning" / "scripts" / "validate_visual_learning.py"
    if not validator.is_file():
        raise ValueError("pinshu-visual-learning validator dependency is missing; release package is incomplete")
    command = [sys.executable, str(validator), "--md", str(md), "--html", str(html),
               "--mobile-content-width", str(mobile_content_width)]
    if formal:
        command.append("--formal")
    if link_base is not None:
        command += ["--link-base", str(link_base)]
    cp = subprocess.run(command, text=True, capture_output=True)
    if cp.returncode:
        try:
            detail = "; ".join(json.loads(cp.stdout).get("errors", []))
        except (json.JSONDecodeError, AttributeError):
            detail = cp.stderr.strip() or cp.stdout.strip()
        raise ValueError("visual mechanical validation failed: " + detail)


def validate_mobile_evidence(data: dict) -> float:
    evidence = data.get("mobile_evidence")
    if not isinstance(evidence, dict):
        raise ValueError("visual_report requires mobile_evidence")
    viewport = evidence.get("viewport_width_px")
    content = evidence.get("content_width_px")
    diagrams = evidence.get("diagrams")
    if (not isinstance(viewport, (int, float)) or not isinstance(content, (int, float))
            or viewport <= 0 or content <= 0 or content > viewport
            or not isinstance(diagrams, list) or not diagrams):
        raise ValueError("mobile_evidence requires positive measured viewport/content widths and diagrams")
    for diagram in diagrams:
        if not isinstance(diagram, dict) or not str(diagram.get("path", "")).strip():
            raise ValueError("mobile_evidence diagram requires path")
        width = diagram.get("rendered_width_px")
        font = diagram.get("min_display_font_px")
        if (not isinstance(width, (int, float)) or width <= 0 or width > content + 0.5
                or diagram.get("horizontal_overflow") is not False):
            raise ValueError("mobile diagram must fit the measured content column without horizontal overflow")
        if not isinstance(font, (int, float)) or font < 11:
            raise ValueError("mobile diagram minimum displayed font must be at least 11px")
    return float(content)


def validate_obsidian_evidence(data: dict) -> None:
    evidence = data.get("obsidian_evidence")
    if (not isinstance(evidence, dict) or evidence.get("checked_by") not in {"agent", "user"}
            or evidence.get("whole_document_checked") is not True
            or not isinstance(evidence.get("evidence"), list) or not evidence["evidence"]
            or any(not isinstance(x, str) or not x.strip() for x in evidence["evidence"])):
        raise ValueError("obsidian_render=true requires agent/user real-reading evidence for the whole document")


def validate_visual_result(state: dict, lesson: dict, artifacts: dict, *, formal: bool = False,
                           allow_blocked: bool = False, check_batch: bool = True,
                           state_path: Path | None = None,
                           lecture_hash_override: str | None = None) -> dict:
    stable = state_path or (Path(state.get("path_context", {}).get("control_dir", ".")) / "course-state.json")
    if check_batch:
        require_visual_permission(state, lesson, stable)
    report_value = artifacts.get("visual_report")
    report_path = resolve_state_path(state, stable, report_value, must_exist=True) if report_value else None
    if not report_path or not report_path.is_file():
        raise ValueError("enabled visual learning requires visual_report")
    if formal:
        bound = lesson.get("artifact_sha256", {}).get("visual_report")
        recorded = lesson.get("artifacts", {}).get("visual_report")
        recorded_path = resolve_state_path(state, stable, recorded, must_exist=True) if recorded else None
        if not bound or sha256_file(report_path) != bound or report_path != recorded_path:
            raise ValueError("artifact integrity failed visual_report")
    data = load_json(report_path)
    if (data.get("schema_version") != 1 or data.get("kind") != "visual_learning"
            or data.get("course_id") != state.get("course_id") or int(data.get("lesson_no", 0)) != int(lesson["lesson_no"])):
        raise ValueError("visual_report identity or schema mismatch")
    for key in ("reviewer_model", "reviewer_kind", "checked_at"):
        if not isinstance(data.get(key), str) or not data[key].strip():
            raise ValueError(f"visual_report requires {key}")
    checks = data.get("checks")
    if not isinstance(checks, dict) or any(not isinstance(checks.get(k), bool) for k in
            ("semantic", "desktop_render", "mobile_render", "obsidian_render")):
        raise ValueError("visual_report requires boolean semantic/desktop/mobile/obsidian checks")
    inputs = data.get("input_sha256")
    if not isinstance(inputs, dict):
        raise ValueError("visual_report input_sha256 must be an object")
    lecture_hash = lecture_hash_override or lesson.get("artifact_sha256", {}).get("lecture")
    if not lecture_hash or inputs.get("lecture") != lecture_hash:
        raise ValueError("visual_report input_sha256.lecture mismatch")
    lecture_value = artifacts.get("official_lecture") if formal else artifacts.get("lecture")
    lecture_path = resolve_state_path(state, stable, lecture_value, must_exist=True) if lecture_value else None
    if not lecture_path or sha256_file(lecture_path) != lecture_hash:
        raise ValueError("artifact integrity failed lecture")
    decision = data.get("decision")
    if decision == "skipped":
        if (data.get("skip_code") != "no_reliable_visual_source" or checks["semantic"] is not True
                or not isinstance(data.get("skip_reason"), str) or len(data["skip_reason"].strip()) < 20
                or not isinstance(data.get("source_limitations"), list) or not data["source_limitations"]):
            raise ValueError("skipped visual needs concrete no-reliable-source evidence, not a generic bypass")
        return data
    if decision == "blocked" and allow_blocked:
        if not isinstance(data.get("blocking_reason"), str) or not data["blocking_reason"].strip():
            raise ValueError("blocked visual requires blocking_reason")
        return data
    if decision != "pass" or not all(checks.values()):
        raise ValueError("visual learning is not passed: all four real checks must be true")
    mobile_content_width = validate_mobile_evidence(data)
    validate_obsidian_evidence(data)
    paths = render_paths(state, lesson, stable)
    for key in ("visual_md", "visual_html"):
        actual = resolve_state_path(state, stable, artifacts.get(key), must_exist=True) if artifacts.get(key) else None
        if not actual or actual != Path(paths[key]).resolve():
            raise ValueError(f"visual learning requires manifest-rendered {key}")
        if inputs.get(key) != sha256_file(actual):
            raise ValueError(f"visual_report {key} SHA256 mismatch")
        if formal:
            official_key = "official_" + key
            official = resolve_state_path(state, stable, artifacts.get(official_key), must_exist=True) if artifacts.get(official_key) else None
            if not official or official != Path(paths[official_key]).resolve() or sha256_file(official) != inputs[key]:
                raise ValueError(f"{official_key} must match validated candidate and manifest-rendered path")
    check_md = resolve_state_path(state, stable, artifacts["official_visual_md"] if formal else artifacts["visual_md"], must_exist=True)
    check_html = resolve_state_path(state, stable, artifacts["official_visual_html"] if formal else artifacts["visual_html"], must_exist=True)
    link_base = None if formal else Path(paths["official_visual_md"]).parent
    run_visual_mechanical(check_md, check_html, formal=formal, mobile_content_width=mobile_content_width,
                          link_base=link_base)
    assets = data.get("assets")
    if not isinstance(assets, list) or not assets:
        raise ValueError("visual_report requires PNG and editable SVG assets")
    by_path = {}
    for asset in assets:
        if not isinstance(asset, dict) or not isinstance(asset.get("path"), str) or not Path(asset["path"]).is_absolute():
            raise ValueError("visual_report asset path must be absolute")
        p = Path(asset["path"]).resolve()
        if str(p) in by_path or not p.is_file() or sha256_file(p) != asset.get("sha256"):
            raise ValueError(f"visual asset integrity failed: {p}")
        by_path[str(p)] = asset["sha256"]
    images = markdown_images(resolve_state_path(state, stable, artifacts["visual_md"], must_exist=True))
    if any(str(p) not in by_path for p in images):
        raise ValueError("visual_report assets must bind every embedded PNG")
    if not [Path(p) for p in by_path if Path(p).suffix.lower() == ".svg"]:
        raise ValueError("visual_report requires editable SVG sources")
    return data


def visual_batch_valid(state: dict, state_path: Path | None = None) -> bool:
    config = state.get("production", {}).get("visual_learning", {})
    if config.get("batch_approved") is not True:
        return False
    approval = config.get("approval", {})
    if not all(isinstance(approval.get(k), str) and approval[k].strip() for k in ("approved_by", "approved_at")):
        return False
    try:
        pilot = get_lesson(state, int(config.get("pilot_lesson_no", state.get("sample_gate", {}).get("lesson_no", 1))))
        stable = state_path or (Path(state.get("path_context", {}).get("control_dir", ".")) / "course-state.json")
        validate_visual_result(state, pilot, pilot.get("artifacts", {}), formal=True,
                               check_batch=False, state_path=stable)
        return (pilot["status"] == "ACCEPTED"
                and approval.get("report_sha256") == pilot.get("artifact_sha256", {}).get("visual_report"))
    except (OSError, ValueError, KeyError, TypeError):
        return False


def require_visual_permission(state: dict, lesson: dict, state_path: Path | None = None) -> None:
    config = state.get("production", {}).get("visual_learning", {})
    pilot = int(config.get("pilot_lesson_no", state.get("sample_gate", {}).get("lesson_no", 1)))
    if int(lesson["lesson_no"]) != pilot and not visual_batch_valid(state, state_path):
        raise ValueError("visual sample is not user-approved or changed; only the pilot may produce graphics")


def cmd_record_visual(args: argparse.Namespace) -> int:
    path = Path(args.state).resolve()
    state = load_json(path)
    lesson = get_lesson(state, args.lesson)
    accepted_revision = lesson.get("status") == "ACCEPTED" and lesson.get("revision", {}).get("status") == "open"
    if not visual_enabled(state) or (lesson.get("status") not in {"SEMANTIC_QA_PASS", "PROMOTED"} and not accepted_revision):
        raise ValueError("record-visual requires semantic approval or an open accepted revision")
    require_visual_permission(state, lesson, path)
    artifacts = dict(lesson.get("artifacts", {}))
    artifacts["visual_report"] = str(Path(args.report).expanduser().resolve())
    artifacts.update(parse_artifact_args(args.artifact, {"visual_md", "visual_html"}))
    report = validate_visual_result(state, lesson, artifacts, allow_blocked=True, state_path=path)
    validate_usage_delta(args.tokens_used, args.wall_minutes_used, args.agent_calls)
    budgets = lesson.get("effective_policy", {}).get("budgets", state.get("production", {}).get("budgets", {}))
    payload = visual_budget_payload(args)
    credit = lesson.get("budget_credit")
    if credit and credit.get("payload") != payload:
        raise ValueError("budget recovery is pending; retry the exact blocked visual registration")
    charge_tokens = 0 if credit else args.tokens_used
    charge_wall = 0.0 if credit else args.wall_minutes_used
    charge_calls = 0 if credit else args.agent_calls
    usage = normalize_usage(lesson)
    projected = {
        "tokens": usage.get("tokens", 0) + charge_tokens,
        "wall_minutes": usage.get("wall_minutes", 0.0) + charge_wall,
        "agent_calls": usage.get("agent_calls", 0) + charge_calls,
    }
    if budget_overages(projected, budgets):
        block_for_budget(path, state, lesson, phase="visual", payload=payload,
                         prior_status=lesson["status"], tokens=charge_tokens,
                         wall=charge_wall, calls=charge_calls, budgets=budgets)
    stamp = now()
    lesson["artifacts"] = artifacts
    for key in ("visual_report", "visual_md", "visual_html"):
        if key in artifacts:
            lesson.setdefault("artifact_sha256", {})[key] = sha256_file(Path(artifacts[key]))
    add_usage(lesson, "visual", charge_tokens, charge_wall, charge_calls)
    lesson.pop("budget_credit", None)
    lesson.setdefault("visual_evidence_history", []).append({
        "at": stamp,
        "decision": report["decision"],
        "path": artifacts["visual_report"],
        "sha256": lesson["artifact_sha256"]["visual_report"],
    })
    lesson["updated_at"] = state["updated_at"] = stamp
    atomic_write(path, state)
    print(json.dumps({"lesson": args.lesson, "visual_decision": report["decision"], "status": lesson["status"]}, ensure_ascii=False))
    return 0


def cmd_approve_visual_sample(args: argparse.Namespace) -> int:
    path = Path(args.state).resolve()
    state = load_json(path)
    config = state.get("production", {}).get("visual_learning", {})
    pilot_no = int(config.get("pilot_lesson_no", state.get("sample_gate", {}).get("lesson_no", 1)))
    lesson = get_lesson(state, args.lesson)
    if not visual_enabled(state) or args.lesson != pilot_no or lesson.get("status") != "ACCEPTED":
        raise ValueError("visual approval requires the accepted enabled pilot")
    if not args.approved_by.strip():
        raise ValueError("visual approval requires approved_by")
    report = validate_visual_result(state, lesson, lesson.get("artifacts", {}), formal=True,
                                    check_batch=False, state_path=path)
    if report["decision"] != "pass":
        raise ValueError("skipped pilot cannot approve visual batches")
    config["batch_approved"] = True
    config["approval"] = {
        "approved_by": args.approved_by,
        "approved_at": now(),
        "report_sha256": lesson["artifact_sha256"]["visual_report"],
    }
    state["updated_at"] = now()
    atomic_write(path, state)
    print(json.dumps({"visual_sample_approved": args.lesson}, ensure_ascii=False))
    return 0


def cmd_audit(args: argparse.Namespace) -> int:
    state_path = Path(args.state).resolve()
    state = load_json(state_path)
    problems: list[dict] = []

    def problem(lesson: dict, category: str, detail: str) -> None:
        problems.append({"lesson": lesson["lesson_no"], "category": category, "problem": detail})

    shared_map = state.get("shared_artifacts", {}).get("course_map")
    shared_map_ok = True
    if isinstance(shared_map, dict) and shared_map.get("path"):
        try:
            current_map = resolve_state_path(state, state_path, shared_map["path"], must_exist=True)
            shared_map_ok = sha256_file(current_map) == shared_map.get("sha256")
        except ValueError:
            shared_map_ok = False
    for lesson in state["lessons"]:
        profile = state_profile(state, lesson)
        status = lesson.get("status")
        if status not in ALL_STATES:
            problem(lesson, "registration_defect", f"unknown status {status}")
            continue
        archived = lesson.get("artifacts_archived", {})
        for key in required_artifacts(status, profile):
            if key == "course_map" and status == "ACCEPTED" and isinstance(shared_map, dict):
                if not shared_map_ok:
                    problem(lesson, "formal_candidate_drift", "latest shared course_map baseline is missing or changed")
                continue
            if key in archived:
                if status != "ACCEPTED" or key not in {"faithful", "lecture", "mechanical_report"} or not valid_archived_entry(archived[key]):
                    problem(lesson, "registration_defect", f"invalid archived artifact {key}")
                continue
            value = lesson.get("artifacts", {}).get(key)
            if not value:
                category = "report_missing" if key.endswith("report") else "registration_defect"
                problem(lesson, category, f"missing artifact key {key}")
                continue
            try:
                actual = resolve_state_path(state, state_path, value, must_exist=True)
            except ValueError as exc:
                category = "report_missing" if key.endswith("report") else "registration_defect"
                problem(lesson, category, str(exc))
                continue
            expected_hash = lesson.get("artifact_sha256", {}).get(key)
            if expected_hash and sha256_file(actual) != expected_hash:
                category = "formal_candidate_drift" if key.startswith("official_") else "qa_binding_mismatch" if key in {"qa_report", "semantic_check"} else "registration_defect"
                problem(lesson, category, f"artifact integrity failed {key}")
        evidence = lesson.get("semantic_evidence_history", [])
        revision = lesson.get("revision")
        deterministic_revision = (isinstance(revision, dict) and revision.get("status") == "closed"
                                  and revision.get("deterministic_equivalence") is True)
        if status in {"SEMANTIC_QA_PASS", "PROMOTED", "ACCEPTED"}:
            if not evidence:
                problem(lesson, "registration_defect", "semantic pass has no registered evidence history")
            else:
                latest = evidence[-1]
                if (int(latest.get("review_round", 1)) > 1 or requires_full_qa(state, lesson, int(latest.get("review_round", 1)))) and latest.get("kind") != "qa_report":
                    problem(lesson, "independent_qa_missing", "current acceptance required independent QA")
                if not deterministic_revision:
                    current_inputs = revision_hashes(state, state_path, lesson) if status == "ACCEPTED" else bound_input_hashes(lesson)
                    declared = latest.get("input_sha256")
                    relevant = {k: v for k, v in current_inputs.items() if k in {"source", "faithful", "lecture", "uncertainties", "coverage"}}
                    if not isinstance(declared, dict) or any(declared.get(k) != v for k, v in relevant.items()):
                        problem(lesson, "qa_binding_mismatch", "latest semantic evidence is bound to different inputs")
        if status in {"PROMOTED", "ACCEPTED"}:
            baseline = lesson.get("promotion_baseline", {})
            for key in ("official_faithful", "official_lecture"):
                try:
                    actual_hash = sha256_file(artifact_path(state, state_path, lesson, key))
                except ValueError:
                    continue
                expected = lesson.get("artifact_sha256", {}).get(key)
                if expected != actual_hash:
                    problem(lesson, "formal_candidate_drift", f"current {key} differs from registered formal candidate")
                if status == "PROMOTED" and baseline.get(key) and baseline.get(key) != actual_hash:
                    problem(lesson, "formal_candidate_drift", f"{key} changed after promotion")
            try:
                validate_promotion_hygiene(state, state_path, lesson, lesson.get("artifacts", {}))
            except ValueError as exc:
                problem(lesson, "promotion_hygiene", str(exc))
        if isinstance(revision, dict) and revision.get("status") == "open":
            problem(lesson, "revision_open", f"revision {revision.get('revision_id')} remains open")
        if not usage_consistent(lesson):
            problem(lesson, "registration_defect", "usage phase totals do not equal lesson totals")
        if status in {"BLOCKED", "SKIPPED", "FIX_REQUIRED", "ESCALATED"} and not lesson.get("last_reason"):
            problem(lesson, "registration_defect", f"{status} requires reason")
    categories = Counter(item["category"] for item in problems)
    print(json.dumps({"ok": not problems, "categories": dict(sorted(categories.items())), "problems": problems}, ensure_ascii=False, indent=2))
    return 0 if not problems else 1


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def cmd_approve_sample(args: argparse.Namespace) -> int:
    path = Path(args.state).resolve()
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
    expected_paths = [resolve_state_path(state, path, str(x), must_exist=True) for x in expected]
    if [str(p) for p in samples] != [str(p) for p in expected_paths]:
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
    path = Path(args.state).resolve()
    state = load_json(path)
    lesson = get_lesson(state, args.lesson)
    if lesson["status"] != "ACCEPTED":
        raise ValueError("artifacts may be archived only after ACCEPTED")
    allowed = {"faithful", "lecture", "mechanical_report"}
    if args.key not in allowed:
        raise ValueError(f"artifact cannot be archived: {args.key}")
    value = lesson.get("artifacts", {}).get(args.key)
    if not value:
        raise ValueError(f"artifact not found: {args.key}")
    actual = resolve_state_path(state, path, value, must_exist=True)
    digest = sha256_file(actual)
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
    q = sub.add_parser("transition"); q.add_argument("--state", required=True); q.add_argument("--lesson", type=int, required=True); q.add_argument("--to", required=True); q.add_argument("--reason", required=True); q.add_argument("--severity", choices=["high", "note"]); q.add_argument("--tokens-used", type=int); q.add_argument("--wall-minutes-used", type=float); q.add_argument("--agent-calls", type=int); q.add_argument("--phase", choices=sorted(USAGE_PHASES)); q.add_argument("--artifact", action="append"); q.set_defaults(func=cmd_transition)
    q = sub.add_parser("set-budget"); q.add_argument("--state", required=True); q.add_argument("--lesson", type=int, required=True); q.add_argument("--key", choices=sorted(BUDGET_KEYS), required=True); q.add_argument("--value", type=int, required=True); q.add_argument("--reason", required=True); q.set_defaults(func=cmd_set_budget)
    q = sub.add_parser("resume-budget"); q.add_argument("--state", required=True); q.add_argument("--lesson", type=int, required=True); q.add_argument("--event-id", required=True); q.add_argument("--reason", required=True); q.set_defaults(func=cmd_resume_budget)
    q = sub.add_parser("next"); q.add_argument("--state", required=True); q.set_defaults(func=cmd_next)
    q = sub.add_parser("agreement"); q.add_argument("--state", required=True); q.set_defaults(func=cmd_agreement)
    q = sub.add_parser("paths"); q.add_argument("--state", required=True); q.add_argument("--lesson", type=int, required=True); q.set_defaults(func=cmd_paths)
    q = sub.add_parser("work-order"); q.add_argument("--state", required=True); q.add_argument("--lesson", type=int, required=True); q.set_defaults(func=cmd_work_order)
    q = sub.add_parser("preflight"); q.add_argument("--state", required=True); q.add_argument("--lesson", type=int, required=True); q.add_argument("--report"); q.add_argument("--json-out"); q.set_defaults(func=cmd_preflight)
    q = sub.add_parser("self-rework"); q.add_argument("--state", required=True); q.add_argument("--lesson", type=int, required=True); q.add_argument("--reason", required=True); q.add_argument("--artifact", action="append", required=True); q.add_argument("--tokens-used", type=int); q.add_argument("--wall-minutes-used", type=float); q.add_argument("--agent-calls", type=int); q.set_defaults(func=cmd_self_rework)
    q = sub.add_parser("revision-open"); q.add_argument("--state", required=True); q.add_argument("--lesson", type=int, required=True); q.add_argument("--type", required=True, choices=["metadata_link_only", "formatting", "content"]); q.add_argument("--reason", required=True); q.set_defaults(func=cmd_revision_open)
    q = sub.add_parser("revision-close"); q.add_argument("--state", required=True); q.add_argument("--lesson", type=int, required=True); q.add_argument("--revision-report", "--report", dest="revision_report", required=True); q.add_argument("--qa-report"); q.add_argument("--artifact", action="append"); q.add_argument("--tokens-used", type=int); q.add_argument("--wall-minutes-used", type=float); q.add_argument("--agent-calls", type=int); q.set_defaults(func=cmd_revision_close)
    q = sub.add_parser("record-visual"); q.add_argument("--state", required=True); q.add_argument("--lesson", type=int, required=True); q.add_argument("--report", required=True); q.add_argument("--artifact", action="append"); q.add_argument("--wall-minutes-used", type=float, required=True); q.add_argument("--tokens-used", type=int, default=0); q.add_argument("--agent-calls", type=int, required=True); q.set_defaults(func=cmd_record_visual)
    q = sub.add_parser("approve-visual-sample"); q.add_argument("--state", required=True); q.add_argument("--lesson", type=int, required=True); q.add_argument("--approved-by", required=True); q.set_defaults(func=cmd_approve_visual_sample)
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
