---
name: pinshu-wechat-layout
description: 将品叔公众号 Markdown 原稿与配图交接清单生成六款可切换的本地排版预览、独立发布字段和可复制正文；用于图文排版试稿，不处理发文。
---

# 品叔公众号排版 v0.4.0-rc.1（试用版）

同一预览页提供六款版式，可切换、可复制正文。只改版式，不改原稿文字，不自动写摘要或配图。

## 来源与维护

- 原创身份：品叔原创（original）
- 原创归属与维护者：Aidan（品叔）
- 上游依赖：Python 3.10 以上，`markdown-it-py`、`beautifulsoup4`；整篇入口可选搭配同仓库的 `pinshu-visual-system`。
- 分发状态：0.4.0-rc.1 公开试用版；不声明正式发布、tag、CI 通过或微信后台真机验收。

## 运行环境

需要 Python 3.10 以上。装依赖并自查：

```sh
python3 -m pip install -r requirements.txt
python3 scripts/doctor.py
```

最后一行是“全部就绪”才往下走。缺同级的 `pinshu-visual-system` 只影响整篇入口，单独 build.py 仍可用。

## 三步上手

1. 读用户明确指定的定稿正文和旁边的“发布物料包”，不要自己挑最新稿。
2. 整篇入口（推荐，交接文件自动生成）：
   `python3 ../pinshu-visual-system/scripts/run_ready_article.py --article <定稿正文.md> --kit <发布物料包.md> --output-dir <过程文件夹里的新目录> --space-id <ego空间号>`，没有浏览器把 `--space-id <ego空间号>` 换成 `--prepare-only`。
   只想排版：`python3 scripts/build.py --handoff 交接.json --output-dir 新目录`，交接文件照下面样例写。
3. 打开输出目录里的 `公众号图文排版预览.html`，切换六款，复制正文、标题、摘要。

最小交接文件样例（无配图）。`配图清单.json`：

```json
{"article": "正文.md", "article_sha256": "<正文文件的 SHA256>", "files": []}
```

`交接.json`：

```json
{"source_md": "正文.md", "image_manifest": "配图清单.json", "author": "作者名", "body_images": []}
```

SHA256 用 `shasum -a 256 正文.md` 算。有配图时，在 `files` 里列每张图的 `filename` 和 `sha256`，在 `body_images` 里写 `filename` 和放在哪一段后面（`after_prefix`，填那一段开头的几个字）。走整篇入口时这两个文件由视觉 Skill 自动生成，不用手写。

字段完整说明见 `references/handoff-and-rules.md`。

## 出错了怎么办

- 提示缺依赖：运行 `python3 -m pip install -r requirements.txt`，再跑 doctor。
- 提示 YAML 未闭合：正文开头的文件信息格式坏了。不手改原稿，退回写稿方用导出脚本重导。
- 提示表格、代码块、原始 HTML 不支持：先告诉用户，不要悄悄删。
- 提示输出目录已存在：换一个新目录名，不要覆盖旧稿。
- 图有问题（模糊、字小、框重叠）：带原文位置退回视觉环节，排版这边不自己换图。

## 交付与状态

构建成功只说明本地试排通过，不等于可发布。用户选版、微信后台真机粘贴效果，要分别如实记录，没确认前不写“可发布”。

更多细节（字段、图注规则、章号规则）：`references/handoff-and-rules.md`。
