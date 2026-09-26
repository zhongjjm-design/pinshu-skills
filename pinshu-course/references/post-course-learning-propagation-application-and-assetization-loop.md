# Post-Course Learning, Explanation, Application, Dissemination, and Assetization Loop

## Core Judgment

Transcripts and lectures are a usable foundation for course knowledge. They do not prove that the user understands, has mastered, or can apply it. After course completion, first determine which result the user wants and route accordingly. Do not generate every derivative product by default.

## Six Outcomes

### 1. Understand

The goal is to organize the instructor’s content into knowledge the user can read independently. Use `pinshu-distill` to produce structured lectures, concept relationships, method entries, and formal cross-lesson topics. Acceptance is not “all headings exist”; a person who has not seen the course must be able to explain the problem, principle, steps, conditions, cases, and boundaries.

### 2. Master

The goal is active retrieval from memory. Use `pinshu-study` for guided study, active recall, follow-up questions, error analysis, source review, and retesting. Reading, highlighting, and saving do not qualify as mastery.

### 3. Explain

The goal is to express the course in the user’s own language so a specific audience can understand. Use the Feynman explanation path in `pinshu-study`: the user explains without looking at notes; the Agent plays the audience and asks follow-up questions; conceptual, inferential, case, evidence, boundary, and expression gaps are identified; the user returns to the source and explains again. An audience nodding does not prove mastery. Passing requires handling follow-up questions, counterexamples, and transfer questions.

### 4. Apply

The goal is to transfer a course method into a real project. Select one concrete business problem and specify: which course judgment will be used, prerequisites for validity, intended actions, business metric, stop condition, and review time. After execution, record the actual outcome and distinguish method failure, unmet conditions, and execution failure.

### 5. Disseminate

The goal is external sharing, an article, a course, or internal team training. Generate expression materials only after basic understanding is complete. Prefer the user’s own experience, judgments, and cases, and distinguish the instructor’s words, the user’s synthesis, and editorial expansion. The main file selects dissemination-reuse rules based on the user’s current objective, avoiding recap copy such as “my biggest takeaway from today’s lesson.”

### 6. Assetize

The goal is to preserve methods that remain effective across repeated real applications as cases, SOPs, Skills, or products. A method taught in a course is only a candidate. It enters the formal capability library only after validation in at least one real context, with applicable conditions, failure modes, acceptance criteria, and human boundaries documented.

## Recommended Loop

```text
Raw evidence
→ faithfully edited transcript
→ structured lecture
→ cross-lesson knowledge map
→ active recall
→ user’s first explanation
→ audience questions and gap list
→ return to source and correct
→ user’s second explanation
→ transfer to a real project
→ outcome review
→ update the lecture, case, Skill, or product
```

This is not a mandatory pipeline to run for every lesson. If the user wants only to consult original wording, stop at the faithful transcript. If the user wants quick understanding, stop at the lecture. Continue only when the user explicitly wants mastery, explanation to others, or business application.

## Evidence Levels for Mastery

- **Recognition:** the answer looks familiar when seen;
- **Recall:** the core structure can be stated without the material;
- **Explanation:** causality and cases can be explained in the user’s own words;
- **Response:** audience questions, counterexamples, and boundaries can be handled;
- **Transfer:** the method can be applied to a new real problem;
- **Creation:** practice can refine the method and generate a new asset.

The course map and personal records mark only states supported by existing evidence. File generation does not upgrade mastery automatically.

## File and Directory Discipline

1. Read the course map and inspect existing directories first. Reuse any equivalent category rather than creating a duplicate with a different number from a template.
2. Store faithful transcripts, lectures, cross-lesson topics, personal learning records, external sharing, and business-application records separately so none can overwrite another.
3. Preserve the user’s original explanation. Do not save only an AI-polished perfect version, because that hides actual learning gaps.
4. Write real project outcomes back to application records. Promote experience to a general Skill only after it holds across contexts.

## Minimum Acceptance

- Explanation training preserves at least the first explanation, audience questions, gaps, source locations, and second explanation;
- Application training preserves at least one business hypothesis, one action, one metric, one stop condition, and the outcome;
- External sharing clearly labels instructor viewpoints, user understanding, and editorial synthesis;
- Every assetized entry can answer when to use it, why it works, how to apply it, when it fails, and how to accept the result.
