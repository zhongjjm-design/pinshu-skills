# Course Article Editing

## Course Module: Faithfully Edited Article

Enable this module when the source is a course, tutorial, or instructor narration and the user requests a “faithfully edited draft,” “edited course,” “turn the lesson into an article,” or “preserve the instructor's expression while improving readability.” Continue to use the general rules for ordinary meetings, interviews, talks, and hands-on transcripts.

### Intended Output

A faithfully edited draft is not caption segmentation, a third-party course interpretation, or a content summary. It is:

> **An oral course edited into a first-person article that still sounds as if the instructor is speaking.**

The editor must remain invisible. Keep the instructor's “I” and “we” in the main text. Do not recast the prose as “the course mentions,” “the instructor believes,” “the author points out,” “an instructor had a friend,” “she did...,” or another observer's voice. Put risk notices, fact checks, and source notes in separate editor's notes; never blend them into the instructor's voice.

### Fidelity Target: All Meaningful Content, Not Every Spoken Construction

You must preserve:

- people, relationships, products, brands, tools, situations, times, prices, percentages, and other numbers;
- complete claims, reasoning, rhetorical questions, analogies, case sequences, reversals, concerns, adjustments, and results;
- causal relationships, qualifiers, strength of judgment, and category-specific expressions;
- process information such as what the speaker thought at the time, why they acted that way, and what they later discovered.

You may delete or merge:

- content-free fillers such as “um,” “uh,” “ha,” “right?”, “everyone look,” and “OK”;
- equipment and course-administration chatter;
- abandoned versions after verbal slips;
- mechanical repetition that adds no information;
- circuitous speech and synonymous sentences whose removal does not change meaning.

The rule is: **remove noise, not information; revise syntax, not meaning.**

### Structural Segments in Long Livestream Courses

Long courses, including livestreams and recorded series, often contain structural segments that are not teaching but are not all noise. Handle each type as follows:

- **Promo reel / looping intro**: Merge repeated identical content into one occurrence and note, “The promo reel repeats N times here; the content is identical.”
- **Opening ceremony / participant introductions**: Preserve useful details such as participants' professional backgrounds, medical histories, and learning motivations. Together, these form a meaningful cohort profile. Compress greetings, pleasantries, and repeated “Hello, I am...” introductions.
- **Break-time Q&A**: Preserve every question and answer that contains subject-matter knowledge, and label the Q&A segment. This content is especially easy to misclassify as idle chat. Delete procedural exchanges such as “Can you hear the instructor?” / “Yes.”
- **Breaks / advertisements**: Delete them and note, “A break of X minutes occurs here.”

The test remains: would deleting this cause the student to learn less? If yes, retain it. If no, remove it.

### Authority to Resolve Specialist Content

The general prompt says to mark uncertainty as `[To confirm]`. In large course-editing projects, however, marking every doubt can accumulate hundreds or thousands of items, most of which the model can resolve from standard references. Apply these rules:

- For verifiable specialist knowledge, including standard textbooks, canonical passages, standard anatomy or formula composition, and dynastic eras, resolve it directly when confidence is high; do not mark it for confirmation.
- Reserve confirmation requests for names, commercial product names, and severely fragmented or inaudible content that standard references cannot resolve.
- For a large lesson whose raw transcript exceeds 10,000 Chinese characters, keep confirmation items to no more than 10. More than 10 indicates insufficient use of the authority to resolve specialist content.
- Even directly resolved terms must be consistent throughout and recorded in the proofreading table as `raw transcript -> corrected form`.

### Semantic Anchors: Do Not Replace Specifics with Abstractions

Do not replace concrete terms, numbers, or situations with broader words that seem safer, more general, or more “professional.” For example:

| Source semantic anchor | Do not replace with |
|---|---|
| Luck-changing effect | Desired effect |
| RMB 69 diagnosis; RMB 999 coaching program | Low-priced and high-priced products |
| Unable to sleep at night; lying at home after resigning | Career uncertainty |
| 53 action guides; 64 case studies | Rich content |
| Selling several thousand yuan in one day; too many customer-service messages to answer | Delivery pressure increased after sales grew |
| Northeastern Chinese mixed stew | A somewhat disorganized product structure |

You may summarize after retaining the specific information, but the summary may not replace the source. Do not quietly weaken, intensify, sanitize, or rewrite the author's views in the name of safety, professionalism, stylistic consistency, or controversy avoidance.

### Risk and Fact Discipline

When a course discusses guaranteed income, health effects, luck changing, financial fortune, gray-area customer acquisition, or platform evasion:

1. Preserve the instructor's intended meaning in the main text.
2. Do not sharpen vague claims into more precise efficacy claims or evasion instructions.
3. Use a separate **Editor's Note / Fact Check** to explain evidence, compliance, and applicability boundaries.
4. Do not remove risk by rewriting the instructor's main text, and do not present spoken course claims as verified facts.

### Article Form and Reading Hierarchy

Article editing changes expression, not authorship or informational content:

- Add subheadings at the instructor's natural topic boundaries without changing the overall order. **A subheading must show the direction of the instructor's thought, not merely label the topic.** “Why approach X underperforms approach Y” is better than “Discussion of approach X”; “The upgrade path from A to B to C” is better than “Several approaches.” Read together, the section headings should form a map of the instructor's reasoning.
- Faithful drafts in the Zhekou Niu course library use one H1 plus H3 section headings, with no H2 headings. The current Obsidian Nord theme renders H2 in large yellow type and H3 in green, while body emphasis is also yellow. Standardizing on H3 prevents headings and emphasized text from competing throughout the page and preserves the established style of lessons 1, 7, and 8.
- Give each paragraph one complete idea. Avoid both subtitle-like one- or two-sentence fragments and oversized walls of text.
- Split paragraphs by meaning, not punctuation. Normally, two to four connected sentences should complete one idea. Never use automatic “insert a blank line after every period” segmentation as the final draft.
- A paragraph must not begin with a comma, period, semicolon, colon, enumeration comma, or closing quotation mark. Merge isolated fragments of 12 characters or fewer and paragraphs ending with a comma or colon back into their context.
- Do not simulate letter spacing in Chinese body text with multiple ASCII spaces. Five consecutive paragraphs under 45 characters count as subtitle-like fragmentation and must be merged by meaning.
- **Heading density**: Add a subheading after each complete knowledge point, case, or method. Prefer slightly more headings over a large section that covers three or four knowledge points. A reader should be able to locate any review topic by scanning the table of contents.
- **Use frequent visual anchors**: Every few lines, give the eye something to catch, such as an emphasized keyword, a subheading, or a blockquote. These anchors guide readers who scan quickly.
- Apply emphasis sparingly to central judgments, key definitions, important numbers, and decisive actions.
- Representative verbatim remarks may appear in blockquotes. Never disguise an editor's summary as a verbatim quote.
- Use lists when the instructor explicitly enumerates items. Do not force continuous reasoning into a list merely to make it appear structured.
- A case may receive a title, but its background, process, concerns, adjustments, and result must remain intact.

The finished draft must support three reading speeds: headings alone reveal the topics; emphasis and blockquotes reveal the skeleton; full reading preserves every argument and case.

**Structural fidelity (no reordering):** Keep paragraph order strictly aligned with the original narration. Do not reorder or merge topics. Preserve a rhythm in which the instructor briefly introduces a point, digresses, and later returns to explain it in detail. If topic B appears during topic A, keep B where it occurred rather than moving it to a “more logical” location. Reorganizing dispersed material into a systematic structure belongs to `pinshu-distill` (systematic study notes), not to a faithful draft.

Here, “do not merge” means do not reorganize across topics or compress meaningful content. It does not mean every spoken sentence must become a separate paragraph. Edit consecutive sentences within one semantic unit into natural paragraphs and avoid subtitle-style formatting.

### Mandatory Semantic Reconciliation

After editing, sample and compare the opening, an important case from the middle, and the ending line by line:

- Has every person, situation, number, price, and key term from the source found a place?
- Did the strength of judgment, causal relationship, or qualifying condition change?
- Did any abstract term replace a specific expression?
- Did several rounds of explanation that each add information collapse into one vague sentence?
- Did a third-person narration or new judgment not expressed by the author enter the text?
- If the draft became substantially shorter, was everything removed truly noise?

If any check fails, return to the original source and revise. Never reconstruct missing content backward from a summary or systematic study notes.

### Length Reconciliation for Long Courses

**Protection against editorial failure:** A “faithfully edited draft” is the source-of-truth corpus at the bottom of the knowledge library, not a summary. Every batch task must repeat this positioning in its prompt and explicitly exclude compression, reorganization, case cards, and method extraction from the faithful main text. Subagents may write temporary drafts only; the orchestrator promotes them after a model semantic decision. For ordinary clean lessons outside the adaptive sample, the draft task may include its own semantic self-check. For risk-triggered or adaptively sampled lessons, use independent QA in a different context. A script's `PASS` proves only its deterministic checks; generation, acceptance, and map updates cannot be completed solely from one self-reported result.

Length is only a completeness warning and never a substitute for semantic reconciliation. Compare the **raw main text** against the **faithful main text**, excluding frontmatter, lesson highlights, quotable lines, shareable takes, user connections, social-media copy, and other derivative content.

- A 60% retention ratio is only an automatic rejection threshold, not a passing target.
- Main-text retention triggers review only; it does not prove fidelity or replace paragraph-by-paragraph semantic reconciliation.
- Never infer a universal retention ratio from a draft that the user has not accepted, and never promote “useful for reference” to “gold-standard example.”
- A faithful draft passes only when every meaningful unit has an explicit destination. Locate every case, number, judgment, inference, reversal, qualifier, and repeated emphasis paragraph by paragraph.
- Any substantial shortening requires a paragraph-by-paragraph list of removed pure noise and a coverage audit. A percentage or validation script alone cannot promote the draft.
- Words added in derivative content must not inflate the measured length of the faithful draft.
- Raw STT with long lines, repeated punctuation, and many fillers may shrink substantially, but every meaningful unit must still have an explicit destination.

### Confirmation Loop and Final-Draft Cleanup

After the first editing pass, do not deliver a body scattered with unresolved `[To confirm]` markers. Complete this loop:

1. **Correct against source materials**: If supporting teaching documents, slides, screenshots, or course pages exist, use them first to correct names, English spellings, product names, model names, version numbers, prompts, and hands-on details. Append links to the original materials at the end.
2. **Deliver one consolidated confirmation list**: Tell the user explicitly, “The full text has been edited. The following items still require your confirmation.” Group the list by people, English/product names, specialist terminology, numbers/facts, and visual content. Do not make the user search through the main text.
3. **Verify item by item**: Record the user's correct form, write it back into the main text **immediately**, standardize it throughout, and then search the entire file to confirm the old form is gone. Never record a correction only in the proofreading table without updating the main text. For unresolved items, let the user decide whether to retain a broader expression, delete the detail, or continue tracing the source; do not guess.
4. **Clear draft artifacts**: After user confirmation, search for and resolve draft markers such as `[To confirm]`, `[To verify]`, `raw transcript`, `as transcribed`, `unable to confirm`, `cannot determine from`, `exact name pending`, and `not independently verified`. Keep confirmed content as clean final prose; do not leave parenthetical editorial notes behind.
5. **Separate substantive risk notices**: Privacy, security, health, compliance, psychological diagnosis, and similar substantive boundaries may remain. They are not confirmation placeholders. When a fact remains unverified, verify it, reduce the strength of the claim, or attribute it explicitly; do not replace editorial judgment with a trail of draft parentheses.
6. **Final delivery statement**: Only after reviewing the full text and removing every draft-style confirmation artifact may you report, “Transcript editing and correction complete; items awaiting user confirmation: 0.”
