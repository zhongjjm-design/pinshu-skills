#!/usr/bin/env python3
"""Patch a few rushed words without re-synthesizing (a new take changes the voice): slow chosen stretches with ffmpeg
atempo, pitch unchanged. Each stretch is processed with 0.12 s of context on both sides and trimmed back, so edges do
not smear. Cut points must sit in silence or a fricative. Writes a new voice source folder; the source stays untouched.
Method comparison on one 5.5 s passage (naturalness score, only used to detect artefacts): original 2.83, atempo 2.75,
rubberband 2.26-2.53 (audible).

The stretches live in the spec:
  PATCH = {"src": "voice/gemini_Charon", "dst": "voice/gemini_Charon_patched",
           "ops": {1: [(19.75, 20.38, 1.35), (20.85, 21.54, 1.10), (21.6, 21.6, ("pause", 0.09))]}}
  ops: section number -> list of (start, end, slow-down factor) or (t, t, ("pause", seconds)).
Times must be measured on that exact take (energy curve plus transcription of the stretch); every new take needs new times.
Usage: python3 patch_voice.py   then point VO_SRC in the spec at PATCH["dst"]. Needs numpy, soundfile, librosa.
"""
import json
import os
import shutil
import subprocess
import tempfile

import librosa
import numpy as np
import soundfile as sf

import common as C

H = C.project_dir(); SPEC = C.load_spec(H); FF = C.ffmpeg()
P = SPEC.PATCH
SRC = os.path.join(H, P["src"]); DST = os.path.join(H, P["dst"])
SR = 24000; CTX = 0.12
TD = tempfile.mkdtemp(); T = lambda n: os.path.join(TD, f"_pv_{n}.wav")
shutil.copytree(SRC, DST, ignore=shutil.ignore_patterns("*.bcut", "_whole*", "_island_cache.json"), dirs_exist_ok=True)  # reruns overwrite; the output folder is regenerable
if os.path.exists(f"{DST}/_island_cache.json"): os.remove(f"{DST}/_island_cache.json")  # audio changed: build.py's transcription cache is stale


def slow(y, a, b, k):
    sf.write(T("i"), y[int((a - CTX) * SR):int((b + CTX) * SR)], SR)
    subprocess.run([FF, "-v", "error", "-y", "-i", T("i"), "-af", f"atempo={1 / k:.5f}", T("o")], check=True)
    x = sf.read(T("o"), dtype="float32")[0]; return x[int(CTX * k * SR):len(x) - int(CTX * k * SR)]


for j, ops in P["ops"].items():
    j = int(j); y = librosa.load(f"{SRC}/sec{j:02d}.mp3", sr=SR)[0]; out, pos = [], 0.0
    for a, b, k in ops:
        out.append(y[int(pos * SR):int(a * SR)])
        out.append(np.zeros(int(k[1] * SR), dtype=np.float32) if isinstance(k, (tuple, list)) else slow(y, a, b, k)); pos = b
    out.append(y[int(pos * SR):]); z = np.concatenate(out)
    sf.write(T("z"), z, SR); subprocess.run([FF, "-v", "error", "-y", "-i", T("z"), "-b:a", "192k", f"{DST}/sec{j:02d}.mp3"], check=True)
    print(f"section {j}: {len(y) / SR:.2f} -> {len(z) / SR:.2f} s")
    shutil.rmtree(f"{DST}/sec{j:02d}.bcut", ignore_errors=True)
    json.dump(C.transcribe(f"{DST}/sec{j:02d}.mp3", DST), open(f"{DST}/sec{j:02d}.words.json", "w"), ensure_ascii=False)
shutil.rmtree(TD, ignore_errors=True)
print("ok", DST)
