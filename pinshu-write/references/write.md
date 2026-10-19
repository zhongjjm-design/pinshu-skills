# Writing the article (3.0)

This route keeps the complete seed, a coherent line and whole-section revision together. Research, source checks, review roles, export and mechanical gates remain part of the process.

## What the organizer does differently

- **Read like a reader first.** Every draft the organizer reads whole, top to bottom, before any script or reviewer. If it does not read well, the fault is at the root (the line, the brief, the writer), and the fix is a rewrite there, not a list of patches.
- **Pass the author's words, not a translation of them.** The seed and the author's later comments go to the writer verbatim. The organizer does not turn a remark into a rule for every section, does not write sample sentences (the writer copies them), and does not set quotas ("one or two cases per section").
- **Keep the seed's soul.** The author's doubts, attitudes and reasons for writing (for example, their open questions and reasons for investigating) are what make the piece sound like a person thinking. They go to the writer and may stand in the body. They are never filed away as internal requirements.
- **Be strict on facts, loose on prose.** Names, numbers, quotes and the author's experiences are checked against sources; how the piece flows is judged by reading, not by counting.
- **A missing experience is asked, never ruled invented.** When a draft says something about the author that the seed does not, list it and ask the author; it may be true.

## The hook (before the line, stop 2)

A new account has no followers, so the title and the opening decide whether anything else gets read. They are settled first, by the author, before the line and before any drafting.

1. **One sentence the whole piece says**, written as a stand someone could disagree with ("嫌 AI 味、囤 AI 课，都是不动手；动手的人已经在用它干活、收钱了"). Everything in the article serves it; a second message is cut or becomes one section.
2. **Candidates from two vendors** (the configured writer and a second vendor, prompt 15): six title-and-opening pairs each, each pair on a different hook: the reader sees themselves in a scene and is stung (a mirror); a stand one part of the readers nods at and another wants to argue with; what the reader is losing; a concrete event or number with a contrast; a gap the reader wants closed. Openings 150 to 220 characters, short sentences, a sting or a conflict in the first three lines. Facts in them only from the material pack; common scenes written so a reader sees they are common, never as real people.
3. **The organizer picks four**, checking each before showing it: every sentence joins the next (nothing appears in the second paragraph that the first did not set up); no invented fact; no copying of a source article (`1-topic.md`, "Someone else's article"). It recommends one with one line why, and may suggest combining one title with another opening.
4. **The author picks.** The chosen title and opening go to the writer verbatim, and the writer writes on from that opening. A title or opening the author has called good is never replaced without asking.

What grips: high-arousal feeling (anger, anxiety, awe) is shared and low-arousal content (mild, sad, balanced) is not (Berger and Milkman, 2012); moderate, defensible controversy is talked about most (Chen and Berger, 2013); a reader is drawn by a gap next to something they already know (Loewenstein, 1994); a claim made as strong as it can be without becoming false is the useful one (Paul Graham, 2020); the first idea everyone has is not the one to write (咪蒙); stand on one side of a tension readers already feel (李叫兽).

## The line (stop 2)

Sharpen the seed first, inside the author's direction, with five moves: narrow it to one question (three things to say are three articles); find the reader's "以为 A，其实是 B"; find one concrete scene the piece can open on; settle who it is for (a boss and a peer need different angles); check that real material exists for it. Then write four lines above the line:

- **Core question**: the one question this article answers, in one sentence.
- **The reader's shift**: "读者原来以为……，看完知道……", one sentence. For a practical piece the second half can be "知道先做哪一步、关键卡在哪". If it cannot be written, the topic has not stood up yet. This sentence goes to the writer, to the organizer's read and to the reader role's comparison.
- **Opening scene**: the concrete thing the piece starts from.
- **Material**: enough, or what is still missing.

Then, before anyone drafts, write for the author one paragraph in plain words: how this article moves from its first paragraph to its last. What the reader wonders at the start; what each part answers; how each part grows out of the one before and hands the reader to the next; where the reader learns something they did not know; what they leave with. This is 起承转合: the writer knows the logic before writing, and every paragraph is joined to its neighbours. It is not four labelled boxes, and not a list of subheads.

Name the shape the line takes: building (what it is, why, what to do; one layer pushes the next; suits opinion and review pieces), parallel cases (several cases each hold up one corner; suits method and round-up pieces), or question by question (a big question split into small ones answered in turn; suits practical and Q&A pieces). Under the paragraph, one line per step: what that step stands on, by name (which of the author's experiences, which outside case, which pair of numbers). A step that stands on nothing is said at stop 2: research more, or move differently. Length is the configuration's total (default 2000 to 2500); it is not split across steps.

When a genuinely different shape would also work, add one or two sentences on how that alternative moves and what it changes; never a near-copy of the first.

With it: three title candidates. A title tells the reader at a glance what the piece is about **and** carries one thing the reader does not already know (a turn, a finding, a number, a real conflict). A line any reader could have said first ("写一遍 Skill，以后不用反复教 AI") fails, however clear it is. Ask of each candidate: would the reader say "谁不知道"? If yes, rewrite.

The author approves the line, or says how it should move. Their words go to the writer as they are.

## The writer's brief

One writer, the one configured as `writer` (selected by the author for the account). A second writer only when the author asks for two.

The brief holds only these, in this order, and is written the way an editor talks to a writer:

1. **A few plain sentences on what this piece is**: who reads it, why the author is writing it, what the reader should feel and take away, and the reader's shift approved at stop 2 ("读者原来以为……，看完知道……"), verbatim. For a practical piece: "这是作者自己琢磨出一套做法、又拿去跟别人对照之后的心得，像跟朋友聊天一样讲，读者读完知道每一步怎么做。"
2. **The seed, whole and verbatim**, with the line: "这篇的线就是作者这段话里的那个疑问，顺着它写。"
3. **The title and opening the author chose**, verbatim ("从这个开头往下写"), the one sentence the whole piece says, and then **The line the author approved at stop 2**, verbatim.
3a. **What makes it gripping**, pasted as written, then the account standard's sections on why readers share, titles and openings (configuration `good_article_standard`, `writer_parts`):

```text
这篇最要紧的：让人忍不住点开、看完、转出去。观点只站一边，说到再强一点就不对了为止；限定语只在真不确定的地方用，不用"可能""某种程度上"给自己留退路；话要让另一边的人看了想反驳，但站得住，有事实撑着。刺的是行为，不是人。每隔几段给读者一个他没想到、一看就懂的点。最狠的那句话留着，别改成劝告。结尾不总结、不给建议清单，把问题抛回给读者，让他读完坐不住。比喻前文没讲明白就别用，宁可多说半句大白话。
写法：开头从选定的那个开头往下接。写每一段前想清从哪句接上一段、这段让读者明白什么、到哪句交给下一段；一段讲一个点，观点先站出来再拿事撑，抽象的话后面跟一个有人、有过程的"比如"；段和段靠上一段末尾那句接。句子长短交错，能用动词就不用形容词；读者可能不认识的词第一次出现先说清是什么。一句话单独成段全文最多两处、不连着。初稿先把意思写顺，金句不硬憋。
```
4. **One or two whole exemplars** of the same article type from mature writers (configuration `exemplar_index`), introduced in one sentence each on what to learn: how it opens, how one paragraph leads to the next, how a case comes in and what follows it. "学它的口气和推进，不借它的事实和句子。"
5. **How the author edits**: the configuration's edit-learning rule file (`修改规律.md` in `edit_pairs_folder`), the rules learned from his past edits, each with its "原稿 → 终稿" example. Paste it whole; it is the author's voice in his own corrections.
6. **The material pack**: the author's real experiences (from the seed, the decision log and the library), facts and cases with their sources, each marked "可以用". A number comes with the number it is compared against ("聚焦的提升 18.8 个点，大而全的反而掉了 2.9 个点"), since a bare number tells the reader little. An item marked "需确认" (a personal blog, a community test) says so, with the wording to use ("有人实测"). Cases keep their people, process and contrast. Nothing says how many to use or where.
7. **Five bottom lines**, pasted as written:

```text
1. 人名、公司、数字、引语、日期，以及作者本人和别人做过的事、结果，只用上面给的，不改事情本身，不编没发生的事；情绪、场景、口气可以写，合情合理就行。
2. 文章里不透露用 AI 写稿：不写写稿流程、写稿工具、用 AI 写稿这件事。
3. 不用破折号，不用这些词：<profile banned words>。
4. 全文 <length>（默认 2000 到 2500 字，最多不超过 2700 字）；一句话不单独成段，别连着两段都是一句。
5. 读者大概不认识的人不点名，按他做的事称呼（"一位做 PPT 的设计师"），名字放进文末参考文章；不用"AI 博主"这类标签。
```

8. **Output**: only the article, `#` title, `##` subheads, then the 参考文章 block.

Nothing else goes in: no rule book, no audit list, no per-section template, no sample sentences. The passages in 3a are the explicit exception: they provide positive writing guidance rather than an audit checklist.

`writer_parts` is an optional per-account selector into that account's own `good_article_standard`, not a bundled standard. If it is empty, read the standard and select its guidance on sharing, titles and openings by heading; ask at stop 2 if the selection is ambiguous. If there is no readable standard, keep the guidance in 3a, record the missing account asset and follow the conditional good-article-check fallback in `models.md`. Do not invent an account profile or claim the omitted guidance was supplied.

## The opening (stop 3)

When the draft arrives, the organizer reads it whole first and answers, before anything else:

1. In one sentence: what did the reader believe before, what do they know now? Does it match the stop 2 sentence?
2. Does it open on a concrete thing (a scene, a contrast, a number, the reader's own question, someone's words)?
3. Are there two paragraphs in a row of pure reasoning with no event, person or number in them?
4. Does any stretch lecture the reader or turn into a list of advice?
5. Can the whole piece be said in one sentence the reader takes away?
6. Section by section: can each be said in one sentence the reader takes away? (A check on the thinking, not a request for a closing line in every section.)

Any "no" sends the draft back to the writer with the line and the answer, before stop 3 and before review. If it passes, send the author the first 300 characters (title included) and one question: does the first sentence make sense, would you read on. A fresh model with no context may stand in when the author is away, asked only those two things. An opening that fails is rewritten before anything else is looked at.

## Review and revision

Before any reviewer sees the draft, the organizer reads it whole as a reader (the questions under "The opening") and runs the gates (`audit_draft.py --first-draft --length 2000-2500 --hard-max 2700`, or the configuration's length): one-sentence paragraphs in a row, dashes and banned words block; on the first draft a body over the hard maximum is a reminder that heads the merged list, and the revision brings it back inside the range. A draft that reads badly at the root (no line, pieced together) goes back to the writer with the line before review; review is for a draft that already reads like one piece.

Then every reviewing role runs (`5-review.md`, "Running step 7"; prompts 5 to 14). Facts and risk checks hard facts only, as written in `5-review.md`. The merged list goes to the same writer with the line and its full text, and the writer rewrites whole sections where the list points, once (`5-review.md`, "Revising"). The organizer reads the result whole and lays its title, opening and three sharpest lines beside the previous version's: if the new version is flatter (a stand turned into advice, a sting removed, a hook gone), it goes back to the writer with both versions quoted, before anything else. Then it runs the gates again without `--first-draft` (now the hard maximum blocks), then the after-revision read and the seed check.

## After 定稿: learn from the author's edits

When the author has edited the draft by hand (pasted back, or edited the file), save the writer's last draft in the `原稿库` folder and the author's version in the `终稿库` folder of `edit_pairs_folder`, both named by date and title. Compare them sentence by sentence and add to `修改规律.md` what the author did, each as a short rule with its "原稿 → 终稿" example: how he brings a case in, what he adds after it, where he puts his own judgment, how he joins sections, which numbers he softens, how he shortens sentences. Merge with an existing rule when it is the same move; note the sample count. The next brief carries the whole file. This is how the Skill learns the author's voice: from his edits, never from the account's old articles.

## Time

Length: 2000 to 2500 characters, never over 2700 (default; the account configuration wins). Time is measured, not chased: the review roles stay even when they take longer; what saves time is a draft that reads like one piece before review and one whole-section revision instead of rounds of patches. Record start and end of each article in the decision log.
