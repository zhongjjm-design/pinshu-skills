# Bring your own character

The default is no fixed character. No Pinshu, personal-photo or private mascot reference is bundled. Use only reference material the user has supplied and approved for the task.

Create a local JSON profile next to your own reference image:

```json
{
  "id": "team-editor",
  "status": "approved",
  "identity_asset": "identity.png",
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
