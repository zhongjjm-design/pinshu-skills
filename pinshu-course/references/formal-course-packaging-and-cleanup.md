# Formal Course Packaging, Validation, and Intermediate-Draft Cleanup

Use this workflow when accepted per-lesson drafts must move from a temporary workspace into a formal course library. Cross-topic work and independent QA are included when the purpose or risk triggers them; neither is a universal precondition.

## 1. Define the Content Boundary First

By default, the formal package contains only durable deliverables:

- the manifest/path-map target `course_map`;
- terminology and audio-review table;
- accepted per-lesson faithful edited transcripts;
- accepted per-lesson systematized lectures;
- cross-topic knowledge library, only when produced and accepted for this course.

Preserve and verify the immutable raw transcript as one of the four core results in its designated raw-source area; it need not be duplicated inside the formal edited-draft folder. Do not copy source audio, disposable transcription derivatives, logs, partial batch outputs, completion markers, temporary QA reports, or rework reconciliation files into the edited-draft folder. Filter actual accepted files from the course map, not an invented `lesson-*.md` naming rule; do not copy entire directories indiscriminately.

## 2. Review File Operations Before the Formal Write

List:

1. operation type;
2. file types and counts;
3. source directory and complete target path;
4. whether the target directory exists and whether conflicts exist;
5. formal-package directory structure;
6. complete paths of files or directories proposed for cleanup;
7. validation method;
8. governing rule source.

Interpret “continue” as approval of the current plan only when it immediately follows an explicit operation list and the scope is unambiguous. Prefer an explicit authorization sentence for deletion or a formal write across libraries. If a terminal security confirmation times out or is denied, stop. Do not bypass it with another tool. State what was and was not completed, then wait for new authorization.

## 3. Copy; Do Not Move

First copy the accepted deliverables to the formal directory and retain the temporary-workspace copy until the formal package passes validation. If the target directory already exists, stop by default and determine whether it is an old version or a naming conflict; do not overwrite it.

Preserve the source directory's relative structure, especially relative links from systematized lectures to faithful transcripts and from the cross-topic library to per-lesson lectures. Do not rename directories merely to make them look neater and thereby break links.

## 4. Four Required Formal-Package Checks

After copying, actually execute:

1. **Count:** formal-package file count matches the plan.
2. **SHA-256:** every source file and target file have identical hashes.
3. **Heading structure:** every Markdown file contains exactly one H1.
4. **Relative links:** resolve every relative Markdown link; broken-link count is zero.

Also confirm that source audio, transcription derivatives, logs, and temporary QA artifacts did not enter the formal package. If any check fails, cleanup must not begin.

## 5. Clean Up Only After Validation

- Deletion requires separate authorization.
- On macOS, always use `/usr/bin/trash`, never `rm`.
- Prefer moving a clearly obsolete directory to the Trash as a unit. List scattered duplicate files by complete path.
- After cleanup, verify that each cleanup target is absent, the formal package remains complete, and the accepted deliverables remain in the temporary workspace.

## 6. Final Delivery Report

Report the actual execution result:

- formal title and absolute path;
- formal file count;
- SHA-256 mismatch count;
- H1 anomaly count;
- broken relative-link count;
- count of cleaned intermediate files;
- retained source material and unresolved audio-review boundaries.

Do not describe a fact-verification table that requires ongoing updates as incomplete content. Structure and source governance can pass acceptance while external facts remain explicitly under continued verification.
