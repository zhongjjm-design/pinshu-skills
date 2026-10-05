"""Shared helpers for pinshu-film-teardown scripts.

Everything machine-specific is discovered at run time (environment variables first,
then common install locations), so the skill never stores personal paths or keys.
Chinese punctuation is written as escapes so the source stays ASCII.
"""
import importlib.util
import json
import os
import shutil
import subprocess
import tempfile

SKILL_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ASSETS = os.path.join(SKILL_DIR, "assets")

# Chinese punctuation used by narration scripts.
COMMA, PERIOD, QUESTION, EXCLAIM = "\uff0c", "\u3002", "\uff1f", "\uff01"
SEMI, COLON, ENUM = "\uff1b", "\uff1a", "\u3001"
LDQ, RDQ, LCB, RCB = "\u201c", "\u201d", "\u300c", "\u300d"
PUNC = COMMA + PERIOD + QUESTION + EXCLAIM + SEMI + COLON + ENUM + LDQ + RDQ + '"' + LCB + RCB + " "
SENTENCE_END = PERIOD + QUESTION + EXCLAIM


def strip(s):
    """Drop punctuation and spaces; character positions are counted on this form."""
    return "".join(c for c in s if c not in PUNC)


def _first(*cands):
    for c in cands:
        if c and os.path.isfile(c) and os.access(c, os.X_OK):
            return c
    return None


def ffmpeg():
    """FFMPEG env var, then a full Homebrew build, then ffmpeg on PATH."""
    path = _first(os.environ.get("FFMPEG"), "/opt/homebrew/opt/ffmpeg-full/bin/ffmpeg", shutil.which("ffmpeg"))
    if not path:
        raise SystemExit("ffmpeg not found. Install it (macOS: brew install ffmpeg) or set FFMPEG=/path/to/ffmpeg.")
    return path


def ffprobe():
    path = _first(os.environ.get("FFPROBE"), shutil.which("ffprobe"))
    if not path:
        raise SystemExit("ffprobe not found. It ships with ffmpeg.")
    return path


def duration(path):
    return float(subprocess.check_output([ffprobe(), "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", path]).decode())


def baocut():
    """BaoCut CLI (Qwen3-ASR transcription). BAOCUT env var, then the BaoCut skill, then PATH."""
    return _first(os.environ.get("BAOCUT"), os.path.expanduser("~/.agents/skills/baocut/bin/baocut"), shutil.which("baocut"))


def transcription_enabled():
    return os.environ.get("PINSHU_TRANSCRIBE", "on").lower() not in ("off", "0", "no") and baocut() is not None


def transcribe(audio_path, workdir=None):
    """Transcribe Chinese audio with BaoCut; returns [{"t0", "t1", "text"}]. The .bcut project is kept next to the audio
    (or in workdir) so a rerun reuses it."""
    bc = baocut()
    if not bc:
        raise SystemExit("BaoCut CLI not found. Install the BaoCut app and skill (https://github.com/JimLiu/baocut) or set BAOCUT=/path/to/baocut.")
    workdir = workdir or os.path.dirname(os.path.abspath(audio_path))
    proj = os.path.join(workdir, os.path.splitext(os.path.basename(audio_path))[0] + ".bcut")
    tj = os.path.join(proj, "transcript.json")
    if not os.path.isfile(tj):
        if os.path.isdir(proj):
            raise SystemExit(f"Unfinished BaoCut project (no transcript.json): {proj}. Move it to the Trash and rerun.")
        r = subprocess.run([bc, "transcribe", os.path.abspath(audio_path), "--project", proj, "--model", "qwen3-asr-1.7b", "--source-lang", "zh",
                            "--json", "--yes"], capture_output=True, text=True, cwd=workdir)
        if r.returncode != 0 or not os.path.isfile(tj):
            shutil.rmtree(proj, ignore_errors=True)  # only the folder this call just created
            raise SystemExit(f"BaoCut transcription failed for {audio_path} (exit {r.returncode}): {(r.stdout + r.stderr).strip()[-600:]}")
    with open(tj, encoding="utf-8") as f:
        return [{"t0": w["t0"], "t1": w["t1"], "text": w["text"]} for w in json.load(f)["words"]]


def transcribe_clip(src, a, b):
    """Transcribe the stretch a..b seconds of src in a throwaway folder; returns the text with punctuation removed."""
    td = tempfile.mkdtemp()
    try:
        wav = os.path.join(td, "isl.wav")
        subprocess.run([ffmpeg(), "-v", "error", "-y", "-ss", f"{a:.3f}", "-to", f"{b:.3f}", "-i", src, "-ac", "1", "-ar", "16000", wav], check=True)
        return strip("".join(w["text"] for w in transcribe(wav, td)))
    finally:
        shutil.rmtree(td, ignore_errors=True)


def project_dir():
    return os.path.abspath(os.environ.get("PROJECT", os.getcwd()))


def load_spec(project=None):
    """Load the film's content spec: SPEC env var, else <project>/spec.py."""
    project = project or project_dir()
    path = os.environ.get("SPEC") or os.path.join(project, "spec.py")
    if not os.path.isfile(path):
        raise SystemExit(f"Content spec not found: {path}. Run new_project.py first, or set SPEC=/path/to/spec.py.")
    sp = importlib.util.spec_from_file_location("spec", path)
    mod = importlib.util.module_from_spec(sp)
    sp.loader.exec_module(mod)
    return mod


def gemini_key():
    """GEMINI_API_KEY env var, else GEMINI_API_KEY= line in ~/.config/gemini/.env. The key is never written anywhere."""
    if os.environ.get("GEMINI_API_KEY"):
        return os.environ["GEMINI_API_KEY"]
    env = os.path.expanduser("~/.config/gemini/.env")
    if os.path.isfile(env):
        for line in open(env, encoding="utf-8"):
            if line.startswith("GEMINI_API_KEY="):
                return line.split("=", 1)[1].strip()
    raise SystemExit("Gemini API key not found. Set GEMINI_API_KEY or put GEMINI_API_KEY=... in ~/.config/gemini/.env.")
