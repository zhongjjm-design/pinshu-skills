# Models and fallbacks

Use the configuration's model-routing fields and interfaces the user has lawfully configured. Model menus, IDs, quotas and prices change often; check the current provider documentation and the interface's real availability before each run. Examples are not rankings or proof that an interface is installed.

## The vendor rule

Every reviewing position should come from a provider other than the writer's when possible. Models from one provider can share mistakes, and a reviewer may favor text that resembles its own habits. Reviewing positions may share a provider with each other, but independence comes first from what each position receives (`5-review.md`). Give the editor and expert different providers when practical.

## Who does what

| Role | Choice | Boundary |
|---|---|---|
| Writer | The session that talks with the author, using the configured `writer` | One writer carries the author's words from step 1 through the last edit. If that session cannot write the article, use `writer_fallback` and record the actual writer |
| Research | Configured web-capable models, several bounded jobs when useful | Public material only; no private customer or financial inputs |
| Fact-sheet names | Any inexpensive model or the supplied extraction script | Lists names and claims; judges nothing |
| Editor | The strongest available writing model from another provider | Two fresh calls: pass one after the first draft, pass two after revision |
| Reader | A plain model from another provider | One fresh call per section; it receives no later sections |
| Expert | A web-capable model from another provider | Acts as a practitioner in the field named at step 1; every material finding has a source |
| Fact checker | A rigorous web-capable model willing to report “not found” | Pass one, pass two and the two re-checks; no finished result by the configured deadline is recorded as skipped and sent to the backup |
| Mechanical tasks | Supplied scripts or any inexpensive model | File handling, audits, formatting and collecting links |

## Configuration contract

The examples in `templates/config.example.yaml` describe roles, not guaranteed executable dispatchers. A blank entry does not silently waive a required role. Choose an authorized interface that meets the role's provider and capability requirements, probe it, and record the actual provider, model and channel used.

- `writer` is the author's configured or explicitly named choice.
- `writer_fallback` is used only when the primary writer cannot complete the article.
- `research` contains one or more authorized web-capable routes.
- `hook_second` must differ from the writer's provider when possible.
- `editor`, `reader`, `expert` and `fact_checker` retain the jobs and timing defined above.
- When a required provider or capability is unavailable, use the fallbacks below. Report the downgrade or skipped role at the next gate; never report a missing review as completed.

## Calling another provider

Use an official CLI, supported API or the current runtime's model dispatcher. Commands, model IDs, quotas, keys and machine-specific defaults belong in the user's configuration, not in this package. Each caller uses its own authorized access; do not borrow another application's credentials.

Send the complete brief inline instead of only a file path. Give each call only the material and role card it needs, starting with the delegated read-only line in `prompts.md`. Omit private author identity and preferences from blind reviewers. A fresh working folder does not by itself hide global rules, isolate credentials, prevent file access or create a sandbox; verify the interface's actual behavior. If global rules remain visible, record `global rules visible` rather than claim a blind run.

Probe an interface with a one-line request before the real call. A command on `PATH`, a menu entry, an empty successful exit, or a login/quota error is not proof that the model works. Move to a fallback if the probe fails. A successful short probe does not establish the duration or output limit of a full draft.

Watch command-line calls with `scripts/run_watched.py`. Keep completion notification connected to the session; do not detach a job and forget it. Typical `--check-after` values are about 1,500 seconds for a full draft or revision and 600 seconds for reviews. After that, allow a call whose output, watched files or process-tree CPU is still moving to finish; stop only one that stays silent for the configured window. `--deadline` is reserved for a role whose finished result becomes unusable after a fixed limit, such as the fact checker. Inspect the output and ending status rather than treating exit code 0 as proof of a complete answer.

### Portable example

Run `python3 scripts/run_watched.py --help` from the installed Skill folder first. With an existing brief and output folder, replace `MODEL_CLI` and its arguments with an authorized interface already configured on the machine:

```bash
BRIEF="$(python3 -c 'from pathlib import Path; print(Path("article/brief.md").read_text(encoding="utf-8"))')"
python3 scripts/run_watched.py \
  --out article/draft.md --check-after 1500 --silent 300 \
  -- MODEL_CLI "$BRIEF"
```

The wrapper runs the child in a fresh temporary working folder with stdin closed. Standard output goes to `--out`; standard error and the elapsed/end-status line go to `<out>.err`. Inputs that the child needs must be included in the brief or passed explicitly. This arrangement is not a security sandbox.

## Output-budget troubleshooting

Output limits and reasoning behavior differ by provider. Use settings supported by current provider documentation and record the actual provider, model, channel, brief, output and terminal status. Ask for conclusions and cited reasons, not hidden reasoning traces.

For empty or truncated output, inspect `<out>.err` and available provider diagnostics. Authentication failure, exhausted quota, silence and an output budget consumed before visible text require different fixes. Retry with supported settings or an authorized alternative route, keeping the failed attempt. An empty successful exit remains a failed result.

## Writer unavailable

Try an authorized alternative route to the same model, then a configured writer-grade model from another provider. Only if none works may the organizer draft, and that downgrade is recorded. Re-pair all reviewing providers against the model that actually wrote.

## Only one model available

If another provider is reachable, the organizer calls it and saves the report. Otherwise run each role in a fresh session with only that role's material and record `same-provider review` in the editor notes and next gate. This is a downgrade, not cross-provider validation. If even a fresh role session is unavailable, mark the review skipped and ask the author whether to continue. The author is never asked to carry text between models.