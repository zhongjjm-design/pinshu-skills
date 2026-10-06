#!/usr/bin/env python3
"""Render a native SVG/PPTX into a final-platform PNG with a reproducible receipt."""
from __future__ import annotations

import argparse
from decimal import Decimal, InvalidOperation
import hashlib
import json
import math
from pathlib import Path
import posixpath
import re
import shutil
import subprocess
import tempfile
import xml.etree.ElementTree as ET
import zipfile
from svg_label_checks import check_svg_labels, normalize_font_units

from export_platform_image import convert_exact, load_profile, ExportError
from prepare_publish_images import pixel_difference, is_zero_pixel_difference


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def command(args: list[str]) -> str:
    result = subprocess.run(args, capture_output=True, text=True, timeout=120)
    if result.returncode:
        raise ValueError("Render command failed: " + (result.stderr or result.stdout).strip())
    return (result.stdout + result.stderr).strip()


def executable(name: str) -> str:
    path = shutil.which(name)
    if not path:
        raise ValueError("Rendering requires " + name + "; install the documented dependency and retry, without substituting a background")
    return path


def native_inventory(source: Path, slide: int = 1) -> dict:
    """Read complete native text segments and category/value pairs on the selected slide."""
    texts, points, formatted_points = [], [], []
    if source.suffix.lower() == ".svg":
        document = ET.fromstring(source.read_bytes())
        def inspect(element, inherited):
            tag = element.tag.rsplit("}", 1)[-1]
            if tag in {"script", "foreignObject", "style"}:
                raise ValueError("Use native SVG text, presentation attributes and self-contained graphics; scripts, CSS style blocks and foreignObject are unsupported")
            own = dict(element.attrib)
            own.update(dict(part.split(":", 1) for part in element.get("style", "").split(";") if ":" in part))
            own = {k.strip(): v.strip() for k, v in own.items()}
            attrs = dict(inherited)
            attrs.update(own)
            for key, value in element.attrib.items():
                if key.rsplit("}", 1)[-1] == "href" and value and not value.startswith(("data:", "#")):
                    raise ValueError("Embed SVG assets instead of using external or local files")
            blocked = inherited.get("_hidden") == "yes" or attrs.get("display") == "none" or element.get("opacity", attrs.get("opacity", "1")) in {"0", "0.0", "0%"}
            attrs["_hidden"] = "yes" if blocked else "no"
            hidden = blocked or attrs.get("visibility") in {"hidden", "collapse"} or attrs.get("fill-opacity") in {"0", "0.0", "0%"}
            hidden |= attrs.get("fill", "black").lower() in {"none", "transparent"} and attrs.get("stroke", "none").lower() == "none"
            def opacity_number(value):
                result = float(value.rstrip("%")) / (100 if value.endswith("%") else 1)
                if not math.isfinite(result) or not 0 <= result <= 1:
                    raise ValueError("SVG opacity must be a finite number from zero to one")
                return result
            effective = float(inherited.get("_effective_opacity", "1")) * opacity_number(own.get("opacity", "1"))
            attrs["_effective_opacity"] = str(effective)
            if tag in {"text", "tspan"} and "".join(element.itertext()).strip():
                try:
                    fill_opacity = opacity_number(attrs.get("fill-opacity", "1"))
                    size_value = attrs.get("font-size", "12").strip()
                    size_match = re.fullmatch(r"([+]?(?:\d+(?:\.\d*)?|\.\d+))(?:px|pt|pc|in|cm|mm|Q)?", size_value)
                    if not size_match:
                        raise ValueError("Unsupported font-size; use an absolute SVG unit")
                    size = float(size_match[1])
                except ValueError:
                    raise ValueError("SVG native text requires numeric opacity and absolute numeric SVG font sizes") from None
                if not hidden and (effective * fill_opacity < .1 or not math.isfinite(size) or size <= 0):
                    raise ValueError("SVG native text opacity is below 0.1 or font size is not positive; use readable labels")
            if tag in {"text", "tspan"} and hidden and "".join(element.itertext()).strip():
                raise ValueError("Native labels must be visible; hidden or transparent SVG text is not delivered text")
            if tag == "text":
                texts.append("".join(element.itertext()))
            for child in element:
                inspect(child, attrs)
        inspect(document, {})
    elif source.suffix.lower() == ".pptx":
        if slide < 1:
            raise ValueError("slide must be a positive one-based index")
        with zipfile.ZipFile(source) as deck:
            ns = {"a": "http://schemas.openxmlformats.org/drawingml/2006/main",
                  "c": "http://schemas.openxmlformats.org/drawingml/2006/chart",
                  "r": "http://schemas.openxmlformats.org/officeDocument/2006/relationships"}
            name = f"ppt/slides/slide{slide}.xml"
            if "ppt/presentation.xml" in deck.namelist():
                presentation = ET.fromstring(deck.read("ppt/presentation.xml"))
                order = presentation.findall(".//{http://schemas.openxmlformats.org/presentationml/2006/main}sldId")
                if slide > len(order):
                    raise ValueError("Selected PPTX slide does not exist")
                relid = order[slide - 1].get("{" + ns["r"] + "}id")
                presentation_rels = ET.fromstring(deck.read("ppt/_rels/presentation.xml.rels"))
                target = next((r.get("Target") for r in presentation_rels if r.get("Id") == relid), None)
                if not target:
                    raise ValueError("Selected PPTX slide has no presentation relationship")
                name = target.lstrip("/") if target.startswith("/") else posixpath.normpath("ppt/" + target)
            if name not in deck.namelist():
                raise ValueError("Selected PPTX slide does not exist")
            doc = ET.fromstring(deck.read(name))
            texts.extend("".join(e.itertext()).strip() for p in doc.findall(".//a:p", ns)
                         for e in [p] if p.findall(".//a:t", ns))
            # Paragraph itertext contains only XML text nodes, not geometry attributes.
            relname = posixpath.dirname(name) + "/_rels/" + posixpath.basename(name) + ".rels"
            rels = {}
            if relname in deck.namelist():
                for rel in ET.fromstring(deck.read(relname)):
                    if rel.get("TargetMode") == "External":
                        raise ValueError("Embed PPTX assets; external relationships are unsupported")
                    target = rel.get("Target", "")
                    rels[rel.get("Id")] = target.lstrip("/") if target.startswith("/") else posixpath.normpath(posixpath.dirname(name) + "/" + target)
            for chart in doc.findall(".//c:chart", ns):
                target = rels.get(chart.get("{" + ns["r"] + "}id"))
                if not target or target not in deck.namelist():
                    raise ValueError("PPTX chart needs a valid slide relationship and cached category/value data")
                chart_doc = ET.fromstring(deck.read(target))
                for series in chart_doc.findall(".//c:ser", ns):
                    categories = {p.get("idx"): p.findtext("c:v", namespaces=ns) for p in series.findall(".//c:cat//c:pt", ns)}
                    values = {p.get("idx"): p.findtext("c:v", namespaces=ns) for p in series.findall(".//c:val//c:pt", ns)}
                    parent = next(node for node in chart_doc.iter() if series in list(node))
                    cache_format = series.findtext(".//c:val//c:formatCode", default="General", namespaces=ns)
                    labels = series.find("c:dLbls", ns)
                    if labels is None:
                        labels = parent.find("c:dLbls", ns)
                    if labels is not None and labels.findall("c:dLbl/c:numFmt", ns):
                        raise ValueError("Per-point chart number formats are unsupported; use one series/plot format and review again")
                    fmt = labels.find("c:numFmt", ns) if labels is not None else None
                    # Unlinked data-label formatting overrides the cached number format.
                    display_format = fmt.get("formatCode", cache_format) if fmt is not None and fmt.get("sourceLinked", "0") != "1" else cache_format
                    if "%" in display_format and any(marker in display_format for marker in (";", "[")):
                        raise ValueError("Conditional percentage formats are unsupported; use a simple percent format")
                    # Quoted/escaped percent signs are literal suffixes, not x100 formats.
                    percent_format = "%" in re.sub(r'"[^"\n]*"|\\.', "", display_format)
                    for idx in sorted(set(categories) & set(values)):
                        try:
                            value = Decimal(values[idx])
                        except (InvalidOperation, TypeError):
                            raise ValueError("PPTX chart cache contains an invalid value") from None
                        if not value.is_finite():
                            raise ValueError("PPTX chart cache values must be finite")
                        points.append((categories[idx], value))
                        if percent_format:
                            formatted_points.append((categories[idx], value * 100, "%"))
                    texts.extend(v for v in categories.values() if v is not None)
                    texts.extend(series.findtext(".//c:tx//c:v", default="", namespaces=ns).splitlines())
    else:
        raise ValueError("Use a native SVG or PPTX editable source")
    return {"texts": [t.strip() for t in texts if t.strip()], "chart_points": points, "formatted_chart_points": formatted_points}


def renderer_versions(suffix: str) -> dict:
    versions = {"imagemagick": command([executable("magick"), "-version"]).splitlines()[0]}
    if suffix == ".pptx":
        versions["libreoffice"] = command([executable("soffice"), "--version"])
        versions["poppler"] = command([executable("pdftoppm"), "-v"]).splitlines()[0]
    return versions


def render(source: Path, font: Path, platform: str, output: Path, *, slide: int = 1,
           fit: str = "contain", gravity: str = "center", background: str = "#fafaf8") -> dict:
    source, font = source.resolve(), font.resolve()
    if not font.is_file():
        raise ValueError("font-file must name a readable installed font; fonts are not bundled")
    inventory = native_inventory(source, slide)
    versions = renderer_versions(source.suffix.lower())
    profile = load_profile(platform)
    width, height = (int(profile["publish_size"][k]) for k in ("width", "height"))
    magick = executable("magick")
    mapping = {}
    visibility = {}
    with tempfile.TemporaryDirectory(prefix="pinshu-native-render-") as scratch:
        work = Path(scratch)
        raw = work / "native.png"
        if source.suffix.lower() == ".svg":
            # MSVG avoids implicit switching between Inkscape, librsvg and the internal renderer.
            raster_source = normalize_font_units(source, work / "font-units.svg")
            command([magick, "-background", background, "-font", str(font), "MSVG:" + str(raster_source), str(raw)])
            visibility = check_svg_labels(raster_source, font, raw, work, magick, background, width, height, fit)
        else:
            local = work / "native.pptx"
            shutil.copyfile(source, local)
            with zipfile.ZipFile(source) as deck:
                pres = ET.fromstring(deck.read("ppt/presentation.xml"))
                count = len(pres.findall(".//{http://schemas.openxmlformats.org/presentationml/2006/main}sldId"))
            pdf_filter = 'pdf:impress_pdf_Export:{"ExportHiddenSlides":{"type":"boolean","value":"true"}}'
            command([executable("soffice"), "-env:UserInstallation=" + (work / "lo-profile").as_uri(),
                     "--headless", "--convert-to", pdf_filter, "--outdir", str(work), str(local)])
            pdf = work / "native.pdf"
            if not pdf.is_file():
                raise ValueError("LibreOffice did not produce a PDF; use a valid self-contained PPTX")
            info = command([executable("pdfinfo"), str(pdf)])
            page_count = re.search(r"^Pages:\s+(\d+)", info, re.M)
            if not page_count or int(page_count[1]) != count:
                raise ValueError("PDF page count differs from PPTX slide count; no safe slide mapping")
            mapping = {"slide_count": count, "pdf_page_count": int(page_count[1]),
                       "pdf_page": slide, "export_hidden_slides": True, "scaling": "preserve-aspect"}
            command([executable("pdftoppm"), "-f", str(slide), "-l", str(slide), "-singlefile", "-scale-to-x", str(width),
                     "-scale-to-y", "-1", "-png", str(pdf), str(work / "native")])
        convert_exact(magick, raw, output, width, height, gravity, fit, background)
    return {"schema": "native-render-v2", "status": "PASS", "source_sha256": sha(source),
            "source_format": source.suffix.lower(), "font_file": str(font), "font_sha256": sha(font),
            "renderer_versions": versions, "platform": platform, "slide": slide, "fit": fit,
            "gravity": gravity, "background": background, "final_png_sha256": sha(output),
            "native_text": inventory["texts"], "slide_mapping": mapping, "svg_label_checks": visibility, "scope": "reproducible rendering, not semantic or aesthetic approval"}


def verify_render(source: Path, reviewed_png: Path, receipt: dict, platform: str) -> dict:
    if receipt.get("schema") != "native-render-v2" or receipt.get("status") != "PASS":
        raise ValueError("Supply a successful render_editable.py receipt")
    if receipt.get("source_sha256") != sha(source) or receipt.get("final_png_sha256") != sha(reviewed_png) or receipt.get("platform") != platform:
        raise ValueError("Render receipt does not match the editable source, final image and platform")
    font = Path(receipt["font_file"])
    if not font.is_file() or sha(font) != receipt.get("font_sha256"):
        raise ValueError("Rendering font is missing or changed; render and review again")
    if renderer_versions(source.suffix.lower()) != receipt.get("renderer_versions"):
        raise ValueError("Renderer versions changed; render and review again")
    with tempfile.TemporaryDirectory(prefix="pinshu-render-check-") as scratch:
        output = Path(scratch) / "rerender.png"
        fresh = render(source, font, platform, output, slide=receipt["slide"], fit=receipt["fit"],
               gravity=receipt["gravity"], background=receipt["background"])
        if fresh["slide_mapping"] != receipt.get("slide_mapping"):
            raise ValueError("Render receipt has an incorrect slide mapping; render and review again")
        if not is_zero_pixel_difference(pixel_difference(executable("magick"), reviewed_png, output)):
            raise ValueError("Editable source re-render differs from the reviewed image; render and review the current source")
    return {"re_render_pixel_difference_ae": 0, "renderer_versions": receipt["renderer_versions"],
            "font_sha256": receipt["font_sha256"]}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", required=True, type=Path)
    parser.add_argument("--font-file", required=True, type=Path)
    parser.add_argument("--platform", required=True)
    parser.add_argument("--output-dir", required=True, type=Path)
    parser.add_argument("--slide", type=int, default=1)
    parser.add_argument("--fit", choices=["contain", "cover"], default="contain")
    parser.add_argument("--gravity", choices=["center", "north", "south", "east", "west", "northeast", "northwest", "southeast", "southwest"], default="center")
    parser.add_argument("--background", default="#fafaf8")
    args = parser.parse_args()
    created = False
    try:
        args.output_dir.mkdir(parents=True, exist_ok=False)
        created = True
        receipt = render(args.source, args.font_file, args.platform, args.output_dir / "platform-final.png",
                         slide=args.slide, fit=args.fit, gravity=args.gravity, background=args.background)
        (args.output_dir / "render-receipt.json").write_text(json.dumps(receipt, indent=2) + "\n")
    except (OSError, ValueError, KeyError, ExportError, ET.ParseError, zipfile.BadZipFile, subprocess.TimeoutExpired) as exc:
        if created and not (args.output_dir / "render-receipt.json").exists():
            (args.output_dir / "render-failure.json").write_text(json.dumps({"status": "FAIL", "deliverable": False, "error": str(exc)}, indent=2) + "\n")
        parser.exit(1, "HARD_STOP: " + str(exc) + "\n")
    print("RENDER PASS: inspect platform-final.png and its thumbnail before QA")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
