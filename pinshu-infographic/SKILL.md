---
name: pinshu-infographic
description: "Turn source material into readable knowledge diagrams: processes, comparisons, hierarchies, components and real feedback loops. Use for information graphics, course explainers, Chinese knowledge diagrams and presentation illustrations. Shares style, character and platform contracts with pinshu-visual-system; cultural atmosphere posters use the core instead."
---

# Pinshu Infographic

Public preview **0.1.4**, created by Aidan (Pinshu) with Codex. Read the actual source, expose one information relationship and produce a readable diagram. This portable edition includes no personal character artwork or private examples.

## Dependencies and routing

Requires the public pinshu-visual-system 0.2.4 or later package beside this folder. It owns mode cards, optional approved character profiles, platform presets, generation planning and delivery. This package adds source-anchored units, arrow meaning, reading density and diagram review. If the public core is missing, report the dependency; do not overwrite or use an existing private core.

When this Skill's entry is a symlink, resolve its real package directory first (Python: `Path(skill_md_path).resolve().parent`). Read this package's references there and load `../pinshu-visual-system/SKILL.md` relative to that real directory. Use that sibling for all mode cards, render and publish commands. Do not look up the core by its global Skill name: a private core may legitimately occupy that name. The installer supplies the public sibling automatically. Run the quickstart commands from the real package's parent directory; the planner resolves the same sibling even when invoked through the shared entry link.

Read `references/logic-and-density.md` for content structure and viewing distance, `references/mode-routing.md` for style choice, `references/visual-qa.md` for diagram review, and `references/quickstart.md` for the executable brief and delivery commands. Load the complete selected mode card from the public core.

Jim Liu's baoyu-infographic may be used as an optional, separately installed analysis/layout workflow. Retain its attribution and inspect its own current license before use. No upstream code, templates, instructions or reference images are bundled. The included planner works without that upstream package; do not install third-party tools merely because this Skill mentions them.

## Explain before styling

State one main claim and choose the source-supported relationship. Build short information units, each tied to a verbatim source excerpt. Give every arrow a verb and a source excerpt. A real loop returns to its starting stage; parallel responsibilities do not form a loop. A literal excerpt match establishes provenance, not the truth of a paraphrase or causal arrow.

Choose document or slide density. Document diagrams can carry up to seven principal units; slides up to five. Use fewer when the chosen mode has a tighter limit, when there are long Chinese labels, or when a vertical crop needs simpler reading. Keep one main structure and at most two annotation levels. Split overloaded content rather than shrinking essential labels.

## Select a mode and render

Warm Paper is the character-free starting point for knowledge diagrams. Lively Vector remains an explicit single-image candidate experiment. Character Presenter requires the user's own approved identity reference and tested pairing; no Pinshu role or legacy alias is assumed.

Compile the structured brief with scripts/plan_infographic.py. Save the exact generation prompt before calling the runtime's image tool. Produce and inspect a first image before extending a series. Follow the user's language; keep exact names, numbers and quotations accurate. Multiple or long exact labels go into a separate editable layer. A background without that layer is not a finished information graphic.

For editable slides, keep essential labels, figures, arrows and simple shapes native in the slide tool; raster illustration is an asset. This package does not bake an entire editable deck into screenshots.

## Review and deliver

Inspect the actual full image and the thumbnail. Check source meaning, labels, arrow directions, density, selected mode, identity where present and the target crop. Record the core checks plus information-relationships, density-and-reading and text-delivery against the exact bitmap and plan hashes.

Use the public core's scripts/publish_image.py for platform export and a separate metadata-clean copy. Any export failure stops delivery. Report image, source, brief, prompt, plan and review paths; state text-layer completion and remaining limitations. Agent review, mechanical PASS and the user's aesthetic acceptance are separate states. This edition is usable for shared trials, not a claim that every topic is stable in batches.

Before delivery, compose required native text, export the final platform image and inspect it and its thumbnail. Hash-bound QA must use review_stage=final-platform-image. For editable text/chart work, include the actual native SVG/PPTX evidence in QA; the wrapper rejects missing native labels. Source-external exact text needs a real declared user approval. See the core visual-qa reference for the precise contract.

For native SVG/PPTX composition, read the sibling core reference `../pinshu-visual-system/references/editable-rendering.md`. Render with its explicit font and receipt workflow, review the final PNG, then verify re-render pixel identity during delivery.
