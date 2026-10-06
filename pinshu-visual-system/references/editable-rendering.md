# Editable rendering and delivery

Use this path for every editable-text or precision-chart plan. Produce a self-contained SVG with native `text` elements, or an actual PPTX with native paragraphs/category charts. Embed supporting background images rather than referencing local or network files. Keep each required label in one complete text element/paragraph; a SVG title may use `tspan` line breaks inside that element. Do not hide required text or replace it with outlines. Inline presentation attributes are supported; SVG CSS style blocks, scripts and foreignObject are outside this renderer.

## Fonts and dependencies

SVG rendering uses ImageMagick 7's explicit MSVG backend and a readable font file. A CSS font-family list is not enough. On macOS, check for `/System/Library/Fonts/STHeiti Light.ttc` and use it explicitly when available; set the SVG family to `Heiti SC` and normal weight for that Light font. Do not claim a 600-weight PingFang layout was delivered with this font. Another installed CJK font is acceptable after inspecting its actual Chinese glyphs. On Linux, install `fonts-noto-cjk` and use an existing CJK font such as `/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc`; use the actual chosen family in the SVG. Other systems must supply their own readable licensed CJK font. Fonts are not bundled or copied for public distribution.

PPTX rendering additionally needs LibreOffice (`soffice`) and Poppler (`pdftoppm`). On macOS, verify the LibreOffice CLI is on PATH; `brew install --cask libreoffice` and `brew install poppler` are possible manual setup steps. On Debian/Ubuntu, `libreoffice-impress`, `poppler-utils` and `fonts-noto-cjk` provide the needed tools. The package does not install them automatically on a user's machine. Set fonts inside the deck and ensure they are installed: `--font-file` fingerprints the selected font, and does not rewrite PPTX fonts. LibreOffice layout can differ from PowerPoint; review the actual PNG, not a screenshot from another renderer. The native chart reader currently supports linked category charts with cached category/value points, not all scatter, bubble or external-workbook forms.

## Render a final platform candidate

From the core Skill directory, with new output directories:

```bash
python3 scripts/render_editable.py \
  --source ./work/composite.svg \
  --font-file "/System/Library/Fonts/STHeiti Light.ttc" \
  --platform wechat-article --output-dir ./work/rendered
```

For PPTX use the same command with `--source ./work/chart.pptx --slide 1` and the actual installed font. The output is `platform-final.png` plus `render-receipt.json`. It defaults to contain; an intended cover crop needs explicit `--fit cover` and actual crop review. Inspect the complete final PNG and a platform/mobile preview before QA. The receipt records the native file hash, font hash, renderer versions, slide, platform, fit, gravity, background and final PNG hash. The same environment is needed for verification; a changed font or renderer requires a fresh render and review.

In the QA `editable_source`, include `path`, `sha256`, `rendered_image_sha256` and `render_receipt` (receipt path relative to the QA file, or absolute). Then run `publish_image.py` on this final PNG. Delivery re-renders the actual native source with the recorded recipe and requires zero pixel difference. Updating only hash declarations cannot approve an old image. The native file and receipt are copied with the metadata-clean PNG.

## Review all visible native text

Required labels are checked as whole text elements/paragraphs, not substrings of concatenated document text. Linked PPTX chart categories/values count as editable data on the selected slide; unrelated slides/charts do not satisfy this plan.

The wrapper also inventories plan-external native text. Literal original-source text is recorded as such. Otherwise add `additional_text_review` entries with `text`, `origin` and `reason` to QA. Supported origins are `editorial-paraphrase`, `structural-label` and `dataset-value`; paraphrases additionally need a literal `source_excerpt`. For example:

```json
{"additional_text_review": [{"text": "Direction and execution", "origin": "editorial-paraphrase", "source_excerpt": "Think through the first two layers before using AI for the lower layers.", "reason": "Reviewed grouping summary, not a quotation"}]}
```

Use a source excerpt actually present in your input; this example is not an approval for arbitrary wording. Any extra annotation, axis title or numeric label still needs source/QA review. A native-text inventory does not OCR words embedded in background pixels. Re-render identity establishes file-to-image correspondence, not semantic truth, chart proportions or aesthetic acceptance. Actual final-image review remains required.
