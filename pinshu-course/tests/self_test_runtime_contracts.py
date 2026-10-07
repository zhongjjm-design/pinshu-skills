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
    course_requirements = {
        "immutable raw transcript": ("不可变原始转写", "immutable raw transcript"),
        "faithful edit": ("忠实精编稿", "faithful edit"),
        "structured notes": ("结构化讲义", "structured notes"),
        "shared-map entry": ("共享课程地图", "课程地图", "shared-map entry"),
        "pinshu-content-assets": ("pinshu-content-assets",),
        "adaptive sampling": ("自适应抽样", "adaptive sampling"),
    }
    for label, alternatives in course_requirements.items():
        if not any(requirement in c for requirement in alternatives):
            errors.append(f"course missing core release rule: {label}")
    study_requirements = {
        "separate JSON indices": ("独立 JSON 索引", "separate JSON indices"),
        "real study": ("真实学习", "真实作答", "real study"),
        "not studied": ("未学习", "没学过", "not studied"),
        "metadata_index": ("索引指针", "metadata_index"),
    }
    for label, alternatives in study_requirements.items():
        if not any(requirement in s for requirement in alternatives):
            errors.append(f"study missing core release rule: {label}")
    if errors:
        print("runtime_contracts self-test: FAIL\n" + "\n".join(errors))
        return 1
    print("runtime_contracts self-test: PASS (2 package roots, main-file links and contracts)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
