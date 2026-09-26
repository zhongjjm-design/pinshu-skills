# Single-Writer and Safe-Commit Protocol for Concurrent Course Work

Use this protocol when a primary Agent, background subagents, batch scripts, or other sessions operate concurrently within the same course tree.

## Core Rule: One Writer Only in the Formal Course Library

Parallelism is allowed for reading, analysis, drafting, and QA, but **two execution units must never modify the same formal course directory concurrently**. In particular, never modify these concurrently:

- the manifest/path-map target `course_map`;
- official titles, filenames, and frontmatter;
- paired drafts for the same lesson;
- cross-topic methodology, case, tool, fact, and assignment libraries;
- synchronized copies of formal drafts and delivery previews.

The primary Agent is the sole committer by default. Each subagent writes only to its own exclusive temporary directory, for example:

```text
{runtime_dir}/drafts/{course_id}/{task_id}/
```

A subagent must not rename, overwrite, clean up, or update the map in the formal library.

## Before Starting Concurrent Tasks

1. **Freeze the authoritative naming manifest:** read `lesson → official title → target filename` from the user-confirmed official directory or course map. Do not let subagents infer section prefixes, parentheses, full-width punctuation, or labels such as “Part 1/2/3.”
2. **Define read/write boundaries:** each task specification must list read-only inputs, the one temporary output location, and formal paths that must not be written.
3. **Prevent overlapping tasks:** one subagent owns one clearly defined deliverable. The primary Agent serially handles the map, formal renames, and cross-lesson state updates.
4. **Record a baseline:** save the formal directory's file manifest. For a high-risk batch, also record modification times or hashes to detect concurrent changes.

## Safe Commit Workflow

```text
read-only inventory of formal library
→ subagent writes to one exclusive temporary directory
→ primary Agent verifies temporary output
→ primary Agent rereads current formal-library state
→ check for external modifications
→ primary Agent merges/promotes serially
→ update course map
→ final full validation of links, titles, duplicate files, and state
```

### Verification After a Subagent Finishes

A subagent's “complete” status is only a self-report. The primary Agent must verify that:

- the temporary file actually exists;
- its content matches the assigned source file;
- nothing was written outside the boundary into the formal directory;
- the title matches the frozen official title;
- no duplicate file or unintended directory was created;
- no existing course state was regressed to `awaiting-input`.

## When a Concurrent Modification Is Detected

If a tool reports that a file changed after the last read, stop patching from the stale snapshot immediately:

1. Reread the complete current file.
2. List each side's additions and conflicting fields.
3. Merge against the authoritative title manifest and actual file state.
4. Never overwrite the entire file with the stale version.
5. Never batch-rename while a background writer remains active.
6. After establishing the sole writer, perform one serial repair pass.

## Precedence for Official-Title Conflicts

```text
user-confirmed official directory/screenshot
> confirmed title in the course map
> instructor's self-announced opening title
> old filename or subagent inference
```

Only an authoritative source can determine whether a section prefix belongs to the official title. Do not add a prefix because a directory grouping resembles one, and do not remove one merely for brevity.

## Recovering from Duplicate Files

If one lesson has two title variants or duplicate lectures:

1. Compare the authoritative title, content completeness, provenance, and latest modifications.
2. Select the single formal version.
3. Repair internal links, frontmatter, and the course map first.
4. Then move the non-formal copy out of the formal library or to the Trash.
5. Finally, search for the old title, old H1, old Wikilink, and duplicate lesson number; all counts must be zero.

Do not determine authority merely from longer content or a newer modification time.

## Authorization Boundary for Automated Batch Operations

When a batch script, code runner, or security guard requires additional authorization:

- Do not reinterpret existing business authorization as permission for that tool to run.
- Do not bypass a block by using another tool to create the same batch side effects.
- State the file scope, replacement rule, and rollback method before obtaining explicit authorization.
- After authorization, reread the latest state and execute once.

## Final Acceptance

- The formal course tree has no duplicate files for the same lesson.
- Filenames, H1s, `original_title`, map titles, and Wikilinks match exactly.
- Map states such as `received`, `paired-drafts-complete`, and `accepted` match actual files.
- The next lesson number is correct.
- Temporary drafts were not mistaken for formal drafts.
- Subagents left no out-of-scope modifications.
- The formal draft and delivery preview contain the same version.
