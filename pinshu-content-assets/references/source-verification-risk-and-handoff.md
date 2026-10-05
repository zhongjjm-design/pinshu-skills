# Source verification, risk, and handoff

Use this reference when speaker identity, consequential facts, first-person experience, or automated handoff could affect the result. Normal sourcebooks start from a corrected faithful transcript and structured guide. Check raw transcripts for direct quotes and conflicts, not as a fresh source of uncorrected reader-facing text.

## Three kinds of accuracy

**Faithfulness of meaning** applies to ordinary claims, explanations, methods, and cases. Condense, organize, and polish only while preserving subject, conditions, causal direction, strength, and uncertainty. A course opinion is not an independently proven fact.

**Verbatim accuracy** applies only when a line is explicitly attributed as the speaker's exact words. Matching a raw STT line does not establish that it was transcribed correctly. After a well-supported change to a name, word, punctuation mark, capitalization, filler, or repetition, show only the corrected line and label it **edited quotation** with a source note; it is not verbatim. Paraphrase when the correction leaves meaning uncertain. Keep known misrecognitions in the raw transcript, dictionary mapping, or working notes rather than visible quotation text.

**External verification** applies to medicine, law, finance, earnings, regulation, privacy, current platform rules, product versions, consequential numbers, and similar real-world claims. A course can establish only that someone said something; check external evidence before treating such claims as current facts or recommendations.

## People and personal experience

Keep an instructor's first-person experience with that instructor. Use Aidan's first person only when Aidan's own material or explicit confirmation establishes it. Do not invent outcomes, numbers, or details missing from the source. If the speaker cannot reliably be named, use “the instructor” or “a guest”; do not guess. A speaker recounting a client's remarks does not turn those remarks into a verified client quotation.

## How the reader sees sources

Ordinary assets end with concise, natural-language source notes, for example: “Source: lesson 8, discussion of building a company knowledge base; full context in the faithfully edited transcript.” When literal quotes, consequential checks, or automated readback require exact documents, headings, excerpts, and identifiers, keep those details in working records. Do not expose machine fields and review receipts by default.

## Let risk affect the relevant item, not every item

- For ordinary ideas and practices, check faithful meaning.
- Where an item is misleading outside context, add its necessary condition nearby.
- Verify current prices, platform mechanics, generalized outcomes, financial recommendations, returns, and decision-critical numbers before using them as established facts.
- A classroom case number may remain when its exact scale matters to the causal explanation. Identify its speaker, classroom context, and inability to prove a general effect. Lack of external verification alone does not require deleting every such number.
- For medical, legal, financial, earnings, regulatory, privacy, or unidentified high-consequence figures, have a person decide whether to anonymize, generalize, keep in working notes, or exclude.

Deleting a number, anonymizing a person, or softening adjectives does not automatically remove a risky claim. If only a safe derivative remains, rewrite it as an independent, supported knowledge unit rather than laundering the original assertion.

A risk log can exist in private working records when needed. A high-risk item alone does not require JSON. Use a machine registry only if a real reader needs it for bulk automation, structured audit, a legacy migration, or an explicit user request. The reader should not have to wade through a comprehensive risk ledger to use a safe entry; put a brief restriction beside the item only when it changes how it may be used.

## When a second reviewer is necessary

Use a reviewer other than the producer or obtain user confirmation before putting a high-consequence fact into an approved asset, combining distant course passages into a new causal claim, publishing first-person experience, approving automated bulk production, or taking a step whose failure would not be caught by ordinary reading. Ordinary low-risk knowledge still needs real reading and use testing, but not a hash and review receipt for every item. In all cases, the sourcebook remains pending until the user approves formal writing use.

## Downstream route resolution

Only after the sourcebook exists, consider a downstream destination if the user explicitly requests more production. Optional portable roles are:

```yaml
content_draft_destination: /absolute/path/to/drafts
content_final_destination: /absolute/path/to/approved-work
content_workflow_handoff: workflow-name-or-identifier
```

Provide a configuration path **explicitly** with `--config`; this public skill never looks for local private files or invents directories. Precedence is an explicit per-call destination over an explicitly supplied project or user config; without either, the route is `unresolved`. A resolved route is only a proposed handoff, not a written draft, a sent message, or delivery. The route helper reports `created: false`; verify any later external delivery by reading its real target.

## Limits of machine checks

The original internal legacy registry validator was tied to an old multi-file packaging contract and is not included in this public edition. Its mechanical PASS would not establish that a sourcebook captured the valuable material, kept enough explanation, handled omissions, or supported real reuse. Confirm these outcomes by reading the finished document against the sources and using it for a real retrieval question.
