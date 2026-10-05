# Core Editing Rules

## Step 1: Identify the Content Type

Read all input and identify the primary type. Mixed material may match several types at once.

| Type | Preserve especially |
|---|---|
| Talk / opinion course | Claims, evidence, examples, rebuttals, data, emotional expression |
| Interview / multi-speaker conversation | Speaker identity, follow-up questions, disagreements, contextual continuity |
| Hands-on demonstration course | Procedures, entered content, tool feedback, parameters, files, exceptions, and corrections |
| Coding / technical course | Code, commands, configuration, dependencies, errors, versions, and runtime results |
| Personal voice note | Sequence of thought, action items, judgments, and unfinished but valuable leads |

If the source includes screenshots, slides, screen-recording frames, or attachments, treat the visual material as source evidence. Do not rely only on spoken-word STT.

## Step 2: Build a Terminology and People List

Before editing, build an internal proofreading table. It need not appear verbatim in the output. Include:

- names of people, teams, brands, products, tools, and models;
- English terms, abbreviations, and correct capitalization;
- lesson numbers and numeric facts such as times, prices, percentages, and version numbers;
- spellings the user has already corrected;
- candidate homophone errors and the contextual evidence for each.

This skill creates and maintains the course glossary. On the first lesson, create `00_Terminology-and-Corrections.md` in the course root unless an equivalent already exists; use the established local naming convention when different. Load it before each later lesson and add newly confirmed raw-to-correct mappings afterward. Recurrent STT errors should be corrected consistently across lessons. Display only confirmed spellings in edited material; keep erroneous source forms in the immutable raw source, glossary mappings, or internal source-trace notes.

Priority: explicit user correction > course terminology glossary > clearly legible on-screen text > repeated consistent usage within the same material > contextual inference. Do not expand the transcript with web research merely to correct an external fact that may have changed; flag a separate verification need instead.

## Step 3: Clean the Main Text

### Correct STT Errors

- Correct homophone errors, polyphonic-character errors, sentence breaks, duplicate recognition, and word-order slips.
- Restore specialist names such as Claude Code, Codex, Agent, MCP, Prompt, Token, RAG, API, Skill, and Obsidian.
- Correct English capitalization, numeric units, and obvious mismatches between languages.
- Use one spelling for the same term throughout, without collapsing distinct concepts that the speaker intentionally distinguishes.

### Remove Speech Noise

- Delete fillers that carry no meaning, such as “um,” “uh,” “er,” “like,” and “what I mean is.”
- Delete mechanical repetition, stuttering, and abandoned versions after a verbal correction; retain the final expression.
- Retain speech that contributes tone, rhetorical force, pacing, or individual voice.
- Do not mechanically delete words such as “then,” “so,” or “right?” when they carry logical transitions or speaking style.

### Handle Timestamps and Live-Session Chatter

- Remove timestamps by default. Retain key timestamps when the user requests a timeline.
- Remove pure equipment chatter, such as “Can you see my screen?” or “Let me adjust the microphone.”
- **Never remove reproducible operations**, such as which page to open, which button to click, what to paste, and what appears after pressing Enter.
- Preserve speaker labels in multi-speaker material. Repeated identity labels may be removed from single-speaker material.
