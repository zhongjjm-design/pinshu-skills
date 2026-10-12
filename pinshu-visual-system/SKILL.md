---
name: pinshu-visual-system
description: "用于来源忠实的文章配图、封面、社交卡片、演示视觉、手绘讲解图、跨平台内容视觉和用户自有授权角色一致性；English keywords: visual system, article illustration, cover image, social card, presentation visual, character consistency."
---

# Pinshu Visual System

## 中文主规则（公开候选）

本 Skill 负责公开可分享版的品叔视觉系统：读真实来源，固定 `character + task + structure + layout + mode + platform + density` 七字段，生成前保存计划和提示词，生成后检查实际位图与目标裁切。公开包不包含私人角色资产、账号映射、真人参考图或内部样张；如用户提供自己的已授权参考图，才按配置接入。

默认能力不能依赖本机私有素材。视觉验收分为来源语义、画面审美、平台裁切、文字可读、身份一致和人工接受；脚本 PASS、生成成功或模型自评都不是发布验收。商业图和信息图优先交给本仓两个 companion，文化海报候选方法只在明确请求时测试。

公开候选版本：**0.3.0**。原创方法归属 Aidan（品叔），实现与文档由项目维护者协作完成。此版是可移植共享层，不含私人角色资产、账号映射或内部样张；规则正文以中文为主，稳定 ID、脚本参数、文件名和机器字段保留英文。

## 运行环境（先跑自查）

下面的命令都在本 Skill 的根目录里执行（装好后就是 `skills/pinshu-visual-system/`，先 `cd` 进去）。

- 必需：Python 3.10+，`python3 -m pip install -r requirements.txt`（Pillow、markdown-it-py、beautifulsoup4）；同一个 skills 目录里装好 `pinshu-wechat-layout`。
- 可选：ego 浏览器（自动截图、手机检查）；ImageMagick 7（平台尺寸导出、发布副本）。缺了自查会说跳过哪一步。
- 生图：本 Skill 不自带生图模型和钥匙，靠当前 Agent 自己的生图能力。没有就只交视觉计划和提示词，标“待生图”。
- 自查：`python3 scripts/doctor.py`。它说 Python 太旧，就按它给的补法换成新版 Python 再跑。

**两种“做完”要分清。** 只有 Python：能做到格式检查、视觉计划、待截图清单、排版预览，算“准备包完成”。浏览器、生图、ImageMagick 都齐：才能截图、出图、导出，算“成品完成”。不许把前者报成后者。

## 公众号整篇文章：三步上手

1. **先查格式。** `python3 scripts/run_ready_article.py --article <定稿正文> --kit <发布物料包> --check-format`。格式约定见 `references/ready-folder-contract.md`。
2. **做图。** 证据截图只用截图工具，最小命令（先在 ego 里打开一个空间，拿到空间号）：
   `python3 scripts/capture_evidence.py --space-id <空间号> --url <原帖网址> --selector <唯一选择器> --purpose quote --describe "<大白话：截哪一块>" --output-dir <过程文件夹/配图/截图_01>`
   选择器不好写就把 `--selector` 换成 `--clip X Y 宽 高`。失败了用同一条命令重跑，第 3 次失败会自动生成人工截图指引并停下。其他规矩见 `references/article-asset-handoff.md` 开头九条。封面出 2 到 3 张真样张让作者挑。每张图都要打开看。
3. **排版。** `python3 scripts/run_ready_article.py --article <正文> --kit <物料包> --output-dir <过程文件夹里的新目录> --space-id <ego空间号>`（没浏览器用 `--prepare-only`）。它会生成六款排版预览，并回写物料包进度。

## 出错了怎么办

- 缺库、找不到排版 Skill：跑 `scripts/doctor.py`，照补法装。
- 格式检查不通过：让写稿方用导出脚本重导，不手改。
- 截图失败满 3 次：照工具生成的“人工截图指引”人工截，其余照常往下做。
- 截图“成功”但有遮挡、截断：重截，或用 `--clip X Y 宽 高` 按坐标截；修好的图放回原位，在物料包进度里记一行。

> 第一次跑通整篇流程，读到这里就够了。下面是做视觉决策、生图和维护时才需要的规则。

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

The shared edition is intended for colleagues and other compatible agents to use and improve with the maintainer. Private character files belong in the user's own local project. Installation must preserve any same-name private/local visual system and upgrade only a marked public installation. This local candidate has not yet been integrated or release-tested with the repository installer.

Before delivery, compose required native text, export the final platform image and inspect it and its thumbnail. Hash-bound QA must use review_stage=final-platform-image. For editable text/chart work, include the actual native SVG/PPTX evidence in QA; the wrapper rejects missing native labels and requires a verified render receipt. Source-external exact text needs a real declared user approval. See the core visual-qa reference for the precise contract.

For native SVG/PPTX composition, read `references/editable-rendering.md`. Render with its explicit font and receipt workflow, review the final PNG, then verify re-render pixel identity during delivery.

## 模式与候选方法的直接入口

按上面已选定的模式读取对应完整说明；状态以注册表为准，不因列在此处自动启用。

- `references/mode-cards/airy-architectural-watercolor.md`。
- `references/mode-cards/archive-tabletop-editorial.md`。
- `references/mode-cards/character-presenter.md`。
- `references/mode-cards/cinematic-ink-narrative.md`。
- `references/mode-cards/clear-portrait-doodle-collage.md`。
- `references/mode-cards/hand-drawn-comparison-comic.md`。
- `references/mode-cards/handwritten-documentary-card.md`。
- `references/mode-cards/literary-crayon-editorial.md`。
- `references/mode-cards/lively-vector.md`。
- `references/mode-cards/notebook-knowledge-explainer.md`。
- `references/mode-cards/warm-paper.md`。
- `references/mode-cards/warm-studio-illustration.md`。

只有用户明确要求文化海报研究时，按所选方法读取：

- `references/method-cards/oriental-colorfield-landscape.md`。
- `references/method-cards/oriental-material-craft.md`。

核对旧版本变化时读取，历史说明不覆盖当前工作流：

- `references/release-notes-0.2.1.md`。
- `references/release-notes-0.2.2.md`。
- `references/release-notes-0.2.3.md`。
- `references/release-notes-0.2.4.md`。

修订记录：`references/release-notes-0.3.0.md`（本版）、`references/release-notes-0.2.5-rc.1.md`。

## Share finished images safely

All route plans, prompts, source snapshots, QA files, render/clean/export receipts and complete delivery directories are local-only: they can contain absolute source, font, reviewer and output paths. Keep them locally for audit. To share user-approved final PNG files, run `scripts/export_share.py --image <final.png> --output-dir <new-share-directory>` (repeat --image for multiple files). It copies only metadata-whitelisted PNGs and creates share-manifest.json with filenames and hashes; it excludes every local receipt and native SVG/PPTX. Read `references/sharing-boundary.md` before handing files to colleagues. Share only the files listed in that manifest. Image sharing does not confer approval, rights or aesthetic acceptance.

Publishing cleanup and sharing use one PNG chunk whitelist. prepare_publish_images.py removes all other ancillary chunks after conversion, including tIME/orNT, verifies dimensions and AE=0, then runs the same validator as export_share.py before PASS. The original image is unchanged. “Metadata-clean” here means no metadata outside that whitelist; rendering/color/density chunks can remain. For system-produced raster images, run cleanup first and share the resulting *-publish-clean.png; a raw source with metadata is correctly rejected by the sharing gate. Local source/font/QA receipts stay excluded.
