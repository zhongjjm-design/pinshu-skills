---
name: pinshu-video-core
description: "品叔视频类 Skill 的公共底座：整篇一次合成配音、局部放慢、配乐对齐片尾卡、省内存渲染并核对帧数、固定增益混音、成片九项体检、环境检查。供 pinshu-film-teardown 等视频类型 Skill 调用，一般不直接给用户用（用户要做哪类片子就用那类 Skill）。只在新建视频类型 Skill、或维护这些公共脚本时读本文件。"
---

## 来源与维护

- 原创身份：品叔原创（original）
- 原创归属：Aidan（品叔）
- 维护者：Aidan（品叔）
- 上游依赖：FFmpeg（转码、响度、静音检测）；BaoCut（https://github.com/JimLiu/baocut，MIT，中文转写取逐字时间）；Gemini TTS（Google 接口，各人用自己的钥匙）；HyperFrames（https://github.com/heygen-com/hyperframes，Apache-2.0，`render.py` 调它的命令行渲染）；librosa（ISC，`fit_music.py`、`patch_voice.py` 用）；numpy（BSD-3-Clause）、soundfile（BSD-3-Clause）、Pillow（MIT-CMU）；Demucs（https://github.com/adefossez/demucs，MIT，可选，环境检查只查装没装）
- 原创能力：各类品叔视频共用的做法：整篇旁白一次合成、只在真实静音处切段（防声音漂移成两个人），按请求签名拦住重复花钱；念急的字局部放慢而不重新合成；配乐自动接缝让原曲收尾和弦落在片尾卡；省内存渲染并核对时间和帧数（防混进旧渲染）；固定增益混音到 -14 LUFS、真峰值不超过 -1 dBTP；成片九项体检；一次查全的环境检查。2026-10-07 从 `pinshu-film-teardown` 抽出，代码原样搬家
- 分发状态：14 项统一公开候选之一；与 `pinshu-film-teardown` 同仓分发，`bundled`
- 调用方：`pinshu-film-teardown`（品牌片拆解）

# 品叔视频公共底座

这是供 `pinshu-*` 视频类型 Skill 调用的公共底座，一般不直接给用户调用。用户说"做个品牌片拆解"，用的是 `pinshu-film-teardown`；以后的商业讲解片、东方文化可视化片也各有自己的类型 Skill。

分工：类型 Skill 管"这一类片子长什么样"（场景种类、版式、样式、封面、项目模板、规矩和坑）；本底座管"每类片子都要做、而且做法一样"的那几步。

## 脚本一览（都在 `scripts/`）

| 脚本 | 干什么 | 读什么 |
|---|---|---|
| `common.py` | 公共函数：找 ffmpeg、ffprobe，量时长，调 BaoCut 转写（结果缓存在音频旁边），读项目的 `spec.py`，读 Gemini 钥匙（只读不写），中文标点表 | 环境变量 `FFMPEG`、`FFPROBE`、`BAOCUT`、`PINSHU_TRANSCRIBE`、`SPEC`、`PROJECT`、`GEMINI_API_KEY` |
| `gen_voice.py` | 整篇旁白一次合成（可加热身句再剪掉），在段与段之间的真实静音处切成 `secNN.mp3`，每段出逐字时间；同一份稿子、声音、风格、模型已经合成过就不再花钱 | `sections.json`；`--dry-run` 只核对、不调接口 |
| `patch_voice.py` | 念急的几个字局部放慢、加小停顿，不重新合成；写到新目录，原配音不动 | `spec.PATCH` |
| `fit_music.py` | 配乐按片尾卡位置自动接缝，让原曲收尾和弦落在片尾卡；章节卡上太安静的段落托起来；最后一句旁白之后收尾音提 10 分贝 | `spec.BGM`、`spec.OUT_VOICE_SUBDIR`、`timeline.json`、`wide/index.html` |
| `render.py` | 省内存渲染 HyperFrames 工程，失败自动重试；成片比工程新、帧数对得上才算成功；工程引用的文件缺了就拒绝渲染 | 工程目录的 `index.html` |
| `mix.py` | 无配乐渲染加配乐出成片：固定增益到 -14 LUFS，真峰值不超过 -1 dBTP；`soft` 是解说片默认 | 命令行参数 |
| `qc.py` | 成片九项体检：时长、黑场、首帧、响度和片尾卡有没有声、切点和镜头尾截图、字幕压黑画面、画面静止超 2 秒、切点首帧异常、句中卡顿 | 成片、`timeline.json`、无配乐渲染 |
| `doctor.py` | 环境检查：Python 模块、ffmpeg 滤镜、node、HyperFrames、BaoCut、Demucs、Gemini 钥匙、磁盘；给项目目录时查 `spec.py`；类型 Skill 可以加自己的项目文件检查 | 可选的项目目录 |

各脚本开头的英文说明写了完整用法和参数。

## 类型 Skill 怎么接

1. **找底座**：先看环境变量 `PINSHU_VIDEO_CORE`（指向本 Skill 目录），再找和类型 Skill 并排的 `pinshu-video-core`。现成写法照抄 `pinshu-film-teardown/scripts/_video_core.py`。
2. **命令照旧**：想让用户继续用 `python3 $S/mix.py ...` 这种命令，就在类型 Skill 里放同名的薄转接文件（一行 `_video_core.run("mix.py")`），参数和输出原样不变。
3. **公共函数**：类型 Skill 自己的脚本要用 `common.py` 时，放一个同名 `common.py` 转发底座的函数，再补上自己的 `SKILL_DIR`、`ASSETS`（样式、模板归类型 Skill，底座不管）。写法见 `pinshu-film-teardown/scripts/common.py`。
4. **环境检查**：类型 Skill 的 `doctor.py` 调底座的 `main(project_checks)`，传一个函数 `(项目目录, ok, warn, bad)`，往三个列表里加自己项目要的文件。写法见 `pinshu-film-teardown/scripts/doctor.py`。
5. **毛病只在一处改**：公共脚本的问题在本 Skill 改，改完跑本 Skill 的自测和每个调用方的自测。

## 类型 Skill 要守的约定（脚本按这些读）

- **项目目录**：在项目目录里跑命令（或设 `PROJECT`）；内容配置默认是项目里的 `spec.py`（或设 `SPEC`）；横版工程在 `wide/`。
- **`wide/index.html`**：根节点写成 `data-composition-id="main" data-start="0" data-duration="<总秒数>"`，按每秒 30 帧算；每段旁白是 `<audio id="voN" src="assets/<OUT_VOICE_SUBDIR>/secNN.wav" data-start="…">`（`OUT_VOICE_SUBDIR` 默认 `voice`），属性顺序不能变，`fit_music.py` 靠它找最后一句旁白。
- **`timeline.json`**：`{"TOTAL": 总秒数, "SC": [场景…], "caps": [[起点, 时长, 字幕]…], "narr": [按顺序的旁白原文…]}`。每个场景至少有 `i`（序号）、`k`（类型）、`t`（起点）、`d`（时长）；可选 `vo`（第一个字出声的时刻）、`cl`（镜头列表，每个有 `st`、`dd`，原片或素材镜头带 `file`）、`bite_t` 和 `bite_d`（当事人原声的起点和时长，体检不把那里的停顿当卡顿）。
- **三种场景类型有固定含义**：`end` 是片尾卡（`fit_music.py` 要求有一个，体检单独量它的响度）；`chapter` 是章节卡（前 2.9 秒是卡、之后是画面，要带 `vo`，配乐在卡上会被托起）；`full`、`story`、`chips`、`chapter` 没有镜头列表时，体检在场景开头（章节卡在卡之后）查切点首帧。新片型用别的类型名不会出错，只是不享受这几项特殊处理。
- **体检截图标签**用项目里的 `wide/assets/fonts/SourceHanSerif-VF.ttf`，没有就用默认字体。

## 自测

`python3 tests/self_test.py`：用合成素材离线跑通全部 8 个脚本（转写和 HyperFrames 用替身，Gemini 用假钥匙，不会花钱）。缺 librosa 时跳过 `patch_voice.py`、`fit_music.py` 两项。整条线用同一个装齐 numpy、soundfile、pillow、librosa 的 Python。

## 已知局限

- `render.py` 按每秒 30 帧核对帧数，别的帧率要改脚本。
- `gen_voice.py` 默认风格是"像跟同行朋友聊一个案例，松弛，有观点"（拆解片定的），别的片型用 `--style` 换；`--dry-run` 报的字数把段与段之间的空行也算进去了，比纯文字多几个。
- `qc.py`、`fit_music.py` 依赖上面的 `timeline.json` 和 `wide/index.html` 约定，新片型的生成脚本要照约定写出这两个文件。
- 自测覆盖不到真渲染和真配音，那两步还是要看成片、听配音。
