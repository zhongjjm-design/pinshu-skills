# Review Loop: Rules and Prompts

Source: adapted from the Gauntlet review loop in echris6/motion-video-kit (MIT) for the brand film teardown genre. In round 1 on the pilot film (a retail brand's anniversary film), all 3 hard defects the reviewer reported were real, but one of its suggestions conflicted with the rules ("replace the generic stock footage with the brand's original footage") and was not adopted. So **verify the reviewer's findings by measurement before changing anything**.

## Rules

1. **The maker never reviews their own film.** For every round, spawn a brand-new subagent as the reviewer.
2. **The reviewer gets only four things**: the path of the final film, a one-sentence brief, the rules file (this skill's `rules.md`, given as an absolute path), and the previous round's review report (verification rounds only). **Do not give it the maker's reasoning or any "here is what I think I fixed."**
3. **Watch only the final film, never the project**: no code, no timeline, no narration script.
4. **For sound, report only what can be measured**: the reviewer cannot hear, so it measures only loudness, silent stretches, and whether sound effects land on picture events. Voice timbre and music quality are judged by a human listening.
5. **No scores**: report only problems, timestamps, and fixes, and end with a verdict: "ready to publish" or "one more round."
6. **Each round fixes the biggest problems.** The next round uses a new reviewer to verify item by item. Stop at "ready to publish" or when only minor details remain; this usually takes 2 to 3 rounds.
7. **Keep a log**: `review/log.md` in the project directory, one row per round: the film, the reviewer's top findings, the verification result, what was changed, and the measurement after the change.

## Full-film review (round 1)

```
You are an independent film reviewer. You did not make this film. Judge only from the film's picture and the sound you can measure, regardless of what the makers meant to say.

Film: <absolute path to the mp4> (<duration>, 1920x1080, with audio).
What it is: <one-sentence brief: the account, which brand film is being broken down, which article it accompanies, who the audience is, which platform, and which device they watch on>.
Standard (must be met): the whole of <absolute path to this skill's rules.md>.
Do not read the project's code, timeline, or narration script.

Method:
- Use ffmpeg to extract one frame every 0.5 s and tile them into contact sheets with timestamps, saved to <temporary directory>. Around each cut, extract dense frames at 30 fps for 0.3 s before and after, and inspect them closely.
- Also make a contact sheet 360 pixels wide (the size of a horizontal film on a phone held upright) to judge whether captions and overlaid text are legible.
- Use frame differencing to find near-static stretches (10 fps; luma difference between adjacent frames below 0.35) and list any longer than 2 s.
- Use ebur128 to measure integrated loudness and true peak, and silencedetect to find silences longer than 1.5 s.
- You cannot hear the audio: do not judge the timbre of the narration or the music; report only what you can measure.

Check each item:
- First 3 seconds: is the first frame a complete picture, and is there something within 3 seconds that makes a viewer stop?
- Things the narration names (people, stores, numbers, objects): is each one on screen within 1.5 s?
- Does the same person, or the same footage from the original film, appear more than once?
- Do overlaid text, labels, and numbers appear when the narration mentions them? Do they cover captions, faces, or the original film's own text?
- At cuts: any flash frames, black frames, or glimpses of the previous or next shot?
- Any violation of the rules file: black-and-white footage, still images over 2 s, the same picture held over 3 s, black-background cards, a full-width black caption band?

Write the report in the user's language (at most 900 characters if Chinese, about 500 words otherwise) to <report path>:
1. By segment: time range, what is on screen, and problems ranked by severity.
2. Layout and transition problems, with timestamps and screen positions.
3. The 6 to 8 most important fixes, ranked by impact, each with a clear description of the fix.
4. Verdict: ready to publish / one more round.
Be direct: no pleasantries and no scores. When you are done, move the extracted frames in the temporary directory to the Trash.
```

## Verification review (round 2 onward)

```
You are an independent film reviewer. You did not make this film. New film: <path>. Previous review report: <path>. <If segment timings have moved, state the mapping from old to new times.>
Standard: <absolute path to this skill's rules.md>.

For each item in the previous report's "most important fixes," state: fixed / partly fixed / still present, with timestamps and evidence. Then look for new problems introduced by the changes (skipped frames, text overlapping text, clipped text, odd frames inside transitions). Use the same method as the full-film review; you may extract frames only around the changed segments.
Write the report in the user's language (at most 500 characters if Chinese, about 300 words otherwise) to <path>. The last line must read "ready to publish" or "one more round (at most 3 items)." When you are done, move the extracted frames to the Trash.
```

## Script review (after the narration script is written, before synthesis)

```
Review the narration script for a <duration> brand film teardown: <script path>. You did not write this script. Standard: section 1 of <absolute path to this skill's rules.md>. Check:
- Facts: can every claim be traced to the original film, the original article, or public reports? Are the numbers, names, and dates correct?
- Order: does the order of the storytelling match the original film and what actually happened?
- Does each section have its own job? Which section is filler?
- Voice: is it "a peer breaking down a case"? Is there any preaching, self-praise, or promotion of the brand?
Return a list of problems ranked by severity, each with one concrete fix, written in the user's language.
```
