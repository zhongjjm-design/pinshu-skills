# Lesson-by-Lesson Update Standard for Long Course Series

This reference defines the detailed execution format for `pinshu-course`. It is intended for course series in which dozens of lessons are added to a knowledge base one at a time.

## 1. Frontmatter

### Faithfully Edited Transcript

```yaml
---
date: YYYY-MM-DD
status: organized
course: [course name]
lesson: 6
module: [module]
speaker: [instructor]
original_title: [official title]
knowledge_title: [search-friendly knowledge title]
source: user-provided course transcript
document_type: proofread transcript
tags: [topic 1, topic 2, topic 3]
---
```

The body of a faithful transcript should use natural paragraphs and a small number of semantic headings. Headings may aid navigation, but they must not rearrange the source into a lecture-note structure such as “background—steps—conclusion.” By default, do not convert continuous speech into a bullet-point summary.

### Structured Lecture

```yaml
---
date: YYYY-MM-DD
status: organized
course: [course name]
lesson: 6
module: [module]
speaker: [instructor]
source: faithful transcript for Lesson 06
tags: [topic 1, topic 2, topic 3]
---
```

## 2. Structured Lecture Template

```markdown
# Lesson XX · [Cleaned Official Title]

## Problems This Lesson Solves

1. ...
2. ...

## Core Model

> **[Formula or model]**

## 1. [Knowledge Module]

[Principle, rationale, and applicable scenarios]

## 2. [Case]

### Background
### Target Users and Problems
### Actions Taken
### Result as Described in the Course
### Reusable Elements
### Conditions That Must Not Be Copied Blindly

## 3. [Execution Method]

## Applicable Conditions and Limitations

## Lesson Assignment / Canvas / Diagnostic Worksheet
```

## 3. Course Map Fields

```markdown
| Lesson | Cleaned Official Title | Knowledge Title | Organization Status |
|---|---|---|---|
| 06 | Building an Entry-Level Business Model from 0 to 1: Traffic First | Choosing a Traffic Starting Point Within the Overall Business Model | Organized |
```

The course map should also maintain:

- Course module boundaries;
- The current overall model;
- The range of transcripts received;
- The next expected lesson input;
- Naming and factual-discipline rules.

## 4. Incremental Rules for Cross-Lesson Libraries

### Methodology and Model Library

Add only models that appear for the first time in the course or are materially deepened. Do not copy lesson notes verbatim into this library.

Recommended fields:

- Model name;
- Formula;
- Definition;
- Execution steps;
- Applicable conditions;
- Limitations.

### Case Library

```markdown
## [Sequential Number] [Case Name]

- Background:
- Existing base:
- Users and problems:
- Product and channel:
- Actions taken:
- Course-reported result:
- Reusable elements:
- Conditions that must not be copied:
- Data status: instructor’s direct experience / friend’s case / public case / pending verification.
```

When the same case appears again at a later stage, add subsections such as “Cold-Start Addendum,” “0-to-1 Addendum,” or “1-to-10 Addendum.”

### Tool Library

Prioritize the following:

- Uses of platforms and channels;
- Market-research methods;
- Data-recording fields;
- Selection matrices;
- Compliance and privacy boundaries.

### Template Library

Convert instructions such as “think this through” or “analyze this” into fillable tools, for example:

- Direction-scoring worksheet;
- Cold-start validation worksheet;
- Problem-attribution worksheet;
- Business Model Canvas;
- Public-to-private channel priority matrix.

Number templates sequentially so they can be referenced reliably.

### Fact-Verification Register

```markdown
| Lesson | Claim | Type | Current Status | Required Before Formal Use |
|---|---|---|---|---|
| 06 | A particular case generated more than CNY 500,000 in annual revenue | B | Pending verification | Contracts and revenue records from the case owner |
```

Do not invent sources merely to make the material “look rigorous.” Label the claim first, then perform separate verification only when the user requests it.

## 5. Series Terminology Glossary

Maintain an internal correction dictionary throughout course processing. Typical recognition errors include:

- Mis-segmented or homophonic renderings of “one-person company” → `one-person company`;
- Misrecognized renderings such as “can start” or “cold action” → `cold start`;
- Homophones of the Chinese term for “private domain” → `private domain`;
- “Apartment traffic” or similar homophones → `public-domain traffic`;
- “Conversion endpoint” when the context means the conversion function → `conversion end`;
- Homophone-based misrecognitions of platform or product names.

Do not treat these examples as fixed global replacements. Judge each occurrence in context to avoid corrupting valid text.

## 6. Truncated Input

If the user’s message ends mid-sentence:

1. Do not invent the missing continuation;
2. Organize only the clearly visible portion;
3. Mark the lesson as “additional input required,” not “completed”;
4. Tell the user where the last visible truncation occurs;
5. When the user supplies the remainder, update the same file rather than creating a duplicate version.

## 7. Example: Handling Gray-Area Content

If the course discusses diverting users from comment sections, evading contact-information controls, or black-/gray-market tactics:

### Faithful Transcript

- Preserve the instructor’s original judgments, cases, and operational details;
- Place risk notices in an opening “Editorial Note,” a footnote, or a separate verification register rather than inserting rewrites into the instructor’s body text;
- Do not proactively add more effective evasion techniques.

### Structured Lecture

Add:

- Platform-policy violation risk;
- Account and brand-reputation risk;
- Effects on creator and user rights;
- Weakness of long-term traffic compounding;
- Compliant alternatives.

### Cross-Lesson Knowledge Base

- Record compliance boundaries in the tool library;
- Record claims such as “high effectiveness” in the fact-verification register;
- Do not promote the method into a recommended SOP.

## 8. Lesson Acceptance

1. Read the first 20 lines of the faithful transcript and verify the frontmatter and title;
2. Read the first 20 lines of the structured lecture;
3. Read the corresponding lesson entry in the course map;
4. Check `source_lessons` in all five cross-lesson libraries;
5. Search for high-frequency STT residue specific to the lesson;
6. Check whether cases have been duplicated;
7. Check whether numerical claims have entered the verification register;
8. Report “organized and written” to the user only after all of the above pass.

For final acceptance of a long course, do not run only the basic validator. Use the following for the faithful transcript:

```bash
python3 scripts/validate-course-markdown.py FILE.md --profile long-course-faithful
```

Use the following for the structured lecture:

```bash
python3 scripts/validate-course-markdown.py FILE.md --profile long-course-notes
```

A basic `PASS` proves only that format requirements such as UTF-8 encoding, heading spacing, and required terms are satisfied. It does not prove semantic fidelity, clear emphasis, or complete cases. Content reconciliation and scan-level reading checks are still mandatory.

The current long-course profiles must also reject punctuation at the start of paragraphs, abnormal spaces in Chinese text, sentence fragments ending in commas or semicolons, clusters of mechanically short paragraphs, root-level lists with more than seven ungrouped items, and “Lesson Highlights” sections in lectures containing fewer than three or more than five sentences. These mechanical gates only eliminate obviously defective drafts; they do not replace reading-view acceptance.

Never run a “insert blank lines after punctuation” script directly against a formal file. Any automated reflow must first write to a temporary file. An editor must then merge paragraphs by meaning and inspect the opening, the longest middle section, and the closing dissemination section in reading view.

## 9. Faithful-Transcript Acceptance

Checks for file existence, headings, and typographical errors do not prove fidelity. Perform content-level comparison as well:

1. Extract three to five consecutive substantive sentences from the beginning, middle, and end of the source input;
2. Locate each sentence in the faithful transcript. A summary sentence that is merely “close in meaning” is not an acceptable substitute;
3. Separately sample the longest case and confirm that its background, process, numbers, emotions, and instructor judgments all remain;
4. Check whether questions, repeated emphasis, and transitions from the source were over-deleted;
5. Check whether the result contains many bullet points even though the source was continuous speech;
6. Compare the raw character volume with the cleaned character volume. If the result is substantially shorter, explain whether every deletion was pure noise;
   - Compare only source body text with faithful body text, excluding frontmatter, lesson highlights, and derived closing content;
   - 60% is an elimination threshold, not a passing score. The body-retention ratio can raise an alarm but cannot prove fidelity;
   - Do not calibrate retention rates against drafts the user has not accepted, and do not unilaterally promote “usable as a reference” into a gold-standard exemplar;
   - Whenever the body is substantially shorter, provide a deletion explanation and paragraph-by-paragraph coverage audit proving that every meaningful semantic unit has a destination. A ratio or basic-script `PASS` does not justify delivery;
7. If the user says the material was “over-condensed,” rework the most recent lesson first as a calibration sample. After the user approves the scale, batch-rework historical lessons;
8. Before batch rework, recover each lesson’s original source. Never reconstruct it from an old summary.

Use `document_type: proofread transcript` for the faithful transcript and clearly label the structured output as a lecture, so future maintainers do not confuse the two document types.
