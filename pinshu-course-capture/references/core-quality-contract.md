# Core Quality Contract

Writing workers, rework workers, QA workers, and the official committer read this contract directly. A production card selects an assurance mode and budget; it never replaces this quality floor.

## Deliverable identities

### Faithful edit

The reader should receive a complete edited article that still sounds as if the lecturer is speaking.

- The source transcript is the highest authority for facts and meaning.
- Preserve the lecturer's first-person voice, narrative order, strength of judgment, and constraints.
- Preserve substantive people, numbers, brands, tools, case processes, causal chains, and counterexamples.
- Remove only verbal noise, mechanical repetition, and superseded false starts.
- You may repair sentence boundaries, add paragraphs, correct confirmed STT errors, and add restrained subheadings.
- Do not summarize away the reasoning process, turn the lecturer into a third-party subject, or add views absent from the source.
- Mark uncertain proper nouns, numbers, and transcriptions; never guess.

### Structured lecture

Organize source knowledge for study and retrieval.

- You may reorder material, merge related knowledge, and use tables or procedures.
- Preserve source arguments, cases, and applicability boundaries.
- Link back to the source transcript and faithful edit.
- Never present editorial interpretation as the lecturer's judgment. Put claims requiring external verification into the fact-review list.

## Semantic-fidelity priority

When requirements conflict, apply this order:

1. Do not fabricate or change the original meaning.
2. Do not omit substantive information.
3. Preserve lecturer identity, voice, and strength of judgment.
4. Improve readability.
5. Standardize formatting.

Layout, length targets, summarization efficiency, or a desire to sound “more professional” must never override the first three priorities.

## One quality baseline, different evidence intensity

Every mode rechecks people, numbers, key cases, methods, constraints, the opening, middle, and ending. No mode may replace substantive meaning with a summary. These modes describe only how quality is demonstrated:

- `fast`: compact anchor evidence; no sentence-level ledger.
- `standard`: standard evidence by section or natural argument unit.
- `strict`: every substantive source block enters `coverage.json` as `retained | merged | noise | uncertain`, with a destination or reason.

`noise` must never hide difficult content, and a coverage map is not proof of acceptance. Budget, mode names, and a desire for exhaustive evidence must not lower completeness, fidelity, or lecture quality.

A domain adapter may add authoritative terminology, source hierarchy, risk triggers, and boundaries. A content adapter may add required content anchors and noise criteria for that lesson type. Neither adapter type may weaken this contract, add default outputs, or duplicate the complete workflow.

## Proxy metrics cannot prove acceptance

The following are warning signals only:

- faithful-edit-to-source character ratio;
- whether a file exceeds a byte threshold;
- heading count;
- em-dash, bold, or filler-word count; and
- file existence.

When a ratio is abnormal, compare source and output block by block. Never add filler to reach a ratio, and never skip semantic QA because a ratio appears normal.

## Editing and layout boundaries

- Do not create a wall of text by merely adding headings to the transcript.
- Do not fragment a complete story into excessive snippets, lists, or formulaic summaries.
- Use bold only for a small number of genuinely navigational terms; do not bold whole sentences or paragraphs repeatedly.
- Avoid excessive em dashes, mechanical parallelism, forced uplifting conclusions, and stock transitions such as “In conclusion.”
- Preserve an appropriate amount of the lecturer's questions, conversational transitions, and characteristic phrasing; do not enforce a percentage.
- Headings serve comprehension, not symmetry or a fixed count.

## STT and facts

- Correct confirmed STT errors in the body and preserve the correction evidence.
- `uncertainties.json` records only corrections or conflicts that affect proper nouns, numbers, facts, sources, or later review. Do not log ordinary sentence breaks, punctuation, or semantic-neutral cleanup item by item.
- Before completion, search the source again for people, accounts, brands, tools, numbers, and dates. When one object has meaningfully different names or values, record source variants, the chosen treatment, and verification needs.
- Similar pronunciation alone is not enough to force a proper-noun correction.
- Business figures, brand information, and operating judgments spoken in the course do not automatically become externally verified facts.
- Label claims needing external review as lecturer statements or unverified; do not silently rewrite them.

## Failure criteria

Semantic review fails if any condition applies:

- A key case, number, person, method, or constraint is missing.
- A judgment absent from the source is presented as the lecturer's view.
- First person becomes a third-party summary.
- Changed narrative order alters meaning or causality.
- Major content is summarized instead of preserving the reasoning process.
- Uncertain material is resolved by guessing.
- The faithful edit remains an unedited wall of text or is overformatted into fragments.
