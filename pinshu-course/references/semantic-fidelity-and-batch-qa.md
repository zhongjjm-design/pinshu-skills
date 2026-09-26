# Semantic Equivalence and Batch QA for Faithful Editing

Use this reference for batch rework of long courses, especially a “two drafts per lesson” model: a first-person faithfully edited transcript plus a systemized in-depth lecture.

## 1. The Object of Fidelity Is Effective Meaning, Not the Gist

Faithful editing may remove verbal noise, merge mechanical repetition, and adjust sentence form, but it must preserve the source’s semantic anchors:

- Specific people and relationships;
- Products, categories, and proper nouns;
- Numbers, prices, times, and quantities;
- Specific scenes and processes;
- Causal relationships;
- Qualifiers and judgment strength;
- Category-specific user motivations;
- Distinctive metaphors and direct wording from the instructor.

### Common Invalid Abstraction

| Source Semantic Anchor | Incorrect Editing | Why It Is Wrong |
|---|---|---|
| A buyer purchases crystals for a “change-of-fortune effect” | The buyer expects some effect | Loses the category-specific purchasing motivation |
| CNY 69 diagnosis, CNY 999 coaching | Low-priced product converts to a high-priced product | Loses prices, product types, and tier details |
| Insomnia at night, lying at home after quitting without another job | Career confusion | Loses the concrete user situation |
| 53 action guides and 64 cases | Rich content | Loses quantitative evidence |
| “Northeastern everything stew” | Disorganized information structure | Loses the author’s distinctive metaphor |
| Sold several thousand yuan in one day and customer service could not keep up | Service pressure rose with sales | Loses event process and the real trigger for a service SOP |

Acceptance principle: **remove noise, not information; change syntax, not meaning; never let a broad concept swallow a concrete source expression.**

## 2. Boundaries of First-Person Articleization

A faithfully edited transcript is “a course article narrated by the instructor,” not an editor’s interpretation of the instructor.

Avoid body phrases such as:

- “The course mentions…”
- “The instructor believes…”
- “The author wants to explain…”
- “Xu Haha has a friend…” when Xu Haha is the instructor;
- Referring to the instructor as “she.”

Use the instructor’s original perspective instead:

- “As far as I know…”
- “I believe…”
- “I want to add another case…”
- “I have a friend…”
- “This changed how I understand the market…”

Editorial notes, fact verification, and compliance notices may use third-party voice, but they must be separated from the instructor’s body and labeled explicitly as “Editorial Note” or “Verification Note.”

## 3. Articleization Is More Than Rearranging Subtitles

Deleting filler such as “um” and “ah” and adding headings can still produce a subtitle fragment dump. Articleization must also address:

- Interactive rhetorical questions with no informational value;
- Repeated detours used only to maintain live pacing;
- Mechanical rewordings of the same conclusion;
- Course-process language such as “next, let’s look at…”;
- Paragraphs that are too short and fragmented like subtitles;
- Paragraphs that do not carry one complete idea.

Article paragraphs should form “judgment → explanation → example/question → transition” while preserving the source’s speaking order. Headings aid navigation; they do not replace content.

## 4. A Systemized Lecture Must Not Become a Checklist

A systemized lecture should enable a person who has not watched the video to learn independently. At minimum, develop:

```text
Problem background
→ core conflict
→ method or model
→ why it works
→ complete case walkthrough
→ applicable conditions and conditions that must not be copied
→ common mistakes
→ execution method and worksheet
```

Put tables, formulas, knowledge maps, and checklists after complete explanations. They cannot replace prose.

## 5. Integrate Slides and Screenshots Naturally

Use this default pattern: retain the original image as evidence + convert key content into text + connect it naturally to the body.

- Convert high-information-density tables fully into Markdown so they remain searchable;
- For product pages or visual examples, extract only key selling points, numbers, and information hierarchy;
- Place images where the instructor naturally discusses the topic;
- Use a concise caption such as “Original Course Slide”;
- Do not interrupt reading with long “slide supplement / source declaration” passages;
- Do not present text visible in an image as if the instructor spoke each item aloud.

## 6. Acceptance Traps in Parallel Batch Rework

Multiple agents can reduce omissions caused by long contexts, but a subtask’s “complete” status is only self-report, not acceptance evidence. Common residue includes:

- A faithful transcript slips into third person locally;
- Frontmatter is correct while the body still says “the instructor believes” or “the course mentions”;
- The ending is truncated;
- A case name is rewritten, causing simple keyword checks to report a false omission;
- The lecture expands substantially but loses key numbers or source-case detail;
- Numerous headings exist but explanatory prose is still missing.

### Recommended Acceptance Sequence

1. Compare the approved scope with files actually modified. If unauthorized intermediate, QA, or temporary copies exist, register them without deleting them unilaterally and do not count them as formal outputs;
2. Check frontmatter, `document_type`, `status`, and the unique H1 in the faithful transcript;
3. Scan for placeholders, unclosed code fences, and suspiciously truncated endings;
4. Scan the faithful body for third-party terms such as `the course`, `the instructor`, `the author`, `the instructor themself`, `Xu Haha`, and third-person pronouns; manually exclude frontmatter, editing notes, and editorial callouts;
5. Scan for filler such as `right?`, `everyone look`, `OK`, `think about it`, `um`, `ah`, and `uh`;
6. Build a checklist of key people, numbers, tools, and cases for each lesson and verify them individually;
7. Compare one passage each from the beginning, a middle case, and the ending with the authoritative source. Do not sample only the main line; include a side case, a limiting condition, and an operational process;
8. Compare the source range with the edited draft’s non-whitespace character count. The ratio is not a hard quality threshold, but if many lessons consistently retain only about 20%–30%, treat this as a red flag for possible summarization and inspect whether the removed material was truly only verbal noise;
9. Repair defects locally and rescan. Do not rely on subagent line counts or “no issue found” reports.

### Task Size and Timeout Handling for Large Batches

- Do not assign a single agent a full day containing hundreds of thousands of characters and four or five lessons for the first writing pass. Prefer one or two natural lessons per task. Larger tasks are more likely to compress faithful editing into dense summaries.
- Separate generation from acceptance. A drafting agent cannot approve its own work; use another agent or an independent QA perspective to resample the raw transcript.
- A subtask timeout does not prove that no output exists. Inspect actual target files, modification times, character counts, H1, frontmatter, and endings first, then complete only missing work. Never rerun blindly and overwrite generated files because of a timeout.
- A subtask’s “complete” report does not prove quality. Specifically inspect whether complete cases have become conclusions, concrete numbers have been abstracted, gray-area or high-risk expressions have been sanitized, or a source truncation has been converted into a satisfying conclusion.
- Rework tasks must read the entire QA report and repair against the raw transcript. QA reports identify defects; they are not sources from which to reconstruct the instructor’s words.
- Task instructions must specify exactly which files may be modified and forbid creating any others. Even then, acceptance must scan for extra products because a subagent may generate unauthorized QA reconciliations or intermediate drafts.

## 7. Authority Order for Sources

```text
User-provided raw transcript / raw file / audio-video transcript
> faithfully edited transcript
> systemized lecture
> summary and cross-lesson knowledge base
```

Begin batch rework from the highest available source. Never reconstruct the instructor’s original voice from an old lecture or summary.

## 8. Rework Driven by Independent QA: Close Every Finding

When independent QA identifies missing cases, numbers, relationships, operations, or speaking order, do not merely insert a sentence into the old draft. Follow this process:

1. **Lock the source range:** record original audio files, first and last line numbers, and cross-file continuation points for each lesson. Delimit silence hallucinations, break-time chatter, and the next lesson’s opening separately.
2. **Record the pre-rework baseline:** before editing, count non-whitespace characters. Prefer removing all Unicode `isspace()` characters, and state whether frontmatter and Markdown markers are included.
3. **Build a QA-anchor register:** each entry must include source location, old-draft location, missing meaning, action taken, pending confirmation, and final state. “Optimized” is not sufficient.
4. **Restore from source item by item:** recover complete background, relationships, numbers, questions, live actions, correction process, and outcomes from the raw transcript—not from a QA summary or old lecture.
5. **Restore source order:** if the old draft rearranged material across sections, move complete passages and check for duplicates. Verify with a heading-order scan rather than memory.
6. **Restore judgment strength:** if the source makes a direct assertion or gives a specific amount, percentage, or strong promise, do not soften it into “possibly,” “some people,” or “relatively high.” Put compliance risk in a separate editorial note rather than changing the instructor’s body.
7. **Reconcile the ending:** if the source closes on one specific judgment, do not synthesize a new first-person grand conclusion for the whole document. If a summary is needed, label it “Editorial Summary.”
8. **Retest after rework:** recount non-whitespace characters, increment, and total, then update every QA state. Character growth is not sufficient proof, but an abnormally short reworked draft usually indicates continued summary-level deletion.
9. **Consolidate relisten items:** list names, models, commands, paths, account names, incomplete numbers, screen text, and unfinished outcomes by lesson; mark them at the corresponding body locations as well.
10. **For fuzzy enumerations, restore explanations without inventing names:** when the source clearly says “five advantages” or “seven steps” but STT renders item names ambiguously or repeatedly, recover each explanation, example, and causal relation confirmed by context. Put exact wording into relisten status rather than inventing definitive terminology for a tidy list.
11. **Preserve subject specificity:** when the source says “our company,” “my own product,” or “this student,” do not generalize it into “many companies,” “the industry,” or “some people.” Changing the subject converts personal experience into an industry-wide claim.
12. **Restrict modification scope:** when the user says “modify only the target files,” do not create backups, QA drafts, reconciliation tables, or intermediate files. Maintain the QA register internally during execution and report only the final modified-file list, character changes, and relisten items. Persistent additional reports require separate authorization.
13. **Use one character-counting convention:** prefer the existing QA convention of non-whitespace characters using Unicode `isspace()`. Report before, after, absolute change, and percentage change. Total characters including whitespace may be added only when labeled separately. Never treat UTF-8 byte count as character count.

### Two-Layer Annotation for Ambiguous Numbers and Editorial Voice

When a number has two or more plausible transcriptions:

- Put only a minimal inline marker in the body, such as “during the sales peak [amount requires relistening],” without placing editorial reasoning inside the instructor’s first-person sentence;
- In a separate closing “Editorial Notes | Items Requiring Relistening,” list candidate numbers, conflicting evidence, contextual anomalies, and why no candidate was selected;
- If exact precision can be omitted without losing meaning, retain the event and judgment without forcing a choice;
- Keep editorial notes, product-segment transition notes, and STT anomaly explanations separate from the instructor’s body. Do not make the instructor appear to explain transcription errors.

### Minimum QA Report Fields

```markdown
| # | QA Item | Source Location | Resolution | Status |
|---:|---|---|---|---|
| 1 | [Missing issue] | [File + line number] | [Restored content] | Passed / Requires relistening |
```

The report must end with:

- Non-whitespace character count before, after, increment, and total for each file;
- Items requiring relistening or visual verification for each lesson;
- Explicit counting convention;
- Actual modified-file list.

## 9. Do Not Rewrite a Live Demonstration as a Retrospective SOP

Technical, agent, and software-demo lessons often contain a messy live process: installing while trying, help from multiple people, unclear commands, and differing system paths. In a faithful rework:

- Preserve the true action sequence for group commands, copying, downloads, extraction, directory searches, confirmation prompts, errors or stalls, and continued Q&A;
- If the instructor did not demonstrate a complete standard process, do not manufacture a clean six-step SOP and present it as the source lesson;
- Treat suspected commands in STT as approximate transcription and mark them “requires relistening / compare with group message.” Do not complete them into executable commands;
- Use Windows and macOS paths only when supported by a clear screen or reliable speech;
- You may add an “Editorially Reconstructed Reproduction SOP” after the body, but separate it from “Live Classroom Process” and label provenance clearly.

## 10. Preserve High-Risk Cases and Separate Editorial Warnings

Income guarantees, efficacy claims, fortune-changing promises, and extreme outcomes are often central to the classroom argument about why users believe or disbelieve. Do not delete them merely because risk is high:

1. Preserve the instructor’s intended meaning, numbers, and judgment strength in the body;
2. Do not present a spoken case as verified fact;
3. Add an “Editorial Risk Note” immediately afterward or in a separate verification section;
4. Limit the note to evidence status, applicable boundaries, and compliance risk; do not rewrite the instructor’s position.
