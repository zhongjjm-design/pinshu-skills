#!/usr/bin/env python3
"""Prepare a reviewed candidate; stop on any export or copy-verification failure."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import shutil
import struct
import unicodedata
import xml.etree.ElementTree as ET
import zipfile
import re
from decimal import Decimal, InvalidOperation
from render_editable import native_inventory, verify_render
from prepare_publish_images import png_chunks, pixel_difference, is_zero_pixel_difference, PublishPrepError

CHECKS = ("source-faithfulness", "visible-text", "mode-and-composition",
          "identity-and-actions", "thumbnail-and-crop")
WORKFLOW_CHECKS = {
    "pinshu-infographic": ("information-relationships", "density-and-reading", "text-delivery"),
    "pinshu-business-graphics": ("mother-integrity", "metaphor-source-fit", "data-accuracy", "series-consistency", "text-delivery"),
    "pinshu-visual-method-test": ("method-grammar", "cultural-source-fit"),
}


def reviewed_editable_source(plan: dict, qa: dict, qa_path: Path, image_hash: str, image_path: Path) -> dict | None:
    chart = plan.get("rendering", {}).get("strategy") == "editable-chart-final"
    if plan.get("text_route") != "editable-text-layer" and not chart:
        return None
    evidence = qa.get("editable_source")
    if not isinstance(evidence, dict) or not isinstance(evidence.get("path"), str):
        raise ValueError("An editable chart final requires a reviewed editable_source" if chart else
                         "Editable text delivery requires a reviewed editable_source, not only a background")
    resolve = lambda value: (qa_path.parent / value).resolve()
    path = resolve(evidence["path"])
    if not path.is_file() or evidence.get("sha256") != hashlib.sha256(path.read_bytes()).hexdigest():
        raise ValueError("Editable source is missing or its hash does not match")
    if evidence.get("rendered_image_sha256") != image_hash:
        raise ValueError("Editable source review must bind its final rendered image")
    receipt_path = resolve(evidence.get("render_receipt", ""))
    if not receipt_path.is_file():
        raise ValueError("Editable delivery requires a render_editable.py render_receipt; declarations alone do not bind pixels")
    receipt = json.loads(receipt_path.read_text())
    inventory = native_inventory(path, receipt.get("slide", 1))
    normalize = lambda text: "".join(unicodedata.normalize("NFC", text).split())
    segments = {normalize(text) for text in inventory["texts"]}
    content = plan.get("structured_content", {})
    labels = list(plan.get("visible_labels", [])) + [u["label"] for u in content.get("units", [])]
    labels += [r["verb"] for r in content.get("relations", [])]
    if content.get("claim"):
        labels.append(content["claim"])
    missing = [label for label in set(labels) if normalize(label) not in segments]
    if missing:
        raise ValueError("Editable source has missing native labels (whole text segments): " + ", ".join(sorted(missing)))
    dataset = content.get("dataset") or {}
    if chart:
        numbers = {Decimal(x.replace(",", "")) for text in inventory["texts"] for x in
                   re.findall(r"[+-]?(?:\d{1,3}(?:,\d{3})+|\d+)(?:\.\d+)?", text)}
        for row in dataset.get("rows", []):
            unit = unicodedata.normalize("NFKC", row.get("units", dataset.get("units", ""))).lower()
            formatted = inventory.get("formatted_chart_points", [])
            if unit in {"%", "percent", "percentage"} and any(p[0] == row["label"] for p in formatted):
                native_pair = (row["label"], Decimal(str(row["value"])), "%") in formatted
            else:
                native_pair = (row["label"], Decimal(str(row["value"]))) in inventory["chart_points"]
            text_pair = normalize(row["label"]) in segments and Decimal(str(row["value"])) in numbers
            if not native_pair and not text_pair:
                raise ValueError("Editable chart must contain its dataset labels and values as native text or linked chart data")
    original = ""
    source_info = plan.get("source", {})
    if source_info.get("path"):
        source_file = Path(source_info["path"])
        if source_file.is_file():
            if hashlib.sha256(source_file.read_bytes()).hexdigest() != source_info.get("file_sha256", source_info.get("sha256")):
                raise ValueError("Original source changed; review the plan and visible text again")
            original = source_file.read_text()
    allowed = {normalize(x) for x in labels + [row["label"] for row in dataset.get("rows", [])]}
    declarations = {normalize(item["text"]): item for item in qa.get("additional_text_review", [])}
    additional = []
    # Whole lines/sentences retain conditions that a bare substring can omit.
    source_segments = {normalize(part.strip(" #*-\t")) for part in re.split(r"[\n\r\u3002\uff01\uff1f!?;\uff1b]", original) if part.strip()}
    for text in inventory["texts"]:
        if normalize(text) in allowed:
            continue
        if original and normalize(text).rstrip(".:!?;\u3002\uff01\uff1f\uff1b\uff1a") in {part.rstrip(".:!?;\u3002\uff01\uff1f\uff1b\uff1a") for part in source_segments}:
            additional.append({"text": text, "origin": "literal-source"})
            continue
        item = declarations.get(normalize(text))
        if not item or item.get("origin") not in {"editorial-paraphrase", "structural-label", "dataset-value"} or not item.get("reason"):
            raise ValueError("Unreviewed additional native text: " + text + "; list it in additional_text_review with origin and reason")
        if item["origin"] == "editorial-paraphrase" and (not item.get("source_excerpt") or item["source_excerpt"] not in original):
            raise ValueError("Additional paraphrase needs a matching source_excerpt")
        if item["origin"] == "editorial-paraphrase" and any(c.isdigit() for c in unicodedata.normalize("NFKC", text)):
            raise ValueError("Numeric paraphrases must be explicit planned labels with source review, not additional annotations")
        if item["origin"] == "structural-label":
            value = unicodedata.normalize("NFKC", text)
            if any(c.isdigit() for c in value) or len(value) > 40:
                raise ValueError("Structural labels must be short nonnumeric headings; source factual or numeric annotations explicitly")
        if item["origin"] == "dataset-value":
            value = unicodedata.normalize("NFKC", text).strip().replace(",", "")
            matched = False
            for row in dataset.get("rows", []):
                unit = unicodedata.normalize("NFKC", row.get("units", dataset.get("units", ""))).strip()
                token = value[:-len(unit)].strip() if unit and value.endswith(unit) else value
                try:
                    matched |= Decimal(token) == Decimal(str(row["value"]))
                except InvalidOperation:
                    pass
            if not matched:
                raise ValueError("Additional dataset-value must be a numeric value from this plan's dataset, optionally with its unit")
        additional.append(dict(item, semantic_approval="declared-review-only"))
    binding = verify_render(path, image_path, receipt, plan["visual_card"]["platform"])
    return {"path": str(path), "sha256": evidence["sha256"], "rendered_image_sha256": image_hash,
            "render_receipt": str(receipt_path), "render_receipt_sha256": hashlib.sha256(receipt_path.read_bytes()).hexdigest(),
            "native_labels_checked": sorted(set(labels)), "additional_text_review": additional, **binding,
            "scope": "native labels/data and actual re-render pixel binding; semantics, other visibility and chart geometry require review"}

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
    editable = reviewed_editable_source(plan, qa, qa_path, expected, source)
    if qa.get("review_stage") != "final-platform-image":
        raise ValueError("Export first, inspect the final platform image and thumbnail, then write review_stage=final-platform-image")
    chunks = png_chunks(source.read_bytes())
    width, height = struct.unpack(">II", chunks[0][1][:8])
    size = plan["platform_profile"]["publish_size"]
    if (width, height) != (int(size["width"]), int(size["height"])):
        raise ValueError("Reviewed source is not at final platform dimensions; run export_platform_image.py and review its output before delivery")
    magick = shutil.which("magick")
    if not magick:
        raise ValueError("ImageMagick 7 is required for verified delivery")
    output_dir.mkdir(parents=True, exist_ok=False)
    scripts = Path(__file__).resolve().parent
    export_dir, clean_dir = output_dir / "platform", output_dir / "publish-clean"
    commands = [
        [sys.executable, str(scripts / "export_platform_image.py"), "--source", str(source),
         "--platform", plan["visual_card"]["platform"], "--fit", "contain", "--output-dir", str(export_dir)],
        [sys.executable, str(scripts / "prepare_publish_images.py"), "--output-dir", str(clean_dir),
         str(export_dir / "platform-export.png")]
    ]
    try:
        for command in commands:
            result = subprocess.run(command, capture_output=True, text=True)
            if result.returncode:
                raise ValueError("Preparation failed; no source-image fallback: " + (result.stderr or result.stdout).strip())
        export = json.loads((export_dir / "platform-export-report.json").read_text())
        clean = json.loads((clean_dir / "publish-clean-report.json").read_text())
        if export.get("status") != "PASS" or clean.get("status") != "PASS":
            raise ValueError("A mechanical report did not pass")
        if not is_zero_pixel_difference(pixel_difference(magick, source, export_dir / "platform-export.png")):
            raise ValueError("Final export changed reviewed pixels; review that image again")
        if editable:
            saved = output_dir / "editable-source" / Path(editable["path"]).name
            saved.parent.mkdir()
            shutil.copyfile(editable["path"], saved)
            if hashlib.sha256(saved.read_bytes()).hexdigest() != editable["sha256"]:
                raise ValueError("Editable delivery copy changed")
            editable["delivery_copy"] = str(saved.resolve())
            shutil.copyfile(editable["render_receipt"], saved.parent / "render-receipt.json")
    except Exception as exc:
        (output_dir / "delivery-report.json").write_text(json.dumps({"status": "FAIL", "deliverable": False,
            "error": str(exc), "intermediates": "not approved for delivery"}, indent=2) + "\n")
        raise
    result = {"status": "candidate-ready-for-review", "original": str(source.resolve()),
              "source_sha256": expected, "visual_review": str(qa_path.resolve()),
              "platform_export": export, "publish_copy": clean, "editable_source": editable,
              "reviewed_export_pixel_difference_ae": 0,
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
    except (OSError, ValueError, KeyError, TypeError, PublishPrepError, ET.ParseError, zipfile.BadZipFile, subprocess.TimeoutExpired) as exc:
        parser.exit(1, f"HARD_STOP: {exc}\n")
    print(result["status"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
