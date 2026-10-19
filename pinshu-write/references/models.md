# Models and fallbacks

Use the configuration's `models` block and the models actually available to the installer. Check current model menus, access, costs and terms; provider examples are not a quality ranking or a guarantee that a command is installed.

## The vendor rule

The picked writer's vendor differs from every reviewing role's. Reviewing roles may share a vendor with each other. Multiple agents of one model agreeing is not cross-vendor validation.

## Who does what

| Role | Choice | Boundary |
|---|---|---|
| Organizer | Main conversation | Runs the route, keeps evidence and decisions, merges findings; does not silently substitute itself as writer |
| Scan and research | Configured models with web access | Public material only; no private customer or financial inputs |
| Writer | Configured writer selected by the author | One writer by default; second writer only on request |
| Counter | Another vendor | Tests the opposing argument |
| Structure editor | Another vendor | Checks the line before stop 2 |
| Managing editor (two) | Two configured vendors other than the writer's | Same prompt 10, independently; no author identity or preferences |
| Reader | Another vendor or an available human reader | Reads in the target reader's context |
| Attraction reader | Another vendor | Title, opening, reading and sharing appeal; advice only |
| Originality check | Another vendor | Compare against an outside article used as a seed |
| Expert | Another vendor with relevant subject capability | Correctness and limits |
| Facts and risk | Another vendor with web/source access | Check hard claims against sources |
| Language and flow | Another vendor | Diagnose wording, then read flow in a separate call |
| Good-article check | Another vendor | Account-specific standard |
| After-revision read | Another vendor | Read the revised body alone |
| Seed check | Another vendor able to read the whole input | Verbatim seed, point map, decisions, key words |
| Mechanical tasks | Local scripts | No model required |

### Configuration defaults and conditional roles

The `models` entries in `templates/config.example.yaml` are routing instructions for the organizer, not an executable dispatcher schema. An empty or omitted entry does not disable a required role: choose an available, authorized interface that meets the table's vendor and capability requirements, probe it, and record the actual selection. Do not infer a model ID, installed command or authorization from an example name.

- `organizer` defaults to the main conversation. `writer` is the author's configured or explicitly named choice; if neither is known, ask for the choice at stop 2. `research` uses available authorized web-capable interfaces; without web access, follow the library/source fallbacks in `1-topic.md` and `2-research-and-counter.md`.
- `counter`, `structure_editor`, `managing_editor`, `reader`, `attraction`, `expert`, `facts_risk`, `language`, `after_revision` and `seed_check` retain their jobs and timing above. Several jobs may use the same eligible model in separate calls, but the two managing editors use two vendors other than the writer's. `language` still runs wording and flow as separate calls; `after_revision` receives only the revised body.
- `second_writer` runs only when the author requests two drafts. The second vendor for hook candidates (prompt 15) is still needed even with one drafting writer; select it from available authorized interfaces if this entry is empty.
- `originality` runs when someone else's article is the seed; otherwise record it as not applicable. An empty model entry does not waive a triggered originality check.
- `good_article` runs when the selected account supplies a readable `good_article_standard`; otherwise record "no account standard; good-article check not run", without inventing a standard or marking it passed. If a configured standard cannot be read, ask for it or record the missing asset and the author's decision before proceeding.
- When the required vendor or capability is unavailable, use the quota and one-model fallbacks below. Report the downgrade or skipped role at the next stop, never a completed review. These are organizer decisions; no parser or schema change is required.

## The author names the writer

Any model the author explicitly names writes, including the main conversation. Record the actual writer; retain all reviews and re-pair the reviewing vendors. A named writer replaces the second-writer arrangement unless the author asks for two. Follow the normal stops unless the author explicitly waives a choice.

## Calling another vendor

Use an interface the installer has lawfully configured: an official CLI, supported API, or the current runtime's model dispatcher. Commands, channels, model IDs, quotas and keys belong in the installer's own configuration, never in this package. Each caller uses its own authorized access. Do not borrow another application's credentials or promise that a working directory hides global rules.

Send the full brief inline rather than only a path. Give each call only the material and role card it needs, with a first line explaining that it is a delegated read-only review (`prompts.md`, "Every brief"). Omit private author identity and preferences from blind reviewers. Verify the interface's real isolation behavior; when global rules remain visible, record "global rules visible" rather than claim a blind run.

Probe a configured interface with a one-line request before the real call. A command on PATH, a menu entry, an empty successful exit or a login/quota error is not proof the model works. Move to a fallback if the probe fails. A successful short probe does not establish the duration of a full draft.

Watch real command calls with `scripts/run_watched.py`. Keep completion notification connected to the session; do not detach a job and forget it. Reference `--check-after`: about 25 minutes for drafts and revisions, 10 for short reviews; after that allow a moving call to finish and end only one silent for about five minutes. Tune CPU/activity thresholds for the interface. `--answer-idle 90` is an optional adapter for a command that keeps running after its answer. Diagnose empty output from available diagnostics; distinguish quota, authentication, output ceiling and silence. Check that no called model is left running before reporting the stage complete.

### Watching a call

Run `python3 scripts/run_watched.py --help` from the installed Skill folder to check the supported parameters. For example, with an existing `article/brief.md`, an existing writable `article/` output folder and `CLAUDE_MODEL` set to a model ID supported by your authorized Claude Code installation:

```bash
BRIEF="$(python3 -c 'from pathlib import Path; print(Path("article/brief.md").read_text(encoding="utf-8"))')"
python3 scripts/run_watched.py \
  --out article/draft.md --check-after 1500 --silent 300 \
  --watch-claude-log \
  -- claude -p "$BRIEF" --model "$CLAUDE_MODEL"
```

The shell reads the brief before the wrapper starts the command. The wrapper resolves `--out` before launching the child in a fresh temporary working folder with stdin closed; stdout goes to that output file, stderr and the elapsed/end-status line to `<out>.err`, and the wrapper also prints that status line. Supply other needed inputs inline or by explicit absolute paths. `--watch-claude-log` watches Claude Code's session-log directories derived from the temporary working folder; it is Claude-specific, not a generic log adapter. Other interfaces may use repeatable `--watch <file-or-folder>` paths. This working-folder arrangement does not sandbox the command, hide global rules, isolate credentials or prevent network/file access; verify the interface's actual behavior before claiming a blind review.

The default check delay is 600 seconds, silence window 300 seconds and polling interval 5 seconds. The wrapper normally returns the command's exit code; stopping a silent call returns 124. `--answer-idle` defaults to 0 (off); enabling it can stop a non-empty unchanged answer and return 0, so inspect the ending status and the output rather than treating exit 0 as proof of a complete answer. The example omits that early-stop adapter.

### Provider-specific output-budget troubleshooting

Output limits and reasoning behavior differ by provider. Choose supported settings from that provider's current documentation. Record the actual provider/model/channel, the brief, output and terminal status. Ask for conclusions and cited reasons, not hidden reasoning traces. Paid calls require the author's cost authorization.

For empty or truncated text, read `<out>.err` and the provider's session diagnostics first. Authentication, exhausted quota, a silent process and an output/reasoning budget exhausted before visible text require different fixes. In a Claude Code installation that supports `CLAUDE_CODE_MAX_OUTPUT_TOKENS`, check its effective value and the selected model's supported ceiling; do not assume a fixed value such as 64,000 is supported by every model or interface. Check reasoning settings only through that provider's documented controls. Do not pass Claude-specific environment variables to unrelated providers or lower reasoning indiscriminately. Retry with supported settings or an authorized alternative channel, keep the failed attempt, and record the change; an empty successful exit remains a failed draft.

## Writer out of quota

Try an authorized alternative entry to the same model, then a configured writer-grade model of another vendor, then the one writer that answered. Only if none works may the organizer draft. Record the downgrade and pair reviewers against the actual writer.

## Only one model available

If another vendor is reachable, the organizer calls it and saves its report. Otherwise use a fresh isolated role session and record "same-vendor review" in the editor notes and next stop; this is a downgrade, not cross-vendor PASS. If a fresh session is unavailable, mark that review skipped and ask the author whether to continue. With no writer model, the organizer writes and records it. The author is never asked to carry text between models.
