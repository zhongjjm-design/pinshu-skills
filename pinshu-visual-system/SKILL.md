---
name: pinshu-visual-system
description: "用于来源忠实的文章配图、封面、社交卡片、演示视觉、手绘讲解图、跨平台内容视觉和用户自有授权角色一致性；English keywords: visual system, article illustration, cover image, social card, presentation visual, character consistency."
---

# Pinshu Visual System

## 中文主规则（公开候选）

本 Skill 负责公开可分享版的品叔视觉系统：读真实来源，固定 `character + task + structure + layout + mode + platform + density` 七字段，生成前保存计划和提示词，生成后检查实际位图与目标裁切。公开包不包含私人角色资产、账号映射、真人参考图或内部样张；如用户提供自己的已授权参考图，才按配置接入。

默认能力不能依赖本机私有素材。视觉验收分为来源语义、画面审美、平台裁切、文字可读、身份一致和人工接受；脚本 PASS、生成成功或模型自评都不是发布验收。商业图和信息图优先交给本仓两个 companion，文化海报候选方法只在明确请求时测试。

公开候选版本：**0.2.4**。原创方法归属 Aidan（品叔），实现与文档由项目维护者协作完成。此版是可移植共享层，不含私人角色资产、账号映射或内部样张；规则正文以中文为主，稳定 ID、脚本参数、文件名和机器字段保留英文。

## 当前任务要读取

- 读取 `references/workflow.md` 和 `references/system-registry.json`。
- 读取所选模式在 references/mode-cards 下的完整模式卡，例如 `references/mode-cards/notebook-knowledge-explainer.md`。
- 读取所选平台的 `references/platform-profiles.json`。
- 商业图或报告图读取 `references/business-graphics.md`。
- 用户提供自有授权角色时读取 `references/character-profiles.md`。
- 渲染后读取 `references/visual-qa.md` 并检查实际图片。
- 安装、依赖和命令例子读取 `references/quickstart.md`。
- 新视觉参考、海报格式或同事反馈读取 `references/visual-evolution.md`。

## 伴随路由

需要来源锚定知识图解时使用 `pinshu-infographic`；需要七类商业视觉母体时使用 `pinshu-business-graphics`。两个公开 companion 依赖本核心提供共享风格、平台和交付合同。只有用户明确要求文化海报方法研究时，才读取 `references/method-candidates.md`；其中候选不进入默认路由。

## 做视觉决策

Identify the source-supported claim, audience, delivery type and actual platform. Fix one visual card:

`character + task + structure + layout + mode + platform + density`

Use one main relationship, one composition and one visual mode per image. A whole article needs a coherent primary visual language and meaningful insertion points, not an equal number of images per section. When the user requests generation, proceed within that scope; otherwise present 2-3 concrete directions and recommend one.

The shared registry provides seven available or scoped modes, one character-dependent mode, three test-only candidates and one frozen candidate. "Available" describes the inherited method scope, not guaranteed cross-theme aesthetic stability. No public mode is described as fully automated production-ready. Character Presenter needs the user's own approved reference and an approved mode pairing. Warm Paper excludes fixed characters. Frozen candidates remain blocked.

## Compile, generate and review

Use `scripts/visual_compiler.py` to save the source, `route-plan.json` and `prompt-final.txt`. The output is a contract, not an image. Choose the mode and structure from actual source meaning; this release does not pretend a keyword classifier can understand an article.

Generate with the agent's available image tool. Load every required identity reference as an actual image input. Record the actual provider/model/channel when the runtime reports them; never guess a model name or silently start a paid API. For long exact text or multiple text blocks, generate an illustration/background and compose an editable text layer using the runtime's supported layout tools. Never paint over incorrect bitmap letters.

Inspect the actual full-size image and its thumbnail. Fix one real defect at a time. Recheck source meaning, wording, actions, identity, composition and platform crop. Internal visual checks and human acceptance are separate. One successful image does not establish repeatable production.

## 准备交付

First export the complete composition with scripts/export_platform_image.py; its default contain fit preserves content. Inspect the final platform image and thumbnail, then write the review record described in `references/visual-qa.md`. Run `scripts/publish_image.py` with the image, plan and matching review record. It packages the reviewed platform-sized image, creates a separate metadata-clean PNG copy and verifies pixel preservation. Any failure stops delivery; the source is never used as an export fallback. Any intended crop must be completed before this review.

Deliver the candidate image, insertion position or page function, source/plan/prompt paths, review evidence and any remaining limitation. Use the prepared copy for the reviewed candidate; keep the original. A mechanical PASS does not mean aesthetic approval, factual verification or permission to publish.

## 依赖与共享边界

Planning uses Python 3's standard library. Image generation requires an image-capable agent; no account, subscription or image backend is bundled. Export requires ImageMagick 7 (`magick`). Optional business/chart/PPT tools are chosen only when available; exact editable charts are not replaced by a bitmap.

The shared edition is intended for colleagues and other compatible agents to use and improve with the maintainer. Private character files belong in the user's own local project. The installer refuses to overwrite a same-name private/local visual system; upgrade only a marked public installation.

Before delivery, compose required native text, export the final platform image and inspect it and its thumbnail. Hash-bound QA must use review_stage=final-platform-image. For editable text/chart work, include the actual native SVG/PPTX evidence in QA; the wrapper rejects missing native labels and requires a verified render receipt. Source-external exact text needs a real declared user approval. See the core visual-qa reference for the precise contract.

For native SVG/PPTX composition, read [editable rendering](references/editable-rendering.md). Render with its explicit font and receipt workflow, review the final PNG, then verify re-render pixel identity during delivery.
