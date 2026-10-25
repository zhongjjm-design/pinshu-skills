# Bring your own character

The default is no fixed character. No Pinshu, personal-photo or private mascot reference is bundled. Use only reference material the user has supplied and approved for the task.

Create a local JSON profile next to your own reference image:

```json
{
  "id": "team-editor",
  "status": "approved",
  "identity_asset": "identity.png",
  "identity_sha256": "<SHA256 of the actual approved image>",
  "approval_quote": "<actual user authorization from this task>",
  "tested_modes": ["warm-studio-illustration"],
  "dominant_hand": "right",
  "constraints": [
    "Preserve the supplied face, hairstyle, clothing and proportions.",
    "Use a natural working action rather than a standing presentation pose."
  ]
}
```

Relative assets resolve against the profile directory. The compiler checks file existence and records a hash; the rendering agent must actually load the image. Profile approval is a user's real decision, not a flag the agent may set automatically. Add a mode to tested_modes only after a real sample pairing has been reviewed. Warm Paper always refuses fixed characters. Character Presenter requires an approved pairing for that exact mode.

First test a new identity across the required expressions and actions. Identity approval does not approve every visual mode. Check anatomical handedness, build, clothing and action causality in every image. Keep character profiles and sample approvals local unless their owner explicitly chooses to share them.

For 1.0 candidates, bind the actual approved identity with identity_sha256 and preserve the real user approval in approval_quote. The executing agent verifies that approval against the user conversation; a JSON status is a declaration, not independent authorization. Replacing the identity invalidates the hash and requires renewed approval. No private identity database is shipped.

For authorization covering the complete profile, the executing agent matches the compiler-recorded profile_sha256 to the profile approved in the current task, including tested_modes, constraints and handedness. Keep that approval reference in the task record; changing those fields requires checking the approval again. Compiler hashes detect bytes, not human consent.
