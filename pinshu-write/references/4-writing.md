# Step 6: Writing

The reader is busy, reads on a phone and stops at the first word they do not understand. Write so that a reader outside the industry never gets stuck and a reader inside it still finds something new.

Two writers of different vendors (`models.md`) draft the article from the same brief; the author picks one at stop 3. The writer also writes outline wording, titles, subheads, the opening paragraph for stop 2 and every revision. The organizer builds the brief (prompt 1), pastes the material in (never file paths), sends one step per call, and checks the result before anyone else reads it. Draft each article in a fresh session.

## The exemplar brief

The writer learns voice, breath and pace from whole articles rather than a rule-heavy brief. Count a brief in characters (Python `len`, or the audit script), never with `wc -c`, which counts bytes rather than characters. Keep the brief to these parts, in this order (the numbers are why, not part of the brief):

1. **The author's direction in one sentence**, in the author's words.
2. **Two exemplars, whole** (below, "Exemplars"), introduced with one line each on what to learn from it (how it opens, how it pushes one point through), and the line: learn the voice, breath and pace; use none of its facts, cases or phrases.
3. **What to write**: the title (locked once approved), the reader in one sentence, the judgment and how it unfolds (how an opinion piece opens depends on how sharp the judgment is, `3-structure.md`), the approved outline with each section's target length, and the opening paragraph the author approved at stop 2, to be kept as written unless the author asked for changes, and the line “第一节接着开头往下走，不重复开头已经说过的。” When the author has said this article has none of their own experience, add: “开头不写任何具体某人的经历，用读者共同的感受。”
4. **The material**, per section where it helps: facts from the fact table with their Chinese wording, the author's own material verbatim, hypothetical scenes marked as such. "Use what helps; leftovers are fine."
5. **The six bottom lines**, pasted as written below, then "the rest is up to your ear".
6. **The 参考文章 block**: the format from `6-deliver.md` ("Delivery format": the long-form pieces used and the main research reports with a source a reader can find, one line each, full title in 《》, author or organization, platform, date) and the entries to list.
7. **Output**: only the article, from the title line, subheads as `##` (the audit splits sections there), then the 参考文章 block if any.

Everything else in this file (the after-check, the hard rules, machine patterns, the evidence budget) stays out of the brief: the organizer checks the draft against it afterwards and sends failures back as a sized revision (`6-deliver.md`).

**The six bottom lines** (fill the angle brackets with the configuration's or the profile's wording, word for word; the organizer adds no number of its own):

```text
1. 人名、公司、数字、引语、日期和作者本人的经历，只用上面给的，不编；缺的写“[待确认]”。人物的身份和性别、调查问的是谁和怎么问的、作者的观察，也都照上面写，不加头衔，不加重。一般生活经验的描写（比如熬夜赶方案）可以写。
2. 文章里不透露用 AI 写稿：不写写稿流程、写稿工具、用 AI 写稿这件事；作者自家的案例只写做视频、服务客户这类业务上的事。
3. 重点句和金句可以加粗，别满篇。不用破折号，不用这些词：<profile banned words>。“不是……而是……”这类句式默认不用，确实需要时全篇最多一次，用句号拆开写。
4. 全文 <length> 字；小标题 <n> 个，每个都是题眼：不看正文就知道这一节说什么，带自然的逗号，十六字以内，不加编号。
5. 段落正常：一段三到五句、八十到两百字；核心观点和金句可以单独成段，别连着两段都是一句；也不写大段文字墙。
6. 主语清楚：开头第一句和每段第一句都说清在说谁（我、你、某个具体的人或公司）。
```

## Exemplars

- An exemplar is a whole article by a mature writer that the author has approved, listed in the index the configuration's `exemplar_index` points to (format: `templates/exemplar-index.example.md`). Pick two marked approved whose type and length match this article; record which two in the editor notes.
- Exemplars are other writers' good articles. The author's own earlier drafts join only once the author approves them as representative of a settled style.
- No index yet, or no approved exemplar of this type: use the configuration's `exemplar_fallback` (articles the author approved for briefs); otherwise ask the author at stop 2 for two articles of this type they like (links or text); with none, write from the bottom lines alone and write "no exemplar" in the editor notes.
- Exemplar texts and their paths live in the author's library and configuration; this Skill holds no third-party article.
- Judge "sounds like the author" by how much the author edits, not by an AI score.

## The organizer's after-check

Run on every draft that comes back, before review and before the author sees it.

1. **The author's experience comes only from the fact table's entries of the author's words**, written in the first person ("I"), never "<author name> said". The organizer checks every first-person detail against the table; anything missing becomes "[to confirm]".
2. **Facts come only from the table.** The table governs names, companies, numbers, quotes, dates and the author's experiences; an invented one, or an approximation ("the past two years", "thirty to forty percent"), is removed. A person's role and gender, who a survey asked and how, and the author's observations follow the table too: an added title ("a business scholar"), a survey's hypothetical question turned into something that happened, or an observation made stronger goes back to the table's wording. Everyday detail anyone lives through ("staying up late on a proposal") is description, not a fact, and stays. A hypothetical scene looks hypothetical.
3. **The writing run stays out of the article**: timing, test runs, tools, approval friction, how the article was written. The author's own business (making videos, serving clients) is material when the author names it.
4. **Every claim carries its origin**: what a named source says, what engagement numbers show (reader interest only), what the author's material contributes, or an agent inference worded as the organizer's hypothesis, never as a source's conclusion. A pattern generalized from samples is a label: write the count over the sample ("8/10"); under five samples add 仅供参考. A statistic quoted from a source keeps the source's form.
5. **The author's own work is described by what was done and tested**, without praise or self-deprecation; a test is never written up as a success.
6. **Points serve the judgment.** Seed points may be merged or compressed into the passage where they help the judgment; the direction stays the author's, and a point the author stated is dropped only with the author's approval (stop 2). The organizer writes the coverage list (each S-number and the paragraph that carries it, or merged into which, or "not covered" with the reason) into the editor notes.
7. **Length**: each section near its target. A short draft expands one named section with illustrative examples, never new facts; a rewrite pastes the full earlier draft and states "not shorter than the previous draft".
8. **Locked items stay word for word**, in the draft and every revision: the title, approved subheads, the opening paragraph approved at stop 2, wording adopted in earlier rounds.
9. **Nothing the author cut comes back.** Check every revision against the cuts in the decision log; a cut passage that returns is removed.
10. **Sources survive revision.** A source the fact table holds stays in the article; a study or survey named in the body says who did it.
11. The editor notes, written by the organizer, carry the verification list (each fact, what it supports, source, date), the coverage list, the two exemplars used and which writers drafted.

Optional tool for the outline stage: write the judgment as one relationship ("under condition C, A changes B through mechanism M, so result R follows"); if it will not write, the body is not ready to lay out. Not a gate.

**Faults to check.** Check every writer's output for research jargon, invented detail when material is thin, short or long drafts, single-sentence reversals, numbered subheads ("01"), straight quotes in Chinese text, approximate figures, unreliable self-reported counts, excessive ornament, invented reference titles, single-sentence paragraphs, prompt colons and corner quotes 「」. Convert straight quotes with `scripts/fix_quotes.py`, punctuation only, and note it. Run the audit and the language check on every output; do not treat these checks as a model-specific performance claim.

## Chinese hard rules

The organizer's after-check: breaking any fails a draft; the writer's brief carries only the six bottom lines. Rules 4, 6 to 10 and the punctuation and emoji parts of 11 also apply to all Chinese shown to the author, except quotes; messages to the author carry no bold (`stops.md`). Chinese wording and examples are printed by `python3 scripts/audit_draft.py --rules`.

1. One main line: the opening question, the evidence and the closing answer concern one thing.
2. Shared feelings are allowed, invented crowds are not: writing a feeling most readers share ("most of us have felt this") is how an article earns resonance; a crowd used as evidence with nothing behind it ("many people say", "a friend told me") is removed.
3. Freshness follows the account profile; where it says nothing, evidence older than six months is replaced or dated. AI claims are current; classic principles are exempt.
4. Plain words, judged by the account's reader: words that reader uses every day stay unexplained (for readers who use AI at work: Token, Agent, Skill); jargon and foreign terms the reader may not know get half a sentence at first use saying what kind of thing it is, or are replaced; a plain statement beats a metaphor.
5. No sources in parentheses inside sentences. After the body, only a 参考文章 block; the verification list stays in the editor notes (`6-deliver.md`).
6. A normal mix of long and short sentences unless the profile asks otherwise; no chopped strings of short sentences.
7. No em dash (U+2014, including the doubled form).
8. No single-sentence reversal ("bu shi X er shi Y" and the variants `--rules` prints); when one is truly needed, at most once per article, split by a full stop.
9. Banned words: the profile's list plus the script defaults.
10. No meta narration ("this article wants to say", "to sum up").
11. Exactly one H1, full-width punctuation, curly quotes (U+201C, U+201D), no emoji. Bold marks key sentences and punchlines so a skimmer can follow the argument; a page where most lines are bold has no key sentence.
12. Three to five punchlines (lines worth repeating), spread over the opening, the ends of sections and the close.
13. Counts come from `scripts/audit_draft.py`, never from the model's report of its own text.
14. After cutting or moving a passage, search the draft for anything still referring to it.

## Words and stuck points

- Explain industry shorthand in everyday words at first use or replace it: person-day pricing, rate cards, pricing anchors, deliverables, execution, capacity, retrospectives, window periods, white-label goods, IP (owned content franchises), the Big Four, award names, losing a bid. If the word must stay, add half a sentence: "...which means...".
- Translate concepts into the reader's own scene: say what the person does or sees. One word for one thing; no synonym swapping. Prefer the word you would say across a table.
- Introduce a person or organization in its own sentence, or at the next mention; a parenthesis in the middle of a sentence breaks the reading.
- Seven places where readers get stuck:
  - pointers land on a person or thing ("this", "this line", "it" in a row become names);
  - a work (film, post, product) is introduced, with whose it is, before it is named;
  - transitions say from what to what;
  - action words are exact (no "we sampled" when nothing was sampled);
  - products are named, not "this kind of feature";
  - no home-made phrases ("the smallest line" becomes plain words);
  - numbers that change (views, plays, followers) are re-measured on publishing day with the date in the sentence.
- Paragraphs of three to five sentences, about 80 to 200 Chinese characters; a core claim or a punchline may stand alone as a one-sentence paragraph, never two in a row. The article's first sentence and the first sentence of every paragraph name their subject (I, you, a named person or company), because a reader who does not yet know who is meant stops there. One paragraph, one point; at most one example and one number-heavy statement per paragraph; sections of similar weight, each near its target length in the outline. Every few paragraphs give the reader a reason to keep going: a new fact, a turn, a return to their own situation.
- Addressing the reader as "you" helps; about 4 to 7 uses per 1,000 characters reads naturally, far more reads as lecturing (the audit reports the count).

## Evidence budget

Outside evidence serves the author's argument; it does not replace it.

- At most one strong outside item per section, about five in the article; extras merge into a passing sentence or go.
- People and events before papers: a named person doing a concrete thing persuades more than a survey percentage.
- Outside material has three jobs: confirm a claim, mark its limits, add a detail. Except in a news-analysis piece it is never the main character, the opening or the ending.
- Each citation points to the one sentence it supports.
- In the text, light attribution in words suffices ("a UK industry association interviewed more than sixty agencies").

## Machine patterns to remove

- The single-sentence reversal as a rhetorical move.
- A punchline closing every paragraph; connectors opening every paragraph; "first, second, finally" skeletons; a label before each example ("even more striking").
- Invented crowd voices and straw-man readers set up to be corrected; over-precise sensory details nobody measured.
- Climbing to "in essence" or "fundamentally" plus a claim larger than the article.
- Translation-flavored function words and nominalized verbs; inline parenthetical sources.
- Prompt colons: announcing a point with a label and a colon ("in a word:", "the key is:"). Say the point directly.
- Abrupt comment openings: a non-first paragraph that starts with an evaluative phrase ("it is worth noting", "the problem lies in") without linking back through "this", "that", "but", "so" or a subject.
- Evenly sized sentences and paragraphs: a text with even structure still reads as machine-made after every flagged word is replaced. Check structure before words.

Couplets and three-part lines are a form, judged like any line by whether they say something (`3-structure.md`, "Subheads").

**Two structure reminders for the language reviewer only.** They are not rules: flag them for the author and never require a rewrite. (1) An ending that states the moral of the whole piece. (2) One straight line of argument from start to finish, with no turn, aside or counter-case. Basis: an outside test of 23 de-AI-flavor Skills found that rewriting kept both in almost every case (GoSailGlobal, 2026-10-07, small sample). They are not the author's words, so they stay reminders.

Do not overdo it. Human writers use metaphors and rhetorical questions in the body far more often than AI, so a language check never deletes them as "AI flavor". (Basis: the lieflat-less-ai-tone study, 629 texts; human baselines cannot be recomputed and the patterns match wording, not intent.)

## Mechanical checks

Run both audits on every draft before each review round and before the author sees a draft. If the tool cannot run commands, ask an agent that can, and write "audit not run" in the editor notes until then.

```bash
python3 scripts/audit_draft.py draft.md --length <min>-<max> [--banned-file <list>]
```

- `--length` takes the configuration's range; its floor only catches a half-delivered draft, the target is the account's own length.
- The script counts and locates; it reports blockers, fixes and warnings. Exit 1 means blockers; exit 2 means seed flags. Read the counts, never only the exit code; exit 0 can still carry warnings.
- `--card` for process text shown to the author (judgment, outline, messages): keeps the wording rules and drops article-shape checks. `--seed <the author's verbatim seed file>` flags scope and relationship words the seed does not use ("no longer", "turn to", "replace", "the real thing is", "has failed"); every flag goes to the author. It is a mechanical floor with known blind spots; the author judges meaning.
- The AI-flavor audit is `scripts/audit_ai_flavor.py <file>` from the `remove-ai-flavor` Skill, run beside it. Run both on the text readers will see, alone: the article body without editor notes or the 参考文章 block, or the message by itself, never a file that also holds the author's seed or sources. A finding on a word the author used in the seed is the author's vocabulary and stays. If that Skill is not installed, say so in the editor notes.
- Passing is a floor, never proof of quality.
