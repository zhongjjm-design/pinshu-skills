# Ingesting Multiple Course Screenshots and Final Verification

Use this reference when a user submits a long transcript together with multiple slides, screenshots, or temporary attachments for one course-processing task.

## 1. Inventory First, Draft Second

Do not archive material based on thumbnail counts or display order in the chat interface. Build an asset inventory first, recording:

- Original absolute path;
- Whether the file exists;
- File type;
- Pixel dimensions;
- File hash;
- Visible title, key text, and corresponding course topic.

If the image toolchain is temporarily unavailable, use native system commands to read dimensions and hashes. Preserve the general method of cross-checking through multiple paths, not a negative conclusion about one tool.

## 2. Deduplicate and Sort Semantically

1. Use hashes first to detect byte-identical duplicates; retain one copy for matching hashes.
2. Then perform semantic deduplication. If different hashes represent crops, resizes, or varying screenshot boundaries of the same slide, retain the clearest version with the most complete text. Record in source metadata: “N images received; M retained after semantic deduplication.”
3. Temporary attachments, desktop attachments, and images embedded in messages may reside in different directories; inventory them together.
4. **Screenshot time is supporting evidence only; it does not replace semantic course order.** A user may return to the opening slide after class, so the last screenshot could be the opening overview.
5. Visually inspect attachments that were not expanded in chat. Never assume they duplicate visible thumbnails.
6. Name the final files by “position in course + topic,” for example: `01_Follower-Growth-Milestones.png` and `02_Spiral-Growth-Model.png`.

## 3. Permanent Archival

- Copy assets from temporary storage into the course's manifest/path-map target `{lesson_assets}`;
- Do not reference `/private/var/...`, desktop attachment folders, or any other temporary path from formal documents;
- Preserve original images unless the user explicitly asks for cropping, redaction, or compression;
- Use the same relative path rendered from `{lesson_assets}` in both documents.

## 4. Connect Each Image to the Body

Every image must serve at least one explicit purpose: section overview, course model, numerical or case evidence, operational process, resource recommendation, or closing judgment.

Place each image near the corresponding semantic passage. If a slide contains an essential framework that the instructor did not read aloud in full, convert the visible text into searchable body text and label it as originating from the course slide. Do not present it as verbatim speech.

## 5. Two-Layer Treatment of Risk Information

For revenue, follower counts, platform algorithms, public figures, documentaries, health, or psychology content:

- Preserve the instructor’s meaning in the faithful transcript and explain boundaries in a separate editorial note;
- In the structured lecture, distinguish “course viewpoint, editorial structural analysis, external fact pending verification, and application recommendation”;
- State that revenue and pricing cases are not income guarantees;
- State that personal recovery experiences are not diagnostic, medication-discontinuation, or treatment advice;
- State that experience-based psychological models do not replace professional assessment.

## 6. Final Inspection

Before changing the course map to “organized,” the main agent must inspect the actual files directly:

1. Both the faithful transcript and lecture exist and contain substantive content;
2. Count total and unique image references in each document;
3. Resolve every relative path; missing paths must total zero;
4. Image-reference counts must match the final asset inventory;
5. Search for destinations for critical lesson numbers, people, products, prices, cases, SOPs, and risk notices;
6. Read the beginning and end of the lecture to confirm complete information layering, applicable boundaries, and transition to the next lesson;
7. Only then update status in the faithful transcript, lecture, and course map.

Recommended acceptance criteria:

```text
Total assets = images after deduplication = unique image references in the faithful transcript = unique image references in the lecture
Missing links = 0
Samples of critical cases and numbers = all found
Course-map status = updated only after verifying the actual files
```

## 7. Common Pitfalls

- Inspecting chat thumbnails only and missing collapsed attachments;
- Numbering mechanically by screenshot time so the opening overview appears last;
- Referencing temporary paths in formal documents;
- Archiving an image without semantic integration in the body;
- Trusting a subagent’s “all embedded” claim without direct main-agent verification;
- Marking the course map “organized” before the deep lecture is complete;
- Altering the instructor’s words to reduce risk instead of separating an editorial note.
