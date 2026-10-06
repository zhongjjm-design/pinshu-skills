# Editable rendering and delivery

Use this path for every editable-text or precision-chart plan. Produce a self-contained SVG with native `text` elements, or an actual PPTX with native paragraphs/category charts. Embed supporting background images rather than referencing local or network files. Keep each required label in one complete text element/paragraph; a SVG title may use `tspan` line breaks inside that element. Do not hide required text or replace it with outlines. Inline presentation attributes are supported; SVG CSS style blocks, scripts and foreignObject are outside this renderer.

## Fonts and dependencies

SVG rendering uses ImageMagick 7's explicit MSVG backend and a readable font file. A CSS font-family list is not enough. On macOS, check for `/System/Library/Fonts/STHeiti Light.ttc` and use it explicitly when available; set the SVG family to `Heiti SC` and normal weight for that Light font. Do not claim a 600-weight PingFang layout was delivered with this font. Another installed CJK font is acceptable after inspecting its actual Chinese glyphs. On Linux, install `fonts-noto-cjk` and use an existing CJK font such as `/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc`; use the actual chosen family in the SVG. Other systems must supply their own readable licensed CJK font. Fonts are not bundled or copied for public distribution.

PPTX rendering additionally needs LibreOffice (`soffice`) and Poppler (`pdftoppm` and `pdfinfo`). On macOS, verify the LibreOffice CLI is on PATH; `brew install --cask libreoffice` and `brew install poppler` are possible manual setup steps. On Debian/Ubuntu, `libreoffice-impress`, `poppler-utils` and `fonts-noto-cjk` provide the needed tools. The package does not install them automatically on a user's machine. Set fonts inside the deck and ensure they are installed: `--font-file` fingerprints the selected font, and does not rewrite PPTX fonts. LibreOffice layout can differ from PowerPoint; review the actual PNG, not a screenshot from another renderer. The native chart reader currently supports linked category charts with cached category/value points, not all scatter, bubble or external-workbook forms.

## Render a final platform candidate

From the core Skill directory, with new output directories:

```bash
python3 scripts/render_editable.py \
  --source ./work/composite.svg \
  --font-file "/System/Library/Fonts/STHeiti Light.ttc" \
  --platform wechat-article --output-dir ./work/rendered
```

For PPTX, `--slide` always indexes the original presentation order, including hidden slides. PDF export explicitly includes hidden slides and checks that its page count equals the deck slide count. Rasterization preserves the slide aspect ratio; a 4:3 or portrait page is contained with padding instead of stretched to 16:9.

For PPTX use the same command with `--source ./work/chart.pptx --slide 1` and the actual installed font. The output is `platform-final.png` plus `render-receipt.json`. It defaults to contain; an intended cover crop needs explicit `--fit cover` and actual crop review. Inspect the complete final PNG and a platform/mobile preview before QA. Current receipts use `native-render-v2`; legacy v1 receipts must be rendered and reviewed again. The receipt records the native file hash, font hash, renderer versions, slide, platform, fit, gravity, background and final PNG hash. The same environment is needed for verification; a changed font or renderer requires a fresh render and review.

In the QA `editable_source`, include `path`, `sha256`, `rendered_image_sha256` and `render_receipt` (receipt path relative to the QA file, or absolute). Then run `publish_image.py` on this final PNG. Delivery re-renders the actual native source with the recorded recipe and requires zero pixel difference. Updating only hash declarations cannot approve an old image. The native file and receipt are copied with the metadata-clean PNG.

## Review all visible native text

Required labels are checked as whole text elements/paragraphs, not substrings of concatenated document text. Linked PPTX chart categories/values count as editable data on the selected slide; unrelated slides/charts do not satisfy this plan.

The wrapper also inventories plan-external native text. Complete original-source lines or sentences are recorded as literal text matches; fragments must be explicitly reviewed with their full source context. A literal match does not establish that a claim is true or that its use preserves meaning. Otherwise add `additional_text_review` entries with `text`, `origin` and `reason` to QA. Supported origins are `editorial-paraphrase`, `structural-label` and `dataset-value`; paraphrases additionally need a literal `source_excerpt`. Structural labels are nonnumeric headings of at most 40 characters, not a way to introduce factual claims. Dataset-value annotations must be numeric values from this plan, optionally followed by the declared unit; a dataset must exist. Numeric paraphrases must enter the plan as explicit source-reviewed labels, rather than as additional annotations. For example:

```json
{"additional_text_review": [{"text": "Direction and execution", "origin": "editorial-paraphrase", "source_excerpt": "Think through the first two layers before using AI for the lower layers.", "reason": "Reviewed grouping summary, not a quotation"}]}
```

Use a source excerpt actually present in your input; this example is not an approval for arbitrary wording. Any extra annotation, axis title or numeric label still needs source/QA review. A native-text inventory does not OCR words embedded in background pixels. Re-render identity establishes file-to-image correspondence, not semantic truth, chart proportions or aesthetic acceptance. Actual final-image review remains required.

## Percentage charts and visibility limits

Plan values use the expressed source unit: 30 with units `%` means 30 percent. A native PPTX chart may store 0.30 with an actual percent number format such as `0%`; delivery compares the displayed value, 30. A quoted or escaped percent suffix such as `0"%"` does not multiply by 100. An unlinked data-label format overrides the cache format. English `percent`/`percentage` aliases and fullwidth numeric characters are supported after literal source anchoring. Mixed/custom conditional formats, per-point format overrides and arbitrary unit conversion are outside the current chart adapter; inspect actual axis/data labels. Single-series chart names can become automatic titles in LibreOffice; explicitly remove unintended titles and inspect the exported PNG. Master/layout text and rasterized background words are not a complete native-text inventory.

SVG text checks reject effective opacity below 0.1, font sizes below 8 native units, labels with zero contribution to actual pixels, and rendered glyph bounds outside the original canvas. Each label is measured with the same MSVG backend and font on a padded canvas; masks use a 30-million-pixel limit. Use explicit numeric/px dimensions or a numeric viewBox. These checks catch common invisible/clipped labels; they do not prove mobile readability, sufficient contrast, partial occlusion or correct meaning. Inspect the final platform PNG and thumbnail. PPTX text visibility and clipping still require actual review.

For developer validation, install `python-pptx==1.0.2` in an isolated Python environment and run `tests/test_native_pptx_render.py`. Its actual LibreOffice render tests cover hidden first/middle/selected slides, 4:3/portrait/16:9 geometry and a native percentage chart. Set `PINSHU_REQUIRE_NATIVE_RENDER=1` to fail on missing integration dependencies; CI always requires them. This dependency creates test inputs, and is not needed to deliver an existing PPTX.
