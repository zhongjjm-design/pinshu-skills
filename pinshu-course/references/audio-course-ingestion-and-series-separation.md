# Batch Intake, Transcription, and Series Separation for Audio Courses

Use this workflow when one instructor has multiple online and in-person courses delivered as dozens of long audio files, attachments, and scattered Skill files.

## 1. Apply the Course Identity Gate First

Do not assume that materials belong to the same course merely because of the download-folder name, recording-file dates, or nearby course context.

Before writing a batch to the formal course library, verify at least:

- the instructor;
- the course format: online warm-up, formal online course, in-person course, or bonus course;
- the actual teaching dates and location;
- whether the materials are chapters of one course or separate products from the same instructor;
- whether the formal course title is known.

User-confirmed information outranks recording filenames. A date in a filename may represent only a save date, export date, or automatically assigned date.

When one instructor has multiple courses, prefer a two-level structure:

```text
[instructor-course-series]/
├── 01_online-courses/
│   └── [course-title]/
└── 02_in-person-courses/
    └── [course-title-derived-after-complete-analysis]/
```

If the course title is unknown, transcribe and analyze the material in a temporary workspace first. Do not use names such as “Three-Day Course by X” or “Course Pending Organization” as the long-term formal title.

## 2. Inventory Source Audio Before Renaming Anything

Keep the downloaded filenames and first create an asset ledger covering:

- file count, total size, and total duration;
- continuity of dates and sequence numbers;
- `ffprobe`/media readability;
- SHA-256 content hashes and duplicate groups;
- suffixes such as “autosaved”;
- unusually short, unusually long, or anomalous-duration files.

Do not deduplicate based only on matching sequence numbers; the same number on different dates may represent different recordings. Only identical content hashes establish byte-for-byte duplication.

## 3. Run Trial Transcriptions Before the Full Batch

Sample one segment from each of these categories:

- a clear middle section containing substantive instruction;
- an ending, interactive, or noisy segment.

Do not judge model quality using only the shortest audio file. It may happen to contain post-session conversation, silence, or non-course content.

Compare:

- completeness of continuous Chinese speech;
- names, brands, numbers, and domain terminology;
- hallucinations such as repeated “thank you” during silence;
- speed and total cost;
- whether a paid API is required.

Prefer a local option unless the user has explicitly approved usage-based charges. On Apple Silicon, evaluate MLX Whisper first; use standard Whisper only as a fallback or for small-scale testing.

## 4. Stable Parameters for Local MLX Whisper

Begin testing with a high-quality Chinese model, such as an MLX build of `whisper-large-v3-turbo`. Recommended settings for long courses:

```text
language=zh
condition_on_previous_text=False
word_timestamps=True
hallucination_silence_threshold≈1.5
output_format=all
```

Rationale:

- Disabling forced continuation from previous text reduces error loops and repeated passages.
- Word-level timestamps support later review and correction.
- The silence-hallucination threshold suppresses repeated text during dismissal, pauses, and ambient noise.
- `all` must retain at least TXT, JSON, SRT, VTT, and TSV; a single cleaned Markdown file is insufficient.

Include only high-confidence terminology in the initial prompt. Do not insert an unconfirmed course title, person name, or product name, because an incorrect prompt can bias the model.

## 5. Batch Jobs Must Be Recoverable

For long-running batch transcription, create:

- a task-state file;
- per-file START/DONE/FAIL logs;
- automatic skipping when complete TXT and JSON outputs already exist;
- isolation so that one failed file does not overwrite other results;
- read-only handling of the source-audio directory;
- transcription output in the runtime workspace first, with promotion to the formal knowledge base only after course identity and titles are confirmed.

The task state must record at least the asset path, model, parameters, completed steps, next action, and formal output parent directory.

## 6. Three-Layer QA After Transcription

### File Layer

- TXT, JSON, and subtitle files exist for every audio file.
- Output count matches audio-file count.
- There are no empty texts, zero-byte files, or anomalously short texts.
- Timestamp coverage approaches the source-audio duration.

### Text Layer

- Scan for silence hallucinations and consecutively repeated sentences.
- Normalize frequent STT errors.
- Add names, brands, book titles, prices, percentages, and platform terms to a pending-confirmation glossary.
- Do not guess unclear proper nouns from machine transcription alone.

### Course Layer

- Reconstruct course boundaries from actual teaching dates, natural topic boundaries, and instructor transitions.
- Do not mechanically treat every MP3 as one lesson.
- Do not collapse every audio file from the same day into one lesson.
- Build a day/module map before creating paired drafts for each lesson.

## 7. Detailed Organization Standard for Scarce In-Person Courses

When the user states that the in-person material is scarce and information-dense, add the following beyond the paired drafts for each lesson:

- source transcript and audio-timestamp index;
- master course map;
- methodology and model library;
- complete case library;
- tool/platform/Skill resource library;
- assignments and execution templates;
- verification table for facts, platform rules, and revenue claims;
- index of original course attachments, including PPT, DOCX, and Skill files.

Do not install an attached Skill automatically. Read every file first, then evaluate it against four stable criteria: `fit`, `readiness`, `direct-output-value`, and `parsimony`.

- Does it solve a real, recurring scenario?
- Does it depend on missing files or obsolete paths?
- Does it duplicate an existing Skill?
- Does it contain fabricated references, outdated platform rules, or unsafe hard rules?
- Should it be installed directly, absorbed into an existing Skill, or retained only as course evidence?

## 8. Final Four-Way Reconciliation

Before delivery, reconcile:

```text
actual course dates/modules
↔ source audio and attachments
↔ raw transcripts and timestamps
↔ faithful edited transcripts, systematized lectures, and cross-topic knowledge library
```

Do not declare completion if any layer has an unknown identity, mismatched counts, broken links, or a title that cannot be traced to its source.
