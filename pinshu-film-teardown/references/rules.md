# Brand Film Teardown: Current Rules

This file holds only the rules **currently in force**. The note in parentheses after each rule gives its source: reviewer feedback or a review finding. The dated history is in `pitfalls.md`.
New feedback goes into `pitfalls.md` first; once it is confirmed as a rule, update this file. When the two disagree, this file wins.

## 1. Script

- The voice is "a peer breaking down a case": facts first, then reasons; conversational; no piling up of punchlines; no preaching, no self-praise, no promoting the brand (feedback: the narration sounded too AI-like, more like a promotional film than a case commentary).
- Put verbal fillers only where a real person would naturally say them: 3 to 5 per script, each kind used once. Replace jargon with plain words and split long sentences (feedback: do not make it colloquial just for the sake of it).
- The structure follows the article's sections. Length is set by the content; do not squeeze it into 60 seconds.
- Moving from a specific case to a general conclusion needs a connecting phrase (such as "so what this shows is").
- The ending ties back to the opening to close the loop, then gives peers one judgment they can take away. Do not end on a sentiment (feedback: the ending felt weightless).
- Leave a beat (about 0.8 seconds) after a rhetorical question.
- Move the fact list forward: before narration is recorded, find a source (the original film, the original article, public reports) for every number, name, and date.
- Check the speakers' own words character by character against the transcript; never drop a single word from memory (feedback: a word was missing from a speaker's self-introduction in the captions).

## 2. Narration

- Default voice: Gemini TTS, Charon, with the style note "like chatting with a peer about a case: relaxed, opinionated." Add a warm-up sentence at the start and cut it afterwards. The user's choice of voice prevails; if that voice is not available, say so instead of substituting another.
- **Synthesize the whole narration in one pass**, then split it at the real silences between sections. Synthesizing each section separately makes the voice drift until it sounds like two people (feedback: it sounded like two different speakers).
- **Never cut narration by the transcript's per-character timings** (they are off by one or two hundred milliseconds, so the cut lands in the middle of a word; feedback: very mechanical, no human feel). Narration on the same topic plays continuously; pauses are added only inside measured silences.
- Before trimming a breath pause, transcribe the short stretch just before it on its own and confirm it is not a normal punctuation pause; otherwise leave it alone (after full-stop pauses were compressed, feedback was that it sounded rushed).
- Slow down a few rushed words locally with `patch_voice.py`; do not re-synthesize (re-synthesis changes the voice).
- Add 0.6 to 1.2 seconds of extra pause at topic changes (feedback: there were no pauses between sections and the delivery felt too dense).
- Do not use a clone of the user's own voice for case commentary; the user's own voice is reserved for digital-avatar content.
- Use naturalness-scoring models only to discard bad takes, never to rank voices (their ranking ran opposite to human listening).

## 3. Picture

- **The main picture must be real footage** (feedback: it should not look like a slide deck). Text cards are only for chapters and key points.
- **When discussing industry-wide problems or other companies' practices, do not use this brand's footage.** Use generic corporate stock footage (cities, meetings, award ceremonies, handshakes, applause) with no brand names visible, and avoid foreign faces where possible.
- Every specific thing the narration names gets matching footage. If nothing fits, find stock footage to fill the gap rather than padding with warm, emotional shots.
- Footage must make clear who is doing what. For list-style narration, use one shot per word, about 1 second each.
- The same person appears at most once in the whole film; the same footage is used only once across adjacent scenes; the same group of shots is never replayed unchanged (feedback: a sequence of images was shown twice).
- Prefer bright shots in which people are recognizable. Before starting, screen the original film person by person (a contact sheet at one frame per second).
- **A still image stays on screen for at most 2 seconds at a time**, except when the narration is about that very image. End a story with a shot of that person moving in the original film (feedback: static still montages holding for several seconds look bad).
- **The same picture is never held for more than 3 seconds in a row** (feedback: a blurred picture stayed on screen far too long).
- **No "card on a black background" layout.** Images fill the whole screen, and the picture is mainly bright real footage (feedback: dark screens look ugly).
- **Recaps and summaries use moving footage of real people**, not black-background infographics (feedback: a black-background recap with a scale looked messy and oppressive).
- **No black-and-white or desaturated footage**: Chinese audiences read it as a sign of mourning (feedback: it suggested a death). To express "dull" or "uninteresting," pull back, blur, or darken while keeping the original color.
- No text cards with slow push-ins, no persistent large title bands, no glows, and no grids of equal-weight cards (feedback: these look cheap).
- Semi-transparent color blocks let the background show through; put opaque backing under overlaid text.
- Large numbers use Source Han Serif, not Didot (its numeral 1 looks like a Roman numeral I).

## 4. Captions

- Horizontal captions are size 62, white text with a thin black outline and a soft drop shadow, with **no full-width black band** (feedback: such a wide and tall black caption background is unusual and does not look standard).
- When the original film's burned-in captions need covering, use only a narrow, light frosted bar (about 200 pixels, not darkened). With a new original film, first measure the height of its captions in the frame and set `FRAME["subband_top"]` in `spec.py` (`None` when it has no burned-in captions); the scale and the corner it grows from are set in `FRAME` too.
- Punctuation follows the Netflix Simplified Chinese style guide: full-width commas, full stops, semicolons, and colons are replaced by spaces; the enumeration comma (the Chinese list separator) is kept only in lists; quotation marks are used only for the speakers' own words.
- Caption timing is anchored to real pronunciation. Each block lasts at least 0.6 seconds, blocks never overlap, and blocks shorter than 5 characters merge into the next block.

## 5. Transitions and motion

- Video to video is a hard cut, never a fade up from black (feedback: "dark, then bright again" looks like a blink).
- Every clip runs 2 extra frames (about 0.07 s) underneath the next one, and the next one comes in with a very short 2-frame transition. This hides the renderer's misdrawn first frame. **Do not revert to a plain hard cut.**
- Exits are staggered, last in, first out. Labels finish leaving before the new picture appears.
- The original film's own title cards are not enlarged, are centered, and get no frosted caption bar during those seconds.

## 6. Sound and music

- Commentary films need music and sound effects (feedback: without background music and sound effects the film felt flat). Music sits underneath, transition sounds mark topic changes, and light effects accompany numbers, labels, and page turns.
- Default music: sparse, darker solo piano chosen from a music library (feedback: soft, slightly dark, barely noticeable yet exactly right). Use `mix.py ... soft`, which keeps the music 14 dB below the narration.
- Do not use AI-composed music as the main score. Do not reuse the original film's music (feedback: taken out of its context, it does not fit our picture and narration). Separate vocals from the speakers' original audio first.
- Edit the music so that the track's real closing cadence lands on the end card (feedback: the ending always felt unfinished). Use `fit_music.py`.
- The speakers' original audio is at most 1 dB louder than the narration. Final loudness is -14 LUFS with a true peak no higher than -1 dBTP, using fixed gain and no dynamic compression (feedback: the sound suddenly dropped a lot).

## 7. Covers and titles

- The cover uses a frame from the original film **with a face, emotion, and brightness** as the main image, plus one hook line (a number or a question) in bold type. Text-only covers do not attract viewers.
- **No text over faces** (feedback: the text covered a child's face on the horizontal cover). Measure the face position first; `make_cover.py` blocks overlaps. Crop the horizontal 16:9 cover and the vertical 3:4 cover separately around the face.
- WeChat Channels short titles **must not contain any punctuation** (no commas, question marks, or quotation marks).

## 8. Platform publishing

- WeChat Channels gets the horizontal edition, with the original WeChat Official Account article attached as the extended link. No paid promotion (feedback: in-feed ads are not needed), but the first 3 seconds and the cover still matter.
- Douyin gets the vertical edition. The ending must not contain a WeChat QR code, "scan to follow" wording, or WeChat Official Account wording (Douyin's short-video mounting rules, section 4.5). Use `CLEAN_FOR_VERTICAL=1` to render a clean horizontal edition, then wrap it into the vertical edition.
- On both platforms, **tick the "AI-generated / synthetic content" declaration** (the narration is an AI voice; China's Measures for Labeling AI-Generated Synthetic Content took effect on 2025-09-01).
- Do not tick the originality declaration: the film uses a large amount of the brand's original footage.
- Log the source and license of all outside material (library music tracks, external video).

## 9. Publish checklist (every item ticked before publishing)

1. The review loop reached "ready to publish," and every hard defect is fixed.
2. QC passed: duration, black screens, first frame, loudness, true peak, sound on the end card, frozen picture, first frame at cuts, stutters.
3. Fact check: every number, name, and date has a source.
4. The user has watched and listened to the whole film once, with nothing that breaks immersion.
5. One horizontal and one vertical cover, with no text over faces.
6. Platform editions: horizontal for WeChat Channels, vertical for Douyin (no QR code, no WeChat Official Account wording).
7. Publishing copy: a short title without punctuation, a description, and hashtags; tick the AI declaration when publishing.

## 10. How to work

- Show the user a film first and change what they point to. On big jobs, deliver something watchable every 30 to 60 minutes.
- When one problem is pointed out, immediately scan the whole film for the same kind of problem and fix them all at once. Batch small flaws into a single render.
- Verify reviewer findings and outside suggestions by measurement first, then sort them into "should fix," "the user decides," and "does not hold." Do not adopt suggestions that conflict with this file.
- Record every change in `pitfalls.md`: symptom (with the feedback as given), cause, fix, and how to prevent it.
