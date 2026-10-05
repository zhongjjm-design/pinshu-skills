# Config File (`spec.py`) Field Reference

Everything a film says lives in `spec.py`; how the film is made lives in this skill's scripts. `new_project.py` copies a commented template into the project.

## Required

| Field | Form | Notes |
|---|---|---|
| `VO_SRC` | `"voice/gemini_Charon"` | Narration source folder (relative to the project): the output of `gen_voice.py`, or the folder written by `patch_voice.py` |
| `S` | Scene list | See below |
| `TITLE` | `{"d": 3.4, "src": 0.0, "t1": "...", "t2": "...", "sub": "...", "by": "..."}` | Opening title page: duration, which second of the original film is used as the background, two title lines, a small red label, and the byline |
| `END` | `{"kicker", "title_html", "author", "author_clean", "qr", "qr_text"}` | End card. `author_clean` is the byline for the Douyin edition (it must not contain WeChat Official Account wording); `qr` is the QR code image under `wide/assets/img/` |
| `BGM` | `{"file": "....mp3", "loop": (b1, b2), "cadence": (dominant chord seconds, tonic chord seconds)}` | Music. The loop seam means "when playback reaches b1 seconds, jump back to b2 seconds"; the harmony at both points must be nearly identical. `cadence` is the position of the track's own closing cadence |

## Scene list `S`

Each item is `(type, narration text, params)`. **Joining the narration of all scenes in order must reproduce the text of each section in `sections.json` exactly, character for character** (`build.py` stops with an error if it does not).

| Type | Purpose | Common params |
|---|---|---|
| `full` | Original film full screen with narration | `src` second in the original film; `over` small label at the top right; `clips` multiple shots |
| `comments` | Comment-section screenshots (over a blurred original film) | `src`; uses `COMMENTS` |
| `ask` | Large-text question (over a blurred original film) | `src`; uses `ASK`. Mind the rules: a dark text card held too long makes viewers swipe away, so use real footage whenever possible |
| `chapter` | Chapter card (the first 2.9 seconds are the card, then footage) | `no` number, `t1` title, `t2` subtitle; the first item in `clips` must be a video (it becomes the blurred background) |
| `story` | One person's story | `n` number, `tag` label, `bite` speaker bite name; **a story with a `bite` must be the first scene of its section** |
| `chips` | Key points that pop in one by one | `head` heading, `items` list `[(display text, word that triggers the pop), ...]` |
| `posters` | Poster wall or a single poster | Uses `POSTERS` (starting from `wide/assets/img/hd/p01.jpg`) |
| `end` | End card | Narration is an empty string; params are `{}` |

### Writing shots in `clips`

| Form | Meaning |
|---|---|
| `12.5` | The original film from second 12.5 (cut to it at the start of the scene) |
| `{"src": 12.5, "at": "<word>"}` | Cut to second 12.5 of the original film when `<word>` is spoken (the cut happens 0.12 s early). `<word>` must appear in this scene's narration |
| `{"f": "4801", "ms": 2.0, "at": ...}` | Stock footage `wide/assets/stock/4801.mp4`, starting at second 2 |
| `{"img": "hd/p01.jpg", "at": ..., "full": True}` | An image; `full` fills the whole screen (do not use a card on a black background) |
| `{"gfx": "brand", "at": ...}` | An animated card whose content is defined in `GFX` (name -> HTML; the wrapper gets the class `gk-<name>`, and only `gk-recap` has built-in styles, so style other cards inline in their HTML); `recap` is generated automatically from `RECAP` and accepts `"t2at": "<word>"`, the word at which the recap line draws (default: 2.2 s before the clip ends) |
| `{"flip": 16, "at": ...}` | A fast poster flip |

Flags on a shot: `"card": True` marks the original film's own title card (not enlarged, centered, no frosted caption bar); `"hideover": True` marks an original-film segment that carries its own numerals, so the story number is hidden there; `"quote": "<comment text with a [bold part]>"` overlays a comment card (the name line beside the avatar comes from `COMMENTS["meta"]`, so `COMMENTS` must be filled in when `quote` is used).

## Optional

| Field | Notes |
|---|---|
| `BITE_TEXT` / `BITE_CUTS` | Speaker bites: the exact words (used for captions; check them character by character) and their start and end seconds in the original film (used by `prep_bites.py`) |
| `SPLITS` | `[(phrase, seconds)]`: add a pause in the real silence just before this phrase |
| `SEC_TAIL` | `{section number: seconds}`: silence after a section ends, default 0.4; 0.6 to 1.2 at topic changes |
| `PATCH` | Local slow-down of the narration (`patch_voice.py`); the time points must be measured against that particular take |
| `COMMENTS` / `ASK` / `POSTERS` / `RECAP` / `GFX` | Fill in only when the matching scene type is used |
| `WHOOSH_AT` / `CHIME_AT` | Extra transition whooshes and chimes, by scene index; **indices shift when scenes are added or removed, so update them** |
| `END_BG` | End-card background color, default `#b3161b` |
| `VERTICAL` | Top band of the vertical edition: `{"kicker": ..., "title": [two lines]}`; an empty `title` hides the title band |
| `COVER` | Cover: which frame of the original film, the face position (forehead to chin), the hook line, font size, and the horizontal and vertical crops (see the top of `make_cover.py`) |
| `BITES_DIR` / `OUT_VOICE_SUBDIR` | Compatibility settings for older projects; new projects leave them unset |

## sections.json

`{"sections": [{"j": 0, "text": "<first section narration>"}, ...]}`: one section is one topic. The whole script is synthesized in one pass and then split by section. The section number `j` is also the key used in `SEC_TAIL`.
