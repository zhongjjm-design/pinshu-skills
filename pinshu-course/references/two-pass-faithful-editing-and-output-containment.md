# Two-Pass Acceptance and Output-Scope Control for Faithful Long-Course Editing

Use this reference for course projects with dozens of audio files, long per-lesson drafts, and parallel editing by multiple agents.

## 1. Generation Is Not Acceptance

A subtask writing a file or reporting “semantic reconciliation complete” proves only that an initial draft exists. The controller must not change state directly to “complete.” Recommended states:

```text
Initial draft generated → independent QA → targeted rework → second independent verification → accepted
```

Only after the second verification passes may the controller update the course map, frontmatter, and task state together.

## 2. Compression Ratio Is a Warning, Not a Quality Conclusion

Count non-whitespace characters in the source and edited draft. When length drops substantially, inspect whether every deletion was limited to verbal noise, silence hallucinations, breaks, and device chatter.

A low retention ratio is not by itself failure, but any of the following requires rework:

- A complete case has become only a conclusion;
- Numbers, amounts, relationships, or tool names disappeared;
- A live operation was rewritten as a generic SOP;
- Limiting conditions, failure processes, or counterexamples were deleted;
- High-risk language was sanitized into “compliant” wording;
- A source truncation was completed into a satisfying conclusion.

## 3. Fixed Sampling for Independent QA

For every lesson, verify at least:

1. One continuous semantic passage from the opening;
2. One important middle case or operation;
3. The source’s actual ending;
4. At least five semantic anchors covering people, numbers, tools, cases, and limitations;
5. High-risk or easily abstracted source language.

QA must return source file and line number, corresponding edited location, and the specific omission or semantic change. “It feels over-compressed” is insufficient.

## 4. Rework Against the Authoritative Source Only

A QA report locates problems; it is not a source for restoration. During rework, reread the raw transcript, subtitles, timestamped JSON, or audio. Preserve qualified passages and restore omissions locally so a whole-document rewrite does not introduce fresh errors.

For uncertain commands, names, amounts, or version numbers:

- Preserve the semantic slot;
- Mark `[requires relistening]`;
- Do not replace the specific term with a vague higher-level concept;
- Do not present external common knowledge as original course wording.

## 5. Audit Speaker Identity and Multiple Voices

In-person classes often switch among the lead instructor, guests, and students. In a first-person article, “I” must remain unambiguous:

- For a single guest session, add `speaker` to frontmatter and identify the speaker at the beginning;
- For multi-speaker Q&A, add `speakers` to frontmatter and use headings or labels such as `## Dong Answers: ...` and `## Teacher Li Answers: ...` at each switch;
- Never merge two speakers’ experiences, platform operations, or methods into one “I”;
- If a full name is unclear, write “Teacher Li (full name requires relistening)” rather than deleting the person’s role.

The second QA pass must inspect speaker attribution explicitly, not only terminology and cases.

## 6. Separate Editorial Notes from the Instructor’s Voice

Use an independent blockquote for fact verification, compliance notices, source truncation, and relisten notes:

```markdown
> **Editorial verification:** The critical verb in the source audio cannot be confirmed and requires relistening.
```

Never write an editorial synthesis as the instructor’s first-person ending. If the source closes with “thank you” or “let’s go eat,” do not add a grand concluding paragraph.

## 7. Control Output Scope in Parallel Tasks

Every subtask must receive an absolute-path allowlist and state explicitly:

- Only listed files may be created or modified;
- Additional QA reports, completion markers, asset candidates, and intermediate master drafts are prohibited;
- “Finished writing” must not be upgraded unilaterally to “accepted”;
- Return actual modified paths and file count.

At the end of every batch, the controller immediately inventories:

```text
Planned files ↔ actual files ↔ modification times ↔ status fields
```

If files appear outside the allowlist, register and isolate them for judgment rather than deleting them unilaterally. Wait until authoritative products are verified before following the approved cleanup process.

## 8. Split Long Batches

Do not make one subtask generate many long documents and self-check them. Prefer one or two lessons per task or split by natural module. After a timeout, inspect actual files first; “timed out” does not mean “no output,” and “file exists” does not mean “qualified.”

## 9. Final Green Conditions

- Lesson boundaries match source transitions;
- Every target file exists and has exactly one H1;
- Speaker identity is clear;
- Silence hallucinations and common STT errors scan to zero;
- Editorial notes are separate from the instructor’s body;
- Every issue from the prior QA pass is closed;
- The second independent verification has no blocker;
- Only the controller writes “faithful edit accepted.”
