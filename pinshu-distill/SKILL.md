---
name: pinshu-distill
description: "Use when users want to reorganize faithful transcripts, courses, interviews, talks, or livestreams into structured study guides, methods, cases, or formal cross-course topic syntheses. Do not use it to preserve the original speaking sequence or to run tutoring, quizzes, or personal learning records."
---

# Pinshu Knowledge Distillation

## Provenance and maintenance

- Original work: Pinshu (`original`)
- Owner: Aidan (Pinshu)
- Maintainer: Aidan (Pinshu)
- Optional upstream skills: `pinshu-data-cleaning` (not bundled), `pinshu-transcript`
- Downstream learning skill: `pinshu-study`
- Series orchestration skill: `pinshu-course`
- Distribution status: `bundled`

Reorganize stable source material into knowledge that stands alone and can be reused. For courses, default to a structured study guide. Create a formal cross-course topic synthesis only after the required lessons are available. `pinshu-study` owns active-recall cards, tutoring, drills, and personal learning records.

## Scope

Use this skill for:

- structured study guides, course notes, and standalone learning material;
- extracting methods, models, SOPs, cases, or tools;
- reorganizing knowledge from talks, interviews, panels, or livestreams;
- formal cross-course topic syntheses after the relevant lessons are complete.

Route elsewhere for:

- an edited transcript that preserves the speaker's wording and sequence -> `pinshu-transcript`;
- review cards, quizzes, tutoring, or error-based drills -> `pinshu-study`;
- progress, checkpoints, and pending synthesis leads across a course series -> `pinshu-course`.

If the user says only "organize this" and the desired result is unclear, ask whether they want a faithful transcript or structured knowledge. If the target is clear, proceed without asking.

## Upstream gate

Before drafting, confirm that:

1. the source and lesson identity are clear;
2. the transcript has received necessary cleanup and terminology correction;
3. uncertain passages are marked;
4. the availability of images, slides, board work, or worked examples is known;
5. multiple versions have not been silently merged.

If the source still contains transcript-level errors, return it to `pinshu-transcript`. For heterogeneous corruption, missing pages, ordering errors, or uncertain provenance, use `pinshu-data-cleaning` only if it is installed; it is not provided by this repository. Otherwise request pre-cleaned Markdown or a transcript, or continue only with a clearly identified clean-text subset. Do not silently omit unsupported material or infer content while distilling it.

For course production, learner-facing prose follows the manifest's `output_language` or the user's explicit preference; an omitted field means `match-user`, with source language as fallback. Stable IDs, frontmatter keys, enum values, and program fields remain English. When course-capture state or a manifest exists, save only to its rendered path keys. Without one, preserve the existing confirmed project paths; for a new course, confirm an explicit path map before writing.

## First decision: choose the requested result

### Route A: structured guide for one lesson

Reorganize one lesson into a guide for second-pass learning. You may change the lecture order, but must retain more than its conclusions. Choose the primary structure from the lesson's main learning task, then embed only the cases, procedures, source texts, or other submodules that actually occurred. Never invent stages to fill a template.

Read `references/structured-study-guide-rules.md`. For professional instruction, cases, medical content, or visually dependent procedures, also read `references/professional-course-source-safety-and-visual-gates.md`.

### Route B: formal cross-course topic synthesis

Use this route only when a complete module or course is available. Merge the same concept, method, case, disagreement, and change across lessons into one authoritative topic entry.

Read the cross-course section in `references/structured-study-guide-rules.md`. A lesson's "pending synthesis leads" are input hints, not finished topic entries.

### Route C: other knowledge distillation

For talks, interviews, sales livestreams, methods, and competitor analysis, read `references/general-distillation-patterns.md`.

## Core result for a structured study guide

The guide serves the learner, not the template. Prioritize:

1. clear emphasis;
2. coherent organization;
3. standalone comprehension without replaying the source;
4. a clear place for the instructor's distinctive reasoning, cases, mnemonics, critiques, and experience;
5. explicit source identity.

Use no universal length threshold and do not optimize for a contrived perfect score. Each important module should usually contain:

```text
Question and prerequisites
-> Core judgment
-> Why it holds
-> Comparisons and conditional branches
-> Complete case
-> Misconceptions, counterexamples, and limits
-> Sources
```

Tables, models, and diagrams should expose relationships. They do not replace necessary explanation or cases.

## Information completeness

Structure is not summarization. Every distinct unit of knowledge must have a destination, including:

- core concepts and judgments;
- reasoning, conditions, and counterexamples;
- cases, numbers, and tools;
- the instructor's distinctive views and critiques of the source material;
- valuable side discussions;
- safety, compliance, and factual limits.

Merge mechanical repetition. Lower-priority or high-risk material may move to sections such as "Instructor Perspective," "Needs Verification," or "Not for Training," but it must not disappear silently.

## Source identity

Distinguish at least:

1. explicit statements by the author or instructor;
2. editorial restructuring based on the source;
3. external authoritative additions;
4. unverified, disputed, or simulated material.

A spoken course is not automatically factual. Layer verification for income claims, medical guidance, medication, law, platform rules, and guaranteed outcomes. Preserve the instructor's view without rewriting it out of existence or elevating it into consensus. Place source identity and real-world limits beside each high-risk claim, table, or map; a single disclaimer at the end is insufficient.

## Formal cross-course topic synthesis

- Keep one authoritative topic entry per knowledge object.
- Record new conditions, cases, changes, and sources from other lessons.
- Keep distinct objects, schools, or course editions separate even when names overlap.
- Link methods to their cases.
- Separate source texts, instructor views, external standards, and editorial analysis.
- When material has index value only, create a pointer instead of copying the full text.
- The result must answer where the topic appeared, which lesson covers it most completely, and what later lessons added or changed.

## Layout

- Use exactly one H1.
- Let heading levels express knowledge relationships, not timestamps.
- Give each paragraph one complete idea; avoid subtitle fragments and walls of text.
- Use bold for core judgments, definitions, and important distinctions, not as continuous highlighting.
- Place each case near the method it illustrates instead of collecting all cases at the end.
- Keep reader-facing prose natural. Put engineering fields in frontmatter, hidden comments, or production-control files.

## Quality assurance

Run mechanical checks for frontmatter, one H1, heading spacing, links, images, tables, placeholders, and terminology.

Use an independent semantic review to check whether the draft:

- omitted any distinct unit of knowledge;
- introduced reasoning absent from the source;
- changed the strength of a judgment or its conditions;
- separated a case from its method;
- presented an instructor's view as fact;
- merged different objects incorrectly;
- can genuinely be learned without the source.

The writer cannot be the only reviewer. A script reporting `PASS` does not prove that learning material is sound.

## Save and stop

- Follow the current project's path rules and any explicit user destination; do not save to three locations by default.
- Keep final guides, formal topic syntheses, and internal candidates separate.
- Hand requests for cards or drills to `pinshu-study`.
- Stop when the requested result is complete. Do not generate promotional posts, social copy, or unrelated derivatives by default.
