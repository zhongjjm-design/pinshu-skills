#!/usr/bin/env python3
"""Render a HyperFrames composition reliably.

Long films with many video clips can crash the renderer when memory is short ("Target closed", "Navigating frame was
detached"), and a failed render can still exit 0 - a later mix step would then silently reuse an OLD render. This script
uses the low-memory profile, retries, and only succeeds when the output is newer than index.html and has the expected
number of frames.
Usage: python3 render.py <composition dir, e.g. wide or vertical> <output.mp4> [--tries 3] [--workers auto]
"""
import argparse
import json
import os
import re
import shutil
import subprocess
import sys

import common as C

ap = argparse.ArgumentParser()
ap.add_argument("comp"); ap.add_argument("out")
ap.add_argument("--tries", type=int, default=3)
ap.add_argument("--workers", default=None, help="parallel workers; default is the low-memory single-worker profile")
ap.add_argument("--force", action="store_true", help="render even when check reports missing files")
args = ap.parse_args()
hf = os.environ.get("HYPERFRAMES") or shutil.which("hyperframes")
if not hf: sys.exit("hyperframes CLI not found: npm install -g hyperframes")
comp = os.path.abspath(args.comp); out = os.path.abspath(args.out); os.makedirs(os.path.dirname(out), exist_ok=True)
index = os.path.join(comp, "index.html")
total = float(re.search(r'data-composition-id="main" data-start="0" data-duration="([\d.]+)"', open(index).read()).group(1))
chk = subprocess.run([hf, "check"], cwd=comp, capture_output=True, text=True); text = chk.stdout + chk.stderr
if "Check passed" not in text:
    errs = [l.strip() for l in text.splitlines() if "\u2717" in l or "error" in l.lower() and "0 error" not in l.lower()]
    print("hyperframes check did not pass:"); [print("  ", e[:300]) for e in errs[:12]]
    if "missing_local_asset" in text and not args.force:
        sys.exit("stopped: the composition references files that do not exist (the renderer would silently leave them out). Add them or pass --force.")
    print("WARNING rendering anyway")
cmd = [hf, "render", "-q", "delivery", "-o", out] + (["-w", args.workers] if args.workers else ["--low-memory-mode"])
log = out + ".render.log"
for n in range(1, args.tries + 1):
    with open(log, "w") as lf:
        subprocess.run(cmd, cwd=comp, stdout=lf, stderr=subprocess.STDOUT)
    if os.path.exists(out) and os.path.getmtime(out) > os.path.getmtime(index):
        frames = int(subprocess.check_output([C.ffprobe(), "-v", "error", "-count_packets", "-select_streams", "v:0", "-show_entries", "stream=nb_read_packets", "-of", "csv=p=0", out]).decode().strip())
        if abs(frames - round(total * 30)) <= 2:
            os.remove(log); print(f"OK {out}: {frames} frames ({total}s)"); sys.exit(0)
        print(f"attempt {n}: output has {frames} frames, expected {round(total * 30)}")
    else:
        stage = re.findall(r'"failedStage":"([^"]*)"', open(log).read())
        print(f"attempt {n} failed{': ' + stage[-1] if stage else ''} (log: {log}). Close memory-hungry apps if this repeats.")
sys.exit(f"render failed after {args.tries} attempts; the previous output (if any) is stale - do not mix it")
