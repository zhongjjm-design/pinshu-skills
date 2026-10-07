# Publishing Candidate Rules

This repository is a unified candidate, not a formal public release.

Before freezing a version:

1. Update `approved-members.json` outside this repository and keep the package roster in `install.sh`, `scripts/validate_release.py`, `pinshu-manifest.yaml`, README tables and installer tests identical.
2. Run the release validator, installer lifecycle tests, package self-tests, `git diff --check`, and a current secret/path scan.
3. Record skipped tests as `SKIP`, not `PASS`, with the missing dependency.
4. Do not publish private account profiles, local course material, real credentials, source snapshots, personal paths or machine-specific defaults.
5. Do not claim a license, tag, CI result or final release state that has not been granted and verified.

Adding a new Skill requires an explicit business approval, source/provenance review, dependency boundary, installer test coverage and a short Chinese public entry rule in `SKILL.md`.
