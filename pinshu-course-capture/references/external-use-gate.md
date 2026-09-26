# External-Use Gate

This is the shared conditional gate for public release, formal reports, academic work, paid courses, client deliverables, consulting, teaching materials, real-world decisions, and public quotation. Internal course assets may enter `ACCEPTED` after basic acceptance. Failure at this gate blocks external use only; it does not retroactively invalidate an internal asset unless the review discovers core semantic distortion.

## One integrated review

Run the following checks when their content triggers apply, and emit only one `external-use-review-record.json`:

1. external facts, numbers, timeliness, and source hierarchy;
2. medical, legal, financial, safety, and platform-compliance boundaries;
3. privacy, subject authorization, and client confidentiality;
4. rights in images, slides, source text, code, and third-party content;
5. attribution of quotations, paraphrases, lecturer views, and editorial additions; and
6. whether external claims exceed the evidence or applicable scope.

Mark categories that do not apply as `not_applicable`. Do not create several sequential gates.

## Pass conditions

- Every triggered item is `pass` or has an explicit, acceptable restricted-use scope.
- No unresolved `blocker` remains.
- The record binds the source transcript, faithful edit, structured lecture, and course map by SHA-256.
- The record identifies the reviewer, review time, intended use, evidence sources, and remaining limitations.

## Safeguards

- A disclaimer never replaces claim-adjacent facts and risk boundaries.
- Spoken course content does not automatically become objective fact.
- The existence of an external-use gate never lowers the quality required for the four internal assets.
- Do not split review categories into a serial sequence that repeatedly starts new agents.
