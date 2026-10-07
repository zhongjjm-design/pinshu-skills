# Apple Silicon 本地批量课程转写

适用于几十个 MP3/M4A、十几小时以上的连续课程。目标是：先盘点与归属，再试转，最后批量转写；不因文件名相邻就误并课程。

## 1. 素材盘点先于转写

- 让用户把全部音频下载到一个本地文件夹，保留原始文件名，不手工排序或改名。
- 扫描文件数量、日期/编号、总时长、总大小、损坏文件。
- 对每个文件计算 SHA-256，按哈希识别内容重复；同编号但日期不同不能直接判重。
- 用 `ffprobe` 获取时长；按日期＋编号建立顺序，并显式列出缺号。
- 下载未结束时只盘点，不启动批处理；等待用户明确说“下载完成”。

## 2. 代表性试转门控

不要拿最短文件、结尾散场录音或明显嘈杂片段作为唯一质量样本。推荐从一段较长音频的中部切出 120 秒：

```bash
ffmpeg -hide_banner -loglevel error \
  -ss 120 -t 120 -i "/path/source.mp3" \
  -ac 1 -ar 16000 "/tmp/course-sample.wav" -y
```

试转同时承担两个任务：

1. 判断识别准确率、噪声和专有名词错误；
2. 核验课程归属。若样本中的讲师、课名、天数、场景与目标课程不一致，先向用户确认，不能批量写入既有课程库。

## 3. Apple Silicon 推荐路径

优先使用 MLX Whisper，避免传统 PyTorch Whisper 在 Apple Silicon 上速度过慢。推荐模型：

```text
mlx-community/whisper-large-v3-turbo
```

用 `uvx` 运行，不必污染项目 Python：

```bash
uvx --from mlx-whisper mlx_whisper "/tmp/course-sample.wav" \
  --model mlx-community/whisper-large-v3-turbo \
  --language zh \
  --task transcribe \
  --initial-prompt "课程名，讲师名，平台名，专业术语。" \
  --condition-on-previous-text False \
  --word-timestamps True \
  --hallucination-silence-threshold 1.5 \
  --output-format txt \
  --output-dir "/tmp/course-transcript-test" \
  --verbose False
```

关键参数：

- `condition-on-previous-text False`：减少错误文本在后续窗口循环扩散；
- `word-timestamps True`＋`hallucination-silence-threshold 1.5`：减少静音段反复生成“谢谢”等幻觉；
- `initial-prompt`：只放已确认的课程名、人名和术语，不把猜测写进去。

## 4. 质量判断

- 传统 `small` 模型可做快速探测，但中文线下课、人声远、混响和多人插话时容易错人名、数字与行业词。
- `large-v3-turbo` 通常更快、更准，但仍需后续术语纠错和上下文校对。
- 不能因为试转文本“看起来通顺”就判定准确；抽查音频开头、中段、结尾，并核对数字、人名、产品名和专有名词。
- 最短文件常是散场闲聊，不代表正课音质；至少再测一个正课中段样本。

## 5. 模型下载恢复

若大模型下载中断，优先使用支持断点续传的下载方式；恢复后必须核对文件大小与 SHA-256，再让缓存加载。经验原则是：保存并验证完整权重，而不是反复从零重下。临时未完成文件在确认无进程使用后移入回收站，不直接 `rm`。

## 6. 批量转写产物

批量阶段先写临时工作区，不直接进入正式课程库：

```text
00_音频盘点.csv
01_原始转写/日期_编号.txt
02_带时间戳/日期_编号.json 或 srt
03_术语纠错表.md
04_课程归属表.md
```

确认课程边界后，再生成：

- 忠实精编稿；
- 系统化讲义；
- 课程地图更新；
- 待核验事实与缺图登记。

## 7. 计费边界

- 本地 MLX Whisper 不调用 OpenAI API，不产生 API 按量计费。
- 若改用 `gpt-4o-mini-transcribe`、`whisper-1` 等云端 API，必须先向用户确认计费路径，不能默认切换。
