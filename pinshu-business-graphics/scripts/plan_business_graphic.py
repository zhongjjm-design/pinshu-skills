#!/usr/bin/env python3
"""Plan one business graphic with a distinct mother and source-anchored content."""
from __future__ import annotations

import argparse
from decimal import Decimal, InvalidOperation
import hashlib
import json
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
CORE = ROOT.parent / "pinshu-visual-system"
if not (CORE / ".public-bundle").is_file():
    raise SystemExit("HARD_STOP: Install the public pinshu-visual-system beside this package; do not use a private core")
try:
    core_version = tuple(int(part) for part in (CORE / "VERSION").read_text().strip().split("."))
except (OSError, ValueError):
    raise SystemExit("HARD_STOP: The public core has no valid VERSION; reinstall the complete visual set") from None
if core_version < (0, 2, 0):
    raise SystemExit("HARD_STOP: This companion requires public pinshu-visual-system 0.2.0 or later; upgrade the complete visual set")
sys.path.insert(0, str(CORE / "scripts"))
from visual_compiler import digest, load_configs
from visual_contracts import anchor, check_relations, check_units, read_source, save_plan

MOTHERS = {"typographic-metaphor", "strategic-map", "structural-section", "editorial-collage",
           "engineering-blueprint-narrative", "chinese-modernism", "data-journalism"}


def check_dataset(dataset: object, source: str) -> dict:
    if not isinstance(dataset, dict) or not isinstance(dataset.get("rows"), list) or not dataset["rows"]:
        raise ValueError("Data Journalism requires an actual dataset with provenance")
    for key in ["source", "period", "units", "methodology", "verified_by"]:
        if not isinstance(dataset.get(key), str) or not dataset[key].strip():
            raise ValueError(f"Dataset provenance needs {key}")
    if dataset.get("status") != "verified":
        raise ValueError("Dataset must be declared verified; unsourced conceptual numbers are blocked")
    for row in dataset["rows"]:
        if not isinstance(row, dict) or not isinstance(row.get("label"), str) or not row["label"].strip():
            raise ValueError("Each data row needs a label")
        value = row.get("value")
        try:
            number = Decimal(str(value))
        except InvalidOperation:
            raise ValueError("Data values must be finite numbers") from None
        if isinstance(value, bool) or not number.is_finite():
            raise ValueError("Data values must be finite numbers")
        excerpt = anchor(row.get("source_excerpt"), source)
        if not re.search(r"(?<![+\-\w.])" + re.escape(str(value)) + r"(?![\w.])", excerpt):
            raise ValueError("The exact data value must occur in its source excerpt")
    return dataset


def compile_business(brief_path: Path) -> tuple[dict, str]:
    brief = json.loads(brief_path.read_text(encoding="utf-8"))
    source_path, source = read_source(brief, brief_path)
    mother = brief.get("mother")
    if mother not in MOTHERS:
        raise ValueError("Choose exactly one registered business mother")
    if brief.get("character_profile"):
        raise ValueError("This business preview has no fixed-character adapter; route identity work through the core")
    claim = brief.get("claim")
    if not isinstance(claim, str) or not claim.strip():
        raise ValueError("Supply one main claim")
    anchor(brief.get("claim_source_excerpt"), source)
    registry, profiles = load_configs()
    platform = brief.get("platform", "wechat-article")
    structure = brief.get("structure")
    if platform not in profiles or structure not in registry["structures"]:
        raise ValueError("Unknown platform or information structure")
    units = check_units(brief.get("units"), source, 6)
    relations = check_relations(brief.get("relations", []), units, source, structure)
    defaults = {"single-claim": "focus-hero", "process": "linear-steps", "comparison": "split-compare",
                "hierarchy": "layered-steps", "components": "asymmetric-bento",
                "true-loop": "linear-steps", "timeline": "linear-steps"}
    layout = brief.get("layout", "auto")
    if layout == "auto":
        layout = "vertical-scene-flow" if profiles[platform]["ratio"] == "3:4" else defaults[structure]
    if layout not in registry["layouts"]:
        raise ValueError("Unknown layout")
    if profiles[platform]["ratio"] == "3:4" and layout not in {
        "vertical-scene-flow", "vertical-editorial-crop", "vertical-photo-essay", "carousel-sequence"
    }:
        raise ValueError("Vertical output requires a dedicated vertical layout")
    metaphor = brief.get("metaphor", {"description": "none", "status": "none"})
    if not isinstance(metaphor, dict) or metaphor.get("status") not in {"none", "proposed", "source-literal"}:
        raise ValueError("Separate a proposed metaphor from literal source claims")
    if not isinstance(metaphor.get("description"), str) or not metaphor["description"].strip():
        raise ValueError("Describe the one metaphor or use none")
    if metaphor["status"] == "source-literal":
        anchor(metaphor.get("source_excerpt"), source)
    medium = brief.get("delivery_medium", "raster-concept")
    if medium not in {"raster-concept", "editable-required"}:
        raise ValueError("delivery_medium must be raster-concept or editable-required")
    dataset = None
    if mother == "data-journalism" or brief.get("dataset") is not None:
        dataset = check_dataset(brief.get("dataset"), source)
        medium = "editable-required"
    exact = brief.get("exact_text", [])
    if not isinstance(exact, list) or not all(isinstance(label, str) for label in exact):
        raise ValueError("exact_text must be a list of strings")
    editable_text = medium == "editable-required" or len(exact) > 1 or any(len(label) > 20 for label in exact)
    card = ROOT / "references" / (mother + ".md")
    structured = {"claim": claim, "units": units, "relations": relations, "metaphor": metaphor,
                  "dataset": dataset, "delivery_medium": medium,
                  "semantic_review": "pending", "data_verification": "declared-only" if dataset else "not-applicable"}
    prompt = "\n\n".join([
        "Source material (use only supported facts):\n" + source,
        "Business mother (one visual language, not an illustration-mode mixture):\n" + card.read_text(),
        "Structured content:\n" + json.dumps(structured, ensure_ascii=False, indent=2),
        f"Surface: {platform}; structure: {structure}; layout: {layout}; no fixed character.",
        "Platform: " + profiles[platform]["layout_rule"],
        "Output language: " + brief.get("output_language", "match-user"),
        "Exact text:\n" + "\n".join(exact),
        ("Generate only supporting illustration/background. Keep exact labels and charts in a separate editable medium. Do not invent chart geometry."
         if editable_text else "Preserve short essential labels; inspect every visible term and number."),
        "Show a true loop only with a supported return path. Proposed metaphors are design interpretations, not facts. No invented data, pseudo-sources or generic technology decoration."
    ])
    return {
        "schema_version": "public-visual-plan-v1", "version": "0.1.0", "status": "candidate-plan",
        "workflow": {"kind": "pinshu-business-graphics", "version": "0.1.0"},
        "source": {"path": str(source_path), "sha256": hashlib.sha256(source.encode()).hexdigest(),
                   "file_sha256": digest(source_path)},
        "registry_sha256": digest(CORE / "references/system-registry.json"),
        "mother_card_sha256": digest(card),
        "visual_card": {"character": "none", "task": "business-graphic", "structure": structure,
                        "layout": layout, "mode": None, "mother": mother, "platform": platform,
                        "density": "slide" if platform in {"ppt-16x9", "livestream-16x9"} else "social",
                        "units": len(units)},
        "platform_profile": profiles[platform], "identity_reference": None,
        "structured_content": structured, "text_route": "editable-text-layer" if editable_text else "short-text-with-visual-qa",
        "prompt": prompt,
        "rendering": {"provider": "agent-runtime", "actual_model": None, "channel": None,
                      "strategy": "editable-chart-final" if dataset else medium},
        "required_checks": ["source-faithfulness", "visible-text", "mode-and-composition", "identity-and-actions",
                            "thumbnail-and-crop", "mother-integrity", "metaphor-source-fit", "data-accuracy",
                            "series-consistency", "text-delivery"],
        "acceptance": {"visual_qa": "pending", "human_review": "pending", "production_claim": False}
    }, source


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--brief", required=True, type=Path)
    parser.add_argument("--output-dir", required=True, type=Path)
    args = parser.parse_args()
    try:
        plan, source = compile_business(args.brief)
        save_plan(plan, source, args.brief, args.output_dir)
    except (OSError, ValueError, KeyError, TypeError) as exc:
        parser.exit(1, f"HARD_STOP: {exc}\n")
    print("PLAN READY: mother and source anchors saved; actual visual and semantic review remain pending")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
