# Pinshu Skills

Aidan (Pinshu) maintains this suite of eleven skills for faithful transcript editing, course production, learning, reusable content assets, visuals, and brand-film teardown videos. It works with Claude Code and other compatible agents.

## Quick install

On macOS or Linux (including WSL), have Bash, Git, `rsync`, and Python 3 available. The same command installs all eleven skills on a fresh computer or upgrades an older Pinshu installation. Before replacing an existing, correctly named Pinshu Skill, the installer moves the complete old directory and any previous repository clone to recoverable backups; unrelated or unsafe paths are refused. Inspect the installer before executing a remote script on your computer.

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

The visual system is now a three-piece public preview:

This is a sharing trial for one image at a time with an Agent and actual human review. Its ongoing scope includes article visuals, social carousels, WeChat image posts, seasonal posters and promotional posters. Each format needs its own composition and acceptance; a successful cover does not validate a whole series. See [visual evolution](pinshu-visual-system/references/visual-evolution.md) for turning useful references and colleague feedback into tested methods.

| Package | Version | Best use |
|---|---|---|
| [pinshu-visual-system](pinshu-visual-system/README.md) | 0.2.4 | Choose among twelve scoped visual modes, plan a platform composition, render and prepare a reviewed candidate |
| [pinshu-infographic](pinshu-infographic/README.md) | 0.1.4 | Explain knowledge through source-anchored processes, comparison, hierarchy, components and real loops |
| [pinshu-business-graphics](pinshu-business-graphics/README.md) | 0.1.4 | Express a business argument with one of seven distinct visual method families |

All three use eleven platform presets. Work without a fixed character or supply your own approved references to a supported core mode. Planning uses Python 3; generation needs an image-capable agent; raster export uses ImageMagick 7. The companions require the public core 0.2.4 or later beside them, installed together by the repository installer. Precision charts need an editable chart tool and separate data review. Native SVG delivery requires an installed CJK font; PPTX delivery additionally uses LibreOffice and Poppler, with a render receipt and actual re-render pixel verification.

Tell your Agent:

> Use pinshu-visual-system to illustrate this article for WeChat. Read the source, recommend a coherent style, generate and inspect one first image, then prepare the reviewed platform-sized candidate. Use no fixed character.

For a knowledge diagram, name pinshu-infographic instead. For a commercial mechanism, strategic relationship or typographic argument, name pinshu-business-graphics. The linked READMEs contain actual new examples and their evidence records.

The core also has two experimental cultural-poster method cards. These are candidate research references outside the twelve-mode roster. Material-craft has two theme tests, with the origami sample awaiting cultural interpretation and layout-variation review; colorfield-landscape still needs an actual test. Neither enters automatic or batch routing. This is a maintained sharing edition with human review and repeatability limits clearly marked. The installer protects existing private/local installations of all three visual Skills from replacement. See the [visual repair notes](pinshu-visual-system/references/release-notes-0.2.4.md) for engineering changes and remaining acceptance limits.

## Brand-film teardown videos

[`pinshu-film-teardown`](pinshu-film-teardown/SKILL.md) is a public preview (0.1.0) that makes a peer-to-peer breakdown video (about four minutes) of a brand film, in a horizontal edition for WeChat Channels and a vertical edition for Douyin, with covers. A film is a project folder (footage, voice), a `spec.py` describing what the film says, and the skill's scripts. Captions, cuts and labels are anchored to the moment each word is actually spoken; the narration is synthesized in one pass and cut only at measured silences; the music is fitted so its own ending chord lands on the end card; an independent critic reviews every cut before it ships.

It is tested on macOS (on Linux, also install a CJK font such as Noto Sans CJK SC). It needs FFmpeg, Node.js and the HyperFrames CLI, a Python with numpy, soundfile, pillow and librosa, the BaoCut transcription CLI, and your own Gemini API key for the voice (optional: Demucs for vocal separation). Tell your Agent:

> Use pinshu-film-teardown to turn this brand film into a teardown video. Read its rules first, run the environment check, and show me the script and a 30-second preview before producing the whole film.

The skill ships no fonts, music, footage or keys. `scripts/new_project.py` copies the sound effects bundled with HyperFrames (Pixabay Content License) and, on macOS, the Hiragino Sans GB system font into the project and downloads Source Han Serif (SIL OFL) from Adobe's repository. `tests/self_test.py` runs the pipeline offline on synthetic material. It has been proven on one film so far; expect updates as more brands go through it.

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
| `pinshu-infographic` | Plan source-anchored knowledge diagrams with explicit relationships, density and diagram review |
| `pinshu-business-graphics` | Select seven business-visual method families, distinguish metaphor from fact and prepare source-faithful concept graphics |
| `pinshu-film-teardown` | Turn a brand film (TVC, anniversary film, ad) into a teardown explainer video: real footage, AI narration, speaker bites, code-built motion and music, horizontal and vertical editions, covers, QC and an independent review loop |
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
