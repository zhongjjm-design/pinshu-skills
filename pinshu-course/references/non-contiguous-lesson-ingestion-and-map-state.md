# Non-Contiguous Lesson Input and Course-Map State Governance

Use this reference when a long-running course receives a complete later lesson before an earlier one. For example, Lesson 14 is missing while the user explicitly submits the full transcript for Lesson 15.

## 1. Distinguish Skipped-Number Input from Cross-Conversation Contamination

Continue processing only if all of the following are true:

1. The user states the lesson number explicitly;
2. The instructor, course name, official outline, and current `write_root` agree;
3. The text is complete from beginning to end, and the user has not said “I have not finished sending it”;
4. Valid series-level continuing authorization exists for this course;
5. The user has not required earlier gaps to be filled first.

If course identity conflicts, the lesson cannot be mapped to the official outline, or the text clearly belongs to another project, pause under the cross-conversation identity gate. A skipped number is not permission to ignore identity conflict.

## 2. Explicit Lesson Number Overrides Default Sequence but Does Not Erase the Gap

When the user explicitly submits a later lesson, generate both drafts, knowledge navigation, and preview for that lesson, but preserve the earlier gap:

```text
Transcripts received: Lessons 01–13 and 15; Lesson 14 not yet received
Dual drafts generated: Lessons 01–13 and 15
Next lesson: Lesson 14 awaiting input
```

Do not write:

```text
Lessons 01–15 completed
```

unless Lesson 14 actually exists and has been completed.

## 3. Count Set Cardinality, Not the Maximum Lesson Number

Count completion by the lessons actually organized:

```text
{01,02,...,13,15} = 14 lessons organized
```

The maximum lesson number being 15 does not justify “15 lessons organized.”

Apply the same rule to module ratios. If Lessons 10, 11, 12, 13, and 15 are complete in a seven-lesson module, write:

```text
5/7 completed (gap at Lesson 14)
```

## 4. Fields in an Atomic Map Update

When a non-contiguous lesson is completed, update in one operation:

1. Frontmatter `current_progress`;
2. `next_lesson`, which still points to the earliest gap;
3. Lessons with transcripts received;
4. Lessons with dual drafts generated;
5. Lessons accepted;
6. Module ratio;
7. Actual total number of completed lessons;
8. The corresponding official catalog row;
9. The current lesson’s knowledge navigation;
10. Gap description and acceptance boundary.

## 5. Preview and Acceptance Still Use a Two-Stage Commit

A skipped number does not change acceptance rules:

- After source-side dual drafts are generated, mark only “generated; preview pending synchronization”;
- Mark “non-restricted acceptance passed” only after the preview exists and readback reconciliation completes;
- If the user requests no SHA execution, write “SHA not executed at user request,” not “failed” or “passed”;
- After final map state changes, synchronize the map copy again and read it back for consistency.

## 6. Report Template

```markdown
This lesson is complete, but an earlier gap remains in the course:

- Generated: Lessons 01–13 and 15
- Awaiting input: Lesson 14
- Actual completion: 14 lessons, not 15
- Next processing entry point: Lesson 14
```

## 7. Prohibited Actions

- Do not use the maximum lesson number as the completion count;
- Do not fabricate the state of a missing lesson to make the outline look tidy;
- Do not advance `next_lesson` past the earliest gap automatically;
- Do not ignore complete, identity-unambiguous later input merely because default sequencing expects the earlier lesson first;
- Do not misclassify explicit skipped-number input as contamination from another course;
- Do not mark acceptance passed before preview synchronization.
