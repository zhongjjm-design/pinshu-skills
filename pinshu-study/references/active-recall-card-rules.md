# Active-Recall Card Rules

Active-recall cards prompt the learner to retrieve knowledge from memory after closing the lesson notes. They are not fragments cut from the notes or shorter summaries.

## Learner-facing and internal content

The learner-facing body shows only a question, a collapsible answer, any necessary explanation, and a source citation in the resolved output language. Put the English ID, cognitive operation, attributes, source path, and status in hidden comments or a separate internal index. Do not occupy the reading interface with body sections such as "Attributes," "Type," or "Status."

Every card file must contain a parseable `source_lecture`. Cards containing mnemonics, numbers, safety guidance, instructor opinions, cases, or unresolved material must also retain `source_transcript`. A path must be either a plain absolute path or a valid relative path resolved from the current file.

## Two card classes; report them separately

### Atomic recall card

Test only one target that can be scored independently. A definition plus a necessary qualifier, a two-item comparison along one axis, or tightly coupled steps on one path may count as one target. A list of multiple medications combined with effects, exceptions, reasons, and safety constraints does not.

### Integrative retelling card

Use this class to retell a complete model, case-reasoning chain, meridian pathway, formula derivation, or comprehensive safety review. It may contain multiple retrieval units, but it must be explicitly labeled `integrative card` and must not be represented in self-evaluation as "one target per card."

Candidate sets may contain both classes. Reports must count atomic cards, integrative cards, core cards, and optional cards separately. Do not use "avoiding excessive fragmentation" to conceal a compound cognitive load.

## Cognitive operations and attributes

Cognitive operations include basic recall, comparison and discrimination, causal derivation, ordered pathway, conditional branching, error or counterexample analysis, and visual identification or simulated chart analysis.

Mnemonics, memory aids, safety, core status, and optional use are attributes, not question types. Do not create an artificial difficulty hierarchy.

## Card selection

Cards are required for core definitions, classifications, decision sequences, compatibility or safety boundaries, easily confused distinctions, and mnemonics the instructor repeatedly emphasized.

Create cards as needed for complete derivations, turning points in cases, representative errors, and cross-module integration.

Do not create cards from equipment noise, social chatter, unverified fragments, mechanical repetition, or unresolved items in the faithful transcript presented as definitive answers.

Do not impose a fixed number of cards per lesson. Extract candidate cards for each lesson first. At the end of a module, `pinshu-course` merges cards about the same knowledge object across lessons. `pinshu-study` produces and uses cards for learning; it does not make cross-lesson consolidation decisions.

## High-risk cards

For medical care, medication, dosage, toxicity, critical illness, acupuncture, and other hands-on content that could cause harm, train only:

- how to distinguish the recorded course statement from real-world standards;
- applicability conditions, stopping conditions, and boundaries that require a qualified professional;
- why a case cannot be generalized directly;
- which authoritative source must be consulted.

Do not turn self-diagnosis, self-performed procedures, specific dosages, household substitutes, or unverified classroom experience into a single canonical answer. Every high-risk card must state within its own answer: "Course record; not externally verified; do not use this card to self-treat, self-medicate, or perform the procedure." Do not rely on one disclaimer at the end of the file.

When strongly visual hands-on material lacks action footage, create cards only for recognition principles, visual dependencies, and safety boundaries. Do not create a procedural card that implies the operation can be completed from text alone.

## Source strength

Every card must trace back to the structured lesson notes. Mnemonics, numbers, safety claims, instructor opinions, and cases must also trace back to the faithfully edited transcript. Do not label an editorial synthesis as the instructor's own words. Cross-lesson additions must cite a second source. Direct quotations must be findable word for word.

Write learner-visible citations naturally in the resolved output language. Preserve actual paths and searchable anchors internally.

## Count metadata

A real card unit exists only when all four elements are present: card title, unique ID, question, and answer. Use this frontmatter consistently:

```yaml
card_count_total: 23
core_card_count: 21
optional_card_count: 2
atomic_card_count: 18
integrative_card_count: 5
```

Write `0` when a category has no cards. The total must equal both core plus optional and atomic plus integrative. Generate counts by parsing the actual file; never enter them manually without verification.

## Learning presentation

Display only one card at a time during an actual review. Show the question first. Reveal the answer, explanation, and source only after the learner responds. An integrative card may use stepwise follow-up questions, but the record must preserve the learner's first complete answer.

## Card QA

Before promotion, check all of the following together:

1. The counts of card titles, unique IDs, questions, and answers match.
2. Every frontmatter count matches the actual cards.
3. Each atomic card contains only one independently scorable target.
4. Every integrative card is explicitly identified and does not masquerade as an atomic card.
5. The learner-facing body contains no internal attributes, English type codes, or pipeline status fields.
6. Source paths resolve, and every high-risk card traces directly to the faithful transcript.
7. No unresolved item has been converted into a definitive answer.
8. High-risk content cannot become real-world advice when a card is viewed outside its original context.

A generator's self-evaluation is only a diagnostic clue. It does not replace independent QA or a real learning test.
