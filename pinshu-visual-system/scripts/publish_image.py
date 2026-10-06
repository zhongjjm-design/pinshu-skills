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
from prepare_publish_images import png_chunks, pixel_difference, is_zero_pixel_difference, PublishPrepError

CHECKS = ("source-faithfulness", "visible-text", "mode-and-composition",
          "identity-and-actions", "thumbnail-and-crop")
WORKFLOW_CHECKS = {
    "pinshu-infographic": ("information-relationships", "density-and-reading", "text-delivery"),
    "pinshu-business-graphics": ("mother-integrity", "metaphor-source-fit", "data-accuracy", "series-consistency", "text-delivery"),
    "pinshu-visual-method-test": ("method-grammar", "cultural-source-fit"),
}


def reviewed_editable_source(plan: dict, qa: dict, qa_path: Path, image_hash: str) -> dict | None:
    chart = plan.get("rendering", {}).get("strategy") == "editable-chart-final"
    if plan.get("text_route") != "editable-text-layer" and not chart:
        return None
    evidence = qa.get("editable_source")
    if not isinstance(evidence, dict) or not isinstance(evidence.get("path"), str):
        raise ValueError("An editable chart final requires a reviewed editable_source" if chart else
                         "Editable text delivery requires a reviewed editable_source, not only a background")
    path = Path(evidence["path"])
    if not path.is_absolute():
        path = qa_path.parent / path
    path = path.resolve()
    if not path.is_file() or evidence.get("sha256") != hashlib.sha256(path.read_bytes()).hexdigest():
        raise ValueError("Editable source is missing or its hash does not match")
    if evidence.get("rendered_image_sha256") != image_hash:
        raise ValueError("Editable source review must bind its final rendered image")
    if path.suffix.lower() == ".svg":
        document = ET.fromstring(path.read_bytes())
        for element in document.iter():
            if element.tag.rsplit("}", 1)[-1] in {"script", "foreignObject"}:
                raise ValueError("Editable SVG must use native SVG text and self-contained graphics")
            for attr, value in element.attrib.items():
                if attr.rsplit("}", 1)[-1] == "href" and value and not value.startswith(("data:", "#")):
                    raise ValueError("Embed SVG assets instead of depending on external or local files")
        texts = ["".join(e.itertext()) for e in document.iter() if e.tag.rsplit("}", 1)[-1] == "text"]
    elif path.suffix.lower() == ".pptx":
        texts = []
        with zipfile.ZipFile(path) as deck:
            for name in deck.namelist():
                if name.startswith("ppt/slides/slide") and name.endswith(".xml"):
                    document = ET.fromstring(deck.read(name))
                    texts.extend(e.text or "" for e in document.iter() if e.tag.endswith("}t"))
    else:
        raise ValueError("Supply a native-text SVG or PPTX editable source; a raster/PDF is not editable text")
    normalize = lambda s: "".join(unicodedata.normalize("NFC", s).split())
    native = normalize(" ".join(texts))
    content = plan.get("structured_content", {})
    labels = list(plan.get("visible_labels", [])) + [u["label"] for u in content.get("units", [])]
    labels += [r["verb"] for r in content.get("relations", [])]
    if content.get("claim"):
        labels.append(content["claim"])
    missing = [label for label in set(labels) if normalize(label) not in native]
    if missing:
        raise ValueError("Editable source has missing native labels: " + ", ".join(sorted(missing)))
    if chart:
        # Data geometry still requires actual data-accuracy review; this checks native labels/values only.
        from decimal import Decimal
        import re
        numbers = {Decimal(x.replace(",", "")) for x in re.findall(r"[+-]?(?:\d{1,3}(?:,\d{3})+|\d+)(?:\.\d+)?", " ".join(texts))}
        for row in content.get("dataset", {}).get("rows", []):
            if normalize(row["label"]) not in native or Decimal(str(row["value"])) not in numbers:
                raise ValueError("Editable chart must contain its dataset labels and values as native text")
    return {"path": str(path), "sha256": evidence["sha256"], "rendered_image_sha256": image_hash,
            "native_labels_checked": sorted(set(labels)), "scope": "file/hash/native-text checks; actual composition and data geometry require review"}

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
    editable = reviewed_editable_source(plan, qa, qa_path, expected)
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
    except (OSError, ValueError, KeyError, TypeError, PublishPrepError, ET.ParseError, zipfile.BadZipFile) as exc:
        parser.exit(1, f"HARD_STOP: {exc}\n")
    print(result["status"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
