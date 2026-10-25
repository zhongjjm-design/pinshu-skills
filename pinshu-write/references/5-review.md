# Steps 5, 6 and 8: the fact sheet, review, facts again

Each position holds different information, so their judgments are independent; that is the whole reason for having four. Hide from each what its job must not see, and give each only what it needs.

The order, every time: the writer's first draft; the fact sheet (step 5); expert, fact checker pass one, fact checker pass two and reader, sent at once on that same draft; the two re-checks (补核); the organizer grades; the editor's first pass; the writer's one revision (step 7); facts again and the editor's second pass (step 8); gate 3. The organizer is the writer's own session, or a stronger session working beside it that hands every file over verbatim (`models.md`): writing, the writer is the author; grading and merging, the organizer runs the route.

## Iron rules

1. **Every position comes from a vendor other than the writer's** (`models.md`).
2. **Positions flag; they never rewrite.** Each cites the place (paragraph number, sentence under 60 characters) and gives a direction for the fix that invents no facts or experiences. One exception, the editor's first pass: an item may carry one sample sentence, marked "这是样子，不是必须照抄"; it holds only facts already in the draft (checked against the original sentence, every added name, title, number or cause removed), uses no dash, no single "不是……而是……" sentence and none of the standard's 第十五节 item 7 banned words, and only splits sentences or reorders them, never removing a specific number, person or practice (a name the citation rule says not to carry is the one exception, `write.md`, step 3, item 5).
3. **Findings about the author's own experiences or the article's stance go onto the author's sheet** for gate 3; nobody deletes or softens such a passage on their own.
4. **Launch each call clean**: no author identity or preferences, no other position's findings, the author's global settings kept out (`models.md`, "Calling another vendor").
5. **Only hard facts and copying force a change.** Every other finding is advice; reader findings are listed apart and each needs a change or a reason (`write.md`, step 7). The expert's verdict is graded by size ("Grading"); its other sourced findings get a change or a reason.
6. Nobody is asked whether the article is worth publishing or will be forwarded; that is the author's call at gate 3. The reader's last call says which passage it would pass on to whom: that is its own reaction, not a verdict on the article.

## Step 5: the fact sheet

Pulled from the draft by a third party, never by the writer: a writer that invented a number would leave it off a list it made itself.

1. Run `python3 scripts/extract_facts.py <draft> --out <folder>/tmp/fact-sheet.md`. It lists every sentence holding a number, a date, a percentage, a quote mark, a colon after a verb of saying, or a Latin-script name, with its paragraph number.
2. Send the draft to one model with prompt "Fact sheet: names" (`prompts.md`) to add the people, companies, organizations, studies and events the script cannot recognise. It only lists; it judges nothing.
3. Merge both into one sheet with four columns: 内容 | 原句（段落号）| 出处 | 状态. The 出处 and 状态 columns stay empty for the fact checker. A name line carries its whole sentence and paragraph number; a sentence appears on one line only, with its names merged into that line rather than given lines of their own.

Done when every number, name, company, date, quote and citation in the draft is a line on the sheet, each with its whole sentence and paragraph number.

## Step 6: review

### The three positions on the first draft

Expert, fact checker pass one, fact checker pass two and reader are sent at the same time, each in its own call or calls, from vendors other than the writer's. The editor waits for grading.

| Position | Gets only | Never gets | Delivers | Done when |
|---|---|---|---|---|
| Reader | Who it is (the profile's reader in one sentence; the difficulty this topic's reader is stuck on, one sentence from the first of the three answers; how it scrolls), the title alone, then the title plus one more section per call, in order | Anything about the author, the standard, the purpose, or what comes later | Title call: would I open it, and why. Each section: read on or not; why; the sentence it stuck on, verbatim; what this section said in one sentence; a guess at the next section; the sentence it does not believe or accept, verbatim, with its reason as its own reaction (or "none"). After the last: what it remembers, which passage it would pass on to whom with what line, how it would retell the piece, what in its own work it could use the argument on and where it stops working | Every section has all six, and the last call all four |
| Expert | The draft (title, subheads, body); the profile's reader in one sentence; its field from step 1 ("专家身份", `write.md`); the standard's 第十七节 items 2 and 5 | The fact sheet, the standard's 第十五节, the platform, the three answers and outline, the material pack, the author's identity, any other position's findings | The core judgment in one sentence and whether it is two judgments; a verdict per judgment: 站得住, 说满了 (with the condition that would make it hold, and whether the title's answer narrows or changes), 站不住 (with the counter-example and why no condition saves it); a case table (what the draft says happened, whether the reason is written, the conditions for the reader's own business); the strongest counter-argument and whether the draft answers it; where the author sounds like an outsider (terms used wrongly, wrong analysis, outdated claims, cases proving something else, one person's words stretched into a rule); vague wording carrying an accusation or key conclusion; a 交核查官 column for facts that do not match their sources. Every item with a source; no severity | All seven actions answered (`prompts.md`, "Expert") |
| Fact checker | Pass one: the fact sheet only. Pass two: the draft (title, subheads, body); the seed when it is someone else's work; the published articles research marked as the same topic, at most three in all; the standard's 第十五节 whole; the platform and content type | Pass one never sees the draft; pass two never sees the sheet, a summary of the argument, the three answers or the outline | Pass one: every line split into points (who with that year's title, when, how much with its basis of measurement, what was said, cause and sequence, order and degree), every point checked against a source, every line one of five statuses (有出处 / 对不上 / 待补 / 查不到 / 无需核, the line taking its worst point), a return list for lines missing their sentence or paragraph number, names that look invented. Pass two: copying in six checks (title and subheads, opening scene, order of sections, the source's own frame, phrases, metaphors, lines and data, naming the source or its author, the angle as a whole), each close passage quoted on both sides as 必改 or 可留; and sentences that may not be publishable in five fixed kinds, flagged and not researched: 名誉, 内部数据, 政策, 平台, 版权 | Pass one: every line has a status or is on the return list. Pass two: all six and all five answered, "未发现" where nothing was found |

The reader runs as one call per step: title; title plus the opening and first section; plus the next section; and so on to the end (five to seven calls). Each call is fresh, so the reader cannot know what comes next. Use a plain model rather than the strongest: a clever reader fills gaps the writer left.

What counts as a hard fact for the fact checker: who (with the title held in the year it happened), what was done, numbers with their basis of measurement, quotes, dates, outcomes, causes and sequence, "first" and other claims of order, whether an event happened. A source weaker than the sentence ("有" in the source, "很常见" in the draft) is 对不上. A fitting feeling, a scene or a tone that fits what happened is how a person writes and is not a fault. Promises keep their source's strength ("may" never becomes "will"). The author's experiences are checked against his own words; a gap is "[待确认]" and asked.

Where the fact checker and the expert divide: whether something is true and whether it may be written belong to the fact checker; whether it is professionally right, and whether vague wording can carry what it claims, belong to the expert. When both report the same "据说", the organizer merges them into one line, and on a fact the fact checker's re-check decides; the expert's report is a lead.

### Checking the expert's report and the reader's record

The expert's report is complete when it has the core judgment (one sentence, or two marked 两个判断), a verdict for each with its reason, a condition and "narrows or changes" for 说满了 or a counter-example with its source for 站不住, every case in the table answered, every item with paragraph, sentence and source, and the 交核查官 column apart. A verdict without a reason, a summary verdict ("整体专业", "论证扎实"), or 站不住 without a counter-example: run it again. Items about structure, voice or style mixed into its list: void those items and keep the rest; a rerun on the same model would mix them again. Two runs that still miss what should be there (two judgments not written out), or keep reporting structure or arguing with a quoted person: the brief needs changing; tell the maintainer.

The reader's one-sentence account of each section is laid against the outline (did this section get written as planned; a mismatch may be the draft's fault, not the reader's) and against the draft (did the reader add something the draft never said). Both go into grading; the outline itself never goes to the editor.

### Checking the fact checker's pass one

The organizer checks it, never the fact checker itself:

1. **Open five links.** From the lines marked 有出处 take one line of each kind (number, title, cause, basis of measurement, quote), at most five, never at random. Open the link, find the sentence, paste the source's sentence beside the line and mark it 一样 or 不一样. Only the 不一样 lines go to the author. For a kind marked 不一样, the backup model re-checks every line of that kind, not the whole sheet; lines the two checks disagree on go to the author.
2. **Scan the whole notes column.** A line marked 有出处 whose note says 但, 注, 大体, 基本 or 略有出入 has not passed; run `scripts/check_fact_notes.py <fact checker output>`.
3. **Check the table itself.** Every line has a status or is on the return list; every 对不上 and 待补 says what the source says and which point was not found; returned lines are checked again once completed.

### The two re-checks (补核)

The expert's 交核查官 column arrives after pass one has finished, so nobody would check it; pass two flags risks it does not research. Two re-checks close both, each sent as soon as its input arrives, each its own call, timed separately in the log. Grading waits for both.

1. **First re-check: the expert's leads.** The 交核查官 column, plus the counter-example the expert used for 站不住 as a line of its own, in five columns: 内容 | 原句（段落号）| 出处 | 状态 | 线索 (the expert's source, worded neutrally). It uses pass one's brief and question (does it match the source), split into points; the links in 线索 are opened too, and where they and the checker's own source differ the line is 对不上.
2. **Second re-check: is there public ground.** Only the 名誉 and 内部数据 lines from pass two, in the same five columns, 线索 holding any source the draft gives; prompt "Fact checker: second re-check". The other three kinds are not re-checked: 政策 goes back to the writer, 版权 goes back to the writer to be retold in its own words, 平台 goes onto the author's sheet.

Each call, pass one, pass two or re-check, with no result 20 minutes after sending is stopped and sent to the backup model, recorded "skipped" with the reason.

### Grading

Once the three positions and both re-checks are back, the organizer sorts every finding by the size of the change it needs, the standard's 第十七节: sentences and words, back to the writer; paragraph order and subheads, back to the writer and the whole reread; 动骨架 (core judgment, main case, skeleton), stop and take it to the author before the editor runs (`stops.md`, "When review stops the route"). Sort by the size of the fix, not by how strongly a position said it. When unsure, take the larger size.

The organizer reads the reader's record now. The editor does not see it until its first pass is delivered.

The expert's verdict:

1. **说满了**: back to the writer, who adds the condition to the facts only (who, when, how far), in a sentence of its own rather than inside the original; the judgment keeps its edge. If the condition would leave the reader nothing to take away, it goes onto the author's sheet instead.
2. **站不住**: 动骨架. Its counter-example was checked in the first re-check; the message to the author gives that result, and the author picks rewrite, no rewrite (the editor runs) or overrule the expert (reason on the review sheet).
3. **Two judgments**: whatever the verdict, lay the expert's core judgment beside the third of the three answers. Both judgments inside the third answer: the judgment itself is wrong, 动骨架. The answer holds one and the draft wrote a second: a whole section or more of it is 动骨架; a sentence or two goes back to the writer to delete.
4. **One judgment**: write the expert's sentence and the third answer side by side and ask whether both can be true. They can (one says A, the other A and B): onto the review sheet, no stop. They cannot (A and not A): to the author.
5. **The expert's other findings** (outsider errors, vague wording): a change or a reason, the reason on the review sheet, like reader findings; whether a reader would rather read it does not decide what is right.

Where to go back is the author's call; the organizer recommends one: gate 1 when the judgment itself is wrong (站不住, or two judgments inside the third answer), gate 2 when the draft wandered off a sound judgment (a second judgment the three answers never held, a section crowding in four companies).

Before an editor's or expert's item that deletes a whole passage or case, or squeezes out its details, check the reader's record: a passage the reader would pass on to someone, or did its sums by, keeps its numbers and practices.

Grading is done, and the editor runs, when no finding sits at 动骨架, or the author has ruled on each one. When the author orders a rewrite, the new draft is a new first draft: the three positions run on it again.

### The editor's first pass

After grading, a fresh call with prompt "Editor" (`prompts.md`).

| Position | Gets only | Never gets | Delivers | Done when |
|---|---|---|---|---|
| Editor | The first draft, the one the other three read; the exemplars the author picked at gate 2, whole; the standard's 第一、五、六、七、八、九、十一、十二、十三、十五、十七、十九节; the entries of the edit rules (`edit_pairs_folder`/`修改规律.md`) still in force and resting on two or more articles (entries written before 3.9 and not yet counted go as before, noted in the editor notes), without those marked 已取代 or 已并入 and without G2 | The reader's record, the expert's report, the fact checker's tables, the line "the reader has already read it", the outline, the three answers, the writer's subhead sentence and self-check record, the material pack | Ten actions in three groups (读不通, 读得通但没意思, 不像人话) plus a comparison with the exemplar (where a reader of the exemplar reads on and a reader of the draft would drift off), every item with its group, place, a problem someone can check, and how to fix it. Groups one and two are 退回写手 items; group three is marked only, for the author, except 金句拼贴 (a section closed by a forced golden line; several maxim-style short sentences in a row), which counts as group two by the standard's 第五、十一节 and goes back to the writer | All three groups run, every item carries its group |

## Merging

The organizer merges everything into one list for step 7. Its first line is always: "锋利的话、冲突、钩子一样不许磨软；下面改的是事实、抄袭和读着卡的地方，不是语气。" The writer revises once, from all of it together (`write.md`, step 7).

1. Fact checker items: 查不到, 对不上 and copying marked 必改 are must-fix. 待补: the writer adds the source or deletes the unfound point; a soft word ("可能", "据说") that keeps the meaning is not a fix. Copying in the title or opening, which the author set at gate 2, goes onto the author's sheet with candidates. The five kinds from pass two: 名誉 and 内部数据 with public ground found are no risk; without it, onto the author's sheet; 政策 back to the writer to drop the verdict on the policy; 版权 back to the writer to retell; 平台 onto the author's sheet.
2. Reader items, listed apart: each "here I would stop" and each "this I do not accept" with the reader's own words, changed or given a reason. One that touches the author's stance or experience goes onto the author's sheet only (iron rule 3); the writer neither deletes nor softens it.
3. A condition, qualifier or source goes into a sentence of its own, never into the sentence it qualifies (`write.md`, step 7). Editor items: groups one and two come back to the writer, who changes each or gives a reason the second pass judges; each is adopted only when the reader would rather read the result, with one line why; a fix never removes a specific number, practice or person, except a name the citation rule says not to carry (`write.md`, step 3, item 5); findings that would flatten a stand go onto the author's sheet instead. Group three is marked for the author, not sent back, except 金句拼贴 (a section closed by a forced golden line; several maxim-style short sentences in a row), which counts as group two (the standard's 第五、十一节) and comes back to the writer.
4. Expert items, written apart: as "Grading" says.
5. Findings about the author's experiences or stance: the author's sheet only.

Whose miss it was, before a reader's spot goes back to the writer: open the editor's first pass. The editor flagged it and the writer did not change it: the writer missed it. The editor did not flag it: the editor missed it. A muddled subject or unclear reference belongs to the editor's first pass; the reader passing over it is no miss of the reader's.

## Step 8: facts again, and the editor's second pass

1. **Facts, on every revised version.** The organizer pulls a fresh sheet from the revised draft (step 5) and marks each line against the previous sheet: 旧 (sentence identical), 改 (words changed), 新 (not on the previous sheet). 旧 lines keep their status; 新 and 改 lines go to pass one. A sentence the writer marked "意思变了" in the change list goes onto the sheet and is re-checked too, even with no number or Latin-script name in it. Pass two runs again only when the title, the opening or any subhead changed, or a whole section was rewritten. This runs after the first revision and after any revision the second pass sends back; the version the author reads at gate 3 has always been checked.
2. **The editor's second pass** replaces the old read of what changed. Its brief is built only after the first pass has been delivered, so the first pass can never see it, and holds five things: the first pass's list verbatim, the revised draft, the writer's change list (`write.md`, step 7), the reader's spots verbatim, and the changes outside the list. Before building the brief the organizer lays the revised draft against the first draft paragraph by paragraph and lists every change the change list does not mention; that list is the fifth thing, and the editor treats each as it does any changed place: joins and breakage only, not content. No expert report or fact table: items the change list traces to them are checked only for whether they join their neighbours. Prompt "Editor: pass two" (`prompts.md`).
   - One question per first-pass item of groups one and two (group three was marked for the author and is not checked): is that problem still there? Gone is a pass, whatever wording the writer chose ("写法与示范不同，问题已解决" is recorded as a good thing); still there, or left unchanged without a reason, is 退回写手.
   - One read through, watching the same five things (the changes outside the list are read like any other changed place; the five do not grow): joins at every change, the nail still in, new sticking points, untouched passages broken, the reader's spots. A reader's spot still there goes to the author, never back to the writer; the numbers and practices in passages the reader would pass on or did sums by are still there.
   - What the read finds: brought in by the revision, 退回写手; missed by the first pass, sentences or paragraphs, 退回写手 and recorded "第一遍漏了"; missed by the first pass, skeleton, 建议推翻 and recorded "第一遍漏了". "Could be better" is not raised.
   - It returns one of three: 过 (to the author); 退回写手, once only; 建议推翻 with its reason, to the author (`stops.md`). The brief says whether this is the first check or the second after a return; on the second, a problem still there is 交作者, never 退回写手. It never edits the draft.
   - An incomplete change list goes back to the writer to complete; that is unfinished work, not a 退回写手 verdict.
   - Rounds: the first pass's list and the writer's one revision are not a return; the second pass returns to the writer at most once; a problem still there after that goes to the author. The writer revises at most twice.

Done when every new or changed line has a status, none stays 查不到 or 对不上 without the author's decision, every 待补 has a source or lost its unfound point, and the second pass has said 过 or the author has ruled.

## Findings

Each position's format is in its own card (`prompts.md`). Positions give no severity; the organizer sorts every finding by the size of the change it needs ("Grading") and quotes the reader's and expert's words as they are. No problem means saying so.

## Review sheet (for gate 3)

In the article folder. First line: the expert's verdict, its condition or counter-example verbatim, and how the organizer graded it. Then: the deliverables and what was done with each item; cases N, of which M have no reason written (the expert's case table); every section the reader said it would stop reading, in its own words, whatever size it was graded; reader items not adopted, with their reasons; expert findings not adopted, with their reasons; facts still 查不到, 对不上 or [待确认], and pass two's flags on the author's sheet; reader spots still there after the second pass; what the second pass recorded as 第一遍漏了; open items first.

## Feedback candidates (every article)

At the close of every article write one line per place the author rejected something or we withdrew our own work: the problem sentence verbatim | what happened and why | where in this Skill the fix belongs. Four standing lines appear even when nothing was rejected: the seed's outcome (stands, partly wrong, overturned; did the author agree); which title the author picked at gate 2 and at gate 3, and why; at which gate or stop, if any, the route went back, and why; the misses, counted: the editor missed N, the writer missed changing N, the first pass missed N. Sessions that use the Skill write candidates and do not edit its files; the maintainer merges recurring ones in one place and deletes old rules that no longer earn their place. **Every three articles**, the maintainer lays the reader's spots beside the editor's first passes: how often they overlap and what the editor missed show which of its ten actions is written too loosely.

**Every five articles**, the maintainer lists the rules, bottom lines and editor questions that none of those five articles triggered, and the author decides which to delete. A process that only adds grows heavier with every article.

**Rejected changes.** When the maintainer revises this Skill, each change the author rejects gets one line in the maintainers' record of why the rules exist: the change, why it was rejected, the date. The next revision reads these lines first and does not propose the same change again.

**One class per version.** A revision fixes one class of problem where it can, and the next real article checks it before the next class is changed. Writing has no automatic score, so the real article is the check.
