# Delivery and the mechanical check

Details behind step 7 (Deliver) of the SKILL.md workflow: the audit script, the delivery format, file names, the ready folder, evidence screenshots, cleanup, the handoff to the visual and layout Skills, and the one-page publishing kit.

## Mechanical check

Run on every draft before each review round and before the draft goes to the author. If your tool can run commands, run it yourself; if not, ask the author or another agent that can run Python 3 to run it and paste the output back, and until then check the hard rules (plain-writing reference) by reading, noting "audit not run" in the editor notes:

```bash
python3 scripts/audit_draft.py draft.md --length 2500-4000
```

- Add `--seed <the author's verbatim seed file>` when checking a seed restatement, judgment card or approval message: it flags scope and relationship wording the seed does not use ("no longer", "turn to", "replace", "the real thing is", "has failed" and the like), which models in testing added and then reported as unchanged. The check is the script's, never the writing model's. It judges sentence by sentence (table cells count as sentences): a sentence quoted from the seed is skipped (short ones only when copied whole), a negated scope word ("不能替代", "不能完全替代", "并未过时") is skipped, ordinary senses such as "替代方案" are skipped, everything else is reported with its line. Exit code 2 means scope flags were found: that is not a pass; every flag goes to the author, and the author's answer goes in the decision log. Known limits: wording outside its lists can slip through, and so can a reversal carried by an inserted clause; a plain "只看" in an unrelated sentence is still flagged. It is a mechanical floor, not a reading of meaning; the author judges.
- Read the counts in the report, never only the exit code: exit 0 can still carry fixes and warnings. Exit 1 means blockers; exit 2 means seed flags.
- Run the AI-flavor audit beside it every time (the plain-writing reference, "AI flavor at every step": which script, and which of its findings stay because they are the author's own words).
- For a judgment card, outline or other process text shown to the author, add `--card`: it keeps the wording rules (reversals, banned words, dashes, quotes) and drops article-shape checks (length, sections, subheads, opening).
- Add `--banned-file` with the account's banned-word list (one per line, UTF-8).
- Before writing any Chinese, run `python3 scripts/audit_draft.py --rules` once. It prints the banned words, the sentence patterns and the title and subhead examples in Chinese characters. If you cannot run commands, read the `RULES_TEXT` block near the top of that script instead.
- The script only counts and locates: it reports blockers, fixes and warnings, and exits 1 when a blocker exists. Passing it is a floor, never proof of quality.
- An opening built on a hypothetical scene is a required fix. It also warns about subheads outside 8 to 14 characters or uneven in length, paragraph lengths that are too even, foreign terms that look unexplained (a term followed by a bracketed explanation, or explained in the same sentence with phrases such as "is a kind of" or "that is", is not listed), prompt colons, and paragraphs that open with an abrupt comment.
- Character counts and pattern counts always come from the script, never from a model's own report.

## Delivery format

- Markdown. First line is the single `# title`; body uses `##` subheads written for readers who only scan subheads.
- After the body, at most one reader-facing source block, headed `## 参考文章` ("reference articles"; the author chose this name). It lists only complete long-form pieces a reader can go and read: articles on websites, long posts, reports. One line each: the full title in 《》 (foreign titles kept in the original language; whether to add a Chinese translation is the author's call), author, platform, date. List as many as the article really drew on, often only one or two; the point is not to pile up every source (a long list of short posts and notes was what the author rejected), not to reach a number. If there is none, leave the block out. Never list: short posts or quotes already told in the body, screenshot sources (they go in captions), our own checks, searches, surveys, community conversations, internal workflow or tools used. Good: 《Build live dashboards and animate explainers with Claude》，Anthropic，2026 年 10 月 8 日. Bad: "Tom CC's prompt, anchor words, the climax at 17 seconds, four steps: Tom CC post, X".
- Then a line `===EDITOR NOTES===`, followed by: **the verification list** (one line per fact: what it supports, source, date; kept from drafting through review, never exported to the ready copy); facts still to verify; author experiences to confirm; hypothetical scenes used; material deliberately left out and why; article type used; who wrote and who reviewed (and whether the author named the writer); whether any review was same-vendor; the seed's outcome (stands, partly wrong, overturned); the audit summary.

## Folders and file names

- One folder per article, named with the date and topic, in the configured drafts folder. Ask where if none is configured.
- Process files (seed, topic cards, research pack, judgment card, outline, writer and review files, drafts) carry step numbers and versions, for example `03-outline-v2.md`.
- Inside the process folder, every body version carries a version number (`draft-v13.md`); never keep a title-named body there. In testing, a title-named file in the process folder stayed at version 8 while the real draft was version 12, and a downstream step nearly laid out the old one.
- **The finished article's file name is the article title**, in exactly two places: the ready copy (`date_title.md`, written by the export script) and any preview copy made for the author to open. In testing, the author twice could not tell from a file name what the article was.

## Ready folder

After approval 4, write the approved article into the configured `ready_folder` with the export script, never by hand:

```bash
python3 scripts/export_article.py --source <the approved draft> --ready-dir <ready_folder> \
  --account "<account>" --date <approval date, YYYY-MM-DD> --writer "<the model that actually wrote it>" \
  --process-dir <this article's process folder>
python3 scripts/export_article.py --check --body-only <the ready copy it printed>
```

Then write the publishing kit and the image task (below), and check the whole pair:

```bash
python3 scripts/export_article.py --check <the ready copy>
```

The script adds the account folder itself (passing a path that already ends in the account folder also works; it is not added twice). Never copy a draft into the ready folder by hand: in testing, a hand-copied file had the wrong header and the visual entry refused it. `--check --body-only` verifies the article alone (five-field header, file name, one H1, account folder, no editor notes, the 参考文章 block). The full `--check` adds the pair: the kit and its two paths, that the process folder and image task exist, and that every image anchor in the kit is the opening of a real paragraph. Fix every problem it reports before telling anyone the article is ready.

It writes `YYYY-MM-DD_<title>.md`: a flat YAML info block first (exactly these five fields, every value in double quotes: 账号, 定稿日期, 写手模型, 过程文件夹, and 配图排版进度 fixed as "详见配对发布物料包的配图排版进度"), then the H1, body and 参考文章 block, without the editor notes (so the verification list never reaches readers). The layout Skill recognizes the block and keeps it out of the published text. The script prints the file path, its SHA-256 and the paired kit name. "The article hash" always means the SHA-256 of this whole file, header included; the visual Skill checks that same value. A draft saved with Windows line endings or a byte-order mark is handled; a draft with an unclosed YAML block at the top is refused. The real image and layout progress is written only in the kit, never in this header, so a progress change does not change the article's hash.

Once made, the publishing kit (below) goes beside it as `YYYY-MM-DD_<title>·发布物料包.md`, the same date and title, so the pair sorts together. The kit also opens with a flat YAML block of two double-quoted paths: 正文路径 (the ready article) and 配图任务路径 (the image task file in the process folder). Images, screenshots and the image task file stay in the article's own process folder; the kit lists their paths and never copies them into the ready folder. The ready folder holds approved articles waiting to be published, so the author can see at a glance what is ready; the article's own folder in the drafts folder keeps every process file. If no ready folder is configured, ask where it is. `ready_folder` in the configuration is the root of the ready-to-publish area; the script adds the account folder. If the article goes on to the visual Skill's ready-article entry, that root must be the one the Skill's ready-folder contract names (one level above the account folders); any other root works for writing only, and the visual entry will refuse it. If the article changes after it is in the ready folder, re-run the command (it replaces that file) and update the kit if it is affected, and say so. The visual and layout Skills keep the receiving side of this contract (their "ready folder contract" reference); this Skill does not edit theirs.

Layout limits to tell the author before approval 4: any number of `##` sections is fine; tables are not supported by layout yet, so a table in the body is flagged to the author to choose another form, never silently dropped or turned into an image.

Pieces in the drafts folder and the ready folder do not yet speak for the account: collision scans check them by title only, and research does not read them as the account's views or material. Published articles are read in full.

### Post-approval wording edits

A narrow polish after approval 4 is allowed only when the author requests or authorizes it. Treat it as one atomic release edit, not as an isolated patch:

1. Lock the approved title, judgment, facts, numbers, dates, author experiences and the 参考文章 block. If any of those must change, reopen the relevant approval instead of hiding the change inside a style pass.
2. Produce an AI-flavor report first; change only confirmed problem sentences. A high count for an ordinary word is a clue, not a reason to replace every occurrence, because blind synonym replacement damages meaning and voice.
3. Re-run the language specialist's no-new-facts check and `audit_draft.py`; passing the script remains only a floor.
4. Re-run the `--ready-dir` export above; it replaces the ready copy and prints the new SHA-256.
5. Search the publishing kit and image task for old sentence prefixes, quote lines, summaries and captions; update only affected fields. Write the new article hash into the task file and parse the structured file to verify it remains valid. If the kit's needs changed, re-bind the kit through the visual Skill's ready-article entry (its `--bind-kit` step); it refuses the old binding otherwise.
6. If screenshots, illustrations or layout already exist, mark affected anchors and outputs `to re-check`; if they do not exist yet, keep the task synchronized without pretending visual work is complete.
7. Verify the article title still matches the file name and that the article hash equals the asset-plan hash before reporting completion.

**Pitfall:** Never report a post-approval polish as complete after editing only the Markdown: stale quote lines, anchors or hashes send the visual and publishing stages to the wrong text.

## Make every delivery openable

Anything the author must read is either pasted in the chat or delivered as a link or path the author's own tool can open with one click. Find out how the author's tool opens files (some chat apps open only files inside their own workspace) and deliver in that form. A file the author cannot open counts as not delivered.

## Cleanup at the close

When the article is delivered, run `export_article.py --check` on the ready copy once more, then move empty files, files that contain only an error, and intermediate outputs that will not be used again to the system trash (never delete permanently). Keep: the seed (original and confirmation), the judgment card, the outline, every version of the body, the writer and review records, the review sheet, the feedback candidates and the publishing kit. List what was moved in the closing message. In testing, one article left 25 process files, many of them empty.

## Evidence screenshots

Screenshots are evidence, and the writing step knows best which page and which sentence each one proves; pages also change (view counts move, posts are edited). So the writing step captures them.

1. **Record while researching.** Every piece of evidence in the research pack and the fact table carries its link and the exact sentence quoted. When the fact table is locked (approval 3), mark the entries that need a screenshot. Capture from that list; never re-search for the post. In testing, most of 29 lost minutes went to finding posts again.
2. **When.** After approval 3, as a separate job that never blocks drafting or delivering a draft. If your tool can run work in the background, run it there; read results as soon as they arrive.
3. **How.** Use the visual Skill's capture script, never an ad hoc script: only its script writes the capture record (time, source link, file fingerprint) the visual entry needs, and its checks catch blank and cut-off images. Framing, sharpness, hiding sticky bars, scroll offsets and the no-frame rule live only in the visual Skill's article asset handoff reference; follow that. Without the visual Skill or a browser, deliver the list and mark every item "待补截" (to capture).
4. **Time limits.** Before the first capture, check that the browser window is visible (some browsers render nothing to screenshots while in the background), and try one capture of a simple page. Give every attempt a time limit of about one minute; never wait without one. Use the attempt limit the visual Skill sets for its capture script (do not invent a second number here); a capture the script calls a success but that fails your own look (step 5) counts as a failed attempt. When the limit is reached, stop, write a manual handoff (which link to open, which part to capture, how, where to save it, the file name) and carry on with everything that does not depend on it. In testing, one attempt waited 16 minutes and four retries in a row all failed because the browser window was in the background.
5. **Open every image.** A script's "success" is a floor. Open each image and check it is not blank, cut off, covered by a floating bar, or showing the wrong post. Fix it on the spot; a fixed image counts only once it is back in the article's own image folder and the kit, with one line saying who fixed what and when. A fixed image left in someone else's workspace is not fixed. In testing, a blank image and two cut-off ones went unnoticed, and the corrected versions stayed in another agent's workspace.
6. **Foreign-language screenshots.** A screenshot readers cannot read (for example a Japanese article for Chinese readers) does not go in the article. An English post may stay, with one Chinese sentence in the caption saying what it shows.
7. **Numbers that change.** Views, plays and likes are re-measured on the day the article is published, and their screenshots are re-captured that day so the picture and the text agree; mark them "发稿当天重截" (re-capture on publishing day) in the list. In testing, the image showed 792,000 views while the text said 796,000.
8. **Save** originals in the process folder's evidence-screenshot folder; for each, record the source link, capture time, the sentence it proves and the paragraph it goes after.

## Keep the kit true after every new version

Once an image list or kit exists, every new body version is followed by one pass over it: does each anchor (the sentence an image goes after) still exist in the new version, do the subheads named in the kit still exist, and does every status line match reality (how many images are done, which are broken, which wait for capture)? Update only what changed. In testing, the image list still pointed at version 8's subheads after version 12 had changed them, and the kit said "6 images done" while one was blank and two were cut off.

## Hand off to illustration and layout

When to hand off: the article needs images, the editor-in-chief review has confirmed it is the commissioned article, and the author has approved it at approval 4.

**Approved articles go through the visual Skill's ready-article entry**, the path tested end to end with this Skill:

1. Write the ready copy with `export_article.py --ready-dir` (section "Ready folder"), then the paired publishing kit beside it with its two-path header, and the image task file in the process folder: its `source_md` is the ready copy and its `article_sha256` is the hash the export printed. Agents maintain the task file; authors never fill in structured files.
2. Bind them through the visual Skill's ready-article script (it belongs to that Skill; find it there): `--article <ready copy> --kit <paired kit> --bind-kit`. Then use the same script for every later step: `--prepare-only` when no browser is available, or its full run for screenshots and the trial layout. If that Skill documents different options, follow that Skill.
3. Pass only these explicit paths. Never let a downstream step pick the newest draft or the newest file in a folder.
4. When the kit's image needs change, update the task file and bind again; when the article changes, follow "A narrow polish after approval 4" below.

**Drafts that are not approved yet** may get a trial layout only: export with `export_article.py --source <selected.md> --output-dir <new-directory>` (the exact bytes before the editor-notes marker plus a hash receipt, the draft unchanged and not declared approved), then the visual Skill's general article pipeline script with that export. Say plainly that it is a trial of an unapproved draft.

The shared machine contract (capture provenance, pending-capture fallback, separate phone and human acceptance states) lives in the visual Skill's references (its article asset handoff and ready-folder contract); read them for image requests and handoff. Keep the image needs in the kit: paragraph position, the point each image helps the reader understand, the suggested kind (AI illustration, source screenshot, real photo), and real source links. The writing step captures evidence screenshots (section "Evidence screenshots"); AI illustrations, information graphics and covers stay with the visual Skill. If no visual Skill is installed, deliver the needs and the explicit source identity without claiming asset production or publishing.

## One-page publishing kit

Made only after the editor-in-chief review confirms this is the commissioned article and the author approves at approval 4.

An article ships as three files: the writing original with its editor notes, the exported article, and the image task file defined in the visual Skill's handoff contract (agent-maintained; each image names the paragraph it follows, what it helps the reader understand, and its kind: AI-generated visual, evidence screenshot, real photo, or program-rendered graphic). Alongside them, give the author one human-readable page, the publishing kit, saved in the ready folder beside the body (see "Ready folder") with the paths of every image, screenshot and the image task file in the process folder. It is a view of the same data, not a second task list. It has these parts:

1. **Images.** A table with a column headed 放在哪段后面（段落开头） ("after which paragraph", quoting that paragraph's opening words exactly, so `--check` can find it). For every screenshot: the source link, exactly which part to capture (only the part the article comments on, never the whole page), the paragraph it goes after, what it is quoted to show, the text credit (author, platform, date), and its status: 已截好 (captured, with its path), 待补截 (to capture) or 发稿当天重截 (re-capture on publishing day). Permission status in its own line. The visual Skill checks this list first and captures what is missing; the author can also capture with their own tool. Never substitute an AI-generated image for a screenshot. Screenshots carry no frame of their own; the layout template adds frames to all images in one style. Data charts are drawn by program, never by an image model. (In recent copyright cases, "source credited", "non-commercial" and "low readership" were not accepted as defences; summaries only.)
2. **Captions** carry the text credit only, never a link.
3. **Video.** Video shows a moving result better than a still. A WeChat Official Account article can embed only Channels videos or uploaded videos and cannot carry external links. Work down this order for each video, judging each case: (1) a Channels copy exists: embed it; (2) none, and the video suits uploading: download and upload it; (3) uploading does not suit (copyright, the creator's stance, quality, length): a screenshot with a text credit; (4) a screenshot does not suit either: no image. List each video with its link, length and resolution, whether it can be downloaded (probe only, do not download), and the suggested step with the reason. Whatever is unclear goes to the author to decide.
4. **Cover and share image**: not written here. The visual Skill makes real sample covers for the author to choose from; this kit supplies only the title and the quote lines below. In testing, cover directions written in the kit were improvised, unclear to the author, and one used another creator's video frame without a permission check.
5. **Title, 3 summary candidates, 3 quote-line candidates** (for share cards and social posts). Each line passes `audit_draft.py --card` and the AI-flavor audit before the author sees it; quote lines are where slogans and mirrored couplets creep back in.
6. **Facts still to check** before publishing, including numbers to re-measure on publishing day, and where the verification list is.
7. **For the author to confirm personally**, never chosen by the agent: a title marked "tentative" because the author was away when it was picked; whether to declare originality; whether to tick the AI-generated-content declaration; any open visual choices.
8. **Next handoffs**: what goes to the visual Skill and to layout. When the article changes after images or layout exist, mark them "to re-check".
