# Transcript-First Order for Dual-Document Delivery

## When to Use

Use this reference when the user continuously supplies complete transcripts from courses, interviews, talks, or expert presentations and asks to “organize this,” “organize this talk,” or “put it into the asset library,” without explicitly requesting only a summary.

## Core Correction

“Organize the transcript” and “summarize the course” are different tasks. Never skip the faithful transcript and output only a summary merely because a structured lecture displays value more readily.

Default delivery order:

1. **Faithfully edited transcript:** the corpus master;
2. **Systemized lecture / summary version:** a derivative of the transcript;
3. Other models, quotations, and action checklists: derive only when needed.

A summary comes after the transcript. It cannot occupy the transcript’s place or mix summary prose into the instructor’s first-person body.

## From Collection State to Execution State

When a user sends a long transcript over multiple messages:

- Before the user finishes: collect only. Do not summarize early or interrupt with interim summaries;
- When the user labels “Part 1 / Part 2 / Part 3,” record boundaries and terminology pending confirmation;
- When the user says “that is everything” or “start organizing,” or the final part contains a clear lesson ending, enter execution if the overall task was already explicit;
- If “organize” could still refer to both a faithful transcript and a lecture, default to both drafts rather than selecting the lecture alone;
- If only one can be completed first, it must be the faithful transcript.

## Responsibilities of the Two Documents

### 01 Faithfully Edited Transcript

- Preserve the instructor’s first-person voice;
- Preserve original speaking order and development of the argument;
- Preserve every case, number, person, product, transition, question, and qualifier;
- Delete only meaningless fillers, mechanical repetition, stalls, and course-process noise;
- Normalize high-confidence STT errors directly and consolidate uncertain items at the end;
- Do not introduce editorial models, applicable boundaries, or rebuttals; those belong in the lecture.

### 02 Systemized Lecture / Summary

- May reorganize order, extract models, and add applicable conditions;
- Must be based on the faithful transcript rather than replace it;
- Must label editorial extraction rather than present it as instructor wording;
- May place facts pending verification in the lecture or a separate file without contaminating the faithful body.

## Default File and Directory Structure

When the user asks for an asset directory by instructor or expert, reuse an existing expert-talk directory in the library rather than inventing a new system. Suggested structure:

```text
[Instructor]·[Topic]/
├── 01_[Instructor]·[Topic]·Proofread-Transcript.md
└── 02_[Instructor]·[Topic]·Systemized-Lecture.md
```

If the current library uses another convention, follow existing examples. Update the directory index when necessary.

## File-Operation Gate

- When the user explicitly says “create the folder and put the files there,” task intent and scope are already clear;
- If the environment imposes file-operation acceptance, use one minimal notice: operation type, file type, full path, directory verification, and governing convention;
- Do not reopen an already settled dual-draft design during the notice or add rounds of synonymous confirmation;
- Once approved, create the directory, transcript, lecture, index, and readback verification in one execution.

## Acceptance

- [ ] `01` is a complete first-person faithful transcript, not a summary;
- [ ] `02` is the structured summary;
- [ ] The two documents are physically separate and clearly linked;
- [ ] The summary did not replace or contaminate the transcript;
- [ ] The transcript covers the opening, critical middle cases, and course ending;
- [ ] All uncertain terminology is delivered in one consolidated list;
- [ ] The user-specified asset library and existing directory conventions were reused;
- [ ] Both files and the index were read back after writing.

## Typical Failures

- The user asks to “organize the transcript” and receives only a course summary;
- Interim summaries interrupt segmented source collection and fragment later content;
- The faithful transcript uses third-person language such as “the instructor believes”;
- Editorial rebuttals, boundaries, or formulas are inserted into the transcript;
- The summary is numbered `01` and the transcript is placed afterward;
- The user already approved both drafts and a folder, but the agent continues explaining the process instead of executing.
