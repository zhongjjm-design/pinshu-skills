"""Shared helpers for pinshu-film-teardown scripts."""
import os

import _video_core

globals().update({
    key: value
    for key, value in vars(_video_core.load("common.py", "pinshu_video_core_common")).items()
    if not key.startswith("__")
})

SKILL_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ASSETS = os.path.join(SKILL_DIR, "assets")
