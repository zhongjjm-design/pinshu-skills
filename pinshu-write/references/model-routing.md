# Model routing

Recorded in October 2026 from the team's own use. Model menus differ by tool, version and account, and change often: check what your tool actually offers. If your menu shows other versions, use the newest model of the families named here (Claude, Gemini, Qwen, DeepSeek; Kimi for reviewing); older or smaller versions work with lower quality. When a newer version appears, prefer it and re-run the planted-error test from the review chain.

## Who does what

| Role | Good choices | Notes |
|---|---|---|
| Organizer (main conversation) | Whatever runs your session | Runs the workflow, merges research, keeps the fact table, writes the seed confirmation and judgment card, writes every pen brief, checks every pen output. Does **not** write reader-facing Chinese (outline wording, titles, subheads, body, revisions) unless the author names it as the writer. In tests, the main conversation (Claude Opus 5.5) understood the author but its Chinese prose was rejected repeatedly. |
| Writer: outline wording, title, subheads, body, revisions | **The model the author names**, if any. Otherwise **Claude Opus 4.6** (team's choice); then Sonnet 4.6, Gemini 3.8 Flash, Qwen 3.8, DeepSeek V4.1 Flash or another DeepSeek model | Pick the strongest Chinese prose model you have. Keep one writer per article. |
| Wording editor | **Gemini 3.8 Flash** (team's choice), from a vendor other than the writer's | Checks the writer's text item by item against the written standards. Keeps what passes (the default); proposes a fix only where a named standard fails, citing it. Never rewrites the whole text, never touches structure, facts, locked items or what the author approved. The organizer applies accepted fixes. In tests, the author trusted Gemini 3.8 Flash's judgment of Chinese wording most. |
| Revisions after author comments | By size ("Revisions after the author comments" below): the organizer for word swaps the author spelled out; otherwise the writer, then the wording editor on the changed parts only | The organizer sends the author's verbatim comments automatically; the author never forwards between models. |
| Structure judges | Two models from vendors other than the writer's | Yes/no questions; "cannot judge" allowed. |
| Red team and common-sense floor | Two or three models from different vendors | Different vendors give different blind spots, which is the point. DeepSeek and GLM both produced sharp red teams in testing. |
| Layperson reader | Any model from another vendor, or a real colleague outside the industry | Kimi, DeepSeek and GLM all worked; Kimi's quota window ran out after a few calls. |
| Fact check | A model with web access | High-risk items are spot-checked by the author. |
| Mechanical tasks | Any model, including GLM | File handling, running `audit_draft.py`, formatting, collecting links. |

**By default, do not draft with GLM** (for example GLM 5.3 Flash). In the team's experience its Chinese prose is noticeably weaker. Every other role is fine: common-sense floor, red team, structure review, layperson reading and mechanical tasks all worked well with GLM in testing. If the author names GLM as writer, that is the author's call; follow "The author names the writer" below and watch its known habits.

Writers are strong Chinese prose models from the Claude, Gemini, Qwen or DeepSeek families (in October 2026: Claude Opus 4.6 or Sonnet 4.6, Gemini 3.8 Flash, Qwen 3.8, DeepSeek V4.1 Flash). If your tool lists other versions, use the newest one from these families. Reviewers must come from a different vendor than the writer; a domestic-only setup can pair Qwen, DeepSeek, Kimi and GLM with each other.

## The author names the writer

If the author names a writer (any model, including the main conversation itself or a model this file does not recommend), that model writes. It is a legitimate choice, not a workaround to explain away. Record it in the editor notes ("writer: <model>, named by the author").

- When the named writer is not the team's first choice, no review step is skipped or shortened: the wording editor, the structure review and the layperson read all run.
- When the named writer is the organizer itself (the main conversation writes), the judgment gate's seven questions go to a model from another vendor; the organizer does not answer its own questions alone. The wording editor must also come from another vendor. If no other vendor can be called, follow "When only one model is available" below.
- Every writer, whoever it is, follows the experience rule: the author's experiences come only from the author's words (below, "Known habits").

## Writer, then the wording editor

Model reviewers in the review chain check whether a text is wrong, and only flag. Whether its wording works (titles direct, subheads clear, sentences natural) needs a second check by a strong Chinese reader against the written standards: the wording editor. It is an editor, not a rewriter: what meets the standard stays exactly as written; only an item that fails a named standard gets one proposed replacement line; it never edits the draft itself.

**Roles.**

- **Organizer**: the main conversation. Runs the workflow, merges research, keeps the fact table, writes the seed confirmation and the judgment card, prepares every brief, applies accepted review changes, and checks before anything reaches the author. In the team's tests the main conversation (Claude Opus 5.5) understood the author but its Chinese prose was rejected repeatedly, so when a writer model is available and the author has not named the organizer as writer, the organizer does not write reader-facing Chinese itself.
- **Writer**: the author's named choice, otherwise the strongest Chinese prose model available. Writes the outline wording, title candidates, subheads, opening, ending, body and revisions. Team's choice (October 2026): Claude Opus 4.6.
- **Wording editor**: a strong Chinese model from another vendor checks the writer's text against the standards and proposes lines only where a standard fails. Team's choice: Gemini 3.8 Flash, whose judgment of Chinese wording the author trusts most.

**What gets reviewed.** Everything from the outline onward that readers will read: title candidates, every subhead, the outline wording, opening and ending, the body, and every revision (only the revised parts). The seed confirmation and the judgment card set direction rather than wording; they are not part of this review.

**The sequence, every time.**

1. The organizer writes the brief for the writer: the author's original seed text, the numbered point map with the section each point goes in, the judgment card, the author's decisions and verbatim comments, the locked items (word for word), the fact table, the Chinese rules (`audit_draft.py --rules` output), the evidence budget, and the target length per section. Materials are pasted in, never given as file paths.
2. **The writer writes** (prompt kit 7 for the body, 11 for the outline, title and subheads).
3. **Cold readers, where titles are involved** (prompt kit 3): their verbatim "did not understand" words go into the wording editor's brief.
4. **The wording editor checks item by item** (prompt kit 12). For each title candidate, each subhead, the opening, the ending, and each paragraph of a body draft, it gives one verdict:
   - **Keep**: meets the standards. This is the default; most items should be kept. An item containing a word any cold reader could not understand cannot be kept: change it, or send it to the author.
   - **Change**: fails a named standard. It quotes the item, names the standard it fails (for example "subhead hard test: an outsider cannot say what this section teaches"), and gives the replacement: the complete new line, written out in full, changed only as much as the standard requires. Advice without the new line ("make it more direct", "consider rephrasing") is not a valid change. The replacement must itself meet every standard it is judged by, including length.
   A change without a named standard is not allowed; "I would phrase it differently" is not a reason. The wording editor never rewrites the whole text, never touches structure, facts or locked items, and never changes what the author has already approved (it may only flag a hard-rule breach there).
5. **The organizer applies** the proposed fixes it accepts, word for word, and checks: locked items unchanged; no name, number, quote, date, or concrete detail of the author's own experience that is not in the fact table or the author's words (anything missing is marked "[to confirm]" and asked); hard rules pass (run the audit); the author's direction intact; **seed-point coverage**: compare the writer's coverage list against the point map, and treat any point missing, merged or dropped without a recorded author decision as a must-fix before anyone else reads the draft. If a proposed fix is rejected, say why.
6. **The author sees** the result through the approval message (approvals reference, "How to write an approval message"): in chat, only the items that were changed and why, in plain words; kept items are not listed. The full item-by-item review table stays in the article folder and is shown when the author asks.
7. **After the author comments**, follow "Revisions after the author comments" below. The author never forwards anything between models by hand.

Save every brief, writer output and review in the article folder (for example `pens/03-outline-<writer>-v1.md`, `pens/03-outline-review-<reviewer>-v1.md`), so anyone can see who wrote what and why each change was made.

## Revisions after the author comments

**First sort the comments into three kinds**: wording (words, punctuation, sentences, paragraphs), checking (re-measure a number, confirm a name or date, look something up) and images or downloads (screenshots, videos). Wording goes first and alone: revise, check, and hand the draft back. Checking and images run as separate jobs that never hold the draft back; report them when they finish. In testing, ten wording comments took about three minutes to fix, but the author waited 49 minutes because checking (12 minutes) and failed screenshots (29 minutes) ran in one line before delivery.

**Then size each wording change:**

| Size | What it looks like | What happens |
|---|---|---|
| 1 Swap | The author gave the exact words ("change X to Y", add a comma) | The organizer replaces them word for word, runs the audit, and shows a before-and-after list. No writer, no review, no rerun of the editor-in-chief review. Using the author's own words is not the organizer writing. |
| 2 Sentence | The author points at a problem in a few sentences but gives no wording ("unclear who 'this' is", "I don't get this word") | The writer rewrites only those sentences (prompt kit 13, sentence version); the wording editor checks only those sentences; run the audit. No review chain, no editor-in-chief rerun. |
| 3 Paragraph | A paragraph rewritten, an example swapped, one section reworked | The writer revises only that part; the wording editor checks only that part; run the audit. Rerun the matching check only if a fact or claim changed. |
| 4 Direction | The judgment, structure or title direction changes | Go back to the matching gate and run the full workflow from there. |

When unsure which size applies, take the smaller one, say so in one line, and let the author ask for more.

Whatever the size, the organizer applies the accepted changes to the current full text and hands the author the complete article (with a short before-and-after list), never only a table of changed sentences.

**After approval 4.** Sizes 1 to 3 keep the editor-in-chief review already done; the author reading the complete revised article and saying it can go is the approval for that version. Then follow the delivery reference, "Post-approval wording edits" (re-export, kit, hashes). Size 4 reopens the matching approval.

**Facts touched by a change** are re-checked one by one at their original source, not the whole article; anything newly confirmed goes into the fact table at once (see the topic reference, "Fact table").

**Checking has a budget.** A check whose answer cannot change the body (for example, whether someone also reposted an article elsewhere) gets about two minutes; if nothing turns up, write "not found; looked in: ...".

**Read background results as soon as they arrive.** A review running in the background is read and merged the moment it finishes; it is never left waiting behind another job. In testing, a wording review finished in two minutes and sat unread for twenty.

**Browser work** (screenshots, opening pages) follows the time limits in the delivery reference, "Evidence screenshots".

## What stays separate, and fallbacks

This is separate from the review chain. Review-chain reviewers only flag. The wording editor only proposes; the organizer decides what to apply, and the author's own sentences and approved items are never changed by it.

**Fallbacks.** If your tool cannot call a second model, follow "When only one model is available" below; never ask the author to carry briefs or replies between models. If no second model is available at all, say so in the editor notes ("wording not reviewed by a second model") and tell the author before approval 3 or 4. If no writer model is available, the organizer writes and the wording editor's check matters even more.

## Calling the writer and the wording editor

- **If your tool can run commands**: call the model's own command line with the full brief pasted in the prompt, from an empty working folder and without your personal settings, so that plugins and hooks you use do not reach the pen (for Claude Code, `--setting-sources project`). In testing, a pen called with the user's settings returned only a memory-plugin footer instead of the revision. Examples used by the team: Antigravity's command line `agy -p "<brief>" --model gemini-3.8-flash-high` (Gemini 3.8 Flash) or `--model claude-opus-4-6-thinking` (Opus 4.6); Claude Code `claude -p "<brief>" --model claude-opus-4-6`. Run in a fresh call, tell the pen not to read or write files, and save its output into the article folder yourself.
- **If your tool can dispatch helper agents on another model**: give the helper the full brief and the same instructions.
- **Probe before the real call.** Before sending a long brief, send each pen a one-line request with a short time limit (about a minute). An empty reply, a quota or login error, or a command that exits 0 with no text is not a result: move to the next entry in the fallback order at once instead of waiting out a long timeout. A model listed in a menu, or a command found on the path, is not proof that it can be called. In testing, three entry points failed one after another (an empty timeout, a quota error, an empty exit 0) and most of a ten-minute revision went to waiting on them.
- **If neither**: treat it as one model available (below).
- **If no second model exists**: write "wording not reviewed by a second model" in the editor notes and tell the author before the approval point.
- Models forget instructions in long outputs: keep each call to one step (outline, or one draft, or one revision), and paste the locks and the Chinese rules every time.

## Pairing writer and reviewers

| Writer vendor | Reviewer vendors |
|---|---|
| Anthropic (Opus or Sonnet) | Google (Gemini), Alibaba (Qwen), DeepSeek, Moonshot (Kimi) |
| Google (Gemini) | Anthropic, Alibaba, DeepSeek, Moonshot |
| Alibaba (Qwen) | DeepSeek, Moonshot, Google, Anthropic |
| DeepSeek | Alibaba, Moonshot, Google, Anthropic |

## Per-tool notes

| Tool | What the team reported | Suggested setup |
|---|---|---|
| Antigravity | Offers Gemini 3.8 Flash, Claude Opus 4.6 and Claude Sonnet 4.6 | Write with Opus 4.6 or Sonnet 4.6; review with Gemini 3.8 Flash (different vendor, same tool). |
| ZCode | Default model is GLM | Use it for files, scripts and checks. Switch to a writer-grade model for drafting if the menu allows; otherwise draft in another tool. |
| Qoder, WorkBuddy | Mostly domestic models | Choose Qwen or DeepSeek as writer if listed; use the other one, or Kimi, as reviewer. |
| Command-line agents (Claude Code, Codex, Gemini CLI, Kimi CLI and similar) | Depends on the account | Same pairing rules; run reviews in fresh sessions, or in helper agents running another vendor's model where your tool supports them. When calling a writer from the command line, paste the profile, judgment, outline, material and rules into the prompt; a writer given only file paths went to the wrong place and returned one sentence. |
| Kimi command line | Prints its reasoning along with the answer | End the prompt with "output only the final result table". |

## When the writer is out of quota

Check the quota before handing out the draft. If the writer cannot run, substitute in this order:

1. the same model through another entry point (another tool or the vendor's own command line);
2. a writer-grade model from another vendor in the table above;
3. only then the main conversation writes the draft itself.

Record the substitution in the editor notes, and re-pair reviewers so they still come from a different vendor than whoever actually wrote. In testing, both articles of one day hit the writer's quota and ended up drafted by the main conversation without a planned order.

## When only one model is available

This applies to every step that asks for another vendor: common-sense floor, red team, the judgment gate's seven questions, wording editor, structure judges and layperson read. The author is never the courier: do not ask the author to paste prompts or drafts into another model's chat and bring replies back.

- If the organizer can reach another vendor by command line or a helper agent, it calls that model itself and saves the reply in the article folder (`review-<role>-<model>.md`).
- Otherwise run each review role in a fresh session with only the material and that role's prompt. Do not show the writer's reasoning.
- Write "same-vendor review" in the editor notes, and say it in the next approval message in one line (for the seven questions: "the seven questions were answered by the same model that wrote the judgment, so they may share its blind spots"). The author decides whether to go on.
- A same-vendor review is a recorded downgrade, never a pass. In testing, same-vendor wording checks let mirrored couplets and coined jargon through, and the same model that changed the author's direction also passed its own seven questions. The author's own reading and `audit_draft.py` carry more weight here.
- A real colleague outside the industry may still do the layperson read (a person reading the draft, not a courier between models).
- If even a fresh session is impossible, mark the step "skipped" in the editor notes and let the author decide whether to proceed.

## How to use model-test evidence

Every routing note carries one of three evidence levels: **observed once** (one article, one session), **repeated** (seen across several articles or sessions), or **not tested here**. A single article can nominate a candidate or reveal a failure mode; it cannot establish a ranking. Attribute a result to the actual model that wrote, not to the desktop app or command line that hosted it; if the model was not recorded, write "model not verified", and the note then counts as a process finding, not as evidence about any model.

The notes below come from one test in October 2026: four sessions wrote the same seed (an opinion piece on how to judge real effort in the AI era), each under different routing, and the author compared the results. None of them is a model-selection conclusion.

| Observation | Level | Session and actual model | What it supports |
|---|---|---|---|
| The writer opened with an event the seed never contained ("I had two assistants research the same topic") and wrote it as the author's own experience | Observed once | A DeepSeek session; exact model version not verified | A process rule, not a ranking: every first-person detail is checked against the fact table (it agrees with the repeated habit under "Known habits") |
| The same DeepSeek session's final title was judged by the author as understood at a glance and distinctive | Observed once | Same | At most: a DeepSeek-family model may be tried as a title writer. Not a ranking |
| The writer squeezed a ten-item observation list from the seed into one main proof and pushed another seed point into background because a collision showed it "already covered" | Observed once | A Qoder session; the main conversation wrote at the author's request; which model Qoder ran was not verified | Process only: give every writer the point map and require a coverage list (prompts 7 and 11); say nothing about the model |
| With the organizer also writing, a readable article faithfully carried out an earlier narrowing of the seed that the author had approved without seeing its effect | Observed once | Same Qoder session | Process only: the editor-in-chief checks the original seed against the point map before judging prose |
| Writers invent the author's experience when material is thin | Repeated | Several sessions and models (see "Known habits") | Applies to every writer |

## Known habits to watch

Observed in tests; re-check after version changes.

- **Every writer invents the author's experience when material is thin.** In tests, the main conversation writing as the named writer added "I was on a business trip for two weeks", and Gemini 3.8 Flash added failures and routines the author never mentioned. Rule for every writer: the author's experiences, conversations and feelings come only from the author's own words and the decision log, copied into the fact table as whole sentences. Anything missing is written "[to confirm]" and asked; the organizer checks every first-person detail against the table before the author sees it.
- **GLM as writer** (when the author names it): many prompt colons (announcing a point with a label and a colon), corner quotes 「」 instead of curly quotes, and frequent "not X, it is Y" reversals. Put these three in the brief as explicit "do not", and run the audit script on every output.
- Claude Opus 4.6 as writer: overuses the single-sentence reversal; uses straight quotes in Chinese text (in testing, two revisions in a row; the organizer converts them with `scripts/fix_quotes.py`, which changes punctuation only, and notes it); occasionally invents approximate figures ("the past two years", "thirty to forty percent") not present in the research pack; its own counts of characters and patterns are unreliable; once it turned a quoted inner thought into something that read like a study's words. Run the audit script and the fact check every time.
- **Gemini 3.8 Flash fills thin material with invented detail when asked to write.** In a test with sparse material ("we used a spreadsheet and AI for two months"), its outline added specific failures, column counts, template counts, a named mistake and an exact morning routine that the author never mentioned; Kimi K3, given the same input, marked those spots "waiting for your original". This is one more reason it reviews rather than writes; whenever any model writes with thin material: give it the fact table and the author's material in full, tell it to write "[to confirm]" where material is missing, and have the organizer check every concrete detail against the material before the author sees it.
- **Writes short.** Asked for 3,000 to 3,600 characters it delivered about 2,500; in later tests it came in short four times (asked for 2,800 or more, delivered about 1,800). Give every section a target length in the brief. When rewriting from an earlier draft, paste the full earlier draft and state "not shorter than the previous draft". When a draft is short, ask it to expand one named section with illustrative examples, never with new facts.
- **Invents scenes.** First drafts opened on scenes nobody reported (labels on videos, a boss reacting the same day), added years of experience the author never claimed, and put quotation marks around paraphrases. Before drafting, lock names, numbers, quotes (with their Chinese wording) and dates into a fact table; the writer may use only the table, and the brief forbids scenes and crowds not in the material. The first job on any draft is to split out every fact and check it against the material. The same idea comes from persona-write (page read): lock facts and terms before writing.
- **Changes what it was told to keep.** In a revision, the writer rewrote approved subheads; in another, revising one paragraph, it turned an adopted phrase from the previous round ("my team and I") back into "we". List every locked item word for word in the revision brief, including wording adopted in earlier rounds.
- **Writes the author in the third person.** It wrote the author's own experience as "<author name> said" in an article the author signs. The brief says first person for the author's experiences.
- **Misjudges the author's own work.** One draft turned a two-shot test into "done well in one go"; the over-correction then had the author run their own work down in public. Describe the author's own work by what was done and tested, without praise or self-deprecation; a test is not written up as a success, and "we still have much to learn" is internal, not for readers.
- Any writer: drifts toward jargon from the research material. The layperson read is the cure.
- Any judge: rates drafts from its own vendor more kindly. Keep vendors separate.
- Any cold-reader judge: two models agreed on a title the author could not understand. Treat title tests as advice.

## Keep inputs small

Flash-class models and long conversations both lose instructions. Give each call only what that step needs: the draft plus the one relevant reference, not the whole research pack. Draft each article in a fresh session and paste the style layers again when writing long pieces in parts.
