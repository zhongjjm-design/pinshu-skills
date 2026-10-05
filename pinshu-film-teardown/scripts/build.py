#!/usr/bin/env python3
"""Build the horizontal (16:9) brand-film teardown composition from a project's content spec.

A film = project folder (footage, voice) + spec.py (what this film says) + this engine (how it is made).
Usage: cd <project> && python3 build.py   (or PROJECT=<project> SPEC=<spec.py> python3 build.py)

What it does:
1. Narration is synthesized per topic section (gen_voice.py), then cut into scenes by real per-character
   pronunciation times; leading and trailing silence is trimmed.
2. Captions, cuts, label pops and inserts are anchored to the moment a word is actually spoken, never estimated.
3. Speaker bites from the original film play over the speaker's own shot; captions show their exact words.
4. Pauses are added only inside measured silences (spec SPLITS). A mid-sentence pause is shortened only after a
   separate transcription of the audio just before it proves it is not a punctuation pause. Each sentence is levelled.
Environment: VO_SRC overrides the voice source folder; CLEAN_FOR_VERTICAL=1 builds the caption-free version used
inside the vertical edition; PINSHU_TRANSCRIBE=off skips transcription-based checks.
"""
import difflib
import html
import json
import os
import re
import shutil
import subprocess

import common as C

H = C.project_dir(); PJ = f"{H}/wide"
SPEC = C.load_spec(H)
FF = C.ffmpeg(); E = html.escape; dur = C.duration
VO_SRC = os.path.join(H, os.environ.get("VO_SRC", SPEC.VO_SRC))
BITES = os.path.join(H, getattr(SPEC, "BITES_DIR", "voice/bites"))
OVS = getattr(SPEC, "OUT_VOICE_SUBDIR", "voice"); OUTVO = f"{PJ}/assets/{OVS}"  # processed voice goes to wide/assets/<OVS>
os.makedirs(OUTVO, exist_ok=True)
PUNC = C.PUNC; strip = C.strip
# Caption-free build for the vertical edition: no burned-in captions, no WeChat QR or account wording on the end card
# (Douyin forbids traffic to WeChat).
CLEAN = bool(os.environ.get("CLEAN_FOR_VERTICAL"))

S = SPEC.S  # (kind, narration, params); see references/spec-format.md
BITE_TEXT = getattr(SPEC, "BITE_TEXT", {})
BITE_SRC = json.load(open(f"{BITES}/bites.json")) if BITE_TEXT else {}


# ---------- Per-character times: map each character of the reference text to transcribed pronunciation times ----------
def char_times(ref, words):
    hc, tm = [], []
    for w in words:
        cs = strip(w["text"]); n = max(len(cs), 1)
        for k, c in enumerate(cs):
            a = w["t0"] + (w["t1"] - w["t0"]) * k / n; b = w["t0"] + (w["t1"] - w["t0"]) * (k + 1) / n
            hc.append(c); tm.append((a, b))
    r = strip(ref); sm = difflib.SequenceMatcher(None, r, "".join(hc), autojunk=False)
    T = [None] * len(r)
    for bl in sm.get_matching_blocks():
        for k in range(bl.size): T[bl.a + k] = tm[bl.b + k]
    known = [i for i, x in enumerate(T) if x]
    for i in range(len(r)):  # unmatched characters: interpolate between the nearest known neighbours
        if T[i]: continue
        L = max([k for k in known if k < i], default=None); R = min([k for k in known if k > i], default=None)
        if L is None: T[i] = (T[R][0] - 0.15 * (R - i), T[R][0] - 0.15 * (R - i - 1))
        elif R is None: T[i] = (T[L][1] + 0.15 * (i - L - 1), T[L][1] + 0.15 * (i - L))
        else:
            f0, f1 = (i - L) / (R - L), (i - L + 1) / (R - L)
            T[i] = (T[L][1] + (T[R][0] - T[L][1]) * f0, T[L][1] + (T[R][0] - T[L][1]) * f1)
    return T


def sidx(text, pos):  # position in raw text -> position in punctuation-free text
    return len(strip(text[:pos]))


secs = json.load(open(f"{VO_SRC}/sections.json"))["sections"]
for sc in secs:
    sc["T"] = char_times(sc["text"], json.load(open(f"{VO_SRC}/sec{sc['j']:02d}.words.json")))
    sc["dur"] = dur(f"{VO_SRC}/sec{sc['j']:02d}.mp3"); sc["pos"] = 0

# ---------- Voice: a topic section plays continuously; pauses are added only inside measured silences ----------
# (cutting at transcribed times lands inside words: transcription lags one or two characters at pauses)
SPLITS = getattr(SPEC, "SPLITS", [])
SEC_TAIL = getattr(SPEC, "SEC_TAIL", {})  # air after a section ends (longer at topic changes); default 0.4 s


def silences(f, db=-38):
    r = subprocess.run([FF, "-i", f, "-af", f"silencedetect=n={db}dB:d=0.08", "-f", "null", "-"], capture_output=True, text=True).stderr
    st = [float(x) for x in re.findall(r"silence_start: (-?[\d.]+)", r)]; en = [float(x) for x in re.findall(r"silence_end: ([\d.]+)", r)]
    return [(a, en[k] if k < len(en) else dur(f)) for k, a in enumerate(st)]


SPLIT_LOG = []
# Transcribe a short stretch on its own to learn which characters were really spoken there.
# Results are cached per file|start|end in the voice source folder, so rebuilds do not re-transcribe.
ISL_F = f"{VO_SRC}/_island_cache.json"
ISL = json.load(open(ISL_F)) if os.path.exists(ISL_F) else {}
TRANSCRIBE = C.transcription_enabled()


def island_text(f, a, b):
    key = f"{os.path.basename(f)}|{a:.3f}|{b:.3f}"
    if key not in ISL:
        if not TRANSCRIBE: return ""  # cannot verify -> the pause is left alone
        ISL[key] = C.transcribe_clip(f, a, b)
        json.dump(ISL, open(ISL_F, "w"), ensure_ascii=False, indent=0)
    return ISL[key]


for sc in secs:
    f = f"{VO_SRC}/sec{sc['j']:02d}.mp3"; T = sc["T"]; D0 = sc["dur"]; sil = silences(f)
    lead_sil = [e for a, e in sil if a <= 0.05]
    start = max(0.0, lead_sil[0] - 0.05) if lead_sil and lead_sil[0] <= T[0][0] + 0.15 else max(0.0, T[0][0] - 0.12)
    tail_sil = [a for a, e in sil if a >= T[-1][1] - 0.15 and e >= D0 - 0.05]
    stop = min(D0, tail_sil[0] + 0.12) if tail_sil else min(D0, T[-1][1] + 0.2)
    cuts = []
    for ph, g in SPLITS:
        if ph not in sc["text"]: continue
        p = T[sidx(sc["text"], sc["text"].index(ph))][0]
        cand = [(e - a, (a + e) / 2) for a, e in sil if p - 0.8 <= e <= p + 0.3 and start < a]  # the pause at punctuation is usually the longest nearby silence
        if not cand: SPLIT_LOG.append(f"section {sc['j']} before '{ph}': no silence found, no pause added"); continue
        cuts.append((max(cand)[1], g)); SPLIT_LOG.append(f"section {sc['j']} before '{ph}': +{g}s at {max(cand)[1]:.2f}s")
    # Tighten breaths: a pause of 0.4 s or more between characters, away from punctuation, in real silence, shrinks to 0.2 s
    should, k0 = set(), -1
    for c in sc["text"]:
        if c in PUNC: should.add(k0)
        else: k0 += 1
    removes = []; sil30 = silences(f, -30)  # wider threshold: an in-sentence breath also counts as a removable gap
    cutpts = [c for c, _ in cuts]
    for a, e in sil30:  # start from measured silence; shorten only those proven not to sit at punctuation
        if e - a < 0.4 or a <= start or e >= stop or any(a - 0.05 <= c <= e + 0.05 for c in cutpts): continue  # under 0.4 s is a normal breath; keep it (over-tightening kills the human feel)
        m = (a + e) / 2
        k = min(range(len(T) - 1), key=lambda n: abs((T[n][1] + T[n + 1][0]) / 2 - m))  # which two characters this silence falls between
        if any(x in should for x in (k - 1, k, k + 1)): continue  # next to punctuation: a normal sentence pause
        # Transcribed times often lag one or two characters at pauses (five "mid-sentence pauses" once turned out to be
        # ordinary punctuation pauses; shortening them made the read sound rushed). So transcribe the 2.5 s before the
        # pause on its own and see which character it really follows; if that cannot be matched, do nothing.
        p0 = max(start, a - 2.5); it = island_text(f, p0, a + 0.05); R = strip(sc["text"])
        hits = next((h for n in (4, 3, 2) if len(it) >= n for h in [[i + n - 1 for i in range(len(R) - n + 1) if R[i:i + n] == it[-n:] and abs(i + n - 1 - k) <= 6]] if h), [])
        if not hits: SPLIT_LOG.append(f"section {sc['j']} pause {e-a:.2f}s at {a:.2f}s: could not verify by transcription ({it[-6:]}), left alone"); continue
        k = min(hits, key=lambda i: abs(i - k))
        if k in should: SPLIT_LOG.append(f"section {sc['j']} pause {e-a:.2f}s after '{strip(sc['text'])[max(0,k-3):k+1]}' is at punctuation, left alone"); continue
        keep = 0.2; removes.append((m - (e - a - keep) / 2, m + (e - a - keep) / 2))
        SPLIT_LOG.append(f"section {sc['j']} mid-sentence pause {e-a:.2f}s '{strip(sc['text'])[max(0,k-2):k+1]}|{strip(sc['text'])[k+1:k+3]}' shortened to {keep}s")
    # Cut points for per-sentence levelling: the silence at each sentence end
    levs, k0 = [], -1
    for c in sc["text"]:
        if c in C.SENTENCE_END and 0 <= k0 < len(T) - 1:
            cand = [(e - a, (a + e) / 2) for a, e in sil if a >= T[k0][1] - 0.25 and e <= T[k0 + 1][0] + 0.25 and start < a and e < stop]
            if cand: levs.append(max(cand)[1])
        elif c not in PUNC: k0 += 1
    # Kept pieces: drop removes, insert pauses at cuts, split at sentence ends so each sentence can be levelled
    marks = [(c, "ins", g) for c, g in cuts] + [(a, "rm", b) for a, b in removes]
    marks += [(x, "lev", 0) for x in levs if all(abs(x - m[0]) > 0.15 and not (m[1] == "rm" and m[0] - 0.05 <= x <= m[2] + 0.05) for m in marks)]
    marks.sort()
    pieces, gaps_after, cur = [], [], start
    for x, kind, v in marks:
        pieces.append((cur, x))
        if kind == "rm": gaps_after.append(0); cur = v
        else: gaps_after.append(v); cur = x
    pieces.append((cur, stop)); gaps_after.append(0)
    sc["pieces"], sc["gaps_after"], sc["src"] = pieces, gaps_after, f

    def mp(x, pieces=pieces, gaps_after=gaps_after):  # original audio time -> processed time
        off = 0.0
        for (a, b), g in zip(pieces, gaps_after):
            if x <= b: return off + max(0.0, x - a)
            off += (b - a) + g
        return off
    sc["Tn"] = [(mp(a), mp(b)) for a, b in T]; sc["file"] = f"assets/{OVS}/sec{sc['j']:02d}.wav"


# Per-sentence levelling: gated loudness per sentence, pulled to the median of the whole film, at most +/-3 dB;
# deviations under 0.8 dB are left alone. One fixed gain per sentence, no dynamic compression.
def piece_lufs(f, a, b):
    if b - a < 0.6: return None
    r = subprocess.run([FF, "-ss", f"{a:.3f}", "-to", f"{b:.3f}", "-i", f, "-af", "ebur128", "-f", "null", "-"], capture_output=True, text=True).stderr
    v = re.findall(r"I:\s+(-?[\d.]+) LUFS", r); return float(v[-1]) if v and float(v[-1]) > -60 else None


ALL = []
for sc in secs:
    sc["lu"] = [piece_lufs(sc["src"], a, b) for a, b in sc["pieces"]]; ALL += [x for x in sc["lu"] if x is not None]
TARGET = sorted(ALL)[len(ALL) // 2]; LEV_LOG = []
for sc in secs:
    ins, fc = [], ""
    for n, ((x, y), g, lu) in enumerate(zip(sc["pieces"], sc["gaps_after"], sc["lu"])):
        gain = 0.0 if lu is None or abs(TARGET - lu) < 0.8 else max(-3.0, min(3.0, TARGET - lu))
        if gain: LEV_LOG.append(f"s{sc['j']} {x:.1f}-{y:.1f}s {gain:+.1f}dB")
        ins += ["-ss", f"{x:.3f}", "-to", f"{y:.3f}", "-i", sc["src"]]
        fc += f"[{n}:a]aformat=sample_rates=44100:channel_layouts=mono,volume={gain:.2f}dB,afade=t=in:d=0.01,areverse,afade=t=in:d=0.03,areverse,apad=pad_dur={g}[p{n}];"
    fc += "".join(f"[p{n}]" for n in range(len(sc["pieces"]))) + f"concat=n={len(sc['pieces'])}:v=0:a=1[o]"
    o = f"{OUTVO}/sec{sc['j']:02d}.wav"
    subprocess.run([FF, "-v", "error", "-y", *ins, "-filter_complex", fc, "-map", "[o]", o], check=True); sc["d"] = round(dur(o), 3)

# Which section each scene belongs to, and at which character it starts
si = 0; LOC = {}
for i, (k, txt, p) in enumerate(S):
    if not txt: continue
    while True:
        if si >= len(secs):
            raise SystemExit(f'Scene {i} ({k}): its text "{txt[:20]}" comes after the end of sections.json. Scene texts joined in order '
                             f'must reproduce sections.json exactly; remove the extra text or add it to sections.json and re-record.')
        sc = secs[si]; at = sc["text"].find(txt, sc["pos"])
        if at == sc["pos"]: break
        if not (at == -1 and sc["pos"] == len(sc["text"])):
            raise SystemExit(f'Scene {i} ({k}) does not continue section {sc["j"]}: the section goes on with "{sc["text"][sc["pos"]:sc["pos"] + 20]}" '
                             f'but the scene starts with "{txt[:20]}". Scene texts joined in order must reproduce sections.json exactly, '
                             f'punctuation included; fix the scene text in spec.S.')
        si += 1
    LOC[i] = (si, at); sc["pos"] = at + len(txt)
for sc in secs:  # every character of the narration must belong to a scene, or captions and pictures silently go missing
    if sc["pos"] != len(sc["text"]):
        raise SystemExit(f'Section {sc["j"]} is not fully covered by the scene list: {len(sc["text"]) - sc["pos"]} characters from '
                         f'"{sc["text"][sc["pos"]:sc["pos"] + 20]}" on belong to no scene. Add them to a scene in spec.S (in order), '
                         f'or remove them from sections.json and re-record.')
BT = {}; BITE_LOG = []
for bn, btxt in BITE_TEXT.items():
    # A speaker bite may be at most 1 dB louder than the narration (review: bites ran 2.2-2.9 dB hot); one fixed gain
    lub = piece_lufs(f"{BITES}/{bn}.wav", 0, dur(f"{BITES}/{bn}.wav")); bg = 0.0 if lub is None else round(max(-4.0, min(0.0, TARGET + 1.0 - lub)), 1)
    if bg: subprocess.run([FF, "-v", "error", "-y", "-i", f"{BITES}/{bn}.wav", "-af", f"volume={bg}dB", f"{OUTVO}/{bn}.wav"], check=True); BITE_LOG.append(f"{bn} {lub:.1f}->{lub + bg:.1f} LUFS ({bg:+.1f}dB)")
    else: shutil.copy(f"{BITES}/{bn}.wav", f"{OUTVO}/{bn}.wav")
    BT[bn] = {"file": f"assets/{OVS}/{bn}.wav", "d": round(dur(f"{OUTVO}/{bn}.wav"), 3), "rel": char_times(btxt, json.load(open(f"{BITES}/{bn}.words.json"))), "src": BITE_SRC[bn]}

# ---------- Timeline: sections set positions, scenes follow pronunciation inside their section ----------
STOCK = f"{PJ}/assets/stock"
TITLE = SPEC.TITLE; TVC_MAX = dur(f"{PJ}/assets/tvc.mp4") - 0.1  # never read past the end of the original film
SC = []; SECPOS = {}


def absT(s, k):  # absolute start of the k-th character (punctuation-free count) of a scene
    sc = secs[s["sec"]]; return SECPOS[s["sec"]] + sc["Tn"][sidx(sc["text"], s["off"]) + k][0]


def at_time(s, phrase):
    if phrase not in s["txt"]:
        raise SystemExit(f'Scene {s["i"]} ({s["k"]}): cue word "{phrase}" (from "at", "t2at" or a chips item) is not in this scene\'s '
                         f'narration "{s["txt"][:30]}". Use words that are spoken in this scene, exactly as written in spec.S.')
    return round(absT(s, sidx(s["txt"], s["txt"].index(phrase))), 2)


t = TITLE["d"]
for i, (k, txt, p) in enumerate(S):
    s = {"i": i, "k": k, "txt": txt, **{x: y for x, y in p.items() if x not in ("gaps", "items")}}
    if i in LOC:
        s["sec"], s["off"] = LOC[i]; sc = secs[s["sec"]]
        if s["off"] == 0:  # first scene of a section: lead-in depends on the scene type
            bite = p.get("bite")
            lead = 2.8 if k == "chapter" else (0.3 + BT[bite]["d"] + 0.4 if bite else (0.6 if i == 0 else 0.3))
            s["t"] = round(t, 2); SECPOS[s["sec"]] = round(t + lead - sc["Tn"][0][0], 3)
            if bite: s["bite_t"] = round(t + 0.3, 2); s["bite_d"] = BT[bite]["d"]
        else:
            s["t"] = round(absT(s, 0) - 0.2, 2)  # picture cuts 0.2 s before the voice
        s["vo"] = round(absT(s, 0), 2)
        if SC: SC[-1]["d"] = round(s["t"] - SC[-1]["t"], 2)
        s["d"] = 0; SC.append(s)
        last_of_sec = (i + 1 not in LOC) or LOC[i + 1][0] != s["sec"]
        if last_of_sec: t = SECPOS[s["sec"]] + sc["Tn"][0][0] + (sc["d"] - sc["Tn"][0][0]) + SEC_TAIL.get(sc["j"], 0.4)
    else:  # end card
        if SC: SC[-1]["d"] = round(t - SC[-1]["t"], 2)
        s.update({"t": round(t, 2), "vo": round(t, 2), "d": 7.0}); SC.append(s); t += 7.0
TOTAL = round(t, 2)
for s in SC:
    i, k, p = s["i"], s["k"], S[s["i"]][2]
    if p.get("items"): s["items"] = [x for x, _ in p["items"]]; s["chipT"] = [at_time(s, ph) for _, ph in p["items"]]
    cs = [c if isinstance(c, dict) else {"src": c} for c in p.get("clips", [])]
    if p.get("bite"):  # during a bite: the speaker's own shot (lip sync), then the story picture
        cs = [{"src": round(BT[p["bite"]]["src"] - 0.3, 2), "_st": s["t"]}, {"src": p["src"], "_st": round(s["vo"] - 0.1, 2)}] + [c for c in cs if "at" in c]
    if cs:
        b0 = s["t"] + (2.9 if k == "chapter" else 0); st = []
        for c in cs:
            if "_st" in c: st.append(c["_st"])
            elif "at" in c: st.append(round(at_time(s, c["at"]) - 0.12, 2))
            else: st.append(round(b0, 2))
        cl = []
        for ci, c in enumerate(cs):
            dd = round((st[ci + 1] if ci + 1 < len(cs) else s["t"] + s["d"]) - st[ci], 2)
            if "flip" in c: cl.append({"st": st[ci], "dd": dd, "flip": c["flip"]})
            elif "gfx" in c: cl.append({"st": st[ci], "dd": dd, "gfx": c["gfx"], **({"t2": round(at_time(s, c["t2at"]) - 0.1, 2)} if c.get("t2at") else {})})
            elif "img" in c: cl.append({"st": st[ci], "dd": dd, "img": c["img"], **({"full": 1} if c.get("full") else {})})
            elif "f" in c:
                fd = dur(f"{STOCK}/{c['f']}.mp4"); ms = min(c.get("ms", 0), round(fd - dd - 0.05, 2))
                if ms < 0:
                    raise SystemExit(f'Scene {i} ({k}): stock clip {c["f"]}.mp4 is {fd:.1f} s long but has to fill {dd:.1f} s here. Use a longer clip, '
                                     f'cut to another shot earlier with "at", or split the scene.')
                cl.append({"st": st[ci], "dd": dd, "file": f"assets/stock/{c['f']}.mp4", "ms": ms, "stock": 1})
                if c.get("quote"): cl[-1]["quote"] = c["quote"]
            else:
                if c["src"] + dd > TVC_MAX:
                    raise SystemExit(f'Scene {i} ({k}): the original-film shot from {c["src"]} s has to run {dd:.1f} s, past the end of the film '
                                     f'({TVC_MAX + 0.1:.1f} s). Start it earlier ("src") or cut to another shot with "at".')
                cl.append({"st": st[ci], "dd": dd, "file": "assets/tvc.mp4", "ms": c["src"], "stock": 0, **({"card": 1} if c.get("card") else {}), **({"hideover": 1} if c.get("hideover") else {})})
                if c.get("quote"): cl[-1]["quote"] = c["quote"]
        s["cl"] = cl
        imgs = [c["st"] for c in cl if c.get("img") or c.get("hideover")]
        if imgs and k in ("chips", "posters"): s["overlayOff"] = imgs[0]
        cards = [c["st"] for c in cl if c.get("img") or c.get("flip") or c.get("gfx") or c.get("hideover")]
        if cards and k == "story": s["overlayOff"] = cards[0]
for s in SC:
    if "src" in s and not s.get("cl") and s["src"] + s["d"] > TVC_MAX:
        raise SystemExit(f'Scene {s["i"]} ({s["k"]}): the original film from {s["src"]} s has to run {s["d"]:.1f} s, past the end of the film '
                         f'({TVC_MAX + 0.1:.1f} s). Start it earlier ("src") or add shots with "clips".')
# Original-film cut check: a clip whose start or end lands within 0.25 s of a cut in the original film flashes the
# neighbouring shot for a frame or two. Cuts come from scene detection, cached in wide/assets/tvc_cuts.json.
CUTS_F = f"{PJ}/assets/tvc_cuts.json"; _sig = str(os.path.getsize(f"{PJ}/assets/tvc.mp4"))
_cc = json.load(open(CUTS_F)) if os.path.exists(CUTS_F) else {}
if _cc.get("sig") != _sig:
    r = subprocess.run([FF, "-i", f"{PJ}/assets/tvc.mp4", "-vf", "scale=320:-1,select='gt(scene,0.25)',showinfo", "-an", "-f", "null", "-"], capture_output=True, text=True).stderr
    _cc = {"sig": _sig, "cuts": [round(float(x), 3) for x in re.findall(r"pts_time:([\d.]+)", r)]}; json.dump(_cc, open(CUTS_F, "w"))
CUT_LOG = []
for s in SC:
    cl_ = s.get("cl", []); nxt = lambda ci: cl_[ci + 1]["ms"] if ci + 1 < len(cl_) and cl_[ci + 1].get("file") == "assets/tvc.mp4" else None
    segs = [(c["ms"], c["dd"], f"#{s['i']} clip {ci}", nxt(ci)) for ci, c in enumerate(cl_) if c.get("file") == "assets/tvc.mp4"]
    if "src" in s and not s.get("cl") and s["k"] in ("full", "story", "chips", "chapter"):
        o = 2.9 if s["k"] == "chapter" else 0.0; segs.append((s["src"] + o, s["d"] - o, f"#{s['i']}", None))
    for ms, dd, name, nx in segs:
        for x in _cc["cuts"]:
            if ms + dd - 0.25 < x < ms + dd - 0.01 and not (nx is not None and abs(nx - (ms + dd)) < 0.08): CUT_LOG.append(f"{name}: ends {ms + dd - x:.2f}s after an original cut ({x:.2f}s) - the next shot will flash")
            if ms + 0.01 < x < ms + 0.25: CUT_LOG.append(f"{name}: an original cut ({x:.2f}s) sits {x - ms:.2f}s after the start - the previous shot will flash")

# ---------- Captions: real pronunciation times, each block at least 0.6 s ----------
# Netflix Simplified Chinese style: commas, full stops, semicolons and colons become spaces; the enumeration comma
# stays mid-line; quotation marks are reserved for speaker bites.
caps = []
SPLIT_AT = f"(?<=[{C.COMMA}{C.PERIOD}{C.COLON}{C.SEMI}{C.ENUM}{C.QUESTION}{C.EXCLAIM}])"
TO_SPACE = f"[{C.COMMA}{C.PERIOD}{C.SEMI}{C.COLON}]"
TRAIL = C.COMMA + C.PERIOD + C.COLON + C.SEMI + C.ENUM


def add_caps(text, rel, base, end, quote=False):
    raw = [x for x in re.split(SPLIT_AT, text) if strip(x)]
    parts = []  # merge blocks shorter than 5 characters into the next so captions do not flicker
    for x in raw:
        if parts and len(strip(parts[-1])) < 5 and len(strip(parts[-1] + x)) <= 16: parts[-1] += x
        else: parts.append(x)
    if len(parts) > 1 and len(strip(parts[-1])) < 5 and len(strip(parts[-2] + parts[-1])) <= 16: parts[-2:] = [parts[-2] + parts[-1]]
    pos = 0; starts = []
    for x in parts:
        k0 = text.index(x, pos); pos = k0 + len(x); starts.append((round(base + rel[sidx(text, k0)][0] - 0.05, 2), re.sub(TO_SPACE, " ", x.rstrip(TRAIL))))
    for n, (a, x) in enumerate(starts):
        b = starts[n + 1][0] if n + 1 < len(starts) else round(end, 2)
        caps.append((a, round(max(b - a, 0.6), 2), f"{C.LDQ}{x}{C.RDQ}" if quote else x))


for s in SC:
    if s.get("bite"):
        bt = BT[s["bite"]]; add_caps(BITE_TEXT[s["bite"]], bt["rel"], s["bite_t"], s["bite_t"] + bt["d"] + 0.2, quote=True)
    if s["txt"]:
        n = len(strip(s["txt"])); rel = [(absT(s, k0), absT(s, k0)) for k0 in range(n)]
        add_caps(s["txt"], rel, 0, s["t"] + s["d"])
caps.sort()
for n in range(len(caps) - 1):  # no overlaps
    a, b, x = caps[n]
    if a + b > caps[n + 1][0]: caps[n] = (a, round(max(caps[n + 1][0] - a, 0.3), 2), x)

# ---------- Graphic cards (gfx): cards defined in the spec, plus the engine's built-in recap row ----------
GFX = dict(getattr(SPEC, "GFX", {}))
if getattr(SPEC, "RECAP", None):  # numbers already told, in a row, lighting up one by one, with a ruler
    GFX["recap"] = ('<div class="rc">' + "".join(f'<div class="rci"><div class="rcn num">{n}</div><div class="rct">{t}</div></div>' for n, t in SPEC.RECAP["items"]) + '</div><div class="rcl">' +
                    "".join(f'<i style="left:{x}px"></i>' for x in SPEC.RECAP["ticks"]) + '</div>')

# ---------- HTML ----------
# Every clip runs 2 frames past its end and overlaps the next one. The renderer draws a video at the wrong scale on
# its very first frame, so the next clip enters with a 2-frame fade (assets/wide.js) whose first frame is transparent
# and covered by these extra frames; it still reads as a hard cut. Images, poster flips and cards need the same tail.
VID_TAIL = 0.07
V = [f'<div class="vw" id="tvw"><video id="tv" class="vfull vtitle" src="assets/tvc.mp4" muted playsinline data-start="0" data-duration="{TITLE["d"]}" data-media-start="{TITLE["src"]}" data-track-index="23"></video></div>',
     f'<div class="tshade clip" data-start="0" data-duration="{TITLE["d"]}" data-track-index="5"></div>']
L = [f'<section class="scene clip" id="ttl" data-start="0" data-duration="{TITLE["d"]}" data-track-index="12"><div class="ttl">'
     f'<div class="ttl-k" id="tk">{E(TITLE["sub"])}</div><div class="ttl-t" id="tt1">{E(TITLE["t1"])}</div><div class="ttl-t" id="tt2">{E(TITLE["t2"])}</div>'
     f'<div class="ttl-a" id="ta">{E(TITLE["by"])}</div></div></section>']


def vid(s, cls, idp, dstart=None, ddur=None):
    st = s["t"] if dstart is None else dstart; dd = s["d"] if ddur is None else ddur
    ms = s["src"] + (st - s["t"])
    return (f'<div class="vw" id="{idp}w{s["i"]}"><video id="{idp}{s["i"]}" class="{cls}" src="assets/tvc.mp4" muted playsinline '
            f'data-start="{st}" data-duration="{round(dd + VID_TAIL,2)}" data-media-start="{round(ms,2)}" data-track-index="{20+s["i"]%3}"></video></div>')


def sec(s, inner, tail=0.0):  # tail: card scenes (comments) stay 2 frames longer to cover the next clip's first frame
    return f'<section class="scene clip" id="s{s["i"]}" data-start="{s["t"]}" data-duration="{round(s["d"] + tail, 2)}" data-track-index="{10+s["i"]%2}">{inner}</section>'


for s in SC:
    i, k = s["i"], s["k"]
    if s.get("cl"):
        for ci, c in enumerate(s["cl"]):
            if c.get("flip"):
                V.append(f'<div class="flip clip" id="fl{i}" data-start="{c["st"]}" data-duration="{round(c["dd"] + VID_TAIL, 2)}" data-track-index="30">' + "".join(
                    f'<img class="fp" id="fp{i}_{j}" src="assets/img/hd/p{j+1:02d}.jpg">' for j in range(c["flip"])) + '</div>')
            elif c.get("gfx"):
                V.append(f'<div class="gfx gk-{c["gfx"]} clip" id="gx{i}_{ci}" data-start="{c["st"]}" data-duration="{round(c["dd"] + VID_TAIL, 2)}" data-track-index="{32+ci%2}">{GFX[c["gfx"]]}</div>')
            elif c.get("img"):
                V.append(f'<div class="flip clip" id="imw{i}_{ci}" data-start="{c["st"]}" data-duration="{round(c["dd"] + VID_TAIL, 2)}" data-track-index="{31+ci%2}"><img class="{"fpf" if c.get("full") else "fpc"}" id="im{i}_{ci}" src="assets/img/{c["img"]}"></div>')
            else:
                V.append(f'<div class="vw" id="vw{i}_{ci}"><video id="v{i}_{ci}" class="vfull" src="{c["file"]}" muted playsinline '
                         f'data-start="{c["st"]}" data-duration="{round(c["dd"] + VID_TAIL, 2)}" data-media-start="{c["ms"]}" data-track-index="{24+ci}"></video></div>')
                if c.get("quote"):
                    q = E(c["quote"]).replace("[", "<b>").replace("]", "</b>")
                    L.append(f'<div class="qcard clip" id="qc{i}_{ci}" data-start="{c["st"]}" data-duration="{c["dd"]}" data-track-index="{50+ci%2}"><div class="qmeta"><span class="qav"></span>{E(SPEC.COMMENTS["meta"])}</div><div class="qtxt">{q}</div></div>')
        if k == "chapter":
            c = s["cl"][0]
            V.append(f'<div class="vw" id="bw{i}"><video id="b{i}" class="vblur" src="{c["file"]}" muted playsinline '
                     f'data-start="{s["t"]}" data-duration="3.2" data-media-start="0" data-track-index="{20+i%3}"></video></div>')
    elif k in ("full", "story", "chips"):
        V.append(vid(s, "vfull", "v"))
    if k in ("comments", "ask"):
        V.append(vid(s, "vblur", "b"))
    if k == "chapter" and not s.get("cl"):
        V.append(vid(s, "vblur", "b", s["t"], 3.2))
        V.append(vid(s, "vfull", "v", round(s["t"] + 2.9, 2), round(s["d"] - 2.9, 2)))
    if k == "full" and s.get("over"):
        L.append(sec(s, f'<div class="over" id="o{i}"><i></i>{E(s["over"])}</div>'))
    elif k == "comments":
        L.append(sec(s, f'<div class="cmt-head" id="ch{i}">{E(SPEC.COMMENTS["head"])}</div><img class="cmt" id="cm{i}" src="assets/img/{SPEC.COMMENTS["img"]}"><div class="likes" id="lk{i}">{E(SPEC.COMMENTS["likes"])}</div>', VID_TAIL))
    elif k == "ask":
        L.append(sec(s, f'<div class="ask" id="ak{i}">{E(SPEC.ASK)}</div>'))
    elif k == "chapter":
        L.append(sec(s, f'<div class="chap" id="cp{i}"><div class="cno num">{s["no"]}</div><div class="ct1">{E(s["t1"])}</div><div class="ct2">{E(s["t2"])}</div></div>'))
    elif k == "story":
        L.append(sec(s, f'<div class="sn num" id="sn{i}">{s["n"]}</div><div class="stag" id="st{i}">{E(s["tag"])}</div>'))
    elif k == "chips":
        L.append(sec(s, f'<div class="cshade"></div><div class="chead" id="chd{i}"><i></i>{E(s["head"])}</div><div class="chips">' + "".join(
            f'<div class="chip" id="c{i}_{j}">{E(x)}</div>' for j, x in enumerate(s["items"])) + '</div>'))
    elif k == "posters":
        L.append(sec(s, '<div class="pwall">' + "".join(f'<img class="pst" id="p{j}" src="assets/img/hd/p{j+1:02d}.jpg">' for j in range(SPEC.POSTERS["n"])) + f'</div><div class="phead" id="ph">{E(SPEC.POSTERS["head"])}</div>'))
    elif k == "end":
        N = SPEC.END  # the CLEAN (vertical / Douyin) build has no QR code and no WeChat account wording
        L.append(sec(s, f'<div class="endc"><div class="ek" id="ek">{E(N["kicker"])}</div><div class="et" id="et">{N["title_html"]}</div>'
                        + (f'<div class="ea" id="ea">{E(N["author_clean"])}</div></div>' if CLEAN else
                           f'<div class="ea" id="ea">{E(N["author"])}</div><div class="er" id="er"><img src="assets/img/{N["qr"]}"><span>{E(N["qr_text"])}</span></div></div>')))
# Original-film framing (spec.FRAME): how far the film is scaled up, from which corner, and where the frosted strip
# over its burned-in subtitles starts. Measure every new film (references/spec-format.md); defaults fit the pilot film.
FRAME = {"zoom": (1.12, 1.19), "origin": "0% 0%", "subband_top": 878, **getattr(SPEC, "FRAME", {})}
SB = ""
for s in SC:
    if s["k"] in ("full", "story", "chips"):  # caption band; skipped while an original title card (card) is on screen
        a0 = s["t"]
        for c in [c for c in s.get("cl", []) if c.get("card")] + [{"st": s["t"] + s["d"], "dd": 0}]:
            if c["st"] - a0 > 0.05: SB += f'<div class="subband clip" data-start="{round(a0, 2)}" data-duration="{round(c["st"] - a0, 2)}" data-track-index="{40+s["i"]%2}"></div>'
            a0 = c["st"] + c["dd"]
    if s["k"] == "chapter": SB += f'<div class="subband clip" data-start="{round(s["t"]+2.9,2)}" data-duration="{round(s["d"]-2.9,2)}" data-track-index="{40+s["i"]%2}"></div>'
if FRAME["subband_top"] is None: SB = ""  # the film has no burned-in subtitles to blur
END_BG = getattr(SPEC, "END_BG", "#b3161b")
bgl = f'<div class="bgc clip" data-start="0" data-duration="{TITLE["d"]}" data-track-index="1" style="background:#111"></div>' + "".join(
    f'<div class="bgc clip" data-start="{s["t"]}" data-duration="{s["d"]}" data-track-index="1" style="background:{END_BG if s["k"]=="end" else "#111"}"></div>' for s in SC)
caps_html = "" if CLEAN else "".join(f'<div class="cap clip" data-start="{a}" data-duration="{b}" data-track-index="{60+j%2}"><span>{E(x)}</span></div>' for j, (a, b, x) in enumerate(caps))
aud = []
WHOOSH_AT = getattr(SPEC, "WHOOSH_AT", ()); CHIME_AT = getattr(SPEC, "CHIME_AT", None)
for s in SC:
    i = s["i"]
    if s.get("off") == 0:
        sc = secs[s["sec"]]; aud.append(f'<audio id="vo{sc["j"]}" src="{sc["file"]}" data-start="{round(SECPOS[s["sec"]], 3)}" data-duration="{sc["d"]}" data-track-index="{81+sc["j"]%2}" data-volume="1"></audio>')
    if s.get("bite"): aud.append(f'<audio id="bt{i}" src="{BT[s["bite"]]["file"]}" data-start="{s["bite_t"]}" data-duration="{BT[s["bite"]]["d"]}" data-track-index="84" data-volume="1"></audio>')
    if s["k"] in ("chapter", "posters", "end") or i in WHOOSH_AT:
        aud.append(f'<audio id="sw{i}" src="assets/sfx/whoosh.mp3" data-start="{max(0, round(s["t"]-0.2, 2))}" data-duration="0.57" data-track-index="{85+i%2}" data-volume="0.22"></audio>')
SFX = [("whoosh-cinematic", 0.15, 5.54, 0.16)]
for s in SC:
    if s["k"] == "story": SFX.append(("whoosh-short", (s["vo"] - 0.35) if s.get("bite") else s["t"] + 0.1, 0.57, 0.14))
    if s.get("chipT"): SFX += [("pop", x, 0.72, 0.13) for x in s["chipT"]]
    for c in s.get("cl", []):
        if c.get("flip"): SFX += [("click-soft", c["st"] + j * c["dd"] / c["flip"], 0.37, 0.12) for j in range(c["flip"])]
        if c.get("gfx") and c["gfx"] != "gray": SFX.append(("click-soft", c["st"], 0.37, 0.1))
    if s["i"] == CHIME_AT: SFX.append(("chime", s["cl"][-1]["st"] + 0.5, 2.5, 0.2))
for j, (f, st, du, vol) in enumerate(SFX):
    aud.append(f'<audio id="fx{j}" src="assets/sfx/{f}.mp3" data-start="{round(st, 2)}" data-duration="{du}" data-track-index="{87+j%4}" data-volume="{vol}"></audio>')

css = open(f"{C.ASSETS}/wide.css").read().replace("__SUBBAND_TOP__", str(FRAME["subband_top"] or 0))
z0, z1 = FRAME["zoom"]
js = (open(f"{C.ASSETS}/wide.js").read().replace("__SC__", json.dumps(SC, ensure_ascii=False)).replace("__NPOST__", str(getattr(SPEC, "POSTERS", {}).get("n", 16)))
      .replace("__Z0__", f"{z0:g}").replace("__Z1__", f"{z1:g}").replace("__ZT__", f"{z0 + 0.08:g}").replace("__ORIGIN__", FRAME["origin"]))
doc = f"""<!doctype html><html lang="zh-CN"><head><meta charset="UTF-8"/><meta name="viewport" content="width=1920, height=1080"/>
<script src="https://cdn.jsdelivr.net/npm/gsap@3.14.2/dist/gsap.min.js"></script><style>{css}</style></head><body>
<div id="root" data-composition-id="main" data-start="0" data-duration="{TOTAL}" data-width="1920" data-height="1080">
{bgl}{"".join(V)}<div class="shade clip" data-start="0" data-duration="{TOTAL}" data-track-index="4"></div>{SB}{"".join(L)}
{caps_html}{"".join(aud)}
</div><script>{js}</script></body></html>"""
open(f"{PJ}/index.html", "w").write(doc)
NARR = []
for s in SC:
    if s.get("bite"): NARR.append(BITE_TEXT[s["bite"]])
    if s["txt"]: NARR.append(s["txt"])
json.dump({"SC": SC, "TOTAL": TOTAL, "caps": caps, "vo_src": VO_SRC, "narr": NARR}, open(f"{H}/timeline.json", "w"), ensure_ascii=False, indent=1)
for x in SPLIT_LOG: print(" ", x)
for x in BITE_LOG: print("  bite levelled:", x)
for x in CUT_LOG: print("  WARNING original-film cut:", x)
if not TRANSCRIBE: print("  note: transcription off or BaoCut missing - mid-sentence pauses were not checked")
print(f"  sentence levelling: target {TARGET:.1f} LUFS, {len(LEV_LOG)} sentences adjusted:", "; ".join(LEV_LOG[:12]), "..." if len(LEV_LOG) > 12 else "")
print(f"OK total={TOTAL}s scenes={len(SC)} captions={len(caps)} vo_src={os.path.basename(VO_SRC)}")
