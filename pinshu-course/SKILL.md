---
name: pinshu-course
description: "Use when a multi-lesson course requires ongoing organization, study, practice, and cross-lesson synthesis."
---

# Pinshu Course-Series Orchestration

## Origin and Maintenance

- Original work: Pinshu original (`original`)
- Owner and maintainer: Aidan (Pinshu)
- Content capabilities: `pinshu-transcript`, `pinshu-distill`, `pinshu-study`
- Distribution status: `bundled`

Build a multi-lesson course into a traceable, learnable, and continuously maintainable course-asset library. This Skill manages course identity, scope, progress, concurrency, checkpoints, pending synthesis clues, and promotion into the formal library. It does not replace the three content Skills.

## Determine the Course Goal First

- **Professional learning:** faithful edited transcripts, structured lectures, active recall, guided practice, and formal cross-topic studies; read `references/professional-course-learning-asset-pipeline.md`.
- **Content assets:** paired drafts, methods and cases, publication material, and fact-checking.
- The two may be combined, but professional-learning courses in fields such as traditional Chinese medicine or Chinese divination do not produce publication material by default.

## Division of Responsibility Across the Four Capabilities

```text
pinshu-transcript: source material → faithful edited transcript
pinshu-distill: faithful edited transcript → structured lecture; module material → formal cross-topic study
pinshu-study: lecture → active recall; guided study, practice, error diagnosis, and personal records
pinshu-course: whole-course orchestration, state, checkpoints, and pending synthesis clues
```

The faithful edited transcript is the content source of truth for all downstream learning assets; the source audio/video and raw transcript are the final evidence. When downstream work encounters mnemonics, numbers, safety claims, cases, or disagreements, check the faithful transcript. If the faithful transcript is uncertain, return to the source evidence.

## Course Identity Gate

Bind each course to a course ID, instructor, cohort, one authoritative write root, and authoritative sources. The current session identity outranks similar lesson numbers, old summaries, stale Todos, and cross-session search results.

Pause without generating any draft if another instructor or course appears, lesson numbers conflict, the source is truncated, or the target path leaves the write root. See `references/multi-conversation-course-identity-gate.md`.

## State Gate

- **Collection state (`collection`)**: continue receiving transcripts, images, and feedback; do not draft.
- **Discussion state (`discussion`)**: compare approaches and samples; do not create formal deliverables.
- **Execution state (`execution`)**: execute the agreed scope only after explicit user confirmation.
- **Ongoing series authorization (`ongoing-series-authorization`)**: applies only to the current course, directory, and agreed deliverables; it expires when the identity, directory, or rules change.

When asset attribution is unclear, use `references/lesson-asset-attribution-and-recovery.md`. Do not ask again when the user has already specified the lesson and asset attribution.

## Minimum Directory Structure

If course-capture state or a manifest exists, resolve every target through its path-template key; do not translate or invent a directory name. Otherwise inspect the existing course and confirm an explicit path map before writing. Existing structure and numbering always take precedence, and synonymous or empty directories must not be created. For a completely new course, create and confirm the manifest or path map described in `references/course-directory-layout-and-creation-rules.md`. Keep raw intake separate from formal knowledge ownership, and file formal knowledge under the expert whenever possible.

## Learner Language

Public repository prose stays English. Learner-facing cards, study dialogue, explanations, sources, and records follow the manifest's `output_language` or the user's explicit preference. An omitted field means `match-user`, with source language as the fallback. Stable IDs, frontmatter keys, enum values, and program fields remain English. Do not prescribe English or Chinese learner-facing prose independently of this contract.

## Per-Lesson Professional-Learning Contract

For each lesson, preserve the sequence from source confirmation through faithful transcript, independent semantic QA, structured lecture, learner-visible active-recall cards in the resolved output language, course-map update, evidence-labeled synthesis clues, mechanical checks, real-study state handling, and module closeout. The four default assets are the manifest keys `official_faithful`, `official_lecture`, `active_recall`, and one idempotent entry at `course_map`; count atomic and integrative cards separately, and do not let module-level synthesis block these assets. Study practice begins only when the user actually studies, reviews, answers, or retests; before real answers exist, mark it `not started` and never fabricate progress or mastery. Historical pilots validate rules but never gate current production or carry old non-promotion status forward. Use `references/professional-course-learning-asset-pipeline.md` for the complete per-lesson and module workflow, and `references/cross-course-clues-and-independent-qa-rules.md` for clue and independent-QA rules.

## Per-Lesson Workflow for Content Assets

1. Faithful edited transcript.
2. Systematized lecture.
3. Course map.
4. Use `references/course-to-social-content-reuse.md` when publication material is needed.
5. Every 3–5 lessons, or at module closeout, synthesize methods, cases, tools, templates, and factual risks.

## After the Transcript Is Complete: Route It Instead of Letting the Course Sit in the Library

Organization is not the endpoint of a course task. Route the material to one or more outcomes based on the user's actual purpose:

- **Understand:** structured lectures, concept relationships, and cross-topic studies.
- **Master:** active recall, follow-up questions, error diagnosis, source checks, and retesting.
- **Explain:** teach it to someone else using the Feynman method, field audience questions, expose gaps, correct them, and explain it again.
- **Apply:** transfer the method to a real project and define hypotheses, actions, metrics, and a review.
- **Publish:** create external-facing material from the user's real experience rather than restating the instructor's views as course homework.
- **Productize:** turn methods validated through real use into cases, SOPs, Skills, or products.

Do not run all six routes by default. First determine whether the user currently wants to understand, remember, explain, apply, publish, or productize the material, then invoke the corresponding Skill. Read the complete rules in `references/post-course-learning-propagation-application-and-assetization-loop.md`.

## Single Writer and State Progression

Only the primary Agent writes to the formal course library. Subagents draft only in exclusive temporary directories; the primary Agent reads the actual output, computes programmatic statistics, performs independent QA, and then promotes it serially. Advance state only on real evidence: source material saved → initial draft → generator self-check → independent QA → rework → in-place re-verification → accepted. A subagent's report, file existence, and a script PASS do not constitute content acceptance. Strong claims such as “all,” “nothing omitted,” “no composite items,” and “independently learnable” require negative evidence.

See `references/concurrent-course-write-safety.md` for concurrency rules and `references/approved-course-file-write-and-readback.md` for writing and readback.

## Load References by Scenario

### Input, Boundaries, and Recovery

- Long series fundamentals: `references/long-course-series-workflow.md`
- Faithful transcript before lecture: `references/transcript-first-dual-deliverable-order.md`
- High-throughput plain-text processing: `references/pure-text-high-throughput-lesson-processing.md`
- Chunking an extremely long lesson: `references/long-lesson-chunked-write-map-and-sequence-qa.md`
- Reverse recording order and overlap: `references/mixed-recording-order-and-overlap-dedup.md`
- Repeated playback and terminology authority: `references/repeated-playback-transcript-dedup-and-term-authority.md`
- Multi-lesson live transcripts and sales noise: `references/multi-lesson-live-transcript-boundary-and-sales-noise.md`
- Non-contiguous lessons: `references/non-contiguous-lesson-ingestion-and-map-state.md`
- Filling late gaps and closing a module: `references/late-gap-closure-and-module-finalization.md`
- Interrupted-work recovery: `references/resume-interrupted-batch-course-work.md`

### Terminology, Visuals, and Relationships

- Propagating confirmed terminology: `references/term-confirmation-propagation-and-zero-residual-qa.md`
- Screenshot prompts and reversal corrections: `references/screenshot-prompt-recovery-and-reversal-corrections.md`
- Companion slides and images: `references/companion-course-materials-and-visual-references.md`
- Multi-image ingestion: `references/multi-image-ingestion-and-final-verification.md`
- Relationships and missing visuals: `references/relational-consistency-and-missing-visuals.md`
- Asset-attribution recovery: `references/lesson-asset-attribution-and-recovery.md`

### Paired Drafts and QA

- Integrating course visuals and execution approval: `references/transcript-visual-integration-and-approval-gates.md`
- Value-first delivery and publication layering: `references/value-first-course-delivery-and-propagation.md`
- Semantic fidelity and batch QA: `references/semantic-fidelity-and-batch-qa.md`
- Independent two-pass faithful editing: `references/two-pass-faithful-editing-and-output-containment.md`
- Paired-draft coverage and promotion: `references/dual-draft-semantic-coverage-and-promotion-qa.md`
- Same-name paired drafts and permissions: `references/same-name-dual-draft-preview-and-permission-aware-qa.md`
- Systematized-lecture provenance and reverse coverage: `references/systemized-lecture-provenance-and-reverse-coverage.md`
- Long-course readability: `references/readability-first-long-course-markdown.md`
- Heading spacing and late Agent output: `references/markdown-spacing-and-late-agent-output-control.md`

### Specialized Course Content

- Module entry and irreversible framework lessons: `references/module-entry-and-irreversible-framework-lessons.md`
- High-density platform courses: `references/high-density-platform-course-processing.md`
- Relationships and public issues: `references/relationship-group-public-issue-course-processing.md`
- Identity and positioning: `references/identity-and-persona-course-processing.md`
- Type, style, and growth positioning: `references/type-style-and-growth-positioning-course-processing.md`
- Video-production technical courses: `references/video-production-course-technical-normalization-and-qa.md`
- AI-course module closeout: `references/module-closure-package-and-ai-course-normalization.md`
- Product marketing and risk: `references/product-marketing-course-risk-and-module-closure.md`
- Private-domain operations and compliance: `references/private-domain-course-compliance-and-permission.md`

### Cross-Topic Work, Archiving, and Delivery

- Post-course learning, explanation, application, and productization: `references/post-course-learning-propagation-application-and-assetization-loop.md`
- Cross-lesson course outline and model library: `references/cross-course-horizontal-synthesis.md`
- Final QA for the cross-topic library: `references/horizontal-knowledge-base-final-qa.md`
- Module-closeout assets: `references/module-closure-package-and-ai-course-normalization.md`
- Reusing course material for publication: `references/course-to-social-content-reuse.md`
- Formal packaging and cleanup: `references/formal-course-packaging-and-cleanup.md`
- Multi-event archive taxonomy: `references/multi-event-course-archive-taxonomy-and-safe-move.md`

### Audio and Video Ingestion

- Batch transcription on Apple Silicon: `references/apple-silicon-batch-course-transcription.md`
- Separating multiple audio courses: `references/audio-course-ingestion-and-series-separation.md`

## Final QA

At minimum, verify the course identity, lesson number, source, file existence, separation of paired drafts, headings and frontmatter, semantic coverage, residual terminology errors, image links, pending confirmations, safety boundaries, course-map state, pending synthesis clues, deduplication of formal cross-topic studies, readable output in the resolved learner language, and hidden backend fields.

Run `scripts/validate-course-markdown.py` for mechanical validation. For professional lectures, cards, and clues, also run `scripts/validate-learning-assets.py --kind lecture|cards|clues <paths>`. Scripts prove only the structures, counts, labels, and paths they actually inspect; they do not replace independent semantic QA or the learner's real learning experience.

## Scale-Up Gate

Before batch-producing a professional-learning course, independently QA at least one composite lesson, one case-analysis or chart-reading lesson, one highly visual or hands-on lesson, and the faithful transcript, lecture, active-recall cards, and course-map entry for each sample. One real “guided study → recall → follow-up questions → source check → record” run is an acceptance criterion for the learning experience, not a prerequisite for generating per-lesson cards or updating the course map. Do not fabricate mastery when no real answer exists, but do not use that absence to downgrade or halt the card layer. Complete formal cross-topic synthesis and mixed practice at module closeout.