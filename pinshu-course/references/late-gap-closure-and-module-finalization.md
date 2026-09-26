# Closing a Module After a Late Missing Lesson Arrives

Use this workflow when non-contiguous course input created a module gap, the user later supplies the final missing lesson, and the module becomes complete for the first time.

## Core Judgment

“Filling one missing lesson” triggers two state transitions:

1. **Per-lesson state:** the lesson moves from awaiting input to paired drafts complete and preview acceptance passed.
2. **Module state:** the module moves from `N-1/N` to `N/N`, which requires module-level closeout rather than a one-line table-of-contents update.

Do not handle this as an ordinary single-lesson task.

## 1. Determine Whether the Material Forms a Complete Lesson

Verify at least:

- whether the opening contains a formal start or stable topic anchor;
- whether the ending contains a dismissal, the end of Q&A, a pointer to the next lesson, or another boundary;
- whether a system-level `[truncated]` marker, continuation request, or obvious large omission appears;
- whether a locally incomplete quotation, spoken fragment, or STT segment affects only one citation rather than the lesson boundary.

### Local Incompleteness Does Not Equal Whole-Lesson Truncation

If the lesson has a complete beginning and end and only one quotation, name, or spoken/recognized sentence is incomplete:

- create the paired drafts normally;
- record the local gap explicitly in an editorial note, risk boundary, or pending-verification entry;
- do not complete the original wording from common knowledge;
- do not mark the whole lesson `awaiting-full-text`.

Return to collection state only if the system truncated the material, the latter portion of the lesson is missing, or the user explicitly says that submission is incomplete.

## 2. Resolve Differences Between the Official Title and the Classroom Self-Introduction

Authority order:

```text
official course directory / confirmed course map
> classroom self-announced title
> title inferred from STT
```

Execution rules:

1. Use the official title consistently in the filename, H1, `original_title`, course-map row, and preview filename.
2. Preserve “the classroom self-announced title was...” in the faithful transcript's editorial note and the lecture introduction.
3. Do not force the two titles to become identical or discard the self-announced title.
4. If the titles may indicate genuinely different courses rather than wording variants, pause and ask the user.

## 3. Preserve a Method System That Evolves During the Lesson

A lesson may begin by announcing “six methods,” then add a seventh through interaction or merge one method into another.

Preserve all of the following:

- the count announced at the beginning;
- additions that emerged through classroom interaction;
- the instructor's final consolidation;
- a systematized-lecture overview based on the final classroom state.

Do not erase how the method system formed and changed merely to keep the table of contents neat.

## 4. Course-Map State Surfaces Must Update Atomically

After filling the final missing lesson, inspect and update together:

1. frontmatter `current_progress`;
2. frontmatter `next_lesson`;
3. set of received transcripts;
4. set of lessons with paired drafts;
5. accepted-lesson set;
6. completed modules;
7. current module;
8. next lesson;
9. module completion ratio;
10. total organized lesson count across the course;
11. the lesson's table-of-contents row and paired-draft links;
12. the lesson's knowledge navigation;
13. notes in later organized lessons that say this lesson is missing or archived non-contiguously;
14. stale wording in later module-closeout sections such as “missing lesson,” `N-1/N`, or “do not perform cross-topic synthesis”;
15. the end-of-file next-lesson note.

### Required Residual Scan

Search at least for:

- `lesson-XX-awaiting-input`
- `lesson-XX-not-received`
- `lesson-XX-gap`
- `N-1/N`
- `(missing-lesson)`
- `acceptance-in-progress`
- `next-lesson=lesson-XX`
- `current-module=old-module`

Only a zero residual count permits declaring the module closed.

## 5. Closing the Module Automatically Triggers Five Assets

When the module first reaches `N/N`, create or update:

1. `{cross_lesson_methodology}`
2. `{case_library}`
3. `{tools_and_checklists}`
4. `{fact_checking}`
5. `{practice_and_assignments}`

The braces denote semantic path-map keys, not literal English directories. Resolve them from the manifest or confirmed path map; if a key is absent, confirm it before writing.

These five assets must synthesize the module; they are not concatenated copies of per-lesson lectures.

### Core Methodology

Answer the module's shared overarching problem and provide a cross-lesson causal chain, unified SOP, and capability standard.

### Case Index

Classify cases by the problem they solve and identify the source lesson, use, and pending-verification state.

### Execution Checklist

Convert cross-lesson methods into a fillable, verifiable production tool.

### Facts and Risks List

Separate stable principles, instructor experience, time-sensitive rules, and high-risk claims, while consolidating transcript gaps and historical acceptance limitations.

### Module Assignment

Design one real deliverable spanning the full module rather than adding per-lesson assignments together. It includes a first version, blind test/publication, review, and a second version with controlled variables.

## 6. Preview Synchronization Uses Two Finalization Phases

### Phase 1: Content Synchronization

Synchronize:

- the lesson's faithful transcript;
- the lesson's lecture;
- the current course map;
- the five module assets.

Preserve the paired drafts' relative directories to avoid same-name overwrites.

### Phase 2: Final-State Map Synchronization

After the content and module files pass acceptance, the map usually still needs to move from “in progress” to “passed” and switch the current module to the next module.

Therefore:

1. complete the final state update;
2. synchronize the map again;
3. compare text separately between the per-lesson preview map and module preview map;
4. run the old-state residual scan again.

Do not mistake the interim map from Phase 1 for the final map.

## 7. Non-SHA Acceptance Template

If the user explicitly excludes SHA, use:

- file existence;
- heading/frontmatter readback;
- unique-anchor and placeholder scans;
- faithful-transcript first-person red-line scan;
- per-file text comparison between source and preview;
- course-map stale-state scan;
- completeness and source-lesson coverage of the five module assets.

Record:

```text
lesson_faithful_equal=true
lesson_lecture_equal=true
lesson_map_equal=true
module_five_files_equal=true
module_map_equal=true
stale_state_count=0
sha=not_run
```

## 8. Common Errors

### Error 1: Creating the Paired Drafts Without Clearing the Non-Contiguous State

Consequence: the map and later lectures still claim that the lesson is missing.

### Error 2: Changing the Module Ratio to N/N Without Cross-Topic Synthesis

Consequence: the workflow violates the knowledge-base cadence requiring consolidation at module closeout.

### Error 3: Marking Acceptance as Passed Too Early

Consequence: the map declares completion before the preview actually exists.

### Error 4: Synchronizing the Map Only Once

Consequence: the preview retains interim states such as `acceptance-in-progress` and `current-module=old-module`.

### Error 5: Treating an Incomplete Local Quotation as a Truncated Lesson

Consequence: a complete lesson is blocked unnecessarily.

### Error 6: Completing a Quotation from Common Knowledge

Consequence: the faithful transcript contains original wording that the user never supplied.

### Error 7: Writing the Five Module Assets as Per-Lesson Copies

Consequence: no cross-lesson workflow, risk structure, or executable asset is formed.

## 9. Completion Criteria

Declare module closeout only when all conditions hold:

- paired drafts for the final missing lesson are complete;
- the lesson's knowledge navigation is complete;
- module ratio and total lesson count are correct;
- missing-lesson notes have been removed from later lessons;
- the five assets have been created or updated;
- the map points to the next module and next lesson;
- previews agree for the lesson, five module assets, and final-state map;
- stale-state count is zero;
- truncation, STT, factual, copyright, and platform-rule risks are recorded explicitly.
