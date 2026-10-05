#!/usr/bin/env python3
"""Compile a portable visual contract; rendering and visual acceptance are separate."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_configs() -> tuple[dict, dict]:
    registry = json.loads((ROOT / "references/system-registry.json").read_text())
    profiles = json.loads((ROOT / "references/platform-profiles.json").read_text())
    return registry, {item["id"]: item for item in profiles["profiles"]}


def compile_plan(content: str, platform: str, mode_id: str, structure: str,
                 layout: str = "auto", title: str = "", candidate_test: bool = False,
                 character_profile: Path | None = None, exact_text: list[str] | None = None,
                 units: int = 3, source_path: Path | None = None) -> dict:
    if not content.strip():
        raise ValueError("Source content is empty")
    registry, profiles = load_configs()
    modes = {item["id"]: item for item in registry["modes"]}
    if platform not in profiles or mode_id not in modes:
        raise ValueError("Unknown platform or mode")
    if structure not in registry["structures"]:
        raise ValueError("Unknown information structure")
    mode = modes[mode_id]
    if structure not in mode["supported_structures"]:
        raise ValueError("The selected mode cannot carry this information structure")
    if platform in mode["blocked_platforms"]:
        raise ValueError("The selected mode is blocked on this platform")
    if mode["status"] == "candidate-frozen":
        raise ValueError("This candidate is frozen and cannot be generated")
    if mode["status"] == "candidate" and not candidate_test:
        raise ValueError("Candidate modes require --candidate-test for a single image")
    if not 1 <= units <= mode["max_units"]:
        raise ValueError("Information density exceeds the mode limit; split the content")
    if mode_id == "hand-drawn-comparison-comic" and units > 2:
        raise ValueError("Comparison comics are limited to two main scenes")
    defaults = {"single-claim": "focus-hero", "comparison": "split-compare",
                "process": "linear-steps", "hierarchy": "layered-steps",
                "components": "asymmetric-bento", "true-loop": "linear-steps",
                "timeline": "linear-steps"}
    if layout == "auto":
        layout = "vertical-scene-flow" if profiles[platform]["ratio"] == "3:4" else defaults[structure]
    if layout not in registry["layouts"]:
        raise ValueError("Unknown layout")
    if profiles[platform]["ratio"] == "3:4" and layout not in {
        "vertical-scene-flow", "vertical-editorial-crop", "vertical-photo-essay", "carousel-sequence"
    }:
        raise ValueError("Vertical output requires a dedicated vertical layout")

    character_id, identity, rules = "none", None, "Do not include a fixed branded character."
    if character_profile:
        if mode["character_policy"] == "none-only":
            raise ValueError("This mode excludes fixed characters; choose a tested character mode")
        profile_path = character_profile.resolve()
        character = json.loads(profile_path.read_text())
        character_id = character.get("id", "")
        if not character_id or character_id == "none" or character.get("status") != "approved":
            raise ValueError("A nonempty approved character identity is required")
        asset_path = character.get("identity_asset", "")
        if not asset_path:
            raise ValueError("Character profile has no identity asset")
        asset = Path(asset_path)
        if not asset.is_absolute():
            asset = profile_path.parent / asset
        asset = asset.resolve()
        if not asset.is_file():
            raise ValueError("Character identity asset is missing")
        if mode_id not in character.get("tested_modes", []):
            raise ValueError("This character/mode combination has not been approved")
        constraints = character.get("constraints")
        if not isinstance(constraints, list) or not constraints or not all(isinstance(x, str) for x in constraints):
            raise ValueError("Character constraints must be a nonempty list of text rules")
        if character.get("dominant_hand") not in {"left", "right"}:
            raise ValueError("Declare the character's anatomical dominant hand")
        identity = {"path": str(asset), "sha256": digest(asset)}
        rules = ("Load the actual identity image; it overrides pose and style references. "
                 + " ".join(constraints) + " Use the anatomical " + character["dominant_hand"]
                 + " hand for writing, tools and primary actions. Do not infer hands from screen position.")
    if mode["character_policy"] == "required" and identity is None:
        raise ValueError("Character Presenter requires a supplied approved identity profile")

    exact = exact_text or []
    if not all(isinstance(item, str) for item in exact):
        raise ValueError("Exact labels must be text")
    editable_text = len(exact) > 1 or any(len(item) > 20 for item in exact) or mode_id == "archive-tabletop-editorial"
    card = ROOT / mode["mode_card"]
    text_route = "editable-text-layer" if editable_text else "short-text-with-visual-qa"
    prompt = "\n\n".join([
        "Source material (use only supported facts):\n" + content,
        "Visual title:\n" + title,
        f"Visual contract: character={character_id}; structure={structure}; layout={layout}; mode={mode_id}; platform={platform}; units={units}.",
        ("For a true loop, draw a directed sequence with a visible return path from the last step to the first. The source must support that feedback relationship; a hub-and-spoke diagram is not a loop."
         if structure == "true-loop" else "Preserve the selected information relationship; do not add causal arrows unsupported by the source."),
        "Complete mode grammar:\n" + card.read_text(),
        "Character requirements:\n" + rules,
        "Platform requirements:\n" + profiles[platform]["layout_rule"],
        "Exact visible labels (preserve their original language):\n" + "\n".join(exact),
        ("Generate an illustration/background without text. Compose the exact labels in a separate editable layer; do not erase or paint over generated lettering."
         if editable_text else "Inspect every visible name, number and character against the source."),
        "One focal point and one main relationship. Never invent facts, personal experiences, brands, data or evidence."
    ])
    return {
        "schema_version": "public-visual-plan-v1", "version": registry["version"],
        "status": "candidate-plan", "mode_status": mode["status"],
        "source": {"sha256": hashlib.sha256(content.encode()).hexdigest(),
                   "path": str(source_path.resolve()) if source_path else None,
                   "file_sha256": digest(source_path) if source_path else None},
        "registry_sha256": digest(ROOT / "references/system-registry.json"),
        "mode_card_sha256": digest(card),
        "visual_card": {"character": character_id, "task": "article-cover" if "cover" in platform else "content-visual",
                        "structure": structure, "layout": layout, "mode": mode_id, "platform": platform,
                        "density": "slide" if platform in {"ppt-16x9", "livestream-16x9"} else "social", "units": units},
        "platform_profile": profiles[platform], "identity_reference": identity,
        "text_route": text_route, "prompt": prompt,
        "rendering": {"provider": "agent-runtime", "actual_model": None, "channel": None,
                      "instruction": "Use the available image tool; record the actual returned model/channel without guessing."},
        "required_checks": ["source-faithfulness", "visible-text", "mode-and-composition", "identity-and-actions", "thumbnail-and-crop"],
        "acceptance": {"visual_qa": "pending", "human_review": "pending", "production_claim": False}
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--content-file", required=True, type=Path)
    parser.add_argument("--platform", required=True)
    parser.add_argument("--mode", required=True)
    parser.add_argument("--structure", required=True)
    parser.add_argument("--layout", default="auto")
    parser.add_argument("--title", default="")
    parser.add_argument("--units", default=3, type=int)
    parser.add_argument("--candidate-test", action="store_true")
    parser.add_argument("--character-profile", type=Path)
    parser.add_argument("--exact-text", action="append")
    parser.add_argument("--output-dir", required=True, type=Path)
    args = parser.parse_args()
    try:
        content = args.content_file.read_text(encoding="utf-8")
        plan = compile_plan(content, args.platform, args.mode, args.structure, args.layout,
                            args.title, args.candidate_test, args.character_profile,
                            args.exact_text, args.units, args.content_file)
        args.output_dir.mkdir(parents=True, exist_ok=False)
        (args.output_dir / "source-content.txt").write_text(content, encoding="utf-8")
        (args.output_dir / "prompt-final.txt").write_text(plan["prompt"], encoding="utf-8")
        (args.output_dir / "route-plan.json").write_text(json.dumps(plan, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    except (OSError, ValueError, KeyError, TypeError) as exc:
        parser.exit(1, f"HARD_STOP: {exc}\n")
    print("PLAN READY: rendering and visual acceptance remain pending")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
