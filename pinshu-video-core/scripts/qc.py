#!/usr/bin/env python3
"""Post-render QC (HyperFrames `check` only covers the composition before rendering).
Usage: python3 qc.py <final.mp4> <project/timeline.json> <out dir> [music-free render.mp4]
Give the music-free render as the 4th argument: music hides real pauses and makes short breaths look like pauses,
so the stutter check must listen to the voice-only render.

Checks: (1) duration vs timeline (2) black stretches (3) first frame not black (4) loudness, true peak, and whether the
end card has sound (5) frames at every cut / every shot end / phone-size grid, as contact sheets labelled with scene and
caption (6) captions starting over a nearly black frame (7) picture frozen for more than 2 s (8) broken first frame at a
cut (9) mid-sentence stutters. Writes qc_report.json and prints QC PASS / QC FAIL.
"""
import difflib
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile

import numpy as np
import soundfile as sf
from PIL import Image, ImageDraw, ImageFont

import common as C

V, TL, OUT = sys.argv[1:4]; OUT = os.path.abspath(OUT); os.makedirs(OUT, exist_ok=True)
VA = sys.argv[4] if len(sys.argv) > 4 else V  # audio used for the stutter check
FF = C.ffmpeg()
FONT = os.path.join(os.path.dirname(os.path.abspath(TL)), "wide/assets/fonts/SourceHanSerif-VF.ttf")  # project font (timeline.json sits next to wide/)
tl = json.load(open(TL)); SC, caps = tl["SC"], tl["caps"]
dur = C.duration(V)
rep = {"duration": round(dur, 2), "timeline": tl["TOTAL"], "duration_diff": round(dur - tl["TOTAL"], 2)}
problems = []
if abs(rep["duration_diff"]) > 0.2: problems.append(f"duration differs from the timeline by {rep['duration_diff']}s")
r = subprocess.run([FF, "-i", V, "-vf", "blackdetect=d=0.5:pix_th=0.08", "-an", "-f", "null", "-"], capture_output=True, text=True).stderr
rep["black_stretches"] = re.findall(r"black_start:([\d.]+) black_end:([\d.]+)", r)
if rep["black_stretches"]: problems.append(f"black stretches: {rep['black_stretches']}")
# First frame: on short-video platforms it is the first thing a viewer sees, so it must not be black.
r = subprocess.run([FF, "-i", V, "-frames:v", "1", "-vf", "signalstats,metadata=print:key=lavfi.signalstats.YAVG", "-f", "null", "-"], capture_output=True, text=True).stderr
y0 = float(re.findall(r"YAVG=([\d.]+)", r)[0])  # video luma runs 16-235; 16 is black, an all-black first frame measured 22.6
rep["first_frame_luma"] = round(y0, 1)
if y0 < 28: problems.append(f"first frame is nearly black (luma {y0:.1f})")
r = subprocess.run([FF, "-i", V, "-af", "ebur128=peak=true", "-f", "null", "-"], capture_output=True, text=True).stderr
rep["loudness_lufs"] = float(re.findall(r"I:\s+(-?[\d.]+) LUFS", r)[-1])
# True peak above -1 dBTP may clip when platforms transcode
tp = float(re.findall(r"Peak:\s+(-?[\d.]+) dBFS", r)[-1]); rep["true_peak_dbtp"] = tp
if tp > -1.0: problems.append(f"true peak {tp} dBTP is above -1")
# Does the end card have sound? A track that ends in a long fade leaves the end card silent while overall loudness still passes.
ends_ = [s for s in SC if s.get("k") == "end"]; e0 = ends_[0]["t"] if ends_ else tl["TOTAL"]
if ends_:
    r = subprocess.run([FF, "-ss", f"{e0:.2f}", "-to", f"{tl['TOTAL'] - 1:.2f}", "-i", V, "-af", "ebur128", "-f", "null", "-"], capture_output=True, text=True).stderr
    tail = float(re.findall(r"I:\s+(-?[\d.]+) LUFS", r)[-1]); rep["end_card_lufs"] = tail
    if tail <= rep["loudness_lufs"] - 20: problems.append(f"end card is nearly silent ({tail} LUFS) - check how the music ends")


def frame(t, w=480):
    p = f"{OUT}/_f.png"; subprocess.run([FF, "-v", "error", "-y", "-ss", f"{t:.2f}", "-i", V, "-frames:v", "1", "-vf", f"scale={w}:-2", p], check=True)
    return Image.open(p).convert("RGB")


cap_at = lambda t: next((x for a, b, x in caps if a <= t < a + b), "")
sc_at = lambda t: next((x for x in SC if x["t"] <= t < x["t"] + x["d"]), SC[-1])
try: font = ImageFont.truetype(FONT, 18)  # labels only: an unreadable font must not stop QC
except OSError: font = ImageFont.load_default()


def sheet_of(pts, W, name):  # one frame per tile, labelled with scene number, time and the caption on screen
    Hh = W * 9 // 16; cols = 6; rows = (len(pts) + cols - 1) // cols
    sheet = Image.new("RGB", (W * cols, (Hh + 40) * rows), (20, 20, 20)); d = ImageDraw.Draw(sheet)
    for n, (x, i, k) in enumerate(pts):
        im = frame(x, W); cx, cy = (n % cols) * W, (n // cols) * (Hh + 40)
        sheet.paste(im.resize((W, Hh)), (cx, cy))
        d.text((cx + 4, cy + Hh + 2), f"#{i} {k} {x:.1f}s", font=font, fill=(255, 220, 0))
        d.text((cx + 4, cy + Hh + 20), cap_at(x)[:18], font=font, fill=(230, 230, 230))
    sheet.save(f"{OUT}/{name}", quality=85)


# (5a) one frame just after every cut, including scene starts
pts = []
for s in SC:
    starts = [s["t"] + (3.0 if s["k"] == "chapter" else 0.4)] + [c["st"] + 0.5 for c in s.get("cl", [])]
    for x in sorted(set(round(v, 2) for v in starts)): pts.append((x, s["i"], s["k"]))
sheet_of(pts, 480, "shot_starts.jpg")
# (5b) one frame 0.3 s before every shot ends: leftovers and dead holds show up in the second half of a shot
ends = []
for s in SC:
    st = sorted(set(round(v, 2) for v in [s["t"] + (3.0 if s["k"] == "chapter" else 0.0)] + [c["st"] for c in s.get("cl", [])]))
    for a, b in zip(st, st[1:] + [s["t"] + s["d"]]):
        if b - a > 1.0: ends.append((round(b - 0.3, 2), s["i"], s["k"]))
sheet_of(ends, 480, "shot_ends.jpg")
# (5c) phone size: one frame every 4 s at 360 px wide (a phone held upright playing a horizontal film), to judge legibility
sheet_of([(float(t), sc_at(t)["i"], sc_at(t)["k"]) for t in range(1, int(tl["TOTAL"]), 4)], 360, "phone_size.jpg")
# (6) brightness when a caption starts; nearly black means an empty picture
dark = []
for a, b, x in caps[::3]:
    im = np.asarray(frame(a + 0.1).convert("L").resize((64, 36)), dtype=float); m = float(im.mean())
    if m < 12: dark.append((a, x, round(m, 1)))
rep["captions_over_black"] = dark
if dark: problems.append(f"{len(dark)} captions start over a nearly black frame")
# (7) frozen picture: 10 fps, frame-to-frame luma difference near zero. Reported when a stretch exceeds 2 s
# (end card excluded). Fix by making something happen in the picture; a slow push on a text card is not allowed.
r = subprocess.run([FF, "-i", V, "-vf", "fps=10,scale=320:-1,format=gray,tblend=all_mode=difference,signalstats,metadata=print:key=lavfi.signalstats.YAVG", "-an", "-f", "null", "-"], capture_output=True, text=True).stderr
ys = [float(x) for x in re.findall(r"YAVG=([\d.]+)", r)]; still, s0 = [], None
for n, y in enumerate(ys + [99.0]):
    t = (n + 1) / 10
    if y < 0.35: s0 = t if s0 is None else s0
    elif s0 is not None:
        if t - s0 >= 2.0 and s0 < e0: still.append((round(s0, 1), round(t - s0, 1), f"#{sc_at(s0)['i']} {sc_at(s0)['k']}"))
        s0 = None
rep["frozen_over_2s"] = still; rep["near_frozen_total_s"] = round(sum(1 for y in ys if y < 0.35) / 10, 1)
if still: problems.append(f"picture frozen for more than 2 s at {[x[0] for x in still]}")


# (8) broken first frame at a cut: the renderer can draw a video at the wrong scale on its first frame. For each cut take
# 6 frames from 2 frames before it: a frame far from both neighbours (>8), not an in-between of them (a transition frame
# is), followed by clearly calmer motion (under half), is a broken frame.
def frames6(t0):
    raw = subprocess.run([FF, "-v", "error", "-ss", f"{max(t0 - 0.067, 0):.3f}", "-i", V, "-frames:v", "6", "-vf", "scale=160:90,format=gray", "-f", "rawvideo", "-"], capture_output=True).stdout
    return np.frombuffer(raw, np.uint8).reshape(-1, 90, 160).astype(float)


cuts = sorted(set([round(c["st"], 3) for s in SC for c in s.get("cl", []) if c.get("file")] + [round(s["t"] + (2.9 if s["k"] == "chapter" else 0), 3) for s in SC if s["k"] in ("full", "story", "chips", "chapter") and not s.get("cl")]))
badf = []
for x in cuts:
    f = frames6(x); dd_ = lambda a, b: float(np.abs(f[a] - f[b]).mean())
    for m in range(1, min(4, len(f) - 2)):
        if dd_(m - 1, m) > 8 and dd_(m, m + 1) > 8 and dd_(m + 1, m + 2) < dd_(m, m + 1) / 2 and float(np.abs(f[m] - (f[m - 1] + f[m + 1]) / 2).mean()) > 0.5 * min(dd_(m - 1, m), dd_(m, m + 1)):
            badf.append((x, f"#{sc_at(x)['i']} {sc_at(x)['k']}")); break
rep["broken_first_frames"] = badf
notes = []
if badf: notes.append(f"possible broken first frames at {[b[0] for b in badf]} - look at them; a normal 2-frame transition can trigger this")
# (9) mid-sentence stutters, starting from measured silence rather than transcribed character times (those absorb
# pauses and lag one or two characters). Every stretch of speech between silences is concatenated with 1.5 s gaps and
# transcribed once; a silence is a stutter when the script has no punctuation between the last recognised character
# before it and the first one after it.
if C.transcription_enabled():
    strip = C.strip
    wav = f"{OUT}/_a.wav"; subprocess.run([FF, "-v", "error", "-y", "-i", VA, "-vn", "-ac", "1", "-ar", "16000", wav], check=True)
    AUD, SR = sf.read(wav); h = 800; Q = -45 if VA != V else -32  # voice-only render is near silent at pauses; the final has a music floor
    db = [20 * np.log10(np.sqrt(np.mean(AUD[i:i + h] ** 2)) + 1e-9) for i in range(0, len(AUD) - h, h // 2)]
    runs, st = [], None
    for n, d in enumerate(db + [0]):
        t = n * (h // 2) / SR
        if d < Q: st = t if st is None else st
        elif st is not None:
            if t - st >= 0.3: runs.append((st, t))
            st = None
    bw = [(x["bite_t"] - 0.3, x["bite_t"] + x.get("bite_d", 0) + 0.3) for x in SC if x.get("bite_t") is not None]
    runs = [(a, e) for a, e in runs if not any(p <= a <= q or p <= e <= q for p, q in bw)]  # pauses inside real speaker bites are human breaths
    segs = [(0.0, runs[0][0])] + [(runs[k][1], runs[k + 1][0]) for k in range(len(runs) - 1)] + [(runs[-1][1], len(AUD) / SR)] if runs else [(0.0, len(AUD) / SR)]
    GAP = 1.5; parts, offs, o = [], [], 0.0
    for a, e in segs:
        x = AUD[int(a * SR):int(e * SR)]; parts += [x, np.zeros(int(GAP * SR))]; offs.append((o, o + len(x) / SR)); o += len(x) / SR + GAP
    td = tempfile.mkdtemp(); sf.write(f"{td}/cat.wav", np.concatenate(parts), SR)
    hc, hs = [], []  # each recognised character and the speech stretch it belongs to
    for w in C.transcribe(f"{td}/cat.wav", td):
        cs = strip(w["text"]); seg = max([k for k, (p, q) in enumerate(offs) if p - 0.3 <= w["t0"]] or [0])
        for c in cs: hc.append(c); hs.append(seg)
    ref = "".join(tl.get("narr", [])); rr = strip(ref)
    sm = difflib.SequenceMatcher(None, rr, "".join(hc), autojunk=False)
    h2r = {b.b + k: b.a + k for b in sm.get_matching_blocks() for k in range(b.size)}
    should, k0 = set(), -1  # script characters followed by punctuation
    for c in ref:
        if c in C.PUNC: should.add(k0)
        else: k0 += 1
    stutter, seen = [], set()
    m_of = {}  # matched script positions per speech stretch
    for i in range(len(hc)):
        if i in h2r: m_of.setdefault(hs[i], []).append(h2r[i])
    for k, (a, e) in enumerate(runs):
        # skip stretches with only sound effects (transition whooshes, opening, ending)
        pb = [j for j in range(k, -1, -1) if m_of.get(j)]; pa = [j for j in range(k + 1, len(segs)) if m_of.get(j)]
        if not pb or not pa: continue
        b0, a0 = m_of[pb[0]][-1], m_of[pa[0]][0]
        if (b0, a0) in seen: continue
        seen.add((b0, a0))
        if b0 < 0 or a0 <= b0: continue
        if any(i in should for i in range(b0, a0)): continue  # punctuation in between: a normal pause
        if a0 - b0 > 8: stutter.append((round(a, 2), round(e - a, 2), rr[max(0, b0 - 4):b0 + 1] + "|...|" + rr[a0:a0 + 4], "alignment unclear - listen")); continue
        stutter.append((round(a, 2), round(e - a, 2), rr[max(0, b0 - 4):b0 + 1] + "|" + rr[b0 + 1:b0 + 5], "mid-sentence stutter"))
    shutil.rmtree(td, ignore_errors=True); os.remove(wav)
    rep["misread_ratio"] = round(1 - sum(b.size for b in sm.get_matching_blocks()) / max(len(rr), 1), 3)
    rep["stutters"] = stutter
    if [s for s in stutter if s[3] == "mid-sentence stutter"]: problems.append(f"{len(stutter)} mid-sentence stutters")
    if rep["misread_ratio"] > 0.05: notes.append(f"misread ratio {rep['misread_ratio']} - listen for wrong words")
else:
    notes.append("stutter check skipped: transcription is off or BaoCut is missing")
rep["problems"] = problems; rep["notes"] = notes
json.dump(rep, open(f"{OUT}/qc_report.json", "w"), ensure_ascii=False, indent=1)
if os.path.exists(f"{OUT}/_f.png"): os.remove(f"{OUT}/_f.png")
print(json.dumps(rep, ensure_ascii=False, indent=1))
print("contact sheets:", f"{OUT}/shot_starts.jpg", f"({len(pts)} cuts)", f"{OUT}/shot_ends.jpg", f"({len(ends)} shot ends)", f"{OUT}/phone_size.jpg")
print("QC PASS" if not problems else "QC FAIL: " + "; ".join(problems))
for n_ in notes: print("note:", n_)
sys.exit(0 if not problems else 1)
