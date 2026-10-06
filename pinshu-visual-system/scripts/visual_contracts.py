"""Shared source anchors and relationship checks for the public companions."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
import re
import unicodedata


def read_source(brief: dict, brief_path: Path) -> tuple[Path, str]:
    name = brief.get("source_file")
    if not isinstance(name, str) or not name.strip():
        raise ValueError("Supply source_file; a supplied brief is not the original source")
    path = Path(name)
    if not path.is_absolute():
        path = brief_path.parent / path
    path = path.resolve()
    content = path.read_text(encoding="utf-8")
    if not content.strip():
        raise ValueError("Source file is empty")
    return path, content


def anchor(excerpt: object, source: str) -> str:
    if not isinstance(excerpt, str) or not excerpt.strip() or excerpt not in source:
        raise ValueError("Every source_excerpt must occur verbatim in the original source")
    if sum(c.isalnum() for c in excerpt) < 3:
        raise ValueError("A verbatim source_excerpt must contain meaningful context, not punctuation or a single word fragment")
    return excerpt


def check_brief_fields(brief: object, allowed: set[str], workflow: str) -> None:
    if not isinstance(brief, dict):
        raise ValueError("The brief must be a JSON object")
    unknown = sorted(set(brief) - allowed)
    if unknown:
        hint = "Use relations, not relationships." if "relationships" in unknown else ""
        if workflow == "pinshu-infographic" and set(unknown) & {"mother", "metaphor", "dataset", "delivery_medium"}:
            hint += " Business briefs belong to pinshu-business-graphics."
        raise ValueError("Unknown brief fields: " + ", ".join(unknown) + ". " + hint)


def check_exact_text(exact: object, source: str, approvals: object = None) -> list[dict]:
    if not isinstance(exact, list) or not all(isinstance(x, str) and x.strip() for x in exact):
        raise ValueError("exact_text must be a list of nonempty strings")
    approvals = [] if approvals is None else approvals
    if not isinstance(approvals, list):
        raise ValueError("approved_external_text must be a list of declared approvals")
    declared = {}
    for item in approvals:
        if not isinstance(item, dict) or any(not isinstance(item.get(k), str) or not item[k].strip()
                                             for k in ("text", "approved_by", "reason", "user_quote")):
            raise ValueError("Each external text approval needs text, approved_by, reason and the real user_quote")
        if re.search(r"(?i)\b(agent|assistant|codex|claude|gpt|ai)(?:\b|[-_])", item["approved_by"]):
            raise ValueError("External text requires a human approval, not an agent estimate")
        if item["text"] not in exact or item["text"] in declared:
            raise ValueError("External text approvals must uniquely name an exact_text label")
        declared[item["text"]] = item
    evidence = []
    for text in exact:
        if text in source:
            evidence.append({"text": text, "origin": "literal-source"})
        elif text in declared:
            evidence.append(dict(declared[text], origin="declared-user-approval"))
        else:
            raise ValueError("exact_text is absent from the source: " + text + "; supply a real user approval in approved_external_text")
    return evidence


def text_delivery(labels: list[str], *, exact: list[str] | None = None, force: bool = False) -> dict:
    labels = list(dict.fromkeys(x for x in labels if x.strip()))
    width = lambda s: sum(2 if unicodedata.east_asian_width(c) in "WF" else 1 for c in s)
    cjk_labels = sum(any(unicodedata.east_asian_width(c) in "WF" for c in s) for s in labels)
    editable = force or len(exact or []) > 1 or any(width(s) > 20 for s in labels) or cjk_labels > 1
    return {"visible_labels": labels, "text_route": "editable-text-layer" if editable else "short-text-with-visual-qa",
            "routing_basis": "all visible labels; weighted width and multiple CJK labels are conservative heuristics, not a renderer guarantee"}


def check_units(units: object, source: str, maximum: int) -> list[dict]:
    if not isinstance(units, list) or not 1 <= len(units) <= maximum:
        raise ValueError(f"Information density requires 1-{maximum} units; split the content")
    identifiers = set()
    for unit in units:
        if not isinstance(unit, dict):
            raise ValueError("Each unit must have id, label and source_excerpt")
        check_brief_fields(unit, {"id", "label", "source_excerpt"}, "unit")
        identifier, label = unit.get("id"), unit.get("label")
        if not isinstance(identifier, str) or not identifier.strip() or identifier in identifiers:
            raise ValueError("Unit IDs must be nonempty and unique")
        if not isinstance(label, str) or not label.strip():
            raise ValueError("Each unit needs a readable label")
        identifiers.add(identifier)
        anchor(unit.get("source_excerpt"), source)
    return units


def check_relations(relations: object, units: list[dict], source: str, structure: str) -> list[dict]:
    if not isinstance(relations, list):
        raise ValueError("relations must be a list")
    ids = {unit["id"] for unit in units}
    edges = set()
    for relation in relations:
        if not isinstance(relation, dict):
            raise ValueError("Each relation must name its endpoints, verb and source_excerpt")
        check_brief_fields(relation, {"from", "to", "verb", "source_excerpt"}, "relation")
        pair = (relation.get("from"), relation.get("to"))
        if pair[0] not in ids or pair[1] not in ids or pair[0] == pair[1] or pair in edges:
            raise ValueError("Relationship endpoints must be distinct existing units; no duplicate edges")
        if not isinstance(relation.get("verb"), str) or not relation["verb"].strip():
            raise ValueError("Every arrow needs an explicit verb")
        anchor(relation.get("source_excerpt"), source)
        edges.add(pair)
    if structure in {"process", "timeline", "true-loop"} and len(units) > 1:
        if not relations:
            raise ValueError("A sequence needs source-supported relationships")
        touched = {value for edge in edges for value in edge}
        if touched != ids:
            raise ValueError("Every sequence unit must participate in a relationship")
    if structure == "true-loop":
        if len(ids) < 2 or len(edges) != len(ids):
            raise ValueError("A true loop needs one directed return path through every unit")
        next_node = dict(edges)
        if len(next_node) != len(ids) or {end for _, end in edges} != ids:
            raise ValueError("A hub-and-spoke graph is not a true loop")
        start = units[0]["id"]
        node, visited = start, set()
        while node not in visited:
            visited.add(node)
            node = next_node[node]
        if node != start or visited != ids:
            raise ValueError("All loop units must form one closed cycle")
    return relations


def save_plan(plan: dict, source: str, brief_path: Path, output_dir: Path) -> None:
    plan["brief_sha256"] = hashlib.sha256(brief_path.read_bytes()).hexdigest()
    output_dir.mkdir(parents=True, exist_ok=False)
    (output_dir / "source-content.txt").write_text(source, encoding="utf-8")
    (output_dir / "structured-brief.json").write_text(brief_path.read_text(), encoding="utf-8")
    (output_dir / "prompt-final.txt").write_text(plan["prompt"], encoding="utf-8")
    (output_dir / "route-plan.json").write_text(json.dumps(plan, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
