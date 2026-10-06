# Quick start

Tell your image-capable agent:

> Use pinshu-visual-system to illustrate this article for WeChat. Read the source, recommend a coherent style, produce one first image, inspect it, and continue only when the direction works. Use no fixed character.

For a simple supplied brief, run from this Skill directory:

```bash
python3 scripts/visual_compiler.py \
  --content-file examples/brief.md \
  --platform wechat-article \
  --mode notebook-knowledge-explainer \
  --structure process --units 3 \
  --title "Review the draft" \
  --output-dir ./work/draft-review
```

The output directory must be new. Read prompt-final.txt and submit it to the runtime's image tool. The CLI does not call an image API. Supply --character-profile with your own approved local JSON to add an identity; use --candidate-test only for a single explicitly requested candidate experiment.

For editable text, compose the complete native SVG/PPTX and read [editable rendering](editable-rendering.md). Render and export together with an actual installed font:

```bash
python3 scripts/render_editable.py \
  --source ./work/composite.svg \
  --font-file "/System/Library/Fonts/STHeiti Light.ttc" \
  --platform wechat-article --output-dir ./work/rendered
```

Use a readable installed CJK font on your system; the Mac path is an example to check, not a font distributed with this Skill. Attach work/rendered/render-receipt.json in QA editable_source.render_receipt. For short-text raster plans, use export_platform_image.py before QA instead.

Inspect that final image and thumbnail, then write review_stage=final-platform-image and its exact hash. With this completed review:

```bash
python3 scripts/publish_image.py \
  --source ./work/rendered/platform-final.png \
  --plan ./work/draft-review/route-plan.json \
  --qa ./work/visual-review.json \
  --output-dir ./work/delivery
```

Planning needs Python 3. Export needs ImageMagick 7. macOS users can install it with `brew install imagemagick`; on other systems use the official ImageMagick 7 installation for that system and verify `magick -version`. The package never installs tools or starts billing automatically.

Run meaningful local checks:

```bash
python3 -m unittest discover -s tests -v
```

The shared package has a separate VERSION (0.2.4) from its internal ancestor. Existing private installations must not be replaced with it; the repository installer deliberately refuses that collision. On a clean colleague machine, the repository installer adds the visual Skill with both visual companions and the other suite packages. Restart the client afterward and verify it can discover the Skill and access an image backend.

## Explicit cultural-poster test

A candidate method is separate from a visual mode. For a single experiment:

```bash
python3 scripts/visual_compiler.py \
  --content-file examples/craft-paper.source.md \
  --platform xiaohongshu --method-candidate oriental-material-craft \
  --structure single-claim --candidate-test --title "Paper from water" \
  --output-dir ./work/craft-test
```

Supply a short localized title when required. The method branch rejects fixed-character profiles, custom layouts, multi-node units and exact-text arrays. It does not automatically recommend candidates. A completed QA record needs the five core checks plus method-grammar and cultural-source-fit; the wrapper enforces these even if the plan's required_checks array is changed. Obtain human acceptance and further theme tests before promoting a method.

A companion plan similarly requires its own specialized checks. See each companion's quickstart for its schema. Data Journalism requires a real native chart source plus a reviewed PNG preview. The wrapper can package a verified SVG/PPTX and its preview; a PNG alone remains blocked.

Source-external exact labels need --approved-text-file pointing to a JSON list of text, approved_by, reason and user_quote declarations. Preserve actual user authorization; do not fabricate it. The default contain export preserves content; an explicit cover crop reports edge loss and requires inspection before QA.

Before exporting any editable text/chart composite, follow the core editable-rendering.md reference: use render_editable.py with an installed CJK font, attach its render_receipt to QA and use platform-final.png as the reviewed source. Do not substitute a manually exported preview from another renderer.
