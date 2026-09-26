---
name: pinshu-course-capture
description: "Capture original course transcripts and orchestrate tiered production. Baidu Netdisk is verified; other adapters enter production only after validation. Supports sample approval, budgets, QA, bounded rework, and resumable runs. Use for processing a lesson, producing a course in batches, capturing cloud-drive transcripts, or resuming a course pipeline."
---

# Course Transcript Capture and Tiered Production Orchestration

## Role and objective

- Original work by Aidan (Pinshu).
- Upstream dependencies: `pinshu-transcript`, `pinshu-distill`, and `pinshu-course`.
- This Skill is the **primary course-production entry point**. The user submits one task; the system captures the source transcript, produces a faithful edit and a structured lecture, and updates the course map. During intake, it determines the course purpose. Courses intended for systematic learning, certification, or exam preparation also receive review and practice materials. After real study occurs, `pinshu-study` stores the learning record. Independent QA, rework, promotion, reconciliation, and recovery run only when their conditions apply.
- A cloud drive is only a replaceable source-capture adapter. Downstream production does not depend on one platform, a specific operator, a particular browser, or a specific model.

## Responsibility boundaries

This Skill owns orchestration, state, handoffs, quality gates, model escalation, the single official writer, and resumable execution.

Downstream responsibilities: `pinshu-transcript` produces the faithful edit; `pinshu-distill` produces the structured lecture; `pinshu-course` owns course purpose, the map, and cross-lesson assets; `pinshu-study` owns review and practice materials plus records of actual study.

The source transcript is immutable. No generated artifact may write back into it.

## Before production: confirm the course-production agreement

The orchestrator recommends settings from the course name, structure, content risk, and user objective. The user only confirms or changes the recommendation. Do not expose internal enum values or technical judgments as the user-facing decision. Explain four items together:

1. **Course purpose (multi-select):** reference/archive, systematic learning/review, training/certification/exam preparation, method transfer/real project, or content asset/internal reuse.
2. **External use:** confirm publication, public release, paid course use, client delivery, academic use, or real-world decision support separately. Do not merge this with course purpose.
3. **Assurance approach:** recommend lightweight, standard, or full evidence and explain why in one sentence. These modes change only evidence density, independent-QA sampling, and budgets; they never change the quality floor or the four core results.
4. **Final assets:** always deliver the source transcript, faithful edit, structured lecture, and course map. Then list enabled review/practice materials, horizontal topics, or external-use review.

Write the confirmed choices to `course_purpose`, both decision-basis fields, `optional_extensions`, `external_use`, `output_language`, and `intake_confirmation` in the manifest. `output_language` accepts `match-user`, `match-source`, or a short BCP-47 tag. If an old manifest omits it, the runtime uses `match-user`, falling back to the source language when the user's language is unavailable. Public instructions remain English; learner-facing prose follows this resolved policy, while stable IDs, frontmatter keys, enum values, and other program fields remain English. Do not initialize production before this agreement is confirmed. Use the `agreement` command to show the agreement, including the resolved language policy, to the user, writer, and QA reviewer.

Startup also requires a course identity, lecturer, one canonical root directory, a lesson and source inventory, a primary writing model, an available QA route whenever a trigger applies, and a writable temporary runtime directory. Drafts must never enter the official knowledge base directly.

For batches larger than three lessons, complete one real sample lesson first and have the user inspect and approve its layout, level of detail, and reading experience. Before approval, only source capture may continue. A machine PASS, agent self-assessment, or independent QA cannot replace user approval.

Create the runtime manifest from `templates/course-manifest.example.json`, then read `references/production-modes-and-budgets.md`. Runtime state belongs to the course project and must not be written back into the Skill source. Every downstream Skill must obtain course paths from this manifest/state through the `paths` command. For a new course without either file, confirm an explicit path map before any write; never translate directory names into a parallel tree.

## Mandatory production workflow

After the agreement is confirmed, read and follow `references/default-production-workflow.md`. Its default sequence is:

1. initialize or resume from an atomic state file;
2. capture each immutable source transcript through a production-approved adapter;
3. verify source identity and opening/middle/ending integrity;
4. create a lesson work package with explicit inputs, budget, and writable scope;
5. generate the approved faithful edit and structured lecture once in a temporary lesson directory;
6. run deterministic mechanical checks;
7. perform a writer semantic self-check or selected independent QA;
8. allow at most one routine targeted rework, then one strong-model adjudication if a `high` remains; and
9. let one committer promote accepted artifacts and update the course map serially.

The detailed workflow specifies adapter status, exact inputs, QA selectors, evidence requirements, promotion checks, manifest-rendered paths, and command examples. It is normative, not optional background.

Always read these additional contracts at the point where they apply:

- every writing, rework, QA, and commit task: `references/core-quality-contract.md`;
- assurance selection and budgets: `references/production-modes-and-budgets.md`;
- independent QA or targeted recheck: `references/semantic-qa-contract.md`;
- source capture: `references/capture-adapter-contract.md` plus the selected platform adapter;
- lesson-specific professional boundaries: only matched entries from `references/domain-and-content-routing.md`;
- formal external use: `references/external-use-gate.md`.

## State and recovery

Main flow:

`DISCOVERED -> CAPTURED -> SOURCE_VERIFIED -> DRAFTED -> MECHANICAL_PASS -> SEMANTIC_QA_PASS -> PROMOTED -> ACCEPTED`

Exception states: `FIX_REQUIRED`, `ESCALATED`, `BLOCKED`, and `SKIPPED`.

Common commands:

```bash
python3 scripts/course_pipeline.py init --manifest <course-manifest.json> --state <runtime/course-state.json>
python3 scripts/course_pipeline.py agreement --state <course-state.json>
python3 scripts/course_pipeline.py paths --state <course-state.json> --lesson <N>
python3 scripts/course_pipeline.py next --state <course-state.json>
python3 scripts/course_pipeline.py transition --state <course-state.json> --lesson <N> --to <STATE> --reason <explanation> --wall-minutes-used <minutes> [--tokens-used <tokens>]
python3 scripts/course_pipeline.py audit --state <course-state.json>
python3 scripts/course_pipeline.py summary --state <course-state.json>
```

State writes must be atomic. After interruption, trust the state file and actual artifacts, not a chat summary. If the state file already exists, never overwrite it; resume with `next` or `summary`.

## Scaling rules

Test and production must use the same primary model, QA model, work package, rules, scripts, and promotion paths.

- Run a representative sample for every new course or model.
- After user approval, run a small batch.
- Scale only when the small batch shows no shared deviation.
- When several lessons show the same content error, pause new work and fix the earliest specification, work-package, or routing cause.

Parallelize only independent temporary lessons. Source capture may remain serial when browser stability requires it. Writing and QA may run with limited concurrency. Official promotion and course-map updates must remain serial.

## Definition of complete

“Fully complete” requires all of the following:

- Every lesson is `ACCEPTED`, is intentionally `SKIPPED` with a reason, or is explicitly reported as `BLOCKED`.
- The source transcript, faithful edit, and structured lecture exist and have been read back.
- The course map contains exactly one corresponding entry with matching state and resolvable links.
- The final directories contain no unregistered leftovers, naming is consistent, and frontmatter has zero broken references.
- The manifest records course purpose and the reasons for enabling or disabling learning extensions. When enabled, review and practice content, the separate backend index, and target-interface rendering agree. When disabled, those files and directories are not required. The configured learning-record directory is not required before real study occurs. An external-use record is not required when external use is disabled.
- Unresolved STT, factual, and source issues are listed separately.
- The report states actual models, agent calls, tokens, wall-clock time, rework, escalation, blockers, and untouched scope.

Never conflate “captured,” “generated,” “mechanical checks passed,” and “formally accepted.”

## Closeout cleanup (only after explicit user request)

After every lesson is `ACCEPTED`, retain official deliverables, original sources, pending items, the state file, and final SHA-256 baselines. Temporary drafts and mechanical reports may be registered with `archive-artifact` and moved to the system trash only when the user asks for cleanup.

The archive command may handle only reproducible temporary drafts and mechanical reports for accepted lessons, and it must verify the real SHA-256. Original sources, official paired outputs, coverage evidence, uncertainty ledgers, and semantic-QA reports must not be hidden from audits through `artifacts_archived`.

## Direct resources

- Default sequence: `references/default-production-workflow.md`.
- Capture: `references/capture-adapter-contract.md`, `references/baidu-capture-adapter.md`, `references/quark-capture-adapter.md`, and `references/aliyun-capture-adapter.md`.
- Quality, domain, and external use: `references/core-quality-contract.md`, `references/domain-and-content-routing.md`, and `references/external-use-gate.md`.
- QA, models, and budgets: `references/semantic-qa-contract.md`, `references/orchestration-and-model-routing.md`, and `references/production-modes-and-budgets.md`.
- Manifests and work packages: `templates/course-manifest.example.json`, `templates/lesson-work-order.md`, and `templates/qa-report.example.json`.
- State and mechanical checks: `scripts/course_pipeline.py` and `scripts/validate_lesson.py`.
