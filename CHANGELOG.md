# Changelog

## Visual System 1.0.0-rc.2 and WeChat Layout 0.4.0-rc.3 - 2026-10-25

- Expand the public visual core from twelve directions to 25 bundled visual modes with Chinese short names, six explicit external handoffs, seven held routes, and preserved frozen/retired boundaries.
- Update `pinshu-infographic` and `pinshu-business-graphics` to 0.1.6 so they accept semantic prerelease core versions; remove the retired `lively-vector` route from the infographic companion instead of bypassing the core registry.
- Add source-bound prompt compilation, pre-generation prompt continuity checks, character authorization hashes, exact-text routing, atomic plan output, and explicit separation between mechanical readiness, image generation, visual review, and human acceptance.
- Add cleaned public examples, 39 self-contained release tests, and optional 81-test article integration coverage with declared dependency-based skips.
- Remove a hidden machine-specific plugin pointer, make unsupported Python fail the doctor command, and audit all hidden and extensionless text members in release candidates.
- Clean seven distributed PNGs without changing dimensions or pixels; bump the WeChat layout preview to 0.4.0-rc.3 for its three cleaned chapter assets.
- Keep WorkBuddy and ZCode compatibility claims bounded: the latest text contract is not yet re-rendered in WorkBuddy, ZCode's ordinary request did not complete, and technical tests do not establish cross-agent aesthetic stability.

## pinshu-write 4.0.0 - 2026-10-25

- 写稿流程更新为十步、三道闸门：先向作者问清问题，完整找料后再想透；同一写手从沟通写到修改，专家、核查官、读者和主编按各自材料独立审稿，事实复核和修改后复检保留。
- 加入随包交付的通用《中文商业长文好稿标准》，公开安装不再依赖发布者本机的账号文件；团队仍可在配置中换成自己的标准。
- 公开版不分发维护者版本史、真实改稿故事、内部路径、私人反馈或本机模型通道；模型调用只保留通用角色和授权接口说明。原有 Linux 亚秒级 CPU 采样回归继续保留，并与 4.0 的调用截止时间能力合并。
- 4.0 照真稿测出的问题修改，修改后尚未跑过真稿验证。
- 本次只更新 `pinshu-write`，未增加 Skill，其他 14 个 Skill 内容不变。

## 七项 Skill 更新 - 2026-10-19

- pinshu-write 3.3.0：完整替换旧流程，保留作者种子、整篇主线、开头选择、跨厂商角色审稿、修订对比与导出；不分发私人维护档案和账号配置。保留原 207 项 pytest 回归，另加 4 项 Linux CPU 采样回归：Linux 使用 procfs 的亚秒级时钟计数，避免整秒 ps 时间把仍在计算的调用误停。
- pinshu-visual-system 0.4.0：抽取通用整篇配图与排版更新、截图返修、逐图审核续跑、跨平台锁和 UTF-8 处理；继续保留公开版的来源、身份、元数据与原生文本安全合同。私有角色资产和账号映射不分发。
- pinshu-wechat-layout 0.4.0-rc.2：七款模板，支持双栏标题、2–4 列表格和提示词卡；视频卡片面向读者安全，微信后台效果仍需发布者逐款真机验收。
- pinshu-video-core 0.2.0：无需时间轴的独立视频 QC、可选配音接口和发布文案参考；付费 API 与真实平台发布不由离线自测证明。
- pinshu-business-graphics 0.1.5、pinshu-infographic 0.1.5：明确视觉总控调用顺序和自有授权角色边界，保留独立商业图解与信息图入口。
- pinshu-transcript 0.2.0：明确原始 ASR、校对中间稿和忠实整理的边界，底稿永久保留。
- 本次只更新上述七项，统一安装名单仍为 15 项；未增加其他本机 Skill。

## Unreleased - 2026-10-12

- Add pinshu-wechat-layout 0.4.0-rc.1 (trial edition): turn an approved Markdown article and its image handoff into six equal-status, switchable WeChat layout previews with copyable body text, including the Chief Brand Officer classic edition and its six authorized chapter-number images. The lead image is unframed; body images retain thin template-specific frames; references and author-selected emphasis use separate reading treatments.
- Upgrade pinshu-write from 1.0.0 to 1.3.0: add environment self-check, exact ready-folder export and pair validation, evidence-screen capture handoff, revision sizing, wording review, quote repair and 103 regression tests.
- Upgrade the sanitized public pinshu-visual-system to 0.3.0 with the ready-article bridge, screenshot fallback, image-hash handoff and share-only export boundary; private identity assets and local mappings remain excluded.
- Extend the installer, release validator, manifest and installer tests to fifteen packages. Repeat installs replace only installer-owned public packages, preserve backups and refuse private or modified same-name packages.

## Course Foundation 0.1.0 - 2026-10-07

- Add a CLI-level production foundation for stable path contexts, explicit production agreements, mechanical preflight reports, hash-bound semantic QA, auditable promotion, and bounded writer self-rework.
- Add safe post-acceptance revision workflows for metadata/link, formatting, and content changes; substantive edits require current independent QA and open revisions fail audit.
- Add public quickstart and provenance documentation, focused offline release checks, regression coverage, and a reproducible SHA-256 release manifest.
- Keep one-command installation and repeat upgrades on the same installer path: recognized public packages and the managed repository clone are backed up and replaced, partial older installations are completed, and unrelated or private collisions remain protected.

## Visual set: core 0.2.0, companions 0.1.0 - 2026-10-06

- Complete the public three-piece visual set with independent pinshu-infographic and pinshu-business-graphics packages. The repository now contains eleven Skills.
- Preserve original-source excerpts, unit/arrow contracts and separate semantic review from mechanical validation. Enforce diagram density, real loop closure and explicit experimental-mode tests.
- Move the seven full business-mother cards into the commercial companion. Keep business mothers separate from illustration modes; distinguish proposed metaphors from facts and require provenance for datasets.
- Require editable precision-chart finals; reject raster delivery as a substitute. Require specialized workflow review alongside the five core image checks.
- Add two research-derived cultural-poster candidate cards outside the original twelve modes. Material Craft has two new theme trials; Colorfield Landscape remains untested in this release. Neither is auto-routed or promoted.
- Include actual new source-faithful diagram and business-workbench examples with exact generation histories, a rejected composition record, source/image hashes and export evidence.
- Extend the transactional installer, its upgrade/private-collision tests, release checks and CI to eleven packages. Protect private installations of all three visual Skills.

The public editions are usable sharing previews. Actual examples received agent inspection and exact-size/copy checks; human aesthetic acceptance and stable batch generation remain pending. Private character/IP assets are excluded.

## Film Teardown 0.1.0 - 2026-10-06

- Add pinshu-film-teardown: turn a brand film into a teardown explainer video, with horizontal and vertical editions, covers, publishing copy, QC and an independent review loop.
- Anchor captions, cuts and labels to real pronunciation; synthesize the whole narration in one pass and refuse to reuse a take made from different text; fit the music so its closing cadence lands on the end card.
- Ship the current rules, the pitfalls log, the `spec.py` field reference and three review prompts; an environment check (`doctor.py`) and an offline self-test on synthetic material.
- Extend the installer, release validation and CI to nine packages; CI runs the film self-test with FFmpeg installed.
- Keep client footage, client names, keys and local paths outside the public bundle; each colleague uses their own Gemini key.

This is a public preview proven on one film. Real rendering, real narration and visual acceptance are checked per film, not by the self-test.

## Visual System 0.1.0 - 2026-10-05

- Add the first portable sharing edition of pinshu-visual-system to the seven course/content Skills.
- Share twelve visual-mode cards, seven business-visual method families, eleven platform presets and an explicit content-to-visual workflow.
- Provide a portable plan compiler, user-supplied character references, editable-text routing, exact-size export, crop previews and reviewed candidate preparation.
- Reject fixed characters in Warm Paper, unapproved identity/mode pairings, frozen candidates and delivery after an export failure.
- Extend the transactional installer and release validation to eight packages. Protect existing private visual-system installations from replacement.
- Keep private character artwork, account mappings, private feedback and local project material outside the public bundle.

This is a public preview for use and continued iteration. Mechanical verification is separate from visual acceptance and repeatable batch-production validation.
