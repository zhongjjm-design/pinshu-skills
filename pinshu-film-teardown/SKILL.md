---
name: pinshu-film-teardown
description: "Turn a brand film (TVC, anniversary film, or ad film) into a teardown video of about four minutes: real footage from the original film with AI narration, the original speakers' own voices, code-driven animation, and music. Produces a horizontal edition for WeChat Channels and a vertical edition for Douyin, with covers and a QC report. Use for requests such as 'brand film teardown,' 'TVC breakdown,' 'anniversary film teardown,' 'turn this ad film into a breakdown video,' or 'make a video for this brand case article.'"
---

## Provenance and maintenance

- Original status: Pinshu original (`original`)
- Owner: Aidan (Pinshu)
- Maintainer: Aidan (Pinshu)
- Upstream dependencies:
  - HyperFrames (https://github.com/heygen-com/hyperframes, Apache-2.0; rendering. Its bundled sound effects come from Pixabay under the Pixabay Content License: commercial use, no attribution required)
  - GSAP (https://gsap.com, standard no-charge license; loaded from a CDN inside the page)
  - BaoCut (https://github.com/JimLiu/baocut, MIT; Chinese transcription for per-character timing)
  - Gemini TTS (Google API; each user supplies their own key)
  - Demucs (https://github.com/adefossez/demucs, MIT; optional, vocal separation)
  - FFmpeg
  - librosa (ISC)
  - Source Han Serif (Adobe, SIL OFL 1.1; downloaded when a project is created)
  - Hiragino Sans GB is a macOS system font and is not distributed with this skill (on Linux, install Noto Sans CJK SC instead)
- Original capabilities: the complete method for this film genre (brand film teardowns): captions and cuts anchored to real pronunciation; the whole narration synthesized in one pass and cut only at measured silences; warnings for the original film's own edit points; music fitted so its closing cadence lands on the end card; horizontal and vertical editions plus covers; an independent review loop and QC; and all the rules and pitfalls collected while making the pilot film (a retail brand's anniversary film)
- Distribution: `bundled`; the public English edition lives in `zhongjjm-design/pinshu-skills`; the private Chinese edition adds Chinese-language documentation

# Pinshu Brand Film Teardown

Turn a brand film into a commentary video in the style of "a peer breaking down a case." Outputs: a horizontal final film (WeChat Channels), a vertical final film (Douyin), a horizontal and a vertical cover, publishing copy, a QC report, and a review log.

**One film = a project folder (original film, narration, assets) + `spec.py` (what this film says) + this skill (how it is made).** For a new brand, change only `spec.py` and the assets, never the scripts.

## Before you start

1. **First read the whole of `references/rules.md`.** It holds the current rules; reviews and QC are judged against it.
2. Clarify three things: which account the film will be published on (read that account's profile), which article it accompanies, and where the highest-quality version of the original film is (if the client has the master file, ask for it first; convert HEVC to H.264 before use).
3. Run the environment check and fill any gaps first: `python3 scripts/doctor.py`. Use one Python with numpy, soundfile, pillow, and librosa installed for the whole pipeline.

## Workflow: ten steps, three stops for the user

| Step | What to do | Command | Stop |
|---|---|---|---|
| 1 Create the project | Create the folders; gather the original film, sound effects, fonts, and the config template | `new_project.py <project dir> --film <film>.mp4` | |
| 2 Screen the original | Make a contact sheet of the original film at one frame per second and list everyone who appears; note which seconds each story, each person and each speaker bite occupies; measure where the film's own burned-in subtitles sit and which corner holds a logo, and put that in `spec.py` as `FRAME` | ffmpeg frame extraction | |
| 3 Write the script | Peer-breakdown voice; list the facts; spawn a separate subagent to critique it with the script review; write `sections.json` | `references/review-prompts.md` | **(1) The user approves the script** |
| 4 Narration | Synthesize the whole script in one pass (with a warm-up sentence); slow down rushed words locally; for speaker bites, **first put the exact words and their start and end seconds (from step 2) into `spec.py` as `BITE_TEXT` and `BITE_CUTS`, then cut them** | `gen_voice.py`, `patch_voice.py`, `prep_bites.py` | The user listens to the full narration |
| 5 Write the config | The remaining scenes, shots, labels, pauses, end card, and cover go into `spec.py`; scene texts joined in order must reproduce `sections.json` exactly (`build.py` stops if even one character is left out) | `references/spec-format.md` | |
| 6 Build | Anchor captions and cuts to real pronunciation; clear every warning about the original film's edit points | `build.py` | **(2) Render the first 30 seconds for the user** |
| 7 Music | Pick a piano piece from a music library and edit it so its closing cadence lands on the end card | `fit_music.py` | |
| 8 Render, mix, QC | Low-memory rendering, mixing, and the QC checks | `render.py`, `mix.py`, `qc.py` | QC PASS |
| 9 Review loop | An independent reviewer sees only the final film; verify findings by measurement before changing anything; 2 to 3 rounds; keep a log | `references/review-prompts.md` | Until the verdict is "ready to publish" |
| 10 Deliver | Vertical edition, covers, publishing copy; go through the publish checklist | `build_vertical.py`, `make_cover.py` | **(3) The user watches the final film** |

At each stop, give the user something to watch or look at directly (a film, a sample, a cover), not command-line output. Batch changes before rendering; do not re-render for a single small flaw.

## Commands (run inside the project directory; `S` is this skill's scripts directory)

```bash
S=~/.agents/skills/pinshu-film-teardown/scripts           # adjust if the skill is installed elsewhere
python3 $S/doctor.py .                                   # check the environment and project files
python3 $S/new_project.py <project dir> --film <film>.mp4  # create a project
python3 $S/gen_voice.py sections.json --warm "<warm-up sentence>"  # full narration -> voice/gemini_Charon/
python3 $S/patch_voice.py                                # optional: slow down locally per spec.PATCH
python3 $S/prep_bites.py                                 # fill BITE_TEXT and BITE_CUTS in spec.py first, then cut the bites
python3 $S/build.py                                      # generate wide/index.html and timeline.json
python3 $S/fit_music.py                                  # fit the music -> wide/assets/bgm/<track>_fit.wav
python3 $S/render.py wide wide/renders/raw.mp4           # render (no music)
MIX_NO_FADEOUT=1 python3 $S/mix.py wide/renders/raw.mp4 wide/assets/bgm/<track>_fit.wav wide/renders/<final>.mp4 soft
python3 $S/qc.py wide/renders/<final>.mp4 timeline.json qc wide/renders/raw.mp4
# Vertical edition (Douyin): first render a clean horizontal edition with no captions and no QR code
CLEAN_FOR_VERTICAL=1 python3 $S/build.py && python3 $S/render.py wide wide/renders/clean.mp4 && python3 $S/build.py
python3 $S/build_vertical.py build wide/renders/clean.mp4
python3 $S/render.py vertical vertical/renders/raw.mp4
python3 $S/build_vertical.py mux vertical/renders/raw.mp4 wide/renders/<final>.mp4 wide/renders/<vertical-final>.mp4
python3 $S/make_cover.py                                 # covers -> wide/renders/cover_16x9.png, cover_3x4.png
```

If the config file is not named `spec.py`, set `SPEC=<path>`. **BaoCut is required**: `gen_voice.py`, `patch_voice.py` and `prep_bites.py` need its per-character timings, and without it the narration step stops after the voice has already been paid for, so run `doctor.py` first. `PINSHU_TRANSCRIBE=off` only lets `build.py` and `qc.py` run without BaoCut, at the cost of skipping pause verification and the stutter check; both must be done before delivery.

## Hard rules at a glance (full text in `references/rules.md`)

- The main picture is real footage. When discussing other companies' practices, do not use this brand's footage.
- A still image stays on screen for at most 2 seconds at a time, and the same picture for at most 3 seconds. No black-background cards or black-background infographics. **No black-and-white footage.**
- Captions are white text with an outline and no full-width black band; punctuation follows the Netflix Chinese style guide.
- Synthesize the narration in one pass and cut only at measured silences; the music's closing cadence lands on the end card.
- Covers show a face and emotion, with no text over the face. WeChat Channels short titles contain no punctuation.
- The Douyin edition must not contain a WeChat QR code or WeChat account wording. Tick the AI-generated declaration on both platforms.

## Record every change

Record every change (picture, caption format, copy, transitions and effects, sound, rendering) in `references/pitfalls.md` as soon as you make it: symptom (with the reviewer's feedback as given), cause, fix, and how to prevent it. When a lesson becomes a rule, update `references/rules.md` too. This record is what makes the skill faster with every film.

## Reference files

- `references/rules.md`: current rules and the publish checklist
- `references/pitfalls.md`: pitfalls and fixes (past lessons, organized by problem)
- `references/spec-format.md`: field reference for `spec.py`
- `references/review-prompts.md`: review-loop rules and three prompts

## Known limitations

- The brand color (red) is set in `assets/wide.css` and in the end-card background; changing the brand color requires editing the styles.
- GSAP loads from the web, so rendering needs an internet connection.
- The warning for the original film's edit points detects only hard cuts. Gradual transitions such as flashes to white and dissolves are missed; keep clip boundaries at least 0.3 seconds away from them.
- The automated test (`tests/self_test.py`) runs build, vertical edition, mixing, and QC on synthetic material. It does not cover real rendering or real narration.
