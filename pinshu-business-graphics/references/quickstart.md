# Quick start and brief

Install this package with the marked public pinshu-visual-system 0.2.4 or later in the same parent directory. Planning uses Python 3. Rendering needs an image-capable agent; raster delivery needs ImageMagick 7. No model subscription or charting backend is included.

From the repository root:

```bash
python3 pinshu-business-graphics/scripts/plan_business_graphic.py \
  --brief pinshu-business-graphics/examples/brief.json \
  --output-dir ./work/business-plan
```

The brief names source_file, claim, claim_source_excerpt, mother, platform, structure, units and relations. A unit has id, label and source_excerpt. An arrow has from, to, verb and source_excerpt. Excerpts must occur verbatim in the source. The seven mother IDs correspond to this package's seven method cards.

metaphor has description and status: none, proposed or source-literal. A literal metaphor also needs a matching source_excerpt. delivery_medium is raster-concept or editable-required. exact_text lists immutable names, terms, numbers or quotes. Multiple or long labels route to an editable layer. output_language follows the user's requested language.

For a data graphic, dataset has rows, source, period, units, methodology, verified_by and status=verified. Each row has label, value and source_excerpt. Numeric provenance is mechanically checked, but the declared verifier and source reliability still need actual review. Data Journalism forces an editable chart final even when a raster concept was requested. A raster alone is blocked. Use an actual chart tool, supply the real editable SVG/PPTX and review its full final-platform preview. The wrapper checks native labels/linked chart values and re-renders with the recorded recipe to compare pixels; chart geometry and dataset truth still require actual review.

After exporting and inspecting the complete final-platform PNG and thumbnail, use the public core's scripts/publish_image.py with --source, --plan, --qa and --output-dir. Use its hash-bound QA record with the five additional business checks. Both output directories must be new. Render and inspect a first actual image before continuing a series.

Read the saved prompt and submit it to the runtime's image tool. The CLI only creates a plan. The optional upstream baoyu-infographic is not required for the included planner and is not installed automatically.

Rows may declare per-row units for mixed metrics; otherwise dataset.units applies. Preserve source scale (for example, a value expressed in tens of thousands must retain that unit). Chinese adjacency, decimals and thousands separators are supported; a bare-number excerpt is not meaningful context.

All visible labels participate in text routing. exact_text items need source matches or approved_external_text declarations containing text, approved_by, reason and user_quote; declared approvals still require review. Unknown brief fields are rejected.

Export the composite first with the core export_platform_image.py. Default contain preserves all content. Write review_stage=final-platform-image against the exported PNG, and editable_source evidence as documented in the core visual-qa.md. A background without the completed native text cannot pass delivery.

Before exporting any editable text/chart composite, follow the core editable-rendering.md reference: use render_editable.py with an installed CJK font, attach its render_receipt to QA and use platform-final.png as the reviewed source. Do not substitute a manually exported preview from another renderer.
