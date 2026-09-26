# Per-Lesson Processing for High-Density Platform Courses

Use this workflow for lessons with long transcripts that simultaneously cover media principles, platform differences, algorithms, monetization, violations, and many question-and-answer cases. The goal is neither to compress the lesson into a summary nor to preserve spoken order as a wall of text.

## 1. Identify a Multi-System Lesson First

Treat a lesson as high-density when it contains at least three of the following:

- stable methodology or judgment frameworks;
- time-bound platform experience;
- algorithmic or product mechanisms;
- monetization, paid traffic, and conversion;
- compliance, medical, financial, or platform-governance issues;
- multiple rounds of learner questions and counterexamples;
- first-hand instructor figures for views, followers, or sales.

Do not force all of this into a short summary. Continue using “paired drafts plus course map,” but assign explicit responsibilities to the two drafts.

## 2. Faithful Edited Transcript: Preserve the Instructor's Voice First

1. Preserve the instructor's first-person voice and original speaking order. Greetings, microphone adjustments, and no-information interaction may be removed.
2. Retain follow-up questions, rhetorical questions, corrections, counterexamples, and figures that add information; do not reduce them to “learners asked several questions.”
3. When the instructor discusses platforms, regulation, ownership, algorithm scale, or earnings, preserve the original meaning in the body. Put verification notes in a separate block quote; do not turn the body into third-person narration such as “the instructor believes” or “the course states.”
4. After writing, scan the full text for `instructor-believes|course-believes|instructor-mentioned|course-reminds|mentioned-in-course`. Rewrite body matches into first person. Only source notes and separate editorial notes may retain a third-person perspective.
5. Preserve the full case chain: who the user was → why a certain response emerged → how the platform adjusted → what the case demonstrates. A case name alone is insufficient.

## 3. Systematized Lecture: Reorganize by Knowledge System

Do not mechanically preserve spoken order in a high-density lesson. Recommended structure:

1. problem solved by the lesson;
2. stable judgment framework;
3. platform differences;
4. algorithmic or distribution mechanisms;
5. demand, competition, and traffic models;
6. monetization and paid traffic;
7. risk, factual, and compliance boundaries;
8. execution checklist, diagnostic table, or assignment.

For every module, preserve `context → course judgment → reasoning → complete case → applicability conditions → use`. Tables support comparison and review; they do not replace explanatory prose.

## 4. Conflicting Dates and Source Conventions

The course-directory date, release batch, and recording date stated by the instructor may differ. When they conflict:

- record `date` (archive date/course batch) and `recording_date_claimed` (instructor's spoken claim) separately in frontmatter;
- add a brief opening note that the dates may refer to different stages;
- do not resolve or rewrite one into the other without official information;
- carry the note into the course map so later lessons do not misuse the date.

## 5. Layer Platform Facts and Gray-Area Cases

By default, none of the following is externally verified fact:

- internal platform-label counts, recommendation formulas, or real-time adjustment conventions;
- claims about platform ownership, regulatory authority, or political mandates;
- course retellings of creator conferences, algorithm upgrades, or traffic-pool changes;
- views, sales, conversion, and refund figures reported by the instructor or learners;
- gray-area tactics involving foot-bath businesses, private-domain operations, follower cleansing, or acquisition through false identities.

The faithful transcript preserves course context. The systematized lecture creates a “facts, experience, and risk boundaries” table distinguishing course viewpoints, instructor experience, unverified facts, and gray-area methods that should not be copied. Never turn a vague tactic into operational instructions for evading platform governance.

## 6. Platform-Data Review Lessons: Build a Diagnostic Tree Before Placing Thresholds

When the lesson itself reviews views, engagement, followers, transactions, or account operations, organize the systematized lecture in this order instead of by the view bands reported by the instructor:

```text
content objective
→ influencing factors
→ audience/transaction funnel
→ multiple samples and baselines
→ attribution and alternative explanations
→ actions for the next batch
```

### 1. Separate Content Objectives First

Distinguish at least persona/follower-growth content, lead-generation content, product-linked/conversion content, and live streams. Different objectives must not share one metric set. Product-linked content, for example, cannot be judged only against persona-video view thresholds, and a conversion live stream cannot be judged only by concurrent viewers.

### 2. Demote View Bands to an Experience Ladder

Spoken ranges such as “below 5,000,” “5,000–50,000,” “hundreds of thousands,” and “millions/tens of millions,” or like-rate thresholds such as 5% or 10%, are **instructor experience thresholds** only. The lecture must give the more reliable evaluation order:

1. the account's historical median for comparable content;
2. a peer baseline with similar objective, format, duration, and traffic source;
3. broad platform-dashboard references;
4. course thresholds only as a final auxiliary check.

Do not turn Douyin experience from one recording period into a permanent rule across platforms, industries, and account stages.

### 3. Distinguish Viewers, Engagers, and Followers

- A viewer model answers “Who did this item attract?”
- A follower model answers “Who did the account retain over time?”
- Commenters, likers, followers, and silent viewers cannot substitute for one another.

Visible commenters do not automatically represent the actual user base. If a case observes that commenters skew toward beginners while silent followers are more experienced, preserve the observation process and state that only legally visible platform data may be used; do not collect sensitive data or create profiles beyond authorization.

### 4. Curves Are Leads, Not Causation

Completion, like, and comment curves only locate an inspection range. If a drop occurs at second 8, inspect seconds 2–5 for an earlier information stall, rejection-triggering phrase, or visual problem. Do not mechanically state that “the sentence at second 8 caused the drop.”

### 5. Reduce Misdiagnosis with Batch Samples and Controlled Variables

If the course recommends “review three together,” batches of five to ten, or an A/B test, complete the specification with sample scope, self-baseline, primary changed variable, variables kept similar, alternative explanations, and the next batch test. Content creation is not a laboratory; state that “the current sample supports” a conclusion, never that “users always like/dislike” something.

### 6. The Lecture Must Specify a Next Action

Provide at least one fillable asset: review table, transaction-funnel table, issue-priority matrix, controlled-variable experiment table, account-stage assessment, or 30-day implementation plan. Prefer the action order “standardize what is working, then correct one or two high-impact local issues” instead of rebuilding everything after every review.

## 7. Minimum Acceptance Set

After writing, verify at least:

- paired drafts and course map actually exist;
- every file contains one H1 and complete frontmatter and tags;
- map links and the lecture's relative `source` path resolve;
- the faithful-transcript first-person scan returns zero violations;
- a contextual glossary of frequent STT residual terms was created and searched;
- no `TODO`, `TBD`, continuation sentinel, ellipsis placeholder, or empty image directory remains;
- recording/archive date conflicts remain explicit;
- platform facts, experience thresholds, time-sensitive features, earnings figures, and gray-area cases are layered correctly;
- the map uses two-phase commit: after source files are complete it says `preview-sync-pending/acceptance-pending`, and only after the preview exists and is reconciled does it say `unrestricted-acceptance-passed`;
- when a preview copy is required, at least compare the text of both drafts and the map. If the user explicitly excludes SHA, do not run it. If the permission layer blocks SHA or statistics, do not rewrite the command, switch tools, or bypass the block; record the check as not run;
- a permission block describes only the current action state and must not be generalized into “this tool is permanently unusable.”

## 8. Avoid Overengineering

However long a single lesson is, do not build all six cross-topic libraries from the first lesson. Complete the paired drafts and map first. Every 3–5 lessons, or at module closeout, consolidate stable cross-lesson models, cases, and tools. If a module still has missing lessons, the map must show the completed set and proportion; processing the final-numbered lesson does not by itself close the module.
