"""Bounded SVG text checks using the same MSVG renderer and font as delivery."""
from __future__ import annotations
import copy
from pathlib import Path
import re
import subprocess
import xml.etree.ElementTree as ET
from prepare_publish_images import pixel_difference, is_zero_pixel_difference


def run(args):
    result = subprocess.run(args, capture_output=True, text=True, timeout=120)
    if result.returncode:
        raise ValueError("SVG label check failed: " + result.stderr.strip())
    return result.stdout.strip()


def normalize_font_units(source: Path, output: Path) -> Path:
    """MSVG does not consistently convert pt fonts; normalize absolute font units explicitly."""
    factors = {"px": 1, "pt": 96 / 72, "pc": 16, "in": 96, "cm": 96 / 2.54, "mm": 96 / 25.4, "Q": 96 / 101.6}
    document = ET.fromstring(source.read_bytes())
    changed = False
    def convert(value):
        nonlocal changed
        match = re.fullmatch(r"([+]?(?:\d+(?:\.\d*)?|\.\d+))(px|pt|pc|in|cm|mm|Q)", value.strip())
        if not match or match[2] == "px":
            return value
        changed = True
        return format(float(match[1]) * factors[match[2]], ".12g") + "px"
    for node in document.iter():
        if "font-size" in node.attrib:
            node.set("font-size", convert(node.get("font-size")))
        if node.get("style"):
            parts = []
            for part in node.get("style").split(";"):
                if ":" in part:
                    key, value = part.split(":", 1)
                    if key.strip() == "font-size":
                        part = key + ":" + convert(value)
                parts.append(part)
            node.set("style", ";".join(parts))
    if not changed:
        return source
    ET.register_namespace("", "http://www.w3.org/2000/svg")
    ET.ElementTree(document).write(output, encoding="utf-8", xml_declaration=True)
    return output


def check_svg_labels(source: Path, font: Path, raw: Path, work: Path, magick: str, background: str, final_width: int, final_height: int, fit: str) -> dict:
    ET.register_namespace("", "http://www.w3.org/2000/svg")
    doc = ET.fromstring(source.read_bytes())
    labels = [e for e in doc.iter() if e.tag.rsplit("}", 1)[-1] == "text" and "".join(e.itertext()).strip()]
    if not labels:
        return {"checked_labels": 0, "scope": "native text geometry and nonzero rendered contribution"}
    def number(value):
        if not re.fullmatch(r"[+-]?(?:\d+(?:\.\d*)?|\.\d+)(?:px)?", value):
            raise ValueError("SVG text checks require numeric/px canvas dimensions or an explicit numeric viewBox")
        return float(value.removesuffix("px"))
    if doc.get("viewBox"):
        x0, y0, width, height = map(float, re.split(r"[ ,]+", doc.get("viewBox").strip()))
    else:
        x0, y0, width, height = 0, 0, number(doc.get("width", "")), number(doc.get("height", ""))
    if not (0 < width <= 10000 and 0 < height <= 10000):
        raise ValueError("SVG label checking supports canvases up to 10000 units per side")
    raw_width, raw_height = map(int, run([magick, str(raw), "-format", "%w %h", "info:"]).split())
    viewport_scale = max if "slice" in doc.get("preserveAspectRatio", "") else min
    vertical_scale = raw_height / height if doc.get("preserveAspectRatio") == "none" else viewport_scale(raw_width / width, raw_height / height)
    final_scale = (min if fit == "contain" else max)(final_width / raw_width, final_height / raw_height)
    glyph_to_final = vertical_scale * final_scale
    pad = max(width, height) / 2
    if (width + pad*2) * (height + pad*2) > 30_000_000:
        raise ValueError("SVG text checking canvas exceeds 30 million pixels; use a smaller native canvas")
    for index, label in enumerate(labels):
        text = "".join(label.itertext()).strip()
        # A label must change actual delivered pixels, including its background contrast.
        knockout = copy.deepcopy(doc)
        target = [e for e in knockout.iter() if e.tag.rsplit("}", 1)[-1] == "text" and "".join(e.itertext()).strip()][index]
        next(parent for parent in knockout.iter() if target in list(parent)).remove(target)
        kp, ki = work / "knockout.svg", work / "knockout.png"
        ET.ElementTree(knockout).write(kp, encoding="utf-8", xml_declaration=True)
        run([magick, "-background", background, "-font", str(font), "MSVG:" + str(kp), str(ki)])
        if is_zero_pixel_difference(pixel_difference(magick, raw, ki)):
            raise ValueError("SVG label has no visible pixel contribution: " + text)
        # Isolate this label on a padded canvas. Keep ancestors/transforms and defs.
        mask = copy.deepcopy(doc)
        selected = [e for e in mask.iter() if e.tag.rsplit("}", 1)[-1] == "text" and "".join(e.itertext()).strip()][index]
        keep = set(selected.iter())
        def prune(node):
            if node in keep or node.tag.rsplit("}", 1)[-1] == "defs":
                return True
            for child in list(node):
                if not prune(child):
                    node.remove(child)
            return len(node) > 0
        prune(mask)
        for node in mask.iter():
            if node.tag.rsplit("}", 1)[-1] in {"text", "tspan"}:
                node.set("fill", "black"); node.set("fill-opacity", "1"); node.set("stroke", "none")
                node.set("style", node.get("style", "") + ";fill:black;fill-opacity:1;stroke:none")
        ns = "{http://www.w3.org/2000/svg}"
        group = ET.Element(ns + "g", {"transform": f"translate({pad-x0},{pad-y0})"})
        for child in list(mask):
            mask.remove(child); group.append(child)
        mask.append(group)
        mask.set("width", str(width + pad * 2)); mask.set("height", str(height + pad * 2))
        mask.set("viewBox", f"0 0 {width + pad*2} {height + pad*2}")
        mp, mi = work / "label-mask.svg", work / "label-mask.png"
        ET.ElementTree(mask).write(mp, encoding="utf-8", xml_declaration=True)
        run([magick, "-background", "white", "-font", str(font), "MSVG:" + str(mp), str(mi)])
        bbox = run([magick, str(mi), "-background", "white", "-alpha", "remove", "-negate", "-threshold", "0", "-trim", "-format", "%wx%h%O", "info:"])
        match = re.fullmatch(r"(\d+)x(\d+)([+-]\d+)([+-]\d+)", bbox)
        if not match:
            raise ValueError("Cannot measure SVG label bounds: " + text)
        w, h, x, y = map(int, match.groups())
        if h * glyph_to_final < 8:
            raise ValueError("SVG rendered label height is below 8 final-platform pixels; enlarge text or adjust the viewBox/transform: " + text)
        if w <= 1 or h <= 1 or x < pad-2 or y < pad-2 or x+w > pad+width+2 or y+h > pad+height+2:
            raise ValueError("SVG label is outside or clipped by the canvas; reposition/wrap it: " + text)
    return {"checked_labels": len(labels), "scope": "final-pixel minimum height, rendered glyph bounds and nonzero pixel contribution; human legibility and meaning still require review"}
