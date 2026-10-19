# The four stops

The author is asked at most four times: topic (only when they had none), the line, the opening, final. Everything else runs without asking. Questions that can wait go into the next stop's message. After every answer, append the author's decision and their verbatim words to the decision log in the article folder; the fact table, the language role and the seed check read it.

## The shape of every message

Run every check first, then show the result in plain words, never the machinery:

1. One plain sentence: what I recommend, in the author's terms.
2. One natural question: "Is this what you mean?"
3. At most four small decisions, one line each, each with my recommendation.
4. Where the full record is: a link, written in the reply text itself, to a file that exists and that the author's own tool opens with one click; text that appears only in tool output has not been shown. A whole article is linked, not pasted into the reply. When the configuration sets a `preview_folder` (the author's tool cannot open the article folder), copy the file there and link the copy, named by the full title with its punctuation as is plus a plain suffix after a hyphen (`<title>-Opus写的初稿.md`), with no added full-width brackets.

No bold. Run `audit_draft.py --card` on the message (`4-writing.md`, "Mechanical checks"). The judgment record, the point-map table and the review sheet stay in the article folder and are shown when asked. Name things by what they are, in the author's everyday words; a label the organizer made up ("the ten questions", "draft A") means nothing to the author. Never make the author compare abstract labels or near-identical judgments, or carry text between models.

Any other request for the author's go-ahead (overwrite a file, re-export, download, spend money) says in plain words what will be done, why, and which file it touches, never a bare command word.

## Stop 1: topic (only when the author had none)

Three topics, six lines each (`1-topic.md`), and the source receipt in one line. One question: which one. The topic the author picks is the seed.

Two batches in a row rejected means the scan failed, not the author: invalidate both, widen the source families or the account's own material, and scan again. The author is not asked for the thesis here.

## Stop 2: the line

One short message the author can read in a minute (`write.md`, "The line"):

0. **The hook first** (`write.md`, "The hook"), its own short message before the rest when the author is waiting: the one sentence the whole piece says, then four title-and-opening candidates quoted in full with their hook named and one recommended. The author picks; nothing is drafted before that.
1. **Four lines first** (`write.md`, "The line"): the core question; the reader's shift ("读者原来以为……，看完知道……"); the opening scene; whether the material is enough.
2. **The line**: one plain paragraph on how the piece moves from its first paragraph to its last, what the reader wonders at each turn and how each part hands the reader to the next, with the shape named (building, parallel cases, question by question). Under it, one line per step on what it stands on; a step with nothing under it is said plainly. Not a list of subheads, not four labelled boxes. When a genuinely different shape would also work, one or two sentences on how it moves and what it changes.
3. **Three titles**, each telling the reader what the piece is about and carrying one thing the reader does not already know; one recommended with a reason in one line. A title any reader could have said first fails.
4. **What I will give the writer**: which exemplars; the experiences, cases and numbers are already named under the steps of the line.
5. **At most two decisions**, one line each with my recommendation, only when they change the piece (a real story the author might add, a question research left open). When the seed holds several separate lines, the line follows the one the seed's own doubt points to, and one line lists the others as "这几条可以另写一篇"; the author decides.

If research overturned the core claim, the message is short: the evidence, one proposed new direction, and the question.

The author's answer goes to the writer in their own words. "Use your recommendation" for the title means it goes ahead marked tentative until stop 4.

## Stop 3: the opening

After the organizer has read the draft whole and found it reads well, and checked that the opening the author chose at stop 2 is still there and still grips: the title and the first 300 characters, quoted in the message, and one question: does the first sentence make sense, would you read on. A link to the whole draft for the author who wants it. An opening that fails is rewritten before anything else. When the author asked for two writers, show both openings and let the author pick by reading; the organizer gives no verdict on whose prose is better.

## Stop 4: final

Sent after the revision and the organizer's whole read. It holds: the full article as a link the author's tool opens with one click (a `preview_folder` copy when needed), before any question; what changed since the opening, one line per change (paragraph, before, after, why), ordered: changes the author asked for, then important, then the rest, and findings left unchanged listed with their reason; the author names any line to revert and it is reverted; any fact still marked [待确认] and anything the draft says about the author that needs his confirmation; and three title candidates for the finished article with the current one among them. The author picks the title again.

The author's 定稿 sentence goes verbatim to the export as `--approval`. Comments instead of 定稿 are revised by size (`6-deliver.md`). When the author edits the text by hand, save the writer's draft and the author's version and write the edit pairs (`write.md`, "After 定稿").
