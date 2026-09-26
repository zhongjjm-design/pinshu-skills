# Markdown Heading Spacing and Asynchronous Finalization Control

Use this reference when long course transcripts, structured lectures, and dissemination cards are generated, refined, and written by multiple agents or background processes.

## 1. Heading Spacing Is a Delivery Acceptance Criterion

In Markdown source, every body heading (H1/H2/H3) must be followed by at least one blank line before a paragraph, list, blockquote, or code block begins. It is not enough to confirm that the heading parses correctly. In some Obsidian themes, body text immediately following a heading appears visually stuck to it.

Minimum rule:

```markdown
## Heading

Body text begins here.
```

Notes:

- Reading views usually collapse multiple blank lines; one is enough;
- A `#` inside frontmatter is not a body heading;
- Final acceptance must inspect the line after every H1/H2/H3. The violation count must be zero;
- If the user supplies a screenshot showing spacing problems, inspect the actual line breaks in the source file rather than dismissing the issue because “Markdown adds default spacing.”

## 2. Late Background Results Are Stale by Default After Promotion

Background subagents, Codex processes, and batch jobs must write only to exclusive temporary files. After the main agent promotes a draft into the formal library and reads it back, establish an explicit terminal state: formal path, line count, critical sections, and constraint-scan results.

If an older background task finishes later:

1. It must not overwrite the formal draft directly;
2. Determine whether it was based on an obsolete snapshot;
3. Compare it against the current formal draft and check whether it reintroduces removed content such as sales pushes, group invitations, QR codes, old STT terms, or obsolete formatting;
4. Absorb only clearly beneficial changes through targeted patches;
5. Re-run the complete constraint scan and heading-spacing check;
6. If it adds no value or violates current requirements, retain it as a temporary result and explicitly decline to promote it.

## 3. Speed Gate: Avoid Endless Refinement

Once a faithful transcript covers source order, cases, numbers, and sections, and only a few localized speech remnants remain:

- Prefer deterministic targeted corrections and a global residue scan;
- Do not launch multiple overlapping whole-document refinement agents;
- If the user reports that progress is too slow, stop expanding the process. Complete the minimum necessary corrections, write, and read back;
- Background-task volume is not quality. Completion depends on the main agent’s actual acceptance.

## 4. Final-Acceptance Checklist

- [ ] The formal file exists and can be read back as UTF-8;
- [ ] There is exactly one H1, and H2/H3 counts match expectations;
- [ ] Every H1/H2/H3 is followed by at least one blank line;
- [ ] Residual specified STT errors, marketing noise, and placeholders total zero;
- [ ] The faithful transcript remains first-person and preserves cases, numbers, and process;
- [ ] Late background output has not overwritten the formal draft;
- [ ] The completion report contains only absolute paths and key acceptance results.
