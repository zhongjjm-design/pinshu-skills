# Module-Closure Asset Package and AI Course Normalization

Use this reference to consolidate a completed course module—usually three to five lessons—across lessons. It is especially useful for modules that combine platforms, business, strategy, and foundational AI concepts.

## 1. Do Not Turn Cross-Lesson Outputs into One Giant Summary

At module close, generate five kinds of **course-level assets** by default. Each serves one durable purpose:

1. `{cross_lesson_methodology}`
2. `{case_library}`
3. `{tools_and_checklists}`
4. `{fact_checking}`
5. `{practice_and_assignments}`

These are semantic path-map keys, not literal English directories. Resolve them from the manifest or confirmed path map; if a key is absent, confirm it before writing.

Do not create five files for every lesson, and do not cram all five asset classes into one overview.

## 2. Responsibilities of the Five Asset Classes

### Core Methodology

- Connect the causal chain across lessons rather than summarizing lesson by lesson;
- Extract shared layers, processes, and governing principles;
- Explain what each lesson solves and how the lessons build on one another;
- Preserve applicable conditions so instructor preferences are not presented as universal laws.

### Case Index

- Classify cases by the problem they solve;
- Record source lessons;
- Compare the same case when it appears across lessons rather than creating duplicates;
- Preserve numbers and outcomes as course-reported claims.

### Execution Checklist

- Convert methods into task cards, diagnostic worksheets, and pre-publication checks;
- Give each action an input, objective, and success criterion;
- Do not use the checklist as a substitute for methodology prose.

### Facts and Risks

Use three levels:

1. Stable principles suitable for understanding;
2. Instructor experience requiring business testing;
3. Time-sensitive facts or high-risk claims requiring primary-source verification before use.

### Module Assignment

- Give each assignment a defined deliverable;
- Combine assignments into one foundation that can enter the next module;
- When assignments are editorially derived from the course, label their source explicitly.

## 3. Closing Updates to the Course Map

After a module ends, update all of the following together:

- `current_progress` to state that the lesson range and module are complete;
- `next_lesson` to point to the first lesson of the next module;
- Module-table status to “completed”;
- Per-lesson catalog entries with the knowledge title and links to both drafts;
- A knowledge-navigation entry for the current lesson;
- Relative links to all five asset classes under “Milestone Cross-Lesson Synthesis.”

Links must resolve to files that already exist. Never announce completion before creating the files.

### Acceptance State Must Be Committed Last

Do not mark the course map “accepted / module completed” as soon as drafts or cross-lesson assets are written. Use a two-stage state commit:

1. **Generation stage:** once both drafts and all five asset classes exist, add lesson entries, navigation, and links. The status may say only “dual drafts generated / pending acceptance” or the project’s equivalent;
2. **Acceptance stage:** only after verifying titles, STT residue, first-person voice, fact boundaries, link resolution, file uniqueness, and version identity between formal and preview copies may the final patch mark the lesson and module “organized / accepted / completed” and advance `next_lesson`.

If final SHA checks, link resolution, or permission confirmation remain incomplete:

- Do not report “accepted” externally;
- Do not allow `current_progress` in the map to run ahead of reality;
- Retain “pending acceptance” and identify the exact blocker;
- When permission returns, perform read-only verification first and then commit the final status. Do not regenerate content.

## 4. STT Normalization for AI Courses

Common corrections:

- `dip sick / dp sick / deep sake / Deep Sick` → `DeepSeek`
- Homophonic or number-substituted renderings of the Chinese product name → `Qwen`
- `gbt / g bd` → `ChatGPT`, according to context
- `crock` → `Grok`
- `crowd / clock` → `Claude`, according to context
- Homophonic renderings of Lee Sedol’s Chinese name → `Lee Sedol`
- A near-homophone meaning “deep-forming large model” → `generative large model`
- Misrecognitions such as `Huawei AI` or `Huahao AI` → the course product name `Huahuo AI`
- Normalize references to the Chinese product name “Kouzi” as `Coze`
- Normalize `defy` as `Dify` in a tool context

Do not guess uncertain brands or book titles. Preserve the description and mark it `[confirmation required]`.

## 5. AI Fact Boundaries

The lecture must distinguish:

- Antibiotic-candidate screening, AlphaGo, and large language models as different technical approaches;
- “Probabilistic prediction” as an important simplified explanation of large language models, not a complete definition of all AI;
- Whether AI “truly understands” as a technical and philosophical dispute;
- Unsourced figures or causal claims such as “all internet data has already been consumed,” “only X% of information is in the cloud,” or “a certain IP makes the model smarter” as instructor-reported statements only;
- Model access, platform labels, regional availability, and generated-content rules as time-sensitive;
- The agent economy as a forward-looking judgment, not an inevitable fact.

Preserve the instructor’s intended meaning in the faithful transcript. Put editorial calibration in a separate blockquote or note rather than silently rewriting the instructor’s position.

## 6. Preview Copies and Uniqueness Acceptance

1. Copy the lesson’s two drafts, map, and module assets to the preview directory using an explicit allowlist;
2. Enumerate all Markdown files in the preview directory;
3. If obsolete names, duplicate “systemized/structured lecture” files, or old versions appear, move them to the system Trash;
4. Keep exactly one faithful transcript and one structured lecture per lesson in the formal course directory;
5. Search for STT residue, third-party editorial voice, placeholders, and empty files;
6. Only then change the map status to accepted.

## 7. Minimum Acceptance Checklist

- [ ] Titles and frontmatter in both drafts match the official outline
- [ ] The faithful transcript preserves the instructor’s first-person voice
- [ ] AI terminology has been normalized
- [ ] Technical approaches are not conflated
- [ ] Unsourced numbers are labeled
- [ ] All five module asset classes exist
- [ ] Every map link resolves
- [ ] The preview directory contains no duplicate obsolete files
- [ ] The next lesson points to the first lesson of the next module
