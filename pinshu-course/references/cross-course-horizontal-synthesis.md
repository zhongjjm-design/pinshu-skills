# Cross-Lesson Synthesis: Master Course Outline and Methodology/Model Library

Use this workflow after the accepted per-lesson drafts are complete and the task requires deduplication across lessons and a cross-topic knowledge library that can be studied independently.

## Authoritative-Source Gate

1. Define the one authoritative input layer first, usually the accepted per-lesson systematized lectures.
2. Return to the faithful edited transcripts only when the speaker, a number, sequence, or original meaning needs verification.
3. Do not mix old segmented lectures, asset candidates, historical summaries, or unaccepted intermediate drafts into the synthesis.
4. Frontmatter must declare `authoritative_sources` and `source_policy` so that later work does not misuse old drafts.

## Two Core Deliverables

### Master Course Outline

Include at least:

- the problem the course actually solves and its throughline;
- cognitive progression by day or module;
- a relationship map covering every lesson;
- learning paths for different goals;
- identity, case, and viewpoint-attribution boundaries between the lead instructor and guests;
- relative links to per-lesson lectures, the course map, and the method library;
- a candidate formal master title clearly marked `provisional`;
- the final cross-lesson action framework.

The outline is not a concatenation of thirteen summaries. For each lesson, retain only its function in the full course and its relationship to preceding and following lessons.

### Methodology and Model Library

Deduplicate across lessons before normalizing fields. Every entry includes at least:

1. method name;
2. problem solved;
3. core principle;
4. execution steps;
5. applicability conditions;
6. inapplicable scenarios or risks;
7. source lesson(s);
8. related cases.

When the same method appears in multiple lessons, create one canonical entry and merge later additions into its principle, steps, boundaries, and cases. Do not create duplicate records by lesson.

## Converting Course Methodology into an Executable Skill

If the ultimate purpose of organizing the course is to derive a Skill that guides later content or business work, do not paste the master outline or thirty lectures into `SKILL.md`. Apply these gates:

1. **Complete the course corpus first:** finalize only after all paired lesson drafts and the course map have passed acceptance; until then, record candidate methods only.
2. **Build a cross-lesson method library:** deduplicate by `problem → principle → steps → conditions → risks → cases` and identify recurring core models.
3. **Layer the evidence:** distinguish instructor methods, editorial synthesis, time-sensitive platform experience, case-specific outcomes, and external facts. An unverified threshold must not become a hard rule.
4. **Derive a decision process:** the Skill must diagnose the user's stage and primary constraint before selecting a method; it must not retell the course sequentially from Lesson 1.
5. **Define inputs and outputs:** state what material the user must provide and which diagnoses, topics, content, reviews, or business plans the Skill reliably delivers.
6. **Add stop conditions and failure handling:** define when to request more data, switch methods, avoid execution, or return to user validation.
7. **Audit counterexamples:** specify at least one inapplicable scenario for every core method so that case-specific experience does not harden into a universal rule.
8. **Use class-level naming:** name the repeatable task class, such as “Personal-IP Content Growth and Commercial Conversion,” rather than the course, instructor, or one lesson.
9. **Control `SKILL.md` size:** keep triggers, diagnosis, the main workflow, output standards, and verification in the main file; put course evidence, complete cases, and model entries under `references/`.
10. **Case-test before hardening:** run at least one real business case and record the required changes before treating the method as stable.

The final Skill must answer: What stage is the user in? What is the largest constraint? Which model should be used next? How is it executed? Which metrics establish acceptance? It must not merely prove what the course taught.

## Deduplication Rules

Usually merge when:

- names differ but the same problem is being solved;
- one lesson teaches the principle and a later lesson adds execution, failures, or boundaries;
- one method is applied differently in content, business, and Agent contexts;
- a later lesson adds only cases, limitations, or validation methods to the original model.

Keep separate when:

- inputs, outputs, and completion criteria differ;
- one is a diagnostic method and the other an execution process;
- the two share vocabulary but solve different problems;
- after merging, no coherent applicability conditions and stop criteria can be stated.

## Independent-Learning Standard

Every model must allow someone who has not watched the course to answer:

- When should it be used?
- Why does it work?
- What comes first and what follows?
- Under what conditions does it fail or create risk?
- Which lesson contains the complete argument and case?

A slogan, formula, heading, or lesson index alone is insufficient.

## Speaker and Fact Discipline

- Do not misattribute cases or views among the lead instructor, guests, and learners.
- Classroom experience, platform thresholds, operating figures, and product outcomes do not automatically become externally verified facts.
- Label an editorially derived formula as such; do not present it as the instructor's words or an official model.
- Retain `needs-audio-review` information rather than filling it from common knowledge.
- Analyze the mechanism of gray-area platform tactics without expanding them into instructions for evading governance.

## Navigation Design

- The master outline provides both sequential study and problem-based jump-in paths.
- The method library starts with category navigation, and every entry links back to its per-lesson lecture.
- Use relative paths so the knowledge base remains navigable after relocation.
- Keep exactly one H1 in each file; use H2 or lower for every other heading.

## Minimum Verification

1. Target files exist and only the approved scope was written.
2. Frontmatter contains the course, state, document type, authoritative sources, source policy, related documents, and tags.
3. Each file contains exactly one H1.
4. The master outline covers every lesson and includes speaker boundaries, learning paths, and knowledge-base navigation.
5. The number of method-library entries matches frontmatter.
6. Every method contains all eight standard fields.
7. Every relative link resolves to an existing target.
8. Search for old intermediate-draft paths and confirm that the body references none.
9. Sample the beginning, middle, and end to confirm the files are untruncated.
10. The final report lists only real deliverables, verification results, and unresolved issues; it must not report an unexecuted check as passed.
