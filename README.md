# Pinshu Skills

Aidan (Pinshu) maintains this suite of skills for professional course production and transcript editing. It works with Claude Code and other compatible agents.

## Quick install

```bash
curl -fsSL https://raw.githubusercontent.com/zhongjjm-design/pinshu-skills/main/install.sh | bash
```

Restart your Agent client after installation.

## Get started

Tell your Agent:

```text
Use pinshu-course-capture to process this course. First assess the course content and my goals, then recommend its intended uses, assurance level, and final assets. Wait for me to approve the production agreement before you begin.
```

Before production starts, the workflow confirms the course purpose, any external-use requirements, the assurance level, the final assets, and the sample gate. This prevents every course from being forced through the same process.

## Core course-asset pipeline

```text
pinshu-course-capture → source capture and production orchestration
pinshu-transcript     → faithful edited transcript
pinshu-distill        → structured study guide
pinshu-study          → active recall, guided study, follow-up questions, and learning records
pinshu-course         → series orchestration, checkpoints, cross-lesson leads, independent QA, and promotion
```

The faithful edited transcript is the source of truth for every downstream learning asset. A structured study guide may reorganize the material, but it never replaces the faithful transcript. Markdown remains the canonical source for learning activities; a web interface is optional.

## Default deliverables for professional-learning courses

Each processed lesson produces:

1. A faithful edited transcript;
2. A structured study guide;
3. Candidate active-recall cards;
4. Status, links, and a concise knowledge summary in the course map.

Learning activities are not pre-generated as a static exam bank. `pinshu-study` starts guided study, recall, follow-up questions, error diagnosis, source review, retries, and learning records only after the user explicitly asks to study, practice, review, or retest. It never invents mastery without a real response, but the absence of a response does not block production of candidate recall cards.

Historical pilots in this repository document the origin of rules and lessons from past failures. They are not production gates for new courses.

## Language and runtime-path contract

Repository instructions remain in English. Learner-facing output follows `output_language` in the production manifest: a short BCP-47 tag such as `en`, `en-US`, or `zh-Hans`, or the selector `match-user` or `match-source`. Old manifests that omit the field behave as `match-user`; when the user's language is unavailable, use the source language. Stable IDs, frontmatter keys, enum values, and other program fields remain English.

When a course-capture manifest or state file exists, every Skill uses its path templates through `course_pipeline.py paths`; no Skill translates or invents a parallel directory tree. For a new course without a manifest, create and confirm the manifest or an explicit path map before writing.

`pinshu-data-cleaning` is an optional upstream capability and is not included in this six-package repository or installed by its installer. If it is unavailable, provide pre-cleaned Markdown or a transcript, or use only the clean-text inputs supported by the selected Skill. The workflow must not silently skip heterogeneous-source cleaning.

## Set the purpose before choosing assurance depth

Before work begins, `pinshu-course-capture` creates a production agreement that can be saved, displayed, and audited:

- Purposes may be combined: reference, systematic study, training or exam preparation, method transfer, and content reuse;
- Publication, public release, client delivery, academic use, and real-world decisions trigger a separate external-use review;
- Assurance uses one of three evidence levels—lightweight, standard, or complete—recommended from the source, risk, and intended use. Runtime manifests retain `fast | standard | strict` for compatibility with existing projects;
- Every lesson retains the source transcript, faithful edited transcript, structured study guide, and course map. Assurance level never removes these core assets;
- Active-recall cards, training banks, cross-cutting topics, and external verification are enabled by purpose. Learning records are created only after learning actually occurs.

For batches larger than three lessons, deliver one representative lesson first. Scale production only after the user approves its depth, format, and reading experience. Only high-severity findings trigger rework. Each lesson also has token, wall-clock, QA, and rework budgets; production stops and reports its state when a budget is exhausted.

## Included skills

| Skill | Purpose |
|---|---|
| `pinshu-transcript` | Turn raw transcripts into faithful edited transcripts while preserving substantive meaning and source boundaries |
| `pinshu-distill` | Produce clear, self-contained structured study guides and approved cross-cutting topics from faithful transcripts |
| `pinshu-study` | Run stage-appropriate guided study, active recall, follow-up questions, error diagnosis, source review, and retesting, then save Markdown learning records |
| `pinshu-course` | Orchestrate multi-lesson courses, manage progress and checkpoints, track cross-lesson leads, run independent QA, and promote accepted assets |
| `pinshu-md2pdf` | Convert Markdown into a professionally typeset PDF |
| `pinshu-course-capture` | Capture source material from supported course video or transcript platforms and route it into the production pipeline |

## Quality boundaries

- Spoken course content is not automatically equivalent to a textbook, regulation, industry standard, or objective fact. Preserve source identity and distinguish instructor claims, editorial organization, external verification, and unresolved items.
- For professional judgment, regulated domains, high-risk operations, or real-world use, do not elevate course claims into universal advice. Preserve applicability, limitations, and required safety boundaries.
- Creator self-review, file existence, and a script-level PASS never replace independent semantic QA.
- Active-recall assets distinguish atomic cards from synthesis cards. Cross-lesson leads distinguish candidates, future pointers, verified findings, and safety-governance items.
- The public repository excludes local course materials, personal learning records, and photographs of real people.

## Local validation

```bash
python3 scripts/validate_release.py
```

Aidan (Pinshu) created and maintains this repository. It does not grant general open-source redistribution rights. Contact the maintainer before modifying, redistributing, or incorporating its contents into another product.
