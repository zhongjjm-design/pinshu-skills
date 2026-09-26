# Readability-First Acceptance for Long Course Markdown

## Trigger Conditions

Use this reference when the user says the material is “too dense,” “a wall of text,” or “hard to get through,” or when one lesson combines a long argument, dozens of consultation cases, and dissemination assets.

## Core Judgment

**Completeness and ease of reading are not mutually exclusive.** The faithful transcript preserves complete meaning; the structured lecture is the primary reading entry point. Do not force all content into one reading layer, and do not treat extra blank lines as the sole solution to density.

## 1. Route Content According to Document Responsibility

### Faithfully Edited Transcript: Consult the Original Voice

- Preserve first person, source sequence, complete cases, numbers, and judgments;
- Put no more than three key points at the beginning and state clearly that “this document is for consulting the original voice”;
- Under the current knowledge base’s Obsidian Nord theme, use one H1 and H3 section headings throughout the faithful transcript. Do not use H2 for body subheadings: H2 renders as large yellow text and competes with yellow bold emphasis, while H3 renders green and matches the accepted gold-standard examples;
- Navigate with natural section and case headings, but do not force continuous reasoning into lists;
- For long content, link to the structured lecture as the preferred reading entry point.

### Structured Lecture: Primary Reading Surface

- Present models, judgments, and actions before replaying Q&A in livestream order;
- Use a small number of H2 headings for major modules and H3 headings for “problem background, reasoning, applicable conditions, and case cards” inside each module. This creates three visual levels: yellow major modules, green subheadings, and yellow bold emphasis;
- Put large numbers of cases into separate “case cards” rather than embedding them in the methodology spine;
- Physically separate core explanation from the case library so the reader can read either layer independently;
- Keep dissemination assets and verification boundaries toward the end so they do not displace the reading entry point.

## 2. Hard Layout Rules

- Leave at least one blank line after H1/H2/H3/H4 headings;
- Leave blank lines before and after root-level lists; use loose list spacing when readability requires it;
- Each body paragraph should express one idea and should generally remain within 120 Chinese characters in Chinese source projects, or an equivalent compact semantic unit in translation;
- If a continuous list exceeds seven items, group it or add subheadings. Do not disguise a 30-item list as “structure”;
- A horizontal rule may create breathing room before each H2, but it must not replace content hierarchy;
- Use an Obsidian callout or separate blockquote for core judgments, with only a few highlighted conclusions per screen;
- Maintain clear visual boundaries between headings, body text, lists, quotations, and images;
- Organize body paragraphs as complete semantic units, usually two to four connected sentences. Never split mechanically after every period;
- No body paragraph or list item may begin with punctuation such as a comma, period, semicolon, colon, enumeration comma, or closing quotation mark. Punctuation belongs with the preceding sentence and must not be pushed onto a new line;
- Allow a short paragraph only when it carries a complete judgment. Merge isolated body text of 12 Chinese characters or fewer—or an equivalently fragmentary English clause—and fragments ending in a comma or colon back into context, or delete pure noise;
- Five consecutive body paragraphs under 45 Chinese characters, or equivalently short translated fragments, constitute a mechanically fragmented cluster by default and must be recombined semantically;
- Do not use repeated half-width spaces to manufacture letter spacing in Chinese source text. Let the reading theme control character spacing, line spacing, and alignment;
- Do not create fake breathing room by placing every spoken sentence in a separate paragraph. Blank lines serve semantic segmentation, not sentence splitting.

### Build a Mandatory Scan Layer

“Avoid excessive bolding” does not mean “use no bold.” In long course documents, a reader scanning only headings, bold text, and quotations must be able to restate the lesson’s main line.

- Put no more than three key judgments at the beginning, and bold the judgment sentences themselves;
- In the body, bold only key definitions, core judgments, decisive actions, and important transitions;
- A long draft over 7,000 bytes will usually retain five to ten bold spans. Fewer than five is acceptable only when the source genuinely lacks enough judgments; do not reduce bolding mechanically to zero in the name of restraint;
- Use no more than ten bold spans per file; do not create a second competing bold layer in the dissemination section;
- One to three instructor quotations may carry the lesson’s overall judgments. Never present editorial extraction as a direct quotation;
- During final acceptance, scan the headings, bold text, and quotations. If they do not reveal the lesson’s core, the document fails form acceptance even if paragraph lengths and scripts pass.

## 3. Boundaries of Mechanical Reflow

Automated line wrapping and blank-line insertion may repair local formatting, but cannot replace editorial judgment.

Failure signals:

- Source line count rises, but the primary reading document remains excessively long;
- A long paragraph is merely split into many small paragraphs while the main line and cases remain mixed;
- Every sentence is bolded or placed in a card, creating more visual noise;
- List items touch the next body paragraph and absorb it into the same list when rendered;
- Only H1–H3 are checked, while H4 and list spacing are ignored;
- A comma, colon, or closing quotation mark is pushed to the start of a new paragraph;
- Every sentence becomes a separate paragraph, leaving a screen of same-level body text and oversized empty space;
- Character count, line count, and scripts all pass, but reading view still resembles unedited STT fragments.

Correct sequence:

1. Decide what belongs to the main line and what moves into case cards;
2. Then split long paragraphs and lists;
3. Finally use blank lines, horizontal rules, and callouts for visual organization.

### Never Generate Formal Drafts by Automatically Splitting at Punctuation

An automated script may identify overly long paragraphs, but it must not insert blank lines directly into a formal file after periods, question marks, or semicolons. Before splitting, an editor must decide whether the sentences jointly complete one idea and whether transitions, causal links, and examples belong in the same semantic unit.

Automated formatting output may enter only a temporary file. Before promotion, inspect paragraph-leading punctuation, clusters of short paragraphs, fragments, abnormal spaces in Chinese source text, and the actual reading view.

## 4. Case Cards for Case-Heavy Lessons

Every substantive case must preserve at least:

- Person’s background;
- Original problem;
- Instructor judgment;
- Recommended action;
- Applicable boundary.

Group cases by problem class, such as “product/capability, traffic/content, delivery/organization, or market/transition.” Separate cards visually; do not place dozens of cases into one very long table.

## 5. Final Readability Acceptance Before Delivery

In addition to routine UTF-8, unique-H1, terminology, and number checks, verify:

- [ ] No more than three key points appear at the beginning;
- [ ] The primary reading entry point is explicit; the user is not required to begin with the complete transcript;
- [ ] Long body paragraphs over 180 characters are zero, with ordinary paragraphs kept compact where possible;
- [ ] H1–H4 heading-spacing violations are zero;
- [ ] Root-level list adjacency violations are zero;
- [ ] Paragraph-leading punctuation is zero, and fragments ending in commas or colons are zero;
- [ ] Isolated fragmentary body text is zero, and clusters of five mechanically short paragraphs are zero;
- [ ] Repeated half-width spaces used to manufacture Chinese character spacing are zero;
- [ ] Headings, bold text, and quotations form a self-contained scan layer;
- [ ] Bolding in long drafts was not mechanically reduced to zero and does not exceed ten spans per file;
- [ ] Consultation cases are separated from the methodology spine;
- [ ] No ungrouped list exceeds seven items;
- [ ] The primary reading document was opened in the preview area and inspected in reading view;
- [ ] Reading-view inspection covered at least the opening, the longest middle section, and the closing dissemination section, with no hanging punctuation, screens of undifferentiated body text, or abnormal empty space;
- [ ] The completion report contains only results, paths, and key acceptance findings, not a long process replay.

## 6. Rework Order After a User Complaint

When the user explicitly says the material is hard to read, stop adding content or explaining causes:

1. Make the structured lecture the primary reading document;
2. Reduce opening metadata to no more than three points;
3. Separate the main line from case cards;
4. Repair spacing around H1–H4 and lists;
5. Preview the primary reading document;
6. Report the revision in one sentence without another long explanation.
