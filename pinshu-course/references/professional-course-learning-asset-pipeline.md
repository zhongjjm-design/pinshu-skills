# Professional Course Learning-Asset Pipeline

## Objective

Use this pipeline when the user's course purpose is systematic study, professional foundations, certification, exam preparation, or another enabled learning goal. A discipline name alone does not establish purpose. The user need not remember Skill names; the controller routes from natural-language intent. In every course, the four core results remain immutable raw transcript, faithful edit, structured notes, and one shared-map entry.

## Composition

```text
pinshu-course-capture: immutable raw transcript and per-lesson production
pinshu-transcript: raw transcript → faithfully edited transcript
pinshu-distill: faithfully edited transcript → structured notes; module → formal cross-topic work
pinshu-course: identity, map, state, checkpoints, clues, and promotion
pinshu-study: enabled recall cards and question bank; records after real learning
pinshu-content-assets: on request, a readable content sourcebook per accepted lesson and a cross-lesson sourcebook; pending review
```

## Frontstage and Backstage

### Learner Frontstage

- Structured lectures;
- Active-recall cards in the resolved output language, shown one at a time;
- Guided-study or training dialogue in the resolved output language;
- Formal cross-lesson topics after module completion;
- A concise learning path and summaries awaiting connection in the course map.

### Agent Backstage

- Original sources, anchors, and identity;
- Terminology, QA, and rework;
- Production state and rule version;
- Knowledge clues pending consolidation;
- Machine fields for cards, questions, and learning records.

The backstage must remain auditable without occupying the primary learning interface.

## Per Lesson

1. Original material is available;
2. The faithfully edited transcript passes source and semantic QA;
3. The structured lecture highlights priorities, has coherent organization, and supports independent learning;
4. Enabled active-recall cards and a complementary training bank use the learner's language; atomic cards test one independently scorable objective, integrative cards are separately marked;
5. The course map is updated;
6. Register only knowledge clues with explicit cross-lesson value.

Do not generate a complete mock exam or formal cross-lesson topic for every lesson by default.

## Per Module

- Deduplicate per-lesson cards and create module-level integrative cards when needed;
- Map to the user’s existing question bank first;
- Generate module-level guided study and mixed practice;
- Merge and deduplicate pending clues while preserving meaningful differences;
- Generate a formal cross-lesson topic readable by the learner.

## Knowledge Clues Pending Consolidation

This is a collection basket, not a formal learning document. Each clue must state at least: knowledge object, new contribution from the current lesson, cross-lesson rationale, later trigger, evidence state, and current-lesson source. Only `verified across lessons` requires a second source.

Use only these evidence states: `current-lesson candidate`, `later-lesson foreshadowing`, `verified across lessons`, and `safety-governance candidate`. Expected recurrence is not verified recurrence; without a second source, never label a clue `verified across lessons`.

Register a clue only when it has:

- Explicit foreshadowing for a later lesson;
- A demonstrated connection across multiple modules;
- High confusion or strong disagreement;
- Safety-governance value;
- A change across cohorts or instructors.

Do not register ordinary single-lesson details. Learner-visible course-map summaries follow the resolved output language; stable program fields remain English.

## Learning Triggers

Generating enabled cards and questions is not a training session. Begin actual practice when the user asks to learn, be guided, be quizzed, review, or practice missed questions. Only after real learning create personal records. When purpose is ambiguous, recommend and ask rather than quietly disabling learning.

States:

- Not studied → guided study;
- Just studied → basic recall;
- Reviewed → derivation, comparison, and mixed practice;
- Has errors → targeted retesting.

## Markdown and Web Interfaces

Markdown is the source of truth for lectures, cards, question banks, answers, and state. Web interfaces are downstream readers of those assets. A web database must not silently overwrite the Markdown source.

## Concurrency and Formal Promotion

The formal course library has one writer. Subagents write only to exclusive temporary directories. The sole committer promotes serially after structural checks and writer semantic review. Independent QA is risk-triggered or adaptively sampled; ordinary clean lessons do not require a second writer or independent review. Generator self-assessment and a script PASS do not prove semantic acceptance or target-interface rendering. At module close, `pinshu-course` owns cross-lesson card aggregation and deduplication; `pinshu-study` owns only card production and learning use.

## Scale-Up Gate

Before batch production, validate representative layout, faithful edit, structured notes, map entry, and enabled learning assets. Clinical or case reasoning, strongly visual or hands-on lessons, critical numbers, and consequential claims trigger independent QA; ordinary lessons use adaptive sampling.

A real “guided study → recall → follow-up questions → source review → record” cycle validates the learning runtime experience. It is not prerequisite approval for generating per-lesson active-recall cards, updating the course map, or starting course batch processing. Without real answers, state must remain `not started`; never fabricate learning progress. Complete formal cross-lesson consolidation and mixed practice at module close. Historical pilot lessons are validation evidence only, not gates on current production.
