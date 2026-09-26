# Professional Course Learning-Asset Pipeline

## Objective

Use this pipeline for traditional Chinese medicine, divination systems, academic study, or other course series whose primary goals are learning, review, training, and connecting knowledge across lessons. The user does not need to remember Skill names; the controller routes from natural-language intent.

## Composition

```text
pinshu-transcript: raw transcript → faithfully edited transcript
pinshu-distill: faithfully edited transcript → structured lecture; module materials → formal cross-lesson topic
pinshu-study: lecture → active-recall cards; guided study, training, error analysis, and personal records
pinshu-course: course identity, progress, checkpoints, knowledge clues pending consolidation, and formal promotion
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
4. Candidate active-recall cards use the resolved output language and one primary objective per card;
5. The course map is updated;
6. Register only knowledge clues with explicit cross-lesson value.

Do not generate a complete mock exam or formal cross-lesson topic for every lesson by default.

## Per Module

- Merge per-lesson candidate cards into a formal deck;
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

Do not start training merely because the user submits a course, discusses organization, or opens a lecture. Invoke `pinshu-study` when the user asks to start learning, be guided through the material, be quizzed, review, or practice missed questions.

States:

- Not studied → guided study;
- Just studied → basic recall;
- Reviewed → derivation, comparison, and mixed practice;
- Has errors → targeted retesting.

## Markdown and Web Interfaces

Markdown is the source of truth for lectures, cards, question banks, answers, and state. Web interfaces are downstream readers of those assets. A web database must not silently overwrite the Markdown source.

## Concurrency and Formal Promotion

The formal course library has one writer. Subagents write only to exclusive temporary directories. The main agent promotes serially after programmatic counts, source-path validation, content QA, and frontstage reading checks. Generator self-assessment is rework evidence only; keep candidate, generated, self-checked, independently reviewed, reworked, reverified, and accepted states separate. At module close, `pinshu-course` owns cross-lesson card aggregation and deduplication; `pinshu-study` owns only card production and learning use.

## Scale-Up Gate

Before batch production of an entire course, validate at least:

1. One representative mixed-content lesson;
2. One clinical case or divination-chart lesson;
3. One highly visual or hands-on lesson;
4. Independent QA of the faithful transcript, lecture, active-recall cards, and course map.

A real “guided study → recall → follow-up questions → source review → record” cycle validates the learning runtime experience. It is not prerequisite approval for generating per-lesson active-recall cards, updating the course map, or starting course batch processing. Without real answers, state must remain `not started`; never fabricate learning progress. Complete formal cross-lesson consolidation and mixed practice at module close. Historical pilot lessons are validation evidence only, not gates on current production.
