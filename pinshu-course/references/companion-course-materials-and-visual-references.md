# Revising Companion Teaching Documents, Linking Sources, and Using Visual References

Use this workflow when course audio, a live transcript, or a screen recording has companion teaching documents, lectures, slides, illustrated pages, Prompt pages, or resource links. The goal is a course draft that is faithful, verifiable, traceable, and reusable.

## 1. Source Responsibilities

- **Spoken/video body:** preserve the instructor's order, first-person voice, cases, judgments, concerns, and live process.
- **Companion teaching document:** correct terms, versions, model and product names, links, code, Prompts, parameters, and on-screen text that STT cannot recover reliably.
- **Editorial additions:** explain risk boundaries, source conflicts, update dates, and applicability conditions. Use separate labels such as “Editorial note,” “Teaching-document supplement,” or “Fact check”; never present them as the instructor's own words.

## 2. Revision Workflow

1. Complete a faithful cleanup of the spoken transcript and establish a list of pending confirmations.
2. Open the companion document and actually read its title, table of contents, body, code blocks, tables, images, and attachments. The table of contents or a text summary alone is insufficient.
3. Build an internal comparison table: `spoken STT → accurate document wording → evidence location → treatment in final draft`.
4. Correct person names, tool names, version numbers, system requirements, platform differences, download links, and operation order first.
5. Add valuable Prompts, code, resource links, and operating instructions that the teaching document contains but the speaker did not read in full to the relevant body section or hands-on review.
6. For a long Prompt, retain a “complete core version” by default and clearly label it as a compressed edit; the source teaching document remains authoritative for the verbatim full text. Include the full version only when the user requests it.
7. Add “Further Reading and Related Links” at the end. Link at least the source teaching document and, when useful, the resource repository, download page, and authoritative upstream source.

## 3. Resolving Source Conflicts

Companion material may itself conflict internally, be outdated, or preserve both an old approach and a newer Goal. Do not apply a mechanical “document wins” rule.

Priority:

1. explicit user correction;
2. within the same source, the newer, more fully constrained, lower-risk version;
3. legible original text in a visual or code block;
4. wording repeated consistently in the spoken material;
5. contextual inference.

When a material conflict exists:

- state it explicitly rather than choosing silently;
- use the lower-risk, more fully constrained version as the basis for editorial correction;
- do not present an obsolete high-risk procedure as the current recommendation;
- retain the source link for review;
- label changeable versions, commits, Issues, SHA-256 values, and compatibility claims “re-verify before execution.”

## 4. Prompts and High-Risk Hands-On Procedures

Course material may involve accounts, privacy, process memory, databases, system privileges, downgrade installations, or third-party tools.

- Preserving a course Prompt does not mean recommending immediate execution.
- Distinguish “archived reference” from “the user's current decision.”
- A core Prompt version should retain the authorization statement, platform scope, read-only principle, upstream audit, permission-risk gate, stop conditions, rollback, and acceptance evidence.
- Do not strengthen the course into instructions for bypassing controls, evading risk systems, or gaining unauthorized access.
- An instructor's personal success does not become a universal safety guarantee.
- If the user expresses risk concerns, add a separate editorial note stating that the material may be retained without execution; do not merge the user's concern into the instructor's first-person voice.

## 5. Images Are Also Source Evidence

Infographics, screenshots, and flowcharts in teaching documents may carry information not spoken aloud:

- Inspect the actual pixels of every image; confirming an image block or token exists is insufficient.
- Extract headings, flows, groups, numbers, arrow relationships, and risk warnings from the image.
- To infer a visual style, inspect at least four layouts before identifying a stable visual grammar.
- Before creating a visual Skill, collect 6–10 representative images spanning flowcharts, relationship diagrams, card overviews, device interfaces, and data pages; avoid overfitting to one image.
- Abstract paper texture, palette, typography, layout, iconography, information hierarchy, and use cases rather than copying one image.
- Produce the visual DNA and one test image first; formalize the Skill only after user acceptance.

## 6. Layered Extraction and Conflict Revision for Image-Based Slides

If a PDF exposes copyable text only on the cover and every other page is an image, an empty `pdftotext` result does not mean that the slides contain no content. Use a three-layer evidence chain:

1. **Text-layer inventory:** read page count, dimensions, encryption status, and extractable text; confirm that the file is image-based rather than damaged.
2. **Batch OCR index:** render each page to an image and OCR the batch, producing a searchable draft index of `page → title → terms → numbers → cases`. OCR is for location only, not final authoritative text.
3. **Pixel-level verification of critical pages:** inspect the source image for biographies, amounts, headcounts, brand names, model names, timelines, flowcharts, and summary pages. Correct OCR from legible pixels; never fill text from context alone.

Source responsibilities remain unchanged:

- The transcript is authoritative for the instructor's live argument, first-person voice, and case process.
- Slides correct proper nouns, framework order, explicit on-page numbers, and structures the instructor did not read verbatim.
- Slide text must not be presented as if the instructor spoke it word for word.

When transcript and slide numbers conflict:

- Do not choose silently based on “the slides are more formal” or “the speech is more complete.”
- Record the “live spoken figure” and “slide figure” separately, citing the exact page or timestamp.
- Only the user, source business records, or another authoritative source may resolve the conflict. Until then, use a conclusion that does not depend on the disputed value and list the matter as pending verification at the end.
- If the two numbers might represent different metrics, do not merge them into a total, monthly figure, or cumulative figure.

Also reconcile a slide deck against itself. Treat the cover biography, section headings, timeline nodes, case pages, and summary page as separate statements. If a title says “50→510” while the timeline says “30→200→600,” preserve this as an **internal slide conflict**. In the body, prefer the timeline phrasing with explicit year or stage labels, while recording the title wording in the end notes. Never replace legible source pixels with an OCR approximation or splice the two number sets into a new growth path.

At minimum, critical-page review must cover the cover/instructor biography, master framework, every page with case numbers, process or model pages, timeline, self-assessment checklist, and closing summary. If a course draft treats an image as core evidence, verify that page separately; whole-document OCR is not a substitute.

## 7. End-Matter Format

```markdown
---

## Further Reading and Related Links

- **Companion teaching document for this lesson:** [Course teaching document](source-link)
- **Related resource:** <resource-link>

> These links support later review of course content, retrieval of the complete Prompt, and verification of version information. They do not recommend immediate execution of high-risk operations described in the documents.
```

## 8. Delivery Checklist

- [ ] An image-based PDF was not misclassified as empty because it lacked copyable text
- [ ] Batch OCR was used only for location; critical terms, figures, and case pages were verified against source pixels
- [ ] Transcript/slide conflicts preserve both figures, page/timestamp references, and pending-verification state instead of choosing silently
- [ ] The teaching document was actually read, not reduced to its link title or table of contents
- [ ] Actual image content was inspected, not just an image token or placeholder
- [ ] STT terminology, version numbers, and links were corrected from source evidence
- [ ] Supplemental material has an explicit source identity and was not merged into the instructor's first-person voice
- [ ] A long Prompt is identified as either full text or a core version
- [ ] Internal source conflicts are stated explicitly
- [ ] The user's risk concerns were not rewritten as the instructor's views
- [ ] The end matter contains a clickable link to the source teaching document
- [ ] “Preserve the material” was not interpreted as “execute it immediately”
