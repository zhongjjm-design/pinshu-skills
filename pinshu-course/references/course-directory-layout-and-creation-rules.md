# Course Directory Layout and Creation Rules

Runtime paths have one authority. Never derive them by translating a public English label.

## Existing course

1. If course-capture state or a manifest exists, run `course_pipeline.py paths` for the current lesson and use the returned targets.
2. Otherwise inspect the existing course map, directories, peer files, links, and numbering, then record an explicit path map before writing.
3. Existing structure wins. Do not create a synonym, renumber a directory, or pre-create an empty directory.

## New course

Before the first write, create and confirm either the course-capture manifest or an explicit path map with the required semantic keys. The values may use any language and numbering scheme accepted by the user or source library.

| Semantic key | Purpose | Shape |
|---|---|---|
| `course_map` | One course-level map | file |
| `source` | Immutable source transcript for one lesson | lesson file |
| `official_faithful` | Accepted faithful edit | lesson file |
| `official_lecture` | Accepted structured lecture | lesson file |
| `active_recall` | Per-lesson card candidates | lesson file |
| `training_bank` | Course or module practice questions | file or directory |
| `learning_progress` | Learner progress summary | file |
| `learning_sessions` | Personal training-session records | directory |
| `error_review` | Errors and retests | file |
| `learning_asset_index` | Machine-facing asset index | file or directory |

Add further keys, such as lesson assets or module-closeout outputs, only when that course uses them. Keep raw intake separate from formal knowledge ownership. File formal knowledge under the expert whenever possible.

Use placeholders instead of a competing tree when documenting the layout:

```text
{course_root}/
├── {course_map}
├── {source}
├── {official_faithful}
├── {official_lecture}
├── {active_recall}
├── {training_bank}
├── {learning_progress}
├── {learning_sessions}
├── {error_review}
└── {learning_asset_index}
```

A placeholder is not a literal filename. It must be resolved from the manifest/state or the confirmed explicit path map before writing.
