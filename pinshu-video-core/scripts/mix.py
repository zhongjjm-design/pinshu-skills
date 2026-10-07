#!/usr/bin/env python3
"""Final mix: music-free render + music -> finished film. Fixed gain to -14 LUFS, no dynamic compression
(avoids pumping volume).
Usage: python3 mix.py <render.mp4> <music> <out.mp4> [duck|soft [music start seconds]]
  no mode: music added at a fixed 0.36 level.
  duck: music 10 dB under the narration, ducking about 6 dB more while someone speaks.
  soft: default for explainers ("gentle, a little dark, barely noticed yet just right").
        Music above 4 kHz is cut, 2.5 kHz is dipped 4 dB to leave room for the voice, the bed sits 14 dB under the
        narration, and ducking is only about 3 dB with slow attack and release.
  Both modes loop short music with crossfades and fade it in over 1.5 s and out over 4 s
  (MIX_NO_FADEOUT=1 skips the fade-out when the music was already fitted to end on the end card).
True peak is kept at or below -1 dBTP after AAC encoding (platform transcoding clips anything hotter).
"""
import os
import re
import subprocess
import sys
import tempfile

import common as C

FF = C.ffmpeg()
v, b, o = sys.argv[1:4]
mode = sys.argv[4] if len(sys.argv) > 4 else ""
duck = mode in ("duck", "soft")
ss = float(sys.argv[5]) if len(sys.argv) > 5 else 0.0
REL, EQ, SC = {"soft": (-14, "lowpass=f=4000:p=2,equalizer=f=2500:t=q:w=1:g=-4,",
                        "sidechaincompress=threshold=0.08:ratio=1.8:attack=80:release=900:knee=6")}.get(
    mode, (-10, "", "sidechaincompress=threshold=0.06:ratio=2.5:attack=40:release=600:knee=4"))
tmp = os.path.join(tempfile.gettempdir(), "pinshu_mix_tmp.wav")
lufs = lambda f, extra=[]: float(re.findall(r"I:\s+(-?[\d.]+) LUFS", subprocess.run([FF, *extra, "-i", f, "-af", "ebur128", "-f", "null", "-"], capture_output=True, text=True).stderr)[-1])
dur = C.duration
if duck:
    T = dur(v); bl = dur(b) - ss; k = 1
    while bl + (k - 1) * (bl - 3) < T + 1: k += 1
    ins = sum([["-ss", str(ss), "-i", b] for _ in range(k)], []); fc = ""; prev = "[1:a]"
    for j in range(2, k + 1): fc += f"{prev}[{j}:a]acrossfade=d=3[c{j}];"; prev = f"[c{j}]"
    # Render the looped, EQ'd bed on its own first and set its gain from measured loudness (EQ losses included)
    bed = os.path.join(tempfile.gettempdir(), "pinshu_mix_bed.wav")
    subprocess.run([FF, "-y", "-loglevel", "error", "-i", v, *ins, "-filter_complex", fc + f"{prev}atrim=0:{T},{EQ}aformat=channel_layouts=stereo[o]",
                    "-map", "[o]", "-ar", "48000", bed], check=True)
    g = lufs(v) + REL - lufs(bed)  # music REL dB under the measured narration loudness, not a fixed level
    fade_out = "" if os.environ.get("MIX_NO_FADEOUT") else f",afade=t=out:st={T-4:.2f}:d=4"  # no fade when the music already ends on its own chord
    fc2 = (f"[1:a]volume={g:.2f}dB,afade=t=in:st=0:d=1.5{fade_out}[bg];"
           f"[0:a]aformat=channel_layouts=stereo,asplit=2[vo][key];[bg][key]{SC}[bd];"
           f"[vo][bd]amix=inputs=2:normalize=0:duration=first[a]")
    subprocess.run([FF, "-y", "-loglevel", "error", "-i", v, "-i", bed, "-filter_complex", fc2, "-map", "[a]", "-ar", "48000", tmp], check=True)
    os.remove(bed)
else:
    subprocess.run([FF, "-y", "-loglevel", "error", "-i", v, "-i", b, "-filter_complex",
                    "[1:a]volume=0.36[m];[0:a][m]amix=inputs=2:normalize=0:duration=first[a]", "-map", "[a]", "-ar", "48000", tmp], check=True)
I = lufs(tmp); g = -14.0 - I
tpk = lambda f: float(re.findall(r"Peak:\s+(-?[\d.]+) dBFS", subprocess.run([FF, "-i", f, "-af", "ebur128=peak=true", "-f", "null", "-"], capture_output=True, text=True).stderr)[-1])
# Upsample 4x before limiting to catch inter-sample peaks, limit at -2 dBFS (a -1 dBFS limit still reached -0.3 dBTP
# after AAC). Re-measure after encoding and lower the gain if the true peak is still above -1.
for _ in range(3):
    subprocess.run([FF, "-y", "-loglevel", "error", "-i", v, "-i", tmp, "-map", "0:v", "-map", "1:a", "-c:v", "copy",
                    "-af", f"volume={g:.2f}dB,aresample=192000,alimiter=limit=0.79:level=false,aresample=48000", "-c:a", "aac", "-b:a", "192k", o], check=True)
    tp = tpk(o)
    if tp <= -1.0: break
    g -= tp + 1.3; print(f"  true peak after encoding {tp} dBTP, gain lowered to {g:+.1f} dB and re-encoded")
os.remove(tmp)
print(f"mixed {o}: integrated {I:.1f} -> gain {g:+.1f} dB" + (f" ({mode})" if duck else ""))
