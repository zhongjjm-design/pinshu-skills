# High-Throughput Text-Only Lesson Processing Mode

Use this mode for long course projects where the user already knows the course material and wants to preserve it in a knowledge base quickly, rather than study while listening or wait for screenshots.

## Trigger Signals

Enable this mode when the user says anything equivalent to:

- “Starting with this lesson, do not capture screenshots”;
- “I will send the text directly; organize it lesson by lesson”;
- “I want to preserve, analyze, and apply the material, not listen to the course”;
- An explicit request to increase speed and stop repeated confirmation.

## Mode Switch

After the user explicitly switches to text-only mode, each later lesson requires only:

```text
Lesson XX:
[complete transcript]
```

If the lesson number is clear and the text is complete from opening to close, treat the lesson assets as complete and enter execution state. Do not ask again:

- Whether screenshots exist;
- Whether all images have been sent;
- Whether both drafts are required;
- Whether to retain the existing directory and naming scheme;
- Whether to update the course map.

Once established, these conventions carry forward until the user changes them.

## Fixed Output for Each Lesson

1. Write the manifest/path-map target `official_faithful`.
2. Write the manifest/path-map target `official_lecture`.
3. Update the manifest/path-map target `course_map`.
4. Verify files, titles, state, STT residue, and risk boundaries

Do not create empty image directories for text-only lessons. If frontmatter requires asset status, use `images: none` or the project’s existing equivalent.

## Speed First Without Lowering Quality

### Faithfully Edited Transcript

- Preserve the instructor’s first-person voice and original speaking sequence;
- Delete greetings, verbal noise, and non-informative repetition;
- Correct STT errors;
- Preserve people, cases, scenarios, numbers, products, causality, and judgment strength;
- Do not compress the result into a summary.

### Structured Lecture

- Reorganize the material into a self-contained learning resource;
- Extract models, diagnostic worksheets, execution templates, and relationships to earlier and later lessons;
- Distinguish original course viewpoints, editorial inference, experience-based thresholds, and facts pending verification;
- Preserve gray-area methods only as course context, not optimized prohibited tutorials; provide compliant alternatives.

## Four Additional Gates for Continuous Lesson Processing

### 1. The Official Outline Is the Naming Authority

When the user has already supplied an official syllabus, screenshot outline, or confirmed course map, continue from that authority:

- Filename, H1, `lesson`, `original_title`, map title, and bidirectional links must use the same official title;
- Section prefixes attached to a lesson name in the official entry—such as “Cognitive Preparation:”, “Direction:”, or “Fundamentals:” — are part of the title and must not be omitted merely because the course map already has grouping headings. The entire string following the lesson number is the `original_title`;
- A temporary phrase spoken at the beginning, a historical title, or an approximate STT rendering must not override the official outline;
- When the official outline includes small distinctions such as “and” versus “with,” variant spellings, full-width parentheses, or full-width colons, the filename should follow the official title. Use the knowledge title for search friendliness;
- After each lesson, verify both “the current title matches” and “the next lesson number is correct” to prevent drift during continuous processing.

Title consistency must cover five locations: formal filename, H1, `original_title`, map link, and preview-copy filename. Before correcting old titles in bulk, reread the map and outline. If a parallel task has added lessons, merge the latest state; never use an old snapshot to overwrite “organized” with “awaiting input.” After correction, scan for old filenames, H1 headings without the prefix, and `original_title` values without the prefix. Each expected count is zero.

### 2. Classify Pre-Class Material by Information Value

Long livestream lessons often begin with lateness explanations, waiting, microphone setup, eating, comment interaction, and valid course updates. Do not delete the whole segment mechanically or retain everything:

1. **Delete pure noise:** apologies for being late, waiting for participants, volume adjustment, moving avatars, eating and drinking, and irrelevant comments;
2. **Briefly note valid previews:** previews of later topic lessons, course-version changes, which version to learn first, and course-update direction;
3. **Preserve teaching rules:** changes in the role of AI, class objectives, intended audiences, and logical relationships between lessons.

The faithful transcript should still enter the formal lesson in source order, but each preview should retain its complete meaning only once, without excited repetition or self-justification.

### 3. Final First-Person Check Uses Pattern Scanning Plus Contextual Judgment

Do not search only for “the instructor believes.” In dense business courses, also scan for phrases equivalent to:

- “the course judges,” “the course provides,” “the course emphasizes,” “the course also points out”;
- “the course uses … to explain,” “the course does not …,” “the course’s judgment about the trend”;
- “the author believes,” “this lesson proposes,” “Mr. An believes.”

Read context for every hit:

- Convert instructor body text to “I judge / I provide / I emphasize / I use … to explain”;
- Move editorial additions into a separate blockquote: `> Editorial note: ...`;
- Normal noun phrases such as “short-video course user segmentation” or “my course” are not third-party voice and must not be replaced blindly.

### 4. Formal Files and Delivery Previews Must Be the Same Version

If the project copies formal drafts to a temporary preview or delivery directory, synchronize **after all targeted revisions are complete**. Then verify both drafts, the map, filenames, and content versions. Never copy a preview first and then change only the formal file, leaving the user to download an obsolete version.

## When Narration References a Missing Chart, Book Title, or Unexpanded Acronym

A text-only transcript may say “look at the chart on the right,” “use this price range,” “I recommend this book,” or “use the AIGPACT model,” without including chart values, the exact book title, or the acronym’s English expansion. Do not pause the whole lesson to request screenshots, and do not guess from general knowledge:

1. **Recover only what the narration states explicitly:** organize confirmed model steps, case relationships, and instructor conclusions. Never invent chart values, table fields, titles, or authors that were not spoken;
2. **Mark the smallest gap at the relevant location in the faithful transcript:** for example, “the original lesson references a pricing chart, but the text-only source does not contain the ranges” or “the recommended title is absent from the transcript.” When preserving first-person voice, keep editorial notes separate from the instructor’s body;
3. **Provide an executable alternative in the lecture that does not depend on the missing visual:** if price ranges are missing, use a framework covering value, alternatives, trust, cost, and willingness-to-pay testing. If a chart is missing, extract only relationships that were spoken and do not fabricate precise data;
4. **Retain the original label for an unexpanded acronym:** organize the Chinese-named steps actually explained by the instructor, but state that “the source does not provide the English expansion.” Never invent an expansion and then present it as the course’s original model;
5. **Not asking again does not mean concealing the gap:** state in one sentence in the final report which source information was absent and how it was handled. Mark an item as pending only if the missing information prevents recovery of the core method; do not block the rest of the lesson.

## Two-Layer Treatment of Strong Outcome Promises, Earnings Cases, and Marketing Methods

Product, marketing, and growth courses often include claims such as “profit in 24 hours,” “mastery in seven days,” “10,000 followers in 30 days,” or “0 to one million”; user-income screenshots; limited-time or limited-quantity offers; testimonials; and “no refunds for virtual products.” Apply these rules:

- The **faithfully edited transcript** preserves course cases, numbers, and judgment strength without silent sanitization. Add a nearby independent editorial boundary explaining evidence status, applicable conditions, and why the claim cannot be treated as a universal promise.
- The **structured lecture** must not optimize strong claims into higher-converting copy. Add measurable learning and behavioral outcomes, permission and privacy requirements for cases, selection bias, genuine scarcity, platform rules, consumer rights, and refund compliance.
- Upgrade “packaging increases conversion” into the complete chain: `informed user → fit-based conversion → successful delivery → user action → outcome → authentic reputation`. Evaluate refund rate, complaints, completion, and user outcomes—not only conversion.
- “High sales,” “many positive reviews,” and income screenshots are evidence pending verification. They do not automatically prove product effectiveness and cannot constitute income guarantees.

## Minimum Necessary File-Operation Acceptance

If the environment requires acceptance before writes, provide one concise notice and execute immediately rather than turning approval into a long process:

```text
[File-operation acceptance]
- Create: faithfully edited transcript
- Create: structured lecture
- Modify: course map
- No image directory; the instruction “organize Lesson XX” is explicit approval. Execute directly.
```

When the user has explicitly said “organize Lesson XX,” do not require a second “confirm execution” response.

## High-Throughput Verification Checklist

After each lesson, confirm at minimum:

- Both draft files exist, with matching lesson number and title;
- The faithful transcript is not a third-person course summary;
- The structured lecture is not a pile of lists;
- Course-map status and current progress are updated;
- Lesson-specific frequent STT residue has been searched;
- Text-only lessons contain no meaningless image placeholders;
- The next lesson number is correct.

### Final Scans Must Cover Both Formal Files and Preview Copies

After all revisions are complete and previews synchronized, run each of the following against both the formal and preview directories:

1. **First-person red-line scan:** include patterns equivalent to “the course believes / emphasizes / uses / provides / judges,” “the instructor believes,” “the author believes,” “this lesson proposes,” and “Mr. An believes.” Read context for each hit. Convert instructor body text to first person; keep editorial content in separate blockquotes.
2. **STT-residue scan:** search known misrecognitions for the lesson, `TODO`, `body pending`, and similar placeholders. To obtain a meaningful zero count, do not repeat the incorrect term verbatim in editorial verification notes; write instead, “the original transcript contained a homophone error, now normalized to X.”
3. **Title and link scan:** verify `original_title`, H1, lecture `source`, both map links, and preview filenames.
4. **Map-anchor scan:** verify `current_progress`, `next_lesson`, lesson-catalog status, knowledge navigation, and the next-lesson notice at the end.
5. **Risk-anchor scan:** when the course covers health, copyright, privacy, stereotypes, time-sensitive platform behavior, earnings, or misleading editing, confirm that synchronization did not drop editorial boundaries from either draft.
6. **Same-version check:** compare content or SHA-256 values for each formal draft, the map, and its preview copy.

Keep search expressions compatible. The default content-search engine may not support lookahead or lookbehind, so do not use `(?!...)` or `(?<=...)`. Use simple alternations or separate searches and then exclude legitimate hits by context.

### Read Full State Before Updating the Course Map

The course map is the shared file most vulnerable to parallel overwrite. Even for a targeted patch, read the complete file—or at least confirm total lines and page through every relevant section—before writing. If a tool reports “based only on a paginated snapshot” or “file changed since last read,” reread before modifying it. Afterward, verify all three state layers: received, dual drafts generated, and accepted.

## High Throughput Does Not Mean Parallel Writes to the Formal Library

For speed, subagents may perform read-only analysis, drafting, or QA in parallel, but the formal course tree remains single-writer:

- Subagents write only to exclusive temporary directories and do not modify both drafts, the course map, official titles, or cross-lesson libraries;
- Before promoting drafts, the main agent rereads the latest formal-library state;
- If another task modified a file after the last read, stop applying patches from the stale snapshot;
- Freeze official titles as an authoritative list. No execution unit may add or remove section prefixes independently;
- Keep one writer for the formal library: subagents write only to exclusive temporary directories, and the main agent verifies and promotes serially.

## Separate Status Terms; Never Treat “File Exists” as “Accepted”

The most common high-throughput state error is to announce that an entire module is “complete” merely because both files exist, even though early lessons remain `pending acceptance` in the map. Before every map update and final report, distinguish:

1. **Received:** the authoritative transcript has entered the project;
2. **Dual drafts generated:** the faithful transcript and structured lecture exist;
3. **Accepted:** title, content, STT, map, assets, and risk boundaries passed final inspection, and the map is explicitly marked `organized` or the project’s equivalent passing state.

Determine module completion by scanning every lesson-status row. If any row remains `pending organization`, `pending acceptance`, `blocked`, or otherwise not passed, do not say “the entire module has passed acceptance.” State precisely, for example: “Dual drafts exist for Lessons XX–XX; Lesson YY remains pending acceptance.”

When reporting progress, also reconcile:

- Whether the new lesson completed both drafts and its map update;
- Whether the module contains historical lessons still pending acceptance;
- Whether “next lesson” matches the earliest lesson awaiting input in the map;
- Whether the current-progress section conflates “received,” “generated,” and “accepted.”

## Milestone Cross-Lesson Synthesis

The purpose of high-throughput lesson processing is not to create 30 isolated documents. Every three to five lessons, or at module close, register cross-lesson candidates for:

- Methodology;
- Case patterns;
- Tools and templates;
- Factual risk;
- Decision processes that may become a Skill.

If the user says, “Organize all 30 lessons quickly first, then extract Skills together,” do not create a formal methodology Skill mid-course. At module close, the structured lecture may include a concise “unified module chain / future Skill candidates” section, and the course map may record the module boundary. Create a formal Skill only after full-course deduplication, applicable-condition analysis, counterexamples, and factual and compliance audits. Never turn a stitched course summary directly into a Skill.
