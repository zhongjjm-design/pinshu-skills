---
name: pinshu-write
description: "Use when someone wants an opinionated Chinese long-form article for a business, brand-marketing or applied-AI account (WeChat Official Account style analysis pieces): grow a rough idea into a mature, useful judgment, then title, outline, draft and review it with a writer and reviewers from different model vendors. Triggers include 'write a Pinshu article', 'turn this event into an article', 'write an analysis piece for our account', 'help me find a topic', 'review this draft'. Not for faithful transcripts (pinshu-transcript), course study guides (pinshu-distill), breaking-news flashes, celebrity or social gossip, or any account whose profile says AI must not draft it."
---

# Pinshu Writing

## Provenance and maintenance

- Original status: Pinshu original (`original`). Owner and maintainer: Aidan (Pinshu).
- Original capability: seed-to-judgment workflow, two gates, four approvals, cross-vendor review; built from rejected articles (`references/worked-example.md`).
- Version: 1.3.0 trial version. Only the maintainer edits these files; every session that uses it writes feedback candidates instead.
- 1.3.0: revisions sized and wording delivered first; evidence screenshots taken while writing; 参考文章 replaces the source list; export adds the account folder and has `--check`; self-check script; this file shortened.

## What this Skill is for

It grows a rough idea into a judgment worth publishing, said plainly enough that a busy reader never gets stuck. The AI researches, argues the other side, drafts and checks; the author decides seed, judgment, title, outline and whether it ships; a person publishes under the platform's AI-disclosure rules. Output is Simplified Chinese unless the account profile says otherwise.

## What it needs

- **Core**: Python 3.9 or newer; no third-party packages. With this alone the workflow never gets stuck: every missing capability below has a named fallback, and a skipped or downgraded step is always written down as such, never reported as done.
- **Optional**: web access for research (without it: "no web access", leads from memory marked unverified); a model from a second vendor for writing or reviewing (without one: "same-vendor review"); the visual Skill `pinshu-visual-system` and a browser for evidence screenshots (without them: a "to capture" list).
- **Check once**: `python3 scripts/check_env.py --config <your config>` lists what is there, what is missing and how to add it. Keep the configuration in your own writing folder, not in the shared Skill folder.

## Three steps to start

1. **Check and read the setup.** Run the self-check the first time. Then read the configuration (`pinshu-write.yaml` in the author's writing folder, or the path the author gives; format in `templates/config.example.yaml`) and the account profile. The profile wins over this Skill on topics, reader, length, banned words and titles. Minimum to begin: the account and its reader; ask if either is unknown. If both are known but there is no configuration, go on and add the missing items (profile, material folders, drafts folder) to the approval 1 questions. Without a profile, mark topic cards "checked against the generic floor only" and note "no account profile read".
2. **Print the Chinese rules once**: `python3 scripts/audit_draft.py --rules`.
3. **Enter where the author is**, then follow the workflow below. The normal stops are the four approvals; also stop when the account or reader is unknown, when evidence overturns the seed's core, when an opinion piece has none of the author's own material, and after two rejections in a row.

| The author brings | Enter at | Back-check first |
|---|---|---|
| An idea or topic, any length | 1 Seed | |
| A judgment | 2 Research | Seed and point map from the author's words |
| An outline or title | Skeleton gate | Seed, point map, judgment gate |
| A draft to review | 6 Review chain | Seed and point map from the author's brief; fact check |
| Comments on a draft | Revision | Size each comment: a word swap the author spelled out, a few sentences, a paragraph, or a change of direction (only the last goes back through the full workflow; model-routing reference) |

"Only review it": run the review chain and editor-in-chief review, return findings, stop.

## Workflow

| Step | What happens | Details |
|---|---|---|
| 0 Spec | Account, reader, where they are stuck, what should change | this file |
| 1 Seed | Confirm the seed in the author's words, number its points | `references/topic-and-judgment.md` |
| Approval 1 | | `references/approvals.md` |
| 2 Research | Three lanes, fact table with links and quoted sentences, collision layers | `references/topic-and-judgment.md` |
| 3 Judgment | Baseline, widen, red team; seed outcome; judgment gate | same |
| Approval 2 | | |
| 4 Title and outline | Article type, three titles, subheads, outline; skeleton gate | `references/article-types.md`, `references/plain-writing.md` |
| Approval 3 | Fact table locked; screenshot list marked | |
| 5 Draft | Writer writes, wording editor checks, organizer applies. Evidence screenshots run beside it, never blocking | `references/model-routing.md`, `references/delivery-and-audit.md` |
| 6 Review chain | Layperson, target reader, structure, facts, risk, language; flag only | `references/review-chain.md` |
| Editor-in-chief review | Is every seed point in the point map? Is this the article the author asked for? Then the writing | same |
| Approval 4 | | |
| 7 Deliver | `export_article.py --ready-dir <ready_folder>`, then the kit and image task, then `--check` on the pair; cleanup | `references/delivery-and-audit.md` |
| 8 After publishing | Ledger, edit record | `references/review-chain.md` |

## Rules that do not bend

- **Only the author sets the seed, and its direction is the anchor.** Research and the red team sharpen and limit; they never change direction, type or reader on their own (topic reference).
- **The organizer (the main conversation running this workflow) does not write reader-facing Chinese** unless the author names it as writer, or no writer model can be reached (then it writes, and the editor notes say so). A writer writes; a wording editor from another vendor checks item by item; reviewers only flag (model-routing reference).
- **The Chinese hard rules** (plain-writing reference, first section) apply to every draft; the audit script is a floor, never proof of quality.
- **Revisions are sized.** Wording comments are fixed and handed back first; checking and images run separately and never hold the draft back (model-routing reference).
- **The ready folder is written only by `export_article.py`**; once the kit and image task exist, `--check` the pair; never copy a file there by hand (delivery reference).
- **Every article closes with feedback candidates**: each rejection or withdrawal, the seed's outcome and the title the author picked (review-chain reference).

## When something goes wrong

| Problem | What to do |
|---|---|
| No second model to call | Run the role in a fresh session, write "same-vendor review" in the editor notes and tell the author (model-routing reference) |
| The writer is out of quota | Substitute in the order given in the model-routing reference; record it |
| A screenshot fails | Check the browser window is in front; one-minute limit per try; after two failures with the same method, write a manual handoff and carry on (delivery reference, "Evidence screenshots") |
| `audit_draft.py` exits 1 or 2 | 1: blockers to fix. 2: seed flags, each goes to the author. Exit 0 can still carry warnings: read the counts |
| `export_article.py --check` reports problems | Re-export with the script; never patch the ready copy by hand |
| The author rejects twice in a row | Stop rewording; ask for the one sentence readers should remember |
| The author is away | Recommendations may go ahead, but a title picked in their absence stays "tentative" until they see it (approvals reference) |

## References

| File | Use it for |
|---|---|
| `references/approvals.md` | The four approvals, approval messages, asking the author |
| `references/topic-and-judgment.md` | Seed, topic cards, research, fact table, judgment gate and card |
| `references/article-types.md` | Ten article types |
| `references/plain-writing.md` | Chinese hard rules, words, where readers get stuck, evidence budget, skeleton gate, titles |
| `references/good-article-standard.md` | Acceptance questions |
| `references/review-chain.md` | Review steps, editor-in-chief review, merge rules, feedback |
| `references/model-routing.md` | Models, writer-then-review sequence, sized revisions, fallbacks, habits |
| `references/prompt-kit.md` | Prompts 1 to 15 |
| `references/delivery-and-audit.md` | Audit, delivery format, ready folder, evidence screenshots, visual handoff, kit |
| `references/worked-example.md` | Real articles from seed to final |
