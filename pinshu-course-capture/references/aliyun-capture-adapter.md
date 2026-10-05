# Alibaba Cloud Drive Video Transcript Capture Adapter

This adapter performs capability discovery and a standard handoff. Until validated, it does not assume that Alibaba Cloud Drive provides a native transcript.

## Objective

Return Alibaba Cloud Drive video content through the shared capture contract:

```text
Locate video -> inspect transcript entry points -> obtain source text -> verify opening/middle/ending -> save source transcript
```

## Discovery order

1. Confirm the account, shared directory, course directory, and video filename.
2. Check the web player first for transcript, subtitle, or transcription controls.
3. If the web player has none, check the official desktop player or an official export function.
4. Consider local ASR only when the user has download permission.
5. AI summaries, mind maps, slides, and comments cannot serve as source transcripts.
6. Record one discovery outcome per attempt: `LOCATED`, `NATIVE_TRANSCRIPT_FOUND`, `BLOCKED_DESKTOP_EXTRACTION`, `NO_NATIVE_TRANSCRIPT`, or `BLOCKED`. These are discovery results or blocker reasons; the course state machine uses `BLOCKED` for a blocked lesson.

## Handoff requirements

On success, return the platform, video identity, complete path or URL, native transcript text, extraction method, first sentence, last sentence, and opening/middle/ending integrity evidence.

If the file is located but no transcript text is obtained, preserve the blocker. Do not create a fake source transcript or use an AI summary as full text.

After one real capability validation on Alibaba Cloud Drive, add the exact page selectors or desktop steps. Until then, this file is a safe discovery adapter and does not claim production readiness.
