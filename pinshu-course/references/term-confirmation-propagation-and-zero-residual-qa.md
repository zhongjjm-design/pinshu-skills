# Propagating Confirmed Course Terminology and Zero-Residual Acceptance

Use this reference when the first organization pass of both course drafts is complete, the end of a file or the course map still contains “terms pending confirmation,” and the user then confirms product names, model names, commands, mode names, or feature states in several batches.

## Core Principle

A user’s direct confirmation of the course’s intended wording and recorded screen is an authoritative correction input for course processing. Apply an explicit correction immediately without asking the user to confirm again. However, “the user confirms that the course said this” must not be expanded into independent verification of the external world.

Distinguish three states:

1. **Terminology confirmation:** names, capitalization, homophones, and product classes. Examples: `Grok I → Grok`, `Chat Car → ChatCut`, and `Go → Goal`.
2. **Course-feature confirmation:** the user confirms that a feature demonstrated in the recording was available at recording time. Remove “possibly unavailable,” but do not infer that every platform, client, or current version behaves identically.
3. **External fact verification:** user counts, token rankings, prices, release dates, market share, and similar claims. Unless the user also supplies a verifiable source, retain them as classroom reports or pending external verification.

## Propagation Scope

Every confirmation must produce a checklist from “confirmed item → every derived artifact.” Check at least:

- Faithful transcript body;
- Pending-confirmation section at the end of the faithful transcript;
- Structured lecture body, terminology boxes, and risk boundaries;
- Course map, next-lesson preview, flowcharts, and checklists;
- `fact_status`, status, and source fields in frontmatter;
- Synonymous old forms, homophone errors, and obsolete caveats.

Do not merely check off the confirmation list while leaving the wrong name in the body. Do not modify only the body while leaving the old “still pending confirmation” state.

## Incremental Confirmation Process

The user may provide answers across two or three consecutive messages. Process each incrementally:

1. Read this batch of confirmations and any earlier confirmations not yet propagated;
2. Search the entire course directory for old forms and pending-confirmation language;
3. Apply targeted updates without overwriting the latest changes made by the user or another task;
4. If a patch fails because a file changed or context no longer matches, reread the latest file and rebuild a targeted patch against current text. Never roll back the whole file or overwrite from an old snapshot;
5. After the final confirmation batch, run a zero-residual scan.

## State-Rewrite Rules

A confirmation checklist is process metadata, not a permanent part of course prose. Once terminology or feature state has been integrated into the body, apply this default: **keep the fact in the body and remove the confirmation process from the final draft.** Do not keep confirmation explanations indefinitely merely to prove verification occurred.

- Delete `## Terms Pending Confirmation` after all project items are confirmed instead of mechanically renaming it `## Confirmed Terms`. Retain only a concise log if the user explicitly requests an audit trail.
- Also remove opening callouts such as “confirmed terms / confirmed features and terms,” “tool confirmed” labels inside cases, checked confirmation lists in the course map that exist only for process tracking, and closing “confirmed information” summaries. Correct names, commands, and feature descriptions remain where they belong in the body.
- If the user says “confirmed items can also be deleted,” interpret this as deleting **confirmation-process notes**, not the knowledge facts already integrated into the body.
- When closing the final pending item, do not create a new “confirmed information” section to replace the old list. Update the body, frontmatter, and course state directly.
- Keep only terminology tables in the course map that serve learning or future maintenance. Remove sections whose only purpose is to show who confirmed what unless the user requests an audit trail.
- Rewrite obsolete frontmatter such as “product interface and version unverified.” If every item is closed, use concise factual state rather than a long confirmation history.
- When the user confirms a model name, use the correct name directly. Do not repeatedly add “the course provider confirmed the name,” and do not invent an official release date or external version history.
- If the user confirms that “anything demonstrated must have been live,” describe the capability as available at recording time without expanding that into availability on all platforms. No separate feature-confirmation note is needed.

## Two Meanings of Closing a Confirmation Item

Determine which meaning the user intends:

1. **Content confirmation:** the user says “this is correct” or “the screenshot was already supplied and corrected.” Mark the current name, screenshot transcription, or interface wording as confirmed by the course provider and remove every obsolete caveat.
2. **Blocking waiver:** the user says “this no longer needs confirmation” or “it does not affect this lesson.” This means only that the detail no longer blocks finalization. Unless the user also says the existing wording is correct, do not elevate an incomplete screenshot, guessed name, or fuzzy number into verbatim fact. You may retain “handled as an approximate value reported in the course” or “interface detail does not block finalization,” but remove task state.

Propagate closure **within one lesson boundary**. Close only pending items for the lesson the user identifies; preserve independent items in other lessons until the user explicitly closes them.

## Prevent Confirmed State from Reappearing

Course confirmation state is maintained data, not a one-time endnote. After context compaction, continuation into later lessons, or rereading an old summary, never reintroduce historical pending items. Before reporting what remains pending, inspect the latest formal course tree:

- Current course-map state;
- Ending state in the faithful transcript and lecture;
- Frontmatter `fact_status`;
- Source notes, warning callouts, and editorial notes in the body;
- The user’s latest explicit confirmation or waiver.

Old session summaries, stale tasks, and earlier search results may help locate material, but cannot override the latest on-disk state. If the user says “that was already confirmed,” acknowledge the state-maintenance error and clear the full course tree without asking the user to resend screenshots or explain the same item again.

## Zero-Residual Acceptance

Run at least two search groups:

### Old-Form and Semantic-Residue Search

Do not search only for the heading “Pending Confirmation.” Also search for synonymous stale states such as “pending recording confirmation,” “still requires recording verification,” “exact behavior remains to be confirmed,” “complete source still required,” “precise number pending interface confirmation,” “not fully recovered from text-only input,” “cannot be completed as a definite command,” “may not yet have been released,” and “do not infer from this.” Search every original homophone, old name, `Goal/Go`, `Go command`, “consolidated pending confirmation,” “official name unverified,” and related forms.

Expected result: zero, or a documented reason for every retained hit. Rules such as “deletion, payment, and publication still require human confirmation” are task-safety boundaries, not course terminology pending confirmation. Classify hits semantically rather than deleting valid safety rules for a mechanical zero.

### New-Form Coverage Search

Verify that formal names, commands, and product categories appear in the faithful transcript, lecture, and map where required. Occurrence count is not a quality measure, but can expose a change applied to only one file.

Read back the map’s confirmation region and each lesson’s ending state to verify alignment with the body. Announce terminology clearance only when old-form residue is zero and the result has propagated to both drafts and the map.

## Common Traps

- Recording the user’s correction only in chat without updating formal files;
- Updating the course map but not the body;
- Deleting the final pending list while leaving body warnings, callouts, or “still requires recording confirmation” language;
- Treating a finalization waiver as proof of verbatim evidence;
- Reintroducing a closed item after compaction, stale-summary recovery, or an old task even though the user already supplied a screenshot or confirmation;
- Closing independent items in other lessons while clearing one named lesson;
- Rewriting “demonstrated in the recording” as “available on every platform”;
- Treating a course provider’s confirmation of a model name as external fact verification;
- Claiming all files were updated when some multi-file patches failed;
- Using an old whole-file snapshot after patch context fails and thereby destroying concurrent changes;
- Leaving frontmatter as “version unverified” after terminology is cleared.
