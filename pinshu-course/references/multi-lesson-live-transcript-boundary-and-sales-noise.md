# Boundary Splitting, Repeated Playback, and Sales-Noise Handling for Multi-Lesson Livestream Transcripts

Use this reference when one long livestream transcript contains pre-class industry judgments, two or more formal lessons, full repeated playbacks, inter-lesson transitions, post-class sales promotion, and small amounts of new knowledge embedded in the sales ending.

## Objective

Reconstruct the course’s knowledge sequence from the recording timeline while ensuring that:

- Two formal lessons are not merged into one;
- Valuable judgments are not discarded merely because they occur before or after class;
- Numbers, operations, or failure processes added in a later replay are not lost;
- Sales prompts, bookings, and livestream interactions do not enter the course body;
- New course evidence embedded in a generally low-value sales ending is not missed.

## 1. Build a Segment-Attribution Table First

Segment by explicit semantic anchors, not fixed-minute intervals:

| Segment | Common Anchors | Default Treatment |
|---|---|---|
| Pre-class industry judgment | “Before we formally begin,” “Let me first share a judgment” | If directly relevant to the series, include it as background to the next lesson; otherwise register it only |
| Formal lesson opening | “Today we cover Lesson X,” “Last lesson… this lesson…” | New-lesson boundary; highest priority |
| Repeated playback | The same opening, case, or steps recur | Use the first complete segment as backbone; absorb only additions from later segments |
| Next-lesson opening | “Next comes Lesson 5,” “In the next lesson…” | Switch attribution immediately; do not continue writing into the previous lesson |
| Sales ending | Pricing, early-bird offers, reservations, orders, community benefits | Delete by default |
| Knowledge return inside the sales ending | Tools, numbers, or methodological boundaries reappear | Extract separately and merge into the appropriate lesson |

An explicit lesson-number declaration takes precedence over temporal proximity, topical similarity, and old lesson titles.

## 2. Handle Pre-Class Material in Three Ways

### Retain in the Body

Retain material when it explains why the lesson matters, provides a real product case, establishes industry context for the later method, or contains reusable product strategy, tool boundaries, or workflow changes.

Keep the instructor’s first-person voice in the faithful transcript. In the lecture, label it “course background / instructor judgment”; do not elevate it to verified fact.

### Put Only in the Map or Fact Boundary

Use this treatment when material relates to the course but is not developed, or when it consists of market forecasts, user counts, product mergers, or penetration-rate judgments.

### Delete

Delete livestream warm-up, device setup, booking prompts, requests to share, sales pressure, irrelevant household conversation, and comment-thread interaction.

## 3. Separate Device Setup from Credential Exposure

Device setup is usually removable noise. If it contains a remote-control code, pairing code, verification code, account identifier, token, connection string, or any other reusable credential, elevate it to sensitive-information handling:

1. Do not repeat the original value in the faithful transcript, lecture, course map, source note, pending-confirmation list, or delivery response;
2. If the entire segment is connection troubleshooting, delete it. If course content appears in the same segment, preserve the course meaning and replace sensitive values with `[REDACTED]`;
3. Do not retain credentials as “details of a live failure,” and do not reveal their prefixes, suffixes, or lengths to prove they were removed;
4. During acceptance, search semantically for pairing codes, device codes, verification codes, `token`, `secret`, `password`, remote-control references, and likely high-entropy strings. Judge every hit; only generalized boundary descriptions without original values may remain;
5. A user posting a credential in chat does not authorize writing it to a long-term knowledge base.

## 4. Use a Backbone—Increment—Pure-Duplicate Matrix for Replays

1. Choose the first complete and clearest segment as the backbone.
2. Compare every later repetition for new numbers, interface actions, prompt fragments, failures or corrections, permission boundaries, and case outcomes.
3. Merge increments into the corresponding position in the backbone; do not retain a second duplicate explanation in the final draft.
4. Delete pure repetition, but record in the course map’s source note that “repeated playback was merged as backbone + new details.”

Never deduplicate in bulk solely by textual similarity. A repeated segment may add a boundary value, runtime, button name, directory, or recovery step.

## 5. Attribute Cross-Lesson Cases by Teaching Function

- Put the first complete execution process in the practical lesson;
- In the next lesson, retain only the recap needed to introduce the new concept;
- Preserve every new step, comparison experiment, runtime, and result introduced in the new lesson;
- Do not compress the new lesson into “continues from the previous lesson” merely because the case name repeats.

## 6. Never Delete the Entire Sales Ending Mechanically

Before deleting the remaining sales material, scan for:

- Official tool names;
- The instructor’s actual usage data;
- Reasons behind method design;
- Self-corrections of earlier STT errors;
- New limitations or applicable boundaries.

If a sales segment clearly states a tool’s official name, use that clear utterance to correct earlier homophone STT. Pricing, benefits, and order language still must be removed.

## 7. Terminology Authority and Reversal Corrections

Authority order: the user’s latest explicit correction > clear course visuals > a clear later self-restatement in the same transcript > repeated consistent speech > contextual inference.

When the user reverses an earlier confirmation, propagate the latest wording to the faithful transcript, lecture, map, and frontmatter. Search for zero residual occurrences of the old form and verify coverage of the new form. Unless the name change is itself a course fact, do not preserve obsolete confirmation history in the body.

## 8. Gates and Acceptance

### Before Writing

- Identify start and end anchors for every lesson;
- List files to create and modify;
- Check whether target files already exist;
- Mark cross-lesson cases and repeated segments;
- Consolidate interface names, model names, and prompts that cannot be confirmed from text alone.

### After Completion

- Both draft files exist;
- Filename, H1, frontmatter, and map title agree;
- The faithful transcript uses first person, and editorial risk notes are separate callouts;
- Old STT forms have zero residual occurrences;
- Numbers, commands, directories, prompts, and case outcomes are covered;
- The map explains how repeated playback was handled;
- Pending items are grouped by lesson, and status remains draft until the list is empty.
