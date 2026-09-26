# Relationship-Direction Consistency, No-Image Lesson Records, and First-Person Final Checks

Use this reference for three easily missed quality problems in long course transcripts: reversed case-role direction, spoken references to screenshots that the user did not supply, and editorial voice leaking into a faithfully edited transcript.

## 1. Audit Case Roles and Relationship Direction

A transcript may state a shorthand conclusion first and explain the full story later. STT or a slip of the tongue may reverse the direction between the two, for example:

- Shorthand: copied A’s traffic and B’s product;
- Full story: actually used A’s product together with B’s content.

Do not preserve the shorthand in one place and the full-story relationship elsewhere, creating an internal contradiction.

### Internal Event Tuple

For cases involving A/B, Person A/Person B, merchant/creator, or content/product relationships, first record internally:

```text
Role A: What does this role provide?
Role B: What does this role provide?
Action: Whose content/product/traffic was used?
Outcome: Could not sell, was displaced, or produced profit?
Causality: Why?
```

### Decision Order

1. User’s explicit correction;
2. Clear image or slide;
3. Complete event process later in the transcript;
4. One-sentence shorthand earlier in the transcript;
5. Editorial inference.

If the full story resolves the ambiguity, normalize the relationship according to that story. Record in an editorial note: “The shorthand spoken earlier conflicts with the direction in the later full case; organized according to the complete event process.” If ambiguity remains, mark it for confirmation rather than selecting a version yourself.

### Final Check

Search all role names and relationship terms and confirm:

- A/B direction is consistent in headings, body text, and summaries;
- Content source, product source, and traffic source have not been swapped;
- The case conclusion agrees with the detailed process;
- The structured lecture does not reverse a relationship that is correct in the faithful transcript.

## 2. No-Image Lessons and Spoken References to Missing Visuals

If the user supplies no images in the current batch, treat that as the complete current asset set and do not ask whether more images exist. Distinguish two cases:

### Genuinely No-Image Lesson

Write in frontmatter and the course map:

```yaml
images: none
```

### The Narration Repeatedly Mentions Screenshots or Slides, but None Were Supplied

Write in frontmatter:

```yaml
images: none (the original lesson mentions screenshots or slides, but none were supplied in this batch)
```

Also register in the course map:

- Images: none;
- Types of visuals mentioned in the narration, such as a mind map, revenue table, viewing curve, or search screenshot;
- If images are later supplied, perform visual-text integration and four-way reconciliation.

Processing rules:

- Recover only content confirmed by the narration;
- Do not invent account names, data, table rows and columns, or curve values from absent screenshots;
- If the narration says “you can see it in this image” without reading a value aloud, record only “the visual from the original lesson was not supplied”;
- Do not misstate “no images in this batch” as “the course itself contains no images.”

## 3. Final First-Person Check for the Faithful Transcript

Even when a faithful draft is broadly written as “I,” local passages can slip into editorial voice. In addition to common phrases such as “the instructor believes,” “the course mentions,” and “the author points out,” search for equivalents of:

```text
the course gave an example
the course analyzed
the course proposed
the course chose
the course screenshot
this lesson believes
```

In body text, rewrite these as appropriate:

- “Let me give an example…”
- “I analyzed several creators…”
- “The experience-based metric I use is…”
- “Next, I choose…”
- “This screenshot of mine did not capture the whole view…”

Editorial notes, fact verification, and asset notes may retain neutral third-person voice, but they must remain visually separate from the instructor’s body.

## 4. Minimum Acceptance Checklist

- [ ] An A/B relationship event tuple was created
- [ ] Relationship direction agrees across headings, body, and summary
- [ ] No-image state is recorded in frontmatter and the course map
- [ ] No visual information was invented when the narration mentioned an image that was not supplied
- [ ] Editorial-viewpoint phrases were searched and removed from the faithful body
- [ ] Case relationships in the structured lecture match the faithful transcript
