---
name: pinshu-transcript
description: "Faithful transcript editing and reconstruction of hands-on course demonstrations. Use for transcripts produced from spoken presentations, classroom recordings, livestream recordings, and software demonstration courses; correct STT errors and terminology, remove meaningless speech fillers, rebuild paragraphs, and fully preserve examples, numbers, procedures, prompts, code, commands, parameters, file paths, AI exchanges, and on-screen demonstrations. Do not rewrite the main text as a summary; use pinshu-distill for knowledge distillation."
---

# Faithful Transcript Editing and Hands-On Reconstruction

## Origin and Maintenance

- Original work: Pinshu original (`original`)
- Owner: Aidan (Pinshu)
- Maintainer: Aidan (Pinshu)
- Optional upstream skill: `pinshu-data-cleaning` (not bundled; useful only when the input spans PDFs, images, web pages, audio/video, or multiple versions)
- Distribution status: `bundled` in this English skill collection; installable as a standalone skill

Turn speech-to-text output into a complete, well-structured, readable document that remains faithful to the source. Restore the main text first, then create any derivative content at the end. Never turn “editing” into summarization.

In a course pipeline, this skill edits an immutable raw transcript into the faithful draft. `pinshu-distill` produces the structured guide and `pinshu-course` maintains the series map. Those are distinct required course results, not additional outputs this skill must produce on its own.

## Core Principles

1. **Fidelity first**: Preserve the speaker's views, sequence, tone, and argumentative relationships. Clean only textual noise.
2. **Completeness first**: When in doubt, retain material. Never delete examples, numbers, constraints, procedural details, or emotional expression merely because they appear secondary.
3. **Hands-on work is main-text content**: Software operations, entered instructions, code, parameters, navigation paths, AI outputs, and correction sequences are reproducible knowledge, not incidental classroom chatter.
4. **Separate the main text from derivative content**: A reading guide, key ideas, quotable lines, or social-media copy must not be mixed into or substitute for the main text.
5. **Do not guess through uncertainty**: When a term or on-screen text cannot be confirmed, preserve the context and mark it `[To confirm]`. Never fabricate exact instructions or code.
6. **Name the lesson by its central point**: Read the whole source before naming it. Keep a lesson number only when needed; identify its central question or judgment and a distinctive case, method, or result. If the directory already identifies the document type, keep type labels out of both filename and H1. A title must distinguish this lesson from its neighbors and tell a reader why to open it. An established course timetable title takes precedence where the library requires it.
7. **The raw source is immutable**: Permanently retain the raw transcript. Every deletion in the edited version must remain traceable to the original source. Never modify, overwrite, or delete the raw transcript file.

## Input Boundary: First Decide Whether This Is a Transcript Task

- Use this skill directly when the input is an existing course, interview, livestream, or speech-to-text transcript and the user asks to “preserve the original wording” or “edit the transcript.”
- When the input also includes PDFs, scanned images, web pages, audio/video, multiple versions, or a batch of disorganized sources, use `pinshu-data-cleaning` first if it is installed. It is optional and is not provided by this repository. If unavailable, ask for pre-cleaned Markdown or a transcript, or process only an already clean text subset that this Skill supports; state the excluded material instead of silently skipping heterogeneous-source cleaning.
- This skill may use screenshots, slides, and screen recordings to correct a transcript, but it does not perform batch OCR, format conversion, deduplication, or source-inventory construction for heterogeneous materials.
- Do not invoke the general cleaning workflow merely because the user says “clean up” conversationally. If the intended result is still a faithful main text, this skill remains the primary workflow.
- Route systematic notes, methods, case libraries, and knowledge distillation to `pinshu-distill`; never substitute them for the faithful draft.
- When a course series also requires a catalog, state gates, slide evidence, batch rework, or a cross-course knowledge base, load `pinshu-course` as well.

For course production with an existing manifest, follow its `output_language` for learner-facing prose and use its rendered path keys when course-capture state exists. This English edition does not require a manifest, course-capture, or an English-only learner output: without those tools, honor the user's language and the existing confirmed project paths; confirm the destination before writing a new course. Keep established program identifiers intact.

## Required Reference Loading

Read every applicable reference before editing; references execute the route selected here and never choose a different route.

- **Every transcript**: [`references/editing-rules.md`](references/editing-rules.md) for content typing, terminology priority, STT correction, speech-noise removal, timestamps, and live-session chatter.
- **Course, tutorial, instructor narration, faithfully edited article, or long livestream**: [`references/course-article-editing.md`](references/course-article-editing.md) for first-person authorship, meaningful-content fidelity, structural segments, specialist resolution, semantic anchors, risk notes, article hierarchy, order preservation, reconciliation, retention warnings, and the confirmation loop.
- **Operations, prompts, code, commands, files, parameters, tool feedback, or AI collaboration**: [`references/hands-on-reconstruction.md`](references/hands-on-reconstruction.md) for evidence types, the complete formatting example, incomplete-instruction handling, multi-turn sequences, and the optional recap.
- **Any formal Markdown transcript**: [`references/structure-and-output.md`](references/structure-and-output.md) for searchable titles, paragraph rules, series conventions, the default deliverable, and the complete output example.
- **Every delivery**: [`references/quality-review.md`](references/quality-review.md) for paragraph-level completeness, fidelity, reproducibility, layout, removed-block, visual, terminology, and prohibited-action checks.
- **Formal course-library or batch production**: [`references/course-production-guardrails.md`](references/course-production-guardrails.md) for written numbers, applied corrections, Markdown hygiene, punctuation, library overrides, event-photo use, emphasis, and provenance of experience write-backs.

## Main Workflow

### 1. Read and classify all evidence

Read the complete input, including available visuals and attachments. Identify every applicable content type and reference branch. Completion criterion: the content type, source set, and required references are explicit before editing begins.

### 2. Build the internal proofreading table

Record people, organizations, products, tools, models, abbreviations, capitalization, lesson numbers, numeric facts, user corrections, recurring STT errors, and supporting evidence. **This skill owns the course terminology and correction glossary**: on the first lesson, create `00_Terminology-and-Corrections.md` in the course root, or follow an established local name. Reuse an existing synonymous glossary instead of creating a second one. Before each later lesson, load it; after editing, write back newly confirmed raw-to-correct mappings. A downstream publication or content workflow displays the confirmed spelling, not an STT error.

Apply this priority: explicit user correction > course glossary > clearly legible on-screen text > repeated consistent usage in the same material > contextual inference. Flag changing external facts for separate verification instead of expanding the transcript with web research.

Completion criterion: each correction has evidence and one canonical spelling; the table itself need not appear in the output.

### 3. Restore the faithful main text

Correct STT errors, sentence boundaries, duplicated recognition, slips, capitalization, and units. Remove only content-free fillers, mechanical repetitions, abandoned verbal versions, and pure equipment or administration chatter. Preserve logic, tone, rhetorical force, speaker labels where needed, and every reproducible operation. Remove timestamps unless the user requests a timeline.

Completion criterion: every meaningful unit remains in original order and every deletion is traceable to pure noise in the raw source.

### 4. Apply every active branch

For course prose, keep the instructor's first-person voice and apply the course article rules. For hands-on material, preserve spoken instructions, on-screen text, operations, software or AI output, errors, follow-up instructions, and final results as distinct evidence types in their actual sequence. Apply both branches when both are present.

Completion criterion: no applicable branch is skipped, and no branch rewrites the main text into a summary or systematic notes.

### 5. Structure without reorganizing

Create a searchable semantic filename and heading, then divide the text at the speaker's natural topic boundaries. Improve paragraphs and headings without moving topics, merging dispersed explanations into a new system, or replacing specifics with abstractions. Follow established course-library conventions when they exist.

Completion criterion: headings reveal the speaker's reasoning, while full reading preserves every argument, case, operation, qualifier, and return from a digression in source order.

### 6. Reconcile, confirm, and audit

Compare the draft with the raw source paragraph by paragraph. Resolve uncertainty from source materials first; then give the user one consolidated confirmation list. Apply each confirmed correction immediately throughout the main text and search until the old form is gone. Review every omitted block with: “Would deleting this cause the student to learn less?” Restore it when the answer is yes.

For formal course text, emphasize short key phrases rather than whole sentences; close each `**` pair within its paragraph. Run `references/audit_md.py` for structural checks, then review the opening, a substantive middle passage, and the ending in the actual reading view. Its `PASS` cannot establish semantic fidelity.

For formal course output, run:

```bash
python3 references/audit_md.py <edited-file.md> [--dict <glossary.md>]
```

A `PASS` supplements rather than replaces semantic reconciliation and manual review of three screenfuls in the actual reading view.

## Hard Gate: Frontmatter and Heading Layout

Every formal Markdown file must meet all requirements below:

1. Frontmatter begins on line 1 with `---` and ends with a second standalone `---`. Never leave `tags:`, `course:`, `lesson:`, `title:`, `source:`, or `status:` bare before the body.
2. Include exactly one frontmatter block. When copying content from another draft, remove any old frontmatter copied into the body.
3. Leave one blank line after frontmatter, then add exactly one Markdown H1. The H1 is the document heading and is distinct from a `title` property.
4. Do not repeat frontmatter fields in the body. Update property changes only in the opening frontmatter.
5. After a batch course write, check all four rules in every file. Do not inspect only Lesson 1 or rely on a rendered screenshot.

A course library's explicit convention overrides this default, including a verified no-H1 convention. Apply that exception consistently across the batch.

## Completion Gate

Delivery is complete only when all applicable checks in `references/quality-review.md` pass and:

- the raw source remains unchanged and retained;
- every case, number, judgment, inference, reversal, qualifier, repeated emphasis, instruction, code block, command, parameter, path, tool output, error, correction, and relevant visual detail has an explicit destination;
- the opening, an important middle case, the ending, and the longest middle section have been reconciled with the source, and the opening, middle, and ending have been read in the actual reading view;
- every omitted block is confirmed as pure noise; substantial shortening has a paragraph-by-paragraph removed-noise list and coverage audit;
- executable content preserves line breaks, indentation, symbols, case, and sequence;
- main text and requested derivative sections remain visibly separate, and derivative words never inflate retention measurements;
- all proofreading mappings have reached the main text and user-facing derivative pages; old forms have zero remaining display matches (they may remain in immutable raw sources, glossary mappings, and internal source-trace notes). Edited wording in a quotation is labeled an edited quotation, not passed off as verbatim speech;
- no draft-style confirmation artifact remains after confirmation; substantive risk notices remain separate and attributed claims retain their evidence status;
- `audit_md.py` passes when required, all local links resolve, and manual semantic, visual, and terminology review also passes.

Only after the full text satisfies this gate may you report: “Transcript editing and correction complete; items awaiting user confirmation: 0.” If confirmation items remain, deliver the consolidated list and state the exact unresolved count instead.