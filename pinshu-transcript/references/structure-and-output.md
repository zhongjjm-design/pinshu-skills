# Structure and Output

## Step 5: Structural Editing

### First Create a Searchable Title

Read all material before naming the file. The title must let a future reader determine what the file covers and why it is worth retrieving without opening it.

- Use the same semantic core in the filename and H1. Prefer `speaker/course + 2-4 high-value topics`.
- For a long multi-topic lesson, use `Speaker - Topic One, Topic Two, and Topic Three.md`.
- For a single-topic lesson, use `Speaker - Central Judgment or Method.md`.
- Put the date, lesson number, source, and labels such as “raw recording transcript” in frontmatter, source notes, directory hierarchy, or the end of the filename. They must not replace the substantive topic.
- Give raw transcripts semantic topic names too, with the file type at the end, for example: `Instructor-Huang-Agent-Era-Judgment-and-Content-Production-Raw-Recording-Transcript.txt`.
- Do not use titles such as `2026-07-18-transcript.md`, `batch-one-raw-transcript.txt`, `course-cleaned-draft.md`, or `ongoing-master-draft.md`; they do not support content retrieval.

After creating the title, ask: if a future search uses topic terms such as “agent era,” “Codex workflow,” or “human-AI integrated content production,” will this file appear? If not, revise the title.

- Divide the material by the original speaking logic; never disrupt sequence for neater headings.
- Give each topic a subheading of 7-16 Chinese characters. Prefer action-oriented headings for hands-on sections.
- Ordinary transcript paragraphs should generally be 120-220 Chinese characters. Code, prompts, and tables are exempt from paragraph-length guidance.
- For long courses, a user's explicit complaint about “walls of text,” or use with `pinshu-course/references/readability-first-long-course-markdown.md`, let that reference override the preceding rule: keep body paragraphs under 120 Chinese characters where possible, and allow zero paragraphs over 180 characters.
- Merge material on the same topic and start a new section when the topic changes.
- Keep title conventions consistent across a series: course name, lesson number, and lesson topic follow a fixed order; do not move “Lesson X” arbitrarily to the end.

## Step 6: Output Structure

By default, deliver only the source note and the complete, faithfully edited main text. Add a corresponding checklist when the user explicitly requests a hands-on recap. Add derivative sections such as a reading guide, quotable lines, or social-media copy only when the user explicitly requests them. Send methods, case libraries, and systematic study notes to `pinshu-distill`; never mix them into this draft by default. Follow the user's existing series conventions when provided.

```markdown
# [Speaker / Course]: [Central Judgment, Method, and High-Value Topics]

(Source: course name; instructor / presenter: name)

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

A reading guide, key ideas, quotable lines, social-media copy, and further reflections are not part of the default template. Generate them in separate sections after the main text only when the user explicitly requests them. Continue to use `pinshu-distill` for systematic knowledge distillation.
