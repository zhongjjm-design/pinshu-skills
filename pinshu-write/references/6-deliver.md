# Revision, delivery and after publishing

## Revision after the author's comments

**First sort the comments into three kinds**: wording (words, punctuation, sentences, paragraphs), checking (re-measure a number, confirm a name or date) and images or downloads (screenshots, videos). Wording goes first and alone: revise, check, hand the draft back. Checking and images run as separate jobs that never hold the draft back; report them when they finish. Read a background result the moment it arrives.

**One writer call per round.** All wording changes that need the writer, from the merged review list or from one reply of the author's, go to the writer together in one call; a change noticed after the call joins the next round instead of starting its own call. The 2.2 test article spent five revision calls on one draft.

**Then size each wording change.** When unsure, take the smaller size, say so in one line, and let the author ask for more.

| Size | What it looks like | What happens |
|---|---|---|
| 1 Swap | The author gave the exact words ("change X to Y", add a comma) | The writer's session replaces them word for word, runs the audit, shows a before-and-after list. No writer, no review. Using the author's own words is not the organizer writing |
| 2 Sentence | The author points at a few sentences without wording ("unclear who 'this' is") | The writer rewrites only those sentences (`prompts.md`, "Fallback writer: revise", sentence version, when the fallback wrote it; otherwise in place); run the audit |
| 3 Paragraph | A paragraph rewritten, an example swapped, one section reworked | The writer revises only that part; the editor checks only that part; run the audit; rerun a matching reviewing role only if a fact or claim changed |
| 4 Direction | The judgment, structure or title direction changes | Return to the matching step and run the route from there; gate 2 opens again |

The writer applies accepted changes to the current full text and hands the author the complete article with a short before-and-after list, never a list of new subheads or a new outline. When the author sends several comments at once, number them as received and mark each done, not done (with why), or sent to checking or images. Facts touched by a change are re-checked one by one at their source and written into the fact table at once. A check whose answer cannot change the body gets about two minutes; if nothing turns up, write "not found; looked in: ...".

After 定稿, sizes 1 to 3 keep the facts pass already done (a changed number or quote goes through the fact checker once); the author reading the complete revised article and saying 定稿 for it approves that version. Size 4 reopens the matching gate.

## Export (after the author says 定稿)

The author's sentence goes verbatim as `--approval`; the script refuses any sentence that is not a plain 定稿 (the list of words that are not final is in SKILL.md) and any negation, condition or question around 定稿 (不是定稿, 是否定稿, 等改完再定稿). Without 定稿, use a trial export (`--output-dir`) instead.

```bash
python3 scripts/export_article.py --source <the approved draft> --ready-dir <ready_folder> \
  --account "<account>" --date <approval date, YYYY-MM-DD> --writer "<the model that actually wrote it>" \
  --process-dir <this article's process folder> --approval "<the author's own sentence saying 定稿>"
python3 scripts/export_article.py --check --body-only <the ready copy it printed>
```

Then write the publishing kit and the image task (below) and check the whole pair: `python3 scripts/export_article.py --check <the ready copy>`. Fix every problem it reports before telling anyone the article is ready.

- The ready folder is written only by this script; a hand-copied file has the wrong header. The script adds the account folder itself, writes `YYYY-MM-DD_<title>.md` with a flat YAML block of five double-quoted fields (账号, 定稿日期, 写手模型, 过程文件夹, 配图排版进度 fixed as "详见配对发布物料包的配图排版进度"), then the H1, body and 参考文章 block without the editor notes, and prints the path, the SHA-256 (the article hash is always of this whole file, header included) and the paired kit name. It appends the author's sentence, time, file and hash to `定稿确认记录.jsonl` in the process folder; `--check` warns when the ready copy has no matching entry.
- A changed article is re-exported with `--replace` and the author's 定稿 for the new version; the old copy is kept in the process folder (`定稿替换留底/`). Update the kit if it is affected, and say so.
- `ready_folder` is the root of the ready-to-publish area; to use the visual Skill's ready-article entry, it must be the root that Skill's ready-folder contract names (one level above the account folders). Drafts and ready pieces do not yet speak for the account: collision scans leave them out.
- Tables are not supported by the layout yet: a table in the body is flagged to the author to choose another form, never silently dropped. Tell the author before gate 3.

**Folders and names.** One folder per article, named with date and topic, in the configured drafts folder. Process files carry step numbers and versions (`03-outline-v2.md`); every body version inside carries a number (`draft-v13.md`), never a title-named body. The finished article's file name is the article title in exactly two places: the ready copy and any preview copy for the author.

**Delivery format.** Markdown; first line the single `# title`; `##` subheads written for skimmers. After the body at most one reader-facing block, `## 参考文章`: the complete long-form pieces the article drew on, which a reader can go and read (listing them credits their authors), and the main research reports and surveys the body uses whose source a reader can find; one line each (full title in 《》, author or organization, platform, date), as many as the article really drew on, none if none. Never list short posts or quotes already told in the body, screenshot sources (they go in captions), our own checks and searches, internal workflow or tools. The body ends without a signature line: the platform's author field and original mark already name the writer, and a second byline at the end repeats it. Then `===EDITOR NOTES===`, written by the organizer, with the verification list (never exported), facts still to verify, author experiences to confirm, hypothetical scenes used, material left out and why, article type, the exemplars used, which writers drafted and which draft the author picked, who reviewed (and whether the author named the writer), any same-vendor review, the seed's outcome, the audit summary.

### Wording edits after 定稿

A narrow polish after 定稿 happens only when the author requests it, as one atomic release edit:

1. Lock the title, judgment, facts, numbers, dates, author experiences and the 参考文章 block; if any must change, reopen the matching stop.
2. Produce an AI-flavor report first and change only confirmed problem sentences.
3. Pull a fresh fact sheet from the edited text and mark it against the previous one as step 8 does (`5-review.md`, step 8, item 1); a 改 or 新 line means a fact changed, which reopens the matching stop. Then run `audit_draft.py`.
4. Re-run the export with `--replace` and the author's 定稿 for this version.
5. Search the kit and the image task for old sentence prefixes, quote lines, repost lines, summaries, captions and video slots; update only the affected fields; write the new article hash into the task file; re-bind the kit through the visual Skill's ready-article entry (`--bind-kit`).
6. Mark existing screenshots, illustrations and layout affected by the change "to re-check".
7. Verify the title still matches the file name and the article hash equals the asset-plan hash before reporting completion. Editing only the Markdown leaves stale quote lines, anchors and hashes.

## Evidence screenshots

Screenshots are evidence; the writing step knows which page and sentence each proves, and pages change, so this step captures them.

1. **Capture from the fact table's marked column**, with the link and quoted sentence recorded during research; never re-search for the post.
2. **When**: after gate 2, as a separate job that never blocks drafting or delivering a draft; in the background if the tool allows.
3. **How**: with the visual Skill's capture script, which alone writes the capture record (time, source link, file fingerprint) the visual entry needs. Framing, sharpness and scroll offsets live in that Skill's article asset handoff reference. Without the visual Skill or a browser, deliver the list and mark every item 待补截.
4. **Time limits**: before the first capture, check the browser window is in front and try one capture of a simple page. Each attempt gets about one minute, and the visual Skill's attempt limit applies (no second number here). At the limit, stop, write a manual handoff (link to open, part to capture, how, where to save, file name) and carry on with everything that does not depend on it.
5. **Open every image.** A script's "success" is a floor: check each image is not blank, cut off, covered by a floating bar, or showing the wrong post. Fix on the spot; a fixed image counts only once it is back in the article's own image folder and the kit, with one line on who fixed what and when.
6. **Screenshots readers cannot read** (a Japanese article for Chinese readers) stay out of the article. English stays: one or two short lines need no translation; a long English passage gets one or two Chinese sentences in brackets in the caption.
7. **Numbers that change** (views, plays, likes) are re-measured on publishing day and re-captured that day; mark them 发稿当天重截.
8. **Save** originals in the process folder's evidence-screenshot folder, each with source link, capture time, the sentence it proves and the paragraph it follows.

After every new body version, once an image list or kit exists: does each anchor sentence still exist, do the kit's named subheads still exist, does each status line match reality? Update only what changed.

## Publishing kit

Made only after the facts pass and the author's 定稿. An article ships as three files: the writing original with editor notes, the exported article, and the image task file defined in the visual Skill's handoff contract (agent-maintained; each image names the paragraph it follows, what it helps the reader understand and its kind: AI-generated visual, evidence screenshot, real photo, or program-rendered graphic). Alongside them, one human-readable page, `YYYY-MM-DD_<title>·发布物料包.md`, sits in the ready folder beside the body, opening with a flat YAML block of two double-quoted paths (正文路径, 配图任务路径). Images, screenshots and the task file stay in the process folder; the kit lists their paths. It is a view of the same data, not a second task list. Parts:

1. **Images**: a table with a column 放在哪段后面（段落开头）, quoting that paragraph's opening words exactly so `--check` finds it. For every screenshot: source link, exactly which part to capture (only what the article comments on), the paragraph it follows, what it shows, the text credit, and its status (已截好 with path, 待补截, 发稿当天重截). Permission status on its own line. Never substitute an AI-generated image for a screenshot; data charts are drawn by program, never by an image model.
2. **Captions** carry the text credit ("截图来源：<who> 在 <platform> 上的原帖"), never a link; a short Chinese gist in brackets only when it gives the reader something the image and body do not.
3. **Video**, for each case, in this order: a Channels copy exists, embed it; otherwise the video suits uploading, download and upload; otherwise a screenshot with a text credit; otherwise no image. A WeChat Official Account article embeds only Channels or uploaded videos and carries no external links. List each video in a table with the same anchor column, its name, original link, length and resolution, whether it can be downloaded (probe only), and the suggested step with the reason. Every video that goes into the article is also written into the image task's `body_videos` (`after_prefix`, `label`, `source_url`). A paragraph is followed by one image or one video, never both.
4. **Cover and share image** are not written here; the visual Skill makes real sample covers. The kit supplies only the title and quote lines.
5. **Title, 3 summary candidates, 3 quote-line candidates** for share cards, each passing `audit_draft.py --card` and the AI-flavor audit.
6. **Repost lines (转发语)** for each platform the account runs (the profile says which; counts and lengths follow the profile), written by the writer. First answer, at the top: what doubt do readers have that this article clears up? Each line starts from one real doubt or complaint readers have about the subject, paraphrased from a real post or comment without naming anyone (note the source under the lines; if none can be found, ask the author for a question they have actually heard), then gives the article's answer in one or two sentences. Every fact and number in that answer is in the body; the doubt carries no claim the article does not itself confirm or correct. The speaker is the author about their own article ("I wrote", "I checked", the last only when the fact table records the check), never a third person recommending it. The author's own production line and team are not the subject unless the article is about them. Changing repost lines changes the kit's needs, so re-bind.
7. **Facts still to check** before publishing, numbers to re-measure on publishing day, and where the verification list is.
8. **For the author to confirm personally**, never chosen by the agent: a tentative title, whether to declare originality, whether to tick the AI-generated-content declaration, open visual choices.
9. **Next handoffs** to the visual Skill and layout; changes after images exist mark them "to re-check".

## Hand off to illustration and layout

Approved articles go through the visual Skill's ready-article entry: write the ready copy and the paired kit, write the image task file (its `source_md` is the ready copy, its `article_sha256` the hash the export printed), then bind with that Skill's ready-article script (`--article <ready copy> --kit <paired kit> --bind-kit`; `--prepare-only` with no browser). If that Skill documents different options, follow that Skill. Pass only explicit paths; never let a downstream step pick the newest file. A draft not yet approved may get a trial layout only: `export_article.py --source <selected.md> --output-dir <new-directory>`, then the Skill's general pipeline, said plainly to be a trial. Evidence screenshots stay with the writing step; AI illustrations, information graphics and covers stay with the visual Skill. Without a visual Skill, deliver the needs and the source identity, claiming no asset production.

## Cleanup

When delivered, run `export_article.py --check` on the ready copy once more, then move empty files, files holding only an error, and intermediate outputs that will not be used again to the system trash. Keep: the seed (original and the point map), the judgment record, the outline, every body version, the writer and review records, the review sheet, the feedback candidates, the kit, `定稿确认记录.jsonl`, and on a timing run `阶段记录.jsonl` with `阶段耗时账.md`. List what was moved in the closing message.

## Timing log (only when the author asks to measure speed)

On such a run, log every step with `scripts/stage_log.py`, using the route's step names (1 Topic, 2 Research ... 8 Final, plus Evidence screenshots and Revision), and say in each `--note` what the step changed in the draft ("none" if nothing). A step that changes nothing over two or three timing runs is a candidate to cut or merge.

```bash
python3 scripts/stage_log.py --dir <process folder> start "<step>" --kind machine|wait|human [--model "<model>"]
python3 scripts/stage_log.py --dir <process folder> end "<step>" [--result ok|failed|empty|quota|timeout|login|blocked|skipped] \
  [--note "<what happened>"] [--resume-from "<step>"] [--manual-handoff <file>]
python3 scripts/stage_log.py --dir <process folder> summary
```

`machine` is a model or script working, `wait` is waiting on something outside, `human` is the author reading or deciding (a stop runs from sending the message to the answer). Log every model call with its model, and a probe that came back empty, over quota or timed out with that result. A documented fallback is logged `skipped` with a note of what was delivered. When a step fails or stalls, log it with `--resume-from`, carry on with what does not depend on it; the reporting rule is in SKILL.md. `summary` writes `阶段耗时账.md`.

## Collection / column placement

Treat a WeChat collection as a reader-facing editorial promise, not a precise internal taxonomy. Classify the article by the change it helps readers understand, not by surface nouns: an article about AI changing pricing, profit allocation, contracts or organizational rules can stay in a broad AI-evolution collection even when the title is about quotation or procurement.

Do not open a new collection for one borderline article. First keep an internal candidate tag and reuse the broad existing collection when its reader promise still fits. Propose a new collection only when at least three to five real or firmly planned articles share one repeatable reader question, and the direction can plausibly sustain five to ten pieces; otherwise the account fragments into one-article shelves. State the proposed collection name and boundary, but the author chooses the final collection. Record the chosen collection in the publishing kit only after that decision.

## After publishing

Not part of writing time.

- **Ledger**: one row each at day 1, 3, 7 and 30: the core judgment, the analytical cuts used, reading and interaction numbers, main faults, what to feed back. The author reports the day-7 and day-30 read counts from the account's back end; write them beside what the market reference had suggested, if it ran.
- **Every 8 articles**: take the day-7 read counts of the account's articles so far (at least 8), compute the mean and standard deviation, and set the account's normal band at the mean plus or minus one standard deviation (a starting assumption; re-set it at about thirty articles). Each article outside the band gets one anomaly review in the format of the account's hit-review file (configuration `hit_review_file`: why the title opened, the opening hook, the structure, the emotional line, reusable factors, source); articles inside get none. The band decides only whether to review; it never grades an article.
- **Pass lines**: when the account's good-article standard (configuration `good_article_standard`) gives pass lines for open rate, read-through rate and the like, read the numbers against them; once the account has its own band, the account's own numbers win over borrowed lines.
- Use the numbers to tune titles and openings, not prose style. Keep the AI draft and the author's final side by side; how the author's edits become rules is in `write.md`, "After 定稿", and nowhere else.
