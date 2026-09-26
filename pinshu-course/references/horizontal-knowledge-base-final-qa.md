# Independent Final QA for the Cross-Topic Knowledge Library

Use this read-only final QA after completing the master course outline, methodology library, case library, tool library, execution-template library, and fact-verification table. The goal is not to confirm that files exist, but to verify links, coverage, deduplication, factual boundaries, and executability.

## 1. Acceptance Order

1. **Lock authoritative inputs:** prefer accepted per-lesson systematized lectures. When the speaker, a number, proper noun, or original wording is disputed, return to the faithful edited transcript. Do not mix old segmented assets, candidate drafts, or deprecated intermediate drafts into QA.
2. **Mechanical checks:** for each file, verify parseable frontmatter, exactly one H1, resolving relative paths, valid internal anchors, and agreement between declared and measured entry counts.
3. **Field completeness:** validate required fields for every entry according to library type. Total line count is not evidence of content completeness.
4. **Reverse-coverage scan:** work backward from headings, core chains, assignments, pending audio reviews, and high-risk numbers in every authoritative lecture to the cross-topic library. Downward sampling from the cross-topic library alone is insufficient.
5. **Semantic deduplication and boundary checks:** identify duplicate records for the same method or case and detect distinct mechanisms merged incorrectly.
6. **Independent executability:** a template must define inputs, steps, deliverables, acceptance, risks, and stop conditions. Conceptual explanation alone is insufficient.
7. **Per-file verdict:** give each file an independent `PASS` or `BLOCKED` verdict with line-number evidence. If critical coverage or factual boundaries remain incomplete, do not replace the blocked verdict with “overall quality is good.”

## 2. Minimum Gates for Six File Types

### Master Course Outline

- Lesson count and per-lesson links are complete.
- Dates, instructor, guests, and multi-speaker Q&A boundaries are correct.
- Course throughline, learning paths, and navigation agree.
- Editorial synthesis is not presented as the instructor's official terminology.

### Methodology and Model Library

- Declared entry count equals actual entry count.
- Every entry includes the problem solved, core principle, steps, applicability conditions, inapplicable cases/risks, source lesson, and related cases.
- **Determine critical coverage through reverse scanning:** if a core method from a per-lesson heading or primary chain is buried inside another entry and cannot be independently retrieved, record a coverage gap.
- Formulas distinguish the instructor's original expression, editorial organization, and external laws.

### Case Library

- Every case includes context, critical actions, outcome convention, what it demonstrates, what it does not establish, source, and verification state.
- Merge source references when the same case appears across lessons; do not create duplicate records.
- Do not misclassify similar subject matter with different mechanisms as duplicates.
- Medical, earnings, view, operating, and platform outcomes are downgraded to classroom reports or pending verification.

### Tool and Platform Library

- Distinguish models, chatbots, Agent clients, CLIs, knowledge bases, Skills, MCP, and paid-traffic/trading tools first.
- Record classroom use, limits, time sensitivity/compliance risks, and source for every item.
- “Used in class” does not mean “recommended,” and “available then” does not mean “available now.”
- Distinguish merged entry count from unique product count.

### Assignment and Execution-Template Library

- Every template contains an objective, inputs, steps, deliverables, acceptance criteria, and risks.
- For any undisclosed complete prompt, command, dimension table, review method, or hook system, state `must-reconstruct-from-intent`.
- Every template must be directly fillable or executable rather than a list of principles.

### Fact-Verification Table

- Continuous IDs without gaps or duplicates are only a mechanical gate; they do not prove coverage.
- Distinguish at least: needs audio review; contextually corrected but awaiting audio confirmation; classroom report without external evidence; platform rule requiring time-sensitive re-verification.
- Reverse-scan every lecture for proper nouns, amounts, earnings, views, model numbers, platform rules, medical claims, effects, and commercial terms.
- Any negative claim that “the table contains no such item” requires full-text search or a deterministic script.
- An intentionally empty future-execution ledger is not a hollow file, but it must not be described as already verified.

## 3. Commonly Missed Checks

- A valid Markdown link does not establish that a relative source path in frontmatter resolves; check both.
- Validate in-document navigation anchors separately; confirming the target file exists is insufficient.
- Correct totals do not prove complete coverage: entry counts and fact IDs can still omit a core method or high-risk issue.
- “Source lesson identified” and “traced to a specific paragraph” are different traceability levels. Report lesson-level traceability honestly when that is all that exists.
- Do not rewrite “no obvious conflict found” as “all facts are correct.” Final QA proves only that no conflict was found within the checked boundary.

## 4. Recommended Output Format

```text
Overall: N files passed, M files blocked

Global mechanical checks:
- frontmatter / H1 / links / anchors / entry counts

Per file:
1. Filename: PASS or BLOCKED
   - Passed items
   - Blocking item + authoritative-source line number + target-file line number / evidence of an absent search match

File operations: no files created, modified, or deleted (for read-only QA)
```
