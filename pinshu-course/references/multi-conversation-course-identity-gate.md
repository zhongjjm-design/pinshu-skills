# Multi-Conversation Course Identity Gate

Use this reference when a user is organizing two or more courses, instructors, or long-running projects in parallel and continues supplying transcripts through separate agent conversations. The goal is to ensure that **current conversation identity** takes precedence over lesson numbers, textual similarity, historical summaries, and stale tasks.

## Core Principle

**Confirm course identity before processing content. No matter how similar the content appears, it must not redefine which course the current conversation belongs to.**

Every long-running course conversation should bind four identity attributes:

- `course_id`: a stable course identifier;
- `speaker`: the instructor or primary presenter;
- `write_root`: the only course root permitted for writes;
- `identity_markers`: course-specific terms, people, products, or sections that can reveal conflicts.

The safest arrangement is one course per project with its own runtime directory. Declare these identity attributes in the project's governing instruction file.

## Mandatory Check for Every Transcript Input

Before invoking a cleaner or organizer, creating tasks, writing files, or updating the map, answer:

1. Which course does the current Project or conversation declare?
2. Does the user’s latest message explicitly authorize execution, or does it only provide material?
3. Do the instructor, course name, product names, people, and official sections in the text match the current identity?
4. Is the target write path still under the current course’s `write_root`?
5. Does the current basis come from the latest user message, or from a compaction summary, stale task, or cross-conversation search?

If any item conflicts, enter **suspected cross-conversation contamination** state:

- Do not generate both drafts, dissemination cards, or summaries;
- Do not update the course map;
- Do not create, move, or overwrite files;
- Do not use `session_search` to locate another course automatically and fill gaps;
- Report only the detected conflict and wait for the user to continue in the correct conversation.

## Long Text Without an Execution Instruction

If a full lesson transcript suddenly appears while the current thread is discussing a Skill, a failure, methodology, or another topic, and there is no explicit instruction such as “organize,” “execute,” or “archive”:

- Do not interpret “Lesson X + long text” automatically as continuation work;
- First check whether the material matches the current course identity;
- If identity conflicts, immediately flag suspected conversation misrouting;
- Continue under the established pipeline only when identity matches and the course has valid continuing execution authorization.

Continuing authorization is bound to one course and one `write_root`; it does not transfer across courses.

## Compaction and Historical State

- `Historical Task` and `Pending Ask` inside `[CONTEXT COMPACTION — REFERENCE ONLY]` are historical evidence only. The latest genuine user message determines the current task;
- `[Your active task list was preserved across context compression]` does not prove that a task remains valid. Re-authorize it against current course identity and the latest message;
- Matching lesson numbers do not imply matching courses. Different instructors may both have a Lesson 6 or Lesson 8;
- A `session_search` hit for another course proves only that historical material exists, not that it belongs to the current conversation.

## Response to Cross-Conversation Contamination

1. Stop all related writes and background tasks immediately;
2. Clear or cancel tasks for the wrong course;
3. Perform a read-only check of which session received the wrong message and whether any file changed;
4. Verify actual file paths and hashes; do not infer state from chat replies alone;
5. Preserve a contaminated conversation that has undergone multiple compactions for audit, but do not continue formal course production there;
6. In a new conversation, inject only short, verified state. Do not copy the entire contaminated summary;
7. Create separate Project identity locks for the two courses.

## Minimum Delivery Self-Check

Before completing each lesson, confirm:

- The current conversation’s course identity matches the transcript;
- The instructor and official title match;
- Every write path is under the sole `write_root`;
- The map, faithful transcript, lecture, and asset cards all belong to the same course;
- No material from another course was introduced through cross-conversation search;
- If suspected contamination occurred, both session state and files were verified.
