# Pinshu Skills

Aidan（品叔）维护的14项公开试用Skill，覆盖课程采集、忠实精编、知识提炼、课程编排、学习训练、内容母体、Markdown转PDF、写作、视觉系统、信息图、商业图形、图解学习、视频公共底座和品牌片拆解。

**中文是主要操作规则，英文README是国际化入口；两者使用同一套脚本、状态合同和测试，不维护功能不同的中英文管线。**

## 下载与安装

macOS或Linux（含WSL）需先有Bash、Git、rsync、Python 3。首次安装和受管升级使用同一条命令：

```bash
curl -fsSL https://raw.githubusercontent.com/zhongjjm-design/pinshu-skills/main/install.sh | bash
```

执行远程脚本前，应先阅读仓库中的[安装脚本](install.sh)。安装完成后重启Agent客户端。

包的共享位置为 `~/.agents/skills/`。安装器自动处理Claude的加载入口；其他Agent需按各自支持的Skill发现目录读取共享包，不必复制出另一套功能源。安装不自动提供模型账号、API额度或全部外部渲染依赖。

### 先预览，不写本机

```bash
curl -fsSL https://raw.githubusercontent.com/zhongjjm-design/pinshu-skills/main/install.sh | bash -s -- --dry-run
```

预览不创建锁、安装缓存、暂存、备份或归属回执，不做完整远端下载验证。真实安装会验证来源、名单与配套完整性。

### 已有旧包或本机定制

只有匹配安装归属记录的受管包才正常升级。已有同名包但没有归属证明，或者新增、修改、删除了文件/相关权限/链接，安装器默认拒绝，不会因为“做了备份”就覆盖你的增强。

旧官方版本确实未定制、克隆及包内容能精确证明一致时，可以明确选择 `--adopt-legacy` 接管；不要给定制包盲加此参数。拒绝时先保留原包，再审阅迁移方案。

失败回滚覆盖克隆、包目录、归属回执及必需客户端链接。旧内容保存在提示的可恢复备份位置。此命令不是后台自动更新。

## 14项能力

| 分组 | Skill |
|---|---|
| 课程与知识资产 | pinshu-course-capture、pinshu-transcript、pinshu-distill、pinshu-course、pinshu-study、pinshu-content-assets、pinshu-md2pdf |
| 视觉与品牌表达 | pinshu-visual-system、pinshu-infographic、pinshu-business-graphics、pinshu-film-teardown |
| 中文商业写作 | pinshu-write |
| 视频与图解配套 | pinshu-video-core、pinshu-visual-learning |

`pinshu-md2pdf`的数字保持原样。配套包随统一安装交付，不需要在不同Agent的仓库中分别拼装。

安装后可对Agent说：

> 使用pinshu-write，把我给的选题和材料写成中文商业分析文章，先提炼判断和大纲，再起草、审稿。

> 使用pinshu-course-capture，把这门课程整理成知识资产，先推荐用途、审核方式与最终资产，确认后执行。

## 私有配置与使用边界

公开包不带个人账号画像、真人参考图、私有课程/客户材料、API钥匙或机器路径。品牌、角色、草稿目录和禁词等通过明确配置或任务输入传入；升级不覆盖独立私有配置。

图解需要已验收讲义、用户样稿批准及真实阅读证据。脚本检查不代替图形语义与Obsidian实际阅读。影视需FFmpeg、Node/HyperFrames、相应Python音频依赖、授权素材和各人自己的配音API访问；离线合成素材与服务替身自测不等于真付费配音或实际平台成片验收。

PDF默认用WeasyPrint，不自动启动本机Chrome。Chrome转换需要明确指定，Chrome专项测试也必须明确开启；不要通过 `--no-sandbox` 绕过安全保护。

当前为公开试用版。已执行的测试和仍需按本机环境检查的能力分开看待，不承诺所有平台、原生PPTX或外部付费服务均已实测。

## 使用许可

按[LICENSE](LICENSE)，允许个人与团队内部使用、复制和修改，包括内部商业工作；用这些Skill产生的文章、文档、图片、视频等可商业使用。不授对外转卖或再分发Skill本身及修改版本的权利，扩大范围需另获许可。第三方原许可证与服务条款继续适用。这是受限源码可见许可，不是MIT或OSI开源许可，详见[NOTICE](NOTICE.md)。

## 本地验证

```bash
python3 scripts/validate_release.py --quick
bash tests/test_installer.sh
```

通过、失败、跳过分别报告；跳过测试不是业务成功。

---

<details>
<summary>English guide · expand to read</summary>

## Pinshu Skills

Aidan (Pinshu) maintains this published trial suite of fourteen skills for faithful transcript editing, course production, learning, reusable content assets, writing, visuals, visual-learning notes, shared video tooling, and brand-film teardown videos. It works with Claude Code and other compatible agents. Read the [Chinese guide](README.zh-CN.md) for the primary product instructions.

### Quick install

On macOS or Linux (including WSL), have Bash, Git, `rsync`, and Python 3 available. Use the same command for a first install or an update of packages already managed by this installer. A fresh computer gets all fourteen Skills. After installation, the installer records the source repository, Git revision, active package type, effective file tree, file hashes, relevant permissions, and supported public links. Future updates replace only packages that still match that ownership record; added, modified, deleted, permission-changed, unmarked, or otherwise customized same-name directories are refused before any active package is changed. Inspect the installer before executing a remote script on your computer.

```bash
curl -fsSL https://raw.githubusercontent.com/zhongjjm-design/pinshu-skills/main/install.sh | bash
```

Restart your Agent client after installation.

To preview local conflicts without writes, run the installer with `--dry-run`. Dry runs do not create locks, home subdirectories, clones, caches, staging trees, backups, links, receipts, or Git metadata refreshes; repository download and full remote validation are not performed during preview. When the installer is piped through stdin, dry-run ownership checks use only the already installed trusted helper from the managed clone, never a helper from the current working directory.

Unmarked legacy public packages are not adopted by default, even when their directory name, `SKILL.md` name, repository origin, or `.public-bundle` marker looks correct. If you intentionally want the installer to take over an older public installation, run it with `--adopt-legacy`; adoption succeeds only when the complete active effective tree exactly matches the existing known Pinshu clone and the relevant package plus installer metadata are clean against that clone's committed `HEAD`. If the existing clone is missing, dirty, partial in a way that cannot be proven, or the active package differs, the installer refuses the migration. Keep any refused local package as a separate private package or migrate it manually after review.

If a visual package is private or locally managed (no public-bundle marker), that package is retained. An existing core is also retained when local companions may depend on it. Missing or public companions still install/update automatically: their shared entry points link to the complete public suite in the managed repository clone, and use that suite's public core rather than the private global core. No extra command or destination choice is needed. With only a private visual core already installed, the result is thirteen updated public Skills plus the retained private core: all fourteen Skill names are available. Repeated updates accept only these installer-managed visual links; arbitrary destination links remain refused. Updating the private packages themselves requires a source-aware migration.

For managed packages that still match the installer record, the old active package tree and previous repository clone are moved to recoverable backup directories during an update. If an update fails after mutation starts, the installer rolls back the clone, package directories, ownership receipt, and any newly created Claude links; failed new paths are quarantined under the reported backup area. Re-run the same command whenever you want the latest published version; there is no background auto-update. Claude's existing shared-directory link is reused. In an existing real Claude skills directory, missing package links are added while conflicting copies/links are kept and reported.

### Get started

For the CLI-level production path, report contracts, safe accepted-file revision flow, and offline release checks, see [Course Foundation Quickstart](QUICKSTART.md). Source and repository-history boundaries are recorded in [Provenance](PROVENANCE.md).

Tell your Agent:

```text
Use pinshu-course-capture to process this course. First assess the course content and my goals, then recommend its intended uses, assurance level, and final assets. Wait for me to approve the production agreement before you begin.
```

Before production starts, the workflow confirms the course purpose, any external-use requirements, the assurance level, the final assets, and the sample gate. This prevents every course from being forced through the same process.

If you already have a faithful edited transcript and a structured study guide, start the reusable-content workflow directly:

```text
Use pinshu-content-assets to turn this lesson into one readable, source-traceable content master. Preserve the speaker's main argument and every useful method, case, figure, and expression. Mark missing evidence and quotations accurately. Do not write an article; leave the master pending my review.
```

### Visual assets for colleagues

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

### Brand-film teardown videos

[`pinshu-video-core`](pinshu-video-core/SKILL.md) is the shared public video base used by video-type Skills. [`pinshu-film-teardown`](pinshu-film-teardown/SKILL.md) is a public preview (0.1.0) that makes a peer-to-peer breakdown video (about four minutes) of a brand film, in a horizontal edition for WeChat Channels and a vertical edition for Douyin, with covers. A film is a project folder (footage, voice), a `spec.py` describing what the film says, and the skill's scripts. Captions, cuts and labels are anchored to the moment each word is actually spoken; the narration is synthesized in one pass and cut only at measured silences; the music is fitted so its own ending chord lands on the end card; an independent critic reviews every cut before it ships.

It is tested on macOS (on Linux, also install a CJK font such as Noto Sans CJK SC). It needs FFmpeg, Node.js and the HyperFrames CLI, a Python with numpy, soundfile, pillow and librosa, the BaoCut transcription CLI, and your own Gemini API key for the voice (optional: Demucs for vocal separation). Tell your Agent:

> Use pinshu-film-teardown to turn this brand film into a teardown video. Read its rules first, run the environment check, and show me the script and a 30-second preview before producing the whole film.

The skill ships no fonts, music, footage or keys. `scripts/new_project.py` copies the sound effects bundled with HyperFrames (Pixabay Content License) and, on macOS, the Hiragino Sans GB system font into the project and downloads Source Han Serif (SIL OFL) from Adobe's repository. `pinshu-video-core/tests/self_test.py` and `pinshu-film-teardown/tests/self_test.py` run offline on synthetic material with stand-ins for paid or platform services; they do not prove real paid narration or real platform rendering. It has been proven on one film so far; expect updates as more brands go through it.

### Visual Learning

[`pinshu-visual-learning`](pinshu-visual-learning/SKILL.md) turns an already semantically accepted lecture guide into a Markdown-first illustrated learning note, per-module PNG images with editable SVG sources, and a same-source self-contained HTML companion. It preserves source boundaries and does not replace the original transcript, faithful edit, structured lecture, recall training, or real learning record. The validator checks links, frontmatter, SVG parseability, offline HTML and measurable mobile readability, but semantic correctness and real Obsidian reading still need separate evidence.

### Core course-asset pipeline

```text
pinshu-course-capture → source capture and production orchestration
pinshu-transcript     → faithful edited transcript
pinshu-distill        → structured study guide
pinshu-content-assets → reusable content master from the approved edited transcript and guide
pinshu-study          → active recall, guided study, follow-up questions, and learning records
pinshu-course         → series orchestration, checkpoints, cross-lesson leads, independent QA, and promotion
```

The faithful edited transcript is the source of truth for downstream learning and content assets. A structured study guide may reorganize the material, but it never replaces the faithful transcript. `pinshu-content-assets` makes the main argument, methods, cases, figures, quotable expressions, and source boundaries usable without replaying the entire lesson. It does not automatically write an article. Markdown remains the canonical source for learning activities; a web interface is optional.

### Default deliverables for professional-learning courses

Each processed lesson produces:

1. A faithful edited transcript;
2. A structured study guide;
3. Status, links, and a concise knowledge summary in the course map.

When content reuse is selected, produce a readable content master for each lesson. For a complete course, also produce a course-level master connecting recurring questions, methods, cases, and disagreements back to the individual lessons. Keep every new master pending until the owner reviews it; do not present a script-level PASS as editorial approval. When learning or exam preparation is selected, produce candidate active-recall cards.

Learning activities are not pre-generated as a static exam bank. `pinshu-study` starts guided study, recall, follow-up questions, error diagnosis, source review, retries, and learning records only after the user explicitly asks to study, practice, review, or retest. It never invents mastery without a real response, but the absence of a response does not block production of candidate recall cards.

Historical pilots in this repository document the origin of rules and lessons from past failures. They are not production gates for new courses.

### Language and runtime-path contract

Chinese is the primary language of Skill operating instructions; this README is the English international entry point. Both entries use the same scripts, state contracts and tests. Learner-facing output follows `output_language` in the production manifest: a short BCP-47 tag such as `en`, `en-US`, or `zh-Hans`, or the selector `match-user` or `match-source`. Old manifests that omit the field behave as `match-user`; when the user's language is unavailable, use the source language. Stable IDs, frontmatter keys, enum values, and other program fields remain English.

When a course-capture manifest or state file exists, every Skill uses its path templates through `course_pipeline.py paths`; no Skill translates or invents a parallel directory tree. For a new course without a manifest, create and confirm the manifest or an explicit path map before writing.

`pinshu-data-cleaning` is an optional upstream capability and is not included in the seven course/content packages or installed by its installer. If it is unavailable, provide pre-cleaned Markdown or a transcript, or use only the clean-text inputs supported by the selected Skill. The workflow must not silently skip heterogeneous-source cleaning.

### Set the purpose before choosing assurance depth

Before work begins, `pinshu-course-capture` creates a production agreement that can be saved, displayed, and audited:

- Purposes may be combined: reference, systematic study, training or exam preparation, method transfer, and content reuse;
- Publication, public release, client delivery, academic use, and real-world decisions trigger a separate external-use review;
- Assurance uses one of three evidence levels—lightweight, standard, or complete—recommended from the source, risk, and intended use. Runtime manifests retain `fast | standard | strict` for compatibility with existing projects;
- Every lesson retains the source transcript, faithful edited transcript, structured study guide, and course map. Assurance level never removes these core assets;
- Active-recall cards, training banks, cross-cutting topics, and external verification are enabled by purpose. Learning records are created only after learning actually occurs.

For batches larger than three lessons, deliver one representative lesson first. Scale production only after the user approves its depth, format, and reading experience. Only high-severity findings trigger rework. Each lesson also has token, wall-clock, QA, and rework budgets; production stops and reports its state when a budget is exhausted.

### Included skills

| Skill | Purpose |
|---|---|
| `pinshu-visual-system` | Plan, generate with an image-capable agent, visually inspect and export source-faithful content visuals |
| `pinshu-infographic` | Plan source-anchored knowledge diagrams with explicit relationships, density and diagram review |
| `pinshu-business-graphics` | Select seven business-visual method families, distinguish metaphor from fact and prepare source-faithful concept graphics |
| `pinshu-visual-learning` | Convert an accepted course lecture into Markdown-first illustrated learning notes with PNG/SVG assets and same-source HTML |
| `pinshu-video-core` | Provide shared offline video scripts for narration, pacing, music fitting, rendering, mixing, QC and environment checks |
| `pinshu-film-teardown` | Turn a brand film (TVC, anniversary film, ad) into a teardown explainer video: real footage, AI narration, speaker bites, code-built motion and music, horizontal and vertical editions, covers, QC and an independent review loop |
| `pinshu-transcript` | Turn raw transcripts into faithful edited transcripts while preserving substantive meaning and source boundaries |
| `pinshu-distill` | Produce clear, self-contained structured study guides and approved cross-cutting topics from faithful transcripts |
| `pinshu-content-assets` | Organize corrected course, livestream, or interview material into a source-traceable content master for later writing; never auto-write the article |
| `pinshu-study` | Run stage-appropriate guided study, active recall, follow-up questions, error diagnosis, source review, and retesting, then save Markdown learning records |
| `pinshu-course` | Orchestrate multi-lesson courses, manage progress and checkpoints, track cross-lesson leads, run independent QA, and promote accepted assets |
| `pinshu-md2pdf` | Convert Markdown into a professionally typeset PDF |
| `pinshu-course-capture` | Capture source material from supported course video or transcript platforms and route it into the production pipeline |
| `pinshu-write` | Grow a Chinese business-writing idea into a sourced judgment, title, outline, draft, review sheet and final article candidate |

### Quality boundaries

- Spoken course content is not automatically equivalent to a textbook, regulation, industry standard, or objective fact. Preserve source identity and distinguish instructor claims, editorial organization, external verification, and unresolved items.
- For professional judgment, regulated domains, high-risk operations, or real-world use, do not elevate course claims into universal advice. Preserve applicability, limitations, and required safety boundaries.
- Creator self-review, file existence, and a script-level PASS never replace independent semantic QA.
- Active-recall assets distinguish atomic cards from synthesis cards. Cross-lesson leads distinguish candidates, future pointers, verified findings, and safety-governance items.
- The public repository excludes local course materials, personal learning records, and photographs of real people.

### Local validation

```bash
python3 scripts/validate_release.py
```

Aidan (Pinshu) created and maintains this repository. This is a published trial edition, not a claim of production stability on every platform. Under [LICENSE](LICENSE), personal and internal-team use and modification are permitted, including commercial internal work and commercial outputs. External resale or redistribution of the Skills requires separate permission. This is a restricted source-available license, not MIT or OSI open source; third-party licenses remain applicable. See [NOTICE](NOTICE.md).

</details>
