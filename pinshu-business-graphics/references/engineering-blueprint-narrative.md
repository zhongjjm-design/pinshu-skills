# Engineering Blueprint Narrative

## Identity

Explain how a system works through components, interfaces, flows, states, and control boundaries. The blueprint must tell an operational story rather than merely signal “technology”.

Use for:

- AI systems, automation, workflows, platforms, and agent architectures
- operating mechanisms, handoffs, feedback loops, and exception handling
- technical-commercial relationships that need both mechanism and outcome

Avoid when the content is only a slogan or when no components and interfaces can be named.


## Composition families

1. `input-engine-output`: inputs enter a mechanism, pass controls, and produce measurable outputs.
2. `exploded assembly`: modules separate spatially while interfaces and ownership remain clear.
3. `state machine`: a small set of operating states, transitions, gates, and failure paths.
4. `closed-loop system`: sensing, decision, execution, measurement, and correction form one traceable loop.

## Information rules

- Name system boundary, inputs, outputs, controls, and human checkpoints.
- Use line styles consistently for data, action, feedback, and exception.
- Show where responsibility changes hands.
- Include failure or override paths when risk matters.
- Do not add meaningless code, pseudo-interfaces, or random technical numbers.

## Typography and color

- Use precise labels, monospaced accents only for real identifiers, and strong hierarchy.
- Favor off-white or dark graphite with cyan, orange, or green used semantically.
- Use schematic symbols sparingly and consistently.

## Prompt kernel

> Create an engineering-blueprint narrative for “[system]”. Use [composition family] to show system boundary, [inputs], [modules], [interfaces], human checkpoints, exception path, and [outputs]. Encode data, action, feedback, and risk with consistent line styles. Use exact labels in the requested output language and a restrained technical palette. No sci-fi glow, no robot head, no meaningless code, no decorative circuit board, no invented interface labels.

## Failure boundaries

Reject when:

- the drawing says “AI” without explaining a mechanism
- lines cross without direction or ownership
- technical decoration exceeds operational content
- no system boundary or human checkpoint exists
- the result could not support a narrated walkthrough

