# Course Foundation Quickstart

This guide starts a new course with the public Pinshu course pipeline. It does not install the repository and does not assume a private directory layout.

## 1. Copy and confirm the manifest

Copy `pinshu-course-capture/templates/course-manifest.example.json` outside the Skill source. Set:

- one stable `course_id`, title, lecturer, course root, and runtime directory;
- the real lesson inventory and source paths;
- `output_language` (`match-user`, `match-source`, or a short BCP-47 tag);
- writer, QA, and strong-model identifiers;
- purpose, assurance, extension, external-use, and budget decisions;
- explicit promotion hygiene: the frontmatter fields that carry source links, forbidden draft markers, and `require_source_backlink: true`.

Do not set `intake_confirmation.confirmed` until the owner has approved the production agreement.

## 2. Initialize once

```bash
python3 pinshu-course-capture/scripts/course_pipeline.py init \
  --manifest /absolute/path/course-manifest.json \
  --state /absolute/path/runtime/course-state.json
```

Initialization stores a stable path context. Later commands may run from any working directory. Existing state is never overwritten.

Inspect the contract and next lesson:

```bash
python3 pinshu-course-capture/scripts/course_pipeline.py agreement --state /absolute/path/runtime/course-state.json
python3 pinshu-course-capture/scripts/course_pipeline.py paths --state /absolute/path/runtime/course-state.json --lesson 1
python3 pinshu-course-capture/scripts/course_pipeline.py work-order --state /absolute/path/runtime/course-state.json --lesson 1
```

If no `case_library` is configured, `work-order` reports it as unresolved. It never guesses a location.

## 3. Capture, verify, and draft

Register artifacts with absolute paths. The normal state sequence is:

```text
DISCOVERED -> CAPTURED -> SOURCE_VERIFIED -> DRAFTED
```

The writer creates a faithful edit, structured lecture, uncertainty ledger, and—under strict assurance—a coverage map in the lesson runtime directory. The source remains immutable.

Before independent QA, a writer may use `self-rework` once (or the configured bounded limit) only when the faithful or lecture hash really changes:

```bash
python3 pinshu-course-capture/scripts/course_pipeline.py self-rework \
  --state /absolute/path/runtime/course-state.json --lesson 1 \
  --reason "Restored a missed source boundary" \
  --artifact faithful=/absolute/path/runtime/lesson-1/faithful-v2.md
```

This does not consume a QA round and does not create `FIX_REQUIRED`.

## 4. Run the real mechanical gate

```bash
python3 pinshu-course-capture/scripts/course_pipeline.py preflight \
  --state /absolute/path/runtime/course-state.json --lesson 1
```

`preflight` invokes `validate_lesson.py` against the registered source, faithful edit, lecture, uncertainty ledger, and coverage map. It writes and binds a versioned mechanical report. A pass means only that deterministic checks passed; semantic fidelity remains pending.

## 5. Bind semantic evidence and promote

Use a writer self-check only when the state-selected policy permits it. Otherwise provide an independent `qa_report` with exact identity, round, scope, coverage, reviewer model, and input SHA-256 values. A targeted second round must be `targeted_recheck` and remains registered as independent QA.

Only `SEMANTIC_QA_PASS` can enter `PROMOTED`. Promotion verifies that official files match the reviewed drafts, source backlinks resolve, configured draft markers are absent, and no runtime-draft references remain. `ACCEPTED` also binds the latest shared course-map baseline.

Run the audit before delivery:

```bash
python3 pinshu-course-capture/scripts/course_pipeline.py audit --state /absolute/path/runtime/course-state.json
```

Audit failures are classified as `registration_defect`, `independent_qa_missing`, `qa_binding_mismatch`, `formal_candidate_drift`, `report_missing`, `promotion_hygiene`, or `revision_open`.

## 6. Revise an accepted lesson safely

Open exactly one revision:

```bash
python3 pinshu-course-capture/scripts/course_pipeline.py revision-open \
  --state /absolute/path/runtime/course-state.json --lesson 1 \
  --type metadata_link_only --reason "Repair source metadata"
```

The command snapshots both official files, state, and shared-map context. The lesson remains `ACCEPTED`, but audit fails with `revision_open` until closure.

Close with a hash-bound revision report:

```bash
python3 pinshu-course-capture/scripts/course_pipeline.py revision-close \
  --state /absolute/path/runtime/course-state.json --lesson 1 \
  --revision-report /absolute/path/revision-report.json
```

- `metadata_link_only` closes deterministically only when visible body text is unchanged, links resolve, and promotion hygiene passes.
- `formatting` closes deterministically only when the conservative semantic fingerprint is unchanged. Changes to words, numbers, code, or links require independent QA.
- `content` always requires `--qa-report`. The QA report must bind the current source, official paired outputs, uncertainty ledger, and coverage map and contain no unresolved high issue.

A revision report cannot self-declare semantic equivalence.

## 7. Release validation

Run the focused, offline release gate:

```bash
python3 scripts/release_check.py
```

To create a reproducible file inventory after all checks pass:

```bash
python3 scripts/release_check.py --write-manifest
```

The generated `RELEASE_MANIFEST.json` excludes itself. For the complete package gate, also run `python3 scripts/validate_release.py`; the latter may require optional media and visual-test dependencies.

## Limits

Mechanical validation does not prove meaning. Deterministic revision closure is intentionally conservative. External publication, client delivery, academic use, and consequential decisions still require the external-use gate and human responsibility.
