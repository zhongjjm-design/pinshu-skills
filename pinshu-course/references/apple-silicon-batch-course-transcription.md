# Local Batch Course Transcription on Apple Silicon

Use this reference for dozens of MP3/M4A files representing more than ten hours of continuous course material. The objective is to inventory and attribute the files first, run a trial transcription second, and only then transcribe the full batch. Never merge courses merely because their filenames are adjacent.

## 1. Inventory Assets Before Transcription

- Ask the user to download all audio files into one local folder. Preserve the original filenames; do not sort or rename them manually.
- Scan the file count, dates or sequence numbers, total duration, total size, and damaged files.
- Calculate SHA-256 for every file and use hashes to identify duplicate content. Files with the same sequence number but different dates are not duplicates by default.
- Use `ffprobe` to obtain durations. Establish order by date plus sequence number, and list missing sequence numbers explicitly.
- While downloads are incomplete, perform only the inventory; do not start batch processing. Wait until the user explicitly says, “The download is complete.”

## 2. Representative Trial-Transcription Gate

Do not use the shortest file, an end-of-session recording, or an obviously noisy segment as the sole quality sample. Prefer a 120-second excerpt from the middle of a longer recording:

```bash
ffmpeg -hide_banner -loglevel error \
  -ss 120 -t 120 -i "/path/source.mp3" \
  -ac 1 -ar 16000 "/tmp/course-sample.wav" -y
```

The trial transcription serves two purposes:

1. Assess recognition accuracy, noise, and errors in proper nouns;
2. Verify course attribution. If the instructor, course title, day count, or setting in the sample does not match the target course, ask the user to confirm before writing anything into the existing course library.

## 3. Recommended Path on Apple Silicon

Prefer MLX Whisper to avoid the slow performance of conventional PyTorch Whisper on Apple Silicon. Recommended model:

```text
mlx-community/whisper-large-v3-turbo
```

Run it with `uvx` to avoid modifying the project's Python environment:

```bash
uvx --from mlx-whisper mlx_whisper "/tmp/course-sample.wav" \
  --model mlx-community/whisper-large-v3-turbo \
  --language zh \
  --task transcribe \
  --initial-prompt "Course title, instructor name, platform name, technical terms." \
  --condition-on-previous-text False \
  --word-timestamps True \
  --hallucination-silence-threshold 1.5 \
  --output-format txt \
  --output-dir "/tmp/course-transcript-test" \
  --verbose False
```

Key parameters:

- `condition-on-previous-text False`: reduces the propagation of incorrect text loops into subsequent windows;
- `word-timestamps True` plus `hallucination-silence-threshold 1.5`: reduces repeated silence hallucinations such as “thank you”;
- `initial-prompt`: include only confirmed course titles, names, and terminology. Do not insert guesses.

## 4. Quality Assessment

- The conventional `small` model can support a quick probe, but it frequently misrecognizes names, numbers, and industry terms in Chinese in-person courses with distant voices, reverberation, and overlapping speakers.
- `large-v3-turbo` is generally faster and more accurate, but it still requires terminology correction and contextual review.
- Do not judge a trial transcription as accurate merely because the text “reads smoothly.” Sample the beginning, middle, and end of the audio, and verify numbers, names, product names, and proper nouns.
- The shortest file often contains end-of-session chatter and does not represent the main lesson's audio quality. Test at least one additional sample from the middle of a substantive lesson.

## 5. Recovering Model Downloads

If a large-model download is interrupted, prefer a download method that supports resuming. After recovery, verify the file size and SHA-256 before allowing the cache to load it. The operating principle is to preserve and verify complete weights rather than repeatedly restarting the download from zero. After confirming that no process is using an incomplete temporary file, move it to Trash; do not delete it directly with `rm`.

## 6. Batch-Transcription Outputs

During the batch stage, write to a temporary workspace first rather than directly to the formal course library:

```text
00_audio-inventory.csv
01_raw-transcripts/date_sequence.txt
02_timestamped/date_sequence.json or srt
03_terminology-corrections.md
04_course-attribution.md
```

After the course boundaries are confirmed, generate:

- A faithfully edited transcript;
- A systemized lecture;
- A course-map update;
- A register of facts requiring verification and missing visuals.

## 7. Billing Boundary

- Local MLX Whisper does not call the OpenAI API and does not incur usage-based API charges.
- Before switching to a cloud API such as `gpt-4o-mini-transcribe` or `whisper-1`, confirm the billing path with the user. Never switch by default.
