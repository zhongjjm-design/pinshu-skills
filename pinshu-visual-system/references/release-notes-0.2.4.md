# Reviewed sharing preview: core 0.2.4, companions 0.1.4

The independent review of 6dcfde2 confirmed hidden-slide selection, page reordering, preserved geometry, native percentages and render binding. This update corrects an overbroad percent alias: English percentage points cannot anchor a percent value, while explicitly declared percentage-point units still work.

SVG text no longer fails merely because its unscaled font-size is below eight or uses pt. The same-renderer isolated glyph check applies an eight-pixel height floor at final platform scale, including viewBox scaling, group transforms and contain/cover fitting. Correct scaled/pt cases pass; the reproduced seven-pixel case stops. This is a bounded text-element glyph-height check, not complete readability detection.

Unplanned numeric claims expressed through Chinese multiples, tenths, percent-of and doubling cannot use structural-label or editorial-paraphrase declarations. Structural group headings remain allowed. Chinese agent/assistant approver names are rejected; true human identity and quotations still require review.

Existing accepted px SVG/PPTX rendering remains compatible with v2 receipts, and delivery re-renders under updated checks. Newly accepted absolute SVG font units are explicitly normalized to px before rendering; 42pt and 56px are checked for identical pixels. Weak contrast, partial occlusion, semantic truth, PPTX master/layout text and human aesthetic acceptance retain their stated limits. Existing samples retain design and font-style TODOs; no colleague trial, design series, unattended production or new cloud CI result is claimed.

The fourth independent review of code commit 1d41cc6 ran 153 probes, with 137 meeting expectations, and reported no publication blocker. This is separate from the author's 90 engineering checks and 20 targeted reproductions. Remaining issues include incomplete Chinese quantity detection, large SVG canvases hitting the mask limit and unsupported CSS font shorthand conversion. The editable-rendering guide documents the practical input restrictions; these issues are not claimed fixed.

Release scope is Agent-accompanied single-image trials with human review. Two local Chinese engineering mockups were not aesthetically accepted by the owner and are not approved design references or finished article illustrations. They are not included as public assets. Future style and format expansion follows the visual-evolution reference; no aesthetic acceptance or unattended batch readiness is implied by publication.
