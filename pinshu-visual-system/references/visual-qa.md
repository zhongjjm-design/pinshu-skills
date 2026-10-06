# Visual review and delivery evidence

Actually view the generated image before writing a PASS. Check:

- source-faithfulness: the intended claim, real facts, proposed metaphor and source limits remain distinct;
- visible-text: names, numbers, labels and the requested language match the intended text;
- mode-and-composition: one relationship, one focal point, the complete chosen visual grammar and no generic template shell;
- identity-and-actions: actual loaded identity where required, natural object orientation, grasp, gaze, body and anatomical dominant hand; use pass for a genuinely character-free image after inspection;
- thumbnail-and-crop: the main anchor and reading order survive the thumbnail and the target crop.

Record notes with concrete observations; scores cannot override hard failures. Write a review record tied to both the exact final-platform bitmap and the saved plan:

```json
{
  "review_stage": "final-platform-image",
  "source_sha256": "HASH_OF_THE_FINAL_PLATFORM_IMAGE",
  "plan_sha256": "HASH_OF_ROUTE_PLAN_JSON",
  "reviewer": "reviewing agent or person",
  "checks": {
    "source-faithfulness": "pass",
    "visible-text": "pass",
    "mode-and-composition": "pass",
    "identity-and-actions": "pass",
    "thumbnail-and-crop": "pass"
  },
  "notes": "Concrete observations from actually viewing the image."
}
```

Compute hashes with Python hashlib.sha256(path.read_bytes()).hexdigest(). Never copy a review from a different image or fill the checks without inspecting it. The preparation script verifies the declared checks and hashes; it does not perform the image review itself.

Before final QA, export the complete composition and inspect its preview-thumbnail-180.png and the center-square preview for a WeChat primary cover. Mechanical delivery remains a candidate until the user confirms its use. Delivery accepts only the already reviewed platform-sized PNG; it verifies zero pixel difference during packaging and metadata cleaning. A raw generator image at another size must be exported and reviewed first.

## Specialized plans

The five core checks always remain mandatory. For a companion or method plan, also record:

- pinshu-infographic: information-relationships, density-and-reading, text-delivery;
- pinshu-business-graphics: mother-integrity, metaphor-source-fit, data-accuracy, series-consistency, text-delivery;
- pinshu-visual-method-test: method-grammar, cultural-source-fit.

A genuinely non-applicable check may pass only with an explicit observation explaining why (for example, no dataset or no series). Editable-layer work needs evidence of a completed text layer. A single raster is never an editable chart final; those plans must finish in the chart tool. The wrapper verifies required workflow checks from its own contract, rather than trusting an editable required_checks list in the plan.

## Editable-source evidence

When text_route=editable-text-layer or an editable chart is required, add this to QA:

```json
{
  "editable_source": {
    "path": "final.svg",
    "sha256": "HASH_OF_NATIVE_SVG_OR_PPTX",
    "rendered_image_sha256": "HASH_OF_THE_FINAL_PLATFORM_IMAGE",
    "render_receipt": "rendered/render-receipt.json"
  }
}
```

Use native SVG text or native PowerPoint text; embed SVG image assets. Raster-only/PDF sources, missing files, changed files, absent labels or a mismatched bitmap are rejected. Native data-chart labels and numbers are also checked. These checks establish an artifact contract, not truth, correct chart geometry or honest review: inspect the actual native source and its complete rendered preview.

If packaging fails, delivery-report.json says FAIL and all sub-step artifacts remain intermediates. Only a successful top-level delivery report lists usable candidate artifacts; a platform sub-step PASS cannot approve a failed delivery. Human acceptance stays pending.

Native delivery now requires editable_source.render_receipt. Follow [editable rendering](editable-rendering.md); the wrapper re-renders and compares pixels, matches whole labels, and inventories additional native text through additional_text_review. Previous file/hash-only receipts are not sufficient.
