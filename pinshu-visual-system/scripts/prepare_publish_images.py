#!/usr/bin/env python3
"""Create metadata-clean, pixel-identical PNG copies for publishing."""

from __future__ import annotations

import argparse
from decimal import Decimal, InvalidOperation
import json
import shutil
import struct
import subprocess
import sys
from pathlib import Path
import zlib


BLOCKED_MARKERS = (
    b"c2pa",
    b"jumb",
    b"caBX",
    b"trainedAlgorithmicMedia",
    b"Content Credentials",
)


class PublishPrepError(RuntimeError):
    pass


def is_zero_pixel_difference(metric: str) -> bool:
    try:
        value = Decimal(metric.split()[0])
        return value.is_finite() and value == 0
    except (InvalidOperation, IndexError):
        return False


def run(command: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        command,
        check=False,
        capture_output=True,
        text=True,
    )


def require_magick() -> str:
    executable = shutil.which("magick")
    if executable is None:
        raise PublishPrepError("ImageMagick `magick` is required but was not found.")
    return executable


def identify(magick: str, image: Path, format_string: str) -> str:
    result = run([magick, "identify", "-format", format_string, str(image)])
    if result.returncode != 0:
        raise PublishPrepError(
            f"Cannot inspect {image}: {(result.stderr or result.stdout).strip()}"
        )
    return result.stdout.strip()


def png_chunks(data: bytes) -> list[tuple[bytes, bytes]]:
    if not data.startswith(b"\x89PNG\r\n\x1a\n"):
        raise PublishPrepError("Publish copy is not a valid PNG.")

    chunks = []
    offset = 8
    while offset + 12 <= len(data):
        length = struct.unpack(">I", data[offset : offset + 4])[0]
        chunk_type = data[offset + 4 : offset + 8]
        end = offset + 12 + length
        if end > len(data):
            raise PublishPrepError("Truncated PNG chunk")
        payload = data[offset + 8:offset + 8 + length]
        crc = struct.unpack(">I", data[offset + 8 + length:end])[0]
        if zlib.crc32(chunk_type + payload) & 0xffffffff != crc:
            raise PublishPrepError("PNG chunk checksum mismatch")
        chunks.append((chunk_type, payload))
        offset += 12 + length
        if chunk_type == b"IEND":
            if length or offset != len(data):
                raise PublishPrepError("Invalid PNG ending")
            break
    if not chunks or chunks[0][0] != b"IHDR" or len(chunks[0][1]) != 13 or chunks[-1][0] != b"IEND":
        raise PublishPrepError("Incomplete PNG structure")
    return chunks


def png_chunk_types(data: bytes) -> list[bytes]:
    return [kind for kind, _ in png_chunks(data)]


def residual_provenance(data: bytes) -> list[str]:
    found: list[str] = []
    for kind, payload in png_chunks(data):
        if kind == b"caBX":
            found.append("caBX")
        if kind not in {b"tEXt", b"iTXt", b"zTXt", b"eXIf", b"caBX"}:
            continue
        if kind == b"zTXt":
            keyword, separator, rest = payload.partition(b"\0")
            if not separator or not rest or rest[0] != 0:
                raise PublishPrepError("Invalid compressed PNG metadata")
            payload = keyword + b"\0" + metadata_text(rest[1:])
        elif kind == b"iTXt":
            keyword, separator, rest = payload.partition(b"\0")
            if not separator or len(rest) < 2:
                raise PublishPrepError("Invalid PNG international text metadata")
            flag, method = rest[:2]
            fields = rest[2:].split(b"\0", 2)
            if len(fields) != 3:
                raise PublishPrepError("Invalid PNG international text metadata")
            language, translated_keyword, text = fields
            if flag not in {0, 1} or method != 0:
                raise PublishPrepError("Invalid PNG text compression")
            payload = keyword + b"\0" + language + b"\0" + translated_keyword + b"\0" + (metadata_text(text) if flag else text)
        for marker in BLOCKED_MARKERS:
            if marker.lower() in payload.lower():
                found.append(marker.decode("ascii"))
    return sorted(set(found))


def metadata_text(data: bytes) -> bytes:
    """Decode only bounded metadata, with actionable diagnostics on malformed input."""
    decoder = zlib.decompressobj()
    try:
        decoded = decoder.decompress(data, 2 * 1024 * 1024 + 1)
    except zlib.error as exc:
        raise PublishPrepError("Invalid compressed PNG metadata") from exc
    if len(decoded) > 2 * 1024 * 1024 or decoder.unconsumed_tail:
        raise PublishPrepError("Compressed PNG metadata exceeds the inspection limit")
    if not decoder.eof or decoder.unused_data:
        raise PublishPrepError("Incomplete compressed PNG metadata")
    return decoded


def pixel_difference(magick: str, source: Path, publish_copy: Path) -> str:
    result = run(
        [
            magick,
            "compare",
            "-metric",
            "AE",
            str(source),
            str(publish_copy),
            "null:",
        ]
    )
    metric = (result.stderr or result.stdout).strip()
    if result.returncode not in (0, 1):
        raise PublishPrepError(f"Pixel comparison failed: {metric}")
    return metric


def prepare_one(magick: str, source: Path, output_dir: Path) -> dict[str, object]:
    if not source.is_file():
        raise PublishPrepError(f"Input does not exist: {source}")

    frame_count = int(identify(magick, source, "%n").splitlines()[0])
    if frame_count != 1:
        raise PublishPrepError(
            f"Animated or multi-frame input is not supported: {source} ({frame_count} frames)"
        )

    output = output_dir / f"{source.stem}-publish-clean.png"
    if output.exists():
        raise PublishPrepError(
            f"Refusing to overwrite existing publish copy: {output}"
        )

    source_geometry = identify(magick, source, "%wx%h")
    conversion = run([magick, str(source), "-strip", str(output)])
    if conversion.returncode != 0:
        raise PublishPrepError(
            f"ImageMagick failed for {source}: "
            f"{(conversion.stderr or conversion.stdout).strip()}"
        )

    try:
        publish_geometry = identify(magick, output, "%wx%h")
        if publish_geometry != source_geometry:
            raise PublishPrepError(
                f"Geometry changed: {source_geometry} -> {publish_geometry}"
            )

        metric = pixel_difference(magick, source, output)
        if not is_zero_pixel_difference(metric):
            raise PublishPrepError(f"Pixel data changed; AE metric is {metric}")

        residual = residual_provenance(output.read_bytes())
        if residual:
            raise PublishPrepError(
                "Residual provenance markers remain: " + ", ".join(residual)
            )
    except Exception:
        output.unlink(missing_ok=True)
        raise

    return {
        "source": str(source.resolve()),
        "publish_copy": str(output.resolve()),
        "geometry": source_geometry,
        "pixel_difference_ae": 0,
        "c2pa_markers": [],
        "status": "PASS",
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Preserve source images and create verified metadata-clean PNG copies "
            "for platform publishing."
        )
    )
    parser.add_argument(
        "--output-dir",
        required=True,
        type=Path,
        help="Directory for *-publish-clean.png copies and the JSON report.",
    )
    parser.add_argument(
        "images",
        nargs="+",
        type=Path,
        help="One or more system-produced raster images.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    args.output_dir.mkdir(parents=True, exist_ok=True)
    report_path = args.output_dir / "publish-clean-report.json"
    targets = [
        args.output_dir / f"{image.stem}-publish-clean.png" for image in args.images
    ]

    try:
        if len(set(targets)) != len(targets):
            raise PublishPrepError(
                "Two inputs resolve to the same publish-copy filename."
            )
        existing = [path for path in [*targets, report_path] if path.exists()]
        if existing:
            raise PublishPrepError(
                "Refusing to overwrite existing output: "
                + ", ".join(str(path) for path in existing)
            )

        magick = require_magick()
        results: list[dict[str, object]] = []
        produced: list[Path] = []
        for image in args.images:
            item = prepare_one(magick, image, args.output_dir)
            results.append(item)
            produced.append(Path(str(item["publish_copy"])))
    except (PublishPrepError, ValueError) as exc:
        for path in locals().get("produced", []):
            path.unlink(missing_ok=True)
        print(f"FAIL: {exc}", file=sys.stderr)
        return 1

    report_path.write_text(
        json.dumps(
            {
                "status": "PASS",
                "policy": "preserve-original-and-publish-clean-copy",
                "results": results,
            },
            ensure_ascii=False,
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )

    for item in results:
        print(f"PASS: {item['publish_copy']}")
    print(f"REPORT: {report_path.resolve()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
