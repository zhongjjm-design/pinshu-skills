# Assurance Modes and Evidence Budgets

Purpose: every course uses the same quality floor and the same four core results. Only evidence density, independent-QA sampling, and budgets vary by risk and use. `fast | standard | strict` remain internal manifest values for compatibility; they do not mean low-, medium-, and high-quality deliverables.

## 1. Three assurance modes

### `fast`: lightweight evidence

Use when sources are clear, content is text-based, the lesson presents ordinary viewpoints, or the user wants readable assets quickly.

- Generate the final faithful edit and structured lecture in one pass.
- Check people, numbers, key cases, methods, constraints, and opening/middle/ending anchors.
- Run full QA on the sample lesson. In a batch, run full QA on at least one in every five lessons and automatically route anomalous lessons to full QA.
- Ordinary lessons do not require block-by-block coverage or a second full read.
- Allow at most one targeted rework pass for ordinary issues.

Recommended budget per lesson: up to 300,000 tokens, 20 wall-clock minutes, one rework, and two QA decisions. When a platform does not report tokens, enforce at least wall-clock and agent-call budgets.

### `standard`: standard evidence

Use for professional learning courses that are long or terminology-dense but have complete sources and no high-risk procedures.

- Run full QA on the sample lesson.
- Run full independent QA on every critical lesson and every lesson selected by a risk trigger.
- Use stable sampling for ordinary lessons, targeting about 50% full independent QA.
- Check every number, proper noun, key case, constraint, and high-risk passage.
- If a systemic deviation appears, stop scaling and fix the system rather than repeating lesson-level repairs.

Recommended budget per lesson: up to 800,000 tokens, 60 wall-clock minutes, one rework, and two QA decisions.

### `strict`: full evidence

Use when sources are disordered; cases or real high-risk operations are dense; broad omissions or fabrication have already been found; or the user explicitly requires block-level evidence. Formal external use still goes through the shared external-use gate, which is independent of assurance mode.

- Produce block-by-block coverage for every lesson.
- Run full independent QA on every lesson.
- Still allow only one rework and one targeted recheck.
- Strict does not mean an unlimited loop.

Recommended budget per lesson: up to 1,500,000 tokens, 120 wall-clock minutes, one rework, and two QA decisions.

## 2. Selection rules

- Clear-source, low-consequence lessons may use `fast`.
- Professional courses default to `standard`; escalate individual lessons containing critical procedures, contraindications or doses, complex reasoning chains, or module summaries.
- Use `strict` only when the actual content has high-risk judgments, source ambiguity, severe STT errors, real operational consequences, or a block-level evidence requirement.
- Formal external use must pass the external-use gate; a mode name cannot replace factual, compliance, copyright, or privacy review.
- The user may override a mode explicitly. Record a reason for every escalation or reduction. No mode may omit substantive prose, cases, reasoning, or constraints.

## 3. Hard sample gate

For batches larger than three lessons:

1. Complete only one representative lesson in its final form.
2. Have the user approve detail level, layout, reading experience, and asset scope.
3. Record the approved sample in state with `approve-sample`.
4. Only then allow later lessons to enter `DRAFTED`.

A machine PASS or agent self-assessment cannot replace user approval.

## 4. QA convergence

- Only `high` can trigger `FIX_REQUIRED`.
- Deliver `note` items with the artifact; do not rework them.
- The first QA round may discover issues. The second round checks only previously identified issues.
- If a `high` remains after one rework, allow one strong-model adjudication or stop the line.
- Never start a third stylistic rework round.

## 5. Lean inputs

Every worker must still read the complete core quality contract. QA must also read the semantic-QA contract. To avoid repeatedly loading the whole Skill and unrelated references, an ordinary batch worker reads only:

1. the core quality contract;
2. the current lesson source;
3. the user-approved sample;
4. the current assurance-mode production card;
5. the lesson work package; and
6. any terminology list required for the current task.

A QA task also reads the semantic-QA contract. The production card must record the full contract version or hash, but a hash never replaces the contract text. Load the complete Skill and additional references only for the sample lesson, `strict`, source ambiguity, or disputed adjudication. The orchestrator must never improvise a compressed version of the quality floor.

## 6. Stop conditions

Stop the line and report immediately when any condition applies:

- token, wall-clock, QA-round, or rework budget is exhausted;
- the user has not approved the sample;
- two consecutive lessons show the same `high` issue;
- source identity or lesson number conflicts;
- concurrent official writes or state overwrites appear.

Stopping is not failure. Deliver completed assets, actual state, and the smallest clear blocker. Never rerun an artifact that already exists automatically.
