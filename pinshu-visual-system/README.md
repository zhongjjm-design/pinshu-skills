# Pinshu Visual System 0.4.0（试用版）

## 第一次运行（5 分钟）

1. 进入装好的 Skill 目录：`cd <skills目录>/pinshu-visual-system`
2. 确认 Python 是 3.10 以上：`python3 --version`。不是就 `brew install python`，之后用 `/opt/homebrew/bin/python3` 代替下面的 `python3`。
3. 装依赖：`python3 -m pip install -r requirements.txt`
4. 自查：`python3 scripts/doctor.py`，缺什么照它给的补法补。
5. 查定稿格式：`python3 scripts/run_ready_article.py --article <定稿正文.md> --kit <发布物料包.md> --check-format`
6. 整篇排版：有 ego 浏览器用 `python3 scripts/run_ready_article.py --article <正文> --kit <物料包> --output-dir <过程文件夹里的新目录> --space-id <ego空间号>`；没有就把 `--space-id <ego空间号>` 换成 `--prepare-only`，截图会先生成待截图清单。
7. 截图失败：用同一条命令重跑，第 3 次失败后，工具在输出目录旁边生成 `人工截图指引_<名字>.md`，写明打开哪个网址、截哪块、存到哪、文件名；照着人工截好，告诉 Agent 接着做。

本 Skill 不自带生图模型和钥匙，生图靠你用的 Agent 自己的能力。只有 Python 时能做到“准备包完成”（格式检查、视觉计划、待截图清单、排版预览）；浏览器、生图、ImageMagick 都齐才是“成品完成”。

A usable shared visual workflow developed by Aidan (Pinshu) with Codex: read the content, select a visual relationship and style, generate with your agent, inspect the actual image, and export a reviewed candidate for its platform.

## What colleagues receive

- Twelve visual-mode cards with explicit available, scoped, character-dependent and candidate states;
- A routing index to the seven complete business-visual families in the independent companion;
- Two experimental cultural-poster method cards, separate from the twelve visual modes;
- Seven information structures and eighteen composition/package IDs;
- Eleven project platform presets, including WeChat wide/square covers, article images, vertical cards, X and presentation images;
- A standard-library plan compiler, user-supplied character profiles and exact-text routing;
- Exact-size export, crop previews, metadata-clean copies and a fail-closed delivery wrapper;
- A source brief, command examples, actual public example and local regression tests.

No personal character artwork or private project material is included. Users can work without a character or bring their own approved identity references.

## Honest scope

This is a maintained public preview. It is usable with an image-capable agent, but it is not a standalone image generator or a claim of fully stable automatic batch production. Scripts verify declared contracts, hashes, dimensions and copy integrity. People and reviewing agents still inspect content, lettering and aesthetics. Candidate and frozen modes are clearly separated; the first public edition is independently versioned rather than inheriting a private maturity claim.

Planning needs Python 3; image export needs ImageMagick 7. Whole-article screenshots and layout need `pip install -r requirements.txt` and the ego browser; run `python3 scripts/doctor.py` to check. Read [quickstart](references/quickstart.md). The repository's original usage and redistribution terms apply.

## 现在是试用版：已知问题

- 整篇截图依赖 ego 浏览器；网站改版后定位写法可能失效，失败 3 次会自动转人工截图，不会卡死。
- 外文截中文版走谷歌翻译中转页，部分网站（如 note.com）会挡，挡了就按人工指引用浏览器右键翻译后截。
- 试稿模式使用同仓库 `pinshu-write` 3.3.0 的 `export_article.py`；正式“定稿待发”路线不需要。
- 排版预览的微信后台粘贴效果还没在真机逐款验收。
- 脚本检查通过只是最低要求，图意、审美、手机可读性要人看。

## An actual example

![Three draft-review actions in a notebook illustration](examples/draft-review.png)

This AI-generated example used the included [brief](examples/brief.md) and Notebook Knowledge Explainer mode. The three scenes mean: compare with the source, check names and numbers, and inspect the thumbnail/reading order. The visible "123" is an illustrative placeholder, not a factual statistic. No private character or real person is depicted.

The saved [compiled prompt](examples/draft-review.compiled-prompt.txt) and [evidence record](examples/draft-review.evidence.json) document the generation channel, actual-image inspection and exact 1600 x 900 export. The image is a demonstration candidate; one result does not establish aesthetic acceptance or stable batch output.

## The complete visual set

Use [pinshu-infographic](../pinshu-infographic/README.md) for knowledge-diagram source anchors, relations and density. Use [pinshu-business-graphics](../pinshu-business-graphics/README.md) for the seven business mothers and commercial mechanism review. Both public companions require this public core 0.2.4 or later in a sibling folder. The repository installer adds the full set together and refuses to replace private installations of any of these names.

## Cultural-poster method experiments

![Papermaking material-form test](examples/craft-paper.png)

![Paper-folding material-form test](examples/craft-fold.png)

These two new AI-generated examples test [Oriental Material Craft](references/method-cards/oriental-material-craft.md): the large form grows from the small workshop's material/action. Fibre sheet and folded geometry yield different compositions. Each is exported to 1080 x 1440 from a dedicated portrait generation. The short Chinese titles are intentionally localized image content. The English source concepts and exact prompts are retained in the respective source and generation records; JSON encodes localized title characters with standard Unicode escapes.

[Papermaking source](examples/craft-paper.source.md), [generation record](examples/craft-paper.generation.json), [evidence](examples/craft-paper.evidence.json). [Paper-folding source](examples/craft-fold.source.md), [generation record](examples/craft-fold.generation.json), [evidence](examples/craft-fold.evidence.json).

Actual-image review checked title accuracy, material/action connection, thumbnail and safe export. Both remain method candidates pending human aesthetic review and further themes. The original external research references still need source recovery; no original prompt or reference image is redistributed. [Colorfield Landscape](references/method-cards/oriental-colorfield-landscape.md) is also a candidate card, with no new rendering or promotion claimed in this release.

本版的批次看图、单图替换、截图拒绝和局部审核沿用见 [0.4.0 说明](references/release-notes-0.4.0.md)。发布与安装验收状态以仓库本次回执为准。

Candidate reproducibility: use requirements.txt for the PNG sharing exporter (tested Python 3.14 / Pillow 12.2.0). Existing render/export commands also need ImageMagick 7 and the installed font selected by the user; PPTX trials need LibreOffice and Poppler as documented. A clean installation and candidate repository CI have not yet been validated. Keep local audit receipts private and use the explicit share exporter described in SKILL.md.

Run both bundled suites from this package root:

```sh
python3 -B -m unittest discover -s tests -p 'test_*.py'
python3 -B -m unittest discover -s scripts -p 'test_export_share.py'
```

The first suite covers the existing routing and delivery contracts; the second covers the new sharing boundary. Neither suite independently validates native LibreOffice PPTX rendering for this candidate.

Publishing cleanup and sharing use one PNG chunk whitelist. prepare_publish_images.py removes all other ancillary chunks after conversion, including tIME/orNT, verifies dimensions and AE=0, then runs the same validator as export_share.py before PASS. The original image is unchanged. “Metadata-clean” here means no metadata outside that whitelist; rendering/color/density chunks can remain. For system-produced raster images, run cleanup first and share the resulting *-publish-clean.png; a raw source with metadata is correctly rejected by the sharing gate. Local source/font/QA receipts stay excluded.
