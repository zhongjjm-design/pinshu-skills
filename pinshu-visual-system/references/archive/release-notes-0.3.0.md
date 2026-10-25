# 0.3.0（2026-10-12，试用版）

在 0.2.5-rc.1 公开层上新增公众号整篇链路，供异地同事使用：

- 证据截图工具 `capture_evidence.py`：每次重新打开页面；自动藏浮动栏、吸顶栏和浏览器插件悬浮按钮；ego 光标移出截取区域；四周留边；`--clip` 按坐标截；`--purpose quote|visual` 按用途区分清晰度；`--translate-to zh-CN` 截中文翻译版；同一网址失败 3 次自动出人工截图指引并停止重试。
- 整篇入口 `run_ready_article.py`（含 `--check-format` 只查格式）、`run_article_pipeline.py`、`prepare_article_handoff.py`、`compose_evidence.py`、`record_article_review.py`、`article_preview.py`。
- 自查命令 `scripts/doctor.py`；`requirements.txt` 补 markdown-it-py、beautifulsoup4。
- 文档：`article-asset-handoff.md`（开头“截图规矩”九条）、`ready-folder-contract.md`、`workflow.md` 补封面规则。

已知问题见 README“现在是试用版”一节。
