# Prompt kit

Copy a prompt, fill the angle brackets, paste it into the chosen model. Each prompt asks for answers in Simplified Chinese; change that line if the account writes in another language. Give each prompt only the material it names, pasted into the prompt itself: never give the model a file path and expect it to find the file (in testing, a writer given only paths went to the wrong place and returned one sentence).

## 1. Common-sense floor

Use with two or three models from different vendors during the baseline step.

```text
Answer in Simplified Chinese. Do not search the web.
Question: <the topic question in the reader's words>
Give the mainstream view a well-read business person would give today, in 5 to 8 points, with the usual advice. Do not try to be original. Then list the two points you are least sure about.
```

Whatever all models say by default is common sense. The article must go beyond it.

## 2. Red team (pre-mortem)

Use with a model from a vendor other than the writer's.

```text
Answer in Simplified Chinese.
Here is a judgment we plan to publish, with its key evidence:
<judgment card>
Assume the article has been published and has failed: readers found it wrong, obvious or useless. List the five most likely reasons, the strongest opposing argument stated so well its holder would accept it, and the conditions under which the judgment does not hold. Do not soften. Do not rewrite the judgment.
```

## 3. Cold-reader title test

Give only the reader profile and the titles, never the article. Advisory only: in testing, two models agreed on a title the author could not understand. A title reaches the author only if it passes both scores; any word a cold reader reports as not understood goes to the wording editor (prompt 12), which may then not keep that line.

```text
Answer in Simplified Chinese.
You are <reader profile in one sentence>. You are scrolling on your phone.
For each title below:
1. What do you think it is about? If any word is unclear to you, quote that word exactly and write "not understood". Do not guess what it might mean.
2. Understood at a glance: yes or no.
3. Distinctive: could this title sit on top of many other articles on the same subject? Answer "only this article" or "could be any article", with one line why.
4. Would you open it, and why?
Then pick the one you most want to open that you also understand.
Titles:
<the title candidates, numbered>
```

## 4. Layperson read

Use right after the first draft (it runs early in the review chain), with a model from another vendor, or give the same instructions to a real colleague. Report only; it never rewrites.

```text
Answer in Simplified Chinese. Do not rewrite the article.
You run a small business and are not from <industry>. You read articles on your phone while waiting for a lift.
Read the article below once, as that person, then answer:
1. What did you read? Say it in your own words in two or three sentences, then give the one sentence this article says. Did you know it before?
2. Which facts did you take away? List them.
3. What impression do you now have of the writer?
4. What will you do next because of this article, if anything?
5. Where did you get stuck? Quote every sentence or word that made you pause (jargon, unclear logic, translation-like phrasing, a jump, numbers that do not add up, a "this" or "it" where you could not tell who or what is meant, a work or name you did not know whose it was, a title or subhead you first read as different words), say why, and say what you expected instead. Quote exactly.
6. The article sets out to answer: <the article's question>. Did it answer it? Where?
Also: reading only the title and subheads, did you know what it was about, and would you keep reading?
Also: below are the title candidates. For each, quote any word you do not understand, without guessing its meaning.
Finally: score out of 10 for readability, and the one thing you most want the writer to change.
Title candidates:
<title candidates, numbered>
Article:
<draft body without editor notes>
```

## 5. Structure review

Use two judges from vendors other than the writer's.

```text
Answer in Simplified Chinese. Judge structure and argument only; ignore wording.
For each question answer yes, no or cannot judge, with one line of evidence quoted from the article.
1. Can you state in one sentence what this article says?
2. Is that sentence new to its intended reader (<reader>)?
3. Is there a point where a surface answer is overturned and the reader is taken deeper?
4. Can the reader say what they will do differently, or where they were wrong?
5. Reading only the title, subheads and last section, do you get the judgment?
6. Are opening, development, turn and close each identifiable? Where is the turn?
7. Does the ending answer the opening scene with something usable?
8. Is there a second topic competing with the main one, or a section that repeats another?
9. Evidence: list every outside study, survey, case or quote. For each, name the one sentence in the article it proves; write "proves nothing" if there is none. Does any section carry more than one strong piece of outside evidence, or the article more than about five? Does outside material take the opening, the ending or the main role away from the author's own judgment?
List at most three must-fix structural problems, each with the section it belongs to.
Article:
<draft body>
```

## 6. Fact-claim extraction

```text
Answer in Simplified Chinese.
Split the article below into individual factual claims: every number, date, name, company, quote, study result and event. For each, output one line: claim | the sentence it appears in | the matching item in the research pack, or "not found". Mark anything stated more precisely than its source. Do not judge style.
Article:
<draft body>
Research pack:
<research pack>
```

## 7. Drafting brief (for the writer)

```text
You are the writer for <account>. Write in Simplified Chinese.
Reader: <who, where they are stuck>
The author's original seed (verbatim): <text>
Point map (every seed point, numbered, with its approved fate and the section it goes in): <S1 ... -> section; S2 ... -> section; ...>
Matured judgment: <one sentence>
Article type: <practical how-to / opinion / method / news analysis / integration piece / other: name it>. Rules for this type: <paste its row and extra emphasis from the article-types reference; for an integration piece, also: credit every borrowed point by author and outlet in the body, keep quotes short, our own judgment and choices close the article>
Approved title: <title>
Outline: <approved outline, with a target length in Chinese characters for every section>
Seed points: every point in the point map appears where the map puts it. Do not merge, narrow or drop a point unless the map records the author's decision to; never narrow a point because others have written about it.
Fact table (the only names, numbers, quotes with their Chinese wording, dates and author experiences you may use): <fact table>
The author's own experiences: use only the sentences in the fact table. Never add a trip, a meeting, a feeling, a number or a habit of the author's that is not there; write "[to confirm]" where the article needs one.
Evidence budget: at most one strong outside item per section, about five in the article; people and events before studies; outside material confirms, limits or adds detail, and never takes the opening, the ending or the main role.
Author-supplied material and where each item goes: <list>
Material you may use (and nothing else for facts): <research pack items, pasted in full>
Style: <author voice layer, one model passage>
Chinese rules (paste the output of `audit_draft.py --rules`): <rules>
Machine patterns to avoid (paste the "Machine patterns to remove" list from the plain-writing reference, including its "do not overdo it" paragraph): <list>
Also: one H1; ## subheads written for skimmers; plain words, explain any jargon at first use; normal long and short sentences; no em dash; no single-sentence "not X but Y" reversal; no banned words (<list>); full-width punctuation with curly quotes; no bold; no inline sources; after the body, a block headed 参考文章 listing only complete long-form pieces readers can read (only those the article really drew on, however few; full title, author, platform, date; none if there are none), and the verification list (each fact, what it supports, source, date) goes under the editor notes, never in the body; at most two punchline closers; hypothetical scenes must look hypothetical; never invent names, numbers or approximations; the opening must not describe scenes or groups of people that are not in the material; the author's own experiences are written in the first person ("I"), never as "<author name> said"; the author's own work is described by what was done and tested, without praise or self-deprecation, and a test is never written up as a success; the total length must reach <range>; no chopped strings of short sentences.
Output only the article, then the 参考文章 block if any, then ===EDITOR NOTES===. Under the editor notes, give the verification list and a coverage list: each seed point S1, S2 ... and the paragraph that carries it, or "not covered" with the reason.
```

## 8. Revision brief (targeted fix)

Use when one part needs work and the rest must not move.

```text
You are the writer for <account>. Write in Simplified Chinese.
The author says: <the author's comment, verbatim>
Change only this: <exact sections or paragraphs, and what to do>
Do not touch any other paragraph. These must stay word for word: <quote every locked item, e.g. each approved subhead, and every wording adopted in earlier revision rounds>
The revised article must not be shorter than the current one (<n> characters).
Keep all rules from the drafting brief:
Chinese rules: <audit_draft.py --rules output>
Machine patterns to avoid (paste the "Machine patterns to remove" list from the plain-writing reference, including its "do not overdo it" paragraph): <list>
Output the full revised article only, no preface or notes. Do not call tools.
Current article (full text):
<article>
```

After any revision, diff the result against the previous version to confirm nothing else moved, then run `audit_draft.py` and the AI-flavor audit (plain-writing reference, "AI flavor at every step") again.

## 9. Skeleton read

Give only the title and the subheads, in order. Use a model from another vendor, or a colleague.

```text
Answer in Simplified Chinese.
You have not read the article. Below are only its title and subheads, in order.
1. In one sentence, what is this article saying?
2. For each subhead: do you understand it on its own? If not, what is missing (who, what, change what)?
3. Which subhead would make you stop reading, and why?
4. (If given) Below each subhead are the first and last sentence of its section. Read them in a row: do they make one argument that flows forward, or separate notes side by side? Where does the chain break?
Title and subheads:
<title>
<subheads, one per line, optionally each followed by its section's first and last sentence>
```

If the one-sentence answer does not match the matured judgment, or any subhead needs the body to make sense, rewrite before review.

## 10. Judgment gate

Use before the judgment card goes to the author, with a model from another vendor (required when the writer and the organizer are the same model). It only checks; the author and the agent decide. Paste the collision scan from the research pack; without one, question 6 can only be answered "unverified".

```text
Answer in Simplified Chinese. Do not rewrite the judgment.
Reader: <who>. Judgment we plan to publish: <one sentence>. Its relationship form: <under condition C, A changes B through M, so R>.
Article type: <type>. Confirmed seed and point map (S1, S2 ...): <text>
Collision scan from the research pack (each article: title, outlet, date, main argument, how it was read: full text / fragment / title only; the account's own published pieces read in full, its drafts and ready pieces by title only): <table, or "no scan">
Answer each question yes or no, with one line of reasoning (question 6 with its counts, the seed check with quotes):
1. Is it only an old truth with nothing new attached? A classic principle may be the subject; say what the new situation (AI, the triggering news) changed about it: a condition, a consequence, new evidence or a new way of acting. If nothing, answer yes.
2. Could this reader dismiss it with a one-sentence reply that leaves nothing for the article to do? Give that reply if so. (Being summarizable in one sentence is not a fault.)
3. Does it only describe, with no stance? Would it make the task sound harder and put the reader off?
4. Is its selling point how much the writer installed or built?
5. (Skip for practical how-to and integration pieces.) Is it only a method or a checklist, without an "I thought A; it is actually B" moment for this reader?
6. Using only the collision scan above, put each article in one layer: 1 same subject; 2 same question; 3 same judgment; 4 same structure, evidence and conclusion (layer 4 needs all three together; same structure or evidence with a different conclusion is not layer 4). Do not add articles from memory. Only layers 3 and 4 count against the judgment. Give a count for every layer, zeros included (layer 1: N, layer 2: N, layer 3: N, layer 4: N, could not be placed: N), then how complete the scan was (read in full: N, fragment: N, title only: N; the account's own published pieces scanned or not; drafts and ready pieces read by title only is the rule, not a gap). If the scan is missing or incomplete, answer "unverified", never "passed"; that alone is no reason to narrow the seed or change the topic.
7. Remove every "maybe" and "to some extent": does it still stand? Is it important, new and true for this reader?
Seed check (after the seven): put the judgment beside the confirmed seed. Did any scope or relationship word change (still, also, only, all, no longer, replaces, the one)? Was any seed point narrowed, merged or left out? Answer as a table: the author's sentence, the judgment's sentence, kept, added, removed or changed, needs the author's approval. Quote both sides for each change. If this table cannot be completed, say so: the seed's outcome cannot be "stands" and the card cannot go to approval 2.
```

## 11. Writer: outline, title and subheads

For the writer at step 4 (team's choice: Claude Opus 4.6). The organizer fills every bracket; paste material, never file paths.

```text
Write in Simplified Chinese. Do not read or write files; do not call tools.
You are the writer for <account>. Reader: <who, where they are stuck>.
The author's original seed (verbatim): <text>
Confirmed seed (the author's direction; do not change it): <five-item seed confirmation>
Point map (every seed point, numbered, with its approved fate: kept, deepened, split off, dropped with approval): <S1 ...; S2 ...; ...>
Approved judgment: <one sentence>. Article type: <practical how-to / opinion / method / news analysis / integration piece / other: name it>. Rules for this type: <paste its row and extra emphasis from the article-types reference>
The author's decisions and verbatim comments so far: <list>
Material to arrange (only these facts): <fact table and research points, pasted>
Rules for titles and subheads: <paste the Title and Subheads rules for this article type from the plain-writing reference>
Chinese rules: <audit_draft.py --rules output>
Machine patterns to avoid (paste the "Machine patterns to remove" list from the plain-writing reference, including its "do not overdo it" paragraph): <list>
Write: 3 title candidates in three different forms (for example: one states the conclusion, one is the reader's own question, one is built on a concrete number or event; not one hook reworded three times), each with one line saying what a reader would expect from it; mark the one you recommend and why; the full subhead list; under each subhead, the section's first and last sentence, its target length, and which material it uses; the opening idea and the ending idea; then a coverage list: each kept or deepened seed point and the section that carries it. Do not merge, narrow or drop a point the map keeps; if one does not fit, say so instead of leaving it out.
Where the material does not say something (a number, a step the author took, a mistake they made), write "[to confirm]" instead of inventing it.
Before answering, test every title and subhead:
- Cover the body: can someone outside the industry say in one sentence what this section teaches or claims?
- Can a stranger point at what every noun refers to? No term the article defines for itself, no metaphor the body has not yet explained, no pronoun that needs the section.
- Is the title distinctive: would it fit only this article?
Rewrite any that fail.
```

## 12. Wording editor (keep or change, against the standards)

For the wording editor after any text by the writer (team's choice: Gemini 3.8 Flash). The wording editor is not a review-chain reviewer: it may propose one replacement line for an item that fails a named standard, and it never edits the draft; the organizer decides what to apply.

```text
Answer in Simplified Chinese. Do not read or write files; do not call tools. Do not rewrite the whole text.
You are the wording editor. Below is a text written by another model for <account>, read by <reader>. Check it item by item against the standards below.
Standards: <paste the title and subhead rules for this article type, the opening and ending rules, and the Chinese rules from audit_draft.py --rules>
Machine patterns to avoid (paste the "Machine patterns to remove" list from the plain-writing reference, including its "do not overdo it" paragraph): <list>
AI-flavor findings from the two audit scripts (each one is an item to judge; findings on the author's own words stay KEEP): <list, or "none">
Already approved by the author (do not change; flag only if a hard rule is broken): <list>
Locked items (never change): <list>. Facts may not change or be added.
Words cold readers did not understand (verbatim): <list, or "none">. Any item containing one of these words cannot be KEEP: give a CHANGE, or write "send to author".
For subheads, the cover-the-body test decides: if an outsider could not say what the section teaches from the subhead alone, it is CHANGE, whatever else is true.
For each title candidate, each subhead, the opening, the ending, and each paragraph, give one verdict:
- KEEP: it meets the standards. This is the default. No explanation needed.
- CHANGE: quote the item; name the exact standard it fails; say in one line what is wrong; then write out the complete replacement line in full (the new title, the new subhead, or the new sentence), changed only as much as the standard requires. Advice without the full new line ("make it more direct", "consider rephrasing") is not allowed.
A CHANGE without a named standard is not allowed. "I would phrase it differently" is not a reason. Your replacement must itself meet every standard above, including the length rule for subheads. If everything meets the standards, say so.
Output a table: item | KEEP or CHANGE | standard failed | what is wrong | the new line in full (empty for KEEP).
Text:
<full text>
```

## 13. Writer: revise after the author's comments

The organizer sends this automatically after every author comment; the author never forwards between models. Size the comment first (model-routing reference, "Revisions after the author comments"): a word swap the author spelled out needs no writer; for sentence-size comments use the sentence version below; for a paragraph, prompt 8.

```text
Write in Simplified Chinese. Do not read or write files; do not call tools.
The author read the text below and said, verbatim: <author's words>
Revise the full text to answer exactly that. Change only what the comment concerns; keep everything else, including these locked items word for word: <list>. Do not add facts beyond: <fact table>.
The result must not be shorter than the current text (<n> characters) unless the author asked for cuts.
Chinese rules: <audit_draft.py --rules output>
Machine patterns to avoid (paste the "Machine patterns to remove" list from the plain-writing reference, including its "do not overdo it" paragraph): <list>
Output: the full revised text, then a list of what changed and how each change answers the comment.
Current text:
<full text>
```

Sentence version (the author pointed at a few sentences without giving wording):

```text
Write in Simplified Chinese. Do not read or write files; do not call tools.
The author said, verbatim: <author's words>
Rewrite only these sentences, one replacement each, so they answer that comment: <numbered sentences, each with the paragraph before and after it for context>
Keep facts as they are; add none beyond: <the facts these sentences use>. Keep these word for word: <locked items and wording adopted in earlier rounds>.
Chinese rules: <audit_draft.py --rules output>
Output a table only: number | original sentence | new sentence | how it answers the comment.
```

## 14. Editor-in-chief review (before approval 4)

Use after the review chain, before the draft goes to the author for approval 4. One model from a vendor other than the writer's, able to read long input. Flags only.

```text
Answer in Simplified Chinese. Do not rewrite the article.
You are the editor-in-chief. You are checking a nearly final article against what its author asked for and already confirmed. Use only the material below; if something cannot be judged from it, say "cannot judge".
The author's original seed text (verbatim): <text>
Confirmed seed and numbered point map (S1, S2 ...): <text>
Judgment card, including what happened to each seed point: <text>
The author's decisions and verbatim comments, in order: <decision log>
Account profile essentials: <reader, banned words, length, title rules>
Standards: <good-article questions; title and subhead rules for this article type; publishing kit list>
Article (title, body and 参考文章 block): <text>
Verification list (from the editor notes): <text>
Image list and publishing kit, if they exist yet: <text or "not yet made">
Audit reports (`audit_draft.py` and the AI-flavor audit, latest run): <text>
First, before anything else, two checks in this order:
0a. Is the original seed fully in the point map? Read the author's original seed text and list every distinct point it makes. For each, name the S-number that carries it. Any point with no S-number is "missing from the point map": report it and stop; do not review further.
0b. Is this the article the author asked for? For each seed point S1, S2 ..., where is it in the article: kept, deepened, split into another article, or dropped? Was each drop approved in the decision log? Did the direction, the article type or the reader change? If this fails, report it and stop; do not review the writing.
Then answer each, with the sentence or file line that supports your answer:
1. Answered title: what question or claim does the title set up, and which paragraph answers it? Does the ending answer it plainly?
2. Kept promises: for each subhead, does its section deliver what the subhead says?
3. Drift: compared with the confirmed seed and judgment card, did the direction, the article type or the reader change?
4. Structure: are the opening, development, turn and close each clear? Does the reader leave with one judgment thought through and one action to take?
5. Facts: list every number, name, quote and date not found in the material above.
6. Author's decisions: did anything the author decided get changed or dropped?
7. Images and kit (if they exist): is anything missing or against the list (screenshot list, paired covers, captions without links, the two declarations for the author)?
8. Title and subheads against the finished body: can a stranger point at every noun? Is any metaphor used in a title or subhead before the body explains it? Covering the body, can an outsider say what each section teaches?
9. The author's own material: is any item listed at seed confirmation flattened into a generic statement, or missing?
10. AI flavor: do the two audit scripts' reports (pasted below the article) still show open blockers, or did a polish pass add a date, number or action the earlier version did not have?
Then three editor's questions, one line each: Is this worth publishing? Does it belong on this account (its readers, its topic lines, its tone)? Would the target reader forward it, and to whom?
Then list problems as "must fix" or "suggest", each with the standard it breaks. If there is no problem, say so.
```

## 15. Target reader

Use alongside the layperson read (prompt 4), with a model from another vendor. The layperson hunts stuck words; this reader judges whether the article speaks to the account's real audience. Report only.

```text
Answer in Simplified Chinese. Do not rewrite the article.
You are <the account's reader from the profile, in one or two sentences: who, what they do, what they worry about this month>. You read on your phone.
Read the title and the article once, as that person, then answer:
1. From the title alone, would you open it? Why or why not?
2. Does the opening describe a situation you recognize from your own work? Quote the line that did or did not.
3. What is the one thing you take away? Is it new to you?
4. What will you do differently, or say to someone, because of it?
5. Would you forward it? To whom, and with what one-line comment? If not, why not?
6. Where did it stop speaking to you (too basic, too technical, not your problem)? Quote the passage.
Title: <title>
Article:
<draft body without editor notes>
```
