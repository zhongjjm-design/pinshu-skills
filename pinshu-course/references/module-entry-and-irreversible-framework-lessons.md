# Processing Module-Entry Lessons and Irreversible Sequential Models

## When to Use

Use this reference when a lesson shows several of the following signals:

- It formally opens a new module;
- It reviews the full course or relationships between earlier and later sections;
- It explains the hierarchy of lessons inside the new module;
- It introduces a process that must run in order and in which a later step must not destroy an earlier one;
- It validates the process through many live cases, one segment at a time.

This is neither an ordinary lesson nor a module-closing lesson. It establishes the **module entry point, dependency declarations, and acceptance criteria for later work**.

## 1. Identify the Three-Level Course Architecture First

Both the faithful transcript and lecture must preserve:

1. **Whole-course level:** what the prerequisite modules solved and why practice can begin now;
2. **Current-module level:** which lessons form the foundation, which add detail, and which are specialized extensions;
3. **Current-lesson level:** how this lesson’s process constrains later lessons.

Do not remove the opening discussion of course relationships as idle chatter. If the instructor explicitly says that “learning and practice proceed in parallel” or that particular lessons must be learned first, those are module dependencies, not course-process noise.

## 2. Distinguish Module Entry from Module Closure

After a module-entry lesson:

- Change the current module in the map from “awaiting input” to `1/N`;
- Add navigation for the lesson and identify the next lesson;
- Do not pre-generate the five module-level assets for methodology, cases, checklists, risks, and assignments;
- Register only cross-lesson candidates and wait until the module reaches `N/N` before consolidation.

Run complete module consolidation only after the closing lesson. Do not misclassify a dense opening lesson as module closure.

## 3. Extract the Irreversible Model

If the instructor says that “the order cannot change” or “a later step must not erase an earlier one,” the lecture must represent the method as **stage gates**, not three parallel techniques.

Recommended structure:

```text
Step 0: Freeze the destination / target object
→ Layer 1: Establish prerequisite A
→ Layer 2: Add B without breaking A
→ Layer 3: Add C while preserving A and B
→ Regression test: Did C break B? Did B break A?
```

For every layer, specify at least:

| Field | Requirement |
|---|---|
| Purpose | What problem this layer solves |
| Input | Which prerequisite results it depends on |
| Tools | Methods, signals, or materials available at this layer |
| Failure | Common misuse and inversion of priorities |
| Pass criterion | How to decide whether to enter the next layer |
| Regression question | Whether a later change breaks this layer |

Finish with a diagnostic tree or regression table so “irreversible” becomes operational.

## 4. Preserve the Causal Chain of Classroom Walkthroughs

These lessons often build a model by playing a video, pausing to ask questions, analyzing second by second, and reasoning backward. The faithful transcript must preserve:

- The target-audience definition before a case begins;
- What question the instructor asks at each point;
- Which information causes target users to leave;
- Which later information is the real entry point;
- How the instructor uses the case to prove sequence irreversibility;
- Classroom corrections and feedback when students reverse the order.

You may delete player malfunctions, waiting, and non-informative repetition, but never compress a segment-by-segment walkthrough into one “case insight.”

## 5. Correct Terminology Through Model Relationships

In long transcripts, key layer names may be rendered as homophones by STT. Do not correct from one sentence alone. Check all of the following:

1. The term used when the instructor first enumerates the layers;
2. Later definitions and cases;
3. The sequence recap at the end;
4. The official outline or slides;
5. Co-occurrence patterns for the term across the lesson.

If a term consistently co-occurs with “expanding relevant audiences, shared emotions, and latent needs,” normalize it according to the concept’s meaning rather than preserving an obvious homophone error. If uncertainty remains, mark it in the editorial note rather than inventing a term from common knowledge.

## 6. Recommended Outputs for the Structured Lecture

In addition to the standard lecture structure, prioritize:

1. Course-architecture diagram;
2. Overall irreversible process;
3. Tool table for every layer;
4. Failure modes for every layer;
5. Case matrix: case × stage × evidence × risk;
6. “Who will be rejected / who will remain” test;
7. Iterative revision SOP;
8. Irreversibility regression table;
9. Opening or process diagnostic tree;
10. AI-collaboration prompt template;
11. Progressive training cadence;
12. Interface to the next lesson.

Tables and templates must follow complete explanation; they cannot replace the instructor’s reasoning.

## 7. Separate Facts and Risks by Level

Module-entry lessons often mix platform mechanics, experience-based thresholds, public-account cases, and health examples. Distinguish at least:

- Stable methodology;
- Instructor judgment from experience;
- Thresholds used for teaching emphasis;
- Time-sensitive platform mechanics;
- Public account or view-count data;
- Medical, health, and safety content.

Statements such as “X seconds determine survival” or “more than Y% leave” must not be presented as fixed scientific thresholds without sample evidence. Medical cases may illustrate content structure but must not become individualized diagnostic or treatment advice.

## 8. Recording Time and Archive Time

If the instructor states a date during class:

- Record the spoken class date in `recorded_at`;
- Retain the course archive or catalog date in `date`;
- Keep both fields; do not decide unilaterally which one is the “real course time.”

## 9. Atomic Map Update

When a module-entry lesson is complete, update in the same operation:

- `current_progress`;
- `next_lesson`;
- The three status layers: received, dual drafts generated, accepted;
- Current module `1/N`;
- Total course completion count;
- Official catalog row, knowledge title, dual-draft links, and status;
- The lesson’s knowledge navigation;
- The “next lesson” notice at the end of the map.

Then search for and clear:

- “Awaiting this lesson’s input”;
- The old total count;
- “Awaiting input” on the current module;
- “Pending organization” in the lesson catalog row;
- The old next lesson.

## 10. Preview and Final Acceptance

1. Run content scans after completing the faithful transcript and lecture;
2. Update the map to the true source-side state;
3. Synchronize previews into two separate subdirectories; never flatten same-named files and overwrite one;
4. Use text equality, line counts, and byte counts for non-SHA acceptance;
5. Scan the map again for stale state;
6. Third-party editorial voice must be zero in the faithful transcript. The lecture may use third-person course analysis; do not apply the same red-line judgment to both document types;
7. Continuation anchors, `[truncated]`, “to be continued,” and “additional input required” must be zero unless the source genuinely has a documented gap;
8. The map may state “non-restricted acceptance passed” only after previews actually exist and reconciliation passes.

## 11. Minimum Fields in the Completion Report

- Formal lesson title;
- Recording date and archive date;
- Paths, line counts, and key new tools for both drafts;
- Current overall progress and module ratio;
- Next lesson;
- Whether the source is truncated;
- Whether platform, public-case, and medical risks were separated;
- Preview path;
- Text-consistency result;
- Whether SHA was executed.
