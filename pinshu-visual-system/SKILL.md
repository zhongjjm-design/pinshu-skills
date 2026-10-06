---
name: pinshu-visual-system
description: "Create source-faithful article illustrations, covers, social cards and presentation visuals. Route content through explicit structure, layout, visual mode, platform and density; generate with the available image tool, inspect the output and prepare exact-size delivery. Use for visual systems, article illustration sets, hand-drawn explainers, content visuals, cross-platform graphics and user-supplied character consistency."
---

# Pinshu Visual System

Public preview: **0.2.4**. Original methods and tools by Aidan (Pinshu), developed with Codex. This is the portable sharing edition of the locally developed visual system. It contains no private character assets, account mappings or private example material. Repository instructions are English; output and visible text follow the user's requested language.

## Read for the current task

- Read `references/workflow.md` and `references/system-registry.json`.
- Read the chosen mode's complete card in the references/mode-cards directory, for example `references/mode-cards/notebook-knowledge-explainer.md`.
- Read `references/platform-profiles.json` for the chosen platform.
- For business/report graphics, read `references/business-graphics.md`.
- For a supplied character, read `references/character-profiles.md`.
- After rendering, read `references/visual-qa.md` and inspect the actual image.
- For installation, dependencies and command examples, read `references/quickstart.md`.
- For a new visual reference, poster format or colleague feedback, read `references/visual-evolution.md`.

## Companion routing

Use pinshu-infographic for source-anchored knowledge diagrams and pinshu-business-graphics for the seven business-method families when those public companions are installed. They depend on this core for shared style/platform contracts and delivery. Read `references/method-candidates.md` only for explicitly requested cultural-poster method research; its two candidates do not enter default routing.

## Make the visual decision

Identify the source-supported claim, audience, delivery type and actual platform. Fix one visual card:

`character + task + structure + layout + mode + platform + density`

Use one main relationship, one composition and one visual mode per image. A whole article needs a coherent primary visual language and meaningful insertion points, not an equal number of images per section. When the user requests generation, proceed within that scope; otherwise present 2-3 concrete directions and recommend one.

The shared registry provides seven available or scoped modes, one character-dependent mode, three test-only candidates and one frozen candidate. "Available" describes the inherited method scope, not guaranteed cross-theme aesthetic stability. No public mode is described as fully automated production-ready. Character Presenter needs the user's own approved reference and an approved mode pairing. Warm Paper excludes fixed characters. Frozen candidates remain blocked.

## Compile, generate and review

Use `scripts/visual_compiler.py` to save the source, `route-plan.json` and `prompt-final.txt`. The output is a contract, not an image. Choose the mode and structure from actual source meaning; this release does not pretend a keyword classifier can understand an article.

Generate with the agent's available image tool. Load every required identity reference as an actual image input. Record the actual provider/model/channel when the runtime reports them; never guess a model name or silently start a paid API. For long exact text or multiple text blocks, generate an illustration/background and compose an editable text layer using the runtime's supported layout tools. Never paint over incorrect bitmap letters.

Inspect the actual full-size image and its thumbnail. Fix one real defect at a time. Recheck source meaning, wording, actions, identity, composition and platform crop. Internal visual checks and human acceptance are separate. One successful image does not establish repeatable production.

## Prepare delivery

First export the complete composition with scripts/export_platform_image.py; its default contain fit preserves content. Inspect the final platform image and thumbnail, then write the review record described in `references/visual-qa.md`. Run `scripts/publish_image.py` with the image, plan and matching review record. It packages the reviewed platform-sized image, creates a separate metadata-clean PNG copy and verifies pixel preservation. Any failure stops delivery; the source is never used as an export fallback. Any intended crop must be completed before this review.

Deliver the candidate image, insertion position or page function, source/plan/prompt paths, review evidence and any remaining limitation. Use the prepared copy for the reviewed candidate; keep the original. A mechanical PASS does not mean aesthetic approval, factual verification or permission to publish.

## Dependencies and sharing

Planning uses Python 3's standard library. Image generation requires an image-capable agent; no account, subscription or image backend is bundled. Export requires ImageMagick 7 (`magick`). Optional business/chart/PPT tools are chosen only when available; exact editable charts are not replaced by a bitmap.

The shared edition is intended for colleagues and other compatible agents to use and improve with the maintainer. Private character files belong in the user's own local project. The installer refuses to overwrite a same-name private/local visual system; upgrade only a marked public installation.

Before delivery, compose required native text, export the final platform image and inspect it and its thumbnail. Hash-bound QA must use review_stage=final-platform-image. For editable text/chart work, include the actual native SVG/PPTX evidence in QA; the wrapper rejects missing native labels and requires a verified render receipt. Source-external exact text needs a real declared user approval. See the core visual-qa reference for the precise contract.

For native SVG/PPTX composition, read [editable rendering](references/editable-rendering.md). Render with its explicit font and receipt workflow, review the final PNG, then verify re-render pixel identity during delivery.
