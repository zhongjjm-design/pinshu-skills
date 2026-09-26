# Course Aftertaste Layer: From Course Knowledge to WeChat Moments Content

## Goal

Course organization must do more than make the material searchable later. It must continue answering two questions:

1. Which judgments from this lesson deserve repeated reflection?
2. Which of them connect to the user's current experience, work, and decisions strongly enough to become publishable expression?

This is a derivative layer after the faithful edited transcript and systematized lecture. It must never alter the course body upstream.

## Core Principle: Mine Every Lesson; Do Not Force a Post from Every Lesson

Every lesson should produce candidate publication material, but not every lesson must be forced into a finished WeChat Moments post.

A mandatory “one lesson, one post” rule creates three kinds of waste:

- course homework that merely restates the instructor's view;
- fabricated reflections unsupported by the user's real experience;
- AI copy engineered for quotability but detached from evidence and context.

Use a three-level cadence instead:

```text
mine each lesson → refine every 3–5 lessons or at module closeout → develop a whole-course series
```

## Level 1: Per-Lesson Publication-Material Card (Required for Every Lesson)

Place a lightweight material card at the end of the systematized lecture by default, or append it to the course-level `publication-material-and-wechat-moments-topic-pool.md`. Do not create a large number of small files for each lesson.

### A. Verbatim Quotations (3–8)

- Every quotation must come from the instructor's actual words. Only punctuation, slips of the tongue, and obvious STT errors may be corrected.
- Retain necessary context; do not remove a limiting condition to manufacture a more absolute statement.
- Label the lesson number and corresponding topic.
- If the wording cannot be confirmed as verbatim, do not place it in quotation marks.

### B. Publishable Insights (1–3)

These are reorganized from the course and are not verbatim quotations from the instructor. Each entry contains:

```text
Insight: one complete judgment
Basis: the course case, reasoning, or fact supporting it
Application: relevance to the user's current work, business, or content
Boundary: conditions under which it must not be copied directly
```

Label each one `editorial-distillation` or `course-derived`. Never present it as a quotation from the instructor.

### C. User Connection Points (1–3)

Do not invent first-person experiences for the user. Find real points of entry instead:

- Which matter the user is handling now does this connect to?
- Which past practice or judgment does it correct?
- Which first-hand user case could support, challenge, or extend this insight?
- Which concrete scene would make the best opening for a WeChat Moments post?

If no real connection is available, output questions that would elicit a real scene; do not generate a fabricated final draft.

### D. WeChat Moments Candidate (0–1)

Generate a publishable draft only when all of these conditions hold:

1. The post centers on one core tension.
2. It includes the user's real scene, action, or before/after change.
3. The course insight has become the user's own judgment rather than a lesson summary.
4. It still stands independently after removing references to the instructor, course, and assignment.
5. It invents no experience, misattributes no instructor quotation, and exaggerates no unverified fact.
6. Its language matches the user's established WeChat Moments style.

Otherwise write the exact state: `lesson-mined-no-publishable-draft-ready`.

## Level 2: Curated Module Publication Set (Every 3–5 Lessons or at Module Closeout)

At module closeout, do not concatenate per-lesson candidates mechanically. Instead:

1. Merge duplicate insights.
2. Distinguish different evidence for the same insight from genuinely different insights.
3. Select 5–10 high-value topics.
4. Grade each topic by the availability of the user's real experience:
   - Grade A: a real scene already exists; ready to draft.
   - Grade B: the insight holds, but one user case is still needed.
   - Grade C: appropriate for the knowledge base only, not for public expression.
5. Produce 2–4 WeChat Moments drafts from Grade A for the user to choose among; do not publish them all.

## Level 3: Whole-Course Content Series

After the course ends, use cross-lesson methods and the user's practice to create:

- a WeChat Moments topic map;
- a sequence of publishable insights;
- long-form/article candidates;
- topics suitable for cards, short videos, or live sessions;
- three states: published, awaiting a case, and not for publication.

Do not divide dozens of lessons evenly into dozens of posts. Find recurring themes validated across lessons that also matter to the user's long-term business.

## Storage Target

Do not add many per-lesson files. Resolve the storage target from the manifest or confirmed path map:

```text
{publication_topic_pool}
```

The placeholder is a semantic key, not a literal English filename. If the key is absent, confirm it before writing instead of creating a translated parallel tree.

Append lightweight material cards by lesson and curated sections by module. Record:

- source course and lesson;
- whether the item is verbatim, editorially distilled, or the user's judgment;
- whether a real scene is available;
- state: `needs-experience / ready-to-write / draft / published / not-public`;
- for published material, publication time and D1/D3/D7/D30 review entry points.

## Creating a Final WeChat Moments Draft

For the final draft, chain `social-media:wechat-moments-authentic-rewrite` and follow these rules:

- Begin with a concrete scene, then the action taken, and end with one personal judgment.
- Do not write “My biggest takeaway from today's class was...”
- Do not write a restatement of the instructor's views.
- Avoid polished antithesis and the template “not X, but Y.”
- Do not portray the user as a beginner who has only just encountered the field.
- When no real material exists, ask first; never invent a persona or experience.

## Acceptance Checklist

- [ ] Every lesson includes mined verbatim quotations, publishable insights, and user connection points
- [ ] Verbatim and editorial material have clear identities; no quotation was fabricated
- [ ] No WeChat Moments draft was forced merely to meet a count
- [ ] Module closeout includes cross-lesson deduplication and grading
- [ ] Final drafts contain real scenes and are not lesson summaries
- [ ] Unverified facts, platform rules, health claims, and earnings claims were not presented as settled conclusions
- [ ] Published material enters D1/D3/D7/D30 review
