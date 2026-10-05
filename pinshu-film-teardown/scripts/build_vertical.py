#!/usr/bin/env python3
"""Vertical 9:16 edition (Douyin / WeChat Channels vertical): the horizontal film centred, a title band above,
large captions below.

How:
- The middle is the caption-free horizontal build (CLEAN_FOR_VERTICAL=1 build.py: no burned-in captions, no WeChat QR
  or account wording on the end card), over a blurred, enlarged copy of the same picture.
- Captions are not shrunk from the horizontal film; they are re-laid out large at the bottom from timeline.json.
- Safe zone (TikTok template, used as a guide for Douyin): core area roughly x 120-900, y 240-1260. Captions keep
  120/180 px side margins for the right-hand buttons. No byline: the platform shows the account name below.
- The opening title page is cut (it repeats the title band); the picture starts on the first shot.
- The picture renders silent; the horizontal final's audio is muxed in unchanged (no remix).

Usage:
  python3 build_vertical.py build <clean_horizontal.mp4>     -> vertical/index.html
  cd vertical && hyperframes render -q delivery -o renders/raw.mp4 && cd ..
  python3 build_vertical.py mux vertical/renders/raw.mp4 <horizontal_final.mp4> <vertical_final.mp4>
Spec: VERTICAL = {"kicker": "...", "title": ["line 1", "line 2"]}; an empty title list hides the title band.
"""
import html
import json
import os
import re
import shutil
import subprocess
import sys

import common as C

H = C.project_dir(); OUT = f"{H}/vertical"; E = html.escape; FF = C.ffmpeg()


def build(src):
    SPEC = C.load_spec(H); VT = getattr(SPEC, "VERTICAL", {})
    KICKER = VT.get("kicker", ""); TITLE = VT.get("title", [])
    tl = json.load(open(f"{H}/timeline.json"))
    # +0.4 s skips the first shot's 0.3 s fade so the very first frame has a picture (narration starts later)
    S0 = round(tl["SC"][0]["t"] + 0.4, 2); T = round(tl["TOTAL"] - S0, 2)
    caps = [(round(a - S0, 2), b, x) for a, b, x in tl["caps"] if a >= S0 - 0.01]
    os.makedirs(f"{OUT}/assets/fonts", exist_ok=True); os.makedirs(f"{OUT}/renders", exist_ok=True)

    def link(a, b):  # hard link: no second copy on disk; replaced if present
        if os.path.exists(b): os.remove(b)
        os.link(a, b)
    link(os.path.abspath(src), f"{OUT}/assets/clean.mp4")
    link(f"{H}/wide/assets/fonts/SourceHanSerif-VF.ttf", f"{OUT}/assets/fonts/SourceHanSerif-VF.ttf")
    shutil.copy(f"{H}/wide/hyperframes.json", f"{OUT}/hyperframes.json")
    json.dump({"start_in_horizontal": S0}, open(f"{OUT}/vertical.json", "w"))
    css = """@font-face { font-family: "SHSerif"; src: url("assets/fonts/SourceHanSerif-VF.ttf") format("truetype"); font-weight: 200 900; }
* { margin: 0; padding: 0; box-sizing: border-box; }
html, body { width: 1080px; height: 1920px; overflow: hidden; background: #0e0e0e; }
#root { position: relative; width: 1080px; height: 1920px; overflow: hidden; background: #0e0e0e; font-family: "SHSerif", serif; color: #fff; }
.vw { position: absolute; inset: 0; overflow: hidden; }
.bgv { position: absolute; left: -1166px; top: 0; width: 3413px; height: 1920px; filter: blur(46px) brightness(0.3) saturate(1.1); }
.dim { position: absolute; inset: 0; background: linear-gradient(to bottom, rgba(0,0,0,.55) 0%, rgba(0,0,0,.15) 30%, rgba(0,0,0,.15) 70%, rgba(0,0,0,.6) 100%); }
.mv { position: absolute; left: 0; top: 656px; width: 1080px; height: 608px; box-shadow: 0 20px 60px rgba(0,0,0,.55); }
.kick { position: absolute; left: 0; right: 0; top: 318px; text-align: center; }
.kick span { display: inline-block; font-size: 40px; font-weight: 800; letter-spacing: 6px; padding: 10px 26px; background: #e8322c; text-shadow: 0 1px 2px rgba(0,0,0,.35); }
.ttl { position: absolute; left: 60px; right: 60px; top: 398px; text-align: center; font-size: 86px; font-weight: 900; line-height: 1.24; letter-spacing: 4px; text-shadow: 0 6px 30px rgba(0,0,0,.6); }
.cap { position: absolute; left: 120px; right: 180px; top: 1330px; display: flex; justify-content: center; }
.cap span { display: block; text-wrap: balance; font-size: 64px; font-weight: 700; line-height: 1.36; letter-spacing: 2px; text-align: center; color: #fff; text-shadow: 0 2px 6px rgba(0,0,0,.9), 0 0 18px rgba(0,0,0,.6); }
"""
    V = (f'<div class="vw" id="bgw"><video id="bgv" class="bgv" src="assets/clean.mp4" muted playsinline data-start="0" data-duration="{T}" data-media-start="{S0}" data-track-index="1"></video></div>'
         f'<div class="dim clip" id="dim" data-start="0" data-duration="{T}" data-track-index="2"></div>'
         f'<video id="mv" class="mv" src="assets/clean.mp4" muted playsinline data-start="0" data-duration="{T}" data-media-start="{S0}" data-track-index="3"></video>')
    if KICKER: V += f'<div class="kick clip" id="kick" data-start="0" data-duration="{T}" data-track-index="10"><span>{E(KICKER)}</span></div>'
    if TITLE: V += f'<div class="ttl clip" id="ttl" data-start="0" data-duration="{T}" data-track-index="11">{"<br>".join(E(x) for x in TITLE)}</div>'
    Cp = "".join(f'<div class="cap clip" id="c{j}" data-start="{a}" data-duration="{b}" data-track-index="{20+j%2}"><span>{E(x)}</span></div>' for j, (a, b, x) in enumerate(caps))
    doc = f"""<!doctype html><html lang="zh-CN"><head><meta charset="UTF-8"/><meta name="viewport" content="width=1080, height=1920"/>
<script src="https://cdn.jsdelivr.net/npm/gsap@3.14.2/dist/gsap.min.js"></script><style>{css}</style></head><body>
<div id="root" data-composition-id="main" data-start="0" data-duration="{T}" data-width="1080" data-height="1920">
{V}{Cp}
</div><script>const tl = gsap.timeline({{ paused: true }}); tl.to("#root", {{ opacity: 1, duration: {T} }}, 0); window.__timelines["main"] = tl;</script></body></html>"""
    open(f"{OUT}/index.html", "w").write(doc)
    print("OK vertical", f"{T}s (horizontal title page {S0}s cut)", "captions", len(caps), "->", f"{OUT}/index.html")


def mux(raw, horizontal, out):
    """Put the horizontal final's audio under the silent vertical render, from the same start point; 0.15 s fade-in at the
    cut against clicks; true peak re-checked after encoding."""
    S0 = json.load(open(f"{OUT}/vertical.json"))["start_in_horizontal"]
    gain = 0.0
    for _ in range(3):
        af = "afade=t=in:d=0.15" + (f",volume={gain:.2f}dB" if gain else "")
        subprocess.run([FF, "-v", "error", "-y", "-i", raw, "-ss", str(S0), "-i", horizontal, "-map", "0:v", "-map", "1:a", "-c:v", "copy",
                        "-af", af, "-c:a", "aac", "-b:a", "192k", "-shortest", out], check=True)
        r = subprocess.run([FF, "-i", out, "-af", "ebur128=peak=true", "-f", "null", "-"], capture_output=True, text=True).stderr
        tp = float(re.findall(r"Peak:\s+(-?[\d.]+) dBFS", r)[-1]); lu = float(re.findall(r"I:\s+(-?[\d.]+) LUFS", r)[-1])
        if tp <= -1.0: break
        gain -= tp + 1.3
    print(f"OK {out}: {lu} LUFS, true peak {tp} dBTP")


if __name__ == "__main__":
    if len(sys.argv) >= 3 and sys.argv[1] == "build": build(sys.argv[2])
    elif len(sys.argv) >= 5 and sys.argv[1] == "mux": mux(*sys.argv[2:5])
    else: sys.exit(__doc__)
