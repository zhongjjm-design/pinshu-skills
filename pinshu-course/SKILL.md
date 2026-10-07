---
name: pinshu-course
description: "Use when a multi-lesson course needs ongoing organization, learning, practice, and cross-lesson synthesis."
---

# Pinshu Course-Series Orchestration

## Origin and maintenance

- Original work: Pinshu original (`original`)
- Owner and maintainer: Aidan (Pinshu)
- Content capabilities: `pinshu-transcript`, `pinshu-distill`, `pinshu-study`, `pinshu-content-assets`
- Distribution status: `bundled`

Orchestrate a traceable course library: identity, purpose, progress, concurrency, pending synthesis, and promotion. Delegate specialized content production.

When a capture state exists, `pinshu-course-capture` remains the authority for paths, evidence binding, promotion hygiene, and accepted-file revisions. Update the shared course map serially, then register its latest baseline through that pipeline. Never edit an `ACCEPTED` official pair outside `revision-open` / `revision-close`.

## Common foundation and course purpose

Every lesson has four core results: immutable raw transcript, faithful edit, structured notes, and one idempotently updated shared-map entry—not an extra map file. The faithful edit is the downstream content source; raw recordings/transcripts are ultimate evidence. Recheck mnemonics, numbers, safety, cases, and disagreements against both as needed.

Record purpose and evidence from course title, structure, content, and user goal. Systematic study, professional foundations, bootcamps, certifications, and exam preparation enable review and practice by default unless excluded. Source collections, interviews, and opinion courses need only the four core results unless learning or content reuse is requested. When content reuse is selected, add sourcebooks after the accepted core results; this is not an automatic article. If purpose conflicts or is unclear, recommend a route and ask; do not silently disable learning. Discipline name is insufficient evidence. Cards/questions are not proof of study; records need real activity.

## Responsibility across the course capabilities

```text
pinshu-course-capture: immutable raw capture and per-lesson production orchestration
pinshu-transcript: raw transcript -> faithful edited transcript
pinshu-distill: faithful transcript -> structured lesson notes
pinshu-course: course map, state, checkpoints, cross-lesson assets and promotion
pinshu-study: enabled recall cards and training questions; records only after real learning
pinshu-content-assets: one source-traceable content master per lesson plus a course-level master when requested; both pending review
```

## Identity and authorization gates

Bind course ID, instructor, cohort, write root, and sources. Current-session identity outranks similar lesson numbers, stale summaries, or cross-session results. Pause on identity/lesson conflict, truncated source, or destination outside the approved root. See `references/multi-conversation-course-identity-gate.md`.

- Collection: receive material and feedback; do not draft.
- Discussion: compare approaches and samples; do not write formal results.
- Execution: produce only explicitly confirmed scope.
- Ongoing series authorization applies only to this course, root, and agreed results; changed identity, root, or rules void it.

For ambiguous lesson attribution read `references/lesson-asset-attribution-and-recovery.md`; do not ask again when attribution is already explicit.

## Directories, language, and titles

Read an existing course map, directories, and peer files first; reuse names and numbering, never a parallel tree. For a new course, confirm a project-specific path map; this layout is illustrative:

```text
{course root}/
├── 00_Course_Map.md
├── 00_Source_Transcripts/
├── 01_Faithful_Edits/
├── 02_Structured_Lectures/
├── 03_Review_and_Practice/    # only when the learning purpose is enabled
│   ├── 01_Active_Recall/
│   └── 02_Practice_Bank/
├── 04_Learning_Records/       # only after real learning
│   ├── 00_Progress.md
│   ├── 01_Practice_Sessions/
│   └── 02_Errors_and_Rechecks.md
├── 05_Content_Assets/         # only when content reuse is requested
├── assets/                    # only for real visual material
└── 99_Production_Control/     # only when a production pipeline runs
```

No empty optional directories. In the learner's language, the map explains: read notes → recall → practice → records → retest, with status/next step. Use generic learner paths, separate raw intake from expert-owned knowledge, and keep machine keys in English. See `references/course-directory-layout-and-creation-rules.md`.

Directory expresses document type; filename and H1 express content. Do not repeat type/status words already expressed by the directory. After reading fully, choose lesson number + distinctive question, judgment, case, method, or result. Filename, H1, and frontmatter `title` share the hook. If it cannot distinguish nearby lessons without redundant phrases, leave naming pending instead of promoting a generic placeholder.

## Per-lesson production

1. Confirm course identity, lesson, source, and destination; save and verify the immutable raw transcript.
2. One content writer produces the faithful edit and structured notes together; run deterministic checks and writer semantic self-review.
3. Invoke independent QA only for risk triggers or adaptive sampling. The unique committer promotes the paired drafts and idempotently updates the course map.
4. If learning is enabled, ask `pinshu-study` to make separate recall cards and a training-question bank; they should not substantially duplicate each other. Do not create personal learning records until the learner actually studies or answers.
5. If content reuse is explicitly enabled, `pinshu-content-assets` reads the accepted faithful edit and guide and produces one readable, source-traceable content master per lesson. For the full course, create a separate cross-lesson master that links back to those lesson documents. Both remain pending the user's editorial review; do not auto-write an article or treat a machine PASS as approval.
6. At module close, create cross-topic studies, integrated cards, or mixed practice when useful.

Each pending cross-lesson clue is a collection item, not a formal learning article; label it current-lesson candidate, later-lesson foreshadowing, verified across lessons, or safety-governance candidate. “Verified” requires an actually read second source. Keep only a concise learner-facing summary in the course map. See `references/cross-course-clues-and-independent-qa-rules.md`.

The four core results remain required even when extensions are disabled. Historical pilots are validation evidence, not production gates. With no real answers, learning state is “not started”; never fabricate progress or mastery.

For content-oriented courses: keep the faithful edit, lecture, and map intact; enable a separate content-master layer only when requested. Consolidate knowledge and sourcebooks separately after a module or a small run of lessons. Do not write sourcebook material back into the faithful transcript or notes. See `references/course-to-social-content-reuse.md`.

## After transcript completion

Route to the actual desired result: **understand** (notes/topics), **master** (recall/practice/retest), **explain** (first explanation, audience questions, repair, second explanation), **apply** (real hypothesis/action/metric/review), **reuse for content** (`pinshu-content-assets` lesson and course sourcebooks, subject to user review; downstream publishing only through a separately configured workflow), or **productize** (methods verified by actual use). Do not run all routes by default. Read `references/post-course-learning-propagation-application-and-assetization-loop.md`.

## One writer and evidence-based state

Only one content writer creates each lesson's paired drafts; capture, deterministic scripts, QA, and the committer are not second writers. Subagents draft in exclusive temporary directories and never write formal library files; one committer promotes serially. Clean ordinary lessons may promote after generation, mechanical checks, and semantic self-review; independent QA is triggered by risk or adaptive sampling, not mandatory on every lesson. File existence, script PASS, and a subagent's self-report do not prove content acceptance. Exhaustive claims require reverse evidence. See `references/concurrent-course-write-safety.md` and `references/approved-course-file-write-and-readback.md`.

## References by scenario

### Input, boundaries, recovery

- Long series: `references/long-course-series-workflow.md`
- Transcript first: `references/transcript-first-dual-deliverable-order.md`
- High-throughput text: `references/pure-text-high-throughput-lesson-processing.md`
- Long lesson chunks: `references/long-lesson-chunked-write-map-and-sequence-qa.md`
- Recording order/overlap: `references/mixed-recording-order-and-overlap-dedup.md`
- Replayed transcript/terms: `references/repeated-playback-transcript-dedup-and-term-authority.md`
- Live lessons/sales noise: `references/multi-lesson-live-transcript-boundary-and-sales-noise.md`
- Noncontiguous lessons: `references/non-contiguous-lesson-ingestion-and-map-state.md`
- Late gaps/module close: `references/late-gap-closure-and-module-finalization.md`
- Interrupted batch: `references/resume-interrupted-batch-course-work.md`

### Terminology, visuals, relationships

- Confirmed terms: `references/term-confirmation-propagation-and-zero-residual-qa.md`
- Screenshot/reversal: `references/screenshot-prompt-recovery-and-reversal-corrections.md`
- Slides/images: `references/companion-course-materials-and-visual-references.md`
- Multiple images: `references/multi-image-ingestion-and-final-verification.md`
- Relationships/missing visuals: `references/relational-consistency-and-missing-visuals.md`
- Attribution: `references/lesson-asset-attribution-and-recovery.md`

### Paired drafts and QA

- Visual integration/approval: `references/transcript-visual-integration-and-approval-gates.md`
- Value-first delivery: `references/value-first-course-delivery-and-propagation.md`
- Semantic fidelity: `references/semantic-fidelity-and-batch-qa.md`
- Two-pass edit: `references/two-pass-faithful-editing-and-output-containment.md`
- Draft coverage: `references/dual-draft-semantic-coverage-and-promotion-qa.md`
- Same-name drafts/permissions: `references/same-name-dual-draft-preview-and-permission-aware-qa.md`
- Lecture provenance: `references/systemized-lecture-provenance-and-reverse-coverage.md`
- Readability: `references/readability-first-long-course-markdown.md`
- Heading spacing: `references/markdown-spacing-and-late-agent-output-control.md`

### Specialized content

- Module entry: `references/module-entry-and-irreversible-framework-lessons.md`
- Dense platform lesson: `references/high-density-platform-course-processing.md`
- Relationships/public issues: `references/relationship-group-public-issue-course-processing.md`
- Persona/positioning: `references/identity-and-persona-course-processing.md`
- Type/style/growth: `references/type-style-and-growth-positioning-course-processing.md`
- Video technical: `references/video-production-course-technical-normalization-and-qa.md`
- AI module close: `references/module-closure-package-and-ai-course-normalization.md`
- Product marketing/risk: `references/product-marketing-course-risk-and-module-closure.md`
- Private-domain compliance: `references/private-domain-course-compliance-and-permission.md`

### Cross-topic, archive, delivery

- Professional learning: `references/professional-course-learning-asset-pipeline.md`
- Learning/application loop: `references/post-course-learning-propagation-application-and-assetization-loop.md`
- Cross-course synthesis: `references/cross-course-horizontal-synthesis.md`
- Final cross-topic QA: `references/horizontal-knowledge-base-final-qa.md`
- Module close: `references/module-closure-package-and-ai-course-normalization.md`
- Dissemination compatibility: `references/course-to-social-content-reuse.md`
- Packaging/cleanup: `references/formal-course-packaging-and-cleanup.md`
- Multi-event archive: `references/multi-event-course-archive-taxonomy-and-safe-move.md`

### Audio/video ingestion

- Apple Silicon batch transcription: `references/apple-silicon-batch-course-transcription.md`
- Multi-course audio: `references/audio-course-ingestion-and-series-separation.md`

## Final QA and scale-up

Check identity, lesson, immutable-source completeness, paired-draft separation, content-bearing title and frontmatter, semantic coverage, terms, links, pending confirmation, safety, exactly one resolvable map entry. For enabled learning, check recall vs. question-bank overlap; no `%%`, HTML, item IDs, or engineering fields in reading text; small file-level frontmatter; separate card and question indices matching body type, count, sequence, and unique IDs. For enabled content reuse, check the map's sourcebook link and pending/approved status here; `pinshu-content-assets` owns source traceability, corrected quotations, content completeness, and its separate human review gate. Representative files must actually open in the target reading interface to inspect properties, collapsed answers, mobile layout, and code leakage. Script PASS does not prove semantic or visual acceptance.

Run `scripts/validate-course-markdown.py` for Markdown structure and `scripts/validate-learning-assets.py --kind lecture|cards|questions|clues <paths>` for enabled learning assets. Neither script certifies sourcebook quality. The public `pinshu-content-assets` package provides its own workflow and a portable route resolver; its sourcebook requires a human read against the edited transcript and guide before it becomes an approved writing input. Missing downstream routing blocks platform handoff, not local delivery at an approved project path.

Before scaling, inspect representative lesson layout, detail, faithful edit, notes, and map entry. Clinical/case reasoning, strongly visual/hands-on work, important numbers, and consequential claims trigger independent QA; ordinary lessons follow adaptive sampling. A real guided-study cycle is acceptance of the enabled learning experience, not a prerequisite for basic production or updating the map. Stop at the agreed deliverable scope.
