#!/usr/bin/env python3
"""Resolve an explicitly supplied content destination without creating it."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

KEYS = {
    "draft": "content_draft_destination",
    "final": "content_final_destination",
    "handoff": "content_workflow_handoff",
}
ALLOWED_CONFIG_KEYS = set(KEYS.values())


def reject_duplicate_keys(pairs: list[tuple[str, object]]) -> dict[str, object]:
    result: dict[str, object] = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"duplicate JSON key: {key}")
        result[key] = value
    return result


def load_config(path: Path) -> dict[str, str]:
    text = path.read_text(encoding="utf-8")
    if path.suffix.lower() == ".json":
        payload = json.loads(text, object_pairs_hook=reject_duplicate_keys)
        if not isinstance(payload, dict):
            raise ValueError("config root must be an object")
        unknown = set(payload) - ALLOWED_CONFIG_KEYS
        if unknown:
            raise ValueError(f"unsupported config keys: {sorted(unknown)}")
        data: dict[str, str] = {}
        for key, value in payload.items():
            if value is None:
                continue
            if not isinstance(value, str):
                raise ValueError(f"{key} must be a string or null")
            value = value.strip()
            if value:
                data[key] = value
        return data

    data = {}
    for number, line in enumerate(text.splitlines(), 1):
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        if line[:1].isspace():
            raise ValueError(f"line {number} is nested; only flat top-level key: value is allowed")
        if ":" not in line:
            raise ValueError(f"line {number} is not key: value")
        key, value = line.split(":", 1)
        key = key.strip()
        if key not in ALLOWED_CONFIG_KEYS:
            raise ValueError(f"line {number} has unsupported key: {key}")
        if key in data:
            raise ValueError(f"line {number} duplicates key: {key}")
        value = value.strip().strip("'\"")
        if value:
            data[key] = value
    return data


def main() -> int:
    parser = argparse.ArgumentParser(description="Resolve routes only; never creates or writes destination directories.")
    parser.add_argument("--role", required=True, choices=sorted(KEYS))
    parser.add_argument("--config", type=Path)
    parser.add_argument("--draft-destination")
    parser.add_argument("--final-destination")
    parser.add_argument("--handoff")
    args = parser.parse_args()

    explicit = {
        "content_draft_destination": args.draft_destination,
        "content_final_destination": args.final_destination,
        "content_workflow_handoff": args.handoff,
    }
    key = KEYS[args.role]
    source = None
    destination = explicit.get(key)
    if isinstance(destination, str):
        destination = destination.strip() or None
    if destination:
        source = "explicit_argument"
    elif args.config is not None:
        if not args.config.exists():
            print(json.dumps({"route_resolution_status": "error", "error": "config_not_found", "config": str(args.config)}, ensure_ascii=False))
            return 2
        try:
            config = load_config(args.config)
        except Exception as exc:
            print(json.dumps({"route_resolution_status": "error", "error": "invalid_config", "detail": str(exc)}, ensure_ascii=False))
            return 2
        destination = config.get(key)
        if destination:
            source = "explicit_config"

    if not destination:
        print(json.dumps({
            "role": key,
            "route_resolution_status": "unresolved",
            "delivery_status": "destination_unresolved",
            "destination": None,
            "created": False,
        }, ensure_ascii=False, indent=2))
        return 0

    if key in {"content_draft_destination", "content_final_destination"}:
        target = Path(destination)
        if not target.is_absolute():
            print(json.dumps({
                "role": key,
                "route_resolution_status": "error",
                "error": "destination_must_be_absolute",
                "destination": destination,
                "created": False,
            }, ensure_ascii=False, indent=2))
            return 2

    print(json.dumps({
        "role": key,
        "route_resolution_status": "resolved",
        "delivery_status": "handoff_pending",
        "destination": destination,
        "resolution_source": source,
        "destination_exists": Path(destination).exists() if key != "content_workflow_handoff" else None,
        "created": False,
    }, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
