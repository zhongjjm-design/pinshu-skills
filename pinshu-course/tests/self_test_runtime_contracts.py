#!/usr/bin/env python3
"""Package-scoped release contract checks for course and study."""
from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
COURSE = ROOT / "pinshu-course"
STUDY = ROOT / "pinshu-study"


def main() -> int:
    errors: list[str] = []
    for root in (COURSE, STUDY):
        main = (root / "SKILL.md").read_text(encoding="utf-8")
        for name in re.findall(r"`(references/[^`]+\.md)`", main):
            if not (root / name).is_file():
                errors.append(f"missing referenced file: {root.name}/{name}")
        for path in root.rglob("*.md"):
            body = path.read_text(encoding="utf-8")
            if re.search(r"/(?:Users|home)/[^/\s]+/|\.hermes/skills/", body):
                errors.append(f"private machine path: {path.relative_to(ROOT)}")
    c = (COURSE / "SKILL.md").read_text()
    s = (STUDY / "SKILL.md").read_text()
    for requirement in ("immutable raw transcript", "faithful edit", "structured notes", "shared-map entry", "pinshu-content-assets", "adaptive sampling"):
        if requirement not in c:
            errors.append(f"course missing core release rule: {requirement}")
    for requirement in ("separate JSON indices", "real study", "not studied", "metadata_index"):
        if requirement not in s:
            errors.append(f"study missing core release rule: {requirement}")
    if errors:
        print("runtime_contracts self-test: FAIL\n" + "\n".join(errors))
        return 1
    print("runtime_contracts self-test: PASS (2 package roots, main-file links and contracts)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
