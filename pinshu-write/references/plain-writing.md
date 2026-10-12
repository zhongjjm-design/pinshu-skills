# Plain writing

The reader is busy, reads on a phone, and stops at the first word they do not understand. Write so that a reader outside the industry never gets stuck, and so that a reader inside it still finds something new.

## Hard rules for the Chinese text

Breaking any fails a draft. Rules 4 and 6 to 12 also apply to all Chinese shown to the author, except quotes.

1. One main line: the opening question, evidence and closing answer concern one thing. Ranked dimensions answering the same question are still one line.
2. No fabrication. The author's experiences, clients and data come only from the author's words and decision log, via the fact table; missing items are "[to confirm]". External facts need a source. Hypothetical scenes look hypothetical; invent no companies, names, numbers or approximations.
3. No unsourced crowd ("many people say", "a friend told me").
4. Plain words: explain jargon and foreign terms at first use, or replace them; no metaphor where a plain statement works.
5. No sources in parentheses inside sentences. After the body, only a 参考文章 block of complete long-form pieces; the verification list stays in the editor notes (delivery reference).
6. Normal mix of long and short sentences unless the profile asks otherwise. No chopped strings of short sentences.
7. No em dash (U+2014, including the doubled form).
8. No single-sentence reversal ("bu shi X er shi Y" and the variants `--rules` prints). A short reversal split by a full stop is allowed occasionally.
9. Banned words: the profile's list plus the script defaults.
10. No meta narration ("this article wants to say", "to sum up").
11. Exactly one H1 title, full-width punctuation, curly quotes (U+201C, U+201D), no bold in body text, no emoji.
12. At most two punchline closers per article; no mirrored couplets; no three-item slogans.
13. AI claims are current; evidence older than six months is replaced or dated. Classic principles are exempt.
14. Never self-certify counts; they come from `scripts/audit_draft.py`.
15. After cutting or moving a passage, search the draft for anything still referring to it.

## Words

- At first use, explain any industry shorthand in everyday words, or replace it. Typical offenders in business and agency writing: person-day or man-day pricing units, rate cards, pricing anchors, deliverables, execution, capacity, retrospectives, scheduling, window periods, white-label goods, bet-on-results deals, IP (meaning owned content franchises), "the Big Four", award names such as Cannes, losing a bid, freight forwarders. If the word must stay, add half a sentence: "...which means...".
- Translate concepts into the reader's own scene: instead of a category name, say what the person does or sees.
- Keep one word for one thing. Do not swap synonyms to avoid repetition.
- Prefer the word you would say out loud across a table. Read the draft aloud before review.
- Every foreign name or term gets half a sentence at first use: what kind of thing it is ("BetterUp, an American workplace-coaching company"; "The Information, a US tech publication"). The audit script lists foreign terms that look unexplained; a term followed by a bracketed explanation, or explained in the same sentence ("is a kind of", "that is"), is not listed.

## Where readers get stuck

Seven spots that made the author stop on one article; check each draft for them.

- **Pointers land on a person or a thing.** "This one", "this line", "it" used several times in a row must be replaced by names. In testing, "this line" appeared three times and readers could not tell whose production line was meant.
- **Introduce a work before naming it.** The first time a film, post or product title appears, first say whose work it is ("all three films are his own, posted on his second account").
- **Transitions say where from and where to.** "The same pattern is even clearer" points at nothing; say what moves from which case to which.
- **Action words are exact.** Do not say "we sampled" when no sampling was done; say what was actually done ("we searched the site on October 7 and looked at ...").
- **Name the product.** Write the product's name, not "this kind of feature".
- **No home-made phrases.** A phrase the writer coined ("the smallest line") is replaced by plain words ("the simplest line you can start tomorrow").
- **Numbers that change are re-measured on publishing day** (views, plays, followers), and the date goes in the sentence ("by October 12, 796,000 views"); their screenshots are re-captured the same day.

## Paragraphs and sections

- One paragraph, one point. At most one example and one number-heavy statement per paragraph; spread the rest.
- Paragraphs rarely exceed about 200 Chinese characters.
- Sections of similar weight (roughly 450 to 700 characters for a 3000-to-4000-character article). The audit script reports section sizes.
- Every few paragraphs, give the reader a reason to keep going: a new fact, a turn, or a return to the reader's own situation.
- Sources live in the verification list after the body (editor notes); readers see only the 参考文章 block, which lists complete long-form pieces (delivery reference, "Delivery format"). In the text, a light attribution in words is enough ("a UK industry association interviewed more than sixty agencies").

## Evidence budget

Outside evidence serves the author's argument; it does not replace it. In testing, one draft carried eleven studies and cases and read like an industry briefing; another let a single company case take over both the opening and the ending.

- **Per section, at most one strong piece of outside evidence** (the one that carries the most weight). Across the article, about five in total. Extra items are merged into one sentence in passing, or dropped.
- **People and events before papers.** A named person doing a concrete thing persuades more than a survey percentage; use the study to confirm the story, not the other way round.
- **Outside material has three jobs only**: confirm a claim, mark its limits, or add a detail. Except in a news-analysis piece, it is never the article's main character, its opening or its ending. The author's judgment and the author's own material lead.
- **Every citation can say what it proves.** For each piece of evidence, you can point to the one sentence in the article it supports. If it points to nothing, delete it. The structure review checks this.

## Skeleton gate (before drafting)

The skeleton is the outline, the title, the subheads, the opening and the ending. Readers judge an article by these before they read the middle, so most of the effort goes here. In testing, articles were rejected upstream (an empty judgment, unclear titles, nothing to act on, a soft ending), not in the sentences, and model reviewers catch errors, not emptiness; that is why these checks come before drafting. Nothing is drafted until the skeleton passes the checks below; approval 3 shows the author the result. After the body is written, the title and subheads are checked once more against the finished body (see "Re-check after drafting" below).

### The body: something the reader can act on

- For each section, ask: after reading it, can the reader open a tool and do one thing right away?
- A "how it is made" piece names the tools, the number of steps, the money and time, and the step where people usually get stuck. Concepts are only the frame.
- Hands-on material, the author's own and other practitioners', is the main ingredient. Do not let the judgment squeeze it out.
- For business readers, order the outline by the questions they need answered: what stays the same, what keeps working for years, what to keep doing, what it pays back. Material fills that frame; technical or academic numbers never carry a section on their own.
- In testing, one outline offered only two concepts and the author said there was nothing to act on; another was built on research figures and the author called it stuck in technical detail.

### The outline: it must push forward

- **Pick the order first**: answer first, conflict first, or question first.
- **Vertical check**: is each section the "why" or "how" the reader naturally asks after the previous one?
- **Horizontal check**: are parallel items the same kind of thing, and in a stated order? (Barbara Minto, The Pyramid Principle; summary only.)
- **Chain read**: read the first and last sentence of every section in a row. They should form one argument flowing downhill. Sections that only sit side by side are notes, not an article.
- **Cut check**: find the natural ending point, where the reader's feeling first peaks. If what follows is really another article, cut it or shrink it to a third.
- Read the title and subheads alone, in order, pretending you have not read the body. They should tell the whole argument.

### Title and subheads: direct first

Readers decide in this order: the title (and cover) makes them open the article; the subheads, the opening and the ending decide whether they keep reading. Readers are busy and have endless alternatives; a subhead that needs a second or third reading to decode loses them. This is business writing, not an essay: plain and direct wins.

**Priority, fixed.** Every title and subhead is judged in this order. When a later quality conflicts with an earlier one, the later one gives way.

1. **Direct**: a reader who sees only this line knows what the section (or article) gives them.
2. **Accurate**: it states exactly what the section delivers, no more.
3. **Memorable**: where possible, one short phrase the reader can keep (a named rule, a named step).
4. **Interesting**: a fresh angle or a counter-intuitive edge, only if 1 to 3 still hold.

In version 1.1.0 these sat side by side as equals, and writers chased "interesting" and "a claim someone could dispute" at the cost of "direct"; the author rejected subheads twice in a row for being roundabout. Directness is never traded away.

**The hard test, done on every subhead before showing the author.** Cover the body. Show only the subhead to someone outside the industry (or a fresh model with no context) and ask: "In one sentence, what will this section teach you, or what does it claim?" If the answer is wrong, vague, or needs guessing, rewrite. Do the same with the title: "What will you get from this article?"

**Subheads by article type.** The article type was settled with the author at seed confirmation; the subhead pattern follows it. Chinese examples of every pattern are printed by `python3 scripts/audit_draft.py --rules`.

| Article type | Subhead pattern | Wrong |
|---|---|---|
| Practical how-to | The action of this step, plus the reason it matters, ideally as one memorable named rule ("run every cut past a do-not list; one hit means redo") | Numbered steps ("Step 3: check the cut"), sequence words ("first", "then"), bare actions that read like a manual, summary lines ("quality control is underrated") |
| Opinion | The section's claim stated outright, so the reader knows the position without reading on | A topic label ("the other side of efficiency"), a riddle, a question the body must answer |
| Method | The method itself, distilled into one line the reader can apply | "Thoughts on pricing", "a few principles" |
| News analysis | What this event means for the reader | "Lessons from a launch event" |
| Integration piece | What the reader learns from this group of sources, stated as a claim or a method | "What five experts said", a list of source names |

**Title rules.**

- States plainly what the article is about, ideally the claim itself or the reader's own question. Test: someone who sees only the title can say what the article is about.
- **Every noun in the title can be pointed at by someone who has not read the body.** Ask of each noun: could a stranger say what it refers to? Words the article defines for itself ("the second time", "the ruler", "the new yardstick") fail: they are the article's internal shorthand. In testing, a title built on "the second time" was understood by nobody who had not read the piece.
- **Metaphors are earned in the body first.** A metaphor may appear in a title or subhead only after the body has explained it with a concrete example, and never for the first time in a title or subhead. A good metaphor inside the body stays.
- **Distinctive, not only clear.** Ask: would this sentence fit only this article? A title that could sit on top of any article on the subject fails, however clear it is: balanced couplets ("efficiency up, value down"), general calls ("it is time to rethink effort"), "in the age of AI, X" with nothing specific after it. Chinese counter-examples: `audit_draft.py --rules`. Distinctive comes from this article's own judgment, number, event or reader question, not from clever wording; directness still comes first.
- **Three candidates, written three different ways.** Give the author three title candidates that differ in form, not three rewordings of one hook: for example one that states the conclusion, one that is the reader's own question, one built on a concrete number or event. Mark the one you recommend and say why in one line. The author picks. The title standard is still being refined article by article; record what the author picks and why in the feedback candidates.
- **Cold readers score two things separately**: "understood at a glance" and "distinctive". A candidate needs both to pass before it reaches the author. Cold readers report words they do not understand verbatim and may not guess their meaning; any word a cold reader could not understand blocks a "keep" on that line (prompt kit 3 and 12). A rejected example: "He saved two hours with AI, his colleague spent two more" (who is "he"? what is this about?). Its accepted replacement: "Stop judging staff by how much AI they use".
- Seeing only the title, the reader knows "this is for me, and here is what I get". A practical piece names the result the reader will be able to produce.
- Short and direct. Replace vague words ("many", "important", "key") with a concrete number or object.
- Not the seed's original wording, not an abstract judgment, not a correct but empty sentence. (Rejected: a title of the form "after the hype, what remains is experience".)
- No key word with a second everyday meaning; readers will take the other one. (Rejected: a title whose word for "good-looking" the author read as "widely watched".)
- No riddle, no reversal that needs the body to decode, no lecturing rhetorical question.
- **Trending words the reader knows stay in.** A product or model name central to the body (a new model the article is about) belongs in the title. If a model "cold reader" calls it a barrier word, the author's judgment wins; in testing, a writer removed such a name on a cold reader's advice and the author put it back.
- Generate candidates with `gzh-title-strategist` if installed; the account's own rules win where they conflict (for example, its "not X but Y" patterns stay banned). Outside methods behind these checks: Ogilvy's "name the reader, promise a benefit, carry some news" and the "specific" test of the 4U formula (summaries only).

**Subhead rules.**

- Every word must survive "where does this word come from?" (rejected: subheads built on "for the first time" and "the first craft to be written down", which the body never earned).
- No word that only the body defines: no metaphor, coined term or pronoun ("this", "it", "the second one") that needs the section to make sense.
- **No line that can be split the wrong way.** Read the subhead as a stranger would and ask whether any two characters can be grouped into a different word. In testing, a subhead meaning "explain ideas with code, explain people with generation" was read as containing the word "talent" (人才), and nobody could decode it. When a layperson reader reports such a misreading, it is a must-fix, not a question for the author.
- **No worn-out abstract words** in titles and subheads: judgment, cognition, underlying logic and the like (the audit warns on the Chinese list). Use the words of the reader's own day. In testing, the author rejected a subhead built on "judgment": everyone says it now, and it says nothing.
- **Two checks, and the cover-the-body test decides.** Every subhead passes both the skeleton read (prompt kit 9) and the wording editor (prompt kit 12). If they disagree, the cover-the-body test above has the veto: a subhead an outsider cannot explain without the body fails, whatever the other check said. A replacement the wording editor proposes must itself pass every subhead rule, including length.
- Name the subject and what happens. Rejected: "Do not rush to change these three" (change what?). Accepted: "These three kinds of company need not change their review yet". Rejected: "Colleagues stop daring to use what you hand over" (unclear). Accepted: "With more half-finished work, everything gets checked twice".
- Read alone, in order, the subheads tell the whole article: the argument for an opinion piece, the full path for a how-to.
- Similar in length, about 8 to 14 Chinese characters as a guide; how-to pieces may run longer. Never pad a subhead or strip its punctuation to reach a number.
- Scope: business pieces for owners and managers use subheads as the skim skeleton. Personal long-form pieces about lived experience may go without. Readers scan the title, the opening, key sentences and the subheads first (Liu Run team's 2025 writing rules, reposted by Huxiu, read in full).

**Who writes them.** The writer writes titles and subheads; the wording editor checks each one against these rules: those that pass are kept as written, and only those that fail a named rule get a proposed fix (model-routing reference, "Writer, then the wording editor"). In testing, the subheads finally approved came after a second-vendor review of a rejected set.

**Re-check after drafting.** The title and subheads are written before the body, when the writer cannot yet see which words will turn out to be internal shorthand. Once the body exists, run the noun test, the metaphor rule and the cover-the-body test again on the title and every subhead, against the finished body. Change only what fails; the earlier decision to fix the title first stands. The editor-in-chief review repeats this check.

**The author's reading decides.** Two model "cold readers" once agreed on a title the author could not understand at all.

### Opening

- If you have a real event, open with it. Cap hypothetical scenes at one per article; the audit script now requires a fix when the opening is built on "suppose" or "imagine".
- Vary the opening. Before writing, look at how the account's last few articles opened and choose a different kind: a real event, a striking number, a counter-intuitive line, the reader's own question, a scene. Two test articles in a row opened with "suppose you are the boss of ..." and the author called it a template; a later outline did it again and was rejected for the same reason.
- If you use a scene, make it one the reader recognizes as their own; a hypothetical scene must look hypothetical.
- Within the first three paragraphs, put the reader inside the problem and promise, plainly, what the article will give them. No hook-pain-promise formula; no manufactured anxiety.
- **Glance test.** Give the first three paragraphs to someone who has read nothing else (a fresh model or a colleague) and ask them to retell, in their own words: what happened, and what this article is going to show. If they cannot, rewrite the opening.
- If a real case exists that matches the scene, place it right after the scene as proof that this happens.

### The central new concept

If the whole article depends on one new concept, show what it looks like the first time it appears: first say in everyday words what it did in the example, then give its name. In testing, a layperson reader said the biggest obstacle in the whole piece was never seeing what "making video with code" actually looks like.

### Arc

Opening, development, turn and close should each be identifiable.

- Development explains why the problem exists, ideally from the other party's point of view (the client's procurement, the platform's rules), so the reader stops blaming and starts understanding.
- The turn is where the reader's view changes.
- Limits come before the payoff. If some situations cannot be solved, say so before the final section, not as the last thing the reader sees.

### Ending

- Close on a judgment one size larger than the opening and more precise: the mechanism is more concrete, the conditions clearer. Not an empty lift into meaning.
- Answer the opening: return to the same event or moment.
- The standard is that the reader gains something: they leave having thought, and ready to act, carrying one judgment they now see clearly plus one action they can take (a sentence to say, a checklist for the team chat, a first step). Stop on that concrete action.
- An action list must belong to this article alone; the reader can build something by following it. Generic good habits ("test small first", "keep a retrospective") do not count. In testing, an ending of three such habits was called soft and unoriginal.
- Try deleting the last paragraph. If the article gets stronger, delete it.
- Do not restate the body; do not close on someone else's quotable line.
- **Keep the title's promise.** If the title promises to name something ("... is a misunderstanding"), the ending says plainly what the misunderstanding is.
- Outside methods: the "one idea written through" style card (the closing spine sentence must be more precise than the opening one) and Zinsser's On Writing Well on endings (summary only).

First endings in both early test articles were weak: one stopped on a list of limits, one read like meeting minutes. Both were fixed by handing over a ready-to-use object (a reply script; a three-question checklist) and closing with one line that ties back to the opening.

Avoid: ending on a list of limits; restating the title; a slogan; a blessing ("you deserve..."); a rhetorical climb to a bigger philosophical claim. A demonstration article that ended on "in these situations the price is hard to hold" read as weightless; moving the limits earlier and ending on a reply script fixed it.

## After editing

When a revision deletes or moves a passage (a scene, a case, a name), search the whole draft for anything still pointing to it. In testing, the opening scene of a weekly meeting was replaced, but the ending still said "back at the weekly meeting", which left the author confused.

## Machine patterns to remove

Scan for these, in addition to the audit script:

- Single-sentence reversal ("not X but Y" and its variants) used as a rhetorical move; a split, occasional "Not X. Y." is fine.
- Three-item slogans and evenly matched parallel clauses; mirrored couplets.
- A punchline closing every paragraph (at most two in the whole article).
- Connectors at the start of every paragraph; "first, second, finally" skeletons.
- A label before each example ("even more striking", "more bluntly").
- Invented crowd voices; straw-man readers set up to be corrected.
- Over-precise sensory details nobody measured.
- Climbing to "in essence" or "fundamentally" plus a claim one size larger than the article.
- Translation-flavored function words and nominalized verbs.
- Inline parenthetical sources.
- Prompt colons: announcing a point with a label and a colon ("in a word:", "the problem is:", "the key is:"). Say the point directly. Human writing has about 0.08 per 1,000 characters, AI about 0.30, and Claude models lean on it. The audit script warns.
- Abrupt comment openings: a non-first paragraph that starts with an evaluative phrase ("it is worth noting", "the problem lies in", "what matters more", "in the end") without linking to the previous paragraph through "this", "that", "but", "so" or a subject. Human writing: 0.14% of non-first paragraphs; AI: 0.62%. The audit script warns.

Do not overdo it. Human writers use metaphors about 2.4 times as often as AI, and rhetorical questions in the body about 17 times as often; reviewers must not delete them as "AI flavor". Deliberately varying sentence length does not help: human and AI texts showed no difference in sentence-length evenness. This sits alongside hard rule 4, "no metaphor where a plain statement works": that rule is about being understood at once; this one is about not stripping out human texture in review.

Evidence for the numbers in this section: the lieflat-less-ai-tone study (MIT), 629 texts (300 generated by five models including Claude Opus 4.6, 329 written by people). The human corpus is not public, so the baselines cannot be recomputed, and the patterns match wording only, not intent.

Check structure before words. If sentences and paragraphs come out evenly sized, a text still reads as machine-made after every flagged word is replaced (anti-slop, page read). The audit script warns when paragraph lengths are too even across the article or five in a row are nearly the same length.

## AI flavor at every step

AI flavor is checked at every step that produces Chinese, not only at the end. Two kinds of help: the lists in this file are pasted into every writer and wording-editor prompt (models from other vendors cannot call local Skills), and installed specialist Skills are called by the organizer, never copied in here.

| Step | What runs |
|---|---|
| Any card, outline, approval message, publishing-kit line (titles, summaries, quote lines) | `audit_draft.py --card` (plus `--seed` where the seed applies) and the AI-flavor audit |
| Writer: outline, draft, revision, targeted fix (prompts 7, 8, 11, 13) | The Chinese rules and the machine-pattern list above, pasted in |
| Wording editor (prompt 12) | The same lists, plus both scripts' findings as items to judge |
| Before every review round and before the author sees a draft | `audit_draft.py` and the AI-flavor audit |
| Review chain, language step | Report, then polish, then fact check, then both audits again (below) |
| Editor-in-chief (prompt 14) | Reads the latest reports; open blockers or facts added by polishing are must-fix |

**The AI-flavor audit** is the script that ships with the `remove-ai-flavor` Skill (`scripts/audit_ai_flavor.py <file>`), run beside `audit_draft.py`. It catches shells this Skill's script does not: lifting to "the real thing", "in essence", "the underlying logic"; mechanical "first ... then" sequences; lecture-style summary markers; packaging words; an engagement question at the end; dense "very" judgments. Its packaging-word list also hits ordinary business words: a finding on a word the author used in the seed or decision log is the author's vocabulary and stays. If that Skill is not installed, say so in the editor notes; the checks of this file still run.

**The language step** of the review chain, in this order:

1. Report first. Call `dbs-ai-check` (diagnose only: it quotes each hit and names the feature, and rewrites nothing), and put both scripts' findings beside it. The language editor decides which sentences change; findings on the author's own sentences and stance go to the author.
2. Polish only those sentences, one at a time, with `renwei-writing` (it keeps the person behind the text and then checks only the sentences it touched). Never feed the whole article into a "humanizer" pass, which flattens the voice and can alter facts.
3. Fact check after polishing, with the rule in `natural-chinese-copy-core`: a date, number or action that the earlier version did not contain is deleted.
4. Run both audits again and record the before and after counts in the editor notes.

**What to check.** Run both audits on the text the reader or author will see, alone: the article body (the export without editor notes; leave the 参考文章 block out of the AI-flavor audit), or the approval message by itself. Never run them on a file that also holds the author's seed, the restatement records, sources or editor notes: the author's own words would be reported as AI flavor. Save that text to a check file first if needed. Read the report counts and each hit, never only the exit code.

**"No new facts" after polishing** is a sentence-by-sentence comparison of the version before and after: every changed sentence is set beside its original, and any date, number, name, action or experience that was not there is removed. `natural-chinese-copy-core` ships a checker for numbers, dates and versions; it does not see a changed action ("the author wrote" becoming "the author met"), so the side-by-side comparison is the check and the script only helps.

**What the organizer can do decides how far the language step goes:**

| The organizer can | It does | It may not claim |
|---|---|---|
| Call local Skills and run commands | The whole language step above | |
| Run commands, not call Skills | Both scripts, the report from the lists in this file, the side-by-side fact comparison; records which specialists were not used | "Full language step done" |
| Neither (a web chat, for example) | Hands a check package to an agent that has local access, and waits for its report before the next approval (package below) | That any audit ran, until a report comes back |

The check package for the third row: the version before polishing; the polished version to check; the author's seed and the fact table (locked facts); both scripts' reports if any exist; and the lists in this file. The agent must send back both scripts' reports on the polished version and the side-by-side table of every changed sentence (before, after, any date, number, name, action or experience added). Without the version before polishing the fact comparison cannot be done, so a package missing it is not sent.

"No problem found" is a valid result; over-polishing is the same fault as machine flavor (see "do not overdo it" above).

## Second person

Addressing the reader directly helps, but density matters. Around 15 to 25 uses in a 3500-character article reads naturally; far more feels like lecturing. The audit script reports the count.

## Five-layer style system

Grow a house style by borrowing, not copying:

| Layer | Contents | Source |
|---|---|---|
| 0 Floor | AI-assistance disclosure, fact checks, banned words. For each banned word, record the fault, why readers dislike it and what to use instead; reasons work better than bare prohibitions. | Account profile |
| 1 Author voice (single authority) | Three or four voice traits, each with "is" and "is not"; position on four scales (funny or serious, formal or casual, respectful or irreverent, enthusiastic or matter-of-fact); 3 to 5 author-approved final articles on different subjects as models; one sample paragraph showing the normal sentence rhythm | Author style profile |
| 2 Style cards | Structure and moves borrowed from other writers; at most two per article; layer 1 wins on conflict | Configured style-card folder |
| 3 Article brief | Reader, matured judgment, first-hand material; optionally the author dictates the opening paragraph and the model continues | This article |
| 4 Edit evidence | For each article, the AI draft and the author's final side by side with reasons; monthly, any edit type seen three or more times is promoted into layer 0 or 1, and that final joins the model articles | After publishing |

Practices: draft each article in a fresh session; for long drafts written in parts, paste the style layers again (attention to opening instructions fades over long conversations); judge "sounds like the author" by how much the author edits, not by an AI score.
