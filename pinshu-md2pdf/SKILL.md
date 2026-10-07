---
name: pinshu-md2pdf
description: "将 Markdown 转换为带封面、目录和中文排版的专业 PDF。用于报告、白皮书、讲义、手册、技术文档，以及用户提出“Markdown 转 PDF”“md2pdf”“把 md 排成 PDF”“导出中文 PDF”时。"
---

## 来源与维护

- 原创身份：品叔原创（original）
- 原创归属：Aidan（品叔）
- 维护者：Aidan（品叔）
- 上游依赖：无
- 分发状态：公开候选；不声明正式发布或外部安装验证
- 命名沿革：原仓库目录 `pinshu-md-to-pdf`，2026-08-08 统一为 `pinshu-md2pdf`

# 品叔 Markdown 转 PDF

把 Markdown 转换为可交付 PDF。保留源文件，选择一套主题；交付路径和验证结果。

## 主题选择

只选一套主题。未指定时按用途选择；仍不清楚时用 `business`。`business` 默认是通用无品牌封面，不会自动读取或印出任何私有品牌；只有用户明确给出 `--brand-config <JSON>` 时，才在 `business` 封面显示授权品牌文字或 Logo。

| 主题 | 用途 |
|---|---|
| `business` | 品牌报告、方案、白皮书 |
| `manual-blue` | 技术文档、工具手册、流程规范 |
| `manual` | 操作指南、内部 SOP |
| `manual-orange` | 培训材料、内容生产手册 |
| `kunlun` | 传统文化、课程讲义 |
| `default` | 通用文档 |

## 工作流

1. 检查输入路径存在、文件非空、UTF-8 可读；输出路径必须以 `.pdf` 结尾。
2. 识别第一个 `#` 为标题、开头三行内的 `>` 为眉题、独立括号行为副标题、`##/###` 为目录；剥离 YAML frontmatter。
3. 没有一级标题时停止，要求补 `# 标题` 或提供 `--title`。
4. 运行预检：

```bash
python3 "<skill-dir>/scripts/convert.py" --check
```

预检必须找到 Chrome/Chromium，以及三种 Markdown 渲染器中的至少一种。选用 WeasyPrint 时还须能导入 `weasyprint`。

🔴 **CHECKPOINT · 依赖安装**

缺少依赖时，先说明缺什么和安装命令；得到用户明确许可后才能安装。

5. 运行转换：

```bash
python3 "<skill-dir>/scripts/convert.py" "<input.md>" \
  --theme <按上表选的主题> \
  -o "<output.pdf>"
```

主题按上表选：品牌报告、方案用 `business`，技术手册用 `manual-blue`，其余按用途选。按需添加 `--title`、`--subtitle`、`--author`、`--no-toc`；只有明确选择备选引擎时才用 `--engine weasyprint`。

如需给 `business` 主题接入品牌，必须由用户显式提供 JSON 配置：

```json
{
  "schema_version": 1,
  "brand_name": "品牌名",
  "logo": "business-logo.png"
}
```

```bash
python3 "<skill-dir>/scripts/convert.py" "<input.md>" \
  --theme business \
  --brand-config "<config-dir>/brand.json" \
  -o "<output.pdf>"
```

配置规则：`schema_version` 必须为 `1`；`brand_name` 可选，只按纯文字转义渲染；`logo` 可选，只接受配置文件所在目录内的相对 PNG 路径。拒绝绝对路径、上级穿越、远端 URL、符号链接逃逸、非普通文件、伪装 PNG 和过大文件。`--brand-config` 只支持 `business` 主题，其他主题传入会明确报错，不会静默印品牌。代码不会自动读取私人 Logo 路径。

🔴 **CHECKPOINT · 覆盖文件**

输出文件已存在时默认停止。用户明确要求覆盖后才添加 `--force`。

6. 验证产物：

```bash
file "<output.pdf>"
pdfinfo "<output.pdf>"
pdftotext "<output.pdf>" -
pdffonts "<output.pdf>"
```

确认文件是 PDF、页数大于 0、中文可提取、表格/代码/引用未丢失、字体列表存在。重要交付再检查首页和正文；发现截断、溢出、空白页或乱码时不得宣布完成。

## 失败处理

| 触发条件 | 一线处理 | 仍失败时 |
|---|---|---|
| 输入不存在、为空或不可读 | 核对路径、大小和编码 | 停止并索取正确文件 |
| 缺少 Markdown 渲染器 | 检查三种支持项 | 经许可后安装一种 |
| 找不到 Chrome | 检查路径与 `PATH` | 询问安装，或改用已就绪的 WeasyPrint |
| 输出已存在 | 展示目标路径并停止 | 用户确认后使用 `--force` |
| 未生成有效 PDF | 检查日志、权限和临时输出 | 清理无效文件，报告失败 |
| 中文乱码或版式溢出 | 切换字体链、主题或文档结构 | 说明限制，请用户确认取舍 |
| 品牌配置被拒绝 | 检查 JSON schema、主题是否为 `business`、Logo 是否为配置目录内真实 PNG | 不要改成默认加载私有路径；让用户重新提供显式配置 |

## 不要做

- 不要修改源 Markdown 掩盖问题，也不要混用主题；
- 不要静默安装依赖或覆盖文件；
- 不要把旧 PDF 当作新产物；
- 不要在未验证目标阅读器时宣称“完全兼容”；
- 不要只检查文件存在就宣布完成；
- 不要为 `business` 主题自动加载私有品牌；必须有显式 `--brand-config`；
- 不要把 README、示例集、缓存、备份或嵌套 Skill 副本放进正式包。
