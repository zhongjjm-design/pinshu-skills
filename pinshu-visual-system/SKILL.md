---
name: pinshu-visual-system
description: "为文章配图、公众号封面、小红书及小绿书图组、海报和故事场景选择画法并制作图片。根据内容和平台统一选择内置模式或已安装外部Skill；支持中文短名。Use for article illustrations, covers, social graphics, posters and source-faithful visual storytelling."
---

# 品叔视觉系统

版本：1.0.0-rc.2，已公开的试用候选。作者：Aidan（品叔）；实现：Codex。无私有身份、账号、参考图片或生产提示词。

## 直接开始

用户只需给内容和用途，例如“给这篇文章配图，发公众号”。想指定时可说“用手帐”“用柔和体积”“用怪诞”。英文ID留给程序处理。

1. **读内容、定职责。** 读用户指定的完整版本，明确封面吸引、正文解释/场景/证据、知识卡交付信息或海报促成行动。公众号正文优先轻巧横图；小红书/小绿书竖页独立编排。尺寸读`references/platform-profiles.json`，结构读注册表。
2. **统一选表达。** 运行`python3 scripts/select_styles.py --platform <平台ID> --structure <结构ID>`，从兼容选项结合原文判断2—3种有实质差别的方向并推荐。短名映射、状态和边界只读注册表。用户已授权系列制作时直接推进，不逐张重复确认。颜色、物件和场景从内容选择，不被参考题材或画风名字锁死。
3. **编译并执行。** 内置模式完整读其卡，用`visual_compiler.py --mode <中文短名或ID>`绑定原文与图意。将完整prompt-final实际交给生图工具，附加要求另记；提交前以`verify_generation_input.py`核本次请求JSON中的prompt没有缩掉源文或模式卡。外部选项读`references/external-handoff.md`，加载其真实已安装完整Skill并回交结果；缺依赖就明确报告和提供内置替代。程序图/精确文字需要可编辑层时读`references/editable-rendering.md`。固定角色只用用户本次授权的身份参考，见`references/character-profiles.md`。
4. **实际出图和审看。** 用当前Agent真正可调用的生图工具；无工具标“待生图”，交可继续执行的计划，不报成图片。实际检查原图、手机尺度与裁切：图能否自证含义、文字是否有用、动作和设备是否合理、是否值得读者保留。封面与真实标题同屏比较；整篇检查相邻图的节奏和协调。步骤、判断和阈值逐项对应原文；原文中构成含义的参与者、动作和连接关系逐项核对，画错即返修，不以尺寸或文件生成成功代替。
5. **交付并修正。** 按`references/visual-qa.md`核验最终尺寸图，再按`references/quickstart.md`导出、净化和交付。图片、原图、可编辑源、计划、实际引擎与未通过项分别记录。确认图保留；单图返修只影响对应图，与当前最好版本比较。将“保留什么、改什么”记在当前项目任务里，后续选用回查。

## 能力和依赖

25个内置绘画模式与6个外部画法/版式交接入口由注册表统一维护；暂缓方向不出现在推荐中。外部工具不是捆绑安装，也不是额外6种内置生图引擎。解释其缺件或许可限制，但不要求用户记住Skill名。

计划使用Python标准库。生图使用Agent自身能力，本包不带模型或密钥；导出使用ImageMagick7。先运行`python3 scripts/doctor.py`：Python低于3.10退出1；退出0仅表示规划最低版本满足，导出和整篇依赖另列。具体安装见README。准备包、真实图片、用户接受与发布许可分别判断。

需要内容关系精确图时优先读取已安装的pinshu-infographic或pinshu-business-graphics；需要同篇配图时保持全篇外观一致但按每张职责选择图形语法。公开包不含任何私人身份或客户材料，用户自带素材留在本次项目中。

## 按任务读取的资源

- 截图、实拍、程序图与排版交接：`references/article-asset-handoff.md`。
- 商业关系图：`references/business-graphics.md`。
- 安装或核对Agent实际能力：`references/compatibility.md`。
- 明确研究文化海报方法：`references/method-candidates.md`。
- 明确研究文化海报方法时：`references/method-cards/oriental-colorfield-landscape.md`、`references/method-cards/oriental-material-craft.md`。
- 选定对应画法时，完整读卡：`references/mode-cards/airy-architectural-watercolor.md`、`references/mode-cards/archive-tabletop-editorial.md`、`references/mode-cards/chalk-scene-explainer.md`、`references/mode-cards/character-presenter.md`、`references/mode-cards/clear-portrait-doodle-collage.md`、`references/mode-cards/cut-paper-print-editorial.md`、`references/mode-cards/fine-line-etching-editorial.md`、`references/mode-cards/folded-paper-editorial.md`、`references/mode-cards/graphite-accent-editorial.md`、`references/mode-cards/hand-drawn-comparison-comic.md`、`references/mode-cards/handcrafted-puppet-narrative.md`、`references/mode-cards/light-relief-poetic.md`、`references/mode-cards/literary-crayon-editorial.md`、`references/mode-cards/notebook-knowledge-explainer.md`、`references/mode-cards/oil-pastel-scene.md`、`references/mode-cards/pale-lacquer-decorative.md`、`references/mode-cards/paper-scene-collage.md`、`references/mode-cards/pixelated-scene-editorial.md`、`references/mode-cards/pop-halftone-narrative.md`、`references/mode-cards/soft-volume-editorial.md`、`references/mode-cards/stitched-textile-collage.md`、`references/mode-cards/two-color-risograph.md`、`references/mode-cards/vintage-painted-editorial.md`、`references/mode-cards/warm-paper.md`、`references/mode-cards/warm-studio-illustration.md`。
- 处理正式待发正文及物料包：`references/ready-folder-contract.md`。
- 对外分享或打包：`references/sharing-boundary.md`。
- 选用、短名和状态判断：`references/system-registry.json`。
- 新参考图拆解和反馈回流：`references/visual-evolution.md`。
- 整篇图片制作：`references/workflow.md`。
