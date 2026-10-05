# Cross-Lesson Clues, Independent QA, and Formal Promotion

## 1. Ownership of Cross-Lesson Clues

For enabled learning, `pinshu-study` produces and uses per-lesson cards. At module close, `pinshu-course` owns cross-lesson aggregation, deduplication, evidence review, and module cards. A lesson-level Agent may mark a knowledge clue “verified across lessons” only after actually reading and citing a second authoritative lesson, not merely anticipating one.

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

The validator accepts documented English and Chinese headings/fields; for a learner-visible clue, use one consistent label set matching the course language. The four evidence-state meanings do not change with translation. A second source is mandatory for a verified claim.

“Expected to recur,” “probably useful,” and “another lesson should have covered it” remain current-lesson candidates and cannot be promoted. Do not register an ordinary noun, single herb, or isolated case detail without substantial confusion, disagreement, safety value, or cross-lesson increment.

## 3. Source Paths

Every structured lecture must have a resolvable `source_transcript`. Every card has `source_lecture` and `source_transcript` file-level pointers, plus a separate per-item JSON index. Mnemonics, numbers, safety claims, instructor opinions, and cases must also be checked against the faithful transcript at the item level. A path is a plain absolute path or valid relative path from its owning file; do not embed explanatory prose in it.

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

## 5. Nine-Question Pilot Report (for an actual pilot, not every lesson)

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

## 6. Risk-triggered or sampled independent QA

Only when a high-risk trigger or adaptive sample calls for independent QA, the independent reviewer must complete the applicable checks:

1. Programmatic counts of files, headings, cards, clues, and paths;
2. Reverse checks from the faithful transcript for the opening, main line, ending, safety content, and high-risk anchors;
3. For clinical cases, verification of person attribution, inputs, reasoning, intervention, and feedback;
4. For hands-on lessons, verification of visual dependencies and unsupervised-operation boundaries;
5. Per-card sampling for atomicity, high-risk answers, and source retrieval;
6. Per-clue verification of evidence state and second source;
7. Reconciliation of every strong claim in any generator report against actual files.

If generator and independent QA conclusions conflict, decide from the authoritative source and reproducible evidence. After independent QA fails, keep state as `rework`; complete files or a script `PASS` do not justify promotion.

## 7. Formal Promotion and Scale-Up

Ordinary clean lessons: paired generation → mechanical check → writer semantic self-review → unique committer's promotion. Triggered or sampled lessons add independent QA → targeted rework if needed → in-place re-verification before acceptance.

Run cross-lesson card deduplication and horizontal consolidation at module close when enabled. Before scaling, inspect representative lesson layout, faithful edit, notes, and map; clinical/case, high-visual/hands-on, critical-number and consequential lessons require independent QA. A real learning loop validates learning experience when enabled, not the four-result production foundation.
