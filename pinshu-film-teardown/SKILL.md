---
name: pinshu-film-teardown
description: "把一支品牌片（TVC、周年片、广告片）做成 4 分钟左右的拆解解读视频：原片真实画面加 AI 旁白、当事人原声、代码动画和配乐，横版发视频号、竖版发抖音，带封面和体检。用于“品牌片拆解”“TVC 拆解”“周年片拆解”“把这支广告片做成拆解视频”“给这篇品牌案例文章配视频”。"
---

## 来源与维护

- 原创身份：品叔原创（original）
- 原创归属：Aidan（品叔）
- 维护者：Aidan（品叔）
- 上游依赖：`pinshu-video-core`（品叔视频公共底座，品叔原创；2026-10-07 起配音、局部放慢、配乐对齐、渲染、混音、体检、环境检查这几步的代码在那里，本 Skill 的同名脚本只做转接，必须和本 Skill 并排装在 `~/.agents/skills/`，或用 `PINSHU_VIDEO_CORE` 指明位置）；HyperFrames（https://github.com/heygen-com/hyperframes，Apache-2.0，渲染；它自带的音效来自 Pixabay，Pixabay Content License，可商用、不用署名）；GSAP（https://gsap.com，标准免费许可，网页里从 CDN 加载）；BaoCut（https://github.com/JimLiu/baocut，MIT，中文转写取逐字时间）；Gemini TTS（Google 接口，各人用自己的钥匙）；Demucs（https://github.com/adefossez/demucs，MIT，可选，人声分离）；FFmpeg；librosa（ISC）；思源宋体（Adobe，SIL OFL 1.1，建项目时下载）；冬青黑体为 macOS 系统字体，不随 Skill 分发（Linux 装 Noto Sans CJK SC 代替）
- 原创能力：品牌片拆解这一片种的整套做法：按真实发音锚定字幕和切镜、优先整篇一次合成配音并在长旁白尾段漂移时只重生成漂移尾段、原片剪辑点报警、配乐收尾和弦落在片尾卡、横竖两版和封面、独立审片循环和体检，以及 2026-09 到 10 月做好想来 16 周年拆解时攒下的全部规矩和坑
- 分发状态：公开候选；不声明正式发布、tag、CI 通过或外部安装验证
- 首条成片：好想来 16 周年 TVC 拆解（2026-10-02 发布到首席品牌官视频号）

# 品叔品牌片拆解视频

把一支品牌片做成"同行拆案例"式的解读视频。产出：横版成片（视频号）、竖版成片（抖音）、横竖两张封面、发布文案、体检报告和审片台账。

**一条片子 = 项目文件夹（原片、配音、素材）+ `spec.py`（这条片子讲什么）+ 本 Skill（怎么做）。** 换品牌只改 `spec.py` 和素材，不改脚本。

## 开工前

1. **先读 `references/rules.md` 全文。** 那是 Aidan 定下的现行规矩，审片和体检都按它判。
2. 问清三件事：发哪个号（读那个号的画像）、配哪篇文章、原片最高清的版本在哪（客户有原片先要原片；HEVC 先转 H.264）。
3. 跑环境检查，缺什么先补：`python3 scripts/doctor.py`。整条线用同一个装齐 numpy、soundfile、pillow、librosa 的 Python；本轮文档修复不声明这些脚本已经执行通过。

## 流程：十步，三个停下来等人的点

| 步 | 做什么 | 命令 | 停 |
|---|---|---|---|
| 1 建项目 | 建目录，备齐原片、音效、字体、配置模板 | `new_project.py <项目> --film <原片>` | |
| 2 拉片 | 原片每格 1 秒的总览图，按人头列清单；记下每个故事、每个人、每段当事人原声在哪几秒；量原片自带字幕在画面哪个高度、角标在哪个角，填进 `spec.py` 的 `FRAME` | ffmpeg 抽帧 | |
| 3 写稿 | 同行拆案例口吻；列事实清单；另起子代理按"稿子审片"挑毛病；写 `sections.json` | `references/review-prompts.md` | **① 稿子给 Aidan 批** |
| 4 配音 | 优先整篇一次合成（加热身句）；超过 2 分钟的旁白要对听首尾，若尾段漂移，保留好开头，只用接缝前两句热身并重生成漂移尾段；念急的字局部放慢；当事人原声：**先把原话和起止秒数（第 2 步的清单）填进 `spec.py` 的 `BITE_TEXT`、`BITE_CUTS`，再截** | `gen_voice.py`、`patch_voice.py`、`prep_bites.py` | Aidan 听整篇与接缝 |
| 5 写配置 | 其余场景、镜头、标签、停顿、片尾、封面都写进 `spec.py`；场景文字按顺序连起来必须和 `sections.json` 一字不差（漏一个字 `build.py` 也会停下） | `references/spec-format.md` | |
| 6 生成 | 字幕和切镜锚在真实发音；原片剪辑点报警清零 | `build.py` | **② 前 30 秒先渲染给 Aidan 看** |
| 7 配乐 | 曲库挑钢琴曲，剪到收尾和弦落在片尾卡 | `fit_music.py` | |
| 8 渲染混音体检 | 省内存渲染、混音、九项体检 | `render.py`、`mix.py`、`qc.py` | 体检 QC PASS |
| 9 审片循环 | 独立审片员只看成片；结论先实测再改；2 到 3 轮；记台账 | `references/review-prompts.md` | 审到"可以外发" |
| 10 交付 | 竖版、封面、发布文案；对可外发清单 | `build_vertical.py`、`make_cover.py` | **③ Aidan 看成片** |

停下来时给 Aidan 的是能直接看的东西（成片、样张、封面），不是命令行输出。改动攒一批再渲染，不为一处小毛病重渲一次。

## 命令（建好项目后都在项目目录里跑，`S` 是本 Skill 的 scripts 目录）

```bash
S=~/.agents/skills/pinshu-film-teardown/scripts           # 装在别处就改成实际位置
python3 $S/doctor.py                                     # 先查这台电脑的环境（不带项目）
python3 $S/new_project.py <项目目录> --film <原片.mp4>     # 建项目
cd <项目目录> && python3 $S/doctor.py .                    # 进项目后再查项目文件
python3 $S/gen_voice.py sections.json --warm "<热身句>"    # 整篇配音 -> voice/gemini_Charon/
python3 $S/patch_voice.py                                # 可选：按 spec.PATCH 局部放慢
python3 $S/prep_bites.py                                 # 先在 spec.py 填好 BITE_TEXT、BITE_CUTS，再截当事人原声
python3 $S/build.py                                      # 生成 wide/index.html 和 timeline.json
python3 $S/fit_music.py                                  # 配乐对齐 -> wide/assets/bgm/<曲名>_fit.wav
python3 $S/render.py wide wide/renders/raw.mp4           # 渲染（无配乐）
MIX_NO_FADEOUT=1 python3 $S/mix.py wide/renders/raw.mp4 wide/assets/bgm/<曲名>_fit.wav wide/renders/<成片>.mp4 soft
python3 $S/qc.py wide/renders/<成片>.mp4 timeline.json qc wide/renders/raw.mp4
# 竖版（抖音）：先出不带字幕、不带二维码的干净横版
CLEAN_FOR_VERTICAL=1 python3 $S/build.py && python3 $S/render.py wide wide/renders/clean.mp4 && python3 $S/build.py
python3 $S/build_vertical.py build wide/renders/clean.mp4
python3 $S/render.py vertical vertical/renders/raw.mp4
python3 $S/build_vertical.py mux vertical/renders/raw.mp4 wide/renders/<成片>.mp4 wide/renders/<竖版成片>.mp4
python3 $S/make_cover.py                                 # 封面 -> wide/renders/cover_16x9.png、cover_3x4.png
```

其中 `doctor.py`、`gen_voice.py`、`patch_voice.py`、`fit_music.py`、`render.py`、`mix.py`、`qc.py` 的代码在公共底座 `pinshu-video-core`，这里的同名文件只做转接，命令和输出不变。要改这几步的做法去底座改，改完底座和本 Skill 的 `tests/self_test.py` 都要跑。

配置文件不叫 `spec.py` 时用 `SPEC=<路径>`。**BaoCut 是必装的**：`gen_voice.py`、`patch_voice.py`、`prep_bites.py` 要靠它拿逐字时间，没装会在配音那一步卡住（配音钱已经花了），所以先跑 `doctor.py`。`PINSHU_TRANSCRIBE=off` 只让 `build.py` 和 `qc.py` 在没有 BaoCut 时也能跑，代价是跳过停顿核实和卡顿检查，交付前必须补上。

## 硬规矩速记（全文在 `references/rules.md`）

- 主画面是真实影像；讲别人家的做法不用本品牌素材。
- 静态图单次不超过 2 秒，同一画面不超过 3 秒；不用黑底卡片、黑底信息图；**禁止黑白画面**。
- 字幕白字描边，不铺整宽黑带；标点按 Netflix 中文规范。
- 配音优先整篇一次合成；超过 2 分钟先对听首尾，尾段漂移时只重生成漂移尾段并由用户听接缝；配乐收尾和弦落在片尾卡。
- 封面要有人脸和情绪，字不压脸；视频号短标题不带标点。
- 抖音版不能有微信二维码和"公众号"字样；两个平台都勾 AI 生成声明。

## 改了什么都要记

每改一处（画面、字幕格式、文案、转场特效、声音、渲染），当场记进 `references/pitfalls.md`：现象（原话照录）、原因、修法、以后怎么防。成为规矩的同步改 `references/rules.md`。这是这个 Skill 越用越快的来源。

## 参考文件

- `references/rules.md`：现行规矩和可外发清单
- `references/pitfalls.md`：坑与修法（按问题排的历史经验）
- `references/spec-format.md`：`spec.py` 字段说明
- `references/review-prompts.md`：审片循环规矩和三段提示词

## 已知局限

- 品牌色（红）写在 `assets/wide.css` 和片尾卡底色里，换品牌色要改样式。
- GSAP 从网上加载，渲染时要联网。
- 原片剪辑点报警只认硬切；闪白、叠化这类渐变过渡抓不到，截取点离它们留 0.3 秒以上。
- 自动测试（`tests/self_test.py`）用合成素材跑通生成、竖版、混音、体检，不覆盖真渲染和真配音；底座的局部放慢、配乐对齐、渲染核对由底座自己的自测覆盖。
