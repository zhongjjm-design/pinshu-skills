#!/usr/bin/env python3
"""Offline self-test for pinshu-video-core with synthetic material: no network, no API keys, no real transcription,
no real rendering.

Covers: common helpers; gen_voice.py (dry run, and the guard that refuses to overwrite a paid take made from different
text); patch_voice.py (local slow-down and pause, with a stand-in BaoCut); mix.py (soft and plain); render.py (with a
stand-in HyperFrames CLI: a good render passes, a wrong frame count fails); qc.py on a minimal timeline.json;
fit_music.py on a synthetic track; doctor.py (machine check, and a video-type skill's project hook).
Needs ffmpeg/ffprobe and the Python modules numpy, soundfile and pillow; librosa for patch_voice and fit_music
(those two are skipped without it). A dummy GEMINI_API_KEY is set so no test can ever spend money.
Usage: python3 tests/self_test.py
"""
import importlib.util
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

FF = C.ffmpeg(); SR = 44100; PY = sys.executable
HAS_LIBROSA = importlib.util.find_spec("librosa") is not None
SAFE_ENV = {"GEMINI_API_KEY": "offline-self-test-not-a-key", "PINSHU_TRANSCRIBE": "off"}
failures = []


def check(cond, msg):
    print(("  ok   " if cond else "  FAIL ") + msg)
    if not cond: failures.append(msg)


def run(script, args, cwd, env=None):
    r = subprocess.run([PY, os.path.join(SCRIPTS, script)] + args, cwd=cwd, capture_output=True, text=True, env={**os.environ, **SAFE_ENV, **(env or {})})
    return r, r.stdout + r.stderr


def write_audio(path, y, sr=SR):
    """float array (mono, or channels x samples) -> wav, or mp3 through a temporary wav."""
    data = y.T if y.ndim == 2 else y
    if path.endswith(".wav"): sf.write(path, data.astype(np.float32), sr); return
    tmp = path[:-4] + ".tmp.wav"; sf.write(tmp, data.astype(np.float32), sr)
    subprocess.run([FF, "-v", "error", "-y", "-i", tmp, "-b:a", "192k", path], check=True); os.remove(tmp)


def tone(secs, freq=220.0, amp=0.3):
    return amp * np.sin(2 * np.pi * freq * np.arange(int(secs * SR)) / SR)


def fake_cli(path, body):
    open(path, "w").write(f"#!{PY}\n" + body); os.chmod(path, 0o755); return path


P = tempfile.mkdtemp(prefix="pinshu_video_core_test_")
try:
    print("project", P)
    # ---------- common ----------
    check(C.strip("a" + C.COMMA + "b" + C.PERIOD + " c" + C.LDQ + "d" + C.RDQ) == "abcd", "strip drops Chinese punctuation and spaces")
    check(not hasattr(C, "ASSETS") and not hasattr(C, "SKILL_DIR"), "core helpers define no asset folder (each video-type skill owns its own)")
    open(f"{P}/spec.py", "w").write("X = 7\n")
    check(C.load_spec(P).X == 7, "load_spec reads <project>/spec.py")
    write_audio(f"{P}/t.wav", tone(1.5)); check(abs(C.duration(f"{P}/t.wav") - 1.5) < 0.01, "duration reads the length with ffprobe")
    old = os.environ.get("PINSHU_TRANSCRIBE"); os.environ["PINSHU_TRANSCRIBE"] = "off"
    check(not C.transcription_enabled(), "PINSHU_TRANSCRIBE=off turns transcription off")
    if old is None: os.environ.pop("PINSHU_TRANSCRIBE")
    else: os.environ["PINSHU_TRANSCRIBE"] = old

    # ---------- gen_voice.py: dry run, and the paid-take guard ----------
    secs = [{"j": 0, "text": "\u4e00\u4e8c\u4e09" + C.PERIOD}, {"j": 1, "text": "\u56db\u4e94\u516d" + C.PERIOD}]
    json.dump({"sections": secs}, open(f"{P}/sections.json", "w"), ensure_ascii=False)
    r, out = run("gen_voice.py", [f"{P}/sections.json", "--dry-run"], P)
    check(r.returncode == 0 and "dry run: 2 sections" in out, "gen_voice.py dry run reads the sections")
    VO = f"{P}/voice/gemini_Charon"; os.makedirs(VO)
    write_audio(f"{VO}/_whole.mp3", tone(1.0)); open(f"{VO}/_whole.request.sha256", "w").write("0" * 64 + "\n")
    r, out = run("gen_voice.py", [f"{P}/sections.json"], P)
    check(r.returncode != 0 and "changed since" in out, "gen_voice.py refuses to reuse a take made from different text (no API call)")

    # ---------- patch_voice.py with a stand-in BaoCut ----------
    if HAS_LIBROSA:
        bc = fake_cli(f"{P}/fake_baocut", 'import json, os, sys\na = sys.argv\nproj = a[a.index("--project") + 1]\nos.makedirs(proj, exist_ok=True)\n'
                                         'json.dump({"words": [{"t0": 0.1, "t1": 0.5, "text": "x"}]}, open(os.path.join(proj, "transcript.json"), "w"))\n')
        PV = f"{P}/pv"; os.makedirs(f"{PV}/voice/a")
        write_audio(f"{PV}/voice/a/sec00.mp3", tone(3.0)); src_bytes = open(f"{PV}/voice/a/sec00.mp3", "rb").read()
        open(f"{PV}/spec.py", "w").write('PATCH = {"src": "voice/a", "dst": "voice/b", "ops": {0: [(1.0, 1.5, 1.2), (2.0, 2.0, ("pause", 0.1))]}}\n')
        r, out = run("patch_voice.py", [], PV, {"BAOCUT": bc})
        grow = C.duration(f"{PV}/voice/b/sec00.mp3") - C.duration(f"{PV}/voice/a/sec00.mp3") if os.path.isfile(f"{PV}/voice/b/sec00.mp3") else -1
        check(r.returncode == 0 and abs(grow - 0.2) < 0.08 and os.path.isfile(f"{PV}/voice/b/sec00.words.json"),
              f"patch_voice.py slows 0.5 s by 1.2x and adds a 0.1 s pause (+{grow:.2f} s, expected about +0.2)")
        check(open(f"{PV}/voice/a/sec00.mp3", "rb").read() == src_bytes, "patch_voice.py leaves the source take untouched")
    else:
        print("  skip patch_voice.py (librosa missing)")

    # ---------- mix.py ----------
    T = 12.0; raw = f"{P}/raw.mp4"
    subprocess.run([FF, "-v", "error", "-y", "-f", "lavfi", "-i", f"testsrc2=size=640x360:rate=30:duration={T}", "-f", "lavfi", "-i", f"sine=frequency=200:duration={T}",
                    "-filter_complex", "[1:a]volume=-14dB[a]", "-map", "0:v", "-map", "[a]", "-c:v", "libx264", "-preset", "ultrafast", "-pix_fmt", "yuv420p", "-c:a", "aac", raw], check=True)
    write_audio(f"{P}/music.wav", tone(T + 3, 330.0, 0.2))
    tpk = lambda f: float(re.findall(r"Peak:\s+(-?[\d.]+) dBFS", subprocess.run([FF, "-i", f, "-af", "ebur128=peak=true", "-f", "null", "-"], capture_output=True, text=True).stderr)[-1])
    final = f"{P}/final.mp4"
    r, out = run("mix.py", [raw, f"{P}/music.wav", final, "soft"], P, {"MIX_NO_FADEOUT": "1"})
    check(r.returncode == 0 and os.path.isfile(final) and tpk(final) <= -1.0, "mix.py soft: music under the narration, true peak at or below -1 dBTP")
    r, out = run("mix.py", [raw, f"{P}/music.wav", f"{P}/final_plain.mp4"], P)
    check(r.returncode == 0 and os.path.isfile(f"{P}/final_plain.mp4") and tpk(f"{P}/final_plain.mp4") <= -1.0, "mix.py plain mode also keeps the true peak at or below -1 dBTP")

    # ---------- render.py with a stand-in HyperFrames CLI ----------
    comp = f"{P}/comp"; os.makedirs(comp)
    open(f"{comp}/index.html", "w").write('<div id="root" data-composition-id="main" data-start="0" data-duration="2.0" data-width="320" data-height="180"></div>')
    hf = fake_cli(f"{P}/fake_hyperframes", 'import os, subprocess, sys\na = sys.argv[1:]\nif a[0] == "check": print("Check passed"); sys.exit(0)\n'
                                           'out = a[a.index("-o") + 1]; secs = os.environ.get("FAKE_HF_SECONDS", "2.0")\n'
                                           f'subprocess.run([{FF!r}, "-v", "error", "-y", "-f", "lavfi", "-i", f"testsrc2=size=320x180:rate=30:duration={{secs}}", '
                                           '"-c:v", "libx264", "-preset", "ultrafast", "-pix_fmt", "yuv420p", out], check=True)\n')
    r, out = run("render.py", [comp, f"{P}/render_ok.mp4"], P, {"HYPERFRAMES": hf})
    check(r.returncode == 0 and "OK" in out and "60 frames" in out, "render.py accepts a render with the expected frame count")
    r, out = run("render.py", [comp, f"{P}/render_short.mp4", "--tries", "1"], P, {"HYPERFRAMES": hf, "FAKE_HF_SECONDS": "1.0"})
    check(r.returncode != 0 and "expected 60" in out and "render failed" in out, "render.py fails a render with the wrong frame count")

    # ---------- qc.py on a minimal timeline.json ----------
    tl = {"TOTAL": T, "SC": [{"i": 0, "k": "full", "t": 0.0, "d": 5.0}, {"i": 1, "k": "full", "t": 5.0, "d": 3.0}, {"i": 2, "k": "end", "t": 8.0, "d": 4.0}],
          "caps": [[0.5, 2.0, "a"], [3.0, 1.5, "b"]], "narr": ["a"]}
    json.dump(tl, open(f"{P}/timeline.json", "w"))
    r, out = run("qc.py", [final, f"{P}/timeline.json", f"{P}/qc", raw], P)
    rep = json.load(open(f"{P}/qc/qc_report.json")) if os.path.isfile(f"{P}/qc/qc_report.json") else {}
    check(r.returncode == 0 and "QC PASS" in out and abs(rep.get("duration_diff", 9)) <= 0.2 and os.path.isfile(f"{P}/qc/phone_size.jpg"),
          "qc.py passes a clean synthetic film and writes its report and contact sheets")

    # ---------- fit_music.py on a synthetic track ----------
    if HAS_LIBROSA:
        FM = f"{P}/fm"; os.makedirs(f"{FM}/wide/assets/bgm"); os.makedirs(f"{FM}/wide/assets/voice")
        t = np.arange(int(40 * SR)) / SR; chords = [(220, 277), (247, 311), (196, 247), (165, 208)]  # four 2 s chords, repeating every 8 s
        f1 = np.choose((t // 2 % 4).astype(int), [c[0] for c in chords]); f2 = np.choose((t // 2 % 4).astype(int), [c[1] for c in chords])
        mono = 0.15 * (np.sin(2 * np.pi * f1 * t) + np.sin(2 * np.pi * f2 * t)); write_audio(f"{FM}/wide/assets/bgm/track.wav", np.stack([mono, mono]))
        write_audio(f"{FM}/wide/assets/voice/sec01.wav", np.concatenate([tone(20.0), np.zeros(SR)]))
        open(f"{FM}/wide/index.html", "w").write('<audio id="vo0" src="assets/voice/sec00.wav" data-start="0.6"></audio><audio id="vo1" src="assets/voice/sec01.wav" data-start="12.8"></audio>')
        json.dump({"TOTAL": 51.1, "SC": [{"i": 0, "k": "full", "t": 0.0, "d": 10.0, "vo": 0.6}, {"i": 1, "k": "chapter", "t": 10.0, "d": 34.1, "vo": 12.8},
                                         {"i": 2, "k": "end", "t": 44.1, "d": 7.0, "vo": 44.1}], "caps": [], "narr": []}, open(f"{FM}/timeline.json", "w"))
        open(f"{FM}/spec.py", "w").write('BGM = {"file": "track.wav", "loop": (20.0, 12.0), "cadence": (28.0, 30.0)}\n')
        r, out = run("fit_music.py", [], FM)
        fit = f"{FM}/wide/assets/bgm/track_fit.wav"
        check(r.returncode == 0 and "2 seams" in out and os.path.isfile(fit) and abs(sf.info(fit).duration - 53.1) < 0.05,
              "fit_music.py loops the track so its ending lands on the end card (2 seams, film length plus 2 s padding)")
        if r.returncode != 0: print(out[-2000:])
    else:
        print("  skip fit_music.py (librosa missing)")

    # ---------- doctor.py ----------
    r, out = run("doctor.py", [], P)
    check(r.returncode in (0, 1) and "  ok   python" in out and ("READY" in out), "doctor.py checks the machine")
    r, out = run("doctor.py", [P], P)
    check("content spec" in out, "doctor.py with a project checks the content spec")
    hook = f"{P}/type_doctor.py"
    open(hook, "w").write("import importlib.util, os\nsp = importlib.util.spec_from_file_location('core_doctor', os.environ['CORE_DOCTOR'])\n"
                          "m = importlib.util.module_from_spec(sp); sp.loader.exec_module(m)\n"
                          "m.main(lambda P, ok, warn, bad: bad.append('project custom.file missing (type skill check)'))\n")
    r = subprocess.run([PY, hook, P], cwd=P, capture_output=True, text=True, env={**os.environ, **SAFE_ENV, "CORE_DOCTOR": os.path.join(SCRIPTS, "doctor.py")})
    check(r.returncode == 1 and "FAIL project custom.file missing (type skill check)" in r.stdout, "doctor.main(project_checks) lets a video-type skill add its own project files")

finally:
    if os.environ.get("PINSHU_KEEP_TEST_PROJECT"): print("kept", P)
    else: shutil.rmtree(P, ignore_errors=True)
print("SELF-TEST PASS" if not failures else f"SELF-TEST FAIL: {len(failures)} check(s)")
sys.exit(1 if failures else 0)
