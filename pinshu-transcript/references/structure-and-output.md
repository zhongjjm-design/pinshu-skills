# Structure and Output

## Step 5: Structural Editing

### First Create a Searchable Title

Read all material before naming the file. The title must let a future reader determine what the file covers and why it is worth retrieving without opening it.

- In a series, use the necessary lesson number followed by the central question or judgment and the most distinctive case, method, or result. Do not cram the entire table of contents into the title.
- When the directory already identifies the document type, keep labels such as “transcript,” “edited draft,” and “study guide” out of both filename and H1. Course, speaker, date, source, version, and status belong in frontmatter or directories when already clear from context; retain an identifier only when needed outside that directory.
- Each title phrase must add content information. A standalone work may use `Speaker - Central Judgment or Method.md` when the speaker's name is needed for recognition.
- A raw source can retain its own provenance or type label where necessary; do not rename or alter immutable raw material merely to meet a display-title convention.
- Avoid generic placeholders such as `Lesson-4-Edited-Transcript.md` and `2026-07-18-transcript.md`.

Test it twice: with the directory hidden, can a reader identify the lesson and why to open it? In the directory, does the title redundantly repeat information the folder already supplies? Revise until both pass.

- Divide the material by the original speaking logic; never disrupt sequence for neater headings.
- Give each topic a subheading of 7-16 Chinese characters. Prefer action-oriented headings for hands-on sections.
- Ordinary transcript paragraphs should generally be 120-220 Chinese characters. Code, prompts, and tables are exempt from paragraph-length guidance.
- For long courses, a user's explicit complaint about “walls of text,” or use with `pinshu-course/references/readability-first-long-course-markdown.md`, let that reference override the preceding rule: keep body paragraphs under 120 Chinese characters where possible, and allow zero paragraphs over 180 characters.
- Merge material on the same topic and start a new section when the topic changes.
- Keep title conventions consistent across a series: course name, lesson number, and lesson topic follow a fixed order; do not move “Lesson X” arbitrarily to the end.

## Step 6: Output Structure

By default, deliver only the source note and the complete, faithfully edited main text. Add a corresponding checklist when the user explicitly requests a hands-on recap. Add derivative sections such as a reading guide, quotable lines, or social-media copy only when the user explicitly requests them. Send methods, case libraries, and systematic study notes to `pinshu-distill`; never mix them into this draft by default. Follow the user's existing series conventions when provided.

```markdown
---
source: [source reference]
speaker: [instructor / presenter]
---

# [Necessary lesson number]: [Central judgment and distinctive method or case]

---

### 1. [Topic Heading]

[Complete, faithfully edited main text]

### 2. [Topic Heading]

[Main text]

### Hands-On Recap (only when the source contains hands-on work and the user requests it)

#### Original and Follow-Up Instructions
#### Procedure
#### Parameters, Code, and Files
#### Errors and Corrections
```

The sample is for a new course without an established layout. An existing course convention may omit H1 and the visible source note or use the official timetable title; follow the project's existing frontmatter, naming, and heading rules instead of creating a second layout.

A reading guide, key ideas, quotable lines, social-media copy, and further reflections are not part of the default template. Generate them in separate sections after the main text only when the user explicitly requests them. Continue to use `pinshu-distill` for systematic knowledge distillation.
