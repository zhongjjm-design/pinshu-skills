# Markdown Learning Assets and Records

Keep three distinct layers: reusable recall cards and question banks, records of actual learner activity, and regenerable web views. Generated questions do not mean someone has studied; reading does not equal mastery. A learner's error never changes the course's standard answer, and personal mastery status does not go into shared notes.

## Placement and timing

Use existing confirmed course directories and numbering; never translate them into a second tree. In a new course agree on a project path map before writing. The example is `03_Review_and_Practice/01_Active_Recall/` and `02_Practice_Bank/` for enabled review materials, `04_Learning_Records/00_Progress.md` and `01_Practice_Sessions/` after real learning, `02_Errors_and_Rechecks.md` only after an actual error, and `99_Production_Control/Learning_Asset_Index/` for JSON indices. Never pre-create empty optional directories. Use generic learner labels, never one named individual by default.

The question bank preserves the question, answer, follow-up cues, and sources in learner-facing prose. During practice expose one question, not its answer. A session record preserves date/scope, original answer, coverage, omissions, follow-up and supplemental answer, cause, source reviewed, fresh answer, retest timing and result. Feynman explanation and simulated exams are training methods within session records, not mandatory new top-level folders.

## Reading text versus machine data

Frontmatter contains a few file-level values: course/lesson/document type, total count, source files, and `metadata_index`. Do not put a per-card `cards:` list or per-question `questions:` list in frontmatter. Do not put `%%`, HTML, IDs, operations, attributes, types or pipeline state in the reading body. Use independent JSON indices; paths below are illustrative and must resolve from the owner file:

```json
{
  "schema_version": 1,
  "asset_type": "active_recall_cards",
  "source_document": "../../03_Review_and_Practice/01_Active_Recall/lesson-03.md",
  "items": [{"card_id": "L03-01", "position": 1, "card_kind": "atomic", "action": "basic-recall", "priority": "core"}]
}
```

The separate question index uses `asset_type: training_questions`, `items`, and `q_id`, not `cards` or `card_id`; it points back to the question-bank Markdown. Keep IDs unique and positions aligned to body order. Values for machine classification may be English; visible prose and citations follow the learner's language. The actual relative paths must be checked for existence and round-trip resolution.

The validator checks structure, compact frontmatter, index type/count/order/IDs, and source paths. A representative file must also be opened in the real target reading interface to inspect properties, headings, collapsible answers, mobile readability, and code leaks. Without that visual check, do not claim visual acceptance.
