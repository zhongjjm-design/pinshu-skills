# Multi-Lesson Asset Attribution and Cross-Lesson Contamination Recovery

Use this workflow when transcripts, screenshots, slides, audio, and video arrive interleaved across a continuous course series. Establish asset ownership before any formal write. If cross-lesson contamination occurs, recover the whole set in a verifiable order.

## 1. Authority Order

Determine attribution in this priority order:

1. the user's explicit statement of lesson number and attachment ownership;
2. first-party markers such as the official lesson title, slide header, or lesson number shown in the video;
3. an asset-attribution table confirmed by the user;
4. filename and timestamp, used only as supporting evidence;
5. content similarity, message proximity, and interface display order, none of which may establish attribution alone.

“Highly relevant to the next lesson” does not mean “belongs to the next lesson.” During continuous uploads, images from a previous lesson may appear near the next lesson's transcript.

## 2. Pre-Execution Asset Ledger

Display and confirm first:

| Lesson | Official title | Transcript first–last sentence | Images/slides | Asset state | Attribution basis | User confirmed |
|---|---|---|---:|---|---|---|
| Lesson XX |  |  | N images | complete / missing / no images for this lesson |  | yes/no |

Record all three states explicitly:

- `received-N-images`;
- `image-attribution-pending`;
- `no-images-for-this-lesson`.

`no-images-for-this-lesson` is a confirmed fact, not a blank. Recommended frontmatter:

```yaml
source_state: complete-transcript-received; no-images-for-this-lesson
```

## 3. Attribution Gate

Before confirmation, the following are allowed:

- read-only inspection of attachments;
- hashing, deduplication, and reading image dimensions;
- temporary numbering and an attribution-candidate table.

Before confirmation, the following are prohibited:

- creating the formal `{lesson_assets}` target;
- embedding images in a faithful transcript or lecture;
- expanding a lesson body from image content;
- updating the course map to `organized`;
- delegating a background task that writes formal files.

After confirmation, use this order:

1. archive the physical images;
2. verify count, deduplication, and relative paths;
3. create the faithful edited transcript;
4. create the systematized lecture;
5. update the course map;
6. perform four-way reconciliation.

## 4. Boundaries for Images in the Body

- An image enters only the lesson to which it belongs.
- Content unique to slides is labeled `slide-supplement` and must not be presented as spoken by the instructor.
- The transcript remains authoritative for the faithful draft; images provide evidence and supplementation but must not rewrite the instructor's meaning.
- A lesson without images must not borrow images from adjacent lessons, even when the topics continue across them.
- A structured lecture may explain slides from the same lesson, but it still distinguishes speech, slides, editorial analysis, and unverified facts.

## 5. Recovery Order After Cross-Lesson Contamination

Stop immediately when attribution is found to be wrong. Do not continue “while already here.”

### A. Stop Side Effects

- Stop or cancel related background Agents, build tasks, and batch jobs.
- Stop updating the course map.
- Do not mark contaminated intermediate drafts as complete.

A background task that times out or is stopped may still have written a partial or complete file. Inspect target paths; never interpret `timeout` as “no side effects.”

### B. Take a Read-Only Inventory

List separately:

- incorrect and correct image directories;
- faithful transcripts and in-depth lectures for each lesson;
- image references, source metadata, and lesson-specific cases in every file;
- corresponding rows in the course map;
- background tasks still running or recently completed.

### C. Recover the Authoritative Source

- Prefer the user's original message, source file, or audio/video transcript.
- If context compaction makes the source unrecoverable, ask the user to resend it.
- Do not infer the raw transcript backward from a contaminated lecture, old summary, or conversation summary.

### D. Restore Physical Placement

First move images to the correct manifest/path-map target `{lesson_assets}`, then verify counts and hashes before editing documents. If the incorrectly assigned lesson is confirmed to contain no images, remove its empty image directory and every image path from its files.

### E. Rebuild; Do Not Merely Change Links

Cross-lesson contamination creates two types of corruption:

1. explicit corruption: incorrect image links;
2. implicit corruption: models, cases, names, and conclusions unique to an image enter the wrong lesson body.

Changing paths alone is therefore insufficient. Instead:

- return the faithful transcript to the raw transcript and remove image-derived lesson-specific content;
- regenerate the in-depth lecture from the cleaned faithful transcript by default, overwriting the incorrect old draft;
- for a no-image lesson, require `image syntax=0`, `assets paths=0`, and `adjacent-lesson-specific terms=0`;
- for the correct lesson, confirm that image count, unique-image count, and missing-link count match expectations.

### F. Correct the Map and State

Change the map to `organized` only after all four per-lesson files and image directories pass checks. Update both the received-transcript range and next expected lesson.

## 6. Four-Way Reconciliation Template

| Lesson | Authoritative transcript | Image directory | Faithful transcript | In-depth lecture | Image references | Cross-lesson-specific terms | Map state |
|---|---|---|---|---|---:|---:|---|
| Lesson XX | path/message anchor | `{lesson_assets}` or “no images” | path | path | N | 0 | `organized` / `pending-acceptance` |

Minimum acceptance:

- all four files exist and begin with `tags`;
- for lessons with images: image count equals expectation, references are unique, and no link is missing;
- for lessons without images: zero Markdown image syntax and zero references to the rendered lesson-assets target;
- people, cases, models, and source notes unique to adjacent lessons did not cross lesson boundaries;
- source state in frontmatter matches actual assets;
- map title, knowledge title, progress, and next lesson agree;
- a subagent's “complete” message is only a lead; the primary Agent reads and accepts the actual files.

## 7. Multi-Agent and Late-Task Precautions

- Every delegated task names the authoritative source file, target lesson, image directory, and adjacent-lesson content that must not be referenced.
- State explicitly whether a subtask overwrites the target file or performs a targeted edit. During contamination recovery, prefer complete overwrite from a clean source.
- Multiple subtasks must not write the same file concurrently.
- **Invalidation fence:** when the user says “stop,” corrects the lesson number, or changes asset attribution, the old delegation becomes logically invalid immediately. A late completion notice is stale information and cannot support a success claim.
- Prefer background tasks that write temporary candidate files for primary-Agent acceptance before formal promotion. If direct writing cannot be avoided, reread the final persisted file after the task completes.
- After a subtask times out, inspect actual modification time, source metadata, and content before deciding whether to overwrite or delete; `timeout` does not mean no file was written.
- If a late subtask overwrites a formal version already produced by the primary Agent, recheck image count, missing links, adjacent-lesson-specific terms, critical figures, source metadata, and risk boundaries.
- The primary Agent owns final acceptance for attribution, paths, figures, images, and boundaries; it must not accept a subagent's self-report directly.
