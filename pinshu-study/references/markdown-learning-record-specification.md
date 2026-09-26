# Markdown Learning Record Specification

Preserve three layers: standard course cards and training questions; the learner's personal answers and error diagnoses; and regenerable web interfaces that read from Markdown.

Use the manifest-rendered keys `active_recall`, `training_bank`, `learning_progress`, `learning_sessions`, `error_review`, and `learning_asset_index`. If no manifest or state exists, use the existing confirmed project path map. For a new course, create and confirm one before writing. The neutral personal-record role is `learning_sessions`; never create a directory named for a particular learner or agent by default.

In the body of a training-question file, preserve the question, reference answer, follow-up rules, and sources in the resolved output language; at runtime, display only the question. In a personal record, preserve the date, scope, training method, the learner's first answer, the agent's follow-up questions, supplemental answers, mastered material, omissions and error causes, source-review location, fresh-answer result, and next training session.

Put stable IDs, source types, statuses, and timestamps in frontmatter or hidden comments. Reading does not equal mastery. One personal error must not alter the standard course answer. Personal mastery status must not enter shared lesson notes. A web interface must never silently overwrite original answers in Markdown.
