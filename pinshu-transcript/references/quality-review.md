# Quality Review

## Step 7: Completeness Validation

Compare the finished text against the raw input paragraph by paragraph. Check especially:

- self-introductions, professional history, team background, and business data;
- side cases, counterexamples, objections, and responses;
- prices, percentages, times, version numbers, filenames, and paths;
- emotionally intense passages, personal reflections, and statements of position;
- every original instruction, follow-up instruction, code block, command, and parameter;
- operation sequence, software feedback, errors, and the speaker's corrections or additions;
- important information visible in screenshots but not fully read aloud.

For long material, validate in chunks, but merge and deduplicate all findings at the end. Do not claim “complete editing” before validation.

## Step 8: Quality Review

### Fidelity

- [ ] The main text has not become a summary or methodological notes
- [ ] No judgment or fact absent from the speaker's words has been added
- [ ] Names, tool names, model names, lesson numbers, and figures are consistent
- [ ] Uncertain content is clearly marked rather than presented with false precision

### Reproducibility

- [ ] Instructions appear in their original context instead of being piled abruptly at the beginning
- [ ] Initial instructions and multi-turn follow-up instructions remain separate and complete
- [ ] Code, commands, parameters, and paths preserve exact formatting
- [ ] Each operation corresponds to the correct tool output
- [ ] Pure equipment noise is gone; reproducible operations remain

### Layout

- [ ] The filename and H1 (when the project uses one) identify the lesson's central question or judgment and distinguishing case, method, or result; they do not substitute a document-type label or date for content
- [ ] The filename and H1 (when present) have matching meaning; date, status, and an already-known document type remain in metadata or the directory
- [ ] Timestamps follow the user's requirement
- [ ] Subheadings are clear and consistent with the rest of the series
- [ ] No ellipsis or placeholder substitutes for content
- [ ] Main text, summaries, checklists, and notes are clearly separated
- [ ] There are no paragraphs beginning with punctuation, comma-ending fragments, or isolated body fragments of 12 characters or fewer
- [ ] There are no five consecutive short paragraphs forming subtitle-style fragments and no ASCII-space simulation of Chinese letter spacing
- [ ] The opening, a substantial middle section, and the ending have been checked in the actual reading view

### Review of Removed Blocks

- [ ] Before delivery, compare against the raw transcript and reread every omitted paragraph or block using this test: “Would deleting this cause the student to learn less?” Restore it immediately if the answer is yes.

### Visual and Terminology Review

- [ ] Visual test: when skimming three screenfuls in reading view, does the eye flow downward, or does a wall of text invite skipping? If it invites skipping, paragraphs are too long or visual anchors are too sparse.
- [ ] Terminology test: search the full text for common STT errors in the subject domain and confirm zero matches; use exactly one spelling for each term throughout.

## Prohibited Actions

- Do not reduce a hands-on demonstration to a few abstract methods.
- Do not label a prompt you rewrote as the speaker's original instruction.
- Do not delete code, parameters, or tool feedback because you do not understand the technology.
- Do not invent content that is obscured, inaudible, or never shown.
- Do not change the speaker's position, personal relationships, or course sequence.
- Do not substitute social-media copy, key ideas, or further reflections for the main text.
- Do not use `date + transcript / cleaned draft / edited draft / master draft` as the final filename or primary heading.
