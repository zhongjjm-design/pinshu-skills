#!/usr/bin/env python3
"""Validate legacy/backend propagation-asset JSON registries.

Mechanical guardrails only. The script checks schema, source resolution, quote
anchors, risk gates, completion claims, and handoff routing. A PASS does not
prove that the selected knowledge is valuable, complete, durable, deduplicated,
or useful for real reuse. Those product-success checks require reading and using
the user-facing knowledge assets.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path
from typing import Any

ASSET_TYPES = {
    "propagation_candidates",
    "propagation_selection",
    "propagation_mother_asset",
    "content_handoff",
    "content_asset_package",
}
SCOPE_TYPES = {"single", "lesson", "module", "course"}
COVERAGE = {"partial", "complete"}
IDENTITIES = {"lecturer_quote", "editorial_synthesis", "user_extension", "external_addition"}
VERIFICATION = {"not_required", "pending", "corroborated", "partially_supported", "disputed", "unverifiable"}
RISKS = {"R0", "R1", "R2", "R3"}
CANDIDATE_TYPES = {"quote", "viewpoint", "story", "case", "data", "method", "conflict", "question", "topic"}
CANDIDATE_STATES = {"captured", "normalized", "deduplicated", "verification_pending", "verified", "disputed", "unverifiable", "promoted", "archived"}
SELECTION_STATES = {"building", "stage_complete", "validated"}
MOTHER_STATES = {"building", "course_complete", "validated", "handoff_ready"}
HANDOFF_STATES = {"handoff_ready", "handed_off"}
PACKAGE_STATES = {"building", "mechanically_valid", "semantic_approved", "delivered"}
DELIVERY_STATES = {"destination_unresolved", "handoff_pending", "draft_requested", "draft_created", "human_reviewed", "final_approved", "delivered"}
ROUTE_ROLES = {"content_draft_destination", "content_final_destination", "content_workflow_handoff"}
TOP_STATES = {
    "propagation_candidates": CANDIDATE_STATES,
    "propagation_selection": SELECTION_STATES,
    "propagation_mother_asset": MOTHER_STATES,
    "content_handoff": HANDOFF_STATES,
    "content_asset_package": PACKAGE_STATES,
}
DELIVERABLE_ROLES = {
    "navigation",
    "ready_to_use",
    "topic_library",
    "production_brief",
    "content_component",
    "restricted",
}
USE_STATUSES = {
    "ready_to_browse",
    "ready_to_copy",
    "ready_for_topic_library",
    "ready_for_production",
    "needs_verification",
    "blocked",
}
ROLE_USE_STATUSES = {
    "navigation": {"ready_to_browse"},
    "ready_to_use": {"ready_to_copy"},
    "topic_library": {"ready_for_topic_library"},
    "production_brief": {"ready_for_production"},
    "content_component": {"ready_to_copy", "ready_for_production"},
    "restricted": {"needs_verification", "blocked"},
}
ACTION_ROLES = {"ready_to_use", "topic_library", "production_brief"}
REQUIRED_REVIEW_SCOPES = {
    "complete_visible_claims",
    "source_identity",
    "risk_inheritance",
    "first_person_ownership",
    "topic_contract",
}
TOPIC_FIELDS = {
    "title",
    "target_reader",
    "core_judgment",
    "rationale",
    "safe_evidence",
    "recommended_form",
    "current_status",
    "next_action",
}
TOPIC_STATUSES = {
    "ready",
    "needs_user_experience",
    "needs_external_verification",
    "needs_human_approval",
    "blocked",
}
FIRST_PERSON_EXPERIENCE_RE = re.compile(
    r"(?:^|[，。！？；：\s])我(?:曾经?|去年|今年|自己|做过|发过|服务过|遇到过|的客户|的团队|的公司|亲自|当时)"
)
ROLE_PATH_RULES = {
    "navigation": lambda relative: relative.as_posix() == "00_内容资产导航.md",
    "ready_to_use": lambda relative: relative.parts and relative.parts[0] == "01_可直接使用",
    "topic_library": lambda relative: relative.parts and relative.parts[0] == "02_选题库",
    "production_brief": lambda relative: relative.parts and relative.parts[0] == "03_待生产",
    "content_component": lambda relative: relative.parts and relative.parts[0] == "04_可拆分内容组件",
    "restricted": lambda relative: relative.as_posix() == "05_待核验与禁用.md",
}
PROCESS_FILE_TOKENS = {
    "执行日志", "注册表", "机械验证", "去重报告", "语义复核报告", "核验报告",
    "审核记录", "测试报告", "交接包", "handoff", "构建脚本", "build", "registry",
    "validation", "audit", "候选.json", "阶段精选", "母资产.json",
}
PROCESS_FILE_SUFFIXES = {".json", ".py", ".sh", ".log", ".yaml", ".yml", ".toml"}
NEGATIVE_COMPLETION_RE = re.compile(
    r"尚未完课|课程未完成|仍在进行|未结项|撤回.{0,8}结项|不通过.{0,8}结项|(?:课程|课次|状态).{0,8}待完成"
)


def resolve(owner: Path, raw: str) -> Path:
    target = Path(raw.split("#", 1)[0]).expanduser()
    return target if target.is_absolute() else (owner.parent / target).resolve()


def normalized(text: str) -> str:
    return re.sub(r"\s+", "", text)


def quote_normalized(text: str) -> str:
    clean = text.strip()
    pairs = (("“", "”"), ("‘", "’"), ('"', '"'), ("'", "'"))
    for opening, closing in pairs:
        if len(clean) >= 2 and clean.startswith(opening) and clean.endswith(closing):
            clean = clean[len(opening):-len(closing)].strip()
            break
    return normalized(clean)


def markdown_section(text: str, expected_title: str) -> tuple[str | None, int]:
    """Return the uniquely named Markdown section, including its heading."""
    headings: list[tuple[int, int, int, str]] = []
    for match in re.finditer(r"^(#{1,6})\s+(.+?)\s*$", text, re.MULTILINE):
        title = re.sub(r"\s+", " ", match.group(2).strip().rstrip("#").strip())
        headings.append((match.start(), match.end(), len(match.group(1)), title))
    wanted = re.sub(r"\s+", " ", expected_title.strip().rstrip("#").strip())
    matches = [entry for entry in headings if entry[3] == wanted]
    if len(matches) != 1:
        return None, len(matches)
    start, _heading_end, level, _title = matches[0]
    end = len(text)
    for heading_start, _end, heading_level, _heading_title in headings:
        if heading_start > start and heading_level <= level:
            end = heading_start
            break
    return text[start:end], 1


def read_declared_section(
    owner: Path,
    anchor: Any,
    declared_sources: set[Path],
    where: str,
    errors: list[str],
) -> tuple[Path | None, str | None]:
    if not isinstance(anchor, dict):
        errors.append(f"{where} missing object: source_anchor")
        return None, None
    document = need_string(anchor, "document", f"{where}.source_anchor", errors)
    section = need_string(anchor, "section", f"{where}.source_anchor", errors)
    if not document:
        return None, None
    source_path = resolve(owner, document)
    if source_path not in declared_sources:
        errors.append(f"{where} source_anchor.document is not declared in source_documents")
    if not source_path.is_file():
        errors.append(f"{where} unresolvable source document: {document}")
        return source_path, None
    try:
        source_text = source_path.read_text(encoding="utf-8")
    except Exception as exc:
        errors.append(f"{where} cannot read source document: {exc}")
        return source_path, None
    if not section:
        return source_path, None
    section_text, count = markdown_section(source_text, section)
    if count == 0:
        errors.append(f"{where} source_anchor.section is not an exact Markdown heading")
    elif count > 1:
        errors.append(f"{where} source_anchor.section must identify exactly one Markdown heading")
    return source_path, section_text


def validate_readback_evidence(
    owner: Path,
    evidence: Any,
    where: str,
    errors: list[str],
) -> bool:
    if not isinstance(evidence, dict) or evidence.get("readback_verified") is not True:
        errors.append(f"{where} requires structured readback evidence")
        return False
    kind = evidence.get("kind")
    if kind not in {"file", "external"}:
        errors.append(f"{where} evidence kind must be file or external")
        return False
    approval_excerpt = need_string(evidence, "approval_excerpt", f"{where}.evidence", errors)
    if kind == "file":
        reference = need_string(evidence, "reference", f"{where}.evidence", errors)
        if reference:
            evidence_path = resolve(owner, reference)
            if not evidence_path.is_file():
                errors.append(f"{where} evidence must reference an existing regular file")
            else:
                try:
                    evidence_text = evidence_path.read_text(encoding="utf-8")
                    if not evidence_text:
                        errors.append(f"{where} evidence file must not be empty")
                    elif approval_excerpt and normalized(approval_excerpt) not in normalized(evidence_text):
                        errors.append(f"{where} approval_excerpt not found in evidence file")
                except Exception as exc:
                    errors.append(f"{where} evidence cannot be read: {exc}")
    else:
        need_string(evidence, "receipt_id", f"{where}.evidence", errors)
        need_string(evidence, "readback_reference", f"{where}.evidence", errors)
    return True


def is_negative_completion_statement(line: str) -> bool:
    clean = re.sub(r"^[\s>#*\-\d.、]+", "", line).strip()
    if not clean:
        return False
    for match in NEGATIVE_COMPLETION_RE.finditer(clean):
        before = clean[max(0, match.start() - 24):match.start()]
        after = clean[match.end():match.end() + 24]
        local_start = max(
            before.rfind(token) for token in ("；", ";", "。", "！", "!", "？", "?", "，", ",", "——")
        )
        local_prefix = before[local_start + 1:].strip()
        if local_prefix.startswith(("示例：", "示例:", "反例：", "反例:")):
            continue
        if re.search(r"(?:如果|若|仅当)[^，,；;。！？!?—]{0,16}$", local_prefix):
            continue
        if re.match(r"时.{0,16}(?:不得|不能)", after):
            continue
        return True
    return False


def has_later_completion_conflict(text: str, excerpt: str) -> bool:
    excerpt_norm = normalized(excerpt)
    lines = text.splitlines()
    excerpt_end = None
    for index, line in enumerate(lines):
        if excerpt_norm and excerpt_norm in normalized(line):
            excerpt_end = index + 1
            break
    if excerpt_end is None:
        return False
    return any(is_negative_completion_statement(line) for line in lines[excerpt_end:])


def need_string(obj: dict[str, Any], key: str, where: str, errors: list[str]) -> str | None:
    value = obj.get(key)
    if not isinstance(value, str) or not value.strip():
        errors.append(f"{where} missing non-empty string: {key}")
        return None
    return value.strip()


def validate_evidence_list(value: Any, where: str, errors: list[str]) -> None:
    if not isinstance(value, list) or not value:
        errors.append(f"{where} requires a non-empty evidence list")
        return
    for number, evidence in enumerate(value, 1):
        if not isinstance(evidence, dict):
            errors.append(f"{where} evidence {number} is not an object")
            continue
        need_string(evidence, "source", f"{where} evidence {number}", errors)
        need_string(evidence, "accessed_at", f"{where} evidence {number}", errors)
        need_string(evidence, "claim", f"{where} evidence {number}", errors)


def human_review_is_approved(owner: Path, item: dict[str, Any], where: str, errors: list[str]) -> bool:
    review = item.get("human_review")
    if not isinstance(review, dict) or review.get("status") != "approved":
        errors.append(f"{where} R3 requires structured human_review with status=approved")
        return False
    need_string(review, "reviewer", f"{where}.human_review", errors)
    need_string(review, "reviewed_at", f"{where}.human_review", errors)
    evidence = review.get("evidence")
    if not isinstance(evidence, dict) or evidence.get("readback_verified") is not True:
        errors.append(f"{where}.human_review requires structured readback evidence")
        return False
    kind = evidence.get("kind")
    if kind not in {"file", "external"}:
        errors.append(f"{where}.human_review evidence kind must be file or external")
        return False
    if kind == "file":
        reference = need_string(evidence, "reference", f"{where}.human_review.evidence", errors)
        approval_excerpt = need_string(evidence, "approval_excerpt", f"{where}.human_review.evidence", errors)
        if reference:
            evidence_path = resolve(owner, reference)
            if not evidence_path.is_file():
                errors.append(f"{where}.human_review evidence must reference an existing regular file")
            else:
                try:
                    with evidence_path.open("rb") as handle:
                        first_byte = handle.read(1)
                    if not first_byte:
                        errors.append(f"{where}.human_review evidence file must not be empty")
                    elif approval_excerpt:
                        evidence_text = evidence_path.read_text(encoding="utf-8")
                        if normalized(approval_excerpt) not in normalized(evidence_text):
                            errors.append(f"{where}.human_review approval_excerpt not found in evidence file")
                except Exception as exc:
                    errors.append(f"{where}.human_review evidence cannot be read: {exc}")
    else:
        need_string(evidence, "receipt_id", f"{where}.human_review.evidence", errors)
        need_string(evidence, "readback_reference", f"{where}.human_review.evidence", errors)
        need_string(evidence, "approval_excerpt", f"{where}.human_review.evidence", errors)
    return True


def validate_item(owner: Path, item: Any, number: int, asset_type: str | None,
                  declared_sources: set[Path], errors: list[str]) -> None:
    where = f"item {number}"
    if not isinstance(item, dict):
        errors.append(f"{where} is not an object")
        return
    need_string(item, "asset_id", where, errors)
    candidate_type = need_string(item, "candidate_type", where, errors)
    identity = need_string(item, "expression_identity", where, errors)
    verification = need_string(item, "verification_status", where, errors)
    risk = need_string(item, "risk_level", where, errors)
    status = need_string(item, "status", where, errors)
    content = need_string(item, "content", where, errors)
    need_string(item, "context", where, errors)
    boundary = need_string(item, "boundary", where, errors)
    need_string(item, "value_reason", where, errors)

    if identity and identity not in IDENTITIES:
        errors.append(f"{where} invalid expression_identity: {identity}")
    if candidate_type and candidate_type not in CANDIDATE_TYPES:
        errors.append(f"{where} invalid candidate_type: {candidate_type}")
    if verification and verification not in VERIFICATION:
        errors.append(f"{where} invalid verification_status: {verification}")
    if risk and risk not in RISKS:
        errors.append(f"{where} invalid risk_level: {risk}")
    if status and status not in CANDIDATE_STATES:
        errors.append(f"{where} invalid status: {status}")

    _source_path, source_section_text = read_declared_section(
        owner,
        item.get("source_anchor"),
        declared_sources,
        where,
        errors,
    )

    if identity == "lecturer_quote":
        excerpt = need_string(item, "source_excerpt", where, errors)
        if excerpt and source_section_text is not None and normalized(excerpt) not in normalized(source_section_text):
            errors.append(f"{where} source_excerpt not found inside declared source section")
        if excerpt and content and quote_normalized(content) != quote_normalized(excerpt):
            errors.append(f"{where} lecturer_quote content must match source_excerpt verbatim")
    if identity == "external_addition":
        sources = item.get("external_sources")
        validate_evidence_list(sources, f"{where}.external_sources", errors)
    if identity == "user_extension":
        user_evidence = item.get("user_evidence")
        if not isinstance(user_evidence, dict) or user_evidence.get("readback_verified") is not True:
            errors.append(f"{where} user_extension requires structured user_evidence with readback_verified=true")
        else:
            evidence_kind = user_evidence.get("kind")
            if evidence_kind != "file":
                errors.append(f"{where}.user_evidence kind must be file")
            reference = need_string(user_evidence, "reference", f"{where}.user_evidence", errors)
            excerpt = need_string(user_evidence, "source_excerpt", f"{where}.user_evidence", errors)
            if reference:
                evidence_path = resolve(owner, reference)
                if not evidence_path.is_file():
                    errors.append(f"{where}.user_evidence must reference an existing regular file")
                else:
                    try:
                        evidence_text = evidence_path.read_text(encoding="utf-8")
                        if excerpt and normalized(excerpt) not in normalized(evidence_text):
                            errors.append(f"{where}.user_evidence source_excerpt not found in evidence file")
                    except Exception as exc:
                        errors.append(f"{where}.user_evidence cannot be read: {exc}")

    derived_from = item.get("derived_from_source_ids")
    if derived_from is not None:
        if not isinstance(derived_from, list) or not derived_from or not all(
            isinstance(value, str) and value.strip() for value in derived_from
        ):
            errors.append(f"{where} derived_from_source_ids must be a non-empty string list")
        if item.get("derivative_type") != "safe_derivative":
            errors.append(f"{where} derived item requires derivative_type=safe_derivative")
        removed = item.get("removed_claims")
        if not isinstance(removed, list) or not removed or not all(
            isinstance(value, str) and value.strip() for value in removed
        ):
            errors.append(f"{where} safe derivative requires non-empty removed_claims")
        need_string(item, "risk_reduction_reason", where, errors)
        review = item.get("derivative_review")
        if not isinstance(review, dict) or review.get("status") != "approved":
            errors.append(f"{where} safe derivative requires approved derivative_review")
        else:
            need_string(review, "reviewer", f"{where}.derivative_review", errors)
            need_string(review, "reviewed_at", f"{where}.derivative_review", errors)
            validate_readback_evidence(
                owner,
                review.get("evidence"),
                f"{where}.derivative_review",
                errors,
            )

    if risk == "R1" and (not isinstance(item.get("context"), str) or not item["context"].strip()):
        errors.append(f"{where} R1 requires context")
    if risk in {"R2", "R3"} and verification == "not_required":
        errors.append(f"{where} {risk} cannot use verification_status=not_required")

    if status == "verification_pending" and verification != "pending":
        errors.append(f"{where} verification_pending status requires verification_status=pending")
    if status == "verified" and verification not in {"not_required", "corroborated", "partially_supported"}:
        errors.append(f"{where} verified status conflicts with verification_status={verification}")
    if status == "disputed" and verification != "disputed":
        errors.append(f"{where} disputed status requires verification_status=disputed")
    if status == "unverifiable" and verification != "unverifiable":
        errors.append(f"{where} unverifiable status requires verification_status=unverifiable")
    if status == "promoted" and verification in {"pending", "disputed", "unverifiable"}:
        errors.append(f"{where} promoted status conflicts with verification_status={verification}")

    if verification in {"corroborated", "partially_supported"}:
        evidence = item.get("verification_evidence")
        if identity == "external_addition" and not evidence:
            evidence = item.get("external_sources")
        validate_evidence_list(evidence, f"{where}.verification_evidence", errors)
    if verification == "partially_supported" and not boundary:
        errors.append(f"{where} partially_supported requires boundary")

    requires_clearance = asset_type in {"propagation_mother_asset", "content_handoff", "content_asset_package"} or status == "promoted"
    if risk in {"R2", "R3"} and requires_clearance:
        if verification not in {"corroborated", "partially_supported"}:
            errors.append(f"{where} {risk} cannot enter a promoted or user-facing asset before verification")
    if risk == "R3" and requires_clearance:
        human_review_is_approved(owner, item, where, errors)

    if asset_type in {"propagation_mother_asset", "content_handoff", "content_asset_package"} and status != "promoted":
        errors.append(f"{where} in {asset_type} must use status=promoted")


def validate_content_package(owner: Path, payload: dict[str, Any], declared_sources: set[Path], errors: list[str]) -> None:
    raw_root = need_string(payload, "package_root", "content_asset_package", errors)
    package_root: Path | None = None
    if raw_root:
        raw_entry = Path(raw_root.split("#", 1)[0]).expanduser()
        package_entry = raw_entry if raw_entry.is_absolute() else owner.parent / raw_entry
        if package_entry.is_symlink():
            errors.append("content_asset_package package_root must not be a symlink")
        package_root = package_entry.resolve()
        if not package_root.is_dir():
            errors.append("content_asset_package package_root must be an existing directory")
        elif not re.fullmatch(r"\d{2}_内容资产", package_root.name):
            errors.append("content_asset_package directory must use a two-digit XX_内容资产 name")

    package_mode = payload.get("package_mode")
    if package_mode not in {"created", "reused"}:
        errors.append("content_asset_package package_mode must be created or reused")

    producer = need_string(payload, "producer", "content_asset_package", errors)

    profile = payload.get("delivery_profile")
    if profile not in {"full", "requested_subset"}:
        errors.append("content_asset_package delivery_profile must be full or requested_subset")

    requested_roles: set[str] = set()
    raw_requested = payload.get("requested_roles")
    if not isinstance(raw_requested, list) or not raw_requested:
        errors.append("content_asset_package requires non-empty requested_roles")
    else:
        if len(raw_requested) != len(set(raw_requested)):
            errors.append("content_asset_package requested_roles must be unique")
        for role in raw_requested:
            if role not in DELIVERABLE_ROLES:
                errors.append(f"content_asset_package contains invalid requested role: {role}")
            else:
                requested_roles.add(role)
        if "navigation" not in requested_roles:
            errors.append("content_asset_package requested_roles must include navigation")
        if not (requested_roles & ACTION_ROLES):
            errors.append("content_asset_package must request at least one user action role")

    considered_source_ids: set[str] = set()
    raw_considered = payload.get("considered_source_ids")
    if not isinstance(raw_considered, list) or not raw_considered:
        errors.append("content_asset_package requires non-empty considered_source_ids")
    else:
        if len(raw_considered) != len(set(raw_considered)):
            errors.append("content_asset_package considered_source_ids must be unique")
        for source_id in raw_considered:
            if not isinstance(source_id, str) or not source_id.strip():
                errors.append("content_asset_package considered_source_ids contains an invalid value")
            else:
                considered_source_ids.add(source_id)

    has_restricted = payload.get("has_restricted_content")
    if not isinstance(has_restricted, bool):
        errors.append("content_asset_package requires boolean has_restricted_content")

    deliverables = payload.get("deliverables")
    if not isinstance(deliverables, list) or not deliverables:
        errors.append("content_asset_package requires non-empty deliverables")
        return
    if "items" in payload:
        errors.append("content_asset_package must use content_units, not items")

    ids: list[str] = []
    paths: list[Path] = []
    roles: set[str] = set()
    role_by_id: dict[str, str] = {}
    path_by_id: dict[str, Path] = {}
    text_by_id: dict[str, str] = {}
    for number, deliverable in enumerate(deliverables, 1):
        where = f"deliverable {number}"
        if not isinstance(deliverable, dict):
            errors.append(f"{where} is not an object")
            continue
        deliverable_id = need_string(deliverable, "deliverable_id", where, errors)
        role = need_string(deliverable, "asset_role", where, errors)
        need_string(deliverable, "title", where, errors)
        raw_path = need_string(deliverable, "path", where, errors)
        use_status = need_string(deliverable, "use_status", where, errors)
        need_string(deliverable, "next_action", where, errors)
        if deliverable_id:
            ids.append(deliverable_id)
        if role:
            if role not in DELIVERABLE_ROLES:
                errors.append(f"{where} invalid asset_role: {role}")
            else:
                roles.add(role)
                if deliverable_id:
                    role_by_id[deliverable_id] = role
        if use_status and use_status not in USE_STATUSES:
            errors.append(f"{where} invalid use_status: {use_status}")
        if role in ROLE_USE_STATUSES and use_status not in ROLE_USE_STATUSES[role]:
            errors.append(f"{where} use_status {use_status} is incompatible with role {role}")
        if raw_path:
            deliverable_path = resolve(owner, raw_path)
            paths.append(deliverable_path)
            relative: Path | None = None
            if package_root and package_root.is_dir():
                if not deliverable_path.is_relative_to(package_root):
                    errors.append(f"{where} path must stay inside package_root")
                else:
                    relative = deliverable_path.relative_to(package_root)
            if role in ROLE_PATH_RULES and relative is not None and not ROLE_PATH_RULES[role](relative):
                errors.append(f"{where} path does not match the required location for role {role}")
            if deliverable_path.suffix.lower() != ".md":
                errors.append(f"{where} must reference a Markdown file")
            if not deliverable_path.is_file():
                errors.append(f"{where} path must be an existing regular file")
            else:
                try:
                    text = deliverable_path.read_text(encoding="utf-8")
                    if len(normalized(text)) < 30:
                        errors.append(f"{where} file is empty or too small to be usable")
                    if deliverable_id:
                        path_by_id[deliverable_id] = deliverable_path
                        text_by_id[deliverable_id] = text
                    if "content_review" in deliverable:
                        errors.append(f"{where} content_review is deprecated; use file_freeze plus package semantic_review")
                    freeze = deliverable.get("file_freeze")
                    if not isinstance(freeze, dict):
                        errors.append(f"{where} requires file_freeze")
                    else:
                        need_string(freeze, "frozen_by", f"{where}.file_freeze", errors)
                        need_string(freeze, "frozen_at", f"{where}.file_freeze", errors)
                        expected_digest = need_string(
                            freeze, "file_sha256", f"{where}.file_freeze", errors
                        )
                        actual_digest = hashlib.sha256(deliverable_path.read_bytes()).hexdigest()
                        if expected_digest and expected_digest != actual_digest:
                            errors.append(f"{where}.file_freeze file_sha256 does not match the frozen file")
                except Exception as exc:
                    errors.append(f"{where} file cannot be read: {exc}")

    if len(ids) != len(set(ids)):
        errors.append("content_asset_package deliverable_id values must be unique")
    if len(paths) != len(set(paths)):
        errors.append("content_asset_package deliverable paths must be unique")

    if payload.get("status") in {"mechanically_valid", "semantic_approved", "delivered"}:
        missing = sorted(requested_roles - roles)
        if missing:
            errors.append(f"content_asset_package missing requested deliverable roles: {', '.join(missing)}")
        if "navigation" not in roles:
            errors.append("content_asset_package requires a navigation deliverable")
        if not (roles & ACTION_ROLES):
            errors.append("content_asset_package requires at least one user action deliverable")

    if has_restricted is True and "restricted" not in roles:
        errors.append("has_restricted_content=true requires a restricted deliverable")
    if has_restricted is False and "restricted" in roles:
        errors.append("has_restricted_content=false must not create a restricted deliverable")

    content_units = payload.get("content_units")
    if not isinstance(content_units, list) or not content_units:
        errors.append("content_asset_package requires non-empty content_units")
        content_units = []
    unit_ids: list[str] = []
    unit_counts: dict[str, int] = {}
    for number, unit in enumerate(content_units, 1):
        where = f"content_unit {number}"
        if not isinstance(unit, dict):
            errors.append(f"{where} is not an object")
            continue
        deliverable_id = need_string(unit, "deliverable_id", where, errors)
        source_asset_ids = unit.get("source_asset_ids")
        valid_source_ids: set[str] = set()
        if not isinstance(source_asset_ids, list) or not source_asset_ids or not all(
            isinstance(value, str) and value.strip() for value in source_asset_ids
        ):
            errors.append(f"{where} requires non-empty source_asset_ids")
        else:
            valid_source_ids = set(source_asset_ids)
            if len(valid_source_ids) != len(source_asset_ids):
                errors.append(f"{where} source_asset_ids must be unique")
            missing_considered = sorted(valid_source_ids - considered_source_ids)
            if missing_considered:
                errors.append(
                    f"{where} source_asset_ids are missing from considered_source_ids: "
                    + ", ".join(missing_considered)
                )

        source_support = unit.get("source_support")
        support_ids: set[str] = set()
        direct_support_count = 0
        if not isinstance(source_support, list) or not source_support:
            errors.append(f"{where} requires non-empty source_support")
        else:
            for support_number, support in enumerate(source_support, 1):
                support_where = f"{where}.source_support {support_number}"
                if not isinstance(support, dict):
                    errors.append(f"{support_where} is not an object")
                    continue
                support_id = need_string(support, "source_asset_id", support_where, errors)
                excerpt = need_string(support, "support_excerpt", support_where, errors)
                relationship = need_string(support, "relationship", support_where, errors)
                if relationship not in {"direct_support", "contrast", "background"}:
                    errors.append(f"{support_where} invalid relationship")
                if relationship == "direct_support":
                    direct_support_count += 1
                _support_path, support_section = read_declared_section(
                    owner,
                    support.get("source_anchor"),
                    declared_sources,
                    support_where,
                    errors,
                )
                if excerpt and support_section is not None and normalized(excerpt) not in normalized(support_section):
                    errors.append(f"{support_where} support_excerpt not found inside declared source section")
                if support_id:
                    support_ids.add(support_id)
            if support_ids != valid_source_ids:
                errors.append(f"{where} source_support must cover source_asset_ids exactly")
            if direct_support_count == 0:
                errors.append(f"{where} requires at least one direct_support source")

        role = role_by_id.get(deliverable_id or "")
        if deliverable_id and role is None:
            errors.append(f"{where} references an unknown deliverable_id")
            continue
        validate_item(
            owner,
            unit,
            number,
            "propagation_candidates" if role == "restricted" else "content_asset_package",
            declared_sources,
            errors,
        )
        if role == "topic_library":
            topic_fields = unit.get("topic_fields")
            if not isinstance(topic_fields, dict):
                errors.append(f"{where} topic_library unit requires topic_fields")
            else:
                missing_topic_fields = sorted(TOPIC_FIELDS - set(topic_fields))
                if missing_topic_fields:
                    errors.append(
                        f"{where} topic_fields missing: " + ", ".join(missing_topic_fields)
                    )
                for field in TOPIC_FIELDS - {"current_status"}:
                    if field in topic_fields:
                        need_string(topic_fields, field, f"{where}.topic_fields", errors)
                if topic_fields.get("current_status") not in TOPIC_STATUSES:
                    errors.append(f"{where}.topic_fields invalid current_status")
        unit_content = unit.get("content")
        if (
            role != "restricted"
            and isinstance(unit_content, str)
            and FIRST_PERSON_EXPERIENCE_RE.search(unit_content)
            and unit.get("expression_identity") not in {"lecturer_quote", "user_extension"}
        ):
            errors.append(
                f"{where} first-person experience requires lecturer_quote or verified user_extension identity"
            )
        if isinstance(unit.get("asset_id"), str):
            unit_ids.append(unit["asset_id"])
        if deliverable_id:
            unit_counts[deliverable_id] = unit_counts.get(deliverable_id, 0) + 1
            content = unit.get("content")
            target_text = text_by_id.get(deliverable_id)
            if isinstance(content, str) and target_text is not None and normalized(content) not in normalized(target_text):
                errors.append(f"{where} content is not present in its user-facing deliverable")

    if len(unit_ids) != len(set(unit_ids)):
        errors.append("content_asset_package content unit asset_id values must be unique")
    for deliverable_id, role in role_by_id.items():
        if role != "navigation" and unit_counts.get(deliverable_id, 0) == 0:
            errors.append(f"deliverable {deliverable_id} requires at least one mapped content_unit")

    if payload.get("status") in {"semantic_approved", "delivered"}:
        semantic_review = payload.get("semantic_review")
        if not isinstance(semantic_review, dict) or semantic_review.get("status") != "approved":
            errors.append("semantic_approved package requires semantic_review.status=approved")
        else:
            reviewer = need_string(semantic_review, "reviewer", "semantic_review", errors)
            need_string(semantic_review, "reviewed_at", "semantic_review", errors)
            if reviewer and producer and reviewer == producer:
                errors.append("semantic_review reviewer must differ from producer")
            raw_scopes = semantic_review.get("review_scope")
            if not isinstance(raw_scopes, list) or not all(isinstance(value, str) for value in raw_scopes):
                errors.append("semantic_review review_scope must be a string list")
            elif not REQUIRED_REVIEW_SCOPES.issubset(set(raw_scopes)):
                errors.append("semantic_review review_scope is missing required semantic checks")
            reviewed_unit_ids = semantic_review.get("content_unit_ids")
            if not isinstance(reviewed_unit_ids, list) or set(reviewed_unit_ids) != set(unit_ids):
                errors.append("semantic_review content_unit_ids must match all content units exactly")
            digest_map = semantic_review.get("deliverable_sha256")
            if not isinstance(digest_map, dict) or set(digest_map) != set(ids):
                errors.append("semantic_review deliverable_sha256 must cover all deliverables exactly")
            else:
                for deliverable_id in ids:
                    deliverable_path = path_by_id.get(deliverable_id)
                    if deliverable_path and deliverable_path.is_file():
                        actual_digest = hashlib.sha256(deliverable_path.read_bytes()).hexdigest()
                        if digest_map.get(deliverable_id) != actual_digest:
                            errors.append(
                                f"semantic_review digest does not match deliverable {deliverable_id}"
                            )
            validate_readback_evidence(
                owner,
                semantic_review.get("evidence"),
                "semantic_review",
                errors,
            )

    if package_root and package_root.is_dir():
        package_files: set[Path] = set()
        for path in package_root.rglob("*"):
            if path.is_symlink():
                errors.append(
                    f"content_asset_package must not contain symlinks: {path.relative_to(package_root)}"
                )
                continue
            if path.is_dir() and not any(path.iterdir()):
                errors.append(f"content_asset_package contains empty directory: {path.relative_to(package_root)}")
            if not path.is_file():
                continue
            package_files.add(path.resolve())
            lowered_name = path.name.lower()
            if path.suffix.lower() in PROCESS_FILE_SUFFIXES or any(
                token.lower() in lowered_name for token in PROCESS_FILE_TOKENS
            ):
                errors.append(f"content_asset_package directory contains process file: {path.name}")
        unregistered = sorted(package_files - {path.resolve() for path in paths})
        for path in unregistered:
            errors.append(
                f"content_asset_package contains unregistered file: {path.relative_to(package_root)}"
            )

    raw_process_root = payload.get("process_record_root")
    if raw_process_root is not None:
        if not isinstance(raw_process_root, str) or not raw_process_root.strip():
            errors.append("process_record_root must be a non-empty string when provided")
        elif package_root:
            process_root = resolve(owner, raw_process_root)
            if process_root == package_root or process_root.is_relative_to(package_root):
                errors.append("process_record_root must stay outside package_root")


def validate_payload(path: Path, payload: Any) -> list[str]:
    errors: list[str] = []
    if not isinstance(payload, dict):
        return ["root must be an object"]
    asset_type = payload.get("asset_type")
    schema_version = payload.get("schema_version")
    if asset_type == "content_asset_package":
        if schema_version != "1.1":
            errors.append("content_asset_package schema_version must be 1.1")
    elif schema_version != "1.0":
        errors.append("schema_version must be 1.0")
    scope_type = payload.get("scope_type")
    coverage = payload.get("coverage_status")
    top_status = payload.get("status")
    if asset_type not in ASSET_TYPES:
        errors.append(f"invalid asset_type: {asset_type}")
    if scope_type not in SCOPE_TYPES:
        errors.append(f"invalid scope_type: {scope_type}")
    if coverage not in COVERAGE:
        errors.append(f"invalid coverage_status: {coverage}")
    if asset_type in TOP_STATES and top_status not in TOP_STATES[asset_type]:
        errors.append(f"invalid top-level status for {asset_type}: {top_status}")

    source_documents = payload.get("source_documents")
    declared_sources: set[Path] = set()
    if not isinstance(source_documents, list) or not source_documents:
        errors.append("source_documents must be a non-empty list")
    else:
        for raw in source_documents:
            if not isinstance(raw, str) or not raw.strip():
                errors.append("source_documents contains a non-string value")
            else:
                resolved = resolve(path, raw)
                declared_sources.add(resolved)
                if not resolved.exists():
                    errors.append(f"unresolvable source_document: {raw}")

    if asset_type == "propagation_selection":
        if scope_type not in {"module", "course"} or coverage != "partial":
            errors.append("propagation_selection must be a partial module or course selection")

    if asset_type == "propagation_mother_asset":
        if scope_type == "single":
            if coverage != "complete":
                errors.append("single mother asset requires coverage_status=complete")
            if top_status == "course_complete":
                errors.append("single mother asset cannot use course_complete status")
        elif scope_type == "course":
            if coverage != "complete" or payload.get("course_complete") is not True:
                errors.append("course mother asset requires complete coverage and course_complete=true")
        else:
            errors.append("propagation_mother_asset is allowed only for single or completed course scope")

    if asset_type == "content_handoff":
        if scope_type not in {"single", "course"} or coverage != "complete":
            errors.append("content_handoff requires complete single or course scope")

    if asset_type == "content_asset_package":
        if scope_type not in {"single", "module", "course"}:
            errors.append("content_asset_package is allowed only for single, module, or course scope")
        validate_content_package(path, payload, declared_sources, errors)

    if scope_type == "course" and coverage == "complete":
        if payload.get("course_complete") is not True:
            errors.append("complete course asset requires course_complete=true")
        completion = payload.get("completion_evidence")
        if not isinstance(completion, dict) or completion.get("kind") not in {"course_map", "user_confirmation"}:
            errors.append("complete course asset requires structured completion_evidence")
        else:
            completion_reference = need_string(completion, "reference", "completion_evidence", errors)
            completion_excerpt = need_string(completion, "source_excerpt", "completion_evidence", errors)
            if completion.get("completion_assertion") != "course_complete":
                errors.append("completion_evidence completion_assertion must be course_complete")
            need_string(completion, "verified_at", "completion_evidence", errors)
            need_string(completion, "reviewed_by", "completion_evidence", errors)
            need_string(completion, "review_evidence", "completion_evidence", errors)
            if completion_reference:
                completion_path = resolve(path, completion_reference)
                if not completion_path.exists():
                    errors.append("completion_evidence reference does not exist")
                if completion_path not in declared_sources:
                    errors.append("completion_evidence reference must appear in source_documents")
                if completion_path.exists() and completion_excerpt:
                    try:
                        completion_text = completion_path.read_text(encoding="utf-8")
                        if normalized(completion_excerpt) not in normalized(completion_text):
                            errors.append("completion_evidence source_excerpt not found in reference")
                        if has_later_completion_conflict(completion_text, completion_excerpt):
                            errors.append("completion_evidence reference contains an incomplete or revoked completion statement")
                    except Exception as exc:
                        errors.append(f"cannot read completion_evidence reference: {exc}")
            if completion_excerpt and is_negative_completion_statement(completion_excerpt):
                errors.append("completion_evidence source_excerpt states that the course is incomplete")
    if scope_type == "course" and coverage == "partial" and payload.get("course_complete") is True:
        errors.append("partial course asset cannot claim course_complete=true")

    items = payload.get("items")
    if asset_type == "content_asset_package":
        items = []
    elif not isinstance(items, list):
        errors.append("items must be a list")
        items = []
    elif asset_type in {"propagation_selection", "propagation_mother_asset", "content_handoff"} and not items:
        errors.append(f"{asset_type} requires at least one item")
    ids: list[str] = []
    for number, item in enumerate(items, 1):
        validate_item(path, item, number, asset_type, declared_sources, errors)
        if isinstance(item, dict) and isinstance(item.get("asset_id"), str):
            ids.append(item["asset_id"])
    if len(ids) != len(set(ids)):
        errors.append("asset_id values must be unique")

    if asset_type == "content_handoff":
        route = payload.get("route")
        if not isinstance(route, dict):
            errors.append("content_handoff requires route object")
        else:
            route_status = route.get("route_resolution_status")
            delivery = route.get("delivery_status")
            if route_status not in {"resolved", "unresolved"}:
                errors.append(f"invalid route_resolution_status: {route_status}")
            if delivery not in DELIVERY_STATES:
                errors.append(f"invalid delivery_status: {delivery}")
            if route_status == "unresolved":
                if delivery != "destination_unresolved":
                    errors.append("unresolved route must use destination_unresolved")
                if route.get("destination"):
                    errors.append("unresolved route must not claim a destination")
            if route_status == "resolved":
                role = need_string(route, "role", "route", errors)
                if role and role not in ROUTE_ROLES:
                    errors.append(f"invalid route role: {role}")
                need_string(route, "destination", "route", errors)
                if delivery == "destination_unresolved":
                    errors.append("resolved route cannot use destination_unresolved")
            if top_status == "handoff_ready" and delivery not in {"destination_unresolved", "handoff_pending"}:
                errors.append("handoff_ready asset cannot claim downstream delivery progress")
            if top_status == "handed_off" and delivery in {"destination_unresolved", "handoff_pending"}:
                errors.append("handed_off asset requires draft_requested or later delivery status")
            if delivery == "delivered":
                evidence = route.get("delivery_evidence")
                if not isinstance(evidence, dict) or evidence.get("readback_verified") is not True:
                    errors.append("delivered route requires delivery_evidence.readback_verified=true")
                else:
                    evidence_kind = evidence.get("kind")
                    if evidence_kind not in {"file", "external"}:
                        errors.append("delivery_evidence kind must be file or external")
                    need_string(evidence, "verified_at", "delivery_evidence", errors)
                    target_reference = need_string(evidence, "target_reference", "delivery_evidence", errors)
                    need_string(evidence, "verification_method", "delivery_evidence", errors)
                    if target_reference and evidence_kind == "file":
                        target_path = resolve(path, target_reference)
                        if not target_path.is_file():
                            errors.append("delivery_evidence target_reference must be an existing regular file")
                        else:
                            try:
                                with target_path.open("rb") as handle:
                                    handle.read(1)
                            except Exception as exc:
                                errors.append(f"delivery_evidence target_reference cannot be read: {exc}")
                    if evidence_kind == "external":
                        need_string(evidence, "receipt_id", "delivery_evidence", errors)
                        need_string(evidence, "readback_reference", "delivery_evidence", errors)

    return errors


def reject_duplicate_keys(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"duplicate JSON key: {key}")
        result[key] = value
    return result


def validate_full_delivery(
    project_root: Path | None,
    records: list[tuple[Path, dict[str, Any], list[str]]],
) -> list[str]:
    errors: list[str] = []
    if project_root is None:
        return ["full-delivery profile requires --project-root"]
    project_root = project_root.resolve()
    if not project_root.is_dir():
        return ["full-delivery project_root must be an existing directory"]

    valid_packages = [
        (path, payload)
        for path, payload, record_errors in records
        if not record_errors
        and payload.get("asset_type") == "content_asset_package"
        and payload.get("schema_version") == "1.1"
        and payload.get("status") in {"semantic_approved", "delivered"}
        and payload.get("delivery_profile") == "full"
    ]
    if not valid_packages:
        return ["full-delivery requires at least one valid semantic_approved content_asset_package"]

    source_items: dict[str, dict[str, Any]] = {}
    source_item_owners: dict[str, Path] = {}
    active_restricted_ids: set[str] = set()
    for source_owner, payload, _record_errors in records:
        if payload.get("asset_type") == "content_asset_package":
            continue
        for item in payload.get("items", []):
            if not isinstance(item, dict) or not isinstance(item.get("asset_id"), str):
                continue
            source_id = item["asset_id"]
            source_items[source_id] = item
            source_item_owners[source_id] = source_owner
            risk = item.get("risk_level")
            verification = item.get("verification_status")
            status = item.get("status")
            if status != "archived" and risk in {"R2", "R3"} and (
                verification in {"pending", "disputed", "unverifiable"}
                or status in {"verification_pending", "disputed", "unverifiable"}
                or (risk == "R3" and status != "promoted")
            ):
                active_restricted_ids.add(source_id)

    for source_id, item in source_items.items():
        parents = item.get("derived_from_source_ids")
        if parents is None:
            continue
        unknown_parents = [value for value in parents if value not in source_items]
        if unknown_parents:
            errors.append(
                f"safe derivative {source_id} references unknown parent IDs: "
                + ", ".join(sorted(unknown_parents))
            )
        known_parents = [source_items[value] for value in parents if value in source_items]
        if known_parents and not any(parent.get("risk_level") in {"R2", "R3"} for parent in known_parents):
            errors.append(f"safe derivative {source_id} has no R2/R3 parent source")

    for manifest_path, payload in valid_packages:
        package_root = resolve(manifest_path, payload["package_root"])
        if package_root.parent.resolve() != project_root:
            errors.append("content_asset_package package_root must be a direct child of project_root")
            continue
        numbered_siblings: list[int] = []
        same_purpose: list[str] = []
        for sibling in project_root.iterdir():
            if sibling.resolve() == package_root.resolve():
                continue
            match = re.match(r"^(\d{2})_", sibling.name)
            if match:
                numbered_siblings.append(int(match.group(1)))
            if re.fullmatch(r"\d{2}_(?:内容资产|传播资产)", sibling.name):
                same_purpose.append(sibling.name)
        if same_purpose:
            errors.append(
                "project already contains another numbered content/propagation asset entry: "
                + ", ".join(sorted(same_purpose))
            )
        if payload.get("package_mode") == "created":
            expected = (max(numbered_siblings) + 1) if numbered_siblings else 0
            actual = int(package_root.name[:2])
            if actual != expected:
                errors.append(f"content_asset_package must use next sibling number {expected:02d}, got {actual:02d}")

        considered_source_ids = set(payload.get("considered_source_ids", []))
        unknown_considered = sorted(considered_source_ids - set(source_items))
        if unknown_considered:
            errors.append(
                "considered_source_ids not present in supplied registries: "
                + ", ".join(unknown_considered)
            )

        deliverable_roles = {
            item.get("deliverable_id"): item.get("asset_role")
            for item in payload.get("deliverables", [])
            if isinstance(item, dict)
        }
        deliverable_texts: dict[str, str] = {}
        for deliverable in payload.get("deliverables", []):
            if not isinstance(deliverable, dict):
                continue
            deliverable_id = deliverable.get("deliverable_id")
            raw_path = deliverable.get("path")
            if isinstance(deliverable_id, str) and isinstance(raw_path, str):
                target = resolve(manifest_path, raw_path)
                if target.is_file():
                    deliverable_texts[deliverable_id] = target.read_text(encoding="utf-8")

        restricted_source_ids: set[str] = set()
        for number, unit in enumerate(payload.get("content_units", []), 1):
            if not isinstance(unit, dict):
                continue
            role = deliverable_roles.get(unit.get("deliverable_id"))
            source_ids = [value for value in unit.get("source_asset_ids", []) if isinstance(value, str)]
            for source_id in source_ids:
                if source_id not in source_items:
                    errors.append(
                        f"content_unit {number} references source_asset_id not present in supplied registries: {source_id}"
                    )
                if role == "restricted":
                    restricted_source_ids.add(source_id)
                elif source_id in active_restricted_ids:
                    errors.append(
                        f"content_unit {number} in {role} cites active restricted source {source_id}; "
                        "keep it restricted or cite an approved safe derivative"
                    )

            support_entries = unit.get("source_support", [])
            if isinstance(support_entries, list):
                for support in support_entries:
                    if not isinstance(support, dict):
                        continue
                    source_id = support.get("source_asset_id")
                    excerpt = support.get("support_excerpt")
                    source_item = source_items.get(source_id)
                    if source_item is None or not isinstance(excerpt, str):
                        continue
                    haystack = "\n".join(
                        value for value in (
                            source_item.get("content"),
                            source_item.get("source_excerpt"),
                            source_item.get("context"),
                        ) if isinstance(value, str)
                    )
                    if normalized(excerpt) not in normalized(haystack):
                        errors.append(
                            f"content_unit {number} source_support excerpt is not present in source item {source_id}"
                        )
                    support_anchor = support.get("source_anchor")
                    source_anchor = source_item.get("source_anchor")
                    source_owner = source_item_owners.get(source_id)
                    anchors_match = False
                    if (
                        isinstance(support_anchor, dict)
                        and isinstance(support_anchor.get("document"), str)
                        and isinstance(support_anchor.get("section"), str)
                        and isinstance(source_anchor, dict)
                        and isinstance(source_anchor.get("document"), str)
                        and isinstance(source_anchor.get("section"), str)
                        and source_owner is not None
                    ):
                        anchors_match = (
                            resolve(manifest_path, support_anchor["document"])
                            == resolve(source_owner, source_anchor["document"])
                            and support_anchor["section"].strip() == source_anchor["section"].strip()
                        )
                    if not anchors_match:
                        errors.append(
                            f"content_unit {number} source_support anchor does not match source item {source_id}"
                        )

        considered_restricted = active_restricted_ids & considered_source_ids
        if considered_restricted:
            if payload.get("has_restricted_content") is not True:
                errors.append(
                    "package considers active restricted sources and must set has_restricted_content=true"
                )
            missing_restricted = sorted(considered_restricted - restricted_source_ids)
            if missing_restricted:
                errors.append(
                    "restricted deliverable does not cover considered active restricted items: "
                    + ", ".join(missing_restricted)
                )

        public_text = "\n".join(
            text
            for deliverable_id, text in deliverable_texts.items()
            if deliverable_roles.get(deliverable_id) not in {"navigation", "restricted"}
        )
        public_norm = normalized(public_text)
        for source_id in active_restricted_ids:
            source_item = source_items[source_id]
            for raw_claim in (source_item.get("content"), source_item.get("source_excerpt")):
                if not isinstance(raw_claim, str):
                    continue
                claim_norm = normalized(raw_claim)
                if len(claim_norm) >= 12 and claim_norm in public_norm:
                    errors.append(
                        f"raw active restricted claim from {source_id} appears in a non-restricted deliverable"
                    )
                    break
    return errors


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("paths", nargs="+", type=Path)
    parser.add_argument("--profile", choices=["registry", "full-delivery"], default="registry")
    parser.add_argument("--project-root", type=Path)
    args = parser.parse_args()
    failed = False
    seen_ids: dict[str, Path] = {}
    records: list[tuple[Path, dict[str, Any], list[str]]] = []
    for path in args.paths:
        try:
            payload = json.loads(path.read_text(encoding="utf-8"), object_pairs_hook=reject_duplicate_keys)
        except Exception as exc:
            print(f"FAIL {path}\n  - cannot parse JSON: {exc}")
            failed = True
            continue
        errors = validate_payload(path, payload)
        for collection_name in ("items", "content_units"):
            collection = payload.get(collection_name)
            if not isinstance(collection, list):
                continue
            for item in collection:
                if not isinstance(item, dict) or not isinstance(item.get("asset_id"), str):
                    continue
                asset_id = item["asset_id"]
                if asset_id in seen_ids:
                    errors.append(f"asset_id also appears in {seen_ids[asset_id]}: {asset_id}")
                else:
                    seen_ids[asset_id] = path
        records.append((path, payload, errors))
        if errors:
            failed = True
            print(f"FAIL {path}")
            for error in errors:
                print(f"  - {error}")
        else:
            print(f"PASS {path} (backend guardrails only; product value still requires real reading and reuse)")

    if args.profile == "full-delivery":
        delivery_errors = validate_full_delivery(args.project_root, records)
        if delivery_errors:
            failed = True
            print("FAIL full-delivery")
            for error in delivery_errors:
                print(f"  - {error}")
        else:
            print("PASS full-delivery (legacy package guardrails verified; knowledge value, completeness, and reuse remain human judgments)")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
