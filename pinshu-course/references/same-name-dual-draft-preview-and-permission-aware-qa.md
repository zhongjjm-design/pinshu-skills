# Same-Name Dual-Draft Previews and Permission-Aware Acceptance

Use this reference when a course knowledge base gives `official_faithful` and `official_lecture` the same filename but stores them at different manifest/path-map targets.

## 1. Preview Synchronization Must Preserve Relative Directories

Incorrect:

```text
{preview_root}/
└── {filename}
```

If the faithful transcript and lecture share a filename, flattening them into one directory causes the later copy to overwrite the earlier one silently. A successful copy command does not prove both drafts exist.

Correct:

```text
{preview_root}/
├── {course_map}
├── {official_faithful_relative_target}
└── {official_lecture_relative_target}
```

### Synchronization Steps

1. Read the previous accepted lesson’s preview directory and reuse its structure;
2. Create the relative parent directories rendered for `official_faithful` and `official_lecture`;
3. Copy each draft into its corresponding subdirectory;
4. Place the course map at the preview root for the lesson;
5. Enumerate actual preview files and confirm there are exactly three: map, faithful transcript, and lecture;
6. If an obsolete flattened copy exists, move it to the system Trash rather than permanently deleting it;
7. After repair, read the frontmatter of both preview files; do not trust the copy command alone.

## 2. Minimum Source-to-Preview Reconciliation

Reconcile at least:

- Relative directory;
- Filename;
- `content_type`;
- `original_title`;
- H1;
- Total line count;
- File size;
- Placeholders and truncation markers;
- Lesson-specific STT residue;
- Third-party editorial voice in the faithful transcript.

Checking only that “a file with the same name exists” is insufficient because the preview may contain only the lecture copy.

## 3. Layer Acceptance State When Permissions Are Restricted

If the system explicitly denies automated scans, scripts, or SHA commands and requires user authorization:

- Do not retry the same restricted command;
- Do not switch tools to bypass the restriction and obtain the same result;
- Continue content checks that are clearly unrestricted and do not constitute a bypass;
- Split state in the map and report rather than writing a broad “all acceptance passed.”

Recommended state:

```text
Content-structure acceptance: passed
Title/frontmatter/H1: passed
Text-residue scan: passed
Source/preview line count and file size: consistent
SHA-256: not executed (permission restricted)
```

“Not executed” means neither “failed” nor “passed.”

## 4. Map Update Timing: Two-Stage Commit, No Optimistic Marking

Treat “content generated” and “preview synchronized and accepted” as separate commit stages.

### Stage A: Source Side Complete

After both drafts and knowledge navigation are written, the map may say no more than:

```text
Dual drafts: generated
Preview: pending synchronization
Non-restricted acceptance: pending
SHA-256: not executed / awaiting authorization
```

At this point, received lessons, lessons with dual drafts, knowledge navigation, and next lesson may be updated. **Do not write “acceptance passed,” “source and preview match,” or include the lesson in accepted totals prematurely.**

### Stage B: Verify After Synchronization

Change the map to “non-restricted acceptance passed” only after reading all of the following from actual files:

1. Map, faithful transcript, and lecture exist in the preview directory;
2. The two drafts occupy their correct subdirectories and did not overwrite each other;
3. Source and preview line counts, sizes, or another permitted equivalence check agree;
4. Frontmatter, H1, placeholders, STT residue, and first-person scans pass;
5. Restricted items remain explicitly “not executed” and are not swallowed by “non-restricted checks passed.”

Then synchronize the final map into the preview root again and read back its progress line.

### If Synchronization Is Permission-Blocked

- Stop immediately; do not retry, alter the command, or switch tools to bypass the block;
- Preserve or restore map state to “source dual drafts generated; preview pending synchronization; acceptance incomplete”;
- If the map was incorrectly marked “passed,” the first action after renewed authorization is to correct that state before synchronizing;
- Explain clearly to the user that source-side completion is not preview completion and a planned terminal state cannot replace an observed result.

**No optimistic writes: any state dependent on the next tool action may be committed only after that action succeeds and is read back.**

## 5. Separate Continuing Business Authorization from Runtime Tool Authorization

A user’s continuing authorization to “write both drafts and update the map directly for each later lesson” approves the **business scope** of one course series. It does not guarantee runtime approval for terminal copies, directory creation, or batch validation. These permission layers do not substitute for one another:

- Series-level continuing authorization determines whether the current lesson may be processed and written into the agreed formal course directory;
- Runtime tool authorization is determined by the current tool and safety layer for each synchronization, copy, or composite command.

Therefore:

1. After source-side drafts and map updates are complete, keep “preview pending synchronization / acceptance pending”;
2. When initiating preview synchronization, constrain directory creation, separate draft copies, map copy, and non-SHA reconciliation to explicit allowlisted paths for the lesson;
3. If the runtime says it is waiting for authorization and eventually times out, stop immediately. Continuing authorization does not justify retrying or switching tools;
4. Report “source side complete” separately from “preview/acceptance incomplete,” and keep task state in progress;
5. When the user later authorizes resumption, **perform a read-only inventory of the actual preview directory and map state first**. Do not assume that a blocked composite command had no partial side effects, and do not rerun the entire command blindly;
6. Complete only missing actions, reconcile through readback, then commit the terminal map state and synchronize that terminal map into the preview root again.

This separation prevents two opposite errors: mistaking old business authorization for current tool permission, and reporting an entire lesson as failed after a tool timeout even though source-side work is complete.
