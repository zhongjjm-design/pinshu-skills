# Approvals and messages to the author

Details behind the approval steps in the SKILL.md workflow: when to stop, what each approval message contains, and how to ask the author for anything.

## Four approval points

Stop only here. If the author says "use your recommendation" for a step, skip that stop; the judgment is always confirmed before drafting.

1. **Seed confirmation and point map** (with no seed: pick one of 3 to 5 topic cards, then confirm it as a seed).
2. **Judgment**, after the judgment gate. Practical pieces use a route table.
3. **Title and outline**, after the skeleton gate. The author's reading decides; model cold readers advise.
4. **Final draft**, after the review chain and the editor-in-chief review; review sheet and seed-to-final map in the article folder.

Questions between stops wait for the next one. Two rejections in a row: stop rewording and ask for the one sentence readers should remember.

**When the author is away.** If the author said "use your recommendation" and left, a title picked in their absence is marked "tentative" and stays so until the author has seen it; list it in the publishing kit under "for the author to confirm". This is the same rule as never choosing between candidates for the author. In testing, an author who stepped away came back to a title nobody but the agent had approved.

## How to write an approval message

Run every gate and review, then show the result in plain words, never the machinery. Same shape every time:

1. **One plain sentence: what I recommend**, in the author's terms.
2. **One natural question**: "Is this what you mean?"
3. **At most four small decisions, one line each, each with my recommendation**.
4. **Where the full record is**: a one-click link to a file that exists; if none was written, say so, paste it.

- **Approval 1**: the first sentence restates the seed in the author's words, no judgment; then the five-item restatement with numbered points, the author's material to confirm, at most three questions.
- **Approval 2**: the judgment in one sentence; the seed's outcome; only points changed or dropped; any changed scope word; the strongest objection; "collisions unverified" if the scan is missing or incomplete (the author decides). If evidence weakens the seed, say plainly what looks familiar or unsupported and give one sharpening.
- **Approval 3**: three titles written three ways, one recommended with a reason; the author picks. Then the subheads; from the wording check, only what changed and why.
- **Approval 4**: the draft that passed the editor-in-chief review; changes and why; open must-fix items; dropped points.

No bold in these messages; run `audit_draft.py --card --seed` on them. Judgment card, gate records, the keep-or-change table and review sheet stay in the folder, shown when asked. Never make the author compare abstract labels or near-identical judgments, or carry text between models.

## Asking the author for anything else

Any request for the author's go-ahead (overwrite a file, re-export, download, spend money) says in plain words: what will be done, why, and which file or thing it touches. Never a bare command word. In testing, an agent asked the author several times only to say "re-export"; the author could not tell what that meant or why it was needed.
