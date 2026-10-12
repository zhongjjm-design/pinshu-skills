# Review chain

## Iron rules

1. **Writer and reviewers come from different vendors.** Models from one vendor make similar mistakes, and a judge tends to over-rate text that shares its own habits. Several sub-agents of the same model agreeing is not cross-validation.
2. **Structure before sentences.** If the structure has a large hole, stop; do not polish sentences in a draft that needs rebuilding.
3. **Reviewers only flag; they never rewrite; the author decides.** This is a hard rule.
   - Reviewers (every step in the table below, and the editor-in-chief) list problems and give no rewritten text. Machine-rewritten wording never goes straight into the draft; the writer rewrites from the author's position.
   - The wording editor is a different role, not a reviewer: for an item that fails a named standard it may propose one replacement line, changed only as far as that standard requires. It never edits the draft; the organizer decides what to apply (see "Wording editor inside the chain" below).
   - Findings that touch the author's own experiences or the article's stance go onto the author's review sheet only. Nobody deletes or softens them automatically. In testing, one reviewer proposed cutting the section on the author's own experience, and another asked to soften the core judgment.
   - Every finding is marked adopted or not adopted on the review sheet, with the reason.
   - After every revision round, check: are the original meaning and force still there?
   - Why process and not prompting: a study from April 2026 (arXiv 2604.22142, abstract only) found that when models edit human writing they make it more formal, more abstract and more neutral, and asking them to "keep the voice" only reduces the drift without reversing it.
   - Send drafts to reviewers without the author's identity or preferences, so they do not flatter. When the writer disputes a finding, the reviewer must show evidence before changing its verdict.
4. **The author can veto on instinct, and owns the title points.** Title, subheads, opening and ending pass only if the author understands them at a glance; model judges are advisory here.
   If the author feels something is off, the draft does not ship, whatever the checks say. The author's review sheet links every source.

## Steps

| Step | Task | Who | Passes when | If not, return to |
|---|---|---|---|---|
| 0 Spec | Account, reader, the change wanted, type | Agent drafts | Reader and change are concrete | |
| 1 Seed | Seed confirmation: the author's text verbatim, five-item restatement, numbered point map, the author's own material, article type. With no seed only: 3 to 5 topic cards first (a topic editor, a session other than the writer's), then the picked card is confirmed the same way | Organizer | Every point in the author's words has a number; the author's material is listed | Ask the author |
| Approval 1 | Confirm the seed and point map (with no seed: pick a card, then confirm it) | **Author** | | |
| 2 Research | Research pack with status labels; three lanes (collision, cases for and against, opposing evidence) | Researcher with web access; three helpers in parallel if your tool can dispatch them, otherwise one after another | Every item sourced and labeled | More research |
| 3 Judgment | Five-step maturation; the seed is shown only with its open questions until research is done | Agent organizes; red team from another vendor; discussion with the author | Five maturity tests pass | Step 1, 2, or keep growing |
| Judgment gate | Relationship sentence and the seven questions (topic-and-judgment reference) | Agent, plus a model from another vendor with prompt kit 10 (required when the writer is the organizer; one-model fallback in model-routing) | Relationship sentence written; seed-against-judgment table and the `--seed` audit done, every flag shown to the author; all seven questions pass. Question 6 "unverified" is not a pass: the gate stays open on it; the flow goes on only if the author, told at approval 2, accepts the gap | Rethink the direction with the author |
| Approval 2 | Confirm the judgment | **Author** | | |
| 4 Outline and title | One-page outline; title and subheads; cold-reader test as advice only | Writer drafts; structure editor checks; the author reads | Title plus subheads, read alone, tell the argument; the author understands each at a glance | Step 3 |
| Skeleton gate | Body, outline flow, title, subheads, opening, central concept, ending (plain-writing reference); skeleton read with prompt kit 9 | Agent; structure editor from another vendor | Every check passes | Step 4, or step 3 if the judgment breaks |
| Approval 3 | Approve outline and title | **Author** | | |
| 5 Draft | Write from the outline with style layers 0 to 3, using the fact table locked at approval 3 (confirm the writer received that version); first job on the draft is to check every fact against the table | The writer (the author's named choice, or the configured one); optional second writer from another vendor | Audit script has no blockers | |
| 5a Title and subhead re-check | Against the finished body: the noun test, the metaphor rule, the cover-the-body test (plain-writing reference, "Re-check after drafting"); change only what fails | Organizer, with the wording editor | Every line passes | Step 4 for that line only |
| 6 Layperson read | Moved early: it caught a number that did not add up and a core concept never explained, the most useful of three review rounds in testing. Six fixed questions plus the title candidates (prompt kit 4, adapted from persona-write's cold reader; page read); hunts jargon, stuck points and numbers that do not add up; report only | A model from another vendor, or a real colleague outside the industry | No stuck points; the article's question is answered | Sentence or structure fixes |
| 6a Target reader | Plays the account's actual reader from the profile (for example people who use AI at work, or people who run businesses): would I open it, does it speak to my situation, what will I do, would I forward it and to whom (prompt kit 15); report only | A model from another vendor | The reader recognizes the problem and leaves with something to do | Judgment or outline, through the author |
| 7 Structure review | Structure and argument only, no wording; includes the natural-ending-point cut, the evidence budget, and for every citation the sentence it proves (a citation that points to nothing is deleted) | Judges from two vendors other than the writer's; yes/no questions with "cannot judge" allowed | One-sentence test; good-article questions 1 to 4, 6 and 10 to 13 | Step 4 or 3 |
| 8 Fact check | Split the draft into individual claims, match each to a source | Researcher with web access; the author spot-checks high-risk items (numbers, negative claims about companies) | Every claim matches a source | Writer revises |
| 9 Risk | Reputation, advertising law, platform rules | Compliance role; red flags go to the author | Checklist passes | Writer revises; serious issues go to step 3 |
| 10 Language | Report first (`dbs-ai-check` plus `audit_draft.py` and the AI-flavor audit); the editor decides which sentences change; polish only those with `renwei-writing`; check that no date, number or action was added (`natural-chinese-copy-core`); re-run both audits. Order and fallbacks: plain-writing reference, "AI flavor at every step" | Language editor | Layer 0 of the style system passes | Sentence fixes |
| 11 Skeleton re-read | Someone who has not seen the body reads only the title and subheads and states the point (prompt kit 9) | A model from another vendor, or a colleague | One-sentence summary matches the judgment | Structure fixes |
| Editor-in-chief review | After the review chain, before approval 4 (see below): first the original seed against the point map, then the point map against the article | A model from a vendor other than the writer's | Question 18 passes; no must-fix left open | Seed confirmation (a point missing from the map), judgment (not the commissioned article), or the relevant step |
| Approval 4 | The full draft that passed the editor-in-chief review, openable; one-page review sheet in the article folder: the seed-to-final map (each seed point and where it ended up), the editor-in-chief findings and what was done with each, unresolved disagreements, risks, the good-article question 5 note if the author proceeded without own material, sources; this article's feedback candidates | **Author** | The author decides | The relevant step |
| Images and publishing kit | Only after the editor-in-chief review confirms this is the commissioned article and the author approves at approval 4; never while the direction is still open | Organizer and the visual Skill | Kit complete | |

## Wording editor inside the chain

From step 4 onward, every reader-facing text is written by the writer and then checked by the wording editor before the author sees it (the full sequence is in the model-routing reference, "Writer, then the wording editor"): items that meet the standards are kept as written; only items that fail a named standard get a proposed fix; the organizer applies accepted fixes and checks locks, facts and rules. Review-chain reviewers still only flag; when a finding is adopted, the fix goes back to the writer with the finding quoted.

## Editor-in-chief review (before approval 4)

This was the "final check" of version 1.1.0, raised to an editor-in-chief's review. It runs after the review chain and before approval 4, so the author signs off a draft that has already been checked against the commission; images and layout come later.

- **Who**: one model from a vendor other than the writer's, able to read long input (team's choice when Claude wrote the body: Gemini 3.8 Flash or Kimi K3).
- **Reads**: files, not the conversation: the author's original seed text, the confirmed restatement and point map, the judgment card, the decision log (every approval and the author's verbatim comments), the account profile essentials, the standards (good-article questions, title and subhead rules for this article type, publishing kit list), the article, and the image list and kit if they already exist. It gets the author's decisions, not the author's identity or preferences.
- **Checks, in this order** (prompt kit 14):
  1. **Is the original seed fully in the point map?** Read the author's original text and list every distinct point it makes; for each, name the S-number that carries it. Any point with no number is "missing from the point map": report it and stop, because everything checked against an incomplete map passes falsely.
  2. **Is this the commissioned article?** Against the point map: is every point kept, deepened, split or dropped with approval; did the direction, type or reader change? If this fails, stop here: the rest does not matter until the author decides.
  3. Then whether it is written well: the title is answered; every subhead's promise is kept; the title and subheads re-checked against the finished body; structure and "the reader gains something"; facts outside the material; the author's decisions intact; images and kit complete (if they exist).
  4. **Three editor's questions**: is this worth publishing at all; does it belong on this account (its readers, its lines of topics, its tone); would the target reader forward it, and to whom?
- **Delivers**: one list, "must fix" or "suggest", each with the standard it breaks and the sentence quoted, plus one line on each of the three editor's questions. No rewriting. The author decides; adopted fixes go to the writer.

## Review notes format

Each finding: paragraph number; the original sentence (quoted, under 60 characters); the problem; "must fix" or "suggest"; a direction for the fix that does not invent facts or experiences. Must-fix is only for real faults; at most three suggestions per role. Wording and AI flavor are raised only by the language role. If there is no problem, say so.

## Merge rules

- The writer revises once per review round, addressing must-fix items first.
- Once a full draft exists and the author criticizes it, revise the full draft and hand back the complete article; keep the good paragraphs and evidence, and append a short change note. Go back to the outline only when the judgment itself is overturned. Do not answer criticism with a list of new subheads or a new outline; the author cannot judge them outside the article.
- Every change must name what was wrong in the original at that spot; mark uncertain changes "revertible". On the second and third pass, the right move is often to restore what the first pass over-edited (`renwei-writing`).
- Suggestions that conflict with the account profile or an earlier author decision are not adopted; note why.
- Author edits win. If an author edit conflicts with a hard rule, apply it and point out the conflict in the notes. Do not quietly revert an earlier author decision.
- Two rounds without convergence on the same issue: put it on the author's review sheet instead of a third round.

## Optional roles

- **Industry expert**: only when real domain material is available; otherwise a general model would pose as an expert. Checks outsider mistakes, outdated facts and where peers would see through the piece.
- (The target reader and the layperson reader are standard steps 6 and 6a above. They are different readers: the layperson hunts stuck words and broken numbers; the target reader judges whether the piece speaks to the account's actual audience.)
- **Experience check**: when the draft contains the author's own experiences. Material the author's notes support passes. Contradictions with the material, or someone else's story told as the author's, are must-fix. Unverifiable items become "please confirm" questions, not deletions.

## Calibration (maintainer task)

Run only by the Skill's maintainer, in a calibration task opened for this purpose (about monthly); never as part of writing a single article, which ends with the after-publishing record.

- Take 20 to 30 past review verdicts and compare the author's call with the AI judges'. Compute agreement separately for "should pass" and "should fail".
- Planted-error test: insert 5 to 10 known errors (a wrong number, a misattributed quote, a fabricated case, a banned pattern) into an approved article and count how many each reviewer catches.
- Reviewers with low catch rates get their prompt rewritten or their model replaced.

## Feedback candidates (every article)

At the close of every article, before or alongside approval 4, write this article's feedback candidates: every place the author rejected something and every place we withdrew our own work. Each entry: the problem sentence verbatim, what happened, why, how to fix it, and where in this Skill the fix belongs.

Two lines appear in every article's candidates, even when nothing was rejected:

- **The seed's outcome**: did the seed stand, change in part, or get overturned; how was it handled; did the author agree. This is how the seed standard grows.
- **The title**: which of the three candidates the author picked, and why if the author said. This is how the title standard grows.

Write the candidates for every article. When they are merged into the Skill, compare them side by side, merge the recurring ones, and at the same time delete old rules that no longer earn their place. Every hands-on article is a chance to refine the rules (claude-writing-skills ends each piece with the same kind of review; page read).

Sessions that test or use this Skill write feedback candidates; they do not edit the Skill files. Changes are made by the Skill's maintainer, in one place, so that several sessions do not overwrite each other.

## After publishing

- Ledger: one row each at day 1, 3, 7 and 30: the core judgment, the analytical cuts used, reading and interaction numbers, main faults, and what to feed back.
- Use the numbers to tune titles and openings, not prose style.
- Keep the AI draft and the author's final side by side; monthly, group the edits by type (style layer 4).
