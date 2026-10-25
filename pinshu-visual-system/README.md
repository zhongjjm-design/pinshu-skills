# 品叔视觉系统 · 1.0候选版

这是已公开的1.0.0-rc.2试用候选，不是稳定版1.0。内含25种通用绘画模式、中文短名和6个外部交接入口。源码基于公开0.4.0，新增媒介说明为独立编写，不携带私人样图、客户原文、身份参考或私有提示词。

## 安装

做单张图时，将整个`pinshu-visual-system`文件夹放进所用Agent实际支持的Skills目录；整篇公众号流程同时安装本候选套件中沿用公开排版代码的`pinshu-wechat-layout`，重新加载该Agent，再确认其能读取本目录的SKILL.md。已有同名私有版或自改版先保留，使用独立测试目录验证，不能直接覆盖。

ZCode、WorkBuddy、Hermes的安装位置与生图能力以各自运行时为准；本候选目前不宣称这三者完整出图均已验证。Agent能看图片不等于能生成图片。

## 使用

“给这篇文章配图，发公众号”；“用手帐做知识图”；“用柔和体积做一组场景图”。中文短名与具体用途见`references/system-registry.json`。Agent按SKILL.md统一选用，外部包已装时加载其完整入口，否则说明缺依赖并提供内置选择。

先运行`python3 scripts/doctor.py`。规划只需Python3.10+；出图需Agent真实生图能力；平台导出需ImageMagick7。整篇流水线另需Pillow、markdown-it-py、beautifulsoup4，doctor会检查这些依赖；只做计划不需要它们。排版依赖安装方法见其随包requirements.txt。详细出图、可编辑文字和发布净化命令见`references/quickstart.md`。

## 本候选需要验证

跨目录清洁安装、全部中文短名、平台和人物边界、外部依赖缺失/可读交接、原文绑定、真实出图及导出。技术测试不代替审美和实际用户接受。最终发布待维护者审核具体文件与提交后决定。


## 环境检查和测试

在视觉Skill目录执行以下命令，Python需3.10以上：

python3 scripts/doctor.py

退出0表示最低Python满足、可以规划；Python低于3.10时planning_ready为false、退出1。ImageMagick7用于导出/净化；Pillow、markdown-it-py、beautifulsoup4及同套件的排版组件用于整篇流程，doctor分别列出，缺这些不把最低Python的失败掩盖成成功。

普通用户的包内自包含测试：

python3 -B -m unittest discover -s tests -v

当前39项；使用包内文件和临时夹具，不需要pinshu-write、Node/linkedom、浏览器、模型或密钥。测试中涉及真实PNG导出，需已安装ImageMagick7和requirements.txt的Python依赖。这里的“自包含”指无需另一个Skill或维护者私有夹具，不是捆绑所有系统依赖。

可选的文章回归（7个scripts/test_*.py，共81项）：

python3 -B -m unittest discover -s scripts -p 'test_*.py' -v

干净解包、未提供写稿导出器及Node/linkedom时，会明确跳过依赖它们的测试；本机本轮81项中72通过、9跳过、0失败。跳过表示该链路未验证，不能写成81项全链路通过。缺少其他基础依赖时先按requirements.txt准备环境，不能把导入失败算作跳过。

维护者完整81项另需：
- 同级pinshu-write/scripts/export_article.py：与目标公开版本匹配的只读公开导出器夹具；不是私有写稿Skill整包。
- 同级pinshu-wechat-layout：本套件已附。
- Node与linkedom（本轮已有测试环境为0.18.12），NODE_PATH可指向维护者既有node_modules。
- requirements.txt里的依赖及ImageMagick7。

先核公开导出器文件存在、node能require('linkedom')，再设CI=true运行上述文章命令；完整集成记录须81通过、0跳过、0失败。CI仅强制DOM依赖，维护者仍要核对导出器及最终计数。无需安装或修改现用写稿Skill来跑本套件核心测试。
