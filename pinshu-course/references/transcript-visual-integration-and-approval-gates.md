# Course Corpus Editing, Slide Integration, and Execution Gates

Use this reference for three high-risk areas in long-term course knowledge bases: executing prematurely while a user is still submitting feedback, allowing a faithful transcript to swing between subtitle dump and third-party interpretation, and damaging reading flow by inserting slide information as abrupt patches.

## 1. State Machine: Material Input Is Not Execution Authorization

### Collection State

Signals: the user continues sending audio, screenshots, or transcripts; says “I am not finished” or “listen first”; or is correcting standards without approving a plan.

Behavior: acknowledge receipt, restate, and record unresolved points only. Do not write files, batch-rework history, update cross-lesson libraries, or promote candidate conclusions into formal outputs.

### Discussion State

Signals: “What do you think?”, “Let’s discuss this,” or “Should this image remain an image or become text?”

Behavior: provide options, short samples, and tradeoffs. A recommendation is not approval.

### Execution State

Signals: “Confirm execution,” “Do it this way,” or “Start with Lesson 07 so I can review it.”

Behavior: restate and strictly limit scope. Old authorization does not automatically cover earlier lessons, later lessons, another draft type, or the cross-lesson knowledge base.

### Mid-Execution Reversion

If the user continues supplying feedback while execution is underway, pause later operations immediately and return to collection state. An in-progress task list is not authorization to continue.

## 2. Faithfully Edited Transcript: An Article Written in the Instructor’s Own Voice

Its role is neither summary nor proofread subtitles. It is:

> Edit the instructor’s spoken course into an article still narrated by the instructor in first person.

The editor should disappear. Avoid third-party interpretive phrases such as “the course mentions,” “the instructor wants to explain,” “the author believes,” and “this case shows.”

### Semantic Equivalence, Not Sentence-by-Sentence Copying

Allowed:

- Delete non-informative fillers such as “um,” “ah,” “right?”, “everyone look,” and “OK”;
- Delete course-process language and mechanical repetition that adds no information;
- Merge synonymous sentences and adjust sentence order, paragraphs, and subheadings;
- Convert meandering speech into natural written language.

Not allowed:

- Delete people, products, concrete scenes, numbers, prices, tools, or case processes;
- Change causality, qualifiers, or judgment strength;
- Replace category-specific concepts with vague higher-level terms;
- Quietly sanitize, soften, or amplify the author’s viewpoint for safety, professionalism, or stylistic consistency.

### Semantic-Anchor Examples

| Source Anchor | Incorrect Editing | Correct Treatment |
|---|---|---|
| “Change-of-fortune effect” | “Expected effect” | Retain “change-of-fortune effect”; annotate risk separately |
| CNY 69 diagnosis, CNY 999 coaching | Low-priced product to high-priced service | Retain products, prices, and the conversion relationship |
| Insomnia at night, lying at home after quitting without another job | Career confusion | Preserve the concrete situation, then summarize if needed |
| 53 action guides and 64 cases | Rich content | Preserve the numbers and their evidentiary function |
| Sold several thousand yuan in one day and customer service could not keep up | Service pressure rose with sales | Preserve sales, problem, and process |
| “Northeastern everything stew” | Somewhat disorganized information | Preserve the distinctive original metaphor |

### Handling Risk Content

Preserve the author’s viewpoint faithfully in the body. Put verification notices in a separate editorial note, footnote, or boundary section of the systemized lecture. For example, references to “changing fortune” or “improving wealth luck” remain in the body but are labeled separately as user beliefs and marketing cases from the course, not verified effects.

## 3. Semantic Reconciliation

After faithful editing, compare the opening, a middle case, and the ending against the source:

- Are people and relationships preserved?
- Are products, tools, and platform names preserved?
- Are scenes, numbers, prices, and times preserved?
- Did causality or sequence change?
- Did judgment strength shift among terms such as “most,” “possibly,” and “certain”?
- Were concrete terms replaced by vague abstractions?
- Did the editor add an explanation the instructor never made?

Principle: **remove noise, not information; change syntax, not meaning.**

## 4. Reading-Edit Standard

Support three reading speeds:

1. Headings alone reveal the course path;
2. Bold text and quotations reveal key judgments;
3. Full body reading provides the complete reasoning and cases.

Rules:

- Use one H1 and natural H2/H3 sections;
- Each paragraph carries one complete idea. Avoid both solid walls of text and subtitle-like one-sentence fragments;
- Bold core conclusions, definitions, numbers, and decisive actions, not whole paragraphs;
- Distinctive source wording may use blockquotes;
- Use lists only when the instructor enumerates items explicitly;
- Give cases clear headings while preserving background, concern, process, adjustment, and outcome.

## 5. Systemized In-Depth Lecture: Explanatory Textbook, Not Slide Outline

The systemized lecture may adopt a neutral knowledge-organizer perspective and reorganize content, but it must not collapse into conclusions, formulas, tables, and checklists.

A significant knowledge module should develop:

```text
Problem background
→ core judgment
→ why it works
→ internal relationships within the method
→ complete case
→ reusable elements
→ conditions that must not be copied
→ execution method
```

Recommended structure:

1. Orientation and the lesson’s place in the course;
2. Core problem and background;
3. Key models and relationships among models;
4. Complete walkthroughs of all important cases;
5. Counterexamples, misconceptions, factual boundaries, and compliance boundaries;
6. Execution tables, assignments, and diagnostic templates;
7. Knowledge map and relationships to earlier and later lessons.

Place tables and checklists after explanation as comparison and execution aids. They cannot replace prose. Acceptance criterion: someone who has not watched the video can understand what was taught, why it works, how cases developed, and how to apply the method.

## 6. Slides and Screenshots: Integrate Naturally, Not as Abrupt Patches

When slides contain tables, models, numbers, or product pages not fully stated in the narration:

1. Save original images permanently at the manifest/path-map target `{lesson_assets}`;
2. Embed each image where the instructor naturally discusses the topic;
3. Convert tables and models fully into text. For product pages, extract key selling points, numbers, structure, and visual logic;
4. Use concise captions such as “Figure 1 | Original course slide: Six Elements of a Selling Proposition”;
5. Do not interrupt the narrative with long “slide supplement / source explanation” blocks;
6. Do not present image text as though the instructor spoke each item;
7. Let the instructor’s first-person narrative connect naturally in the faithful transcript. The lecture may explain further but must label provenance boundaries.

Incorrect rhythm:

```text
Author body → image → slide supplement → source declaration → editorial summary → return to author body
```

Correct rhythm:

```text
Author introduces method → body explains → original course slide serves as visual evidence → case continues
```

### Build a Visual Evidence Chain for Multiple Slides

When several slides appear consecutively, do not recognize each in isolation and insert them mechanically. Identify each image’s argumentative function before placing it. Common functions include:

1. **Problem-evidence image:** shows actual risk, errors, user feedback, or failure scenarios;
2. **Path-comparison image:** compares extra actions, decisions, or drop-off points in two processes;
3. **End-to-end flowchart:** completes nodes and order distributed across the narration;
4. **Before-and-after optimization image:** shows the original path, obstacle, change, and result;
5. **Metric-funnel image:** maps business stages to metrics such as impression, click, purchase, contact-addition, positive-review, or referral rates.

First write the evidence chain for the whole image set, for example:

```text
Payment risk
→ transaction-path bottleneck
→ complete buyer flow
→ change before and after optimization
→ funnel-metric review
```

Then place each image in the body module where it performs that function. The images should advance one course argument, not become five unrelated attachments.

### Maintain a Register of Information Appearing Only in Images

After visual inspection, record content clearly shown on a slide but not explicitly stated in the narration, such as:

- Additional process nodes;
- Arrow directions and branch conditions;
- Complete before-and-after paths;
- Metric names, numbers, and stage relationships;
- Positive reviews, repurchases, or referrals after service;
- A “direct effect” relationship labeled on one node.

Processing rules:

1. **Faithfully edited transcript:** these details may be converted to text and integrated naturally, but captions or provenance notes must identify them as originating from original course slides; never present them as sentence-by-sentence speech;
2. **Systemized lecture:** may explain image relationships further, but must distinguish “explicitly expressed by the slide” from “editorial inference from the diagram”;
3. **Fact verification:** platform rules, conversion rates, and individual outcomes in images remain course material and do not automatically become universal facts;
4. **Semantic reconciliation:** before delivery, reconcile both spoken and visual anchors; transcript keyword search alone is insufficient.

### Preservation Order for Temporary Attachments

When chat attachments reside in temporary storage, after execution authorization complete this sequence first:

```text
Confirm image and lesson attribution
→ copy to the rendered `{lesson_assets}` target
→ assign a semantic filename
→ verify existence, non-empty content, and pixel dimensions
→ only then write a relative path in the body
```

Do not reference a temporary path in a draft first, and do not claim an image is archived before saving the original. Multi-image names should reflect both sequence and function, for example:

```text
01_Payment-Risk-and-Purchase-Abandonment.png
02_Transaction-Path-Comparison.png
03_Complete-Buyer-Flow.png
04_Conversion-Path-Before-and-After.png
05_Funnel-Stages-and-Metrics.png
```

## 7. Anti-Complexity Strategy

Use a progressive “2 + 1” model:

- Per lesson: faithfully edited transcript + systemized in-depth lecture;
- Per lesson: lightweight course-map update;
- Every three to five lessons or at module close: consolidate methods, cases, tools, and templates across lessons;
- Only after a method is corroborated across lessons and cases should it become a Skill, Agent, or original course.

Do not manufacture eight redundant documents per lesson.

## 8. Pre-Delivery Check

- [ ] The user explicitly entered execution state and scope did not expand;
- [ ] The faithful transcript remains narrated by the instructor in first person;
- [ ] No third-party interpretation such as “the course mentions” or “the instructor wants to explain” remains;
- [ ] The opening, a middle case, and the ending passed semantic reconciliation;
- [ ] Specific nouns, numbers, prices, scenes, and judgment strength were not generalized;
- [ ] The page is neither a wall of text nor subtitle-like fragments;
- [ ] The lecture contains explanatory prose and complete cases, not lists alone;
- [ ] Slides are permanently saved, naturally embedded, and searchable as text;
- [ ] Course information, editorial analysis, and fact verification are distinguishable;
- [ ] Other courses and files outside the approved scope remain untouched.
