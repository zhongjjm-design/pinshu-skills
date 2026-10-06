# Fourth visual repair candidate: core 0.2.4, companions 0.1.4

The independent review of 6dcfde2 confirmed hidden-slide selection, page reordering, preserved geometry, native percentages and render binding. This update corrects an overbroad percent alias: English percentage points cannot anchor a percent value, while explicitly declared percentage-point units still work.

SVG text no longer fails merely because its unscaled font-size is below eight or uses pt. The same-renderer isolated glyph check applies an eight-pixel height floor at final platform scale, including viewBox scaling, group transforms and contain/cover fitting. Correct scaled/pt cases pass; the reproduced seven-pixel case stops. This is a bounded text-element glyph-height check, not complete readability detection.

Unplanned numeric claims expressed through Chinese multiples, tenths, percent-of and doubling cannot use structural-label or editorial-paraphrase declarations. Structural group headings remain allowed. Chinese agent/assistant approver names are rejected; true human identity and quotations still require review.

Existing accepted px SVG/PPTX rendering remains compatible with v2 receipts, and delivery re-renders under updated checks. Newly accepted absolute SVG font units are explicitly normalized to px before rendering; 42pt and 56px are checked for identical pixels. Weak contrast, partial occlusion, semantic truth, PPTX master/layout text and human aesthetic acceptance retain their stated limits. Existing samples retain design and font-style TODOs; no colleague trial, design series, unattended production or new cloud CI result is claimed.
