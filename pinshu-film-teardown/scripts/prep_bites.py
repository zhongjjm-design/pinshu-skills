#!/usr/bin/env python3
"""Cut speaker bites (people speaking in the original film) into voice/bites/ for build.py.

For each bite: the stretch is cut from wide/assets/tvc.mp4 with 1 s of padding, the film's own music is removed with
Demucs vocal separation when available (the original score is cut to the original edit and clashes under a new edit),
the padding is trimmed, and the result is saved as mono 44.1 kHz WAV, transcribed (BaoCut) to <name>.words.json, and
its start time in the film is recorded in bites.json (used to show the speaker's own shot for lip sync).
Loudness is matched to the narration later, in build.py.

Spec:
  BITE_CUTS = {"bite1": (32.95, 36.9), ...}   # start, end in the original film (seconds) - listen and measure
  BITE_TEXT = {"bite1": "exact words, punctuated", ...}   # captions use these exact words; check against the audio
Usage: python3 prep_bites.py [--no-separate]   (Demucs: pip install demucs, or set DEMUCS=/path/to/demucs)
"""
import argparse
import json
import os
import shutil
import subprocess
import tempfile

import common as C

ap = argparse.ArgumentParser(); ap.add_argument("--no-separate", action="store_true"); args = ap.parse_args()
H = C.project_dir(); SPEC = C.load_spec(H); FF = C.ffmpeg()
OUT = os.path.join(H, getattr(SPEC, "BITES_DIR", "voice/bites")); os.makedirs(OUT, exist_ok=True)
TVC = f"{H}/wide/assets/tvc.mp4"; PAD = 1.0
demucs = None if args.no_separate else (os.environ.get("DEMUCS") or shutil.which("demucs"))
if not demucs and not args.no_separate:
    print("WARNING Demucs not found: bites keep the original film's music underneath. Install demucs or pass --no-separate to silence this.")
starts = {}
for name, (a, b) in SPEC.BITE_CUTS.items():
    td = tempfile.mkdtemp(); a0 = max(0.0, a - PAD)
    raw = f"{td}/{name}.wav"
    subprocess.run([FF, "-v", "error", "-y", "-ss", f"{a0:.3f}", "-to", f"{b + PAD:.3f}", "-i", TVC, "-vn", "-ac", "2", "-ar", "44100", raw], check=True)
    src = raw
    if demucs:
        subprocess.run([demucs, "--two-stems=vocals", "-o", td, raw], check=True, capture_output=True)
        src = next(os.path.join(dp, f) for dp, _, fs in os.walk(td) for f in fs if f == "vocals.wav")
    out = f"{OUT}/{name}.wav"
    subprocess.run([FF, "-v", "error", "-y", "-ss", f"{a - a0:.3f}", "-t", f"{b - a:.3f}", "-i", src, "-ac", "1", "-ar", "44100", "-c:a", "pcm_s16le", out], check=True)
    shutil.rmtree(td, ignore_errors=True)
    shutil.rmtree(f"{OUT}/{name}.bcut", ignore_errors=True)
    words = C.transcribe(out, OUT)
    json.dump(words, open(f"{OUT}/{name}.words.json", "w"), ensure_ascii=False)
    heard = C.strip("".join(w["text"] for w in words)); want = C.strip(getattr(SPEC, "BITE_TEXT", {}).get(name, ""))
    print(f"{name}: {a:.2f}-{b:.2f}s heard: {heard}" + ("" if not want or heard == want else f"\n  spec text differs: {want} - captions use the spec text, so check it"))
    starts[name] = a
json.dump(starts, open(f"{OUT}/bites.json", "w"), indent=1)
print("ok", OUT, len(starts), "bites")
