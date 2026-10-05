# Quark Cloud Drive Video Transcript Capture Adapter

This is a discovery and conditional capture procedure, **not a production-approved adapter**. Quark has not passed an end-to-end desktop transcript extraction and source-integrity test. It does not clean, summarize, or generate paired outputs. Do not route Quark lessons into the default production pipeline merely because this procedure exists.

## Observed behavior (not end-to-end validation)

- The Quark web interface is suitable for locating shared directories and video files.
- A web file list or preview is not the transcript panel.
- A panel containing Playlist, AI Summary, and Transcript has been observed in the Quark desktop player; this does not establish a working automated extraction path.
- A prospective Quark capture path requires web discovery plus desktop-player extraction. Do not reuse Baidu web selectors.

## Prerequisites

- The controlled browser is signed in to Quark.
- The course directory, video path, and lesson identity are known.
- The user has permission to access the video and any exported content.

## Capture procedure

1. Open the user-specified shared directory in the Quark web interface. Confirm the course directory, video filename, and lesson identity.
2. Use **Open in app**, or the equivalent desktop entry point, to open the same video in the Quark desktop player. Confirm through the window title, video title, or player view that the player really opened. Do not continue before confirmation.
3. Confirm the title and video identity in the desktop player. Play or load at least two seconds so Quark can complete cloud recognition. The Transcript control may appear late; an initially empty view is not proof of failure.
4. Poll the Transcript tab and text state for one complete processing window. After the tab appears, enter it and continue waiting until the transcript stabilizes. AI Summary cannot replace Transcript.
5. Prefer the desktop player's copy or export function. If text is available only through the interface, use controlled desktop text extraction. Never infer the active window from screen coordinates.
6. Extract from the lecturer's opening text and exclude player controls, buttons, timeline, playlist, and recommendations.
7. Save the platform, video filename, complete path, extraction method, first sentence, last sentence, and text length.
8. If the web interface locates the file and the transcript visibly exists in the desktop player but automation cannot read it, mark the lesson `BLOCKED` with reason code `BLOCKED_DESKTOP_EXTRACTION`. Record what was actually observed: location, whether full transcript text was visible, and the broken extraction link. Do not claim there is no transcript or that full text was confirmed when only a tab was seen.
9. If only a summary, mind map, or slides can be verified, record that **no full source transcript was obtained in this attempt**. Do not infer a platform-wide absence from one view, and never substitute a summary.

## Integrity verification

- File identity agrees with the course manifest.
- The opening, middle, and ending are present, and the final sentence is complete.
- Browser- or desktop-extracted text matches the saved text after newline normalization.
- No obvious truncation, duplicate loading, mixed lessons, or interface contamination is present.
- Frontmatter identifies the source as the Quark Cloud Drive video transcript or the actual source type.

## Failure handling

- Not signed in, CAPTCHA, or insufficient permission: `BLOCKED` with the exact reason.
- Transcript still processing: wait for a bounded interval and reopen the video once; never retry without limit.
- No Transcript tab in the web interface: check the desktop player before concluding that no transcript exists.
- Desktop window cannot be controlled reliably: lesson state `BLOCKED`, reason `BLOCKED_DESKTOP_EXTRACTION`; preserve web discovery evidence and video identity.
- AI summary only: evaluate permitted local video transcription.
- Send the file to local ASR only when the user explicitly authorizes a permitted download. Otherwise preserve the blocker. Local ASR is a separate fallback, not proof that the Quark adapter works.
