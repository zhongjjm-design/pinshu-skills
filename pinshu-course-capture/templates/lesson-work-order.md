# 单课工作包

## 任务身份

- course_id: `<课程标识>`
- lesson_no: `<课次>`
- official_title: `<官方标题>`
- lecturer: `<讲师>`
- task_role: `<writer | semantic_check | independent_qa | rework | visual_learning | committer>`
- worker_spec_path: `<自动生成的绝对路径>`
- worker_spec_sha256: `<hash>`
- assurance_mode: `<fast | standard | strict>`
- semantic_reviewer_kind: `<writer_self_check | independent_qa>`
- independent_qa_reason: `<未命中 | 稳定抽样 | 风险触发器 | strict | 样课>`
- budget_remaining: `<tokens / wall minutes / agent calls / max reworks / max QA rounds>`

## 四项核心结果

1. 不可变原始转写；
2. 忠实精编稿；
3. 结构化讲义；
4. 课程地图中的唯一幂等条目。

四项核心结果不变。图解由清单 `visual_learning` 单独启用：讲义语义通过后交给 `pinshu-visual-learning`，以 MD＋逐模块 PNG 为主，保存 SVG 图源和同源自包含 HTML；不把生成图代替讲义或原始来源。主动回忆、学习训练、横向专题和传播素材仍按原用途启用。

## 图解交接（仅启用时填写）

- lecture_semantic_approval: `<已通过报告路径及 SHA-256>`
- approved_lecture: `<讲义路径及 SHA-256>`
- visual_learning: `<enabled / pilot_lesson_no / batch_approved>`
- visual_paths: `<course_pipeline.py paths 输出的候选 visual_md、visual_html、visual_report 与正式路径>`
- visual_assets: `<候选MD同目录的分模块PNG与可编辑SVG；提升时保留同相对结构>`
- visual_result: `<visual-result.json，合同见 semantic-qa-contract.md>`

样课之外先核对用户图解批准及样课哈希；不能把原双稿样稿批准当作图解批准。写稿任务不提前制图；图解任务不反写双稿。真实桌面、手机、Obsidian检查未完成时报告 `blocked`，不填伪造的 `true`。缺可靠视觉来源时逐课给具体限制证据，不能因时间或审美问题通用跳过。

唯一提交者先把已验收双稿提升到正式路径并进入 `PROMOTED`；总控再用 `record-visual` 按正式目录解析图解来源回链并登记报告和实际用量；随后唯一提交者提升 MD、HTML、PNG、SVG，并在 `ACCEPTED` 前登记正式 MD／HTML 路径。

## 权威输入

- 核心质量合同（必须直接读取）：`<absolute path>/references/core-quality-contract.md`
- 核心合同哈希：`<hash>`
- 保障模式生产卡：`<absolute path>/references/production-modes-and-budgets.md`
- 领域与内容路由：`<absolute path>/references/domain-and-content-routing.md`
- 已解析领域适配器：`<只列本课命中项>`
- 已解析内容适配器：`<只列本课命中项>`
- 原始稿：`<absolute path + sha256>`
- 用户批准样稿：`<absolute path + sha256；样课自身写“待用户批准”>`
- QA 合同：`<仅独立 QA／复验填写>`
- 上一轮 QA 报告：`<仅返工与定点复验填写>`
- 第二轮复验输入：`<仅修改块＋必要前后文＋上一轮问题；报告绑定当前完整产物哈希，不再全文重读>`

普通批量课不重复加载整个 Skill 与无关参考。适配器只能增加术语、来源、风险和内容锚点，不能降低核心合同或增加默认产物。

## 允许写入

- 临时目录：`<absolute path>/lesson-<N>/`
- 忠实稿：`faithful.md`
- 讲义：`lecture.md`
- 待确认项：`uncertainties.json`
- 语义自检：`semantic_check.json`（未触发独立 QA 时）
- QA 报告：`qa_report.json`（触发独立 QA 时）
- 覆盖表：`coverage.json`（仅 strict 强制）

Worker 写入临时稿时，必须按 `course_pipeline.py paths` 给出的正式忠实稿、正式讲义和原始稿目标位置预先计算 Markdown 相对回链。忠实稿回链原始转写；讲义分别回链原始转写和正式忠实稿。正文及 frontmatter 禁止引用 `runtime/`、`lesson-*` 或其他临时生产路径。

除提交者外，禁止写正式课程库与课程地图。

## 完稿前回扫

- 人物、账号、品牌、工具、数字、日期、关键案例、方法、限制条件、首中尾；
- 只登记影响专名、数字、事实、来源或后续复核的 STT 冲突；
- strict 再执行逐块覆盖；
- 外部正式使用另走统一外部使用闸门，不混入内部验收。
- 以正式目标位置解析忠实稿和讲义中的 Markdown 回链：忠实稿到原始转写、讲义到原始转写与忠实稿均须存在；全文搜索 `runtime/`、`lesson-` 应为0。

## 完成输出

```json
{
  "lesson_no": 1,
  "result": "drafted | semantic_checked | qa_completed | fix_completed | blocked",
  "worker_spec_sha256": "...",
  "artifacts": {},
  "artifact_sha256": {},
  "usage_delta": {"tokens": 0, "wall_minutes": 0, "agent_calls": 1},
  "uncertainty_count": 0,
  "blocking_reason": null
}
```

“已生成”不得写成“已验收”。
