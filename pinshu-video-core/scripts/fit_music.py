#!/usr/bin/env python3
"""Fit a library music track to the film so its real ending chord lands on the end card.

Why:
1. A library track's natural ending is often a long fade; aligned naively, the end card plays in near silence and the
   film feels unfinished. So the track jumps back from one beat to an earlier beat with nearly identical harmony
   (spec BGM["loop"]) as many times as needed, and the remainder is filled by one more automatically found
   beat-aligned, harmonically similar jump.
2. After the last narrated word, the closing notes are lifted 10 dB, and the last 2 s fade out gently.
3. During chapter cards (no narration) a quiet passage of the track sounds like the audio collapsed; those stretches
   are lifted back to the track's typical level (at most +9 dB, smooth ramps).
Usage: cd <project> && python3 fit_music.py   (needs librosa, numpy, soundfile)
Then:  MIX_NO_FADEOUT=1 python3 mix.py <render.mp4> wide/assets/bgm/<track>_fit.wav <final.mp4> soft
Film length, last narrated word and chapter-card times are read from timeline.json and wide/index.html.
"""
import json
import os
import re
import subprocess

import librosa
import numpy as np
import soundfile as sf

import common as C

H = C.project_dir(); SPEC = C.load_spec(H)
FF = C.ffmpeg(); SR = 44100
OVS = getattr(SPEC, "OUT_VOICE_SUBDIR", "voice")
f = f"{H}/wide/assets/bgm/{SPEC.BGM['file']}"; OUT = f"{H}/wide/assets/bgm/{os.path.splitext(SPEC.BGM['file'])[0]}_fit.wav"
tl = json.load(open(f"{H}/timeline.json")); T = tl["TOTAL"]
# Last narrated word: start of the last voice section + start of its trailing silence
_src, _st = re.findall(r'<audio id="vo\d+" src="(assets/' + re.escape(OVS) + r'/sec\d+\.wav)" data-start="([\d.]+)"', open(f"{H}/wide/index.html").read())[-1]
_r = subprocess.run([FF, "-i", f"{H}/wide/{_src}", "-af", "silencedetect=n=-40dB:d=0.3", "-f", "null", "-"], capture_output=True, text=True).stderr
_s = [float(x) for x in re.findall(r"silence_start: ([\d.]+)", _r)]; _e = [float(x) for x in re.findall(r"silence_end: ([\d.]+)", _r)]
_d = C.duration(f"{H}/wide/{_src}")
VO_END = float(_st) + (_s[-1] if _s and (len(_e) < len(_s) or _e[-1] >= _d - 0.05) else _d)
print("film length", T, "narration ends", round(VO_END, 2))
y, _ = librosa.load(f, sr=SR, mono=False); m = y.mean(0)
b1, b2 = SPEC.BGM["loop"]  # seam: play to beat b1, jump back to beat b2
# Align the jump target to the sample by cross-correlating the two waveforms (beat tracking is only ~23 ms accurate)
w = int(0.4 * SR); a = m[int(b1 * SR) - w:int(b1 * SR) + w]
best = max(range(-int(0.06 * SR), int(0.06 * SR), 8), key=lambda d: np.dot(a, m[int(b2 * SR) + d - w:int(b2 * SR) + d + w]))
b2r = b2 + best / SR; print("jump target refined", round(b2, 3), "->", round(b2r, 4))
print("waveform correlation across the seam", round(np.corrcoef(a, m[int(b2r * SR) - w:int(b2r * SR) + w])[0, 1], 3))
cut1 = int((b1 - 0.15) * SR); cut2 = int((b2r - 0.15) * SR); X = int(0.06 * SR)  # 60 ms crossfade, 0.15 s before the beat (in the decay, not on a key strike)
fo = np.cos(np.linspace(0, np.pi / 2, X)); fi = np.sin(np.linspace(0, np.pi / 2, X))
L = (cut1 - cut2) / SR  # length gained per seam
# Number of seams is derived from the end-card time (a fixed single seam broke once the film grew from 3:57 to 4:27:
# the ending chord landed mid-film and the end card replayed the start of the track)
c0, c1 = SPEC.BGM["cadence"]; END_T = [s for s in tl["SC"] if s["k"] == "end"][0]["t"]
S = END_T + 0.4 - c0; n = max(0, int(S // L)); R = S - n * L; extra = None
print(f"ending chord must move {S:.2f}s = {n} seams of {L:.2f}s + remainder {R:.2f}s")
if R > 1.0:  # remainder: one more beat-aligned, harmonically similar jump of R-0.3 .. R+3 s between the main seam and the ending
    _, beats = librosa.beat.beat_track(y=m, sr=SR, units="time"); bp = float(np.median(np.diff(beats)))
    ch = librosa.feature.chroma_stft(y=m, sr=SR, hop_length=2048); ct = librosa.frames_to_time(np.arange(ch.shape[1]), sr=SR, hop_length=2048)

    def chroma_at(x, span=3.0):
        v = ch[:, (ct >= x) & (ct < x + span)].mean(1); return v / (np.linalg.norm(v) + 1e-9)
    pairs = [(float(np.dot(chroma_at(p), chroma_at(q))) + (0.05 if abs((p - q) / bp / 4 - round((p - q) / bp / 4)) < 0.1 else 0), p, q)
             for p in beats if b1 + 2 <= p <= c0 - 8 for q in beats if R - 0.3 <= p - q <= R + 3.0]
    best = None
    for sc_, p, q in sorted(pairs, reverse=True)[:12]:  # the 12 most similar pairs, then sample-align by cross-correlation
        a = m[int(p * SR) - w:int(p * SR) + w]
        d = max(range(-int(0.06 * SR), int(0.06 * SR), 8), key=lambda d: np.dot(a, m[int(q * SR) + d - w:int(q * SR) + d + w]))
        qr = q + d / SR; cr = float(np.corrcoef(a, m[int(qr * SR) - w:int(qr * SR) + w])[0, 1])
        if best is None or sc_ + cr > best[0]: best = (sc_ + cr, p, qr, cr, sc_)
    if best and best[3] > 0.35 and best[4] > 0.9:
        extra = (best[1], best[2]); print(f"remainder seam: {best[1]:.2f}->{best[2]:.2f} ({best[1] - best[2]:.2f}s), waveform corr {best[3]:.2f}, harmony {best[4]:.2f}")
    else:
        print("WARNING no harmonically matching remainder seam; the ending chord lands", round(R, 1), "s early (closing notes are still lifted after the narration)")
segs = [(0, cut1)] + [(cut2, cut1)] * (n - 1) + ([(cut2, int((extra[0] - 0.15) * SR)), (int((extra[1] - 0.15) * SR), y.shape[1])] if extra else [(cut2, y.shape[1])]) if n else \
       ([(0, int((extra[0] - 0.15) * SR)), (int((extra[1] - 0.15) * SR), y.shape[1])] if extra else [(0, y.shape[1])])
parts = [y[:, segs[0][0]:segs[0][1]]]
for k in range(1, len(segs)):
    e0, (s0, s1) = segs[k - 1][1], segs[k]
    parts += [y[:, e0:e0 + X] * fo + y[:, s0:s0 + X] * fi, y[:, s0 + X:s1]]
bed = np.concatenate(parts, axis=1); shift = (bed.shape[1] - y.shape[1]) / SR
print(f"extended {shift:.2f}s; dominant chord at {c0 + shift:.2f}s, tonic at {c1 + shift:.2f}s (end card starts {END_T}s, film {T}s)")
if bed.shape[1] / SR < T + 1: print("WARNING the music is shorter than the film; mix.py would loop its start onto the end - add a seam or pick another track")
bed = bed[:, :int(T * SR)]
t = np.arange(bed.shape[1]) / SR
g = np.ones_like(t)
# Lift quiet chapter-card stretches back to the track's typical level (median of 1 s windows from 2 s to the last word)
mono = bed.mean(0)
rms_db = lambda p, q: 20 * np.log10(np.sqrt(np.mean(mono[int(p * SR):int(q * SR)] ** 2)) + 1e-9)
REF = float(np.median([rms_db(k, k + 1) for k in range(2, int(VO_END) - 1)]))


def env(p, q, up=0.6, down=0.5):  # 1 between p and q, raised-cosine ramps at both ends
    e = np.zeros_like(t); e[(t >= p) & (t <= q)] = 1.0
    r = (t > p - up) & (t < p); e[r] = 0.5 - 0.5 * np.cos(np.pi * (t[r] - (p - up)) / up)
    r = (t > q) & (t < q + down); e[r] = 0.5 + 0.5 * np.cos(np.pi * (t[r] - q) / down)
    return e


for s in tl["SC"]:
    if s["k"] != "chapter": continue
    p, q = s["t"] - 0.3, s["vo"] - 0.4  # from the card's appearance to just before the chapter's first word
    lv = rms_db(p, q); gain = round(min(9.0, max(0.0, REF - lv)), 1)
    print(f"chapter card #{s['i']} {p:.1f}-{q:.1f}s: music {REF - lv:.1f} dB below typical, lifted {gain} dB")
    if gain >= 1.0: g *= 10 ** (gain / 20 * env(p, q))
# After the last word, lift the closing notes 10 dB (library endings are often recorded ~9 dB softer; +6 dB was not
# enough to close), then fade out over the last 2 s
r = (t > VO_END + 0.1) & (t < VO_END + 1.3); g[r] *= 10 ** (10 / 20 * (t[r] - VO_END - 0.1) / 1.2); g[t >= VO_END + 1.3] *= 10 ** (10 / 20)
e = t > T - 2.0; g[e] *= np.cos(np.linspace(0, np.pi / 2, e.sum()))
out = np.concatenate([bed * g, np.zeros((2, 2 * SR))], axis=1)  # 2 s of padding: mix.py loops music that is not at least 1 s longer than the video
sf.write(OUT, out.T, SR); print("ok", OUT, round(bed.shape[1] / SR, 2))
