#!/usr/bin/env python3
"""Offline end-to-end self-test with synthetic material: no network, no API keys, no transcription.

Builds a throwaway project (synthetic film, tone "narration" with per-character timings, one speaker bite), then runs
build.py (normal and caption-free), build_vertical.py, mix.py, qc.py and gen_voice.py --dry-run, and checks the outputs.
Needs ffmpeg/ffprobe and the Python modules numpy, soundfile and pillow. Rendering (HyperFrames) is not exercised.
Usage: python3 tests/self_test.py
"""
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile

import numpy as np
import soundfile as sf

HERE = os.path.dirname(os.path.abspath(__file__)); SCRIPTS = os.path.join(os.path.dirname(HERE), "scripts")
sys.path.insert(0, SCRIPTS)
import common as C  # noqa: E402

FF = C.ffmpeg(); SR = 44100
failures = []


def check(cond, msg):
    print(("  ok   " if cond else "  FAIL ") + msg)
    if not cond: failures.append(msg)


def run(args, env=None, expect_ok=True):
    r = subprocess.run([sys.executable] + args, cwd=P, capture_output=True, text=True, env={**os.environ, **(env or {})})
    if expect_ok and r.returncode != 0: print(r.stdout[-2000:], r.stderr[-3000:])
    return r


def cjk(seed, n):  # arbitrary CJK characters, never punctuation
    return "".join(chr(0x4E00 + (seed * 131 + i * 17) % 3000) for i in range(n))


def speak(text, path_audio, path_words, lead=0.3, tail=0.5, stray_pause_after=None):
    """Tone-per-character 'voice': 0.18 s tone per character, silence after punctuation; returns nothing."""
    parts, words, t = [np.zeros(int(lead * SR))], [], lead
    for k, ch in enumerate(text):
        if ch in C.PUNC:
            gap = 0.6 if ch in C.SENTENCE_END else 0.35
            parts.append(np.zeros(int(gap * SR))); t += gap; continue
        tone = 0.3 * np.sin(2 * np.pi * (180 + 7 * (k % 9)) * np.arange(int(0.18 * SR)) / SR)
        parts.append(tone); words.append({"t0": round(t, 3), "t1": round(t + 0.18, 3), "text": ch}); t += 0.18
        if stray_pause_after is not None and len(words) == stray_pause_after:  # a mid-sentence pause to exercise tightening
            parts.append(np.zeros(int(0.5 * SR))); t += 0.5
    parts.append(np.zeros(int(tail * SR)))
    wav = path_audio if path_audio.endswith(".wav") else path_audio[:-4] + ".tmp.wav"
    sf.write(wav, np.concatenate(parts).astype(np.float32), SR)
    if wav != path_audio:
        subprocess.run([FF, "-v", "error", "-y", "-i", wav, "-b:a", "192k", path_audio], check=True); os.remove(wav)
    json.dump(words, open(path_words, "w"))


P = tempfile.mkdtemp(prefix="pinshu_film_teardown_test_")
try:
    print("project", P)
    film = os.path.join(P, "film_src.mp4")
    subprocess.run([FF, "-v", "error", "-y", "-f", "lavfi", "-i", "testsrc2=size=1920x1080:rate=30:duration=60", "-f", "lavfi", "-i", "sine=frequency=220:duration=60",
                    "-c:v", "libx264", "-preset", "ultrafast", "-pix_fmt", "yuv420p", "-c:a", "aac", "-shortest", film], check=True)
    font = os.path.join(P, "dummy_font.ttf"); open(font, "wb").write(b"\0")
    r = run([os.path.join(SCRIPTS, "new_project.py"), P, "--film", film, "--serif-font", font])
    check(r.returncode == 0 and os.path.isfile(f"{P}/wide/assets/tvc.mp4") and os.path.isfile(f"{P}/spec.py"), "new_project.py creates the project")

    # Narration: three sections; scene texts concatenate to section texts
    A = cjk(1, 6) + C.COMMA + cjk(2, 6) + C.PERIOD
    B1 = cjk(3, 5) + C.COMMA + cjk(4, 7) + C.PERIOD
    B2 = cjk(5, 4) + C.ENUM + cjk(6, 4) + C.COMMA + cjk(7, 6) + C.PERIOD
    S1 = cjk(8, 8) + C.QUESTION + cjk(9, 6) + C.PERIOD
    S2 = cjk(10, 5) + C.COMMA + cjk(11, 9) + C.PERIOD
    sections = [{"j": 0, "text": A}, {"j": 1, "text": B1 + B2}, {"j": 2, "text": S1 + S2}]
    json.dump({"sections": sections}, open(f"{P}/sections.json", "w"))
    VS = f"{P}/voice/test"; os.makedirs(VS, exist_ok=True)
    for s in sections:
        speak(s["text"], f"{VS}/sec{s['j']:02d}.mp3", f"{VS}/sec{s['j']:02d}.words.json", stray_pause_after=9 if s["j"] == 1 else None)
    json.dump({"source": "test", "sections": [{**s, "file": f"sec{s['j']:02d}.mp3"} for s in sections]}, open(f"{VS}/sections.json", "w"))
    BT = cjk(12, 3) + C.COMMA + cjk(13, 4) + C.PERIOD
    speak(BT, f"{P}/voice/bites/bite1.wav", f"{P}/voice/bites/bite1.words.json")
    json.dump({"bite1": 20.0}, open(f"{P}/voice/bites/bites.json", "w"))

    spec = f'''
VO_SRC = "voice/test"
S = [
    ("full", {A!r}, {{"src": 0.0, "over": "label", "clips": [1.0, {{"src": 5.0, "at": {A[7:10]!r}}}]}}),
    ("chapter", {B1!r}, {{"src": 10.0, "no": "01", "t1": "t1", "t2": "t2"}}),
    ("chips", {B2!r}, {{"src": 12.0, "head": "head", "items": [("x", {B2[0:2]!r}), ("y", {B2[5:7]!r})]}}),
    ("story", {S1!r}, {{"src": 25.0, "n": "1", "tag": "tag", "bite": "bite1", "clips": [{{"src": 30.0, "at": {S1[9:12]!r}, "hideover": True}}]}}),
    ("full", {S2!r}, {{"src": 40.0, "clips": [40.0, {{"src": 50.0, "at": {S2[6:9]!r}, "card": True}}]}}),
    ("end", "", {{}}),
]
BITE_TEXT = {{"bite1": {BT!r}}}
SPLITS = [({S1[:3]!r}, 0.3)]
SEC_TAIL = {{0: 0.8}}
TITLE = {{"d": 3.0, "src": 2.0, "t1": "a", "t2": "b", "sub": "sub", "by": "by"}}
END = {{"kicker": "k", "title_html": "t", "author": "a", "author_clean": "ac", "qr": "qr.jpg", "qr_text": "q"}}
VERTICAL = {{"kicker": "k", "title": ["l1", "l2"]}}
'''
    open(f"{P}/spec.py", "w").write(spec)

    env = {"PINSHU_TRANSCRIBE": "off"}
    r = run([os.path.join(SCRIPTS, "build.py")], env)
    check(r.returncode == 0 and "OK total=" in r.stdout, "build.py builds the horizontal composition")
    tl = json.load(open(f"{P}/timeline.json")); html = open(f"{P}/wide/index.html").read()
    check(len(tl["SC"]) == 6 and tl["TOTAL"] > 20, f"timeline has 6 scenes and a plausible length ({tl['TOTAL']} s)")
    check(len(tl["caps"]) >= 8 and all(b >= 0.3 for _, b, _ in tl["caps"]), f"{len(tl['caps'])} captions, none shorter than 0.3 s")
    check(all(tl["caps"][n][0] + tl["caps"][n][1] <= tl["caps"][n + 1][0] + 1e-6 for n in range(len(tl["caps"]) - 1)), "captions do not overlap")
    check(any(x.startswith(C.LDQ) for _, _, x in tl["caps"]), "speaker bite captions are quoted")
    check('id="vo0"' in html and 'id="bt3"' in html and "assets/voice/sec02.wav" in html, "voice and bite audio are placed")
    check(html.count('class="cap clip"') == len(tl["caps"]) and 'id="er"' in html, "captions and the end-card QR are rendered")
    story = tl["SC"][3]; check(story.get("bite_t") is not None and story.get("overlayOff") is not None, "story scene: bite timing and number hidden for the hideover clip")
    check(any(c.get("card") for c in tl["SC"][4]["cl"]), "original title card clip keeps its card flag")
    check("before" in r.stdout and "could not verify" in r.stdout, "pause added at SPLITS and the unverifiable mid-sentence pause left alone")
    check(re.search(r"[\u4e00-\u9fff]", open(f"{C.ASSETS}/wide.js").read()) is None, "engine template stays ASCII")

    # Rejection tests: a spec that drops narration, or cues a word the scene never says, must stop the build
    good = spec
    dropped = good.replace(f'    ("full", {S2!r}, {{"src": 40.0, "clips": [40.0, {{"src": 50.0, "at": {S2[6:9]!r}, "card": True}}]}}),\n', "")
    check(dropped != good, "rejection test removes the last narrated scene")
    open(f"{P}/spec.py", "w").write(dropped)
    r = run([os.path.join(SCRIPTS, "build.py")], env, expect_ok=False)
    check(r.returncode != 0 and "not fully covered" in (r.stdout + r.stderr), "build.py refuses a scene list that leaves narration out")
    open(f"{P}/spec.py", "w").write(good.replace(f'"at": {A[7:10]!r}', '"at": "' + cjk(99, 3) + '"'))
    r = run([os.path.join(SCRIPTS, "build.py")], env, expect_ok=False)
    check(r.returncode != 0 and "cue word" in (r.stdout + r.stderr), "build.py names a cue word that the scene never says")
    open(f"{P}/spec.py", "w").write(good + 'FRAME = {"zoom": (1.0, 1.05), "origin": "50% 50%", "subband_top": None}\n')
    r = run([os.path.join(SCRIPTS, "build.py")], env)
    fh = open(f"{P}/wide/index.html").read()
    check(r.returncode == 0 and 'class="subband' not in fh and "scale: 1.05" in fh and '"50% 50%" : "50% 50%"' in fh, "spec.FRAME sets the film's scaling and turns off the subtitle strip")
    open(f"{P}/spec.py", "w").write(good)
    r = run([os.path.join(SCRIPTS, "build.py")], env)
    check('class="subband' in open(f"{P}/wide/index.html").read() and "top: 878px" in open(f"{P}/wide/index.html").read(), "default framing keeps the pilot film's subtitle strip")

    r = run([os.path.join(SCRIPTS, "build.py")], {**env, "CLEAN_FOR_VERTICAL": "1"})
    clean_html = open(f"{P}/wide/index.html").read()
    check(r.returncode == 0 and 'class="cap clip"' not in clean_html and 'id="er"' not in clean_html, "caption-free build has no captions and no QR")
    run([os.path.join(SCRIPTS, "build.py")], env)  # restore the normal build

    # Fake renders: picture of the right length, audio = processed narration
    T = tl["TOTAL"]; raw = f"{P}/wide/renders/raw.mp4"
    subprocess.run([FF, "-v", "error", "-y", "-f", "lavfi", "-i", f"testsrc2=size=1920x1080:rate=30:duration={T}", "-f", "lavfi", "-i", f"sine=frequency=200:duration={T}",
                    "-filter_complex", "[1:a]volume=-14dB[a]", "-map", "0:v", "-map", "[a]", "-c:v", "libx264", "-preset", "ultrafast", "-pix_fmt", "yuv420p", "-c:a", "aac", raw], check=True)
    music = f"{P}/wide/assets/bgm/test.wav"
    sf.write(music, (0.2 * np.sin(2 * np.pi * 330 * np.arange(int((T + 3) * SR)) / SR)).astype(np.float32), SR)
    final = f"{P}/wide/renders/final.mp4"
    r = run([os.path.join(SCRIPTS, "mix.py"), raw, music, final, "soft"], {"MIX_NO_FADEOUT": "1"})
    check(r.returncode == 0 and os.path.isfile(final), "mix.py mixes the music under the narration")
    peak = subprocess.run([FF, "-i", final, "-af", "ebur128=peak=true", "-f", "null", "-"], capture_output=True, text=True).stderr
    tp = float(re.findall(r"Peak:\s+(-?[\d.]+) dBFS", peak)[-1]); check(tp <= -1.0, f"true peak after mixing {tp} dBTP <= -1")

    r = run([os.path.join(SCRIPTS, "qc.py"), final, f"{P}/timeline.json", f"{P}/qc", raw], env, expect_ok=False)
    rep = json.load(open(f"{P}/qc/qc_report.json")) if os.path.isfile(f"{P}/qc/qc_report.json") else {}
    if not rep: print(r.stdout[-1500:], r.stderr[-3000:])
    check(r.returncode in (0, 1) and {"duration_diff", "true_peak_dbtp", "frozen_over_2s", "problems"} <= set(rep) and os.path.isfile(f"{P}/qc/phone_size.jpg"),
          "qc.py writes its report and contact sheets")
    check(abs(rep.get("duration_diff", 9)) <= 0.2, "qc.py duration check agrees with the timeline")

    r = run([os.path.join(SCRIPTS, "build_vertical.py"), "build", final])
    vh = open(f"{P}/vertical/index.html").read() if os.path.isfile(f"{P}/vertical/index.html") else ""
    check(r.returncode == 0 and 'class="cap clip"' in vh and 'id="ttl"' in vh, "build_vertical.py lays out the vertical edition")

    r = run([os.path.join(SCRIPTS, "gen_voice.py"), f"{P}/sections.json", "--dry-run"])
    check(r.returncode == 0 and "dry run: 3 sections" in r.stdout, "gen_voice.py dry run reads the sections")
finally:
    if os.environ.get("PINSHU_KEEP_TEST_PROJECT"): print("kept", P)  # for a manual render check
    else: shutil.rmtree(P, ignore_errors=True)
print("SELF-TEST PASS" if not failures else f"SELF-TEST FAIL: {len(failures)} check(s)")
sys.exit(1 if failures else 0)
