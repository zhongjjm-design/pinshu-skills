# Write-and-Readback Loop for Approved Course Files

Use this workflow when a course transcript, structured lecture, case study, or similar deliverable has been completed and the user has explicitly approved writing it to the formal course library.

## Core States

Keep these three states distinct:

1. **Content prepared (`content-prepared`)**: the body has been generated but has not been written to the target file.
2. **File written (`file-written`)**: the write tool returned successfully, but the file has not yet been read back and verified.
3. **Persisted and accepted (`persisted-and-accepted`)**: the target file exists, and its title, frontmatter, key sections, and counts have been reconciled through readback.

Only the third state permits telling the user that the file “has been saved to the library” or that the task is complete.

## Execution Rules After Authorization

- If the user has explicitly said “approved,” “save it here,” or “write it directly,” or if a valid series-level ongoing write authorization remains in force, perform the write immediately in the same turn. Do not ask again about the same scope.
- Persist and verify the file before reporting. A plan, an acceptance description, or another repetition of the path is not a substitute for execution.
- Use the exact directory and filename specified by the user. Create a separate file by default; do not overwrite an existing file with the same name. Overwriting requires explicit authorization.
- After context compaction, recover the body from the user's original message, an existing formal draft, or the final draft in the conversation. Do not reconstruct an approximate version from a summary.

## Minimum Write Loop

For every target file:

1. Lock the final body and absolute target path.
2. Check whether the write would overwrite an existing file.
3. Write the complete body and the required frontmatter/tags.
4. Read back the beginning, a critical middle section, and the end.
5. Reconcile the title, instructor name, case/step counts, pending-confirmation markers, and critical numbers.
6. Report the absolute path and the state `persisted-and-accepted`, not merely “prepared.”

## Interruption and Recovery

- If runtime authorization or a tool call is interrupted before the write, the state remains `content-prepared; file-not-written`. Report this truthfully and do not declare completion.
- On recovery, first perform a read-only inventory to determine whether the target file contains partial side effects. Execute only the missing actions to avoid duplicate writes or overwrites.
- If the user is already pressing for action after a delay, respond action-first: acknowledge the issue in one sentence and execute immediately. Do not provide another long plan, repeat the acceptance table, or ask the user to restate the path.

## Acceptance Checklist

- [ ] Path exactly matches the user's specification
- [ ] No existing file was overwritten accidentally
- [ ] File exists and is readable
- [ ] Frontmatter and tags are present
- [ ] Title and instructor name are correct
- [ ] Case, step, and tool counts match the final body
- [ ] Beginning, middle, and end are all present and untruncated
- [ ] The report uses the accurate state among `content-prepared`, `file-written`, and `persisted-and-accepted`
