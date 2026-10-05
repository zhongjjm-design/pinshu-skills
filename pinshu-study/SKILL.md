---
name: pinshu-study
description: "Use when guiding study, reviewing or quizzing course material, or preserving real learning records."
---

# Pinshu Study Coach

## Origin and maintenance

- Original work: Pinshu original (`original`)
- Owner and maintainer: Aidan (Pinshu)
- Upstream dependencies: `pinshu-distill`, `pinshu-course`
- Distribution status: `bundled`

Turn prepared course material into review and practice, then save learning evidence only after actual study. Prepare reusable active-recall cards and training questions when a course's learning purpose is enabled; guide study, recall, follow-up, error analysis, source review, and retesting when the learner actually participates. Material generated is not mastery achieved. This Skill is not part of every course's default production chain. Markdown holds content and records; the agent runs the practice; web interfaces are regenerable displays.

## Triggers and first decision

Use when the user asks to learn a lesson, be guided, review, be quizzed, revisit an error, explain it to someone else, or test real understanding. Systematic learning, professional foundations, bootcamps, certifications, and exam preparation enable review/training content at course initialization; source collections, interviews, opinion courses, and content-asset courses only enable it on a request to master or assess. Determine the lesson from current course identity and map, never an old pilot. A raw transcript alone does not trigger training before the course purpose has been decided.

| Stage | Evidence | Default |
|---|---|---|
| Not studied | Has not read notes or is mentally blank | Guide; do not quiz |
| Just studied | Explicitly finished reading | Basic recall and understanding |
| Reviewed | Has records or asks for integrated practice | Compare, derive, use counterexamples and mixed questions |
| Has errors | Requests retest or names weak points | Target omissions and require a fresh answer |

If uncertain, ask one question: “Have you studied this section already, or shall I guide you first?” If the learner has not studied, cannot answer, or goes blank, stop testing immediately.

## Paths and learning entry

Reuse the existing confirmed course map, directories, and numbering; never translate them into a second tree. For a genuinely new course these *example* names can be adapted to its convention:

```text
03_Review_and_Practice/
├── 01_Active_Recall/
└── 02_Practice_Bank/
04_Learning_Records/
├── 00_Progress.md
├── 01_Practice_Sessions/
└── 02_Errors_and_Rechecks.md
```

Review/training files appear only when the course's learning purpose is enabled. Create progress/session records only after real study; create error/retest files only after an actual wrong answer. Do not pre-create empty directories. The course map explains in the learner's language “read notes → recall → practice → see records → retest” and shows current status and next step. Directory and template labels must be generic for any learner, not named for Aidan or an agent. Learner-facing prose follows the user's request or established course language; stable machine keys stay English.

## Input priority

Structured lesson notes, then faithfully edited transcript, domain standards, course map and approved cross-topic material, cards and training bank, then personal records/error log. Recheck significant claims against raw source evidence if the faithful transcript remains uncertain. If only raw STT exists or notes are incomplete, return to the appropriate upstream Skill; do not clean and train simultaneously.

## Path 1: guided study

Start with a one-screen throughline; take one module at a time. Explain the problem and structure before details and cases. Once understanding appears, use one low-pressure check. If still blank, explain again. Save the stopping point, not fabricated mastery. Read `references/guided-study-and-training-rules.md`.

## Path 2: active recall

Cards are learner-facing study materials, not engineering-field checklists. An atomic card assesses one independently scorable objective; an integrative card may require a whole model or case chain, but is identified and counted separately. Questions, answers, explanations, and visible sources use the learner's language. Mnemonics, memory aids, and safety are attributes, not an invented difficulty scale. Generate cards for a specified lesson only when enabled; `pinshu-course` can deduplicate across lessons and make module-wide integrative cards. During review show one question at a time and reveal its answer only after the learner responds. Read `references/active-recall-card-rules.md`.

## Path 3: follow-up practice

Only once the learner has studied:

```text
one question → complete original answer → identify coverage and omissions
→ follow up only on omissions → reference answer → diagnose error cause
→ return to notes or faithful transcript → fresh answer → save record
```

Do not paste the full bank or reveal answers early. “Mostly correct” is not actionable feedback.

## Path 4: explain to another person

When the learner wants to make knowledge their own or test understanding, do not write a polished script on their behalf. Ask for their initial explanation without heavy reliance on notes; act as the agreed audience and capture clarity, confusion, and real questions. Diagnose the central question, model, causal chain, examples, evidence, boundaries, and transfer; revisit the source, then explain again to another audience or in another setting. Real listener feedback can be saved. Fluency alone does not prove application; “can respond” or “can transfer” requires handling questions, counterexamples, and new situations. Read `references/feynman-explanation-and-sharing-practice.md`.

## Question sources and diagnosis

Prefer the user's genuine exam questions, printed tests, and textbook exercises, then instructor questions and representative learner errors, then approved course bank items. Generate and label a small number of AI gap-fill questions only for missing coverage, recurring errors, or transfer practice. Distinguish memory lapse, conceptual confusion, skipped reasoning, missed condition, incomplete expression, misread prompt, confused source identity, and safety/boundary errors. Feedback states what was correct, what was missing, where the reasoning diverged, what source to review, and when to answer again.

## Storage and readable presentation

Markdown is authoritative. Store standard cards and training questions in the enabled review/training area. Preserve original answers, follow-ups, error causes, source review, fresh answers, and retests in records after genuine learning. Put each card's or question's English ID, sequence, classification, operation, and other program data in separate JSON indices under the course's existing production-control area (e.g. `99_Production_Control/Learning_Asset_Index/`), with separate `active_recall_cards`/`card_id` and `training_questions`/`q_id` types. Frontmatter contains only a few file-level properties, count, resolvable source paths, and `metadata_index` pointer—not per-item lists. No `%%`, HTML comments/tags, item IDs, or pipeline fields in the reading body. HTML/web display is regenerable and must not overwrite original answers. Read `references/markdown-learning-record-specification.md`.

Open representative files in the actual target reading interface to check properties, heading hierarchy, collapsed answers, mobile width, and code leakage; a structural PASS does not prove rendering.

## Sources and safety

An instructor's speech is not automatically a textbook, pharmacopeia, regulation, or objective fact. A mnemonic cannot replace differential assessment; a case is not causal evidence of efficacy. For medical care, drugs, dosage, toxicity, emergencies, or hands-on procedures, practice only source identification, applicable conditions, stopping conditions, and professional boundaries; never convert content into self-diagnosis, medication, or unsupervised procedure advice. Label simulated divination examples. Do not turn unresolved transcript items into definitive answers. Place each high-risk qualification in that card's answer, not just at the end of a file.

## Acceptance and stopping

Check that guided study actually helps a blank learner understand, cards and training questions are complementary, atomic/integrative cards are separately counted, reading bodies are clean, frontmatter is compact, and each dedicated index matches the body in type/count/order/unique IDs. Inspect representative rendered files. For actual practice, check original answer → follow-up → cause → source → fresh answer, and for explanation practice preserve both explanations and real questions. Never replace an original answer or quiz a learner who has not studied. Historical pilots are evidence, not prerequisites. An unenabled extension produces no empty card or record directories; the core course results can pass without it. Stop when the agreed learning objective is reached.
