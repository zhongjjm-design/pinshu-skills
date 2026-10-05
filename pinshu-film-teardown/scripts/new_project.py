#!/usr/bin/env python3
"""Create a new brand-film teardown project folder.

Usage: python3 new_project.py <project dir> --film <original brand film.mp4> [--serif-font <SourceHanSerif*.ttf>]

Creates:
  <project>/spec.py                     content spec (from assets/spec_template.py)
  <project>/sections.json               narration sections to fill in
  <project>/voice/bites/                speaker bites (prep_bites.py)
  <project>/wide/hyperframes.json
  <project>/wide/assets/tvc.mp4         the original film (hard link when possible, otherwise a copy)
  <project>/wide/assets/{img/hd,stock,bgm,sfx,fonts}
Sound effects are copied from the installed HyperFrames package (Pixabay Content License). Fonts: Hiragino Sans GB is
copied from macOS system fonts; Source Han Serif (SIL OFL) is taken from --serif-font, ~/Library/Fonts, or downloaded
from Adobe's repository (Simplified Chinese subset, about 25 MB). Nothing is overwritten.
"""
import argparse
import glob
import json
import os
import shutil
import sys
import urllib.request

import common as C

SERIF_URL = "https://github.com/adobe-fonts/source-han-serif/raw/release/Variable/TTF/Subset/SourceHanSerifCN-VF.ttf"
SFX = {"whoosh.mp3": "whoosh.mp3", "whoosh-short.mp3": "whoosh.mp3", "whoosh-cinematic.mp3": "whoosh-cinematic.mp3",
       "click-soft.mp3": "click.mp3", "pop.mp3": "pop.mp3", "chime.mp3": "chime.mp3"}
HYPERFRAMES_JSON = {"$schema": "https://hyperframes.heygen.com/schema/hyperframes.json",
                    "registry": "https://raw.githubusercontent.com/heygen-com/hyperframes/main/registry",
                    "paths": {"blocks": "compositions", "components": "compositions/components", "assets": "assets"},
                    "media": {"autoProxy": True}, "authoringSkill": "general-video"}

ap = argparse.ArgumentParser(); ap.add_argument("project"); ap.add_argument("--film", required=True); ap.add_argument("--serif-font")
args = ap.parse_args()
P = os.path.abspath(args.project); A = f"{P}/wide/assets"
for d in ("voice/bites", "wide/renders", "wide/assets/img/hd", "wide/assets/stock", "wide/assets/bgm", "wide/assets/sfx", "wide/assets/fonts"):
    os.makedirs(f"{P}/{d}", exist_ok=True)
done, todo = [], []


def put(src, dst, link=False):
    if os.path.exists(dst): done.append(f"kept existing {os.path.relpath(dst, P)}"); return
    try:
        if link: os.link(src, dst)
        else: shutil.copy(src, dst)
    except OSError: shutil.copy(src, dst)
    done.append(f"{os.path.relpath(dst, P)} <- {src}")


if not os.path.isfile(args.film): sys.exit(f"original film not found: {args.film}")
put(os.path.abspath(args.film), f"{A}/tvc.mp4", link=True)
if not os.path.exists(f"{P}/spec.py"): shutil.copy(f"{C.ASSETS}/spec_template.py", f"{P}/spec.py"); done.append("spec.py (template - fill it in)")
if not os.path.exists(f"{P}/sections.json"):
    json.dump({"sections": [{"j": 0, "text": "<section 0 narration>"}, {"j": 1, "text": "<section 1 narration>"}]}, open(f"{P}/sections.json", "w"), ensure_ascii=False, indent=1)
    done.append("sections.json (template - one entry per topic section)")
if not os.path.exists(f"{P}/wide/hyperframes.json"): json.dump(HYPERFRAMES_JSON, open(f"{P}/wide/hyperframes.json", "w"), indent=2)

# Sound effects from the HyperFrames package
hf = shutil.which("hyperframes"); sfx_dir = None
if hf:
    d = os.path.dirname(os.path.realpath(hf))
    while d != os.path.dirname(d) and not os.path.isfile(os.path.join(d, "package.json")): d = os.path.dirname(d)
    cand = glob.glob(os.path.join(d, "**", "audio", "assets", "sfx"), recursive=True)
    sfx_dir = cand[0] if cand else None
if sfx_dir:
    for name, src in SFX.items():
        if os.path.isfile(os.path.join(sfx_dir, src)): put(os.path.join(sfx_dir, src), f"{A}/sfx/{name}")
else: todo.append("sound effects: install HyperFrames (npm install -g hyperframes) and rerun, or put whoosh/pop/click-soft/chime mp3 files in wide/assets/sfx/")

# Fonts
hiragino = "/System/Library/Fonts/Hiragino Sans GB.ttc"
if os.path.isfile(hiragino): put(hiragino, f"{A}/fonts/HiraginoSansGB.ttc")
else: print("note: Hiragino Sans GB (macOS) not found; comment cards will use the system sans-serif (on Linux install Noto Sans CJK SC), "
            "and make_cover.py needs PINSHU_COVER_FONT")
serif = f"{A}/fonts/SourceHanSerif-VF.ttf"
if not os.path.exists(serif):
    local = args.serif_font or next(iter(sorted(glob.glob(os.path.expanduser("~/Library/Fonts/SourceHanSerif*VF*.tt*")))), None)
    if local and os.path.isfile(local): put(local, serif)
    else:
        try:
            print("downloading Source Han Serif (CN subset, ~25 MB)..."); urllib.request.urlretrieve(SERIF_URL, serif); done.append(f"{os.path.relpath(serif, P)} <- {SERIF_URL}")
        except Exception as ex: todo.append(f"Source Han Serif: download {SERIF_URL} to {serif} ({ex})")
todo += ["music: put a library track in wide/assets/bgm/ and record its source and licence next to it",
         "images: posters as wide/assets/img/hd/p01.jpg ..., comments screenshot, QR code (only what the spec uses)",
         "write sections.json and spec.py, then follow SKILL.md from the voice step"]
print("project:", P); [print("  +", x) for x in done]; print("to do:"); [print("  -", x) for x in todo]
