---
name: pinshu-business-graphics
description: "用于品叔商业图解、商业配图、概念图、商业信息图、PPT图解、报告视觉、视觉母体、字体隐喻、战略地图、结构剖面、编辑拼贴、工程图谱、中国现代主义、数据新闻；English keywords: business graphics, concept visual, strategy map, data journalism, report illustration."
---

## 来源与维护

- 原创身份：品叔原创（original）
- 原创归属：Aidan（品叔）
- 维护者：Aidan（品叔）
- 上游依赖：`baoyu-infographic` 仅作可选工作流参考，不打包其通用引擎
- 分发状态：公开候选；不包含私人角色、内部品牌素材、真实客户资产或未获授权样张
- 原创边界：七类商业视觉母体、内容关系路由、中文与数据 QA 由品叔体系形成

# Pinshu Business Graphics

把商业内容做成有判断、有证据、有画面秩序的静态图解。先选视觉母体，再选隐喻；样张只做质量锚点，不是模板。

## 必要伴随能力

- 有 `baoyu-infographic` 时，用它做来源分析、结构化内容、版式纪律和提示词留档；没有时仍要手动完成同等分析。
- 有图像生成能力时，用于栅格概念画面；没有时交付结构化方案、提示词和可编辑制作说明。
- 精确表格、密集数据、可编辑交付必须使用幻灯片、图表、Figma 或其他原生可编辑介质。
- 不能因为 SVG、HTML 或 canvas 更容易，就把用户明确要求的栅格图生成替换掉。

## 工作流

### 1. 先确定交付模式

把请求分为：

- `single`：一张封面、概念页或信息图；
- `series`：一篇文章、一个轮播或一个主题下的多张图；
- `deck`：一份演示或报告，包含不同页面功能。

For `single`, use exactly one visual mother.

For `series`, select one primary mother and optionally one secondary mother. Keep at least 70% of pages in the primary system.

For `deck`, keep one shared palette, typography, margin, and line system. Route page structures by content, but do not randomly alternate all seven styles.

### 2. Inspect the content before styling

Identify:

- complete title and the shorter visual thesis
- audience and use context
- concept, comparison, system, evidence, cultural, or decision content
- supplied data, source quality, and whether current verification is required
- exact names, terms, brands, dates, and labels that must not change
- aspect ratio and language

Do not invent statistics, cases, citations, or customer claims.

### 3. Select the visual mother

Read [router.md](references/router.md).

If the user names a mother, load only that mother’s reference file. If the user does not name one, recommend two or three candidates with a one-sentence rationale and one risk each.

For direct-generation requests, choose the strongest candidate and state the assumption before generating.

Approved mothers:

- [typographic-metaphor.md](references/typographic-metaphor.md)
- [strategic-map.md](references/strategic-map.md)
- [structural-section.md](references/structural-section.md)
- [editorial-collage.md](references/editorial-collage.md)
- [engineering-blueprint-narrative.md](references/engineering-blueprint-narrative.md)
- [chinese-modernism.md](references/chinese-modernism.md)
- [data-journalism.md](references/data-journalism.md)

### 4. Choose one semantic metaphor

Read [metaphor-router.md](references/metaphor-router.md) only after the visual mother is chosen.

Use one primary metaphor per page. Allow submodules only when they are parts of the same system. Do not stack unrelated funnel, compass, flywheel, ladder, window, and building metaphors.

### 5. Structure the content

Create:

1. one conclusion-led title
2. one short subtitle when needed
3. three to six principal information units
4. one clear reading path
5. one conclusion or action zone
6. source notes for any factual data

Keep the full title in smaller text when a shorter visual thesis is used.

### 6. Persist the prompt before rendering

Follow [output-contract.md](references/output-contract.md).

Write the complete final prompt under `prompts/` before calling an image backend. Include all exact visible text, composition, palette, typography, reference roles, source boundaries, and avoid rules.

### 7. Generate and validate

Render one candidate per distinct direction. Inspect the real output at original resolution.

Run [qa.md](references/qa.md). Check:

- Chinese accuracy and natural character width
- title hierarchy and thumbnail readability
- metaphor-content integration
- chart values and visual proportions
- invented labels, pseudo-English, logos, or watermarks
- whether the result truly belongs to the selected mother

If text or data is wrong, save the flawed candidate and regenerate from a new prompt file. Never paint over text on the bitmap.

### 8. Close out

Save the chosen asset into the working project, not only a generated-image cache. Report:

- selected visual mother
- layout and metaphor
- aspect and language
- source and prompt paths
- final image path
- any remaining bitmap or editability limitation

## Non-negotiable rules

- Visual mother is not a synonym for color palette.
- Changing keywords is not changing style.
- One mother must have its own composition grammar, typography, image language, and failure boundaries.
- Chinese must not be horizontally compressed to fit a narrow column.
- Concept art cannot masquerade as verified data.
- Data journalism requires traceable data and source notes.
- A style reference grants permission to study high-level traits, not to copy protected objects, wording, logos, or exact compositions.
- Do not claim a bitmap is an editable or precision-chart final.
