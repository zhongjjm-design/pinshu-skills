---
name: pinshu-course
description: "用于多节课程持续整理、学习、训练、课程地图、跨课归并、断点恢复和验收后修订；English keywords: course archive, multi-lesson course, course map, cross-course synthesis, learning assets."
---

# 品叔系列课程编排

## 来源与维护

- 原创身份：品叔原创（original）
- 原创归属与维护：Aidan（品叔）
- 内容能力：`pinshu-transcript`、`pinshu-distill`、`pinshu-study`、`pinshu-content-assets`
- 分发状态：公开候选；不声明正式发布、tag、CI 通过或外部安装验证

把多节课程建设成可追溯、可学习、可持续更新的课程资产库。本Skill负责课程身份、范围、进度、并发、断点、待归并知识线索和正式提升，不替代四个内容Skill。

正式验收后的改动统一交给 `pinshu-course-capture` 的 revision 生命周期；本 Skill 不通过重绑哈希、补写历史或直接覆盖正式稿来“修正状态”。课程地图是全课共享且持续更新的单一文件，审计使用共享最新基线，不把早期课次保存的旧地图哈希误判为文件损坏。

## 每门课的共同底座

不再按“学习型/内容型”降低基础产物。每课固定形成原始转写、忠实精编稿、结构化讲义和课程地图条目；项目初始化时先判断课程用途，系统学习、训练营、认证和备考型课程默认启用复习与训练内容，其他扩展按真实用途启用。

## 系列能力的分工

```text
pinshu-course-capture：采集不可变原始转写并编排逐课生产
pinshu-transcript：原始转写 → 忠实精编稿
pinshu-distill：忠实精编稿 → 结构化讲义
pinshu-visual-learning：语义已验收讲义 → MD图解学习笔记、分模块PNG、SVG图源和同源HTML辅助页（属于本轮 14 项候选；仅在课程清单显式启用且依赖完整时调用，否则记录依赖阻塞）
pinshu-course：更新课程地图、状态、断点和跨课资产
pinshu-study：为已启用学习用途的课程生成复习与训练内容，并在真实学习后保存记录
pinshu-content-assets：逐课捕捉传播候选，模块或完课后形成带来源与风险状态的传播母资产
```

忠实精编稿是所有下游学习资产的内容母本；原始音视频和原始转写是最终证据。下游遇到口诀、数字、安全、个案和分歧时回查忠实稿，忠实稿有疑问时回到原始证据。

## 课程用途判断

初始化课程时，根据课程名称、结构、内容和用户目标记录用途与依据。资料、访谈、观点和内容资产型课程默认停在四项底座；系统学习、专业基础、训练营、认证和备考型课程默认启用 `03_复习与训练`，用户明确排除时才关闭；证据不足或用途冲突时说明推荐方案并询问，不能静默把学习扩展设为 `false`。领域名称只能提供线索，不能代替用途判断。

学习内容与学习证据分开：系统可以生成主动回忆卡与训练题库；`04_学习记录` 只有在真实作答后才出现。

## 课程身份闸门

每门课程绑定：课程ID、讲师、期次、唯一正式写入根目录和权威来源。当前会话身份高于相似课号、旧摘要、旧Todo和跨会话搜索。

出现另一讲师、另一课程、节次冲突、来源截断或目标路径离开写入根目录时暂停，不生成任何稿件。详见 `references/multi-conversation-course-identity-gate.md`。

## 状态闸门

- **收集态**：继续接收逐字稿、图片和反馈，不写稿；
- **讨论态**：比较方案和样例，不写正式成果；
- **执行态**：用户明确确认后执行已约定范围；
- **系列持续授权**：仅绑定当前课程、目录和已约定产物；身份、目录或规则变化时失效。

素材归属不清时使用 `references/lesson-asset-attribution-and-recovery.md`。用户已明确节次和素材归属时不重复确认。

## 最小目录

**已有课程先读 `00_课程地图.md`，再检查现有目录与同类文件；实际结构高于下面的示例。**同一功能已经存在时沿用原目录和编号，不得因为示例编号不同而新建重复栏目。

仅当这是一门完全没有既有结构的新课程时，才参考以下骨架，并根据该库的编号规则落位：

```text
课程根目录/
├── 00_课程地图.md
├── 原始资料/
├── 忠实精编稿/
├── 结构化讲义/
├── 03_复习与训练/               # 判定为学习用途时才建
│   ├── 01_主动回忆卡/
│   └── 02_训练题库/
├── 04_学习记录/                 # 真实学习发生后才建
│   ├── 00_学习进度.md
│   ├── 01_训练记录/
│   └── 02_错题与复测.md
├── 传播资产/                     # 明确启用且已有内容时才建，名称沿用现有同义栏目
├── assets/                      # 有视觉材料时才建
└── 生产控制/                     # 运行流水线时才建
```

课程地图必须用自然语言说明“先读讲义→主动回忆→训练→查看记录→复测”，并显示当前状态与下一步。目录和模板使用“学习者”“用户”“学习记录”等通用名称，不把 Aidan、品叔或其他个人姓名写入通用运行结构。

复习与训练内容只在用途成立时创建，学习记录只在真实活动后创建，不预建空目录。正式知识成果优先按专家归档；原始采集区和正式知识归属分开。创建任何目录前必须确认库内不存在同义栏目。

## 逐课基础流程

1. 核对课程身份、课次、来源和目标路径；
2. 保存并验证不可变原始转写；
3. 由一个写稿者一次完成忠实精编稿与结构化讲义；
4. 运行确定性脚本；
5. 完成模型语义判定；
6. 仅命中风险触发器或自适应抽样时运行独立 QA；
7. 讲义语义通过后，清单启用图解时由 `pinshu-course-capture` 调用 `pinshu-visual-learning`，先做图解样课、用户批准后才放量；旧清单缺配置不补产。MD 为主、逐模块 PNG 内嵌、SVG 可编辑、HTML 同源自包含辅助；无可靠视觉来源逐课说明具体限制。唯一提交者提升双稿与已通过图解并幂等更新课程地图，图解结果合同满足才进入最终验收；
8. 课程用途启用学习扩展时，调用 `pinshu-study` 生成 `03_复习与训练/01_主动回忆卡` 与 `02_训练题库`；
9. 真实作答发生后，再建立 `04_学习记录`，保存进度、训练记录、错题与复测；
10. 明确启用传播用途时，调用 `pinshu-content-assets`：逐课在后台捕捉有增量的候选；需要传播成果时，按已完成课次交付标明范围的编号化内容资产，完课后再做课程级归并。候选与母资产不作为默认交付终点；
11. 模块结束后按需生成横向专题、模块综合卡或混合训练。

待归并知识线索是材料收集篮，不是正式学习文章。每条必须标为“本课候选、后课伏笔、跨课已验证、安全治理候选”之一；只有“跨课已验证”必须给出已读取的第二来源。课程地图只显示简明中文摘要。详细规则读取 `references/跨课线索与独立QA规则.md`。

## 每课核心结果合同

每课必须完成四项核心结果：

1. 不可变原始转写；
2. 忠实精编稿；
3. 结构化讲义；
4. `00_课程地图.md` 中唯一、可更新、不重复的本课条目。

前三项是文件，第四项是共享课程地图中的幂等条目，不要求每课另建一份地图文件。学习扩展由课程用途判断：系统学习、训练营、认证和备考型课程默认生成复习与训练内容；其他课程按需启用。是否启用扩展不得影响四项核心结果的质量或基础验收。没有真实作答时只能标记“未开始”，不能伪造学习进度或掌握状态。

历史试点只用于验证规则和记录失败教训，不构成新课程的生产闸门。

## 内容资产型逐课流程

1. 忠实精编稿；
2. 系统化讲义；
3. 课程地图；
4. 明确启用传播用途时，由 `pinshu-content-assets` 捕捉有增量的逐课候选；没有合格候选时记录“本课无足够独立传播增量”，不为填字段生成金句或平台文案；
5. 每3—5课或模块结束，分别归并知识资产与传播候选；传播层去重、核验和母资产不写回忠实稿或讲义正文。

课程地图只保留传播层入口、覆盖范围、待核验数量和聚合状态，不承载传播正文。历史课程正文已有传播字段时保留，不批量迁移；再次使用时再按需纳入独立传播层。兼容规则读取 `references/course-to-social-content-reuse.md`。

## 逐字稿完成后：先分流，不让课程躺在库里

整理完成不是课程任务的终点。根据用户真实目的，路由到以下一种或多种结果：

- **理解**：结构化讲义、概念关系与横向专题；
- **掌握**：主动回忆、追问、错因、回源与复测；
- **讲述**：费曼式讲给别人听、听众追问、暴露漏洞、修正后再讲；
- **应用**：把方法迁移到一个真实项目，形成假设、动作、指标和复盘；
- **传播**：调用 `pinshu-content-assets` 形成可直接使用的观点、选题与内容任务卡，交付编号化内容资产包；候选与母资产作为后台记录。平台成品交给配置的下游工作流，不把老师观点复述成听课作业；
- **资产化**：把经过真实使用验证的方法沉淀为案例、SOP、Skill或产品。

不要默认六路全做。先判断用户现在要“读懂、记住、讲清、用上、发表还是产品化”，再调用对应 Skill。完整规则读取 `references/课程完成后的学习传播与应用闭环.md`。

## 单写者与状态

每课默认只有一个内容写稿者，同时生成忠实精编稿与结构化讲义；不得安排多个写稿者重复产出同一课。采集器、确定性脚本、独立 QA 和正式提交者不是第二写稿者。普通清洁课完成一次生成、机械检查和写稿模型语义自检后，可以直接提升；只有命中风险触发器或自适应抽样时才启动独立 QA。

正式课程库仍只有唯一提交者写入。子Agent只在独占临时目录起草；状态只能按真实证据推进。子Agent自报、文件存在和脚本 PASS 都不是内容验收；“全部、无遗漏、无复合、独立可学”等强声明必须有反向证据。

并发规则见 `references/concurrent-course-write-safety.md`；写入和回读见 `references/approved-course-file-write-and-readback.md`。

## 按场景读取参考

### 输入、边界与恢复

- 长系列基础：`references/long-course-series-workflow.md`
- 忠实稿先于讲义：`references/transcript-first-dual-deliverable-order.md`
- 纯文本高速处理：`references/pure-text-high-throughput-lesson-processing.md`
- 超长单课分块：`references/long-lesson-chunked-write-map-and-sequence-qa.md`
- 录制倒序与重叠：`references/mixed-recording-order-and-overlap-dedup.md`
- 重复播放与术语权威：`references/repeated-playback-transcript-dedup-and-term-authority.md`
- 多课直播与销售噪声：`references/multi-lesson-live-transcript-boundary-and-sales-noise.md`
- 跳号课程：`references/non-contiguous-lesson-ingestion-and-map-state.md`
- 补齐缺课并收官：`references/late-gap-closure-and-module-finalization.md`
- 中断恢复：`references/resume-interrupted-batch-course-work.md`

### 术语、视觉与关系

- 术语确认传播：`references/term-confirmation-propagation-and-zero-residual-qa.md`
- 截图提示词与反转纠正：`references/screenshot-prompt-recovery-and-reversal-corrections.md`
- 配套PPT与图片：`references/companion-course-materials-and-visual-references.md`
- 多图摄取：`references/multi-image-ingestion-and-final-verification.md`
- 角色与缺图：`references/relational-consistency-and-missing-visuals.md`
- 素材归属恢复：`references/lesson-asset-attribution-and-recovery.md`

### 双稿与QA

- 课程图文融合与执行批准：`references/transcript-visual-integration-and-approval-gates.md`
- 价值优先交付与学习／传播分层：`references/value-first-course-delivery-and-propagation.md`
- 语义忠实与批量QA：`references/semantic-fidelity-and-batch-qa.md`
- 两轮独立精编：`references/two-pass-faithful-editing-and-output-containment.md`
- 双稿覆盖与提升：`references/dual-draft-semantic-coverage-and-promotion-qa.md`
- 同名双稿与权限：`references/same-name-dual-draft-preview-and-permission-aware-qa.md`
- 系统讲义来源与反向覆盖：`references/systemized-lecture-provenance-and-reverse-coverage.md`
- 长课阅读性：`references/readability-first-long-course-markdown.md`
- 标题空行与迟到Agent：`references/markdown-spacing-and-late-agent-output-control.md`

### 特殊课程内容

- 模块入口与不可逆顺序：`references/module-entry-and-irreversible-framework-lessons.md`
- 高密度平台课：`references/high-density-platform-course-processing.md`
- 关系与公共议题：`references/relationship-group-public-issue-course-processing.md`
- 人设与定位：`references/identity-and-persona-course-processing.md`
- 类型、风格与生长定位：`references/type-style-and-growth-positioning-course-processing.md`
- 视频制作技术课：`references/video-production-course-technical-normalization-and-qa.md`
- AI课程模块收官：`references/module-closure-package-and-ai-course-normalization.md`
- 产品营销与风险：`references/product-marketing-course-risk-and-module-closure.md`
- 私域与合规：`references/private-domain-course-compliance-and-permission.md`

### 横向、归档与交付

- 专业课程学习资产流水线：`references/专业课程学习资产流水线.md`
- 课程完成后的学习、讲述、应用与资产化：`references/课程完成后的学习传播与应用闭环.md`
- 跨课总纲与模型库：`references/cross-course-horizontal-synthesis.md`
- 横向库最终QA：`references/horizontal-knowledge-base-final-qa.md`
- 模块收官资产：`references/module-closure-package-and-ai-course-normalization.md`
- 课程传播资产兼容与分流：`references/course-to-social-content-reuse.md`
- 正式打包与清理：`references/formal-course-packaging-and-cleanup.md`
- 多活动归档分类：`references/multi-event-course-archive-taxonomy-and-safe-move.md`

### 音视频摄取

- Apple Silicon批量转写：`references/apple-silicon-batch-course-transcription.md`
- 多课程音频分流：`references/audio-course-ingestion-and-series-separation.md`

## 课程标题价值合同

课程目录负责表达稿件类型，文件名与 H1 负责表达本课内容。若上级目录已经是“原始转写、忠实精编稿、校对精编稿、结构化讲义”等类型目录，文件名和 H1 禁止再次出现“逐字稿、忠实精编稿、校对精编稿、结构化讲义、清洗稿、整理稿、阅读版、完整版、总稿”等类型词；稿件类型只保留在目录与 Frontmatter。

标题必须在完整读课后确定，以“必要课次＋题眼”为基本结构。题眼优先提炼本课的主问题、核心判断，以及最有辨识度的案例、方法或结果；每个短语都必须贡献新的内容信息。课程名、日期、版本、稿件状态等已有其他位置承载的信息，不得挤占标题展示长度。

标题验收不能只查格式一致，必须回答三个问题：

1. 隐去目录和正文，只看标题，能否知道本课主要讲什么；
2. 能否看出它与相邻课的区别，以及为什么值得打开；
3. 删除任一短语后是否损失内容信息；若不损失，该短语就是冗余。

文件名、H1、Frontmatter `title` 应共享同一题眼，但不要求机械复制全部元数据。无法通过上述验收时，保持待命名状态，不得用“第X课＋精编稿／讲义”占位晋升。

## 最终QA

图解启用时，按 `pinshu-course-capture` 的图解结果合同核对讲义／MD／HTML／PNG／SVG哈希和真实语义、桌面、手机、Obsidian检查；地图加入图解笔记与辅助页入口，明确跳过或阻塞理由，不用报告替代实读。四项核心结果始终核对：课程身份、节次、来源与原始转写完整性、忠实稿和讲义分离、标题题眼与 Frontmatter、语义覆盖、术语残留、图片链接、待确认、安全边界、课程地图唯一条目和链接可解析。学习用途启用时还要检查：主动回忆卡与训练题不大量重复；正文没有 `%%`、HTML、逐项 ID 或工程字段；Frontmatter 只含少量文件级属性；卡片和题库分别使用独立后台索引且类型、数量、顺序与正文一致。传播用途启用时只检查课程地图入口与状态，传播候选、来源锚点、核验和风险由 `pinshu-content-assets` 的独立验证器负责。代表性文件必须在目标阅读界面真实打开检查属性区、折叠答案、手机阅读和代码泄漏；脚本 PASS 不代替渲染验收。卡片、训练、待归并线索、正式专题和传播资产只在启用时检查。

机械验证可运行 `scripts/validate-course-markdown.py`；已启用的讲义、卡片、题库和线索可运行 `scripts/validate-learning-assets.py --kind lecture|cards|questions|clues <paths>`；传播资产只查后台时运行 `pinshu-content-assets/scripts/validate-propagation-assets.py <registry.json>`；验收默认完整内容资产交付时必须使用 `--profile full-delivery --project-root <课程或项目根目录> <后台注册表.json> <最终资产包清单.json>`，并实际阅读成品确认可直接使用。下游路由未配置只阻止继续交接，不阻止在已批准的项目位置交付本地内容资产。学习资产验证器不要求金句、传播观点、用户连接点或朋友圈字段。脚本只能证明结构、计数与路径，不能替代模型语义判定或目标阅读界面的真实渲染验收；独立 QA 只在触发或抽样时启动。

## 放量门槛

批量生产前先验证代表性样课的版式、详略、忠实稿、讲义和课程地图入口。病案／例盘、强视觉／实操、关键数字与高后果内容命中风险触发器时做独立 QA；普通课按保障模式自适应抽样。主动回忆和真实“带学→回忆→追问→回源→记录”只在启用学习扩展时验收，不是基础生产或课程地图更新的前置条件。
