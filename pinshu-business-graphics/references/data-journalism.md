# Data Journalism

## Identity

Lead with verified evidence. Charts, annotations, context, sources, and a conclusion-led headline form the visual argument. The design must allow the reader to distinguish measured facts from interpretation.

Use for:

- trends, markets, operations, surveys, benchmarks, and business performance
- evidence-led report pages and social explainers
- questions involving change over time, composition, distribution, ranking, or correlation

Do not use when no trustworthy dataset exists. Route a conceptual claim to another mother.


## Composition families

1. `one-chart story`: one decisive chart, direct annotations, context band, and one conclusion.
2. `small multiples`: repeated scales compare segments, regions, periods, or scenarios.
3. `evidence stack`: headline number, main chart, two supporting indicators, methodology, and source.
4. `annotated timeline`: time series with turning points, causal context, and clearly separated inference.

## Data rules

- Record source URL or document, access/publication date, units, period, sample, and methodology.
- Keep common scales for comparisons unless a scale change is explicitly disclosed.
- Start bars at zero unless a non-zero baseline is necessary and conspicuously marked.
- Use direct labels where possible; keep legends close to the data.
- Label estimates, forecasts, and derived calculations.
- Never let a decorative metaphor distort magnitude.

## Production boundary

- Raster image generation may explore art direction and chart composition.
- Build final dense, audit-critical, or editable charts with a charting, slide, spreadsheet, or design tool.
- Compare every visible value and proportion with the structured source before approval.

## Typography and color

- Use a conclusion-led headline, compact annotation style, and readable source note.
- Reserve accent color for the evidence that answers the question.
- Use neutral comparison colors and accessible contrast.

## Prompt kernel

> Create a data-journalism business visual answering “[question]” with the conclusion “[headline]”. Use [composition family] and only the supplied dataset. Show exact units, dates, values, direct annotations, methodology, and source note. Separate observed facts from interpretation and forecasts. Use a restrained newsroom palette with one evidence accent. No invented numbers, no decorative 3D chart, no unlabeled axis, no misleading baseline, no pseudo-source.

## Failure boundaries

Reject when:

- any number, unit, date, or source is altered
- a chart cannot be reconstructed from the supplied data
- visual proportions contradict the values
- annotations imply causation unsupported by evidence
- the final needs precision or editability but only a generated bitmap exists
