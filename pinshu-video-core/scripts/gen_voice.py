#!/usr/bin/env python3
"""Synthesize the whole narration in ONE Gemini TTS call, then split it into sections at real silences.

Why one call: synthesizing section by section lets the voice drift between calls (pitch moved from ~120 Hz to
~135 Hz once, and the film sounded like two narrators).
Output folder (default voice/gemini_<voice><tag>/): secNN.mp3, secNN.words.json (per-character pronunciation times from
BaoCut), sections.json.

Usage: python3 gen_voice.py <sections.json> [--voice Charon] [--style "..."] [--warm "..."] [--tag _v2] [--out DIR]
  sections.json: {"sections": [{"j": 0, "text": "..."}, ...]} - one entry per topic section, in order.
  --warm: a throwaway warm-up sentence read before the narration and cut off afterwards (the first sentence otherwise
          tends to start low and flat).
  --dry-run: check inputs and print the request size without calling the API.
The API key is read at run time from GEMINI_API_KEY or ~/.config/gemini/.env and never written anywhere.
"""
import argparse
import array
import base64
import difflib
import hashlib
import json
import os
import re
import subprocess
import sys
import urllib.error
import urllib.request

import common as C

ap = argparse.ArgumentParser()
ap.add_argument("sections")
ap.add_argument("--voice", default="Charon")
ap.add_argument("--model", default="gemini-3.8-flash-tts")
ap.add_argument("--style", default="\u50cf\u8ddf\u540c\u884c\u670b\u53cb\u804a\u4e00\u4e2a\u6848\u4f8b\uff0c\u677e\u5f1b\uff0c\u6709\u89c2\u70b9")  # "like chatting with a peer about a case: relaxed, opinionated"
ap.add_argument("--warm", default="")
ap.add_argument("--tag", default="")
ap.add_argument("--out", default=None)
ap.add_argument("--dry-run", action="store_true")
args = ap.parse_args()

H = C.project_dir(); FF = C.ffmpeg()
OUT = os.path.abspath(args.out or os.path.join(H, "voice", f"gemini_{args.voice}{args.tag}"))
secs = json.load(open(args.sections, encoding="utf-8"))["sections"]
PUNC, strip = C.PUNC, C.strip
text = (args.warm + "\n\n" if args.warm else "") + "\n\n".join(s["text"] for s in secs)  # a blank line between sections invites a natural pause
if args.dry_run:
    print(f"dry run: {len(secs)} sections, {len(strip(text))} characters, voice {args.voice}, model {args.model}, output {OUT}")
    sys.exit(0)
os.makedirs(OUT, exist_ok=True)
full = f"{OUT}/_whole.mp3"
# A take is reused only if it was made from exactly this text, voice, style and model
sig = hashlib.sha256(json.dumps([args.model, args.voice, args.style, text], ensure_ascii=False).encode()).hexdigest()
sig_file = f"{OUT}/_whole.request.sha256"
if os.path.exists(full):
    old = open(sig_file).read().strip() if os.path.exists(sig_file) else None
    if old is None:
        print(f"WARNING {full} was made by an older version and cannot be checked against sections.json; move it to the Trash if the text changed")
    elif old != sig:
        sys.exit(f"The narration text, voice, style or model changed since {full} was made. Use --tag for a new take (the old one stays "
                 f"for comparison), or move {OUT} to the Trash.")
if not os.path.exists(full):
    body = {"model": args.model, "input": [{"type": "user_input", "content": [{"type": "text", "text": text, "annotations": [{"type": "speech_metadata", "style": args.style}]}]}],
            "response_format": {"type": "audio"}, "generation_config": {"speech_config": [{"voice": args.voice}]}}
    req = urllib.request.Request("https://generativelanguage.googleapis.com/v1beta/interactions", data=json.dumps(body, ensure_ascii=False).encode(),
                                 headers={"x-goog-api-key": C.gemini_key(), "Content-Type": "application/json"})
    try: r = json.load(urllib.request.urlopen(req, timeout=600))
    except urllib.error.HTTPError as ex: sys.exit(f"HTTP {ex.code} {ex.read()[:300]}")

    def big(o):  # the audio is the only very long string in the response
        if isinstance(o, dict):
            for v in o.values():
                if isinstance(v, str) and len(v) > 1000: yield v
                else: yield from big(v)
        elif isinstance(o, list):
            for v in o: yield from big(v)
    wav = full[:-4] + ".wav"; open(wav, "wb").write(base64.b64decode(next(big(r))))
    subprocess.run([FF, "-v", "error", "-y", "-i", wav, "-b:a", "192k", full], check=True); os.remove(wav)
    open(sig_file, "w").write(sig + "\n")
print("whole narration", round(C.duration(full), 2), "s")
# Transcribe the whole take; cut between each section's last character and the next section's first, at the longest silence
W = C.transcribe(full, OUT); hc, tm = [], []
for w in W:
    cs = strip(w["text"]); n = max(len(cs), 1)
    for k, c in enumerate(cs): hc.append(c); tm.append((w["t0"] + (w["t1"] - w["t0"]) * k / n, w["t0"] + (w["t1"] - w["t0"]) * (k + 1) / n))
ref = "".join(strip(s["text"]) for s in secs); sm = difflib.SequenceMatcher(None, ref, "".join(hc), autojunk=False)
r2h = {b.a + k: b.b + k for b in sm.get_matching_blocks() for k in range(b.size)}


def near(ri, d):  # transcribed time of reference character ri (searching sideways when it did not match)
    for off in range(0, 12):
        for x in (ri - off * d, ri + off * d):
            if x in r2h: return tm[r2h[x]]
    raise SystemExit(f"character {ri} could not be matched")


r = subprocess.run([FF, "-i", full, "-af", "silencedetect=n=-38dB:d=0.12", "-f", "null", "-"], capture_output=True, text=True).stderr
sil = list(zip([float(x) for x in re.findall(r"silence_start: ([\d.]+)", r)], [float(x) for x in re.findall(r"silence_end: ([\d.]+)", r)]))
cuts, pos = [], 0
# Transcribed times lag at pauses, so the window reaches back 0.8 s
if args.warm:
    ref = strip(args.warm) + ref; sm = difflib.SequenceMatcher(None, ref, "".join(hc), autojunk=False)
    r2h = {b.a + k: b.b + k for b in sm.get_matching_blocks() for k in range(b.size)}
    pos = len(strip(args.warm)); a = near(pos - 1, -1)[1]; b = near(pos, 1)[0]
    cand = [(e - x, (x + e) / 2) for x, e in sil if x >= a - 0.8 and x <= b + 0.1 and e <= b + 0.6]
    if not cand: raise SystemExit("no silence after the warm-up sentence")
    warm_cut = max(cand)[1]
for s in secs[:-1]:
    pos += len(strip(s["text"])); a = near(pos - 1, -1)[1]; b = near(pos, 1)[0]  # this section's last character ends, the next one's first begins
    cand = [(e - x, (x + e) / 2) for x, e in sil if x >= a - 0.8 and x <= b + 0.1 and e <= b + 0.6]
    if cand: cuts.append(max(cand)[1]); continue
    # fallback: no clear silence, so cut at the quietest 20 ms between the two characters (never inside one)
    lo, hi = min(a, b) - 0.08, max(a, b) + 0.08
    raw = subprocess.run([FF, "-v", "error", "-ss", f"{lo:.3f}", "-to", f"{hi:.3f}", "-i", full, "-ac", "1", "-ar", "16000", "-f", "s16le", "-"], capture_output=True).stdout
    x = array.array("h", raw); h = 320
    en = [(sum(v * v for v in x[i:i + h]) / h, i) for i in range(0, max(len(x) - h, 1), h // 2)]
    cuts.append(lo + (min(en)[1] + h / 2) / 16000); print(f"section {s['j']} has no clear trailing silence, cut at the quietest point {cuts[-1]:.2f}s")
D = C.duration(full)
bounds = [warm_cut if args.warm else 0.0] + cuts + [D]
for n, s in enumerate(secs):
    o = f"{OUT}/sec{s['j']:02d}.mp3"
    subprocess.run([FF, "-v", "error", "-y", "-ss", f"{bounds[n]:.3f}", "-to", f"{bounds[n+1]:.3f}", "-i", full, "-b:a", "192k", o], check=True)
    json.dump(C.transcribe(o, OUT), open(f"{OUT}/sec{s['j']:02d}.words.json", "w"), ensure_ascii=False)
json.dump({"source": f"gemini_{args.voice}", "model": args.model, "style": args.style, "sections": [{"j": s["j"], "text": s["text"], "file": f"sec{s['j']:02d}.mp3"} for s in secs]},
          open(f"{OUT}/sections.json", "w"), ensure_ascii=False, indent=1)
print("ok", OUT, "cuts", [round(c, 2) for c in cuts])
