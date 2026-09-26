# Repeated-Playback Transcripts: Deduplication, Increment Preservation, and Terminology Authority

Use this reference for livestream, screen-recording, or repeated-listening transcripts in which the same material reappears later while adding numbers, steps, limitations, Q&A, or screen details.

## 1. Classify the Repetition First

Build an internal matrix for every suspected duplicate group:

| Primary Segment | Repeated Segment | New Information | Treatment |
|---|---|---|---|
| First complete explanation | Later near-restatement | None | Delete the repetition |
| First complete explanation | Later restatement | New number/exception/step | Merge the increment into the primary segment |
| Concept explanation | Later case | New case or failure process | Retain as a case; do not treat as repetition |
| Spoken explanation | Screen demonstration | New interface fields/precise prompt | Merge both sources and label provenance |

Principle: **remove repeated expression, not new evidence embedded inside repeated segments.** Never delete mechanically based on surface similarity.

## 2. Process the Faithful Transcript and Lecture Differently

### Faithfully Edited Transcript

- Use the first most complete and coherent explanation as the backbone;
- Return new information from later duplicate segments to the original topic location;
- Preserve the instructor’s first-person voice; do not write “the instructor mentioned again”;
- In the opening editorial note, state only that “repeated playback was merged as backbone + new information.”

### Structured Lecture

- Do not preserve playback order. Reorganize by problem, principle, case, boundary, and execution steps;
- Define each concept once;
- Expand new cases, failure-recovery mechanisms, and acceptance methods in full;
- Label editorially extracted formulas, templates, and models as “organized from the course.”

## 3. Terminology Authority Order

When repeated playback and STT produce several homophones, use:

1. Formal name explicitly confirmed by the user;
2. Clear course visuals or official documentation;
3. A form used consistently multiple times in the same material;
4. Contextual inference;
5. If still unresolved, add it to one consolidated confirmation list.

Do not invent a separate command, mode, or product because STT omitted one syllable. If the user has confirmed the formal name `Goal`, treat “Go” in the transcript first as a missing-syllable STT error. Distinguish a separate `go` command only if a visual or official source explicitly shows it.

## 4. When Original On-Screen Text Is Missing

A lesson may say that “the full universal prompt is on screen,” while the text-only transcript records only its structure. In that case:

- Organize “the instruction structure confirmed by the narration”;
- State explicitly that it is “not a verbatim transcription of the course screen”;
- Do not put it in quotation marks as if it were on-screen text;
- Add the full on-screen wording to pending confirmation;
- Keep status as draft or pending verification until the visual source is supplied or the user waives verbatim recovery.

## 5. Reconcile Numbers and Cases

After deduplication, verify each of the following:

- Time: runtime and development duration;
- Scale: number of accounts, quantity per account, total quantity;
- Cost: tokens, price, quota;
- Filtering criteria: replies, reposts, time window;
- Boundary validation: for example, whether Top N retains N+1 as sorting evidence;
- Exception recovery: parse failure, rate limits, sharding, batch saves;
- Final acceptance: counts, table structure, links, sampling, and charts.

Every new number or boundary from a repeated segment must have a destination.

## 6. QA Layers and State Gates

Split acceptance into three levels to avoid overclaiming when one script did not run:

1. **Content acceptance:** first-person voice, cases, numbers, steps, and boundaries are complete;
2. **Targeted-search acceptance:** zero residual old STT terms, coverage of new terminology, and zero residual third-party voice;
3. **Automated comprehensive acceptance:** H1, frontmatter, code fences, duplicate long sentences, internal links, and pending-item counts.

Report only the levels actually completed as passed. If automated comprehensive acceptance did not run, report that the first two passed without equating them to full automated acceptance.

## 7. Minimum Delivery Checklist

- [ ] A backbone–increment matrix exists for suspected duplicate blocks;
- [ ] New numbers, steps, and limitations from later repetitions were merged;
- [ ] The faithful transcript preserves the instructor’s first-person voice;
- [ ] User-confirmed terminology overrides homophone STT;
- [ ] Missing on-screen prompts were not fabricated;
- [ ] Both drafts and the course map use the same formal title;
- [ ] Pending items agree across both drafts and the map;
- [ ] Draft/final state matches whether confirmations are cleared;
- [ ] Content acceptance, search acceptance, and automated comprehensive acceptance are distinguished explicitly.
