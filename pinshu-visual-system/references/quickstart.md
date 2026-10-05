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

With a real generated image and completed visual review:

```bash
python3 scripts/publish_image.py \
  --source ./work/rendered.png \
  --plan ./work/draft-review/route-plan.json \
  --qa ./work/visual-review.json \
  --output-dir ./work/delivery
```

Planning needs Python 3. Export needs ImageMagick 7. macOS users can install it with `brew install imagemagick`; on other systems use the official ImageMagick 7 installation for that system and verify `magick -version`. The package never installs tools or starts billing automatically.

Run meaningful local checks:

```bash
python3 -m unittest discover -s tests -v
```

The shared package has a separate VERSION (0.1.0) from its internal ancestor. Existing private installations must not be replaced with it; the repository installer deliberately refuses that collision. On a clean colleague machine, the repository installer adds the visual Skill alongside the seven course/content Skills. Restart the client afterward and verify it can discover the Skill and access an image backend.
