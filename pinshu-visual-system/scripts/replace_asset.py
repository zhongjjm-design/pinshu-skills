#!/usr/bin/env python3
"""Swap one image in the article's image plan; leave every other image and its review alone.

Use after re-capturing a screenshot or redrawing one picture (meeting 2026-10-12, IMG-05 and IMG-07):

  python3 scripts/replace_asset.py --plan <过程文件夹/配图任务.json> --target 03_TomCC锚词.png \
      --capture-dir <过程文件夹/配图/截图_03_重截> --by "Claude" --reason "原图被浮动栏遮住，重截"
  python3 scripts/replace_asset.py --plan <...> --target 封面横版.png --file <新图> \
      --publish-clean-report <新净化报告> --by "Codex" --reason "封面字太小，重画"

The new files must already sit inside the article's process folder: a fix left in some other
workspace is not a fix. The old files are never touched. The asset keeps a `revisions` list (who,
when, what, old and new hash). Its earlier phone review no longer applies and is cleared; the
other images keep theirs. Then run the ready-article entry into a new output folder with
`--carry-reviews-from <previous output folder>` so only the changed image needs a new look.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

from portable import local_now, ensure_utf8_mode


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _resolve(base: Path, value: str) -> Path:
    path = Path(value).expanduser()
    return (path if path.is_absolute() else base / path).resolve()


def _inside(path: Path, folder: Path, label: str) -> Path:
    path = path.resolve()
    if not path.is_relative_to(folder):
        raise ValueError(f"{label} must be inside the article process folder {folder}; copy it there first: {path}")
    if not path.is_file():
        raise ValueError(f"{label} does not exist: {path}")
    return path


def find_asset(plan: dict, base: Path, target: str) -> int:
    hits = [i for i, a in enumerate(plan["assets"])
            if target in {a.get("filename"), Path(a.get("file", "")).name, str(_resolve(base, a.get("file", "")))}]
    if len(hits) != 1:
        names = [a.get("filename") or Path(a.get("file", "")).name for a in plan["assets"]]
        raise ValueError(f"--target must name exactly one image in the plan; found {len(hits)}. Images: {', '.join(names)}")
    return hits[0]


def replace(plan_path: Path, target: str, by: str, reason: str, process_dir: Path | None = None,
            capture_dir: Path | None = None, file: Path | None = None, original_file: Path | None = None,
            publish_clean_report: Path | None = None, editable_source: Path | None = None,
            render_receipt: Path | None = None) -> dict:
    if not by.strip() or not reason.strip():
        raise ValueError("--by and --reason are required: say who changed the image and why")
    plan_path = plan_path.resolve()
    process = (process_dir or plan_path.parent).resolve()
    raw = plan_path.read_bytes()
    plan = json.loads(raw.decode("utf-8"))
    index = find_asset(plan, plan_path.parent, target)
    asset = dict(plan["assets"][index])
    old_file = _resolve(plan_path.parent, asset["file"])
    # Keep the name the layout and captions know; a capture folder always calls its file 截图.png.
    asset.setdefault("filename", old_file.name)
    old_hash = sha(old_file) if old_file.is_file() else None
    if bool(capture_dir) == bool(file):
        raise ValueError("Give exactly one of --capture-dir (a new screenshot) or --file (a new image)")
    if capture_dir:
        if asset.get("asset_kind") != "evidence-screenshot":
            raise ValueError("--capture-dir is only for evidence screenshots")
        capture_dir = capture_dir.resolve()
        receipt_path = capture_dir / "截图回执.json"
        if not receipt_path.is_file():
            raise ValueError(f"No successful capture in {capture_dir} (截图回执.json missing)")
        receipt = json.loads(receipt_path.read_text(encoding="utf-8"))
        new_file = _inside(capture_dir / "截图.png", process, "New screenshot")
        if receipt.get("delivery_sha256") != sha(new_file):
            raise ValueError("截图.png differs from its receipt; re-capture instead of editing the image")
        captured = receipt.get("original_url") or receipt.get("source_url")
        if asset.get("source_url") and captured and captured != asset["source_url"]:
            raise ValueError(f"Capture is of another page ({captured}), not {asset['source_url']}")
        original = Path(receipt["original_file"]) if receipt.get("original_file") else capture_dir / "原始截图.png"
        original = _inside(original, process, "Original screenshot")
        if receipt.get("frame_baked", False) is not False:
            raise ValueError("New screenshots must be unframed; re-capture without a baked frame")
        # Processing claims belong to the old pixels, not to this asset's stable slot.
        old_disclosure = asset.get("composition_disclosure") or asset.get("capture_receipt", {}).get("composition_disclosure")
        if old_disclosure and asset.get("caption") == old_disclosure:
            asset.pop("caption", None)
        for key in ("processing", "composition_receipt", "composition_disclosure", "acquisition_warning"):
            asset.pop(key, None)
        asset.update(file=str(new_file), original_file=str(original), captured_at=receipt["captured_at"],
                     capture_receipt=receipt, acquisition="new-capture", frame_baked=False)
    else:
        new_file = _inside(file, process, "New image")
        asset["file"] = str(new_file)
        kind = asset.get("asset_kind")
        if kind == "generated-visual":
            if not publish_clean_report:
                raise ValueError("A generated image needs its new --publish-clean-report (publish copy check)")
            asset["publish_clean_report"] = str(_inside(publish_clean_report, process, "Publish-clean report"))
        elif kind == "rendered-graphic":
            if not (editable_source and render_receipt):
                raise ValueError("A program-drawn graphic needs --editable-source and --render-receipt")
            asset["editable_source"] = str(_inside(editable_source, process, "Editable source"))
            asset["render_receipt"] = str(_inside(render_receipt, process, "Render receipt"))
        elif kind == "evidence-screenshot":
            raise ValueError("Use --capture-dir for screenshots, so the capture receipt comes along")
        if original_file:
            asset["original_file"] = str(_inside(original_file, process, "Original file"))
    new_hash = sha(new_file)
    if new_hash == old_hash:
        raise ValueError("The new image is identical to the current one; nothing to replace")
    asset.pop("mobile_review", None)
    asset["review_state"] = "待确认（已替换，需重新看图）"
    revisions = list(asset.get("revisions", []))
    revisions.append({"at": local_now().isoformat(timespec="seconds"), "by": by.strip(), "reason": reason.strip(),
                      "old_file": str(old_file), "old_sha256": old_hash, "new_file": str(new_file), "new_sha256": new_hash})
    asset["revisions"] = revisions
    plan["assets"][index] = asset
    if plan_path.read_bytes() != raw:
        raise ValueError("The image plan changed while replacing; run again")
    temporary = plan_path.with_name(plan_path.name + ".replace-tmp")
    temporary.write_text(json.dumps(plan, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    temporary.replace(plan_path)
    return {"replaced": asset.get("filename") or Path(asset["file"]).name, "old_sha256": old_hash,
            "new_sha256": new_hash, "unchanged_assets": len(plan["assets"]) - 1, "plan": str(plan_path)}


if __name__ == "__main__":
    ensure_utf8_mode()
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--plan", type=Path, required=True)
    p.add_argument("--target", required=True, help="the image to replace: its filename, current file name or path")
    p.add_argument("--by", required=True, help="who made the fix (Agent or person)")
    p.add_argument("--reason", required=True, help="what was wrong and what changed, in plain words")
    p.add_argument("--process-dir", type=Path, help="the article's process folder (default: the plan's folder)")
    p.add_argument("--capture-dir", type=Path, help="output folder of a successful capture_evidence.py run")
    p.add_argument("--file", type=Path, help="the new image (not a screenshot)")
    p.add_argument("--original-file", type=Path)
    p.add_argument("--publish-clean-report", type=Path)
    p.add_argument("--editable-source", type=Path)
    p.add_argument("--render-receipt", type=Path)
    a = p.parse_args()
    try:
        print(json.dumps(replace(a.plan, a.target, a.by, a.reason, a.process_dir, a.capture_dir, a.file,
                                 a.original_file, a.publish_clean_report, a.editable_source, a.render_receipt),
                         ensure_ascii=False, indent=2))
    except ValueError as exc:
        p.exit(1, f"replace_asset.py: {exc}\n")
