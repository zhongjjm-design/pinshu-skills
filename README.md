# Pinshu Skills

Aidan (Pinshu) maintains this suite of eight skills for faithful transcript editing, course production, learning, and reusable content assets. It works with Claude Code and other compatible agents.

## Quick install

On macOS or Linux (including WSL), have Bash, Git, `rsync`, and Python 3 available. The same command installs all eight skills on a fresh computer or upgrades an older Pinshu installation. Before replacing an existing, correctly named Pinshu Skill, the installer moves the complete old directory and any previous repository clone to recoverable backups; unrelated or unsafe paths are refused. Inspect the installer before executing a remote script on your computer.

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

If you already have a faithful edited transcript and a structured study guide, start the reusable-content workflow directly:

```text
Use pinshu-content-assets to turn this lesson into one readable, source-traceable content master. Preserve the speaker's main argument and every useful method, case, figure, and expression. Mark missing evidence and quotations accurately. Do not write an article; leave the master pending my review.
```

## Visual assets for colleagues

The new [Pinshu Visual System](pinshu-visual-system/README.md) is a public preview (0.1.0) for article illustrations, covers, social cards and presentation visuals. It shares twelve explicitly scoped mode cards, seven business-visual method families, eleven platform presets, prompt planning, exact-size export and review checks. Work without a fixed character or supply your own approved references. Planning is usable with Python 3; rendering needs an image-capable agent, and export needs ImageMagick 7.

Tell your Agent:

> Use pinshu-visual-system to illustrate this article for WeChat. Read the source, recommend a coherent style, generate and inspect one first image, then prepare the reviewed platform-sized candidate. Use no fixed character.

This is a usable initial sharing edition, with candidates and limitations clearly marked. We will keep improving it through the repository. It makes no claim of fully stable automatic batch generation. An existing private/local visual-system installation is protected from replacement by the installer.

## Core course-asset pipeline

```text
pinshu-course-capture → source capture and production orchestration
pinshu-transcript     → faithful edited transcript
pinshu-distill        → structured study guide
pinshu-content-assets → reusable content master from the approved edited transcript and guide
pinshu-study          → active recall, guided study, follow-up questions, and learning records
pinshu-course         → series orchestration, checkpoints, cross-lesson leads, independent QA, and promotion
```

The faithful edited transcript is the source of truth for downstream learning and content assets. A structured study guide may reorganize the material, but it never replaces the faithful transcript. `pinshu-content-assets` makes the main argument, methods, cases, figures, quotable expressions, and source boundaries usable without replaying the entire lesson. It does not automatically write an article. Markdown remains the canonical source for learning activities; a web interface is optional.

## Default deliverables for professional-learning courses

Each processed lesson produces:

1. A faithful edited transcript;
2. A structured study guide;
3. Status, links, and a concise knowledge summary in the course map.

When content reuse is selected, produce a readable content master for each lesson. For a complete course, also produce a course-level master connecting recurring questions, methods, cases, and disagreements back to the individual lessons. Keep every new master pending until the owner reviews it; do not present a script-level PASS as editorial approval. When learning or exam preparation is selected, produce candidate active-recall cards.

Learning activities are not pre-generated as a static exam bank. `pinshu-study` starts guided study, recall, follow-up questions, error diagnosis, source review, retries, and learning records only after the user explicitly asks to study, practice, review, or retest. It never invents mastery without a real response, but the absence of a response does not block production of candidate recall cards.

Historical pilots in this repository document the origin of rules and lessons from past failures. They are not production gates for new courses.

## Language and runtime-path contract

Repository instructions remain in English. Learner-facing output follows `output_language` in the production manifest: a short BCP-47 tag such as `en`, `en-US`, or `zh-Hans`, or the selector `match-user` or `match-source`. Old manifests that omit the field behave as `match-user`; when the user's language is unavailable, use the source language. Stable IDs, frontmatter keys, enum values, and other program fields remain English.

When a course-capture manifest or state file exists, every Skill uses its path templates through `course_pipeline.py paths`; no Skill translates or invents a parallel directory tree. For a new course without a manifest, create and confirm the manifest or an explicit path map before writing.

`pinshu-data-cleaning` is an optional upstream capability and is not included in the seven course/content packages or installed by its installer. If it is unavailable, provide pre-cleaned Markdown or a transcript, or use only the clean-text inputs supported by the selected Skill. The workflow must not silently skip heterogeneous-source cleaning.

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
| `pinshu-visual-system` | Plan, generate with an image-capable agent, visually inspect and export source-faithful content visuals |
| `pinshu-transcript` | Turn raw transcripts into faithful edited transcripts while preserving substantive meaning and source boundaries |
| `pinshu-distill` | Produce clear, self-contained structured study guides and approved cross-cutting topics from faithful transcripts |
| `pinshu-content-assets` | Organize corrected course, livestream, or interview material into a source-traceable content master for later writing; never auto-write the article |
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
