# Orchestration and Model Routing

The objective is reliable course production at the lowest stable total cost. Never assign permanent roles by model brand.

## Roles

- **Orchestrator:** maintains the manifest, dispatches work packages, and reads state; never edits course prose.
- **Capture worker:** saves the immutable source transcript; never generates derivatives.
- **Lesson writer:** produces the faithful edit, structured lecture, uncertainty ledger, and semantic self-check in one task; never writes to the official library.
- **Mechanical validator:** checks only deterministic structure, paths, formatting, and counts; never judges semantic fidelity.
- **Independent QA:** is created only when a risk trigger or stable sample selects the lesson; compares outputs with the source and does not rewrite them.
- **Rework worker:** normally the original lesson writer; changes only issues identified by QA.
- **Strong model:** establishes samples, resolves ambiguity, repairs systemic deviation, and improves the Skill.
- **Committer:** the only role allowed to promote official files and update the course map idempotently.

One agent system may schedule several roles. Create only one writing task per lesson by default. Independent QA must use a context isolated from the writing task, but no empty QA task is created when the selector does not match.

## Model qualification

Kimi, GLM, DeepSeek, and every other model must pass the same representative test before receiving a role. Record the exact model version; never infer capability from the provider brand.

Test conditions must be identical:

- the same source transcript;
- the same core contract;
- the same approved sample;
- the same work package;
- the same QA rules; and
- the same tools and context delivery.

Record first-pass success, semantic omissions, unsupported additions, rework count, human review time, call cost, and final accepted cost. A model with low call cost and high rework cost is not inexpensive.

## Default routing

1. Prefer scripts or the browser for deterministic capture and file checks.
2. For a batch larger than three lessons, produce one real sample and wait for user approval before scaling.
3. A qualified lesson writer generates the faithful edit, structured lecture, and semantic self-check once in the approved style.
4. Independent-QA evidence strength and sampling follow the assurance mode; the core quality contract is identical in every mode.
5. Only a `high` issue triggers one targeted rework. The recheck examines only previous issues.
6. If a `high` remains after one rework, QA conflicts, or the source is ambiguous, a strong model adjudicates once.
7. Use strong models for exceptions, samples, and method improvements, not repeated polishing.

## Model or workflow changes

Any of the following creates a new production condition:

- exact model or version changes;
- Harness or agent runner changes;
- the core quality contract changes;
- the work package changes;
- the approved sample changes; or
- the QA contract changes.

Rerun a representative sample after a change. Never switch production conditions inside a batch without validation.

## Context and concurrency

- The user submits one task; the system handles context isolation internally.
- Each lesson worker reads only the current lesson and required rules, not the complete course text.
- The orchestrator does not retain full text in chat; state files and actual artifacts are authoritative.
- Independent temporary drafts may run with limited concurrency.
- Writing, QA, and rework for the same lesson remain dependency-ordered and serial.
- Official promotion and course-map updates remain serial under one writer.

## Scaling and stopping

For a new course, model, or work package: real sample -> user approval -> small batch -> scale after stability. Before sample approval, do not scale paired outputs.

Stop one lesson for an incomplete source, identity conflict, a `high` remaining after one rework, factual ambiguity, or exhausted budget.

Stop the whole batch for repeated omissions across lessons, systematic formatting regression, a sudden concentration of high-risk QA issues, a mid-batch model or Skill change, systematic inconsistency between state and files, or cumulative cost beyond the manifest budget.

After stopping, fix the earliest control point that failed. Do not continue lesson-by-lesson repairs or add synonymous prohibitions to multiple files.

## Cost boundaries

- Per lesson, allow at most one routine rework and two routine QA decisions: the initial review plus a targeted recheck. If severe distortion remains, allow only one strong-model adjudication, targeted repair, and final verification.
- Wording, formatting, and ledger notes do not start a new agent.
- Check channel connectivity once at initial deployment, after a model change, or after a real failure.
- A worker must read the core quality contract, current assurance-mode production card, current lesson, approved sample, and necessary sources. Load additional complete rules only during a dispute; never omit the core contract.
- Stop and report when token or wall-clock usage reaches the manifest budget. Never exceed a budget silently.

Strong-model effort must create reusable leverage: an approved sample, failure diagnosis, source adjudication, or Skill improvement.
