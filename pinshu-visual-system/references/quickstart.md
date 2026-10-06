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

Compose any required native text first. Export the composite before writing final QA:

```bash
python3 scripts/export_platform_image.py \
  --source ./work/composite.png --platform wechat-article \
  --output-dir ./work/platform-final
```

Inspect that final image and thumbnail, then write review_stage=final-platform-image and its exact hash. With this completed review:

```bash
python3 scripts/publish_image.py \
  --source ./work/platform-final/platform-export.png \
  --plan ./work/draft-review/route-plan.json \
  --qa ./work/visual-review.json \
  --output-dir ./work/delivery
```

Planning needs Python 3. Export needs ImageMagick 7. macOS users can install it with `brew install imagemagick`; on other systems use the official ImageMagick 7 installation for that system and verify `magick -version`. The package never installs tools or starts billing automatically.

Run meaningful local checks:

```bash
python3 -m unittest discover -s tests -v
```

The shared package has a separate VERSION (0.2.1) from its internal ancestor. Existing private installations must not be replaced with it; the repository installer deliberately refuses that collision. On a clean colleague machine, the repository installer adds the visual Skill with both visual companions and the other suite packages. Restart the client afterward and verify it can discover the Skill and access an image backend.

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

Source-external exact labels need --approved-text-file pointing to a JSON list of text, approved_by and reason declarations. Preserve actual user authorization; do not fabricate it. The default contain export preserves content; an explicit cover crop reports edge loss and requires inspection before QA.
