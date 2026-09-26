# Hands-On Reconstruction

## Step 4: Reconstruct Hands-On Content

Perform this step whenever the source includes operations, prompts, code, or AI collaboration.

### Distinguish Four Information Types

1. **Instructions spoken by the speaker**: Restore them as literally as possible and place them in a blockquote or code block.
2. **Instructions or code shown on screen**: Prefer clear visual evidence and label it “Shown on screen.”
3. **Operations**: Present them in the order they actually occurred; never change the sequence.
4. **AI or software outputs**: Preserve key responses, decisions, errors, and the speaker's subsequent corrections.

### Instruction Format

Do not collect every instruction at the top of the article. Present each instruction in full where it occurs, then optionally add a **Hands-On Recap** or **Instructions and Operations Checklist** after the main text.

Use this format in the main text:

```markdown
### [The problem this operation solves]

The speaker first explains why this approach is needed and what to prepare.

**Procedure**

1. Open...
2. Select...
3. Paste the following instruction:

> [Original instruction that can be confirmed]

**Tool Output and Speaker Corrections**

- AI output: ...
- Problem identified by the speaker: ...
- Follow-up instruction: ...
- Final result: ...
```

Put code, commands, JSON, configuration, and file paths in code blocks. Preserve line breaks, indentation, symbols, and case. Do not rewrite executable content merely to improve readability.

### Handling Incomplete Instructions

- When a complete instruction can be reconstructed from continuous speech and a clear screenshot, merge the evidence and note, “Reconstructed from the spoken explanation and on-screen content.”
- When only the intent is known, label it **Instruction intent**. Do not put quotation marks around it as if it were the original wording.
- Mark obscured, blurred, or undisplayed portions as `[To confirm]`; never invent a complete prompt.
- When the speaker adds requirements over several turns, preserve the sequence as **initial instruction -> AI feedback -> follow-up instruction -> final confirmation**. Do not compress it into one universal prompt.

### Recommended Placement of the Hands-On Recap

Place it after the main body and before any key-point section. Include only categories present in the source:

- original and follow-up instructions;
- quick procedure reference;
- code, parameter, and path list;
- input-material list;
- common errors and the speaker's corrections;
- reproducible workflow.
