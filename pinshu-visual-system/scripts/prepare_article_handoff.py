#!/usr/bin/env python3
"""Bind prepared article assets to the installed WeChat layout contract."""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import re
import shutil
import sys
from pathlib import Path
from urllib.parse import urlparse


KINDS = {"generated-visual", "evidence-screenshot", "real-photo", "rendered-graphic"}
ROLES = {"body", "cover_landscape", "cover_square"}


def export_capture_requests(plan_path: Path, out: Path) -> Path:
    """Export pending evidence work using only the standard library, without a browser."""
    plan_path = plan_path.resolve()
    plan = json.loads(plan_path.read_text(encoding="utf-8"))
    source = Path(plan["source_md"])
    source = (source if source.is_absolute() else plan_path.parent / source).resolve()
    raw = source.read_bytes()
    source_hash = hashlib.sha256(raw).hexdigest()
    if source_hash != plan["article_sha256"]:
        raise ValueError("Source changed since the image plan; update the plan and anchors")
    text = raw.decode("utf-8")
    requests, names = [], set()
    for asset in plan["assets"]:
        if asset.get("asset_kind") != "evidence-screenshot":
            continue
        # Existing screenshots need no deferred capture; pending items have no final file.
        if asset.get("file") and asset.get("review_state") != "capture-pending":
            continue
        url = asset.get("source_url", "")
        if urlparse(url).scheme not in {"http", "https"} or not urlparse(url).netloc:
            raise ValueError("Capture request needs an HTTP(S) source URL")
        for key in ("capture_region", "filename", "purpose"):
            if not isinstance(asset.get(key), str) or not asset[key].strip():
                raise ValueError("Capture request needs " + key)
        name = asset["filename"]
        if Path(name).name != name or name in names or Path(name).suffix.lower() not in {".png", ".jpg", ".jpeg", ".webp"}:
            raise ValueError("Duplicate or nonlocal capture filename: " + name)
        names.add(name)
        role = asset.get("role", "body")
        if role not in ROLES:
            raise ValueError("Unknown capture role")
        paragraph, prefix = asset.get("after_paragraph", ""), asset.get("after_prefix", "")
        # Keep this fallback standard-library-only; do not require the installed
        # layout/browser just to delegate a capture. Match a complete Markdown
        # paragraph (not a substring), preserving its original inline markup.
        article = text.split("\n===EDITOR NOTES===", 1)[0].replace("\r\n", "\n")
        full_blocks = re.split(r"\n\s*\n", article.strip())
        if role == "body" and (not paragraph or full_blocks.count(paragraph.strip()) != 1 or not prefix):
            raise ValueError("Capture request needs a unique complete verbatim after_paragraph and its after_prefix")
        requests.append({"filename": name, "role": role, "source_url": url,
                         "attribution": asset.get("attribution", "待截图时核对来源作者"),
                         "capture_region": asset["capture_region"], "purpose": asset["purpose"],
                         "after_paragraph": paragraph, "after_prefix": prefix,
                         "review_state": "capture-pending", "frame_baked": False,
                         "capture_scale": 2, "delivery_width_px": 1080,
                         "resolution_rule": "核实际像素，足够时缩到1080；不足重新高清捕获，禁止放大低清图",
                         "completion_rule": "无框，保留高分辨率原图与实际截图时间；禁止AI生图替代证据"})
    if not requests:
        raise ValueError("No pending evidence screenshots in the plan")
    data = {"schema": "pinshu.capture-requests/1", "status": "capture-pending",
            "source_md": str(source), "article_sha256": source_hash,
            "anchor_validation": "唯一原文片段核对；素材回填后仍须由排版解析器核段落",
            "requests": requests}
    lines = ["# 待截图清单", "", "状态：待截图；不是可发布的排版交接。", "",
             "正文：" + str(source), "正文 SHA256：" + source_hash, "",
             "交给具备截图能力的 Agent，或人工用截图工具（如 CleanShot X）手动截。截图本身不加框。",
             "2 倍捕获后核实际像素，再等比缩到 1080；保留原图，不放大低清图，不用 AI 顶替。", ""]
    for item in requests:
        lines.extend(["## " + item["filename"], "", "出处：" + item["source_url"],
                      "准确区域：" + item["capture_region"], "作用：" + item["purpose"],
                      "放在以下段落后：", "", item["after_paragraph"] or "封面，不插正文段落", "",
                      "排版锚点：" + item["after_prefix"], "约定文件名：" + item["filename"], ""])
    out = out.resolve()
    out.mkdir(parents=True, exist_ok=False)
    (out / "待截图清单.json").write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    result = out / "待截图清单.md"
    result.write_text("\n".join(lines), encoding="utf-8")
    return result


def load_layout(folder: Path):
    scripts = folder.resolve() / "scripts"
    if not (scripts / "build.py").is_file():
        raise ValueError("Install pinshu-wechat-layout or pass --layout-skill")
    sys.path.insert(0, str(scripts))
    spec = importlib.util.spec_from_file_location("pinshu_layout_contract", scripts / "build.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def prepare(plan_path: Path, out: Path, layout_skill: Path) -> Path:
    layout = load_layout(layout_skill)
    plan_path = plan_path.resolve()
    plan = json.loads(plan_path.read_text(encoding="utf-8"))
    source = layout.locate(plan_path.parent, plan["source_md"])
    source_hash = layout.sha(source)
    if source_hash != plan["article_sha256"]:
        raise ValueError("Source changed since the image plan; update the plan and anchors")
    _, blocks = layout.parse_markdown(source)
    paragraphs = [b.get_text(" ", strip=True) for b in blocks if b.name == "p"]
    files, body_images, covers = [], [], {}
    names, anchors = set(), set()
    for asset in plan["assets"]:
        kind, role = asset["asset_kind"], asset["role"]
        if kind not in KINDS or role not in ROLES:
            raise ValueError("Unknown asset kind or role")
        if not asset.get("purpose", "").strip():
            raise ValueError("Each image needs an explicit reader-facing purpose")
        file = layout.locate(plan_path.parent, asset["file"])
        if not file.is_file() or file.suffix.lower() not in {".png", ".jpg", ".jpeg", ".webp"}:
            raise ValueError("Expected a prepared local PNG/JPEG/WebP: " + str(file))
        name = asset.get("filename", file.name)
        if not name or name in {".", ".."} or Path(name).name != name or name in names:
            raise ValueError("Duplicate or nonlocal output filename: " + name)
        if Path(name).suffix.lower() != file.suffix.lower():
            raise ValueError("Output extension must match the prepared image")
        names.add(name)
        frame = asset.get("frame_baked", False)
        if type(frame) is not bool:
            raise ValueError("frame_baked must be a Boolean")
        item = {"filename": name, "sha256": layout.sha(file),
                "asset_kind": kind, "role": role, "production_source": str(file),
                "purpose": asset["purpose"], "frame_baked": frame,
                "review_state": asset.get("review_state", "待确认")}
        if kind == "evidence-screenshot":
            acquisition = asset.get("acquisition")
            if acquisition is None:
                raise ValueError("Screenshot acquisition must be explicitly declared")
            if acquisition not in {"new-capture", "reused", "unknown"}:
                raise ValueError("Screenshot acquisition must be new-capture, reused or unknown")
            if acquisition != "reused" and frame:
                raise ValueError("New screenshots must be unframed; layout supplies the frame")
            item["acquisition"] = acquisition
            # These are review evidence, never an automatic visual acceptance.
            for key in ("capture_receipt", "mobile_review"):
                if key in asset:
                    if not isinstance(asset[key], dict):
                        raise ValueError(key + " must be a JSON object")
                    item[key] = asset[key]
            receipt = item.get("capture_receipt", {})
            if frame and acquisition == "reused":
                legacy_hash = receipt.get("delivery_sha256") or receipt.get("output_sha256")
                if legacy_hash != item["sha256"] or not receipt.get("captured_at"):
                    raise ValueError("Framed reused screenshots need a dated hash-bound capture receipt")
            recorded_hash = receipt.get("delivery_sha256") or receipt.get("output_sha256")
            if recorded_hash and recorded_hash != item["sha256"]:
                raise ValueError("Screenshot differs from its capture receipt: " + name)
            review = item.get("mobile_review", {})
            if review.get("image_sha256") and review["image_sha256"] != item["sha256"]:
                raise ValueError("Screenshot differs from its mobile review: " + name)
            if review and not review.get("image_sha256"):
                item["mobile_review"] = {"state": "unknown", "reason": "No image hash; previous judgment is not valid for this file",
                                         "unverified_previous_record": review}
            if acquisition == "new-capture":
                if not receipt.get("delivery_sha256") or not receipt.get("captured_at"):
                    item["acquisition"] = "unknown"
                    item["acquisition_warning"] = "Claimed new capture lacks a bound, dated receipt"
                elif receipt["captured_at"] != asset.get("captured_at"):
                    raise ValueError("Screenshot capture time differs from its receipt: " + name)
                if receipt.get("source_url") and receipt["source_url"] != asset.get("source_url"):
                    raise ValueError("Screenshot source URL differs from its receipt: " + name)
        # Editorial metadata is distinct from the seven-field visual card.
        if "image_function" in asset and asset["image_function"] not in {"evidence", "explanation", "concept"}:
            raise ValueError("Unknown image function")
        for key in ("image_function", "message", "visual_relation", "generation_reason", "feedback_ids", "feedback_response"):
            if key in asset:
                item[key] = asset[key]
        if kind == "generated-visual":
            report_path = layout.locate(plan_path.parent, asset["publish_clean_report"])
            report = json.loads(report_path.read_text(encoding="utf-8"))
            matching = [entry for entry in report.get("results", [])
                        if entry.get("status") == "PASS" and entry.get("pixel_difference_ae") == 0
                        and not entry.get("c2pa_markers")
                        and (candidate := Path(entry["publish_copy"])).is_file()
                        and layout.sha(candidate) == item["sha256"]]
            if report.get("status") != "PASS" or not matching:
                raise ValueError("Generated image lacks a matching PASS publish-clean report: " + name)
            item["publish_clean_report"] = str(report_path)
        elif kind == "rendered-graphic":
            editable = layout.locate(plan_path.parent, asset["editable_source"])
            receipt_path = layout.locate(plan_path.parent, asset["render_receipt"])
            renderer = asset.get("renderer", "").strip()
            receipt = json.loads(receipt_path.read_text(encoding="utf-8"))
            if not editable.is_file() or not renderer or not asset.get("attribution", "").strip():
                raise ValueError("Rendered graphic needs editable source, renderer and attribution")
            if (receipt.get("source_sha256") != layout.sha(editable)
                    or receipt.get("output_sha256") != item["sha256"]
                    or receipt.get("renderer") != renderer
                    or receipt.get("image_model", "missing") is not None):
                raise ValueError("Render receipt does not bind editable source and output")
            item.update(editable_source=str(editable), source_sha256=layout.sha(editable),
                        render_receipt=str(receipt_path), renderer=renderer, image_model=None,
                        attribution=asset["attribution"], processing=asset.get("processing", []))
        else:
            original = layout.locate(plan_path.parent, asset["original_file"])
            if not original.is_file():
                raise ValueError("Missing original source asset")
            attribution = asset.get("attribution", "").strip()
            if not attribution:
                raise ValueError("Source asset needs its author/provider attribution")
            item.update(original_file=str(original), original_sha256=layout.sha(original),
                        attribution=attribution, processing=asset.get("processing", []))
            if kind == "evidence-screenshot":
                url = asset.get("source_url", "")
                if urlparse(url).scheme not in {"http", "https"} or not urlparse(url).netloc:
                    raise ValueError("Evidence screenshot needs an HTTP(S) source URL")
                if not asset.get("captured_at"):
                    raise ValueError("Evidence screenshot needs its actual capture date/time")
                item.update(source_url=url, captured_at=asset["captured_at"])
                receipt = item.get("capture_receipt", {})
                original_hash = receipt.get("original_sha256") or receipt.get("raw_sha256")
                if original_hash and original_hash != item["original_sha256"]:
                    raise ValueError("Original screenshot differs from its capture receipt: " + name)
                # Native detail montage must reproduce the source crops, not merely
                # claim provenance. This import stays out of the stdlib-only fallback.
                from compose_evidence import is_montage, validate_montage, disclosed_caption
                if is_montage(asset):
                    validate_montage(asset, file, original)
                    item['composition_disclosure'] = disclosed_caption(asset)
            else:
                item["source_description"] = asset.get("source_description", attribution)
                if asset.get("source_url"):
                    url = asset["source_url"]
                    if urlparse(url).scheme not in {"http", "https"} or not urlparse(url).netloc:
                        raise ValueError("Photo source URL must be HTTP(S)")
                    item["source_url"] = url
        if role == "body":
            prefix = asset["after_prefix"].strip()
            matches = [i for i, p in enumerate(paragraphs) if p.startswith(prefix)]
            if not prefix or len(matches) != 1:
                raise ValueError("Image anchor must match one paragraph: " + prefix)
            if matches[0] in anchors:
                raise ValueError("Layout accepts one image per paragraph; choose distinct anchors")
            anchors.add(matches[0])
            if kind == 'evidence-screenshot':
                item['evidence_context'] = {'after_paragraph': paragraphs[matches[0]],
                    'purpose': asset['purpose'], 'message': asset.get('message', ''),
                    'source_url': item['source_url']}
            placement = {"filename": name, "after_prefix": prefix,
                         "alt": asset.get("alt", ""), "frame_baked": frame}
            # Omit caption for old alt-as-caption compatibility; explicit "" suppresses it.
            if "caption" in asset:
                placement["caption"] = asset["caption"]
            if item.get('composition_disclosure'):
                placement['caption'] = item['composition_disclosure']
            if kind != "generated-visual":
                placement["source_label"] = item["attribution"]
                if "source_url" in item:
                    placement["source_url"] = item["source_url"]
            body_images.append(placement)
        else:
            if role in covers:
                raise ValueError("Duplicate cover role: " + role)
            covers[role] = name
        files.append(item)
    # Validate/decode all prepared files before writing; engine accepts these three types.
    for file in [Path(item["production_source"]) for item in files]:
        from PIL import Image
        with Image.open(file) as image:
            image.verify()
    out = out.resolve()
    if out.exists():
        raise FileExistsError("Output directory already exists: " + str(out))
    out.mkdir(parents=True)
    for item in files:
        shutil.copyfile(item["production_source"], out / item["filename"])
        if layout.sha(out / item["filename"]) != item["sha256"]:
            raise ValueError("Prepared image changed during handoff")
    manifest = {"article": str(source), "article_sha256": source_hash,
                "files": files, "handoff_schema": "pinshu.article-assets/1"}
    handoff = {"source_md": str(source), "image_manifest": "配图清单.json",
               "body_images": body_images, **covers,
               "article_state": plan.get("article_state", "未提供；不得推断已定稿")}
    for key in ("title", "author", "digest", "emphasis", "lead_image"):
        if key in plan:
            handoff[key] = plan[key]
    for name, data in (("配图清单.json", manifest), ("排版交接.json", handoff)):
        (out / name).write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    if layout.sha(source) != source_hash:
        raise ValueError("Article changed during handoff; discard this candidate")
    return out / "排版交接.json"


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="复用排版实际解析器生成配图清单和排版交接")
    parser.add_argument("--plan", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--capture-requests-only", action="store_true",
                        help="仅导出待截图清单；无需浏览器、Pillow或排版依赖，不生成发布交接")
    parser.add_argument("--layout-skill", type=Path,
                        default=Path(__file__).resolve().parents[2] / "pinshu-wechat-layout")
    args = parser.parse_args()
    print(export_capture_requests(args.plan, args.output_dir) if args.capture_requests_only
          else prepare(args.plan, args.output_dir, args.layout_skill))
