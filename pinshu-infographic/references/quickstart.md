# Quick start and brief

Install the complete repository bundle or place pinshu-infographic and the marked public pinshu-visual-system 0.2.1 or later in the same parent folder. Planning needs Python 3. Generation needs an image-capable agent; delivery needs ImageMagick 7. Do not replace a private installation with the public bundle.

From the repository root:

```bash
python3 pinshu-infographic/scripts/plan_infographic.py \
  --brief pinshu-infographic/examples/brief.json \
  --output-dir ./work/infographic-plan
```

Read the saved source, structured brief, plan and prompt. Submit the saved prompt to the runtime's image tool. The planner makes no API call. Add --candidate-test only for an explicitly requested single candidate image, or --character-profile with your own approved JSON for Character Presenter.

The brief names a source_file relative to the brief, claim, claim_source_excerpt, platform, structure, density, units and relations. Each unit has id, label and source_excerpt; each arrow has from, to, verb and source_excerpt. Excerpts must occur verbatim in the source. exact_text is a list of labels requiring exact preservation; use it for names, numbers, quotations and fixed terms. Ordinary summary labels still require semantic and visual review.

After composing the editable text layer, export the complete final image first:

```bash
python3 pinshu-visual-system/scripts/export_platform_image.py \
  --source ./work/composite.png --platform wechat-article \
  --output-dir ./work/platform-final
```

The default contain fit preserves content and pads. Select cover only for an explicitly intended crop; inspect the recorded crop fractions, final full image and thumbnail. Write hash-bound QA for platform-final/platform-export.png with review_stage=final-platform-image and the completed native-text SVG/PPTX evidence when required. Then prepare delivery:

```bash
python3 pinshu-visual-system/scripts/publish_image.py \
  --source ./work/platform-final/platform-export.png \
  --plan ./work/infographic-plan/route-plan.json \
  --qa ./work/visual-review.json \
  --output-dir ./work/infographic-delivery
```

The output directories must be new. Use the core's hash-bound QA format with the additional diagram checks. Inspect the exported thumbnail as well. A good script result does not approve source claims or aesthetics.

Unknown top-level fields are rejected. Timeline requests route to pinshu-business-graphics with mother=strategic-map and structure=timeline; these three infographic modes do not support timeline. All visible titles, unit labels and arrow verbs participate in text routing, including Chinese labels even when exact_text is empty.

Every exact_text item must occur in the source or have a declared real user approval: approved_external_text=[{"text":"Requested editorial heading","approved_by":"user","reason":"User requested this heading"}]. An approval is a declaration to review, not automatic factual verification. Do not invent approvals to bypass source checks.
