---
name: pinshu-write
description: "Use when the user wants to find a topic for, write, title, outline or review an opinionated Chinese long-form analysis article (WeChat Official Account style) for a business, brand-marketing or applied-AI account. Triggers include 'write a Pinshu article', 'turn this event into an article', 'write an analysis piece for our account', 'help me find a topic', 'review this draft'. Not for faithful transcripts (pinshu-transcript), course study guides (pinshu-distill), breaking-news flashes, celebrity or social gossip, or any account whose profile says AI must not draft it."
---

# Pinshu Writing

## Provenance and maintenance

- Original status: Pinshu original (`original`). Owner and maintainer: Aidan (Pinshu).
- Version: 4.0.0 (2026-10-25), public preview. 4.0 照真稿测出的问题修改，修改后尚未跑过真稿验证。
- Writing sessions may propose feedback candidates; only the maintainer changes the package. Maintainer-only histories, private feedback and local project records are not distributed.

## 中文使用入口

用于把作者给出的选题、灵感、文章、材料或初稿写成中文商业分析长文，也支持找选题、标题开头和审稿。先读使用者自己的配置与账号画像；默认写作标准随包提供在 `references/good-article-standard.md`，配置可以指向团队自己的替代标准。作者决定选题、判断、标题、大纲、开头和是否定稿。公开版保留十步主流程、三道闸门、相互隔离的审稿位置、同一写手整节修改、机械检查与定稿导出；不附带发布者的账号画像、私下反馈、维护档案或本机模型配置。

## The master gate

Above every rule in this Skill: 利他, the root set by the bundled good-article standard (`references/good-article-standard.md`, 第一节): from the reader's side, what the reader takes away for the minutes spent. Before writing it takes the form of the standard's 动笔前先答三问 (第十六节): why does the reader open this article, where does the reader decide to continue, and what does the reader take away. The Skill keeps no set of its own. When the writer or a reviewer is unsure, return to these three first; steps that cannot answer them by nature (research, the fact sheet, export) do not stop on them. A number found in research answers "which of the three does it serve?" before it goes into the article; research itself finds the matter out in full and is not led by these three (`references/2-research.md`).

## What it is for

Articles a busy reader opens, reads to the end and passes on. A new account with no followers gets readers only from strangers who see it pushed or forwarded, so reach comes first; facts, structure and rules serve reach and never file the edge off a piece. The author decides the topic, the title, outline and opening, and whether it ships; models do the work in between. Output is Simplified Chinese unless the profile says otherwise.

An optional account workflow document (configuration `workflow_doc`) may explain why a team's route and roles are shaped a certain way. The good-article standard (configuration `good_article_standard`, default `references/good-article-standard.md`) says what a good article is. This Skill holds the steps and points at the standard rather than restating it.

## Start

1. First time on a computer: `python3 scripts/check_env.py --config <config>`. Read the configuration (format in `templates/config.example.yaml`), the account profile and the good-article standard. Minimum to begin: the account and its reader; ask if either is unknown.
2. Enter where the author is:

| The author brings | Enter at |
|---|---|
| Nothing ("find me a topic") | Topic scan (`references/1-topic.md`), three seeds, the author picks one |
| An idea, a link, someone else's article or title, any length | Step 1, the author's words kept whole as the seed |
| A title or an outline | Step 3 |
| A draft to look at | Step 6 |
| Comments on a draft | Revision by size (`references/6-deliver.md`) |
| The author's own hand edit of a draft | Edit pairs (`references/write.md`, "After 定稿") |

When the author only says "help me write" and does not say what he has, ask once, with four plain choices and not the whole table: 还没题，帮我找；我有个想法；我有篇别人的文章；我有初稿要改. Then enter by the table.

## The route: ten steps, three gates

One folder per article (`references/6-deliver.md`, "Folders and names") holding the author's words verbatim, the material, the decision log and every brief and output.

| Step | Who | What happens | Gate | Details |
|---|---|---|---|---|
| 1 Ask the author | Writer asks, author answers | One question at a time: his point read back, the vaguest word, who it is for and where they get stuck, what happened to him, where the reasoning jumps. His words written down first; the writer never answers for him | | `write.md` |
| 2 Research, then think it through | Research models, then the writer | The matter found out in full, not led by the three questions; then, with the material read, one page of thinking-through and the standard's 动笔前先答三问 (第十六节) as sentences someone could argue with | **Gate 1**: the author says it is thought through | `2-research.md`, `write.md` |
| 3 Title, outline, opening and first section | Writer, plus a second vendor for title and opening candidates | Built from the three answers and the material, a section standing on a case uses one that passes two checks (matches the judgment; the reader meets it in his own work), and may stand instead on the author's experience, his reasoning, an everyday scene or a hypothetical example; exemplars by mature writers found and offered; how the piece moves in one paragraph; the opening and first section written in full | **Gate 2**: the author reviews all three and picks the exemplars; the last place anything is overturned, except by review's two stops (step 6 grading, step 8 建议推翻) | `write.md`, `stops.md` |
| 4 The rest | Writer | Reads the standard's 利他 paragraph (第一节), the picked exemplars and the standard's 第五、九节 first; writes to the end, reads it through and fixes by the paragraph. Core changed after the first section: stop, back to gate 2 | | `write.md` |
| 5 Fact sheet | Script or another model, never the writer | Every number, name, company, date, quote and citation in the draft pulled into one sheet | | `5-review.md` |
| 6 Review | Expert, fact checker, reader at once; then the organizer; then the editor | The three run on the first draft; two re-checks (补核) of what they flagged; the organizer grades every finding by size; the editor's first pass | A finding graded 动骨架 stops for the author before the editor runs | `5-review.md`, `prompts.md` |
| 7 Revision | Writer | One round: fact must-fixes, answers to the expert, the editor's items and the reader's spots together; a change list | | `write.md` |
| 8 Facts again, the editor's second pass | Fact checker, editor | Facts on new and changed lines only; the editor checks whether each first-pass problem is gone and what the revision broke | 建议推翻 goes to the author | `5-review.md` |
| 9 Final | Author | Reads the revised draft; decides whether it ships | **Gate 3** | `stops.md` |
| 10 Edits, export, review | Writer, organizer | The author's edits, export after 定稿, every five articles a look back | | `6-deliver.md` |

**Gates in the script** (`scripts/audit_draft.py --length 2000-2500 --hard-max 2500 --banned-file <the configuration's banned_words_file>`): One-sentence paragraphs in a row, dashes, banned words and the other blocker rules block every draft; on the first draft add `--first-draft`, which turns the length maximum into a reminder.

Ask the author besides the gates when: grading puts a finding at 动骨架, or the editor's second pass says 建议推翻 (`stops.md`); the account or reader is unknown; there is no seed, no web access and no configured source; research overturned the core (bring it to gate 1); a draft says something about the author that his words do not; or the next action spends money, overwrites a file or re-exports.

## The roles

| Role | Stands where | Delivers | Gets only |
|---|---|---|---|
| Writer | The whole article, one agent from step 1 to the last edit: the session that talks with the author, running on the configuration's `writer` model, with no handoff in between; another authorized session may dispatch research, review and fact checks, handing every file over verbatim (`references/models.md`) | The author's points, the thinking-through page and three answers, title, outline, opening, the draft, the revisions | Everything |
| Editor | The editing desk, in two passes | Pass one: ten actions in three groups plus a comparison with the exemplar, each item with its group, place, problem and how to fix. Pass two: whether each pass-one problem is gone; 过, 退回写手 or 建议推翻 | Pass one: the first draft, the exemplars the author picked, the standard's sections named in `5-review.md`, the edit rules still in force; never the outline, the three answers or anyone's findings. Pass two: its pass-one list, the revised draft, the writer's change list, the reader's spots, the changes outside the change list (found by the organizer) |
| Reader | A feed, knowing nothing | Per section: read on or not, why, the sentence it stuck on, what the section said, a guess at the next, and the sentence it does not believe or accept, quoted, with its reason as its own reaction; at the end what it remembers, what it would pass on to whom, how it would retell it, and what in its own work it could use the argument on and where it stops working | Who it is and the difficulty it is stuck on; the title, then one more section per call; nothing else |
| Expert | A practitioner of this topic's field, named at step 1 | The core judgment and a verdict (站得住 / 说满了 / 站不住), a case table, the strongest counter-argument, where the author sounds like an outsider, a 交核查官 column; every item with a source | The draft, the reader in one sentence, its field, the standard's 第十七节 items 2 and 5 |
| Fact checker | The fact sheet | Pass one: every point marked 有出处 / 对不上 / 待补 / 查不到 / 无需核. Pass two: copying, and sentences that may not be publishable. Two re-checks (补核) before grading | Pass one: the sheet only. Pass two: the draft, the seed and same-topic articles, the standard's 第十五节, the platform |

Positions stay apart because each holds different information; four agents reading the same draft with the same standard would agree with each other, not check each other. The writer reads its own draft through and rewrites by the paragraph (`write.md`, step 4), and checks what can be counted (the script, the countable items of the standard's 第十八节); it never plays any of the four positions. Models per role: `references/models.md`.

## Rules that do not bend

- **How to write lives in the standard.** This Skill and its prompts point at the standard's sections; a writing rule restated here is a fault to remove. When two rules disagree, ask the author; never pick one.
- **Only hard facts and copying force a change.** Hard facts include 查不到, 对不上 and 待补; the expert's verdict is graded by size (`5-review.md`, "Grading"), and its other sourced findings get a change or a reason. Every other finding is advice. Findings about the reader (does not care, does not know where to start, cannot understand) are listed apart, and one not adopted gets a reason the author sees at gate 3. Each adopted cut or narrowing carries one line: does the reader now want to read it more, or is it only more careful? Removing the sharpest number or scene waits for the author.
- **Someone else's article or title is a seed only.** When the author picked it for its title, the question that title asks is the question the article answers. The body never names it or its author and takes none of its scenes, frame, signature phrases or data; its facts are researched again or left out.
- **The seed is the author's words, kept whole**; research sharpens claims inside its direction. When evidence overturns the core, the author decides. The author's latest words win; mark the older one "已改" in the decision log.
- **The author's experiences, clients and data come only from his own words, the decision log and the library**; a gap is "[待确认]" and asked.
- **The ready folder is written only by `export_article.py`, and only after the author says 定稿.** "可以", "继续", "还行" and "满意" mean keep working. The author chooses the WeChat collection.
- **A failed or stalled step is reported as failed or stalled**, never as done. A draft whose steps 6 to 8 did not all run is a first draft and is called one, never a final.
- **The Skill stands alone.** A workbench, dashboard or paid data service only speeds it up.

## dbs tools the writer may call

Outside the ten steps: no article has to run any of them. Each is a Skill of that name in the shared Skill folder. What one returns is material or a second opinion; the author and the writer decide, and none stands in for one of the four review positions.

| When | Tool | Call it for |
|---|---|---|
| Step 2, after asking the author, before the thinking-through page | `dbs-standard-answer` | A puzzle in the seed: which trades, fields and writers have worked it through, with cases that succeeded, failed or cut against it |
| | `dbs-deconstruct` | A word in the seed nobody can pin down: draw its edges, or find that the word itself is the trouble |
| | `dbs-theory-grounding` | An experience-based judgment: does it hold, what theory backs it, where it stops applying (the page's "why it holds") |
| | `dbs-chatroom` | The author wants to hear sides argue it out; costly (about 80,000 tokens in one test) |
| After the thinking-through, before the title | `dbs-content-value` | Is the topic worth writing for the reader: whom it draws, whether the opening holds, what the reader gains (the part the author weighs most), reach and business value |
| | `dbs-jtbd` | What the reader is trying to move forward in his own work with this article |
| After the draft | `dbs-resonate` | Where it misses its reader; lay it beside the reader position's record |
| | `dbs-ai-check` | A diagnosis of AI flavor, nothing else |
| | `dbs-content-risk-check` | Before publishing: risk, sentence by sentence |
| After publishing, and other formats | `dbs-spread` | Why a piece that spread did |
| | `dbs-content-value` | Why a piece was read little |
| | `dbs-title-cover-intro` | Title, cover and opening when the article becomes a 小红书 note or a Channels video |
| | `dbs-video-extract` | A video's transcript, taken as a seed |
| | `dbs-benchmark` | Accounts to benchmark against |

## References

| File | Read it when |
|---|---|
| `references/write.md` | Steps 1, 3, 4 and 7 and the end of step 2: asking the author, the thinking-through and three questions, title and outline, writing, revision; the fallback writer's brief; edit pairs |
| `references/2-research.md` | Step 2: the matter found out in full, the material pack |
| `references/5-review.md` | Steps 5, 6 and 8: the fact sheet, the three positions and the re-checks, grading, the editor's two passes, merging, facts again |
| `references/prompts.md` | The briefs for the four positions (the editor's two passes, the fact checker's passes and re-check), the fact-sheet extraction and the fallback writer's revision |
| `references/stops.md` | Writing the message for a gate or the topic scan |
| `references/1-topic.md` | No seed: the topic scan |
| `references/models.md` | Choosing and calling models, watching a call |
| `references/6-deliver.md` | Revisions by size, export, publishing kit, screenshots, after publishing |
| `references/good-article-standard.md` | The bundled public writing and review standard; a team may override it in configuration |
