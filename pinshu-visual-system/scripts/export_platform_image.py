#!/usr/bin/env python3
"""Create exact-size platform exports while preserving the generated original."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import shutil
import subprocess
import sys


SKILL_ROOT = Path(__file__).resolve().parent.parent
PLATFORM_PROFILES = SKILL_ROOT / "references" / "platform-profiles.json"


class ExportError(RuntimeError):
    pass


def run(command: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        command,
        check=False,
        capture_output=True,
        text=True,
    )


def identify(magick: str, image: Path) -> str:
    result = run([magick, "identify", "-format", "%wx%h", str(image)])
    if result.returncode != 0:
        raise ExportError(
            f"Cannot inspect {image}: {(result.stderr or result.stdout).strip()}"
        )
    return result.stdout.strip()


def convert_exact(
    magick: str,
    source: Path,
    output: Path,
    width: int,
    height: int,
    gravity: str,
    fit: str,
    background: str,
) -> None:
    resize_geometry = (
        f"{width}x{height}^"
        if fit == "cover"
        else f"{width}x{height}"
    )
    command = [
        magick,
        str(source),
        "-auto-orient",
        "-gravity",
        gravity,
        "-resize",
        resize_geometry,
    ]
    if fit == "contain":
        command.extend(["-background", background])
    command.extend(["-extent", f"{width}x{height}", str(output)])
    result = run(command)
    if result.returncode != 0:
        raise ExportError(
            f"ImageMagick export failed: "
            f"{(result.stderr or result.stdout).strip()}"
        )


def load_profile(platform: str) -> dict:
    config = json.loads(PLATFORM_PROFILES.read_text(encoding="utf-8"))
    profiles = {item["id"]: item for item in config["profiles"]}
    if platform not in profiles:
        raise ExportError(f"Unknown platform profile: {platform}")
    return profiles[platform]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", required=True, type=Path)
    parser.add_argument("--platform", required=True)
    parser.add_argument("--output-dir", required=True, type=Path)
    parser.add_argument(
        "--gravity",
        default="center",
        choices=[
            "center",
            "north",
            "south",
            "east",
            "west",
            "northeast",
            "northwest",
            "southeast",
            "southwest",
        ],
    )
    parser.add_argument(
        "--fit",
        default="contain",
        choices=["cover", "contain"],
        help="cover crops expendable edges; contain preserves all information and pads.",
    )
    parser.add_argument(
        "--background",
        default="#fafaf8",
        help="Padding color used only with --fit contain.",
    )
    args = parser.parse_args()

    try:
        if not args.source.is_file():
            raise ExportError(f"Source does not exist: {args.source}")
        magick = shutil.which("magick")
        if magick is None:
            raise ExportError("ImageMagick `magick` is required but was not found.")
        profile = load_profile(args.platform)
        width = int(profile["publish_size"]["width"])
        height = int(profile["publish_size"]["height"])
        args.output_dir.mkdir(parents=True, exist_ok=True)
        output = args.output_dir / "platform-export.png"
        report_path = args.output_dir / "platform-export-report.json"
        preview_paths = [
            args.output_dir / "preview-center-383.png",
            args.output_dir / "preview-thumbnail-180.png",
        ]
        existing = [
            path
            for path in [output, report_path, *preview_paths]
            if path.exists()
        ]
        if existing:
            raise ExportError(
                "Refusing to overwrite existing output: "
                + ", ".join(str(path) for path in existing)
            )

        source_geometry = identify(magick, args.source)
        oriented = run([magick, str(args.source), "-auto-orient", "-format", "%wx%h", "info:"])
        if oriented.returncode:
            raise ExportError("Cannot inspect oriented source geometry")
        source_width, source_height = map(int, oriented.stdout.strip().split("x"))
        scale = max(width / source_width, height / source_height) if args.fit == "cover" else min(width / source_width, height / source_height)
        loss_x = max(0.0, 1 - width / (source_width * scale))
        loss_y = max(0.0, 1 - height / (source_height * scale))
        gx = 0 if "west" in args.gravity else 1 if "east" in args.gravity else .5
        gy = 0 if "north" in args.gravity else 1 if "south" in args.gravity else .5
        convert_exact(
            magick,
            args.source,
            output,
            width,
            height,
            args.gravity,
            args.fit,
            args.background,
        )
        output_geometry = identify(magick, output)
        expected_geometry = f"{width}x{height}"
        if output_geometry != expected_geometry:
            output.unlink(missing_ok=True)
            raise ExportError(
                f"Geometry mismatch: {output_geometry}, expected {expected_geometry}"
            )

        previews: list[dict] = []
        if args.platform == "wechat-cover-primary":
            safe = profile["critical_safe_area"]
            center_preview = args.output_dir / "preview-center-383.png"
            result = run(
                [
                    magick,
                    str(output),
                    "-crop",
                    f"{safe['width']}x{safe['height']}+{safe['x']}+{safe['y']}",
                    "+repage",
                    str(center_preview),
                ]
            )
            if result.returncode != 0:
                raise ExportError(
                    "Center preview failed: "
                    + (result.stderr or result.stdout).strip()
                )
            previews.append(
                {
                    "type": "center-crop",
                    "path": str(center_preview.resolve()),
                    "geometry": identify(magick, center_preview),
                }
            )

        thumbnail = args.output_dir / "preview-thumbnail-180.png"
        result = run(
            [
                magick,
                str(output),
                "-resize",
                "180x",
                str(thumbnail),
            ]
        )
        if result.returncode != 0:
            raise ExportError(
                "Thumbnail preview failed: "
                + (result.stderr or result.stdout).strip()
            )
        previews.append(
            {
                "type": "thumbnail",
                "path": str(thumbnail.resolve()),
                "geometry": identify(magick, thumbnail),
            }
        )

        report = {
            "status": "PASS",
            "policy": "preserve-generated-original-then-exact-platform-export",
            "source": str(args.source.resolve()),
            "source_geometry": source_geometry,
            "oriented_source_geometry": oriented.stdout.strip(),
            "crop_fraction": {"left": loss_x * gx, "right": loss_x * (1 - gx),
                              "top": loss_y * gy, "bottom": loss_y * (1 - gy)},
            "content_preserved": loss_x == 0 and loss_y == 0,
            "semantic_review": "pending; inspect this export and thumbnail before delivery QA",
            "platform": args.platform,
            "profile_version": json.loads(
                PLATFORM_PROFILES.read_text(encoding="utf-8")
            )["version"],
            "transform": profile["transform"],
            "gravity": args.gravity,
            "fit": args.fit,
            "background": args.background if args.fit == "contain" else None,
            "output": str(output.resolve()),
            "output_geometry": output_geometry,
            "previews": previews,
        }
        report_path.write_text(
            json.dumps(report, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
    except (ExportError, OSError, ValueError, KeyError, json.JSONDecodeError) as exc:
        print(f"FAIL: {exc}", file=sys.stderr)
        return 1

    print(f"PASS: {output.resolve()}")
    print(f"REPORT: {report_path.resolve()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
