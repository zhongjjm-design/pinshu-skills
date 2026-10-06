# Third visual repair candidate: core 0.2.3, companions 0.1.3

The independent review of 471e5a5 reproduced wrong-slide delivery with hidden slides and stretched 4:3 slides. PPTX export now includes hidden slides, verifies PDF/deck page counts, uses original slide order and preserves aspect ratio before contain/explicit cover fitting. Native-render-v2 receipts replace v1; delivery still re-renders and requires identical reviewed pixels. Real python-pptx/LibreOffice integration tests cover these failures rather than relying on parser-only XML fixtures.

Unplanned structural labels cannot smuggle numeric claims; dataset annotations must match actual plan values. Source fragments require explicit context review rather than automatic substring approval. Semantic truth remains a review responsibility. SVG rendering now tests actual glyph bounds and pixel contribution, alongside minimum opacity/font-size controls. These are bounded mechanical checks, not full visibility or aesthetic acceptance.

Fullwidth numbers and percent words anchor correctly. Native PPTX percentage caches with percent formats compare displayed values; quoted/escaped suffixes are distinguished. Chart adapter boundaries, dependency setup and receipt migration are documented in editable-rendering.md.

This is a local engineering candidate. No human aesthetic acceptance, real colleague trial, five-image design series, unattended design batch or updated cloud CI result is claimed. Existing private installations remain separate; the experimental cultural-poster cards retain their review limits.
