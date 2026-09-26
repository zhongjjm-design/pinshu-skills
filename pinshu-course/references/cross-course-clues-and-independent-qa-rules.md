# Cross-Lesson Clues, Independent QA, and Formal Promotion

## 1. Ownership of Cross-Lesson Clues

`pinshu-study` produces and uses per-lesson cards. At module close, `pinshu-course` owns cross-lesson aggregation, deduplication, evidence review, and promotion into formal cards. A lesson-level Agent submits candidates only; it must not declare them “verified across lessons.”

## 2. Knowledge Clues Pending Consolidation

Every clue must contain at least:

- Knowledge object;
- New contribution from the current lesson;
- Cross-lesson rationale;
- Later trigger;
- Evidence state;
- Current-lesson source;
- Second source, required only for `verified across lessons`;
- Disagreement or change, when present.

Use only four canonical evidence-state values in program fields and the public English examples:

1. `current-lesson candidate`: appears in the current lesson and has cross-lesson potential, but no second source;
2. `later-lesson foreshadowing`: the instructor explicitly says a later lesson will continue it;
3. `verified across lessons`: an authoritative source from a second lesson has been read, with a resolvable source and differences recorded;
4. `safety-governance candidate`: not yet repeated across lessons, but misuse has a high cost and warrants one shared safety node.

The validator also accepts the established legacy Chinese labels and state values and normalizes them to these four internal values. A clue must use one complete documented label set; do not mix languages inside a state or combine English and legacy Chinese field labels in one clue. Learner-facing explanatory prose follows `output_language`, while these enum values remain stable program fields.

“Expected to recur,” “probably useful,” and “another lesson should have covered it” remain current-lesson candidates and cannot be promoted. Do not register an ordinary noun, single herb, or isolated case detail without substantial confusion, disagreement, safety value, or cross-lesson increment.

## 3. Source Paths

Every structured lecture must have a resolvable `source_transcript`. Every card must have a `source_lecture`; mnemonics, numbers, safety claims, instructor opinions, and individual cases must also have a `source_transcript`. A path is either a plain absolute path or a valid relative path from the current file. Do not mix explanatory prose such as “located at,” “same directory,” or “see” into the field.

Before formal promotion, resolve each path and confirm that its target exists. Writing “return to source” does not make a source retrievable.

## 4. Generator Self-Assessment

A generator’s nine-question report provides rework clues, not acceptance evidence. Use strong claims only after reverse verification, including:

- All, every, complete, no omissions;
- No compound cards;
- Source identity is entirely clear;
- Independently learnable;
- Every clue has cross-lesson evidence;
- File, line, heading, and card counts are all correct.

When exhaustive proof is unavailable, write “no issue found in the sampled scope” and identify that scope. Generate counts programmatically from actual files rather than entering them manually.

## 5. Nine-Question Pilot Report

Every pilot must answer at least:

1. What are the absolute paths of the actual input and every output?
2. How were lesson type, primary structure, and embedded submodules selected? Were any stages invented to fill a template?
3. How did independent semantic units from the faithful transcript enter the body, a downgraded region, or an explicit exclusion region?
4. How are instructor wording, editorial synthesis, cross-lesson additions, and pending confirmation layered at the relevant location?
5. How are medical, safety, and visual dependencies handled? Which portions cannot be operated independently?
6. What are the actual totals for all cards, atomic cards, synthesis cards, core cards, and on-demand cards? Do counts reconcile?
7. How many pending clues occupy each evidence state? Does every `verified across lessons` clue have a second source?
8. What did mechanical checks find, and what known issues remain?
9. What is the generator’s judgment, supporting evidence, and limitation?

The report must not present a repair plan as a completed fact.

## 6. Independent QA by the Main Agent

The main agent must complete at least:

1. Programmatic counts of files, headings, cards, clues, and paths;
2. Reverse checks from the faithful transcript for the opening, main line, ending, safety content, and high-risk anchors;
3. For clinical cases, verification of person attribution, inputs, reasoning, intervention, and feedback;
4. For hands-on lessons, verification of visual dependencies and unsupervised-operation boundaries;
5. Per-card sampling for atomicity, high-risk answers, and source retrieval;
6. Per-clue verification of evidence state and second source;
7. Reconciliation of every strong claim in the generator report against actual files.

If generator and independent QA conclusions conflict, decide from the authoritative source and reproducible evidence. After independent QA fails, keep state as `rework`; complete files or a script `PASS` do not justify promotion.

## 7. Formal Promotion and Scale-Up

Per-lesson state: candidate outputs → generator self-check → main-agent independent QA → targeted rework → in-place re-verification → accepted.

Run cross-lesson card deduplication and formal horizontal consolidation only at module close. Scaling an entire course additionally requires a representative mixed-content lesson, one clinical-case or divination-chart lesson, one highly visual or hands-on lesson, one formal cross-lesson consolidation, and one real learning loop.
