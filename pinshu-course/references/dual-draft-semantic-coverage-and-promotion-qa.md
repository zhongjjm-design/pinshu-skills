# Semantic Coverage and Formal-Promotion Acceptance for Paired Drafts

## When to Use

Use this workflow when a long lesson's `faithful-edited-transcript` and `systematized-lecture` were generated in parallel by the primary Agent, subagents, or batch scripts, and then must be promoted from a temporary area into the formal course library with the index updated.

This reference addresses four risks beyond mechanical Markdown validation:

1. A subtask reports completion, but the file was never written or was only partially modified.
2. Both drafts satisfy formatting rules but independently omit a critical case, number, person, or quotation.
3. STT drops digits or produces conflicting values, and an editor infers a missing ten-thousand unit, fills in an ending value, or selects one figure from context.
4. Formal files are written successfully, but the course index, Wikilinks, or preview still points to an old path.

---

## 1. Build a Semantic-Coverage Checklist Before Running Format Checks

Extract a short checklist from the authoritative source containing at least:

- instructor, course, and event track;
- three core judgments;
- critical people and account names;
- core methods and stage order;
- critical numbers, amounts, ratios, times, and counts;
- important case names, cities, industries, and outcomes;
- explicit STT corrections;
- removable material: device setup, applause, purchase prompts, and no-information interaction;
- conflicting figures and proper nouns that must enter the end-of-document verification section.

Because the paired drafts have different responsibilities, divide the checklist into two columns:

| Acceptance item | Faithful edited transcript | Systematized lecture |
|---|---|---|
| First-person voice and speaking order | Required | Not required |
| Complete argument and case process | Required | May be reorganized |
| Method models, case cards, and execution checklists | May be consolidated at the end | Required |
| Verbatim quotations | Must come from the source | Must remain separate from editorial distillation |
| Critical people, figures, and cases | Each must have a destination | Must appear in the body or a case card |
| Editorially added SOPs | Must not enter the instructor's voice | Must be labeled `editorial-distillation` / `execution-guidance` |

Do not use one set of `--require` arguments to force both files to contain exactly the same literal text. Mechanical checks govern formatting; the semantic checklist governs role-specific content coverage.

### Literal-Matching Cautions

- Search normalization may remove spaces, commas, and full-width/half-width differences.
- Do not automatically treat Chinese numerals and Arabic numerals as the same fact, especially for amounts, ratios, and view counts.
- Match person, brand, and course names exactly against the authoritative spelling.
- Cases may be merged into one card, but the people, actions, figures, and boundaries must not disappear through merging.

---

## 2. Order for Handling Conflicting Numbers

When `110 yuan` may be missing a ten-thousand unit, the live speech contains both `4.57 million` and `4.67 million`, or an ending value is incomplete:

1. Preserve the visible form in the raw transcript.
2. Inspect surrounding context and conclude only that a conflict or omission exists; do not fill a definitive value from context.
3. In the faithful transcript, state that the exact amount/value cannot be confirmed or retain both spoken variants.
4. In the systematized lecture, use a range or parallel values labeled `course-spoken` / `pending-verification`.
5. Consolidate the original conflict in the end-of-document verification section.
6. Replace a pending value with a definitive one only after reviewing slides, visuals, or another authoritative source.

Never:

- change `110 yuan` to `1.1 million yuan` because that scale appears more plausible;
- choose one of two spoken variants and present it as settled;
- describe an unverified inserted number as “conservative editing”;
- present instructor revenue, follower, sales, or platform-mechanism claims as externally verified facts.

---

## 3. Read Subtask Deliverables; Do Not Trust Self-Reports

A subagent's `file-written`, `completed`, or `self-checked` status is only a lead. The primary Agent verifies in this order:

1. Confirm that the temporary path exists.
2. Read the actual file as UTF-8 and confirm byte count, character count, line count, and zero NUL bytes.
3. Count the unique H1, H2/H3 structure, blank lines after headings, overlong lines, and residual timestamps.
4. Sample the opening, main method throughline, 3–5 case cards, and end-of-document verification section.
5. Run the lesson-specific STT forbidden-term list and critical semantic checklist.
6. Run `scripts/validate-course-markdown.py`.
7. Make targeted corrections only; do not redelegate an entire slow refinement pass for a small number of residual issues.

If a normal text reader misclassifies UTF-8 Chinese Markdown as binary, use Python `Path.read_text(encoding="utf-8")` as a read-only fallback, then continue checking NUL bytes, line count, and heading structure. Record the reliable readback result; do not generalize one classification error into “the tool is unusable.”

---

## 4. Formal Promotion Uses a Single-Writer, No-Overwrite Protocol

Only the primary Agent writes to the formal course library:

1. Subagents write only to exclusive temporary directories.
2. The primary Agent completes content and mechanical acceptance.
3. Before writing a formal file, confirm that the target does not exist; reject overwrites by default.
4. Write the paired drafts serially to the formal instructor directory.
5. Update the master course index.
6. Reread from the formal paths; do not reuse results from the temporary area.
7. Resolve every Wikilink in the index; broken-link count must be zero.
8. Open the primary reading draft in the preview area and inspect its low-density layout and navigation.
9. In the completion report, provide only absolute paths, primary outcomes, and critical acceptance results.

Minimum readback fields after the formal write:

- file existence, byte count, character count, and line count;
- exactly one H1;
- number of fixed sections;
- zero missing blank lines after headings;
- zero lines longer than 160 characters;
- zero forbidden STT terms;
- case-card count;
- count of end-of-document verification items;
- number of new index entries;
- zero broken links across the entire index.

### Frontmatter and Lossless-Promotion Reconciliation

Before promoting paired drafts, complete traceability metadata rather than retaining only `tags`:

- The faithful transcript includes at least `speaker`, `course`, `document_type`, and `source_message_id`; add `source_ppt` when companion slides exist.
- The systematized lecture includes at least `title`, `speaker`, `course`, `content_type`, and `source_message_id`; add `source_ppt` when companion slides exist.
- `source_message_id`, slide names, and event tracks must come from the current authoritative source, never from an old draft or adjacent course.

After the formal write, calculate SHA-256 for each temporary accepted draft and its formal copy; require exact equality. If hashes differ, compare content before deciding whether promotion was lossless. Two readable files are not sufficient evidence. After writing the index, check not only the new entry but **every** Wikilink so that adding a section cannot silently break an existing link.

Treat any late subtask result as a stale snapshot. After formal promotion, it may only be reconciled and absorbed through targeted edits; never overwrite the whole file with it.

---

## 5. Applying the Fixed Nine-Part Structure to Paired Drafts

When the course series uses a value-first structure, both drafts keep the same top-level order:

1. `big-watermelons` (at most three);
2. faithful edited transcript / systematized lecture;
3. methods and execution checklist;
4. cases, figures, and tools;
5. verbatim quotations;
6. editorially distilled insights;
7. connections to the user's business;
8. zero or one WeChat Moments topic;
9. editorial verification at the end, with at most four items.

Within Part 2, the faithful transcript may use H3 headings in the original speaking order. The systematized lecture may reorganize by method module and separate cases into case cards. Do not turn the faithful transcript into a third-person summary merely to standardize the structure.

---

## 6. Low-Density Completion Report

When the user is submitting lessons continuously, the default completion report contains only:

- `persisted-and-accepted`;
- the two absolute paths;
- confirmation that the primary reading draft was opened;
- three to five critical acceptance results;
- any figures or factual boundaries still pending verification.

Do not replay the complete process or expand every check into a wall of text.
