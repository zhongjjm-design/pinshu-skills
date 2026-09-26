#!/usr/bin/env python3
"""Security and compatibility regressions for pinshu-md2pdf."""

import importlib.util
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


SKILL_DIR = Path(__file__).resolve().parents[1]
CONVERTER_PATH = SKILL_DIR / 'scripts' / 'convert.py'
SPEC = importlib.util.spec_from_file_location('pinshu_md2pdf_convert', CONVERTER_PATH)
if SPEC is None or SPEC.loader is None:
    raise RuntimeError(f'Cannot load converter module: {CONVERTER_PATH}')
CONVERTER = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(CONVERTER)


class SanitizerTests(unittest.TestCase):
    def test_active_content_attributes_and_unsafe_urls_are_removed(self):
        raw = '''
        <p onclick="leak()">Safe paragraph</p>
        <script>LEAK_SCRIPT</script>
        <style>LEAK_STYLE</style>
        <iframe>LEAK_IFRAME</iframe>
        <object>LEAK_OBJECT</object>
        <embed src="file:///private/secret">
        <form>LEAK_FORM<input value="secret"></form>
        <svg><text>LEAK_SVG</text></svg>
        <math><mtext>LEAK_MATH</mtext></math>
        <a href="java&#x0a;script:alert(1)" onmouseover="leak()">Bad link</a>
        <a href="https://example.test/path">Good link</a>
        <img src="data:text/html;base64,PHNjcmlwdD4=" onerror="leak()" alt="bad">
        <img src="https://example.test/tracker.png" alt="remote">
        <details open><summary>Summary</summary><p>Details body</p></details>
        '''
        cleaned = CONVERTER.sanitize_html(raw)

        for forbidden in (
            'LEAK_SCRIPT', 'LEAK_STYLE', 'LEAK_IFRAME', 'LEAK_OBJECT', 'LEAK_FORM',
            'LEAK_SVG', 'LEAK_MATH', '<script', '<style', '<iframe', '<object',
            '<embed', '<form', '<input', '<svg', '<math', 'onclick', 'onmouseover',
            'onerror', 'javascript:', 'data:text', 'tracker.png',
        ):
            self.assertNotIn(forbidden, cleaned.lower() if forbidden.islower() else cleaned)
        self.assertIn('<p>Safe paragraph</p>', cleaned)
        self.assertIn('href="https://example.test/path"', cleaned)
        self.assertIn('<details open="open"><summary>Summary</summary>', cleaned)
        self.assertIn('<p>Details body</p>', cleaned)

    def test_allowlist_preserves_normal_document_structures(self):
        png = 'data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mNk+A8AAQUBAScY42YAAAAASUVORK5CYII='
        raw = f'''
        <h2 id="section">Heading</h2>
        <p>Body <strong>bold</strong> <a href="#section">link</a></p>
        <ul><li>Item</li></ul>
        <table><thead><tr><th scope="col">A</th></tr></thead><tbody><tr><td>1</td></tr></tbody></table>
        <pre><code class="language-python">print(&quot;ok&quot;)</code></pre>
        <img src="{png}" alt="pixel" width="1" height="1">
        <details><summary>More</summary><p>Safe</p></details>
        '''
        cleaned = CONVERTER.sanitize_html(raw)
        for expected in (
            '<h2 id="section">Heading</h2>', '<strong>bold</strong>',
            '<a href="#section">link</a>', '<ul><li>Item</li></ul>', '<table>',
            '<th scope="col">A</th>', '<pre><code class="language-python">',
            png, '<details><summary>More</summary>',
        ):
            self.assertIn(expected, cleaned)

    def test_image_sources_are_data_or_within_the_document_directory(self):
        with tempfile.TemporaryDirectory(prefix='pinshu-md2pdf-images-') as tmp:
            base = Path(tmp) / 'document'
            base.mkdir()
            inside = base / 'inside.png'
            outside = Path(tmp) / 'outside.png'
            inside.write_bytes(b'png')
            outside.write_bytes(b'png')
            png = 'data:image/png;base64,iVBORw0KGgo='
            cleaned = CONVERTER.sanitize_html(
                f'<img src="inside.png"><img src="../outside.png">'
                f'<img src="{outside.as_uri()}"><img src="{png}">',
                base_dir=base,
            )
            self.assertIn(inside.resolve().as_uri(), cleaned)
            self.assertIn(png, cleaned)
            self.assertNotIn(outside.as_uri(), cleaned)
            self.assertNotIn('../outside.png', cleaned)

    def test_metadata_and_csp_are_safe(self):
        marker = 'METADATA_INJECTION_MARKER'
        escaped = CONVERTER.escape_metadata({
            'title': f'</title><script>{marker}</script><title>',
            'author': 'A & B <img src=x onerror=leak()>',
            'subtitle': '" onmouseover="leak()',
        })
        cover = CONVERTER.create_business_cover_and_toc(escaped, '')
        document = CONVERTER.build_document_html(escaped, cover, '<p>Body</p>')

        self.assertNotIn('<script>', document)
        self.assertNotIn('<img src=x', document)
        self.assertIn('&lt;script&gt;', document)
        self.assertIn('Content-Security-Policy', document)
        self.assertIn("default-src &#x27;none&#x27;", document)
        self.assertIn("script-src &#x27;none&#x27;", document)
        self.assertIn("connect-src &#x27;none&#x27;", document)
        self.assertNotIn('CHIEF' + ' BRAND OFFICER', cover)

    def test_unicode_escape_content_survives(self):
        text = '\u4e2d\u6587\u517c\u5bb9\u6027'
        cleaned = CONVERTER.sanitize_html(f'<p>{text}</p>')
        self.assertEqual(cleaned, f'<p>{text}</p>')


@unittest.skipUnless(CONVERTER.available_markdown_renderers(), 'no Markdown renderer available')
class RendererTests(unittest.TestCase):
    def test_active_raw_html_is_removed_before_rendering(self):
        marker = 'RAW_ACTIVE_CONTENT_MARKER_8B13D'
        markdown = f'''# Security\n\n<script>{marker}</script>\n\n<style>{marker}</style>\n\n## Body\n\nSafe text.\n'''
        rendered = CONVERTER.process_markdown(markdown)
        self.assertNotIn(marker, rendered)
        self.assertNotIn('<script', rendered.lower())
        self.assertNotIn('<style', rendered.lower())
        self.assertIn('Safe text.', rendered)

    def test_script_examples_inside_code_remain_inert_and_visible(self):
        markdown = '''# Code examples

`<script>INLINE_CODE_MARKER</script>`

```html
<script>FENCED_CODE_MARKER</script>
```
'''
        rendered = CONVERTER.process_markdown(markdown)
        self.assertIn('INLINE_CODE_MARKER', rendered)
        self.assertIn('FENCED_CODE_MARKER', rendered)
        self.assertNotIn('<script>', rendered)

    def test_normal_markdown_fixture_keeps_table_code_and_image(self):
        png = 'data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mNk+A8AAQUBAScY42YAAAAASUVORK5CYII='
        markdown = f'''# Fixture\n\n## Data\n\n| A | B |\n|---|---|\n| 1 | 2 |\n\n```python\nprint("ok")\n```\n\n![pixel]({png})\n'''
        rendered = CONVERTER.process_markdown(markdown)
        self.assertIn('class="content-table"', rendered)
        self.assertIn('code-block', rendered)
        self.assertIn('<img', rendered)
        self.assertIn(png, rendered)

    @unittest.skipUnless(importlib.util.find_spec('markdown2'), 'markdown2 is unavailable')
    def test_markdown2_output_is_sanitized(self):
        marker = 'MARKDOWN2_ACTIVE_MARKER_17C9'
        rendered = CONVERTER.render_markdown(
            f'<script>{marker}</script>\n\n<span onclick="leak()">Safe text</span>',
            renderer='markdown2',
        )
        self.assertNotIn(marker, rendered)
        self.assertNotIn('<script', rendered.lower())
        self.assertNotIn('<span onclick=', rendered.lower())
        self.assertIn('Safe text', rendered)

    @unittest.skipUnless(importlib.util.find_spec('markdown_it'), 'markdown-it-py is unavailable')
    def test_markdown_it_raw_html_is_inert_and_output_is_sanitized(self):
        marker = 'MARKDOWN_IT_ACTIVE_MARKER_A44E'
        rendered = CONVERTER.render_markdown(
            f'<script>{marker}</script>\n\n<span onclick="leak()">Safe text</span>',
            renderer='markdown-it-py',
        )
        self.assertNotIn(marker, rendered)
        self.assertNotIn('<script', rendered.lower())
        self.assertNotIn('<span onclick=', rendered.lower())
        self.assertIn('Safe text', rendered)


@unittest.skipUnless(
    CONVERTER.find_chrome()
    and shutil.which('pdftotext')
    and shutil.which('pdfinfo')
    and CONVERTER.available_markdown_renderers(),
    'Chrome, Poppler, and a Markdown renderer are required',
)
class ChromePDFTests(unittest.TestCase):
    def test_local_file_disclosure_marker_is_absent_from_pdf_text(self):
        marker = 'LOCAL_FILE_DISCLOSURE_MARKER_4F0D8D4E'
        with tempfile.TemporaryDirectory(prefix='pinshu-md2pdf-security-') as tmp:
            tmp_path = Path(tmp)
            secret = tmp_path / 'local-marker.txt'
            source = tmp_path / 'malicious.md'
            output = tmp_path / 'malicious.pdf'
            secret.write_text(marker, encoding='utf-8')
            source.write_text(
                '# Exploit regression\n\n'
                '<script>\n'
                'var request = new XMLHttpRequest();\n'
                f'request.open("GET", "{secret.as_uri()}", false);\n'
                'request.send(null);\n'
                'document.write(request.responseText);\n'
                '</script>\n\n'
                '## Visible body\n\nThe safe body remains.\n',
                encoding='utf-8',
            )
            result = subprocess.run(
                [sys.executable, str(CONVERTER_PATH), str(source), '-o', str(output)],
                capture_output=True,
                text=True,
                timeout=90,
            )
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            extracted = subprocess.run(
                ['pdftotext', str(output), '-'],
                capture_output=True,
                text=True,
                check=True,
                timeout=30,
            ).stdout
            self.assertNotIn(marker, extracted)
            self.assertIn('The safe body remains.', extracted)

    def test_normal_document_is_at_least_three_pages(self):
        with tempfile.TemporaryDirectory(prefix='pinshu-md2pdf-smoke-') as tmp:
            tmp_path = Path(tmp)
            source = tmp_path / 'smoke.md'
            output = tmp_path / 'smoke.pdf'
            source.write_text(
                '# Smoke Report\n\n'
                '> Verification\n\n'
                '(Normal document fixture)\n\n'
                '## 1. First section\n\nSmoke Body One.\n\n'
                '| Column | Value |\n|---|---|\n| A | 1 |\n\n'
                '## 2. Second section\n\n```text\nSmoke code block\n```\n',
                encoding='utf-8',
            )
            result = subprocess.run(
                [sys.executable, str(CONVERTER_PATH), str(source), '--theme', 'business', '-o', str(output)],
                capture_output=True,
                text=True,
                timeout=90,
            )
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            info = subprocess.run(
                ['pdfinfo', str(output)],
                capture_output=True,
                text=True,
                check=True,
                timeout=30,
            ).stdout
            pages_line = next(line for line in info.splitlines() if line.startswith('Pages:'))
            pages = int(pages_line.split(':', 1)[1].strip())
            self.assertGreaterEqual(pages, 3)
            extracted = subprocess.run(
                ['pdftotext', str(output), '-'],
                capture_output=True,
                text=True,
                check=True,
                timeout=30,
            ).stdout
            self.assertIn('Smoke Body One.', extracted)
            self.assertIn('Smoke code block', extracted)
            self.assertNotIn('CHIEF' + ' BRAND OFFICER', extracted)


@unittest.skipUnless(
    importlib.util.find_spec('weasyprint')
    and shutil.which('pdftotext')
    and CONVERTER.available_markdown_renderers(),
    'WeasyPrint, pdftotext, and a Markdown renderer are required',
)
class WeasyPrintPDFTests(unittest.TestCase):
    def test_active_content_marker_is_absent_from_weasyprint_pdf(self):
        marker = 'WEASYPRINT_ACTIVE_CONTENT_MARKER_3D2A1'
        with tempfile.TemporaryDirectory(prefix='pinshu-md2pdf-weasy-') as tmp:
            tmp_path = Path(tmp)
            source = tmp_path / 'malicious.md'
            output = tmp_path / 'malicious.pdf'
            source.write_text(
                '# WeasyPrint security\n\n'
                f'<script>{marker}</script>\n\n'
                f'<style>{marker}</style>\n\n'
                '## Visible body\n\nSafe WeasyPrint body.\n',
                encoding='utf-8',
            )
            result = subprocess.run(
                [
                    sys.executable, str(CONVERTER_PATH), str(source), '--engine',
                    'weasyprint', '-o', str(output),
                ],
                capture_output=True,
                text=True,
                timeout=90,
            )
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            extracted = subprocess.run(
                ['pdftotext', str(output), '-'],
                capture_output=True,
                text=True,
                check=True,
                timeout=30,
            ).stdout
            self.assertNotIn(marker, extracted)
            self.assertIn('Safe WeasyPrint body.', extracted)


if __name__ == '__main__':
    unittest.main(verbosity=2)
