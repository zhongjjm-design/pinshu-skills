# 语义判定与独立 QA 合同

语义判定的任务不是评价“写得好不好”，而是证明忠实稿与讲义是否满足同一质量合同、能否进入正式知识库。

## 两种判定

- `writer_self_check`：普通清洁课由本课写稿模型在同一任务内对照原文提交 `semantic_check.json`；它不是独立 QA。
- `independent_qa`：命中风险触发器或稳定抽样时，使用与写稿不同的任务上下文，直接读取原始稿、忠实稿、讲义、核心质量合同和当前模式证据。
- `strict` 每课独立 QA；`fast` 与 `standard` 按稳定抽样与内容风险触发。
- 独立 QA 模型可以是另一低成本模型；出现真实歧义时升级强模型。
- 无论采用哪种判定，脚本 PASS、文件存在和写稿者自报都不能单独证明语义通过。

## 检查强度

- `fast`：普通课写稿语义自检；约 20% 稳定抽样、样课和风险触发课做完整独立 QA；
- `standard`：关键课和风险触发课完整独立 QA；普通课约 50% 稳定抽样；
- `strict`：每课完整独立 QA。

保障模式只改变证据形式与独立 QA 覆盖率，不能改变正文与讲义质量底线。第二轮独立复验只接收修改块、必要前后文、`review_round` 和上一轮问题列表；完整产物由脚本绑定 SHA-256，不重复全文灌入，只验证旧问题及其前后关系；除新发现的高严重度失真外，不得重新启动全文挑刺。

## 检查顺序

### 1. 来源与身份

确认课次、标题、讲师、来源视频和三个文件属于同一课。身份冲突直接 `BLOCKED`。

### 2. 全文覆盖

沿原文顺序检查：

- 开头、中段、结尾均能在忠实稿定位；
- 人物、数字、品牌、工具、案例、步骤、限制和反例有对应位置；
- 最长案例与最复杂论证完整；
- 若当前档位提供逐块覆盖表，检查其中 `noise` 与 `merged` 的理由；否则按档位核对锚点清单；
- 看似重复的段落是否包含新增信息。

每个失败项必须给出原文片段/块ID和成稿位置，禁止只写“信息不够完整”。

### 3. 忠实性

检查是否：

- 改变因果关系、对象、程度或适用边界；
- 把经验判断升级为普遍事实；
- 把讲师第一人称改成第三方总结；
- 补入原文没有的解释、数据或结论；
- 猜定了原文不确定的专名或数字。

### 4. 编辑质量

检查是否处于两个失败极端：

- 过度压缩：只剩摘要和结论；
- 几乎未编辑：原文加标题、超长文字墙。

同时检查标题、加粗、列表和破折号是否破坏阅读，而不是追求固定数量。

### 5. 讲义职责

讲义可以重组，但必须：

- 保留原文方法、论证、案例和边界；
- 回链原始稿和忠实稿；
- 区分讲师原话、编辑组织和待核验事实；
- 不把新推断写成讲师判断。

## 严重度与决策

- `high`：命中核心质量合同“失败判定”，会改变知识、来源身份、关键事实、原意或基本可读性；
- `note`：措辞、格式、轻微重复、台账补登和可优化表达，不改变可信度与使用。

决策：

- `pass`：没有未解决的 `high`；允许附带 notes；
- `fix_required`：至少一个 `high`，且位置明确、可一次定点修复；
- `escalated`：来源歧义、事实冲突，或一次返工后 `high` 仍存在；
- `blocked`：来源、身份或原文完整性有问题，生成稿无法解决。

`note` 不得单独触发返工、复验或强模型。格式小问题不能掩盖语义通过；语义高危也不能因格式漂亮而通过。

## 返工边界

QA只指出证据、影响和修复要求，不重写整篇。一般课最多一次常规返工；复验只检查上轮 `high` 是否关闭及其前后关系。没有剩余 `high` 即通过；仍有 `high` 时进入 `ESCALATED`，只允许一次强模型裁决、定点修复与终验，之后必须交付或停线，不进入新一轮润色。

第二轮 `targeted_recheck` 必须保留上一轮 high：已修好的条目写 `resolved: true`，并用非空 `resolved_evidence` 指向修改位置和复核依据；仍未解决的条目写 `resolved: false` 或不写该字段。首轮报告不得预写 `resolved: true`。`pass` 只排除有真实关闭证据的 high，不能通过清空 `issues` 或把问题移到自造字段绕过。

## QA报告

使用 `templates/qa-report.example.json`。报告至少包括：

- 结论；
- 来源身份检查；
- 覆盖结论；
- 逐项问题和证据；
- 风险级别；
- 建议状态；
- 是否需要强模型。

## 图解结果报告合同（仅 `visual_learning.enabled=true`）

总控在讲义 `SEMANTIC_QA_PASS` 后调用 `pinshu-visual-learning`，以 `visual-result.json` 交回真实审读与渲染结果；原语义 QA 报告不兼任图解报告。字段固定为：

- `schema_version: 1`、`kind: "visual_learning"`、相同的 `course_id`、整数 `lesson_no`；
- `decision: "pass" | "blocked" | "skipped"`；非空 `reviewer_model`、`reviewer_kind`、`checked_at`；
- `input_sha256.lecture` 为本课已绑定讲义哈希；通过时另含 `input_sha256.visual_md`、`input_sha256.visual_html`，分别是候选文件 SHA-256；
- `assets` 为 `{ "path": "绝对路径", "sha256": "实际文件哈希" }` 数组；通过时绑定每一张 MD 内嵌 PNG 及可编辑 SVG。SVG 放在候选 MD 目录之内；正式提升保持相同相对结构；
- `checks` 含严格布尔值 `semantic`、`desktop_render`、`mobile_render`、`obsidian_render`。`pass` 四项均须真实完成且为 `true`；机械检查不能代替语义、桌面、手机或 Obsidian 实读；
- `mobile_render=true` 时必须有 `mobile_evidence`：真实测得的视口宽、内容列宽，以及逐图的实际显示宽、最小显示字号和是否横向溢出。内容列按目标页面实测，不写死 351px；逐图须放得进内容列、无横滑，最小显示字号不得低于 11px；
- `obsidian_render=true` 时必须有 `obsidian_evidence`：由 Agent 或用户在 Obsidian 阅读视图完成整篇实读，记录 `checked_by`、`whole_document_checked: true` 和非空证据列表。静态 Markdown 检查、浏览器预览和单张截图不能代替；
- `pass` 不得保留 `blocking_reason`；非用户审查时 `reviewer_model` 必须能在 state.models 中对账；
- 正式图解 Markdown 的 frontmatter 最少含 `kind: 图解学习`、`status: 正式`。只精确验证字段值，不因正文中正常出现“候选”二字而拒绝；正式 MD/HTML 必须从最终位置解析来源回链，HTML 来源使用真实 `<a href>`；
- `blocked` 另有非空 `blocking_reason`，可记录用量和报告但不能进入 `ACCEPTED`；
- `skipped` 只适用于无可靠视觉来源：`skip_code: "no_reliable_visual_source"`、至少20字符的具体 `skip_reason`、非空 `source_limitations` 字符串数组（指出来源位置、缺什么及不能可靠表达的关系），且 `checks.semantic=true` 表示确实核查来源限制。渲染未发生的三项保持 `false`，不要求不存在的图解成品。预算不足、未打开 Obsidian或泛泛“暂不需要”都不能跳过。

`record-visual` 校验输入、图解候选和资产，绑定报告哈希并计入预算。`ACCEPTED` 再验证正式 MD／HTML 与候选一致、PNG／SVG 实物存在且哈希一致。MD 是主要学习笔记，PNG 逐模块嵌入；HTML 须由同一来源生成并自包含。报告只是检查证据声明，内容与 HTML 自包含仍由下游独立验证器和真实阅读验收，不能用报告代替。
