# Screenshot Prompt Recovery and Reversal Corrections

Use this reference when a course note is being finalized from screenshots, the user supplies prompt text through malformed rich links, or the user reverses an earlier terminology confirmation.

## 1. Authority and reversal rule

Use this source order for course wording:

1. The user's latest explicit correction;
2. Clearly visible text in the newest course screenshot;
3. Earlier user confirmations;
4. Transcript/STT inference;
5. External lookup, only for independent fact verification—not to rewrite course wording.

A correction such as `Token Step → Token Rank → Token Step` is not three variants to preserve. The latest explicit correction wins. Propagate it to all current outputs and remove the superseded form from formal notes. Do not keep stale “confirmed” labels merely because the earlier correction was once accepted.

After a reversal:

- Search the whole course tree for both the superseded and current form;
- Update faithful draft, structured lecture, course map, frontmatter, knowledge cards, pending lists, and status counts;
- Search again: superseded form must be zero unless quoted in a correction log for a clear reason;
- Confirm the current form appears in every required artifact.

## 2. Distinguish prompt types

Do not merge prompts merely because they appear in the same lesson.

- **Case prompt**: concrete task inputs, accounts, URLs, quantities, time range, and desired output.
- **Universal startup prompt**: reusable instructions for restating the task, asking questions, drafting acceptance evidence and boundaries, generating a `/goal` prompt, waiting for confirmation, then starting Goal.
- **Commentary/analysis text**: explanations such as “先复述，避免Codex理解错任务”; useful in the lecture, but not part of the prompt unless visibly included in the prompt block.

Track each item independently as `confirmed`, `partial screenshot`, or `missing`.

## 3. Recovering prompt text from screenshots

1. Transcribe only visible text.
2. Preserve commands and punctuation exactly where legible, especially `/goal` versus `goal` or `Go`.
3. If the screenshot crops the right side of a line, stop at the last visible word and mark the line incomplete. Never reconstruct the missing tail from a later explanation slide.
4. Ask for a wider or continuation screenshot before marking the prompt complete.
5. A later screenshot explaining the prompt's four principles does not fill a cropped line in the prompt itself.
6. State explicitly when a screenshot contains no model tier, character limit, or other requested field.

## 4. Repairing malformed rich-link input

Chat surfaces may turn the last URL plus following Chinese requirement into one giant URL. When this happens:

- Use the visible intended account path as the URL boundary;
- Separate trailing natural-language requirements from the URL;
- Normalize link presentation, capitalization, spacing, and punctuation only;
- Do not add requirements or treat automatically attached web-page content as part of the course prompt;
- Label the result “原文，链接边界与排版已校正” rather than claiming byte-for-byte transcription.

## 5. Status bookkeeping

When some items are confirmed and others remain missing:

- Change headings from `待确认` to `已确认与待补充`;
- Reduce the pending count in the course map atomically;
- Explicitly separate “case prompt confirmed” from “universal prompt still missing”;
- Keep the lesson in draft status until the remaining source-dependent items are resolved;
- Do not claim “待确认项：0” until screenshot completeness and terminology zero-residual checks both pass.

## 6. Minimum QA

Run two scans after every correction batch:

### Superseded-form scan

Search old product names, old commands, malformed URL tails, stale pending counts, and obsolete “still unconfirmed” phrases. Expected result: zero, except justified quotations.

### Current-form coverage scan

Verify the latest product name, command, prompt type, and confirmation state appear in:

- Faithful draft;
- Structured lecture;
- Course map;
- Frontmatter/status fields where present.

Report exactly what remains incomplete. Do not convert a partial screenshot into a finalized prompt.
