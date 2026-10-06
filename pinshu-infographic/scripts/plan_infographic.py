#!/usr/bin/env python3
"""Compile a source-anchored information graphic using the installed public core."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import sys

CORE = Path(__file__).resolve().parents[2] / "pinshu-visual-system"
if not (CORE / ".public-bundle").is_file():
    raise SystemExit("HARD_STOP: Install the public pinshu-visual-system companion in the same parent directory; do not use a private core")
try:
    core_version = tuple(int(part) for part in (CORE / "VERSION").read_text().strip().split("."))
except (OSError, ValueError):
    raise SystemExit("HARD_STOP: The public core has no valid VERSION; reinstall the complete visual set") from None
if core_version < (0, 2, 1):
    raise SystemExit("HARD_STOP: This companion requires public pinshu-visual-system 0.2.1 or later; upgrade the complete visual set")
sys.path.insert(0, str(CORE / "scripts"))
from visual_compiler import compile_plan
from visual_contracts import anchor, check_relations, check_units, read_source, save_plan, check_brief_fields, check_exact_text, text_delivery

MODES = {"warm-paper", "lively-vector", "character-presenter"}


def compile_infographic(brief_path: Path, *, candidate_test: bool = False,
                        character_profile: Path | None = None) -> tuple[dict, str]:
    brief = json.loads(brief_path.read_text(encoding="utf-8"))
    check_brief_fields(brief, {"source_file", "claim", "claim_source_excerpt", "mode", "platform", "structure",
        "density", "units", "relations", "layout", "output_language", "exact_text", "approved_external_text"}, "pinshu-infographic")
    source_path, source = read_source(brief, brief_path)
    mode = brief.get("mode", "warm-paper")
    if mode not in MODES:
        raise ValueError("Use an infographic mode; route atmosphere visuals through the core")
    density = brief.get("density", "document")
    if density not in {"document", "slide"}:
        raise ValueError("density must be document or slide")
    platform = brief.get("platform", "wechat-article")
    if platform in {"ppt-16x9", "livestream-16x9"} and density != "slide":
        raise ValueError("Presentation surfaces require slide density")
    units = check_units(brief.get("units"), source, 5 if density == "slide" else 7)
    structure = brief.get("structure")
    if structure == "timeline":
        raise ValueError("This infographic adapter has no timeline mode; use pinshu-business-graphics with mother=strategic-map and structure=timeline")
    relations = check_relations(brief.get("relations", []), units, source, structure)
    claim = brief.get("claim")
    if not isinstance(claim, str) or not claim.strip():
        raise ValueError("Supply one main claim")
    anchor(brief.get("claim_source_excerpt"), source)
    exact = brief.get("exact_text", [])
    text_evidence = check_exact_text(exact, source, brief.get("approved_external_text"))
    plan = compile_plan(source, platform, mode, structure, brief.get("layout", "auto"),
                        claim, candidate_test, character_profile, exact, len(units), source_path,
                        approved_external_text=brief.get("approved_external_text"))
    delivery = text_delivery([claim] + [u["label"] for u in units] + [r["verb"] for r in relations] + exact, exact=exact)
    plan.update(delivery)
    plan["exact_text_evidence"] = text_evidence
    if delivery["text_route"] == "editable-text-layer":
        plan["prompt"] += "\nGenerate only a text-free supporting illustration. All final titles, unit labels and arrow verbs belong in the editable source, not in the bitmap."
    plan["visual_card"]["density"] = density
    plan["workflow"] = {"kind": "pinshu-infographic", "version": "0.1.1"}
    plan["structured_content"] = {"claim": claim, "units": units, "relations": relations,
                                  "wording_review": "pending", "semantic_source_review": "pending"}
    plan["required_checks"] += ["information-relationships", "density-and-reading", "text-delivery"]
    plan["source_anchor_check"] = "literal excerpts matched; label and arrow meaning still require actual review"
    plan["prompt"] += "\n\nInformation graphic brief:\n" + json.dumps({
        "claim": claim, "units": units, "relations": relations, "density": density,
        "output_language": brief.get("output_language", "match-user")}, ensure_ascii=False, indent=2)
    plan["prompt"] += ("\nPreserve source meaning. Display only essential short labels, not source excerpts. "
                        "Every arrow must match the supplied verb and source; generic icons cannot replace the information relationship. "
                        "Keep at most two annotation levels. If readable labels do not fit, split the graphic. "
                        "Use editable text for long or multiple exact labels; never paint over bitmap lettering.")
    if delivery["text_route"] == "editable-text-layer":
        plan["prompt"] += "\nFor this plan, render NO lettering in the illustration bitmap. Compose ALL visible labels and relationships in the native editable final and inspect that composite."
    return plan, source


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--brief", required=True, type=Path)
    parser.add_argument("--output-dir", required=True, type=Path)
    parser.add_argument("--candidate-test", action="store_true")
    parser.add_argument("--character-profile", type=Path)
    args = parser.parse_args()
    try:
        plan, source = compile_infographic(args.brief, candidate_test=args.candidate_test,
                                          character_profile=args.character_profile)
        save_plan(plan, source, args.brief, args.output_dir)
    except (OSError, ValueError, KeyError, TypeError) as exc:
        parser.exit(1, f"HARD_STOP: {exc}\n")
    print("PLAN READY: source anchors matched; rendering and semantic review remain pending")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
