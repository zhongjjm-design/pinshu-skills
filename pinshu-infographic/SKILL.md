---
name: pinshu-infographic
description: "用于来源忠实的中文信息图、文章配图、文档讲解图、知识图解、PPT配图、直播大图、暖纸手绘图、灵动矢量图和清爽矢量图解；English keywords: Chinese infographic, explainer diagram, article illustration, knowledge diagram, PPT visual. 不包含私人角色资产。"
---

## 来源与维护

- 原创身份：品叔原创（original）
- 原创归属：Aidan（品叔）
- 维护者：Aidan（品叔）
- 上游依赖：`baoyu-infographic` 可作为可选分析工作流；不打包其代码、指令文件、布局库、样式库或参考资产
- 原创能力：三种公开可用视觉模式、中文远读与密度分流、角色隔离与防串台、信息逻辑门、三秒焦点、截图污染清除、PPT边界，以及基于多轮真实出图形成的审美 QA 和淘汰规则
- 依赖边界：运行时调用上游的通用内容分析、布局和生成工作流；不复制上游代码、指令文件、布局库、样式库或参考资产。使用上游依赖不改变本 Skill 的品叔原创身份
- 分发状态：公开候选；不包含私人角色图、账号映射、内部样张或未授权提示词

# 品叔信息图

版本：v3.6

视觉方向与最终取舍：Aidan（品叔）

Skill 架构与实现：Codex

这是公开可分享的信息图 Skill。它可以调用 `baoyu-infographic` 的通用分析、布局与生成工作流，也可以手动完成同等分析；在此基础上使用三种公开可用视觉模式、角色安全、中文远读、信息逻辑门和审美 QA，并受 `pinshu-visual-system` 的公开边界约束。

## 1. 加载依赖

开始前：

1. 完整读取 `baoyu-infographic/SKILL.md`。
   - 当前运行时不可见但安装了 `skill-router` 时，运行 `skill-router exact "baoyu-infographic"`。
   - 未安装上游时，先按上游仓库说明安装：`npx skills add jimliu/baoyu-skills`。
2. 采用上游的内容分析、结构化内容、布局推荐、确认门禁、提示词留档、图像后端和版本保留规则。
3. 完整读取同仓公开 `pinshu-visual-system/SKILL.md`。若用户提供自有授权角色参考，按公开角色配置接入；没有授权参考时只生成非特定人物或无角色图解。
4. 读取 `references/mode-routing.md` 和 `references/logic-and-density.md`。
5. 从总控注册表读取并完整加载所选模式的 `mode_card`。
6. 根据所选模式读取对应风格文件：
   - `warm-paper` → `pinshu-visual-system/references/mode-cards/warm-paper.md`
   - `lively-vector` → `pinshu-visual-system/references/mode-cards/lively-vector.md`
   - `character-presenter` → `pinshu-visual-system/references/mode-cards/character-presenter.md`

旧名称 `pinshu-presenter` 只作为兼容别名，固定解析为：

- 角色：`pingge`
- 模式：`character-presenter`

不得把别名解释成成熟品叔、和光先生、Aidan 本人或品妹。

缺少必需依赖时明确报告，不要凭记忆复写，也不要静默换成另一套风格。

## 2. 先过信息逻辑门

美化前先回答：

- 观众第一眼必须记住什么？
- 这张图表达的是流程、对比、层级、组成、循环，还是一个核心观点？
- 每条箭头能否用一个明确动词解释？
- 删除说明文字后，主要图形关系是否仍然成立？

如果主逻辑无法用一句话和一个主结构说清，先重组或拆图。不要用圆环、漏斗、卡片或人物掩盖逻辑不清。

## 3. 选择视觉模式

一张图只使用一种视觉模式。

| 模式 | 适用 | 核心特征 |
|---|---|---|
| `warm-paper` | 文章、知识库、课程讲义、温暖的人文或方法论内容 | 浅暖纸、深海军蓝手写字、陶土橙强调、克制胶带与手绘线 |
| `lively-vector` | 流程、架构、对比、分层、产品机制和课程图解 | 暖白底、低饱和牛仔蓝、鼠尾草绿、陶土橙、几何叠压与流动曲线 |
| `character-presenter` | 已获准角色讲知识、课程、公众号重点图、直播/PPT | 角色身份由注册表锁定；信息板承担逻辑，人物承担信任与亲和力；`pingge` 与 `pinmei` 均已完成横竖样张并可正式生产 |

本 Skill 只使用这三种模式；每种能否进自动生产，以 `pinshu-visual-system` 注册表的状态为准（注册表标为候选时只做测试，不进自动生产）。候选视觉模式统一在 `pinshu-visual-system` 中孵化，通过参考拆解、样张测试和用户确认后，才能进入本 Skill。

平台边界：

- `warm-paper` 保留给横版文章与知识结构图，不再作为朋友圈 3:4 默认模式；
- 朋友圈的情绪和生活内容可在总控候选池测试 `handwritten-documentary-card`，但该方向当前人工评价仅为及格，不是默认模式，本 Skill 不把它伪装成信息图；
- `lively-vector` 用于 PPT 层级图时必须使用一个主几何体与编辑式标题，拒绝标准台阶、圆柱、四等分卡片和底部胶囊总结。

模式卡是视觉语法的单一事实来源；本 Skill 的风格文件只补充信息图生图细节，不得另写冲突色板或构图规则。

## 4. 选择密度与布局

视觉模式和信息密度是两个维度，不要混为一谈：

- `document`：正文配图，4–7 个信息单元，最多两级说明。
- `slide`：16:9 PPT/直播大图，一页一个结论，3–5 个信息单元。

让上游推荐 3–5 个布局，再用 `references/logic-and-density.md` 检查是否符合中文阅读与观看距离。每张图只保留一个主布局。

## 5. 保存结构化内容

沿用上游的 `analysis.md` 与 `structured-content.md`，并额外写明：

- 视觉模式与密度配置；
- 角色、任务、结构和版式 ID；
- 使用场景和观看距离；
- 三秒焦点；
- 必须逐字保留的术语、数字和结论；
- 标题区与主体区的间距；
- 每个信息单元的短标题、短说明和单一视觉隐喻；
- 超过密度上限时的拆图方案。
- 使用的模式卡路径、版本和成熟度。

只做视觉压缩，不补造信息。

## 6. 确认后生成

沿用上游确认门禁。默认确认：

- 视觉模式；
- 密度配置；
- 上游布局；
- 画幅；
- 语言；
- 图像后端。

只有用户当前请求明确说“直接生成”“按默认出图”“跳过确认”或同义表达时才跳过。

生成前把完整提示词保存到独立文件 `prompts/NN-infographic-{slug}.md`。提示词必须包含：

- 上游布局；
- 本地视觉模式与密度配置；
- 模式卡中的色彩角色、空间语法、提示词骨架和负向约束；
- 所有必须出现的中文；
- 参考图及其角色；
- 字体、色板、留白和逻辑关系；
- 禁止项与截图污染清除要求。
- 角色状态；若以后新增候选角色，必须写明 `candidate-test`，不得伪装成正式生产。

暖纸模式遇到较长中文时，先压缩为不改变原意的短标签；如果生成模型连续两次把同一长句写错，保留失败稿，回到结构化内容缩短标签后重新生成。不得靠缩小字号或程序覆字硬救。

优先使用当前运行时原生 `imagegen` / `image_gen`。不得用 SVG、HTML、Canvas 或程序绘图冒充生成位图。

## 7. 使用参考资产

三张用户确认样张只用于锁定视觉语言：

- `assets/approved-examples/warm-paper-v4.png`
- `assets/approved-examples/lively-vector-muted-blue-v2.png`
- `assets/approved-examples/character-presenter-pingge-v1.png`

第二至第四轮的稳定回归基准由总控模式卡统一登记，当前包括：

- 暖纸：真实品牌内容横版；既有朋友圈竖版已被用户否决，不再列为稳定基准；
- 灵动矢量：真实品牌内容流程；既有 PPT 四层能力版因通用模板感被否决，第五轮编辑式折带仍是候选；
- 角色讲解：品哥跨主题横版；品妹短发通勤版已否决，长发、珊瑚红短夹克与雾蓝灰牛仔裤版已完成横竖回归并获品叔确认。

公开包不附带第三方参考截图。暖纸模式只使用已确认样张作为风格锚点；若用户另外提供参考图，只学习材质、色彩、密度和构图语言，不复制原文、品牌标志或完整构图。

角色身份始终以 `pinshu-visual-system/references/system-registry.json` 中登记的身份资产为最高优先级；本 Skill 的样张不能替代身份母版。旧路径 `pinshu-visual-system/assets/pinshu-identity-master.png` 仅为兼容入口，其规范角色是 `pingge`。

## 8. 视觉验收

实际打开生成图，再读取 `references/visual-qa.md` 并把结果写入 `qa.md`。

任何一项失败都保留当前候选，写新提示词和新输出路径后重新生成：

- 中文错误或不清楚；
- 三秒内看不到标题、主结构和结论；
- 图形关系需要二次、三次翻译；
- 信息密度过高；
- 风格落入普通企业 PPT、通用 SaaS 卡片墙、廉价海报或模板素材感；
- 播放键、手指、鼠标、窗口、字幕、水印或屏摄偏色混入成图；
- 角色身份漂移、角色名称误配或角色越权替代。
- 未获许可角色被批量、自动生产或冒充另一角色。

不得用 Pillow、ImageMagick、Canvas、SVG 或其他程序覆盖、擦除或重写位图文字。

## 9. 与 PPT 的边界

本 Skill 默认生成配图资产，不负责把整套可编辑 PPT 烘焙成图片。

- 标题、正文、数字、图表、关键标签、箭头和基础形状优先保留为 PPT 原生对象。
- 复杂插画、纸张纹理、人物和装饰性元素可作为位图或透明素材。
- 只有用户明确要“整页海报式大图”时，才生成包含全部页面文字的整页图。
- 整套可编辑 PPT 交给 `ppt-master`、`collaborative-ppt-forge` 或当前可编辑 PPT 工作流。

## 10. 交付

报告：

- 上游 Skill；
- 角色、任务、结构、版式、视觉模式与密度配置；
- 布局、画幅、语言与后端；
- 使用的参考图；
- 提示词、图片和 QA 的绝对路径；
- 是否通过人工确认；
- 作为位图使用，还是转入可编辑 PPT 流程。

未通过用户确认时标为候选稿，不宣称定稿。

`pinmei` 已于 2026-07-26 由品叔确认并转为正式角色。调用时通过：

```bash
python3 ../pinshu-visual-system/scripts/registry_guard.py resolve \
  --character pinmei \
  --task infographic \
  --structure process \
  --layout presenter-board \
  --mode character-presenter \
  --platform xiaohongshu \
  --density document
```

## 11. 私有边界

本版本属于品叔内部视觉系统，默认不推送 GitHub，不导出身份母版、账号映射、私有样张、内部提示词和反馈记录。未来若需要开源，只从 `pinshu-visual-system` 提取不含角色资产的通用结构、版式、质量门禁和工作流。

署名：Codex
