# Step 7: Review

## Iron rules

1. **Writer and reviewers come from different vendors** (`models.md`).
2. **Reviewers only flag; they never rewrite.** Machine-rewritten wording never goes straight into the draft; the writer rewrites from the author's position. Reviewers cite the sentence and the rule it breaks, and give a direction for the fix that invents no facts or experiences.
3. **Findings about the author's own experiences or the article's stance go only onto the author's review sheet.** A contradiction with the author's words counts as must-fix, but it too waits on the sheet: the author decides, and only then does it go to the writer, with the author's words quoted. Nobody deletes or softens such a passage automatically.
4. Send drafts to reviewers without the author's identity or preferences, and use the configured interface's isolation controls where available (`models.md`, "Calling another vendor"). A fresh working folder alone does not hide global settings; verify what remains visible and record any limit on the blind review. When the writer disputes a finding, the reviewer shows evidence before changing its verdict.
5. **Only hard facts and copying force a change.** Every other finding is advice the organizer adopts when it makes the piece more gripping or easier to read. "Do not overstate" applies to facts (numbers, events, what a source said); it never asks for a softer stand, a hedge on an argued claim, or a sharp line turned into advice.
6. The author's instinct can veto: title, subheads, opening and ending pass only if the author understands them at a glance.

## The roles

One job each, no overlap. The counter runs once before writing; the structure editor checks the line before stop 2; the others (●) run together on the draft that passed stop 3; after the revision come the after-revision read and then the seed check.

| Role | The one thing it checks | Gets |
|---|---|---|
| Counter (step 3) | Holes in the judgment | `2-research-and-counter.md` |
| Structure editor (step 3) | The line: does each step follow from the last, does it carry the reader's shift, does each step stand on its material, the titles | prompt 4 |
| Managing editor ● (two vendors) | The draft as a whole, from a map of every section | prompt 10: one exemplar, the reader line, the body; nothing else |
| Reader ● | Where a reader outside the trade, who uses AI at work, gets stuck | title, body |
| Attraction reader ● | Would a stranger open it, stay, forward it; what went soft | prompt 13: title, body |
| Originality check ● (seed from someone else's article only) | Where the draft sits too close to the source article | prompt 14: the source article, the draft |
| Expert ● | Is it right, as a practitioner in the topic's field knows it today | draft, fact table |
| Facts and risk ● | Is it traceable and safe: claims against sources; author's experiences against the author's words; what may not be said | draft, fact table, author's words |
| Language and flow ● | Machine flavor and wording; every place the reading jolts | draft, both audit reports |
| Good-article check ● | The account's own standard of a good article, check by check | prompt 11: the standard's checks, the body |
| After-revision read (after the revision) | Faults the revision brought in | prompt 12: the revised body |
| Seed check (after the revision) | Is it the author's article, with the author's points and key words | files, listed below |

No role gives the final verdict on whether the article is worth publishing or will be forwarded. The attraction reader's opening and sharing judgments are advice, not measured reader response; whether it ships and whether it is worth forwarding is the author's call.

**Good-article check.** Runs when the configuration names a `good_article_standard`. One model of a vendor other than the writer's gets the standard's checks (the configuration may name which parts) and the body, and answers every check 过、不过 or 判不了, each with the quoted sentence it rests on; it gives no overall verdict. Checks about how the reader will feel (would I click it, how it feels to finish, would I forward it) are not sent to the model: they go to the author at stop 4. A 不过 enters the merged list as important. The managing-editor card (prompt 10) stays unchanged beside it, because it is calibrated.

**After-revision read.** A revision can introduce a repeat, a broken transition, a dropped source or qualifier, or an intrusive parenthesis. One model of a vendor other than the writer's reads the revised body alone and marks only these (prompt 12); it judges nothing else and does not see the review list. Its marks go to the writer as a sized revision (`6-deliver.md`). In the every-five-articles count, a read that caught nothing in five articles goes on the list for deletion.

**Managing editor.** The calibrated card is prompt 10, sent unchanged to two models of vendors other than the writer's (`models.md`) at the same time. It maps every section in one line before judging, then checks set-ups never paid off, paragraphs written for another reader, every case (which sentence it proves, whether it sits in the right section, whether the author's own judgment follows), the most valuable part and its position, the ending against the opening, gaps in the argument, cases told without why, switches of person, metaphors drawn from different fields, whether the author is present, abrupt transitions, unweighted layers, a paragraph suddenly denser than its neighbours, whether the first two paragraphs speak to the reader's own situation, and three places a reader would drift compared with the exemplar. With no exemplar of the article's type, the exemplar is left out and that comparison is answered "未做": a mismatched exemplar produces misplaced findings. It gives no score and no verdict. Merge the two independent reports as follows:
1. Findings both report go first; a finding from one is kept and marked "one reviewer".
2. A finding that asks to delete the author's own view or experience, swap in a different case, or write it "like the exemplar" goes only onto the author's review sheet (iron rule 3), never straight to the writer. Harsh wording in a finding is dropped; the substance stays.
3. Three faults also stay with the author's reading, named in the stop 4 message: two sections saying the same thing, a sudden switch of person, and an abrupt jump between paragraphs. The flow read checks for these too.

**The card's list of kinds grows.** A model catches a kind of fault mostly when the card names that kind (a calibration hypothesis to verify on new articles), so item seven of prompt 10 is kept as a list that grows with editing experience. When the author or an outside editor finds a kind of fault the managing editors missed, the maintainer adds one general question for that kind to item seven ("is there ...?"), never this article's answer; a question that has caught nothing for several articles goes onto the every-five-articles list ("Feedback candidates") for the author to decide, so the card stays short. Each change is recorded in the Skill's provenance and checked against the next real article.

**Reader.** Someone outside the article's trade who uses AI at work, like the account's reader, reading on a phone (a reader who knows nothing of AI would flag words this account's readers use every day): say in your own words the one sentence the article says (the organizer lays it beside the stop 2 sentence "读者原来以为……，看完知道……"; a mismatch is important); quote every word or sentence that made you pause (jargon, unclear logic, a "this" or "it" with no clear referent, a work or name you did not know whose it was, a title or subhead you first read as different words, numbers that do not add up) and why; did the article answer the question its title sets up. A stuck word in the body is a must-fix, not a question for the author; words the account's reader uses every day stay (`4-writing.md`, hard rule 4). A stuck word in the title goes to the author's review sheet, because after stop 2 the title is the author's choice.

**Expert.** Is it right? The topic picks the expert: a marketing practitioner, a finance practitioner, or an applied-AI practitioner. It checks whether what the article says holds as the field knows it today: outsider mistakes, outdated facts and judgments, places where peers would see through the piece. Matching claims to the fact table belongs to facts and risk. Every item carries a source or a concrete example (a named case, a dated number, a product behavior); an item without one is not counted. It works best with web access; without it, it says which items it could not check.

**Facts and risk.** Is it traceable and safe to say? Whether the field's knowledge is current belongs to the expert. It checks hard facts (who, what was done, numbers, quotes, dates, outcomes, whether an event happened); a fitting feeling, a scene, a tone or a vivid detail that fits what happened is how a person writes and is not a fault. It flags an invented event or conversation, or a change to what was actually done.
- Split the draft into single claims (every number, date, name, company, quote, study result, event) and match each to the fact table or its source; flag anything stated more precisely than its source; check that numbers add up. Everyday description is not a claim (`4-writing.md`, after-check item 2).
- One case told as a rule: a single case, company or test written as "大家都这样""一定这样", or a guess written as proven. Quote the sentence; the fix is to name the case as one case, or to state the guess as a guess.
- A number with no source the writer can point to is softened ("提升明显"), cut with its sentence, or marked by how sure it is ("一种解释是""有团队反映"); it never stays as it is on the bet that nobody checks. A core claim the article has argued with solid evidence may be stated plainly; do not ask for layers of "maybe" on it.
- Check the strength of every promise and recommendation against its source and the author's words. "May", "can help" and "tends to" must not become "will", "guarantees" or "always"; "generated a plan" must not become "finished the work"; a condition or exception that a rewrite dropped is the same fault. Quote the sentence and both wordings.
- The author's own experiences must match the author's words. A contradiction, or someone else's story told as the author's, is must-fix and follows iron rule 3; an item the material cannot confirm becomes a "please confirm" question for the author, not a deletion.
- Any sentence that reveals the article was drafted with AI, or describes the writing process or writing tools, is must-fix.
- Risk: reputation (named companies and people, negative claims), advertising law, platform rules. Red flags go to the author's sheet.
- The author spot-checks high-risk items (numbers, negative claims about companies).

**Language and flow.** Machine flavor and wording, then the flow read, in this order.
1. Report first, with the findings of `audit_draft.py` and the AI-flavor audit beside it (`4-writing.md`, "Mechanical checks"); An independently installed AI-flavor checker, when available, diagnoses and rewrites nothing; if unavailable, record that optional tool as missing and perform the language review without claiming an automated check. The role judges each finding; iron rule 3 covers findings on the author's own sentences or stance.
2. Wording: each sentence that breaks a named rule (the Chinese hard rules, the machine patterns, the title and subhead rules) is quoted with the rule it breaks. A sentence that meets the rules is left alone; "I would phrase it differently" is not a finding.
3. The flow read, a separate call with no rules (prompt 8, second text): read from the first sentence to the last and mark every place the reading jolts: an unclear subject, a paragraph that does not follow from the last, a long modifier, report-speak, the same point said again, a stretch that lectures. The standard is smooth reading without a jolt. A flow read complements rule-based checks; its findings are still advice, not proof of reader response.
4. Flagged sentences are fixed by the writer one at a time (`renwei-writing` keeps the person behind the text); the whole article never goes through a "humanizer" pass. After the revision the organizer compares every changed sentence with its original: any date, number, name, action or experience that was not there is deleted (`natural-chinese-copy-core` checks numbers, dates and versions; it cannot see a changed action, so the comparison is the check).
5. Run both audits again and record before and after counts in the editor notes. "No problem found" is a valid result; over-polishing is the same fault as machine flavor.

An organizer that can run commands but not call Skills runs both scripts and the comparison and records which specialists were not used, never claiming a full language check. An organizer with neither hands a check package (the version before the revision, the revised version, seed, fact table, both reports) to an agent with local access and waits for its report.

**Seed check.** One model able to read long input, working from files, not the conversation: the author's original text, the confirmed point map, the decision log (every decision and the author's verbatim comments), the article. In this order:
1. **Is the author's original text fully in the point map?** List every distinct point the text makes and name the S-number that carries it. A point with no number is "missing from the point map": report it and stop, because everything checked against an incomplete map passes falsely.
2. **Is this the article the author asked for?** For each S-number: kept, deepened, merged into another passage, split into another article, or dropped with the author's recorded approval. Did the direction, the type or the reader change? Was any decision the author made changed or dropped? If this fails, stop here and the author decides.
3. **Are the author's key words still there?** List the three to five words that carry the author's original text (the terms the author kept using) and find each in the article. A key word worn away in revision ("Token" became "usage") is must-fix.
4. **Not carried by the source's frame**: the original material (someone's video, article, trending topic) is a springboard; the article does not fight the source author's battle in their framing.

**Outside editors.** An editor outside this Skill (a person, or a service the author uses by hand such as the 得到大脑 writing panel, which has no interface for agents) is the author's own control group. Its findings enter like any reviewer's: by the merge rules above and iron rule 3. A suggested fix that supplies experiences, clients or scenes for the author is a direction only; the experience itself comes from the author's words. Save its words verbatim into the article folder as they arrive. Read its findings beside ours and add any fault it caught and we missed to the feedback candidates.

## Running step 7

1. Run both audits on the picked draft; fix blockers first.
2. The two managing editors, the reader, the attraction reader, the expert, facts and risk, language and flow, the good-article check and, when the seed is someone else's article, the originality check review at the same time and return findings only.
3. Structure check (skipped when there is no approved line, as in a review-only request; the maps then go to the author): the organizer lays each managing editor's section map beside the line as the author approved it at stop 2 (with every change the author made there) and the title. A step of the line missing, a section saying something the line does not, or a title the article never comes round to (the body or the ending should hit it by the last paragraph; the ending need not be where it happens) is a structural finding (see the order below).
4. The organizer merges all findings into one list (below, "Merged list"). The author's notes from stop 3 are quoted verbatim; a finding that conflicts with one of them is listed as not adopted.
5. The writer revises once, working down the list.
6. The organizer runs the before-and-after comparison and re-runs both audits.
7. The after-revision read runs once on the revised body; its marks go back to the writer as a sized revision.
8. The seed check runs once. Its must-fix items go to the writer as a sized revision (`6-deliver.md`); the result, the open items and the review sheet go to stop 4.

A structural finding that sends the draft back to the outline is settled before any sentence is fixed.

## Findings

Each finding has: the paragraph number; the quoted sentence (under 60 characters); the problem and the rule it breaks; its severity; one line on what fixing it changes for the reader (what they will understand, stop misreading or no longer be exposed to; never a number or percentage); a direction for the fix. No problem means saying so.

| Severity | The question | Typical |
|---|---|---|
| **Must fix** | Can you name a rule, a fact-table line or an author decision this sentence breaks; does it leave the title's question answered nowhere; or would it leave the reader believing something false? | A name, number or quote not in the fact table; numbers that do not add up; an author experience not in the author's words; a seed point dropped without approval; the title answered nowhere; a subhead failing the cover-the-body test; unexplained jargon; an audit blocker |
| **Important** | No rule is broken, but the reader loses the main line or takes away the wrong one | Two sections saying the same thing; a set-up never paid off; a case that proves another section's point; the most valuable part buried; an ending the body never set up |
| **Optional** | Neither | A long sentence; one reader's preferred word |

List every must-fix; at most three important and optional findings together per role, except the managing editor, whose card sets its own limit of twelve. Reader reports, managing-editor reports, flow reads and the claim list carry no severity of their own: the organizer grades them with this table and quotes the reader's words.

**Merged list.** Its first line is always: "锋利的话、冲突、钩子一样不许磨软；下面改的是事实、抄袭和读着卡的地方，不是语气。" Hard-fact and copying findings are must-fix; every other finding is listed only if the organizer adopts it, with one line on why (more gripping, easier to read), and findings that would flatten a stand are set aside on the review sheet. Written so the writer can fix everything in one revision, because a revision that needs another round is where time goes. The order: the author's notes from stop 3; structural findings (structure check, anything that sends the draft back to the outline); must fix, false or unsourced content first; important; optional. Within each group the finding that hurts the reader most comes first. Every line names the paragraph to change and the direction of the change, in plain words with no process words (`prompts.md`, "Every brief"). No line asks the writer to drop a source the fact table holds, and nothing the author cut comes back. Findings that contradict each other are settled by the organizer before the list goes out (the author's words win, then the profile, then the reviewer with evidence); the writer never receives a contradiction to resolve. A contradiction that touches the author's own experiences or the article's stance is never settled by the organizer: both findings go onto the author's review sheet (iron rule 3). Every finding the organizer sets aside gets one line on the review sheet: what it said and why it was set aside. Optional findings are marked "可改可不改": the writer may leave one as it is and says in one line why (it keeps the voice; it carries a point). Findings of one kind (the same rule, the same problem) share one line with the count, one "what fixing it changes" line and the sentences listed under it. A finding that conflicts with an author decision or the profile is listed as not adopted, with the decision named. Author edits win; if one conflicts with a hard rule, apply it and point out the conflict.

**Revising.** The same writer gets the merged list, the line and its own full text, and rewrites whole sections where the list points, keeping the voice; it does not patch sentence by sentence, to keep the article coherent. It revises once per round; each change names what was wrong at that spot, and each optional finding it left names why; uncertain changes are marked "revertible", and on a second pass the right move is often to restore what the first over-edited. After every round check that the original meaning and force are still there. Two rounds without convergence on the same issue go onto the author's review sheet, not into a third round.

## Review sheet (one page for stop 4)

In the article folder: the seed-to-final map (each S-number and where it ended up); the seed check's and managing editors' findings and what was done with each; open items first, ordered so the first three lines are the three to deal with first, then adopted and not adopted ones with reasons; unresolved disagreements; risks; the note "no part only this author could write" if the author wrote without own material; the good-article check (each 不过 and what was done with it, and the checks left to the author); sources; this article's feedback candidates.

## Feedback candidates (every article)

At the close of every article write one line per place the author rejected something or we withdrew our own work: the problem sentence verbatim | what happened and why | where in this Skill the fix belongs. Three standing lines appear even when nothing was rejected: the seed's outcome (stands, partly wrong, overturned; did the author agree); which title the author picked at stop 2 and at stop 4, and why; when two writers drafted, which draft the author picked at stop 3, and why. Sessions that use the Skill write candidates and do not edit its files; the maintainer merges recurring ones in one place and deletes old rules that no longer earn their place.

**Every five articles**, the maintainer lists the rules, bottom lines and managing-editor questions that none of those five articles triggered, and the author decides which to delete. A process that only adds grows heavier with every article.

**Rejected changes.** When the maintainer revises this Skill, each change the author rejects gets one line in the maintainers' record of why the rules exist: the change, why it was rejected, the date. The next revision reads these lines first and does not propose the same change again.

**One class per version.** A revision fixes one class of problem where it can, and the next real article checks it before the next class is changed. Writing has no automatic score, so the real article is the check.
