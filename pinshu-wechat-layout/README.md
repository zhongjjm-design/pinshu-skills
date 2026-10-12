# 品叔公众号排版（v0.4.0-rc.1，试用版）

把 Markdown 定稿正文加配图清单，生成一个可在六款版式间切换的本地预览页，并可一键复制正文到公众号后台。六款：青灰手记、暖纸杂志、青绿刊页、橙线手记、蓝白专题、首席品牌官经典版。

## 安装

需要 Python 3.10 以上。

```sh
python3 -m pip install -r requirements.txt
python3 scripts/doctor.py
```

doctor 最后一行显示“全部就绪”即可使用。

## 三步上手

1. 准备定稿正文（Markdown）和交接 JSON（样例见下面“交接文件样例”）。走视觉 Skill 的整篇入口时交接文件自动生成，不用手写。
2. 运行 `python3 scripts/build.py --handoff 交接.json --output-dir 新目录`（输出目录必须是不存在的新目录）。
3. 用浏览器打开 `新目录/公众号图文排版预览.html`，切换版式，复制正文。

整篇入口（同级目录装有 `pinshu-visual-system` 时）：

```sh
python3 ../pinshu-visual-system/scripts/run_ready_article.py --article <定稿正文.md> --kit <发布物料包.md> --output-dir <新目录> --prepare-only
```

有 ego 浏览器时把 `--prepare-only` 换成 `--space-id <ego空间号>`。

## 交接文件样例

最小交接文件样例（无配图）。`配图清单.json`：

```json
{"article": "正文.md", "article_sha256": "<正文文件的 SHA256>", "files": []}
```

`交接.json`：

```json
{"source_md": "正文.md", "image_manifest": "配图清单.json", "author": "作者名", "body_images": []}
```

SHA256 用 `shasum -a 256 正文.md` 算。有配图时，在 `files` 里列每张图的 `filename` 和 `sha256`，在 `body_images` 里写 `filename` 和放在哪一段后面（`after_prefix`，填那一段开头的几个字）。走整篇入口时这两个文件由视觉 Skill 自动生成，不用手写。

## 出错了怎么办

- 缺依赖或 Python 太旧：照 `scripts/doctor.py` 给的补法装好再跑。
- 提示 YAML 未闭合：正文开头的文件信息坏了，退回写稿方重新导出，不手改原稿。
- 提示输出目录已存在：换一个新目录名，不覆盖旧稿。
- 提示表格、代码块、原始 HTML 不支持：先告诉作者，不悄悄删。
- 缺 `pinshu-visual-system`：整篇入口用不了，单独 `build.py` 照常可用。


## 现在是试用版，已知问题

- 表格、代码块、原始 HTML 暂不支持，遇到会明确报告，不会静默丢弃。
- 微信后台粘贴效果还没在真机上逐款验收。
- 头图和正文图片都带模板边框、参考文章区隔、划线句已于 10-12 加入（见 references/handoff-and-rules.md 末节）。
- 经典版只有 01–06 章号图，07 章起改用文字章号。
- 整篇入口依赖同级目录的 `pinshu-visual-system`；没有它时只能单独用 build.py。

## 版本

见 `VERSION`。
