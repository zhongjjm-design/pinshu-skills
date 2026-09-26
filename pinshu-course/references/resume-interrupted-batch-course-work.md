# Resuming Interrupted Batch Course Processing

Use this reference when audio has been partly or fully transcribed, status files may be stale, and final products may already exist in editing directories. The objective is to reconstruct actual state before continuing from the incomplete point, avoiding retranscription, overwrite of finished work, or treating recording chunks as lesson boundaries.

## Authority Order for State

Do not trust the task-status document first. Reconstruct facts in this order:

1. Actual raw audio files;
2. Actual raw transcript outputs: TXT, JSON, SRT, VTT, and TSV;
3. `START`, `DONE`, and `FAIL` entries plus final statistics in batch logs;
4. Actual edited transcripts, lectures, maps, and other output files;
5. Written claims in task-status files.

A status file is a handoff aid and cannot override file evidence. If it says “transcription about to start” while logs show `total=N failed=0` and each output format has N files, treat the actual products as authoritative and mark the status stale.

## Begin with a Four-Way Inventory

After resumption, enumerate state before rerunning anything:

```text
Raw audio
↔ five transcript outputs per audio file
↔ existing edited transcripts / lectures
↔ status files and logs
```

At minimum, verify total audio count, dates and numbers, counts for each transcript format, log success/failure totals, whether finished products already exist, and the presence of empty text, unusually short text, dispersal recordings, and duplicates. Rerun only when the source exists and an output is missing; skip audio with complete TXT and JSON by default.

## Perform Read-Only Semantic Inventory in Parallel by Day

For dozens of audio files, inventory by teaching day or module in parallel, but keep this phase read-only. Each group returns the same fields:

| File | Non-Whitespace Characters | Empty? | Opening/Closing Topic Anchors | Silence/Low-Audio Hallucination | Frequent STT Errors | Suggested Natural Boundary |
|---|---:|---|---|---|---|---|

Focus on continuations across files; breaks, lunch, Q&A, and dismissal; speaker or topic changes inside recordings; silence loops; recognition degradation caused by played videos; systematic terminology drift; and names, amounts, ratios, or case data requiring relistening. Subagent boundaries are candidates only. The main agent must read the full synthesis and create one unified lesson map.

## Natural Lesson Boundaries Take Priority Over Recording Chunks

1. Split by explicit instructor transitions, break announcements, topic closure, and contextual continuation;
2. Do not treat every MP3 as a lesson mechanically;
3. Do not merge every recording from one day into one lesson mechanically;
4. Exclude coffee breaks and dismissal from the main lesson body;
5. Label product promotion, live discussion, and Q&A separately when they have standalone value; do not mix them into methodology prose;
6. If a truncated final sentence has no continuation source, put it in the relisten register rather than completing it.

## Lock the Batch Manifest Before Writing

When the user’s environment requires approval for writes, keep inventory and boundary decisions read-only. After boundaries are settled, list once: operation types, file types, full absolute path for every target file, whether parent directories exist, whether anything will be overwritten, source files and formal knowledge bases excluded from the current run, and the naming and validation standard. Do not precreate empty files with placeholder titles before natural lesson boundaries are known.

## Three Control-Plane Files

When batch editing begins, maintain:

1. `{course_map}`: natural lesson boundaries, dates, knowledge titles, source ranges, and status;
2. `{terminology_review}`: normalized terms, common misrecognitions, names/numbers requiring relistening, and locations degraded by silence;
3. `{task_status}`: actual completed work, next step, and formal destination.

Resolve each placeholder from the manifest or confirmed path map; do not use it as a literal filename.

The control plane does not replace the body. Reverify status updates through actual file counts, non-whitespace character counts, and file reads. A subagent’s self-reported “complete” is not sufficient for green status.

## Main-Agent Acceptance After Batch Writing

1. Confirm that every approved path exists;
2. Count non-whitespace characters and identify anomalously short drafts;
3. Scan for third-party voice, placeholders, filler speech, unclosed code fences, and suspected truncation;
4. Compare systematic STT residue against the terminology register;
5. Sample the opening, a middle case, and the ending of each lesson against the authoritative source;
6. Verify that recording ranges have no overlap, omissions, or cross-lesson contamination;
7. Keep “requires relistening” strictly separate from “confirmed”;
8. Update course-map status only after acceptance.

## Common Failures

- Rerunning an entire audio batch after reading only a stale status file;
- Assuming a finished-product directory contains deliverables without enumerating actual files;
- Treating `DONE` in a log as proof of transcript quality;
- Allowing parallel agents to define lessons independently without main-agent reconciliation;
- Compressing a long course into a dozen summaries for speed;
- Creating a formal knowledge base before confirming course identity or overall title;
- Entering computed totals manually. Use a calculation tool for addition and read files back to verify totals.
