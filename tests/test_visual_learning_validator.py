#!/usr/bin/env python3
"""Positive controls for the public visual-learning mechanical validator."""
from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
VALIDATOR = ROOT / "pinshu-visual-learning" / "scripts" / "validate_visual_learning.py"


class VisualLearningValidatorPositiveFixture(unittest.TestCase):
    def test_formal_fixture_passes_with_relative_sources_and_mobile_width(self) -> None:
        with tempfile.TemporaryDirectory(prefix="pinshu-visual-learning-") as tmp:
            root = Path(tmp)
            (root / "source.md").write_text("# Source\n\nEvidence sentence.\n", encoding="utf-8")
            (root / "diagram.png").write_bytes(b"\x89PNG\r\n\x1a\n" + b"fixture")
            (root / "diagram.svg").write_text(
                '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 360 180">'
                '<text x="24" y="64" font-size="14">Evidence</text></svg>',
                encoding="utf-8",
            )
            md = root / "visual.md"
            html = root / "visual.html"
            md.write_text(
                "---\nkind: 图解学习\nstatus: 正式\nsource_lecture: source.md\n---\n\n"
                "# 图解学习样例\n\n![证据关系](diagram.png)\n\n"
                "## 来源\n\n[讲义](source.md)\n",
                encoding="utf-8",
            )
            html.write_text(
                "<!doctype html><html><head><meta name=\"viewport\" content=\"width=device-width,initial-scale=1\">"
                "<style>img{max-width:100%;height:auto}</style></head><body>"
                "<h1>图解学习样例</h1><svg viewBox=\"0 0 360 180\"><text>Evidence</text></svg>"
                "<h2>来源</h2><a href=\"source.md\">讲义</a></body></html>",
                encoding="utf-8",
            )
            report = root / "report.json"
            result = subprocess.run(
                [
                    sys.executable,
                    str(VALIDATOR),
                    "--md",
                    str(md),
                    "--html",
                    str(html),
                    "--formal",
                    "--mobile-content-width",
                    "360",
                    "--json-out",
                    str(report),
                ],
                text=True,
                capture_output=True,
                cwd=ROOT,
            )
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            data = json.loads(report.read_text(encoding="utf-8"))
            self.assertTrue(data["passed"], data)
            self.assertEqual(data["not_verified"][0], "图形语义")


if __name__ == "__main__":
    unittest.main()
