---
name: pinshu-course-capture
description: "课程资产化统一入口与生产总编排。触发词：课程资产化、把这门课资产化、把图中这门课程资产化、把已购课程变成知识资产、整理成课程知识资产、处理第X课、批量整理课程、网盘取稿、继续课程流水线；English keywords: course capture, course pipeline, batch lesson production, resume course workflow, cloud drive transcript."
---

# 课程原文采集与分级生产编排

## 来源与维护

- 原创身份：品叔原创（original）
- 原创归属与维护者：Aidan（品叔）
- 上游依赖：`pinshu-transcript`、`pinshu-distill`、`pinshu-course`、`pinshu-study`、`pinshu-content-assets`
- 图解学习下游：`pinshu-visual-learning` 属于本轮 14 项候选，但不得静默启用；只有课程清单明确开启、讲义语义通过并能完成真实检查时才可调用，否则记录为依赖或验收阻塞。
- 分发状态：公开候选；不声明正式发布、CI 通过、tag 已创建或同事已验证安装。

## 统一自然语言入口

“课程资产化”是整个课程系列 Skill 的统一自然语言入口。用户说出以下任意表达——无论提供的是文字、课程链接、课程截图、直播回放还是当前页面——都由本 Skill 总入口接管，自动编排 `pinshu-transcript`、`pinshu-distill`、`pinshu-course`、`pinshu-study`、`pinshu-content-assets`；不得只生成逐字稿或忠实精编稿，也不得要求用户指定系列 Skill 的调用顺序：

- 课程资产化；
- 把这门课资产化；
- 把图中这门课程资产化；
- 把已购课程变成知识资产；
- 整理成课程知识资产；
- 把课程链接、课程截图或直播回放交给 Agent 并要求“变成课程资产”的同类表达。

命中后的默认行为（细节沿用下文与既有规则，不在其他文件重复整套流程）：

1. 先从文字、截图、链接或当前页面识别课程名称与平台；信息不足时只追问完成任务所必需的最少信息；
2. 先只读盘点课程身份、范围、来源、采集可行性、用途和目标路径，此阶段不写入任何文件；
3. 回显“开工前：先确认课程生产约定”一节的四件事，经用户批准后才生产 1 节代表性样稿，样稿通过后才能批量处理；
4. 每课固定交付不可变原始转写、忠实精编稿、结构化讲义和课程地图唯一条目，四项缺一不可；
5. 图解学习不是默认产物。只有清单显式启用且 `pinshu-visual-learning` 依赖完整可用时，讲义语义通过后才可调用；否则在课程状态和交付说明中写明“图解依赖未安装/未验证”，不得默默跳过或假称已验收。先只做指定样课，用户批准后才放量；旧清单和旧状态缺少配置时不补产、不迁移；
6. 学习训练、学习记录和内容资产仍按现有用途判断与真实活动规则执行，沿用 `pinshu-course` 与 `pinshu-study` 的既有规则；
7. 不绕过登录、付费、下载权限或 DRM 限制。

反例路由：用户只要单项成果——例如“只帮我校对这份逐字稿”——不启动整门课程流水线，直接交给对应分项 Skill（如 `pinshu-transcript`）按其自身规则处理。面向用户的回显一律使用中文业务语言，不向用户输出英文 Skill 名或内部状态值。

## 身份与目标

- 原创归属：Aidan（品叔）
- 上游依赖：`pinshu-transcript`、`pinshu-distill`、`pinshu-course`
- 本 Skill 是**课程生产总入口**：让用户只下达一次任务，由系统完成原始转写采集、忠实精编稿、结构化讲义、课程地图更新；初始化时判断课程用途，系统学习和备考型课程继续生成复习与训练内容；真实学习发生后再由 `pinshu-study` 保存学习记录。独立 QA、返工、入库、状态对账和恢复按条件触发。
- 网盘只是可替换的原文采集适配器；后续生产不依赖某个平台、特定个人、特定浏览器或特定模型。

## 职责边界

本 Skill 负责：任务编排、状态、交接、质量闸门、模型升级、单一正式写入者和断点恢复。

下游职责：`pinshu-transcript` 负责忠实精编稿，`pinshu-distill` 负责结构化讲义，`pinshu-course` 负责课程用途、地图与跨课资产，`pinshu-study` 负责复习训练内容和真实学习记录；`pinshu-visual-learning` 在讲义语义通过后负责图解学习笔记与配图，不改原始稿、忠实稿和讲义。

原始稿是不可变底稿。任何生成稿都不能反向补写原始稿。

## 开工前：先确认课程生产约定

总控先根据课程名称、结构、内容风险和用户目标给出推荐，用户只需确认或修改；不要把内部英文值和技术判断直接甩给用户。一次说明四件事：

1. **课程用途（可多选）**：资料参考/归档、系统学习/复习、训练/认证/备考、方法迁移/实际项目、内容资产/内部复用；
2. **是否对外使用**：出版、公开发布、付费课程、客户交付、论文或实际决策单独确认，不能混在课程用途里；
3. **审核方式**：系统推荐轻量证据、标准证据或完整证据，并用一句话说明依据；三者只改变证据密度、独立 QA 抽样和预算，不改变质量底线与四项核心结果；
4. **最终资产**：固定交付原始转写、忠实精编稿、结构化讲义和课程地图；新课程同时列出图解学习笔记（MD＋分模块 PNG、SVG 图源、同源 HTML 辅助页），再列出本次启用的复习训练、横向专题或外部使用核验。

把确认结果写入 manifest 的 `course_purpose`、两项判断依据、`optional_extensions`、`external_use` 和 `intake_confirmation`；图解学习单独记录到 `visual_learning`，不塞进受限的 `optional_extensions`。未确认生产约定不得初始化；可运行 `agreement` 命令回显本次约定，供用户、写稿者和 QA 共同核对。

启动还必须具备课程身份、讲师、唯一根目录、课次与来源清单、主写稿模型、命中触发器时可用的 QA 路由，以及可写临时运行目录。初稿不得直接进入正式知识库。

批量超过 3 课时，先完成 1 课真实样稿并由用户亲眼确认版式、详略和阅读体验；样稿未批准前只允许继续采集原文。机器 PASS、Agent 自评和独立 QA 都不能代替用户批准。

从 `templates/course-manifest.example.json` 建立运行清单，并读取 `references/production-modes-and-budgets.md`。运行状态属于课程项目，不写回 Skill 源码。

## 一次命令后的默认流程

### 1. 初始化或恢复

```bash
python3 scripts/course_pipeline.py init \
  --manifest <course-manifest.json> \
  --state <runtime/course-state.json>
```

状态文件已存在时不覆盖，改用 `next` 或 `summary` 继续。主对话只维护短任务清单；全文、产物和状态都从文件读取。

### 2. 逐课采集原文

先根据视频所在平台选择采集适配器。当前正式生产只启用百度网盘；其他平台不进入默认课程流水线，避免未经验证的适配器影响已验证流程：

| 来源 | 状态 | 入口 |
|---|---|---|
| 百度网盘 | 正式支持，已验证 | 网页播放器“文稿” |
| 夸克网盘 | 暂停接入，未通过端到端测试 | 不进入默认流程 |
| 阿里云盘及其他平台 | 暂不接入 | 不进入默认流程 |
| 已落盘视频/音频 | 备用 | 本地字幕或本地转写 |

正式采集只允许使用百度适配器。其他平台即使能够定位文件，也必须单独测试通过后才能加入，不得因为有适配器文档就视为可用。

百度适配器遵守同一顺序：优先获取网页播放器原生“文稿/字幕/转写”，再考虑用户明确允许下载后的本地转写；AI总结、思维导图和课件只能作为辅助材料，不能替代原始文稿。登录、验证码、付费和下载权限不得绕过。

采集适配器必须交回：原始正文、来源平台、视频身份、完整路径或文件名、采集方式、首句、末句和完整性证据。

采集成功后先保存 `00_原始转写/第X课·官方标题.md`，再把状态从 `DISCOVERED` 更新为 `CAPTURED`。找不到文稿、登录失效、疑似截断、无下载权限且无法转写时标记 `BLOCKED`，记录原因，继续处理不依赖该课的任务。

### 3. 原文完整性验收

必须同时检查：

- 来源课次、标题、视频身份一致；
- 平台/转写工具返回正文与落盘正文一致，允许换行差异；
- 开头、中段、结尾均存在，末句完整；
- 无选集、按钮、推荐视频等界面文字；
- 无明显缺段、混课或重复加载。

平台原生文稿与本地 ASR 的来源必须写入 frontmatter；不得把平台 AI 总结误标为原始转写。

通过后进入 `SOURCE_VERIFIED`。仅有文件或字符数不能证明完整。

### 4. 生成单课工作包

总控填写 `templates/lesson-work-order.md`，明确生产档位、预算、当前 QA 轮次和允许写入范围。

- Worker 必读：当前课原始稿、`core-quality-contract.md`、用户已批准样稿、当前保障模式生产卡和单课工作包；命中独立 QA 时还必须读取 `semantic-qa-contract.md`；
- 完整核心合同始终直接读取，不能只交付哈希；普通批量课不再重复灌入整个 Skill、全部参考文件和无关范例；自动生成的 Worker Spec 必须注明合同与适配器版本或哈希，不能由总控临场随意概括；
- 从 `domain-and-content-routing.md` 只解析当前课命中的领域规则与内容锚点，不为每个领域复制整套流程；
- 代表性样课、`strict` 档、来源歧义和真实争议才扩展读取其他完整规则；
- 每课使用干净任务上下文，但不要求用户手动创建对话。

具体读取矩阵见 `references/production-modes-and-budgets.md`。

### 5. 单次生成最终目标样式

写稿 Worker 只写本课临时目录，一次生成用户已确认样式的 `faithful.md` 与 `lecture.md`；不得先批量生成一种临时阅读风格，再整批重写成另一种风格。

- 所有档位输出 `uncertainties.json`；只登记真正影响专名、数字、事实或来源判断的差异，不把普通润色做成逐字台账；
- `fast` 与 `standard` 使用紧凑锚点覆盖，按人物、数字、关键案例、方法和限制条件回扫；
- `strict` 才要求逐块 `coverage.json` 和完整差异台账；
- 写完后的检查强度服从生产档位，不得把严格档要求偷偷叠加到快速档。

完成只代表 `DRAFTED`，不代表合格。字符比例只作异常预警，不能代替语义判断。

### 6. 机械检查

```bash
python3 scripts/validate_lesson.py \
  --profile <fast|standard|strict> \
  --source <原始稿> --faithful <忠实稿> --lecture <讲义> \
  --uncertainties <差异台账JSON> [--coverage <覆盖表JSON>] \
  --json-out <mechanical-report.json>
```

`strict` 必须提供覆盖表；`fast` 与 `standard` 可不提供。脚本只检查确定性风险，不能宣称语义忠实。

### 7. 语义判定与独立 QA 选择

所有课程都必须有模型语义判定；普通清洁课由写稿模型在同一工作任务内提交 `semantic_check.json`。命中以下任一条件时升级为不同上下文的独立 QA：

- 被当前保障模式的稳定抽样选中；
- `uncertainties.json` 有未解决项；
- 医疗、法律、财务、安全或真实操作后果；
- 多人关系、视觉证据、代码／命令或关键数字存在冲突；
- 机械检查出现语义风险警报；
- 模型、核心合同、批准样稿或适配器发生变化；
- 最近课程出现同类 `high`；
- 目标是外部正式使用。

`fast` 采用轻量证据并约 20% 稳定抽样，`standard` 采用标准证据并对关键课 100%、普通课约 50% 独立 QA，`strict` 使用完整证据并每课独立 QA。未命中者不创建 QA Worker。

只有命中核心质量合同“失败判定”的高严重度问题，才能进入 `FIX_REQUIRED`。措辞、格式和可优化表达登记为 `note`，不触发返工。来源或身份问题进入 `BLOCKED`；真实解释冲突或高风险歧义进入 `ESCALATED`。脚本、字符比例和文件存在都不能证明语义通过。

### 8. 一次返工封顶与定点复验

- 一般课最多一次定点返工；只修首轮 QA 明确指出的高严重度问题；
- 第二轮只向独立 QA 提交修改块、必要前后文和原问题列表，报告仍绑定完整成品 SHA-256；只复核这些问题是否修好，不重新全文挑刺；新发现的非高严重度问题记为 `note`；
- 修复后无高严重度问题即可交付并附 notes；
- 高严重度问题仍存在时停止循环，只允许强模型做一次来源/事实/原意裁决，禁止第三轮润色式返工；
- 连续多课出现同类错误时停止放量，修生产卡、样板或路由，不继续逐课修伤口。

不得因格式、措辞或台账补登启动新 Agent。预算和升级细则见 `references/production-modes-and-budgets.md` 与 `references/orchestration-and-model-routing.md`。

### 8.1 讲义通过后调用图解学习

保持原主状态链不变。`visual_learning.enabled=true` 时，本课到达 `SEMANTIC_QA_PASS` 后，唯一提交者先把已验收忠实稿与讲义提升到清单规定的正式路径，执行 `transition ... --to PROMOTED`。随后总控调用 `pinshu-visual-learning`，提供已验收讲义、正式双稿回链、待确认项、`paths` 输出及剩余预算；下游缺失或不能完成真实检查时停在图解未验收，不冒充通过。MD 是主阅读笔记，PNG 分模块内嵌，SVG 随资产保存，HTML 只是同源自包含辅助页。

在本课已为 `PROMOTED`、正式双稿真实存在后，用 `record-visual --state <state> --lesson <N> --report <visual-result.json> --artifact visual_md=<候选MD> --artifact visual_html=<候选HTML> --wall-minutes-used <实际耗时> --agent-calls <实际调用次数> [--tokens-used <实际Token>]` 登记真实图解结果和用量；候选图解的来源链接按正式图解目录解析到正式双稿。`blocked` 报告可登记但不能验收；只有没有可靠视觉来源时才允许有具体来源限制证据的 `skipped`。合同见 `references/semantic-qa-contract.md`。

`pass` 报告除四项布尔检查外，还必须登记按目标页面实测的 `mobile_evidence` 与由Agent或用户完成的整篇 `obsidian_evidence`。静态Markdown检查不能冒充Obsidian实读；手机内容列宽不写死351px，也不要求所有图改成同一种卡片构图。

新清单 `batch_approved=false`，只允许 `pilot_lesson_no` 样课图解。样课图解通过、唯一提交者提升且 `ACCEPTED` 后，用户亲眼批准才运行 `approve-visual-sample --state <state> --lesson <N> --approved-by <用户>`；它不替代原有 `approve-sample`。样稿变动即停止图解放量。不得重写旧状态来启用新扩展。

### 9. 单一写入者入库

只有 `SEMANTIC_QA_PASS` 的课可由唯一提交者提升到正式目录。提升前回读实际文件并保存路径到状态文件；提升后进入 `PROMOTED`。

随后由 `pinshu-course` 更新课程地图和横向资产。课程用途已启用学习扩展时，由 `pinshu-study` 按通用目录生成 `03_复习与训练/01_主动回忆卡` 与 `02_训练题库`；真实作答后才创建 `04_学习记录`。学习资产的人读正文与逐项机器元数据必须分离，代表性文件必须在目标阅读界面真实验收。图解启用且报告为 `pass` 时，提交者按 `paths` 提升 `official_visual_md`、`official_visual_html` 及同相对结构的 PNG／SVG，再用 `transition ... --to ACCEPTED --artifact official_visual_md=<正式MD> --artifact official_visual_html=<正式HTML>` 提交；脚本验证候选、正式文件、讲义和资产哈希，以及报告中的四项检查声明；真实内容审读与渲染由下游执行，不由脚本替代。来源受限的 `skipped` 保留解释，不称已交付图解。状态、正式文件和课程地图一致后进入 `ACCEPTED`。初稿 Worker、QA Worker均不得直接改正式课程地图。

#### 9.1 命名与路径由 manifest 驱动

开工前在 manifest 中定义一次命名模板与三层路径模板，先运行 `paths` 命令生成并核对目标路径；禁止逐课手工登记不同格式。已有课程沿用课程地图和现有命名，不硬套全局文件名。

#### 9.2 改名或返工不得留下双份正式文件

新文件提升成功后，将旧名或旧版移入废纸篓，不做彻底删除。交付前程序对账：目录无未登记残留，状态机路径真实存在，Frontmatter 链接可解析，正式正文与已验收车间正文一致。

## 状态与恢复

主状态：

`DISCOVERED → CAPTURED → SOURCE_VERIFIED → DRAFTED → MECHANICAL_PASS → SEMANTIC_QA_PASS → PROMOTED → ACCEPTED`

异常状态：`FIX_REQUIRED`、`ESCALATED`、`BLOCKED`、`SKIPPED`。

常用命令：

```bash
python3 scripts/course_pipeline.py agreement --state <course-state.json>
python3 scripts/course_pipeline.py paths --state <course-state.json> --lesson <N>
python3 scripts/course_pipeline.py next --state <course-state.json>
python3 scripts/course_pipeline.py preflight --state <course-state.json> --lesson <N>
python3 scripts/course_pipeline.py self-rework --state <course-state.json> --lesson <N> --reason <说明> --artifact faithful=<修订稿> --wall-minutes-used <实际耗时>
python3 scripts/course_pipeline.py transition --state <course-state.json> --lesson <N> --to <STATE> --reason <说明> --wall-minutes-used <本次耗时> [--tokens-used <本次Token>]
python3 scripts/course_pipeline.py audit --state <course-state.json>
python3 scripts/course_pipeline.py summary --state <course-state.json>
```

状态写入必须原子化；中断后以状态文件和真实产物为准，不以聊天摘要为准。

预算超限时，命令会先登记本次真实用量，再把课程置为 `BLOCKED` 并返回事件ID。用户批准调整后执行：

```bash
python3 scripts/course_pipeline.py set-budget --state <state> --lesson <N> --key <预算键> --value <新上限> --reason <批准依据>
python3 scripts/course_pipeline.py resume-budget --state <state> --lesson <N> --event-id <事件ID> --reason <恢复依据>
```

随后原样重试被阻塞的命令；已登记的那次用量不会重复累计。禁止手改state或填0绕过。

`preflight` 从当前真实文件生成机械报告和 SHA-256 绑定，只判断确定性事项，不宣称语义通过。写稿者在首轮独立 QA 前发现遗漏时，使用 `self-rework` 合法回到 `DRAFTED`；它记录前后哈希、原因、次数和 `rework` 分相用量，不伪造 `FIX_REQUIRED`，也不消耗 QA 轮次。

已 `ACCEPTED` 的课程需要修复回链、图解、元数据、排版或内容时，先执行 `revision-open --type metadata_link_only|formatting|content`。它会把旧正式文件、绑定报告、图源、课程地图和状态复制到 `revisions/lesson-N/rX/`，课程保持 `ACCEPTED` 但审计明确标记修订未关闭；样课旧批准失效。`metadata_link_only` 由流水线比较可见正文，`formatting` 由流水线计算语义指纹，正文发生变化时必须附独立 QA，`content` 始终必须附绑定修订后四项输入哈希的独立 QA。最后执行：

```bash
python3 scripts/course_pipeline.py revision-close --state <state> --lesson <N> \
  --report <revision-report.json> [--qa-report <qa-report.json>] \
  --wall-minutes-used <实际耗时>
```

不得覆盖正式文件后手改 state，也不得让 `revision_report` 自报的布尔值代替流水线计算和独立 QA。

## 放量规则

测试流程与正式生产必须完全相同：相同主模型、QA模型、工作包、规则、脚本和入库路径。

- 新课程或新模型先跑代表性样本；
- 样本通过后小批运行；
- 小批无共同偏差后再扩大；
- 连续出现同类内容错误时暂停新任务，先修最早导致偏差的规范、工作包或路由。

并行只用于相互独立的临时课次。原文采集可按浏览器稳定性串行；写稿和QA可有限并行；正式入库和地图更新必须串行。

## 完成定义

“全部完成”必须同时满足：

- 所有课为 `ACCEPTED`、有理由的 `SKIPPED`，或明确报告的 `BLOCKED`；
- 原始转写、忠实精编稿和结构化讲义真实存在并通过回读；
- 课程地图中恰有一个对应条目，状态一致且链接可解析；
- 成品目录无未登记残留，命名统一，Frontmatter 引用 0 断链；
- manifest 已记录课程用途和学习扩展判断依据；已启用时，复习与训练内容、独立后台索引和目标界面渲染验收一致；未启用时不要求对应文件或目录；真实学习未发生时不要求 `04_学习记录`；外部使用未启用时不要求外部核验记录；
- 图解学习启用时，真实图解结果报告、讲义与成品哈希、逐模块 PNG、SVG 图源、MD 主笔记与 HTML 辅助页一致；桌面、手机和 Obsidian 必须真实检查，未检查保持未通过。无可靠视觉来源则逐课保留具体跳过证据；旧课程未启用不受此项影响；
- 未解决的 STT、事实和来源问题单独列出；
- 报告实际模型、Agent调用、Token、墙钟、返工、升级、阻塞和未修改范围。

不得把“已提取”“已生成”“机械检查通过”和“正式验收通过”混为一谈。

## 结项清理（仅在用户明确要求后）

课程全部 `ACCEPTED` 后，先保留正式成品、原始来源、待确认项、状态文件和成品 SHA-256 基线。临时草稿和机械报告只有在用户要求清理时才可通过 `archive-artifact` 登记为已归档，再移入废纸篓。

归档命令只允许处理已验收课程的可再生临时稿和机械报告，必须核对真实 SHA-256；原始来源、正式双稿、覆盖证据、待确认台账和语义 QA 报告不得借 `artifacts_archived` 绕过审计。

## 直接资源

- 采集：`references/capture-adapter-contract.md`、`references/baidu-capture-adapter.md`、`references/quark-capture-adapter.md`、`references/aliyun-capture-adapter.md`；
- 质量、领域和外部使用：`references/core-quality-contract.md`、`references/domain-and-content-routing.md`、`references/external-use-gate.md`；
- QA、模型与预算：`references/semantic-qa-contract.md`、`references/orchestration-and-model-routing.md`、`references/production-modes-and-budgets.md`；
- 清单与工作包：`templates/course-manifest.example.json`、`templates/lesson-work-order.md`、`templates/qa-report.example.json`；
- 状态与机械检查：`scripts/course_pipeline.py`、`scripts/validate_lesson.py`；
- 统一入口触发回归：`scripts/trigger_test.py`。
- 同事快速开始与旧项目迁移：`QUICKSTART.zh-CN.md`；
- 来源与发布基线：`PROVENANCE.md`；
- 发布前一键验收：`scripts/release_check.py`。
