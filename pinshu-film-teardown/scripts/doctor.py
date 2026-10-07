#!/usr/bin/env python3
"""Check the shared video core plus brand-film project files."""
import os

import _video_core

FILES = (
    "wide/hyperframes.json",
    "wide/assets/tvc.mp4",
    "wide/assets/fonts/SourceHanSerif-VF.ttf",
    "wide/assets/sfx/whoosh.mp3",
    "wide/assets/sfx/pop.mp3",
    "wide/assets/sfx/click-soft.mp3",
)


def project_checks(project, ok, warn, bad):
    for rel in FILES:
        path = os.path.join(project, rel)
        if os.path.exists(path):
            ok.append(f"project {rel}")
        else:
            bad.append(f"project {rel} missing (run new_project.py)")
    if os.path.exists(os.path.join(project, "wide/assets/fonts/HiraginoSansGB.ttc")):
        ok.append("project wide/assets/fonts/HiraginoSansGB.ttc")
    else:
        warn.append(
            "Hiragino Sans GB missing: on Linux install a CJK font such as Noto Sans CJK SC; "
            "for covers set PINSHU_COVER_FONT to a bold CJK font"
        )


if __name__ == "__main__":
    _video_core.load("doctor.py", "pinshu_video_core_doctor").main(project_checks)
