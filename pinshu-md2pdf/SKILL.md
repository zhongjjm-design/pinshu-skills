---
name: pinshu-md2pdf
description: "Convert Markdown into a professional PDF with a cover, table of contents, and publication-ready typography. Use for reports, white papers, course materials, manuals, technical documentation, or requests such as 'Markdown to PDF,' 'md2pdf,' 'typeset this Markdown as a PDF,' or 'export this as PDF.'"
---

## Provenance and maintenance

- Original status: Pinshu original (`original`)
- Owner: Aidan (Pinshu)
- Maintainer: Aidan (Pinshu)
- Upstream dependencies: None
- Distribution: `bundled`; distributed with `aidan-skills` and `claude-skills`
- Naming history: Renamed from `pinshu-md-to-pdf` to `pinshu-md2pdf` on 2026-08-08

# Pinshu Markdown to PDF

Convert Markdown into a delivery-ready PDF while preserving the source file. Select one theme, then report the output path and verification results.

## Choose a theme

Use exactly one theme. If the user does not specify one, choose by purpose; use `default` when the purpose remains unclear. This public edition's `business` theme uses a dark cover and accent colors **without a bundled identity**. The private original may add a Chief Brand Officer logo and footer; do not assume either edition automatically represents the user's brand. For a branded deliverable, confirm the intended identity and check the rendered cover before delivery.

| Theme | Best for |
|---|---|
| `business` | Brand reports, proposals, and white papers (unbranded in this edition) |
| `manual-blue` | Technical documentation, tool manuals, and process specifications |
| `manual` | Operating guides and internal SOPs |
| `manual-orange` | Training materials and content-production manuals |
| `kunlun` | Traditional-culture material and course handouts |
| `default` | General documents |

## Workflow

1. Confirm that the input path exists, is non-empty, and contains valid UTF-8. The output path must end in `.pdf`.
2. Treat the first `#` heading as the title, a `>` line within the first three lines as the eyebrow, a standalone parenthesized line as the subtitle, and `##` or `###` headings as table-of-contents entries. Strip YAML frontmatter.
   Raw HTML is not trusted: active elements and their contents are omitted, while other raw HTML is rendered as inert text or removed. Ordinary Markdown links, local/data images, tables, code, and lists remain supported.
3. If the document has no level-one heading, stop and ask the user to add `# Title` or provide `--title`.
4. Run the preflight check:

```bash
python3 "<skill-dir>/scripts/convert.py" --check
```

The check must find Chrome or Chromium and at least one of the three supported Markdown renderers. When using WeasyPrint, Python must also be able to import `weasyprint`.

🔴 **CHECKPOINT · Dependency installation**

If a dependency is missing, identify it and provide the installation command. Install it only after the user gives explicit approval.

5. Run the conversion:

```bash
python3 "<skill-dir>/scripts/convert.py" "<input.md>" \
  --theme <selected-theme> \
  -o "<output.pdf>"
```

Replace `<selected-theme>` with the **one theme chosen from the table** (for example, `manual-blue` for a technical manual); it is not a literal command argument. Add `--title`, `--subtitle`, `--author`, or `--no-toc` as needed. Use `--engine weasyprint` only when that fallback engine is explicitly selected.

🔴 **CHECKPOINT · Existing output**

Stop by default if the output file already exists. Add `--force` only after the user explicitly approves replacement.

6. Verify the artifact:

```bash
file "<output.pdf>"
pdfinfo "<output.pdf>"
pdftotext "<output.pdf>" -
pdffonts "<output.pdf>"
```

Confirm that the file is a PDF, has at least one page, contains extractable text, preserves tables, code, and quotations, and reports a font list. For important deliverables, inspect the cover and representative body pages. Do not report completion if you find clipping, overflow, blank pages, garbled text, or missing content.

## Failure handling

| Trigger | First response | If it still fails |
|---|---|---|
| Input is missing, empty, or unreadable | Check the path, size, and encoding | Stop and request the correct file |
| No Markdown renderer is available | Check all three supported renderers | Install one after approval |
| Chrome is unavailable | Check known locations and `PATH` | Ask to install it, or use an available WeasyPrint installation |
| Output already exists | Show the target path and stop | Use `--force` after confirmation |
| No valid PDF is generated | Inspect logs, permissions, and temporary output | Remove the invalid output and report the failure |
| Text is garbled or layout overflows | Change the font stack, theme, or document structure | Explain the limitation and ask the user to choose the trade-off |

## Guardrails

- Preserve the source Markdown and use one theme per conversion.
- Obtain approval before installing dependencies or replacing files.
- Verify that the PDF was created during the current run.
- Claim compatibility only for readers that were actually tested.
- Validate the PDF content, not only file existence.
- Treat `business` as an unbranded color and layout theme; it never adds a bundled logo or third-party identity.
- Keep README files, example collections, caches, backups, and nested skill copies out of the release package.
