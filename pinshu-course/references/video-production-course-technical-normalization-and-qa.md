# Technical Normalization and QA for Video Production Courses

Use this reference when a transcript simultaneously covers smartphone filming, exposure, HDR, white balance, A-roll/B-roll, shot breakdowns, shot sizes, focal lengths, depth of field, layers, and numerous visual examples.

## 1. Roles of the Two Drafts

### Faithfully Edited Transcript

- Preserve the instructor's first-person voice and original speaking order;
- Retain equipment recommendations, demonstration cases, rhetorical questions, numerical thresholds, and experience-based judgments;
- Normalize high-confidence STT near-homophones directly, but do not recast the instructor's experience as an industry-wide conclusion;
- Put strict technical qualifications in editorial notes so they do not interrupt the main narrative.

### Systemized Lecture

Reorganize the material into the following sequence:

```text
Minimum standard for an acceptable shot
→ equipment and image troubleshooting
→ visual and auditory asset matrix
→ action-based shot breakdown
→ shot size and attention
→ spatial depth
→ layers and editing
→ exercises, SOPs, and risk boundaries
```

For every method, explain the problem it solves, why it works, an example, operating steps, applicable conditions, and risks of misuse.

## 2. Normalize High-Frequency Terminology

Use context to normalize common near-homophones in transcripts:

- `A ròu`, `A row`, `error`, and similar forms → `A-roll`;
- `B ròu`, `B row`, `bro`, `bureau`, and similar forms → `B-roll`;
- `Kùlǐ xiāofù`, `Kùlǐ xiāofū`, and similar forms → `Kuleshov effect`;
- `chún kǒubō`, `chún kǒu bō`, and similar forms → `pure talking-head delivery`;
- `veri log` and similar forms → `vlog`;
- Suspected near-homophones such as `tèxiě zhòng zhì`, `zhōngjǐng zhòngshì`, and `quánjǐng zhòngshì` → use context to verify the intended principle: “close-ups emphasize emotion, medium shots emphasize events, and wide shots emphasize momentum.” Never apply a mechanical glossary replacement without checking context;
- `utility diminishing at the margin` → use semantics to verify and normalize as `diminishing marginal utility`.

Every scan hit must be reviewed in context. Short terms can produce false positives in ordinary phrases. For example, `jǐng zhōng` may occur inside `chǎngjǐng zhōng de` (“within the scene”). Narrow the final scan to genuine errors so false positives are not reported as residue.

## 3. Separate the Instructor's Simplifications from Strict Technical Concepts

Do not silently revise the instructor's position in the faithful transcript. Apply the following distinctions in editorial notes and the systemized lecture:

1. **Exposure compensation is not fully manual exposure:** swiping up or down on a phone usually applies compensation to an existing automatic-exposure decision; shutter speed, ISO, frame rate, computational processing, and encoding also affect the result.
2. **Automatic white balance does not mechanically turn colors back to white:** it estimates a neutral point within the scene; mixed lighting, color rendering, and color casts can still affect the result.
3. **HDR does not necessarily produce a sharper image:** it extends highlight and shadow detail, but can introduce tone-mapping artifacts, motion artifacts, and platform-compatibility problems.
4. **Image noise is not lens grease or aggressive beauty processing:** noise is commonly associated with low light and gain, while the latter problems are optical contamination or algorithmic processing.
5. **Photographic depth of field is not foreground-midground-background depth composition:** the former is the range of acceptable sharpness in front of and behind the focal plane; the latter concerns spatial layering and narrative relationships.
6. **Frame size, camera distance, and focal length are three separate variables:** perspective is determined primarily by camera position; focal length determines angle of view. Moving the camera to preserve the same framing changes spatial compression and facial perspective.
7. **A-roll and B-roll are not an absolute on-camera/off-camera binary:** the course may use “main narrative” and “supplementary footage” as a beginner-friendly definition, but the lecture must note that industry usage is broader.

## 4. Boundary Between Content and Form

When a course emphasizes that “production should not hold the content back,” preserve its resource-allocation logic in the lecture:

- First define the minimum usable image quality;
- Once production meets that threshold, inspect topic selection, copy, structure, hooks, and information density;
- Invest further in motion, optics, color, and stylization only after the content has been validated and production has demonstrably become the limiting factor;
- Treat instructor-provided figures such as 60 points, 75 points, and 80/20 as experiential benchmarks, not industry-standard assessments.

## 5. Asset and Copyright Governance

When the material includes online images, film clips, music, program footage, PPT slides, voices, or likenesses:

- Retain the original examples in the faithful transcript, but do not imply that the assets are free to use;
- Add source, license, likeness, voice, trademark, and platform-rule considerations to the lecture;
- Kuleshov-style juxtaposition can create implied causality and attitude. Do not use misleading edits to distort the intended meaning of interviews, public events, or commercial testimonials;
- Product-promotion footage must not use filters, lighting, cropping, or editing to misrepresent a product's color, size, performance, or usage results.

## 6. Per-Lesson Acceptance

1. Keep the title, filename, H1, `original_title`, and course-map link consistent;
2. Scan the faithful transcript for third-party editorial phrasing such as “the course plays,” “the course mentions,” “the course uses,” and “the instructor believes.” In the body, restore first-person forms such as “I play in the lesson,” “I mention,” and “I use”;
3. Scan for near-homophone terminology and placeholders. Review every hit in context, exclude false positives, and only then declare zero residue;
4. Verify that the lecture distinguishes the technical boundaries among exposure, white balance, HDR, depth of field, focal length, camera position, and related concepts;
5. Distinguish course-map states for material received, paired drafts generated, and acceptance passed;
6. Calculate SHA-256 separately for the formal draft and preview draft, then compare each pair. Declare them the same version only when the hashes match or a byte-for-byte comparison succeeds;
7. Verify that every course-map target file actually exists. Do not treat the appearance of link text as proof that the target resolves;
8. If a compound terminal script is blocked by a permission-confirmation gate, do not falsely report that it passed. After receiving permission, use smaller, single-purpose, read-only commands to verify hashes and file existence if needed. Do not convert a temporary permission block into a permanent claim that the tool is unavailable.

## 7. Minimum Completion Report

Report only:

- Absolute paths to both drafts and the course map;
- Line count or file count;
- First-person and STT scan results;
- Whether all technical boundaries were added;
- SHA values for the formal and preview copies;
- Status of the next lesson.

Do not restate the entire workflow.
