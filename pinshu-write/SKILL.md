---
name: pinshu-write
description: "Use when the user wants to find a topic for, write, title, outline or review an opinionated Chinese long-form analysis article (WeChat Official Account style) for a business, brand-marketing or applied-AI account. Triggers include 'write a Pinshu article', 'turn this event into an article', 'write an analysis piece for our account', 'help me find a topic', 'review this draft'. Not for faithful transcripts (pinshu-transcript), course study guides (pinshu-distill), breaking-news flashes, celebrity or social gossip, or any account whose profile says AI must not draft it."
---

# Pinshu Writing

## Provenance and maintenance

- Original status: Pinshu original (`original`). Owner and maintainer: Aidan (Pinshu). Only the maintainer edits these files; writing sessions propose feedback candidates.
- Version: 3.3.0 (2026-10-19), public preview.
- 3.3.0: select the title/opening hook before the line; add attraction and originality reviews; retain force while checking facts and copying; compare revisions with the preceding version.
- 3.2.0: carry the reader's shift through planning, drafting and review; make research briefs precise; distinguish optional revision advice from hard factual corrections.
- 3.1.0: retain all review roles, revise whole sections with the same writer, and enforce final length and paragraph gates.
- 3.0.0: pass the complete seed, plan one coherent line, and read each draft as a whole before review.

## 中文使用入口

用于把作者已给的选题、灵感、文章或材料写成中文商业分析长文，也支持找选题、标题开头候选与审稿。先读用户自己的配置和账号画像；作者决定选题、主线、开头与定稿。保留四个确认停点、跨厂商多角色审稿、同一写手整节修改、机械检查与定稿导出。以下主流程与参考文件保留与本机通用规则相同的英文规则及中文提示词；不附带发布者的账号画像、私下反馈或维护档案。

## What this Skill is for

**Reach comes first.** An article nobody opens helps nobody, and a new account with no followers gets readers only from strangers who see it pushed or forwarded: every article is first judged on whether a stranger scrolling past opens it, reads on and passes it on (the title and opening must earn attention). Facts, structure and rules serve that; none of them may be used to file the edge off a piece.

It helps the author think the idea through first (the author is the first reader), and turns it into an article a busy reader enjoys reading to the end, finds useful and wants to pass on: one clear line, a person thinking out loud, cases that come in because the reader wants them, and facts that hold. The AI researches, checks and drafts; the author decides the topic, the line, the opening and whether it ships; a person publishes under the platform's AI-disclosure rules. Output is Simplified Chinese unless the account profile says otherwise.

## What it needs

Python 3.9 or newer, no third-party packages. Web access, a second model vendor, the visual Skill `pinshu-visual-system` and a browser are optional; each has a named fallback, and a skipped or downgraded step is written down as such, never reported as done.

## Start

1. Run `python3 scripts/check_env.py --config <your config>` the first time. Read the configuration (`pinshu-write.yaml` in the author's writing folder, or the path the author gives; format in `templates/config.example.yaml`) and the account profile; the profile wins over this Skill on topics, reader, length, banned words and titles. Minimum to begin: the account and its reader; ask if either is unknown.
2. Enter where the author is:

| The author brings | Enter at |
|---|---|
| Nothing ("find me a topic") | 1 Topic: scan, three topics, stop 1 |
| An idea, topic, link or article, any length | 2 Research, the author's words kept whole as the seed |
| A line or a title | 3 The line, then 4 |
| A draft to look at | 6 The read and the fact check |
| Comments on a draft | Revision by size (`references/6-deliver.md`) |
| The author's own hand edit of a draft | Edit pairs (`references/write.md`, "After 定稿") |
| An old article to rewrite, continue or restyle | Read it whole; if the author did not say what to change, ask once: structure, tone, or continue; then 3 The line |

## The route

One route for every article, four stops, every reviewing role kept. Each article has one folder (naming in `6-deliver.md`, "Folders and names") holding the author's verbatim words, the material pack (facts and cases with sources, started in step 2) and the decision log.

| Step | What happens | Details |
|---|---|---|
| 1 Topic, **Stop 1** | Only when the author brought no topic: scan, offer three, the author picks one | `1-topic.md` |
| 2 Research and counter | Facts with links and quoted sentences, cases with sources, the author's real experiences from the library, closest published articles; the counter role argues the other side | `2-research-and-counter.md` |
| 3 The hook and the line, **Stop 2** | First the hook: two vendors write title-and-opening candidates with different hooks, the organizer shows the author four, the author picks one and the one sentence the whole piece says (`write.md`, "The hook"); then the core question, the reader's shift ("读者原来以为……看完知道……"), the opening scene, then one plain paragraph on how the piece moves from first paragraph to last with what each step stands on, and three titles that each carry something the reader does not know; the structure editor checks the line first; the author approves or reshapes it | `write.md`, `stops.md`, `prompts.md` |
| 4 Draft | One writer (a second when the author asks), briefed with the seed whole, the chosen title and opening, the line, what makes it gripping, exemplars of the type, the author's edit rules and the material pack; the organizer reads the draft whole and runs the gates | `write.md`, `models.md` |
| 5 Opening, **Stop 3** | The first 300 characters to the author: does the first sentence make sense, would you read on | `write.md`, `stops.md` |
| 6 Review | Managing editor (two vendors), reader, attraction reader, expert, facts and risk, language and flow, the good-article check, and the originality check when the seed is someone else's article, review together; one merged list in which only hard facts and copying force a change | `5-review.md`, `prompts.md` |
| 7 Revision | The same writer rewrites whole sections once from the merged list, the line and the full text; the organizer reads it whole and lays its title, opening and three sharpest lines beside the previous version's, sending back a version that went flatter; the gates again; the after-revision read and the seed check run once each | `write.md`, `5-review.md` |
| 8 Final, **Stop 4** | The author reads it all, picks the title, says 定稿 or edits; export, publishing kit, images; the author's hand edits go into the edit rules | `stops.md`, `6-deliver.md`, `write.md` |

**Gates** (`scripts/audit_draft.py --length 2000-2500 --hard-max 2700`, or the configuration's length): a blocker stops the draft until fixed. One-sentence paragraphs in a row, dashes, banned words and the other blocker rules block every draft. The hard maximum blocks the revised and final text; on the first draft add `--first-draft`, which turns it into a reminder that heads the merged list. A first draft may be a little over, not far over; review, revision and trimming must bring it back inside the range.

Besides the stops, ask the author when: the account or reader is unknown; there is no topic, no web access and no configured source; research overturned the core (said at stop 2); a draft says something about the author that his words do not; or the next action spends money, overwrites a file or re-exports.

## The roles

| Role | Does |
|---|---|
| Organizer | Runs the route, builds the material pack, writes the line, reads every draft whole as a reader first, merges the findings, keeps the decision log |
| Writer | Writes the article from the brief, and rewrites whole sections once from the merged list |
| Counter | Holes and counter-evidence in the judgment, with the seven questions |
| Structure editor | The line before stop 2: does it move, does each part join the next, do the titles carry something new |
| Managing editor | The finished draft as a whole: a map of every section first, then repeats, set-ups never paid off, cases, the most valuable part, the ending, gaps; two vendors, no verdict on publishing |
| Reader | Where a reader outside the trade, who uses AI at work, gets stuck; what they remember; where it jumped |
| Attraction reader | A stranger scrolling a phone: would they open it from the title, were they caught in the first three lines, where they would leave, which line they would forward, what went soft |
| Originality check | Only when the seed is someone else's article: where the draft sits too close to it (scenes, frame, signature phrases, data) |
| Expert | Is it right: what a marketing, finance or applied-AI practitioner would catch, each with a source |
| Facts and risk | Hard facts against sources and the author's words (who, what was done, numbers, quotes, outcomes); what may not be said; fitting feelings and detail are not faults |
| Language and flow | Machine flavor and wording; a read from top to bottom marking every place the reading jolts |
| Good-article check | The account's own standard of a good article, check by check, no overall verdict |
| After-revision read | Faults the revision brought in: repeats, sentences that do not join, lost sources |
| Seed check | The author's words present, the article the author asked for, the author's key words still there |

## Rules that do not bend

- **Reach comes first; only facts and copying force a change.** A finding about a hard fact (`5-review.md`, "Facts and risk") or about copying someone else's article must be fixed. Every other finding is advice: the organizer adopts it when it makes the piece more gripping or easier to read, and says in the merged list why it was or was not adopted. No rule, standard or reviewer is used to turn a sharp line into advice or a stand into a hedge.
- **Someone else's article is a seed only.** The body never names it or its author, and takes none of its scenes, frame, signature phrases or data; what may be learned from it is how it grips. Its facts are researched again from their own sources or left out.
- **The author's latest words win.** When the author's words at different times disagree, follow the most recent and mark the older one "已改" in the decision log.
- **The seed is the author's words, kept whole.** It goes to the writer verbatim, doubts and attitudes included. Research sharpens claims inside its direction and never changes the direction, the article type or the reader; when evidence overturns the core, the author decides.
- **The organizer passes the author's words, not translations of them**: no sample sentences, no quotas, no remark turned into a rule for every section.
- **The organizer reads every draft whole before any script or reviewer**, and fixes a draft that reads badly at its root, not by patches.
- **The organizer does not write reader-facing Chinese**, unless the author names it as writer or no writer model can be reached; it may correct a single wrong fact.
- **The author's experiences, clients and data come only from the author's own words, the decision log and the library**; a gap is written "[待确认]" and asked; something the draft says about the author that is not there is asked, never ruled invented.
- **Every claim carries its origin**: a named source, the author's material, or an inference worded as one.
- **Exemplars come from mature writers of the same article type**, never from the account's own old articles; the author's voice is learned from his edit pairs.
- **The ready folder is written only by `export_article.py`, and only after the author says 定稿.** "可以", "继续", "还行" and "满意" mean keep working.
- **The author chooses the WeChat collection or column.**
- **A failed or stalled step is reported as failed or stalled**; never report the article done while a step has failed.
- **Revisions are sized**; small ones never rerun the route (`6-deliver.md`).
- **The Skill stands alone.** A workbench, dashboard or paid data service only speeds it up.

## References

| File | Read it when |
|---|---|
| `references/1-topic.md` | Step 1: seed rules, the scan for three topics |
| `references/2-research-and-counter.md` | Step 2: research, the material pack, the counter role and the seven questions |
| `references/write.md` | Steps 3 to 8: the hook, the line, titles, the writer's brief, the opening, how the organizer reads, the whole-section revision, the author's edit rules |
| `references/stops.md` | Writing the message for any of the four stops |
| `references/models.md` | Choosing models, calling another vendor, watching a call (`scripts/run_watched.py`) |
| `references/6-deliver.md` | Revisions by size, export, publishing kit, screenshots, cleanup, after publishing |
| `references/3-structure.md` | 2.x, off the route: the old outline rules, kept for comparison; its "Titles" section is still pasted into prompt 4 |
| `references/4-writing.md` | 2.x, off the route: the old brief and after-check; `audit_draft.py --rules` still prints its Chinese rules |
| `references/5-review.md` | Steps 6 and 7: role cards, merging the findings, severity, feedback candidates |
| `references/prompts.md` | The prompts for the counter, structure editor and every reviewing role (prompts 3 to 14), plus title/opening candidates (15); prompts 1 and 2 are replaced by the brief in `write.md` |
