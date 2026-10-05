#!/usr/bin/env python3
"""Check that this machine can run the whole pipeline; prints what is missing and how to fix it.
Usage: python3 doctor.py [project dir]   (exit code 1 when something required is missing)
Keys are only checked for presence, never printed.
"""
import importlib.util
import os
import shutil
import subprocess
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import common as C  # noqa: E402

ok, warn, bad = [], [], []
v = sys.version_info
(ok if v >= (3, 9) else bad).append(f"python {v.major}.{v.minor}" + ("" if v >= (3, 9) else " (need 3.9+)"))
for mod, pip, need in [("numpy", "numpy", True), ("soundfile", "soundfile", True), ("PIL", "pillow", True), ("librosa", "librosa", False)]:
    if importlib.util.find_spec(mod): ok.append(f"python module {mod}")
    else: (bad if need else warn).append(f"python module {mod} missing: pip install {pip}" + ("" if need else " (needed for fit_music.py and patch_voice.py)"))
try:
    ff = C.ffmpeg(); filters = subprocess.run([ff, "-hide_banner", "-filters"], capture_output=True, text=True).stdout
    miss = [f for f in ("ebur128", "silencedetect", "atempo", "signalstats", "tblend", "blackdetect", "alimiter", "sidechaincompress") if f" {f} " not in filters]
    (bad if miss else ok).append(f"ffmpeg {ff}" + (f" lacks filters {miss} (macOS: brew install ffmpeg-full)" if miss else ""))
    C.ffprobe(); ok.append("ffprobe")
except SystemExit as ex: bad.append(str(ex))
node = shutil.which("node"); (ok if node else bad).append("node" if node else "node missing: install Node.js 22+")
hf = shutil.which("hyperframes")
if hf: ok.append("hyperframes " + subprocess.run([hf, "--version"], capture_output=True, text=True).stdout.strip())
else: bad.append("hyperframes CLI missing: npm install -g hyperframes")
if C.baocut(): ok.append("BaoCut transcription")
else: bad.append("BaoCut missing: install the BaoCut app and skill (https://github.com/JimLiu/baocut), or set BAOCUT=/path/to/baocut")
if shutil.which("demucs") or os.environ.get("DEMUCS"): ok.append("demucs (vocal separation for speaker bites)")
else: warn.append("demucs missing: speaker bites will keep the original film's music (pip install demucs)")
try: C.gemini_key(); ok.append("Gemini API key found (not shown)")
except SystemExit: warn.append("Gemini API key missing: needed for gen_voice.py (GEMINI_API_KEY or ~/.config/gemini/.env)")
P = sys.argv[1] if len(sys.argv) > 1 else None
if P:
    P = os.path.abspath(P)
    spec = os.environ.get("SPEC") or os.path.join(P, "spec.py")
    (ok if os.path.isfile(spec) else bad).append(f"content spec {spec}" + ("" if os.path.isfile(spec) else " missing (run new_project.py or set SPEC)"))
    for rel in ("wide/hyperframes.json", "wide/assets/tvc.mp4", "wide/assets/fonts/SourceHanSerif-VF.ttf",
                "wide/assets/sfx/whoosh.mp3", "wide/assets/sfx/pop.mp3", "wide/assets/sfx/click-soft.mp3"):
        (ok if os.path.exists(os.path.join(P, rel)) else bad).append(f"project {rel}" + ("" if os.path.exists(os.path.join(P, rel)) else " missing (run new_project.py)"))
    if os.path.exists(os.path.join(P, "wide/assets/fonts/HiraginoSansGB.ttc")): ok.append("project wide/assets/fonts/HiraginoSansGB.ttc")
    else: warn.append("Hiragino Sans GB missing (a macOS system font): comment cards fall back to the system sans-serif, so on Linux install a CJK "
                      "font such as Noto Sans CJK SC; for covers set PINSHU_COVER_FONT to a bold CJK font")
free = shutil.disk_usage(P or os.getcwd()).free / 1e9
(ok if free > 10 else warn).append(f"free disk {free:.0f} GB" + ("" if free > 10 else " (a film needs a few GB for renders)"))
for x in ok: print("  ok  ", x)
for x in warn: print("  warn", x)
for x in bad: print("  FAIL", x)
print("READY" if not bad else f"NOT READY: {len(bad)} required item(s) missing")
sys.exit(1 if bad else 0)
