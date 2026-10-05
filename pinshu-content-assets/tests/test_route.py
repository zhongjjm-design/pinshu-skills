#!/usr/bin/env python3
"""Public route-helper regressions (no private configuration or writes)."""

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

HELPER = Path(__file__).resolve().parents[1] / "scripts" / "resolve-content-route.py"


class RouteTests(unittest.TestCase):
    def run_route(self, *args):
        result = subprocess.run(
            [sys.executable, str(HELPER), "--role", "draft", *map(str, args)],
            capture_output=True, text=True, check=False,
        )
        return result.returncode, json.loads(result.stdout)

    def test_no_config_is_unresolved(self):
        code, result = self.run_route()
        self.assertEqual(code, 0)
        self.assertEqual(result["route_resolution_status"], "unresolved")
        self.assertIsNone(result["destination"])
        self.assertFalse(result["created"])

    def test_explicit_config_and_override_do_not_create_destinations(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            target = root / "not-created"
            override = root / "override-not-created"
            config = root / "routes.yaml"
            config.write_text(f"content_draft_destination: {target}\n", encoding="utf-8")
            code, result = self.run_route("--config", config)
            self.assertEqual(code, 0)
            self.assertEqual(result["destination"], str(target))
            self.assertEqual(result["resolution_source"], "explicit_config")
            self.assertFalse(result["destination_exists"])
            self.assertFalse(target.exists())
            code, result = self.run_route("--config", config, "--draft-destination", override)
            self.assertEqual(code, 0)
            self.assertEqual(result["destination"], str(override))
            self.assertEqual(result["resolution_source"], "explicit_argument")
            self.assertFalse(override.exists())

    def test_relative_path_and_missing_config_are_errors_not_delivery(self):
        code, result = self.run_route("--draft-destination", "relative/drafts")
        self.assertEqual(code, 2)
        self.assertEqual(result["route_resolution_status"], "error")
        with tempfile.TemporaryDirectory() as temporary:
            code, result = self.run_route("--config", Path(temporary) / "missing.yaml")
        self.assertEqual(code, 2)
        self.assertEqual(result["error"], "config_not_found")

    def test_duplicate_config_keys_are_rejected(self):
        with tempfile.TemporaryDirectory() as temporary:
            config = Path(temporary) / "routes.yaml"
            config.write_text("content_draft_destination: /one\ncontent_draft_destination: /two\n", encoding="utf-8")
            code, result = self.run_route("--config", config)
            self.assertEqual(code, 2)
            self.assertEqual(result["error"], "invalid_config")


if __name__ == "__main__":
    unittest.main(verbosity=2)
