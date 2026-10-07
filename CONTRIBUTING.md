# Contributing

Keep changes scoped to the approved Skill package and shared installer/release files. Do not edit a user's active `~/.agents/skills` installation from this repository.

For code changes, add or update the smallest relevant tests and preserve existing behavior unless the change is explicitly approved. For documentation, keep Chinese operating rules and English implementation notes on the same workflow; do not create a weaker second pipeline.

Run at least:

```bash
python3 scripts/validate_release.py --quick
```

Run full installer tests before any release freeze:

```bash
bash tests/test_installer.sh
```
