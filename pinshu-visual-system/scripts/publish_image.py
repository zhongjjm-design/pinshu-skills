#!/usr/bin/env python3
"""Prepare a reviewed candidate; stop on any export or copy-verification failure."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import sys

CHECKS = ("source-faithfulness", "visible-text", "mode-and-composition",
          "identity-and-actions", "thumbnail-and-crop")
WORKFLOW_CHECKS = {
    "pinshu-infographic": ("information-relationships", "density-and-reading", "text-delivery"),
    "pinshu-business-graphics": ("mother-integrity", "metaphor-source-fit", "data-accuracy", "series-consistency", "text-delivery"),
    "pinshu-visual-method-test": ("method-grammar", "cultural-source-fit"),
}

def prepare(source: Path, plan_path: Path, qa_path: Path, output_dir: Path) -> dict:
    plan = json.loads(plan_path.read_text())
    qa = json.loads(qa_path.read_text())
    expected = hashlib.sha256(source.read_bytes()).hexdigest()
    if plan.get("schema_version") != "public-visual-plan-v1":
        raise ValueError("Not a supported public visual plan")
    if qa.get("source_sha256") != expected or qa.get("plan_sha256") != hashlib.sha256(plan_path.read_bytes()).hexdigest():
        raise ValueError("Visual review does not match this image and plan")
    if not qa.get("reviewer") or not qa.get("notes"):
        raise ValueError("Name the reviewer and record actual visual observations")
    workflow = plan.get("workflow")
    kind = workflow.get("kind") if isinstance(workflow, dict) else None
    if workflow is not None and kind not in WORKFLOW_CHECKS:
        raise ValueError("Unknown specialized visual workflow")
    required = CHECKS + WORKFLOW_CHECKS.get(kind, ())
    if any(qa.get("checks", {}).get(check) != "pass" for check in required):
        raise ValueError("Visual review is incomplete or contains failures")
    if kind == "pinshu-business-graphics" and plan.get("rendering", {}).get("strategy") == "editable-chart-final":
        raise ValueError("An editable chart final is required; a raster candidate cannot replace it")
    output_dir.mkdir(parents=True, exist_ok=False)
    scripts = Path(__file__).resolve().parent
    export_dir, clean_dir = output_dir / "platform", output_dir / "publish-clean"
    commands = [
        [sys.executable, str(scripts / "export_platform_image.py"), "--source", str(source),
         "--platform", plan["visual_card"]["platform"], "--output-dir", str(export_dir)],
        [sys.executable, str(scripts / "prepare_publish_images.py"), "--output-dir", str(clean_dir),
         str(export_dir / "platform-export.png")]
    ]
    for command in commands:
        result = subprocess.run(command, capture_output=True, text=True)
        if result.returncode:
            raise ValueError("Preparation failed; no source-image fallback: " + (result.stderr or result.stdout).strip())
    export = json.loads((export_dir / "platform-export-report.json").read_text())
    clean = json.loads((clean_dir / "publish-clean-report.json").read_text())
    if export.get("status") != "PASS" or clean.get("status") != "PASS":
        raise ValueError("A mechanical report did not pass")
    result = {"status": "candidate-ready-for-review", "original": str(source.resolve()),
              "source_sha256": expected, "visual_review": str(qa_path.resolve()),
              "platform_export": export, "publish_copy": clean,
              "human_review": "pending", "aesthetic_approval": False}
    (output_dir / "delivery-report.json").write_text(json.dumps(result, indent=2) + "\n")
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ["source", "plan", "qa", "output-dir"]:
        parser.add_argument("--" + name, required=True, type=Path)
    args = parser.parse_args()
    try:
        result = prepare(args.source, args.plan, args.qa, args.output_dir)
    except (OSError, ValueError, KeyError, TypeError) as exc:
        parser.exit(1, f"HARD_STOP: {exc}\n")
    print(result["status"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
