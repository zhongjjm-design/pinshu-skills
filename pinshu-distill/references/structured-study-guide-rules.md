# Rules for Structured Study Guides and Formal Cross-Course Topic Syntheses

## Structured guide for one lesson

### Required functions

1. Learning position: what the lesson solves, prerequisites, and what learners should be able to answer afterward.
2. One knowledge map: a taxonomy, relationship map, decision tree, or reasoning path.
3. Core modules organized by knowledge relationships.
4. Distinctive contributions from the instructor or author.
5. Real connections to preceding and subsequent lessons.
6. Sources, verification status, and unresolved items.

These functions are fixed; the number of sections is not. Let the content determine the structure.

### Preferred sequence

```text
Establish the problem
-> State the core judgment
-> Explain why it holds
-> Expand comparisons and branches
-> Ground it in a case
-> State its limits
```

When the instructor explains one concept in several places, consolidate those passages. `pinshu-transcript` remains responsible for preserving the original speaking order.

### Lesson types

- Concept lesson: definition, components, relationships, common confusions, and examples.
- Classification or comparison lesson: taxonomy, representative items, strengths, selection conditions, and counterexamples.
- Analytical reasoning lesson: inputs, observations, conditional branches, exclusions actually discussed in class, and conclusion.
- Case or chart-reading lesson: bind people and evidence first, then organize only the inquiry, reasoning, correction, intervention, outcome, and non-transferable details that actually occurred. State when a stage was absent; do not invent it.
- Practical or visual lesson: separate conceptual review from demonstration indexing. Record the required visual, limits of text, replay location, and safety stop conditions for each action.
- Source-text lesson: authoritative source wording, instructor interpretation, application, and disputes.

A lesson may combine several types. Choose one primary structure from the main learning task and embed the others as submodules instead of stacking several templates.

### Source anchors

Frontmatter must use a parseable `source_transcript` value: either a plain absolute path or a valid relative path from the current file. Never mix explanatory prose into the path field.

Anchor each major module to the corresponding source section. For numbers, safety guidance, mnemonics, cases, and distinctive claims, also retain wording that can be searched in the source. Case fields must identify the person. Cross-lesson additions must cite the actual second source. Avoid assigning paragraph numbers to every legacy draft when routine editing would make them unstable and create unnecessary maintenance.

### Semantic routing

Before drafting, create an internal inventory of distinct semantic units from the authoritative source. Every unit must enter the guide body, a lower-priority section, or an explicit exclusion list. When the guide compresses heavily, audit at least the main line, side cases, numbers, instructor judgments, closing material, and safety content against the source.

Omit only mechanical repetition already removed during transcript editing or content explicitly determined to have no learning value. Heading count, document length, and the writer's self-rating do not prove source coverage.

### High-risk professional content

When a formula, method, or process has both a prototype and classroom adaptations, separate the original composition, classroom reasoning, conditional changes, instructor-specific optimization, and safety guidance. Tables must not turn medical guidance, medication, emergency material, or procedures into real-world recommendations. Follow the professional-course gates selected by `SKILL.md`.

## Formal cross-course topic synthesis

### Inputs

- Accepted guides for a complete module or course.
- Faithful edited transcripts when source review is necessary.
- Pending synthesis leads.
- Domain standards and terminology lists.
- Any existing authoritative entry for the same knowledge object.

### Process

1. Collect material about one knowledge object across lessons.
2. Choose the most complete lesson as the primary source.
3. Merge repetition.
4. Preserve conditions, cases, and limits added in later lessons.
5. Retain provenance for different editions and schools of thought.
6. Link methods, cases, cards, and training entry points.
7. Produce a reader-ready topic entry, not a dump of candidate fields.

### Minimum content

- Definition and scope.
- Judgment or usage sequence.
- Important branches and comparisons.
- Complete cases.
- Common confusions and counterexamples.
- Disagreements and version changes.
- Safety, factual status, and open verification.
- Every source lesson.

### Do not promote weak candidates

When a topic receives only an ordinary mention in one lesson and has no cross-lesson addition, major confusion risk, or safety value, retain only a course index pointer. Do not create a formal topic entry.

## Validated sample lessons

Validated examples show that a structured guide must route every distinct semantic unit without restoring conversational length. Uncertain material must not be converted into a definite explanation from general knowledge. High-risk material may remain as course content only when it is separated from current real-world guidance.

An initial human review scored the sample at roughly 80/100 and explicitly favored better emphasis and organization over fixed length or a contrived perfect score.
