---
name: pinshu-study
description: "Use when guiding study, reviewing or quizzing course material, and preserving learning records."
---

# Pinshu Study Coach

## Origin and maintenance

- Original work: Pinshu original (`original`)
- Owner: Aidan (Pinshu)
- Maintainer: Aidan (Pinshu)
- Upstream dependencies: `pinshu-distill`, `pinshu-course`
- Distribution status: `bundled`

Turn prepared course material into actual learning: guide the learner first, then use active recall, follow-up questions, error diagnosis, and retesting. Markdown preserves knowledge and learning records, the agent runs the training, and web pages serve only as a later presentation layer.

Learner-facing output follows `output_language` from the course manifest or the user's explicit preference. An omitted field means `match-user`, with source language as the fallback. Stable IDs, frontmatter keys, enum values, and other program fields remain English. If course-capture state or a manifest exists, resolve all storage targets from its path-template keys; otherwise use the existing confirmed project path map. Never translate directory names into a parallel tree.

## Triggers

Use this skill when the user says things such as "start studying a lesson," "guide me through this section," "I finished reading; quiz me," "let's practice for ten minutes," "review what I got wrong last time," "I want to explain this to someone else," "act as my audience and ask follow-up questions," "help me test whether I truly understand this," or "quiz me at random on the latest lessons." Determine the specific lesson from the current course map and the course identity the user has explicitly specified. Never substitute a historical pilot lesson for the current lesson. Merely mentioning a course, sending a transcript, or discussing course production does not automatically start training.

## First decision: learning stage

| State | Evidence | Default action |
|---|---|---|
| Not yet studied | Has not read the lesson notes, has no mental model, or is encountering the material for the first time | Guide the learner; do not test |
| Just studied | Explicitly says they have finished reading or just studied it | Check basic recall and understanding |
| Previously reviewed | Has an existing record or requests integrated practice | Use comparison, derivation, counterexamples, and mixed practice |
| Has known errors | Names missed questions, weak areas, or a retest | Ask targeted follow-ups and require a fresh answer in place |

When the state is uncertain, ask only: "Have you already studied this section, or should I guide you through it first?" If the user says they have not studied it, cannot answer, or their mind is blank, stop testing immediately.

## Input priority

1. Structured lesson notes;
2. Faithfully edited transcript;
3. Domain standards;
4. Course map and approved cross-lesson topic files;
5. Active-recall cards and the training question bank;
6. Personal learning records and error log.

If the available input is still raw speech-to-text (STT) or the lesson notes are unfinished, do not clean the material and train from it at the same time. Return the material to the appropriate upstream capability first.

## Path 1: guided study

For material not yet studied, begin with a one-screen overview of the main throughline. Cover one knowledge module at a time. Explain the problem and structure before details and examples. After the user understands, optionally check with one low-pressure question. If the user is still blank, explain it again. Save the stopping point, but never mark "heard" as "mastered." Read `references/guided-study-and-training-rules.md`.

## Path 2: active-recall cards

Cards are learner-facing study materials in the resolved output language, not a checklist of engineering fields. Distinguish atomic recall cards from integrative retelling cards. An atomic card tests one independently scorable target. An integrative card may ask for a complete model or case-reasoning chain, but it must be labeled and counted separately and must not claim to test one target per card. Write questions, answers, explanations, and visible sources in the resolved output language. Treat mnemonics, memory aids, and safety as attributes. Do not create an artificial difficulty system. Build candidate cards for each lesson first; at the end of a module, `pinshu-course` performs cross-lesson deduplication. During an actual review, display only one card at a time. Read `references/active-recall-card-rules.md`.

## Path 3: follow-up-question training

After the user explicitly confirms that they have studied the material:

```text
Ask one question
-> Wait for the complete answer
-> Identify what the answer covered and omitted
-> Ask only about an omission
-> Provide the reference answer
-> Diagnose the cause of the error
-> Return to the lesson notes or faithful transcript
-> Ask for a fresh answer
-> Save the record
```

Do not paste the full question bank, reveal answers in advance, or replace specific feedback with "good" or "mostly correct."

## Path 4: Feynman explanation and external-sharing practice

When the user explicitly wants to "make it my own," "explain it to someone else," or "test whether I truly understand it," do not begin by writing a polished script for them. First, ask the user to give an initial explanation while consulting the material as little as possible. The agent acts only as the agreed audience, recording what was clear, what remained confusing, and what follow-up questions arose rather than rushing to explain on the user's behalf. Then locate gaps across seven dimensions: central question, core model, causal chain, examples, evidence, boundaries, and transfer. Return to the lesson notes or faithful transcript to repair those gaps, then have the user explain the material again for a different audience or setting.

Follow-up questions and feedback from a real audience may be imported into the training record. Speaking fluently does not prove the learner can apply the material. Mark the learner as "can respond" or "can transfer" only after they can handle follow-up questions, counterexamples, and novel situations. Read `references/feynman-explanation-and-sharing-practice.md`.

## Question sources

Prefer the user's existing authentic exam questions, printed practice tests, and textbook exercises. Next prefer the instructor's in-class questions and representative learner errors, followed by approved course training questions. Generate a small number of AI gap-filling questions only when needed to cover a gap, address a recurring error, or train transfer, and label them as AI-generated gap-fill questions.

## Error causes

At minimum, distinguish memory failure, concept confusion, skipped reasoning step, omitted condition, incomplete expression, misread question, source-identity confusion, and safety or boundary error. Feedback must state what was correct, what was missing, where the reasoning diverged, what to review, and when to answer again.

## Persistence

Use Markdown as the authoritative source. Store standard course cards and training questions at the manifest-rendered course targets. Store the learner's original answers, follow-up questions, error diagnoses, and retest results in the neutral personal-learning-record target. Put stable English IDs and program fields in frontmatter or hidden comments, not in the main reading text. HTML and web pages are regenerable interfaces. Read `references/markdown-learning-record-specification.md`.

## Sources and safety

An instructor's spoken statement does not automatically equal a textbook, pharmacopeia, regulation, or objective fact. A mnemonic cannot replace differential assessment. A case cannot be promoted into a causal efficacy claim. For medical care, medication, toxicity, dosage, critical illness, or hands-on procedures, train only source identification, applicability conditions, stopping conditions, and professional boundaries; never turn the course content into advice for self-diagnosis, self-medication, or self-performed procedures. Label divination-practice cases as simulations. Do not use unresolved items in a faithful transcript as definitive answers. Put each high-risk boundary inside the individual card answer rather than relying only on a file-level disclaimer.

## Acceptance and stopping criteria

Verify that guided study moved the user from blankness to understanding; each atomic card tests one target; integrative cards are labeled and counted separately; actual card units agree with frontmatter totals and category counts; training truly completed the answer -> follow-up -> error diagnosis -> source review -> fresh answer cycle; Feynman practice preserved the first explanation, genuine follow-up questions, gaps, source review, and second explanation; the record preserved the original answer; and testing stopped when the user had not yet studied the material. Historical pilots may serve only as evidence that the rules were validated; they must never become prerequisites for producing or studying a new course. Stop when the learning objective has been met.
