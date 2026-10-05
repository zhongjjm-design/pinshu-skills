"""Content spec for one brand-film teardown video. Everything this film SAYS lives here; how it is made lives in the skill.
Copied into a new project as spec.py by new_project.py. Field reference: references/spec-format.md.
Replace every <...> placeholder. Narration text is written in Chinese; keep it EXACTLY identical to sections.json.
"""
# Voice source (relative to the project): output of gen_voice.py, or of patch_voice.py if words were slowed down
VO_SRC = "voice/gemini_Charon"
# Optional: slow a few rushed words without re-synthesizing (see patch_voice.py); then set VO_SRC to PATCH["dst"]
# PATCH = {"src": "voice/gemini_Charon", "dst": "voice/gemini_Charon_patched", "ops": {1: [(19.75, 20.38, 1.35)]}}

# Scenes: (kind, narration, params). The narration of consecutive scenes, joined, must equal the section texts in
# sections.json, in order. Kinds: full, comments, ask, chapter, story, chips, posters, end.
# Clip forms inside "clips": 12.5 (original film at 12.5 s) | {"src": 12.5, "at": "<word>"} (cut to it when <word> is
# spoken) | {"f": "<stock id>", "ms": 0.0, "at": ...} | {"img": "<file>", "at": ..., "full": True} |
# {"gfx": "<card>", "at": ...} | {"flip": 16, "at": ...}. Flags: "card": True (the film's own title card: no scale, no
# caption band), "hideover": True (the clip shows its own numbers: hide the story number), "quote": "<comment text>".
S = [
    ("full", "<opening narration: the hook>", {"src": 0.0, "clips": [2.0, {"src": 30.0, "at": "<word>"}], "over": "<short label>"}),
    ("chapter", "<chapter narration>", {"src": 60.0, "no": "01", "t1": "<chapter title>", "t2": "<chapter subtitle>"}),
    ("story", "<one person's story>", {"src": 90.0, "n": "1", "tag": "<story label>", "bite": "bite1",
                                       "clips": [{"src": 95.0, "at": "<word>", "hideover": True}]}),
    ("chips", "<why it works>", {"src": 120.0, "head": "<heading>", "items": [("<chip 1>", "<word that pops it>"), ("<chip 2>", "<word>")]}),
    ("full", "<closing line>", {"src": 150.0, "clips": [150.0, {"src": 160.0, "at": "<word>", "card": True}]}),
    ("end", "", {}),
]

# Speaker bites from the original film: exact words (captions use these; check them against the audio) and where they are
BITE_TEXT = {"bite1": "<exact words, punctuated>"}
BITE_CUTS = {"bite1": (31.0, 35.0)}  # start, end seconds in the original film (prep_bites.py)

# Extra pause (seconds) inside the real silence before these phrases; air after each section (section number: seconds)
SPLITS = [("<phrase>", 0.4)]
SEC_TAIL = {0: 1.1}  # default 0.4 s; longer at topic changes

# Opening title page: duration, film second used as background, two title lines, red label, byline
TITLE = {"d": 3.4, "src": 0.0, "t1": "<title line 1>", "t2": "<title line 2>", "sub": "<brand film teardown label>", "by": "<channel | author>"}

# Only needed when the matching scene kinds are used
COMMENTS = {"head": "<comments heading>", "img": "comments.webp", "likes": "<platform and likes>", "meta": "<comment source label>"}
ASK = "<big question>"
POSTERS = {"n": 16, "head": "<poster wall heading>"}  # posters at wide/assets/img/hd/p01.jpg ...
END = {"kicker": "<label>", "title_html": "<film title, may contain <br>>",
       "author": "<byline with account>", "author_clean": "<byline without WeChat wording (Douyin edition)>",
       "qr": "qrcode.jpg", "qr_text": "<scan to read the article>"}
END_BG = "#b3161b"   # end-card background colour
WHOOSH_AT = ()       # scene numbers that get an extra transition whoosh
CHIME_AT = None      # scene number whose last clip gets a soft chime 0.5 s in

# Parody / graphic cards used as {"gfx": "<name>"} clips: name -> HTML. Each card's wrapper gets class gk-<name>; only gk-recap has
# built-in styles, so style other cards inline. Optional recap row
GFX = {}
# RECAP = {"items": [("1", "<label>"), ("3", "<label>")], "ticks": (130, 465)}

# Music: file in wide/assets/bgm/, seam (play to b1 s, jump back to b2 s; nearly identical harmony), the track's own
# ending chords (dominant, tonic) in seconds. Find them by listening plus librosa beat/chroma analysis.
BGM = {"file": "<track>.mp3", "loop": (41.38, 19.55), "cadence": (208.42, 210.07)}

# Original-film framing. Measure the film first (grab frames): where its burned-in subtitles sit after scaling, and
# which corner holds a logo you want pushed out of frame. subband_top None = the film has no subtitles to blur.
FRAME = {"zoom": (1.12, 1.19), "origin": "0% 0%", "subband_top": 878}

# Vertical edition title band; an empty title list hides it
VERTICAL = {"kicker": "<label>", "title": ["<line 1>", "<line 2>"]}

# Covers (make_cover.py): frame second, face box in the 1920x1080 frame (forehead to chin), hook lines
COVER = {"frame": 9.8, "face": [900, 220, 1360, 700], "kicker": "<label>",
         "lines": [[["<hook line 1>", "white"]], [["<hook line 2>", "white"], ["<number>", "yellow"]]],
         "sizes": [140, 104], "byline": "<channel | author>",
         "h": {"zoom": 1.15, "x": 0.0, "y": 0.0, "text_side": "left"}, "v": {"x": 0.4, "sizes": [150, 118]}}
