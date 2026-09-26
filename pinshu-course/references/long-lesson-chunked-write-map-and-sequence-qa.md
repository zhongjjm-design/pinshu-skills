# Chunked Writes, Map Consistency, and Sequence-Conflict Handling for Very Long Lessons

Use this reference when a single transcript is very long, the two document bodies may exceed the capacity of one tool write, or the original recording sequence differs from the formal course outline.

## 1. Do Not Gamble on a Single Write for a Long Document

A successful `write_file` response does not prove that an entire long body reached the file. Long arguments may be truncated at the invocation layer, especially when the interface displays only a summary or the actual byte count written is unexpectedly small.

### Safe Write Procedure

1. Split the document at natural section boundaries into chunks of approximately 6,000–10,000 characters;
2. Write the first chunk with `write_file` and place a unique sentinel at its end: `<!-- CONTINUE_LESSON_XX -->`;
3. Immediately inspect the beginning and end of the file, or count written bytes, to confirm the first chunk was not truncated;
4. For each later chunk, use `patch` to replace the sentinel with “this chunk’s body + the same sentinel”;
5. When replacing the sentinel with the final chunk, do not retain the sentinel;
6. Final acceptance must search for `CONTINUE_LESSON_XX`, `[truncated]`, placeholders, and duplicate H1 headings. The result for each must be zero;
7. Never infer file completeness from arguments shown in truncated form in the tool interface. Read the actual file back.

### Failure Recovery

If the first long write produces only a few lines or frontmatter:

- Rewrite the first chunk immediately; do not continue appending to the incomplete file;
- Restart chunking with a unique sentinel;
- After completion, inspect section continuity to ensure neither the first nor the last chunk is missing;
- Do not fossilize the incomplete write as an “environment failure.” Retain only the general chunking-and-readback method.

## 2. Update Course-Map State Atomically

Completing a lesson requires more than changing one row in the map. One update must reconcile all of the following:

- Frontmatter `current_progress`;
- Frontmatter `next_lesson`;
- “Transcripts received”;
- “Dual drafts generated”;
- “Accepted”;
- Completed range of the current module;
- Module completion ratio, such as `2/7`;
- Total number of organized lessons;
- The lesson’s catalog row: knowledge title, links to both drafts, and status;
- The lesson’s knowledge-navigation entry;
- The next-lesson notice at the end of the file.

After updating, search for the previous lesson number and the old “awaiting input” status to confirm there is no partial update. In particular, a successful patch does not synchronize other counters in the same region automatically.

## 3. Conflict Between Recording Sequence and Formal Outline

A common signal is that the lesson ends with “next we will cover X,” even though the formal outline places X before the current lesson. Recording order, livestream order, publication order, and archive numbering may differ.

Apply this precedence:

1. The official outline controls the filename, H1, `original_title`, map row, and archived next-lesson state;
2. The faithfully edited transcript preserves the instructor’s original transition meaning; do not silently rewrite it to match the current outline order;
3. Add one concise explanation in each of the faithful transcript’s editorial note, the structured lecture’s “Course Sequence Note,” and the map’s risk/boundary area;
4. Do not misclassify a sequence conflict as a wrong-lesson transcript unless the instructor, topic, or main body also conflicts;
5. Build later cross-links according to the formal outline and optionally note the difference from recording order.

## 4. When Verification Is Permission-Gated

If automated scans or SHA commands are blocked pending permission:

- Do not retry the same command;
- Do not switch tools to bypass the gate;
- You may continue with authorized steps that are independent of the blocked check, such as already approved preview synchronization;
- Split status into “content complete / preview synchronized / automated scan incomplete / SHA incomplete”;
- Run blocked verification only after the user explicitly authorizes it;
- If the map says “accepted” but final automated acceptance has not passed, state clearly that closure is incomplete. After authorization, complete verification before ending the lesson session.

## 5. Minimum Final-Acceptance Checklist

- Both drafts and the map exist;
- H1, filename, frontmatter, and official title in the map agree;
- No chunk sentinel, truncation marker, or placeholder remains at the end;
- First-person scan of the faithful transcript has been judged in context;
- The STT scan glossary excludes short terms that would falsely match normal phrases;
- Every map counter is consistent;
- Each formal file and its preview copy have matching SHA values;
- If any automated check was not authorized, do not write “all acceptance checks complete.”
