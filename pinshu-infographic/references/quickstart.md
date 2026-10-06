# Quick start and brief

Install the complete repository bundle or place pinshu-infographic and the marked public pinshu-visual-system 0.2.0 or later in the same parent folder. Planning needs Python 3. Generation needs an image-capable agent; delivery needs ImageMagick 7. Do not replace a private installation with the public bundle.

From the repository root:

```bash
python3 pinshu-infographic/scripts/plan_infographic.py \
  --brief pinshu-infographic/examples/brief.json \
  --output-dir ./work/infographic-plan
```

Read the saved source, structured brief, plan and prompt. Submit the saved prompt to the runtime's image tool. The planner makes no API call. Add --candidate-test only for an explicitly requested single candidate image, or --character-profile with your own approved JSON for Character Presenter.

The brief names a source_file relative to the brief, claim, claim_source_excerpt, platform, structure, density, units and relationships. Each unit has id, label and source_excerpt; each arrow has from, to, verb and source_excerpt. Excerpts must occur verbatim in the source. exact_text is a list of labels requiring exact preservation; use it for names, numbers, quotations and fixed terms. Ordinary summary labels still require semantic and visual review.

After rendering and completing actual review, including any editable text layer:

```bash
python3 pinshu-visual-system/scripts/publish_image.py \
  --source ./work/rendered.png \
  --plan ./work/infographic-plan/route-plan.json \
  --qa ./work/visual-review.json \
  --output-dir ./work/infographic-delivery
```

The output directories must be new. Use the core's hash-bound QA format with the additional diagram checks. Inspect the exported thumbnail as well. A good script result does not approve source claims or aesthetics.
