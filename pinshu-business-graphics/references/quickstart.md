# Quick start and brief

Install this package with the marked public pinshu-visual-system 0.2.0 or later in the same parent directory. Planning uses Python 3. Rendering needs an image-capable agent; raster delivery needs ImageMagick 7. No model subscription or charting backend is included.

From the repository root:

```bash
python3 pinshu-business-graphics/scripts/plan_business_graphic.py \
  --brief pinshu-business-graphics/examples/brief.json \
  --output-dir ./work/business-plan
```

The brief names source_file, claim, claim_source_excerpt, mother, platform, structure, units and relations. A unit has id, label and source_excerpt. An arrow has from, to, verb and source_excerpt. Excerpts must occur verbatim in the source. The seven mother IDs correspond to this package's seven method cards.

metaphor has description and status: none, proposed or source-literal. A literal metaphor also needs a matching source_excerpt. delivery_medium is raster-concept or editable-required. exact_text lists immutable names, terms, numbers or quotes. Multiple or long labels route to an editable layer. output_language follows the user's requested language.

For a data graphic, dataset has rows, source, period, units, methodology, verified_by and status=verified. Each row has label, value and source_excerpt. Numeric provenance is mechanically checked, but the declared verifier and source reliability still need actual review. Data Journalism forces an editable chart final even when a raster concept was requested. Its raster wrapper is blocked; use an actual chart tool and deliver its editable file and checked export.

For an inspected non-data raster candidate, use the public core's scripts/publish_image.py with --source, --plan, --qa and --output-dir. Use its hash-bound QA record with the five additional business checks. Both output directories must be new. Render and inspect a first actual image before continuing a series.

Read the saved prompt and submit it to the runtime's image tool. The CLI only creates a plan. The optional upstream baoyu-infographic is not required for the included planner and is not installed automatically.
