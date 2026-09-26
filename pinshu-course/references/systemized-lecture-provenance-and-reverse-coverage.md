# Provenance Layers in Systemized Lectures and Reverse-Coverage Checks for Cross-Lesson Libraries

## When to Use

Use this reference for final acceptance across “faithfully edited transcript → systemized lecture → cross-lesson knowledge base,” especially for independent QA after parallel generation by multiple agents.

## 1. A Systemized Lecture Must Separate Provenance Layers

A systemized lecture may reorganize, synthesize, and add teaching aids, but it must not present editorial design as original instruction from the instructor.

### Original Course Instruction

The following may enter the body directly:

- Methods, steps, exercises, and acceptance conditions the instructor states explicitly;
- Commands, prompt intent, cases, numbers, and failure processes actually demonstrated in class;
- Judgments traceable to the faithful master transcript.

### Editorial Reorganization

If the master transcript does not explicitly teach the following, declare at the section heading or opening paragraph:

> The following material was organized editorially from the course. It was not presented by the instructor as an original classroom assignment, fixed sequence, or standard SOP.

This includes:

- New homework, exercise counts, or required consecutive days;
- Naming an exploratory process an “N-step method,” “SOP,” or “acceptance standard”;
- Single-variable controls, stop conditions, or scoring rules added for teaching convenience;
- Tool-selection recommendations absent from the master transcript.

Keep editorial safety recommendations separate from “conclusions confirmable from the course up to the truncation point.” After source audio cuts off, never complete an ethical position on the instructor’s behalf and call it “the lesson conclusion.”

## 2. Audit Identity and Pronouns

- If the master transcript confirms only “Teacher Li,” “guest,” or “student,” do not infer gender.
- Do not use unconfirmed gendered pronouns. Use names, titles, “the speaker,” or gender-neutral syntax.
- In multi-speaker Q&A, identify the respondent at section or paragraph level; never merge two people’s first-person statements into one “I.”
- Attribute numbers, credentials, products, and judgments to the person who actually said them.

## 3. Sample Final Acceptance of the Systemized Lecture

For every lesson, sample the beginning, middle, and end plus five critical anchors. Check that:

1. Core cases, numbers, relationships, tools, and qualifiers remain;
2. The result is not a conclusion-only summary;
3. Items requiring relistening were not completed without evidence;
4. Editorial additions are clearly layered;
5. There is exactly one H1;
6. `source_transcript` is a resolvable path relative to the current file.

Recommended field:

```yaml
source_transcript: ../02_Segmented-Faithful-Transcripts/Lesson-XX·Title.md
```

## 4. Cross-Lesson Knowledge Bases Require Reverse Coverage

“Sequential numbering, correct item totals, and complete fields” prove only mechanical structure. They do not prove complete knowledge coverage.

### Methodology Library

Scan backward from every systemized lecture’s core models and confirm that each has an independent searchable entry. In particular, check:

- Whether an independent model from the course’s main chain is buried inside another entry;
- Whether a method present in an assignment template is missing from the methodology library;
- Whether adjacent models were merged incorrectly, erasing applicable conditions.

### Fact-Verification Register

Scan backward from the systemized lectures, case library, and tool library for:

- Proper nouns and tool relationships;
- Amounts, income, followers, views, conversions, and effects;
- Platform rules and current features;
- Medical, health, copyright, and sensitive-industry claims;
- Account IDs, people’s names, and product names.

Sequential numbering in the register does not prove coverage. When omissions are found, append new numbers and update the record-count statement.

## 5. Mechanical Final Checks

- Every Markdown file has exactly one H1; category headings use H2;
- All relative links and source fields resolve to existing targets;
- Frontmatter field names are consistent;
- Status may change to “accepted” only after independent QA passes;
- A generator’s self-check does not replace independent read-only QA.
