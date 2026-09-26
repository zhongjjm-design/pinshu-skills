# Taxonomy Governance and Safe Migration for Multi-Event Course Libraries

## When to Use

Use this reference when a course or institution directory has been flat for a long time and now mixes in-person classes, summits or festivals, special livestreams, private advisory-board Q&A, and other sources—or when the user asks to reclassify material or correct a category name.

The goal is not to “put files into more folders.” It is to establish a small number of stable retrieval entry points while preserving source traceability and every relative link.

## 1. Distinguish Two Kinds of Names

### 1. Knowledge-Base Category Name

This name supports current navigation and classification. The user’s latest explicit name is authoritative. For example, if the user says a group belongs under “In-Person Classes,” do not retain an editor-inferred category such as “Anniversary Masterclass.”

### 2. Historical Source Name

This name records which event, livestream, or batch originally produced the course. A source name may preserve the old event wording; category restructuring must not rewrite historical context.

Recommended separation:

```yaml
course: current knowledge-base category name
source: original event or recording source name
```

By default, preserve old wording when it appears as factual context in body text. Correct only directory names, index headings, and fields such as `course`, `category`, or their project-specific equivalents when those fields perform a classification function.

## 2. Keep the Directory Hierarchy Small and Stable

Do not impose a translated default tree. Inventory the existing hierarchy, then record or confirm semantic targets in the manifest or explicit path map. A multi-event library typically needs these roles:

```text
{archive_root}/
├── {master_index}
├── {in_person_category}/{instructor}/
├── {event_category}/{event_id}/
├── {special_livestream_category}/
└── {private_qa_category}/
```

These are semantic roles, not literal names. Existing course structure wins; for a new library, confirm the rendered values before any move.

Rules:

- Use event category or content batch at the first level;
- For high-volume categories, group by instructor at the second level;
- Do not mechanically add multiple layers such as “transcripts / lectures / cases / images” unless one instructor’s file count is demonstrably unmanageable;
- Keep an instructor’s faithful transcripts, lectures, and assets at stable relative locations that can reference one another;
- Do not create empty categories.

## 3. Perform a Read-Only Inventory Before Moving Anything

Create a migration map:

```json
{
  "old-relative-path": "new-relative-path"
}
```

The inventory must include at least:

1. Counts of all Markdown files, images, and attachments;
2. Current event batch, instructor, document type, and asset attribution;
3. Destination name collisions, existing destinations, and case-sensitivity conflicts;
4. Wikilinks, ordinary relative links, and image links in Markdown;
5. Whether an image directory serves only one instructor or is shared across documents in multiple directories;
6. Whether unclassified files remain at the root.

Stop if any source file is missing or a destination already exists. Do not perform a partial overwrite.

## 4. Move Instructor Directories with Their Assets

Do not move only `.md` files:

- If a document and its rendered `{asset_relative_path}` belong together, move them together into the confirmed destination so the relative path remains valid;
- If multiple categories share assets, do not duplicate them blindly. Retain a shared asset directory or first design an explicit new relative-reference scheme;
- Verify Wikilinks between the two drafts as well as image links.

Prefer a layout that preserves links after the move. Rewrite body links in bulk only when necessary.

## 5. Make the Master Index the Primary Entry Point

Create or update the confirmed `{master_index}` target at the root:

- Display content by category;
- Group high-volume categories by instructor;
- Give distinguishable aliases to the faithful transcript and structured lecture on the same topic;
- Use stable relative paths;
- Keep course summaries out of the index; it is navigation only.

Example:

```markdown
## {category_label}

### Instructor A

- [[{faithful_relative_path}|{faithful_alias}]]
- [[{lecture_relative_path}|{lecture_alias}]]
```

## 6. Use a Rollback-Safe Single-Writer Migration

1. The main agent locks the final mapping; subagents must not write to the formal library.
2. Create all destination parent directories.
3. Move items one by one according to the mapping; record every completed source and destination.
4. If any step fails, roll back completed moves in reverse order.
5. Correct only explicit category metadata after migration succeeds.
6. Write the master index last so it never points prematurely to nonexistent files.
7. Do not use fuzzy bulk overwrites or rewrite course body text merely for classification.

If the environment requires approval for writes, list moves, directory creation, index creation, and metadata edits in one concise acceptance request. After the user says “organize it according to this plan,” execute immediately rather than asking for synonymous confirmation again.

## 7. Final Acceptance After Migration

Verify the actual result:

- [ ] The course-file count before and after migration matches; count the new index separately
- [ ] Every mapped destination exists and every old source path is empty
- [ ] The root contains only the master index, category directories, and permitted hidden system files
- [ ] Every Markdown link in the master index resolves
- [ ] Every cross-link between paired drafts resolves
- [ ] Every relative image and attachment link resolves
- [ ] Course category fields use the user-confirmed names
- [ ] Historical source fields and historical context in the body were not altered accidentally
- [ ] No file was overwritten, lost, or silently duplicated

The completion report should contain only: what was organized, the absolute path to the master index, and file/link acceptance results. Do not replay the migration process.

## Common Failures

### Treating a Source Name as a Category Name

An editor invents a category from an event year or promotional title, while the user thinks in terms of “in-person class / livestream / private advisory board.” Resolution: category names follow the user’s current information architecture; source names remain separate.

### Moving Markdown Without Assets

The body remains but every image breaks. Resolution: migration mappings must include asset directories, followed by final link-resolution checks.

### Rewriting Historical Body Text for Consistency

Directory classification is information architecture, not factual rewriting. Modify only fields that serve classification; preserve event context in the body by default.

### Excessive Depth

“Event → instructor → transcript → year → assets” raises retrieval cost. Start with event and instructor plus a master index. Add layers only when file volume proves they are needed.
