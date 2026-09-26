# Semantic Review and Independent-QA Contract

Semantic review does not judge whether the writing is merely “good.” It establishes whether the faithful edit and structured lecture satisfy the same quality contract and may enter the official knowledge base.

## Two review forms

- `writer_self_check`: for an ordinary clean lesson, the lesson's writing model compares its work with the source and submits `semantic_check.json` in the same task. This is not independent QA.
- `independent_qa`: when a risk trigger or stable sample selects a lesson, a separate task context reads the source transcript, faithful edit, structured lecture, core quality contract, and current-mode evidence.
- `strict` requires independent QA for every lesson. `fast` and `standard` use stable sampling plus content-risk triggers.
- The independent-QA model may be another low-cost model. Escalate real ambiguity to a strong model.
- Under either review form, script PASS, file existence, and writer self-report cannot independently prove semantic acceptance.

## Review intensity

- `fast`: writer semantic self-check for ordinary lessons; full independent QA for about 20% stable sampling, the sample lesson, and every risk-triggered lesson.
- `standard`: full independent QA for critical and risk-triggered lessons; about 50% stable sampling for ordinary lessons.
- `strict`: full independent QA for every lesson.

Assurance mode changes evidence form and independent-QA coverage only. It never changes the quality floor for the faithful edit or structured lecture. A second-round recheck must receive `review_round` and the previous issue list. It verifies only those issues and their surrounding relationships; it must not restart full-text criticism unless it discovers a new high-severity distortion.

## Review order

### 1. Source and identity

Confirm that lesson number, title, lecturer, source video, and all three files belong to the same lesson. An identity conflict goes directly to `BLOCKED`.

### 2. Full-content coverage

Follow source order and verify:

- the opening, middle, and ending can all be located in the faithful edit;
- people, numbers, brands, tools, cases, steps, constraints, and counterexamples have corresponding locations;
- the longest case and most complex argument remain complete;
- when the current mode supplies block-level coverage, inspect the reasons for `noise` and `merged`; otherwise use that mode's anchor checklist; and
- apparently repetitive passages do not contain new information that was lost.

Every failure must cite a source excerpt or block ID and the corresponding draft location. Never report only that “the information is incomplete.”

### 3. Fidelity

Check whether the output:

- changes causality, subject, degree, or scope of application;
- promotes an experiential judgment into a universal fact;
- changes the lecturer's first person into third-party summary;
- adds explanation, data, or conclusions absent from the source; or
- resolves uncertain proper nouns or numbers by guessing.

### 4. Editing quality

Reject either extreme:

- **Over-compressed:** only summary and conclusions remain.
- **Barely edited:** headings were added to a transcript that remains a wall of text.

Also check whether headings, bold text, lists, or em dashes damage readability. Do not enforce arbitrary counts.

### 5. Structured-lecture responsibilities

The structured lecture may reorganize content, but it must:

- preserve source methods, arguments, cases, and boundaries;
- link back to the source transcript and faithful edit;
- distinguish lecturer statements, editorial organization, and unverified facts; and
- never present a new inference as the lecturer's judgment.

## Severity and decisions

- `high`: meets a failure criterion in the core quality contract and changes knowledge, source identity, a key fact, original meaning, or basic readability.
- `note`: wording, formatting, minor repetition, ledger maintenance, or optional improvement that does not change trustworthiness or use.

Decisions:

- `pass`: no unresolved `high`; notes are allowed.
- `fix_required`: at least one precisely located `high` can be fixed in one targeted pass.
- `escalated`: source ambiguity, factual conflict, or a `high` remains after one rework.
- `blocked`: the source, identity, or source-text integrity is defective and generated prose cannot repair it.

A `note` alone must never trigger rework, recheck, or a strong model. Minor formatting cannot hide semantic success, and polished formatting cannot excuse semantic risk.

## Rework boundary

QA identifies evidence, impact, and the required fix; it does not rewrite the entire artifact. An ordinary lesson receives at most one routine rework. The recheck examines only whether previous `high` issues are closed and whether their surrounding relationships remain intact. With no remaining `high`, pass. If a `high` remains, enter `ESCALATED` and allow only one strong-model adjudication, targeted repair, and final verification. Then deliver or stop; never enter another polishing loop.

## QA report

Use `templates/qa-report.example.json`. At minimum, the report includes:

- decision;
- source-identity check;
- coverage conclusion;
- itemized issues and evidence;
- risk level;
- recommended state; and
- whether a strong model is required.
