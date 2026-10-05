# Default Production Workflow

This reference is normative after the user confirms the course-production agreement. It preserves the complete default sequence while keeping `SKILL.md` focused on routing and non-negotiable gates.

## 1. Initialize or resume

```bash
python3 scripts/course_pipeline.py init \
  --manifest <course-manifest.json> \
  --state <runtime/course-state.json>
```

If the state file already exists, do not overwrite it. Resume with `next` or `summary`. The main conversation keeps only a short task list; full source text, artifacts, and state are always read from files.

The manifest may set `output_language` to `match-user`, `match-source`, or a short BCP-47 tag. If an older manifest omits it, initialization records `match-user`; the writing worker must determine the user's language from the conversation and use the source language if it cannot. The CLI reports the stored policy, not a detected language. Learner-facing prose follows that policy, while IDs, frontmatter keys, enum values, and other program fields remain English.

## 2. Capture each source transcript

Select a capture adapter from the video's platform. Only Baidu Netdisk is enabled for production today. Other platforms must not enter the default course pipeline until their adapters pass end-to-end validation.

| Source | Status | Entry point |
|---|---|---|
| Baidu Netdisk | Production-supported and verified | Web player **Transcript** tab |
| Quark Cloud Drive | Integration paused; end-to-end test not passed | Excluded from the default workflow |
| Alibaba Cloud Drive and other platforms | Not integrated | Excluded from the default workflow |
| Local video or audio | Fallback | Local subtitles or local transcription |

Production capture may use only the Baidu adapter. Even if another adapter can locate a file, it must pass a separate test before joining the workflow. Adapter documentation alone is not evidence that an adapter is production-ready.

The Baidu adapter follows this order: obtain the web player's native transcript, subtitles, or transcription first; consider local transcription only after the user explicitly authorizes a permitted download. AI summaries, mind maps, and course slides are supporting materials only and cannot replace the source transcript. Never bypass login, CAPTCHA, payment, or download permissions.

A capture adapter must return the source text, source platform, video identity, complete path or filename, extraction method, first sentence, last sentence, and integrity evidence.

After capture succeeds, save the transcript to the manifest-rendered source path, then transition the lesson from `DISCOVERED` to `CAPTURED`. If no transcript is available, authentication has expired, the text appears truncated, or the user lacks download permission and local transcription is impossible, mark the lesson `BLOCKED`, record the reason, and continue only with work that does not depend on that lesson.

## 3. Verify source integrity

Check all of the following:

- The source lesson number, title, and video identity agree.
- The platform or transcription-tool output matches the saved text, allowing newline differences only.
- The opening, middle, and ending are present, and the final sentence is complete.
- No playlist, button, recommendation, or other interface text is included.
- No obvious omission, mixed lesson, or duplicate loading is present.

Frontmatter must identify whether the source came from a platform-native transcript or local ASR. Never label a platform AI summary as a source transcript.

Transition to `SOURCE_VERIFIED` only after these checks pass. File existence and character count do not prove completeness.

## 4. Build the lesson work package

The orchestrator completes `templates/lesson-work-order.md` with the production profile, budget, current QA round, and writable scope.

- Every worker must read the current source transcript, the core quality contract routed by the main Skill, the user-approved sample, the current assurance-mode production card, and the lesson work package. A worker selected for independent QA must also read the semantic-QA contract routed by the main Skill.
- Always provide the complete core contract, not only its hash. Ordinary batch lessons must not repeatedly load the whole Skill, every reference, or irrelevant examples. An automatically generated Worker Spec must record the contract and adapter version or hash; the orchestrator must not improvise a summary of the contract.
- Resolve only the matched domain rules and content anchors routed by the main Skill. Do not duplicate the complete workflow for every domain.
- Load other complete rules only for the representative sample, the `strict` profile, source ambiguity, or a real dispute.
- Give each lesson a clean task context without requiring the user to create conversations manually.

Use the production-mode and budget contract routed by the main Skill for the exact input matrix.

## 5. Generate the final target style once

The writing worker writes only to the lesson's temporary directory. In one pass, it creates `faithful.md` and `lecture.md` in the user-approved style. Never generate an entire batch in a temporary reading style and then rewrite the whole batch into another style.

- Every profile emits `uncertainties.json`. Record only differences that affect proper nouns, numbers, facts, or source interpretation; do not turn ordinary editing into a word-by-word ledger.
- `fast` and `standard` use compact anchor coverage for people, numbers, key cases, methods, and constraints.
- Only `strict` requires block-by-block `coverage.json` and a complete difference ledger.
- Post-generation checks must follow the selected profile. Do not silently impose `strict` requirements on `fast`.

Completion here means only `DRAFTED`, not accepted. Character ratios are anomaly signals, never substitutes for semantic judgment.

## 6. Run mechanical checks

```bash
python3 scripts/validate_lesson.py \
  --profile <fast|standard|strict> \
  --source <source-transcript> --faithful <faithful-edit> --lecture <structured-lecture> \
  --uncertainties <uncertainties.json> [--coverage <coverage.json>] \
  --json-out <mechanical-report.json>
```

`strict` requires a coverage file; `fast` and `standard` do not. The script checks deterministic risks only and must never claim semantic fidelity.

## 7. Select semantic review and independent QA

Every course requires model-based semantic review. For an ordinary clean lesson, the writing model submits `semantic_check.json` in the same task. Escalate to independent QA in a separate context when any condition applies:

- Stable sampling for the selected assurance mode chooses the lesson.
- `uncertainties.json` contains unresolved items.
- The content concerns medical, legal, financial, safety, or real-world operational consequences.
- Speaker relationships, visual evidence, code or commands, or key numbers conflict.
- Mechanical checks raise a semantic-risk warning.
- The model, core contract, approved sample, or adapter changes.
- A recent lesson had the same `high` issue.
- The target is formal external use.

`fast` uses lightweight evidence and about 20% stable sampling. `standard` uses standard evidence with 100% independent QA for critical lessons and about 50% for ordinary lessons. `strict` uses full evidence and independent QA for every lesson. Do not create a QA worker when no selector matches.

Only a high-severity issue that meets the core quality contract's failure criteria may enter `FIX_REQUIRED`. Wording, formatting, and optional improvements are `note` items and do not trigger rework. Source or identity failures enter `BLOCKED`; genuine interpretation conflicts or high-risk ambiguity enter `ESCALATED`. Scripts, character ratios, and file existence cannot prove semantic acceptance.

## 8. Cap routine rework at one pass and recheck only targeted issues

- An ordinary lesson receives at most one targeted rework pass, limited to high-severity issues identified in the first QA round.
- The second round checks only whether those issues were fixed. New non-high issues become `note` items.
- If no high issue remains, deliver with any notes.
- If a high issue remains, stop the loop. A strong model may adjudicate the source, facts, or original meaning once; do not start a third stylistic rework round.
- If the same error appears across several lessons, stop scaling and fix the production card, sample, or route instead of repairing each lesson independently.

Do not start a new agent for formatting, wording, or ledger maintenance. Use the budget and model-routing contracts routed by the main Skill for escalation rules.

## 9. Promote through one official writer

Only a lesson at `SEMANTIC_QA_PASS` may be promoted to official directories, and only by the designated committer. Before promotion, read back the actual files and save their paths in state. After promotion, transition to `PROMOTED`.

Then `pinshu-course` updates the course map and cross-lesson assets. If the course purpose enables learning extensions, `pinshu-study` creates active-recall cards and a practice bank in the manifest-rendered locations. Create learning records only after the user has actually answered or studied. Keep human-readable learning content separate from item-level machine metadata, and verify representative files in the target reading interface. Transition to `ACCEPTED` only after state, official files, and the course map agree. Draft, QA, and rework workers must never edit the official course map.

### 9.1 Manifest-driven names and paths

Define the naming template and path templates once in the manifest. Run `paths` before production and verify every target needed by downstream Skills. The command renders core and extension keys, including review and learning-record targets when configured. Do not hand-register a different format for each lesson. For an existing course, preserve its course map and established naming instead of forcing global filenames. If no manifest exists, confirm an explicit path map before writing.

### 9.2 Renames and rework must not leave duplicate official files

After the new file is promoted successfully, move the old name or version to the system trash rather than deleting it permanently. Before delivery, reconcile programmatically: no unregistered leftovers, every state-machine path exists, frontmatter links resolve, and official text matches the accepted workshop text.

## 10. Optional content sourcebook after accepted core assets

When the user confirmed `content_asset` as a course purpose, load `pinshu-content-assets` only after the lesson's faithful edit and structured guide are accepted. Have the agent read both in full, reconcile corrected terminology and raw quotations, then write one readable lesson sourcebook. For a full course, organize a separate course-level sourcebook linking back to the lessons. Obtain the destination from the current manifest's `content_master_lesson` and `content_master_course` path templates, an existing course's approved paths, or an explicit user-approved path map. Do not invent or translate a parallel archive. Mark new sourcebooks **pending user review**; their existence and the core lesson's `ACCEPTED` status do not make them approved writing inputs. Do not generate an article unless separately requested. This is an agent handoff, not a claim that `course_pipeline.py` generates or approves content sourcebooks automatically.
