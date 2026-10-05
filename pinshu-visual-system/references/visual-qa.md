# Visual review and delivery evidence

Actually view the generated image before writing a PASS. Check:

- source-faithfulness: the intended claim, real facts, proposed metaphor and source limits remain distinct;
- visible-text: names, numbers, labels and the requested language match the intended text;
- mode-and-composition: one relationship, one focal point, the complete chosen visual grammar and no generic template shell;
- identity-and-actions: actual loaded identity where required, natural object orientation, grasp, gaze, body and anatomical dominant hand; use pass for a genuinely character-free image after inspection;
- thumbnail-and-crop: the main anchor and reading order survive the thumbnail and the target crop.

Record notes with concrete observations; scores cannot override hard failures. Write a review record tied to both the exact bitmap and the saved plan:

```json
{
  "source_sha256": "HASH_OF_THE_RENDERED_IMAGE",
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

After export, inspect platform/preview-thumbnail-180.png and the center-square preview for a WeChat primary cover. Mechanical delivery remains a candidate until the user confirms its use. The pixel comparison applies between platform-export.png and its publish-clean copy, not between the raw generator image and the intentionally resized platform export.
