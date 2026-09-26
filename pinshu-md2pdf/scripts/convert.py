#!/usr/bin/env python3
"""
pinshu-md2pdf · Markdown to PDF
Multi-theme Markdown-to-PDF converter

Usage:
  python convert.py input.md
  python convert.py input.md --theme business -o output.pdf
  python convert.py input.md --theme manual --title "Title"

Themes: kunlun / business / manual / manual-orange / manual-blue
"""

import argparse
import html as html_lib
import importlib.util
import os
import re
import shutil
import subprocess
import tempfile
import unicodedata
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlsplit


ACTIVE_CONTENT_TAGS = {
    'script', 'style', 'iframe', 'object', 'embed', 'form', 'input', 'svg', 'math',
}
ACTIVE_VOID_TAGS = {'embed', 'input'}
ALLOWED_HTML_TAGS = {
    'a', 'blockquote', 'br', 'code', 'del', 'details', 'div', 'em', 'h1', 'h2',
    'h3', 'h4', 'h5', 'h6', 'hr', 'img', 'li', 'ol', 'p', 'pre', 's', 'span',
    'strong', 'summary', 'table', 'tbody', 'td', 'tfoot', 'th', 'thead', 'tr', 'ul',
}
VOID_HTML_TAGS = {'br', 'hr', 'img'}
GLOBAL_HTML_ATTRIBUTES = {'class', 'id', 'title'}
TAG_HTML_ATTRIBUTES = {
    'a': {'href'},
    'details': {'open'},
    'img': {'alt', 'height', 'src', 'width'},
    'li': {'value'},
    'ol': {'reversed', 'start'},
    'td': {'align', 'colspan', 'rowspan'},
    'th': {'align', 'colspan', 'rowspan', 'scope'},
}
BOOLEAN_HTML_ATTRIBUTES = {'open', 'reversed'}
INTEGER_HTML_ATTRIBUTES = {'colspan', 'height', 'rowspan', 'start', 'value', 'width'}
STYLE_NONCE = 'pinshu-md2pdf-generated-style'
CONTENT_SECURITY_POLICY = (
    "default-src 'none'; base-uri 'none'; script-src 'none'; connect-src 'none'; "
    f"style-src 'nonce-{STYLE_NONCE}'; img-src file: data:; font-src file: data:; "
    "media-src 'none'; object-src 'none'; frame-src 'none'; child-src 'none'; "
    "form-action 'none'"
)


class _ActiveMarkdownStripper(HTMLParser):
    """Remove active raw-HTML blocks while leaving other Markdown bytes intact."""

    def __init__(self):
        super().__init__(convert_charrefs=False)
        self.output = []
        self.drop_depth = 0

    def handle_starttag(self, tag, attrs):
        tag = tag.lower()
        if self.drop_depth:
            if tag in ACTIVE_CONTENT_TAGS and tag not in ACTIVE_VOID_TAGS:
                self.drop_depth += 1
            return
        if tag in ACTIVE_CONTENT_TAGS:
            if tag not in ACTIVE_VOID_TAGS:
                self.drop_depth = 1
            return
        self.output.append(self.get_starttag_text())

    def handle_startendtag(self, tag, attrs):
        if not self.drop_depth and tag.lower() not in ACTIVE_CONTENT_TAGS:
            self.output.append(self.get_starttag_text())

    def handle_endtag(self, tag):
        tag = tag.lower()
        if self.drop_depth:
            if tag in ACTIVE_CONTENT_TAGS and tag not in ACTIVE_VOID_TAGS:
                self.drop_depth -= 1
            return
        if tag not in ACTIVE_CONTENT_TAGS:
            self.output.append(f'</{tag}>')

    def handle_data(self, data):
        if not self.drop_depth:
            self.output.append(data)

    def handle_entityref(self, name):
        if not self.drop_depth:
            self.output.append(f'&{name};')

    def handle_charref(self, name):
        if not self.drop_depth:
            self.output.append(f'&#{name};')


def strip_active_html_from_markdown(md_content):
    """Delete active raw-HTML blocks without altering fenced or inline code."""
    protected = []

    def protect_code(match):
        token = f'PINSHU_MD2PDF_CODE_TOKEN_{len(protected)}_END'
        protected.append((token, match.group(0)))
        return token

    chunks = []
    pending = []
    fence_char = None
    fence_length = 0

    def flush_pending():
        if not pending:
            return
        text = ''.join(pending)
        pending.clear()
        text = re.sub(r'(`+)(.+?)\1', protect_code, text, flags=re.DOTALL)
        parser = _ActiveMarkdownStripper()
        parser.feed(text)
        parser.close()
        chunks.append(''.join(parser.output))

    for line in md_content.splitlines(keepends=True):
        fence = re.match(r'^ {0,3}(`{3,}|~{3,})', line)
        if fence_char is not None:
            chunks.append(line)
            if fence and fence.group(1)[0] == fence_char and len(fence.group(1)) >= fence_length:
                fence_char = None
                fence_length = 0
            continue
        if fence:
            flush_pending()
            fence_char = fence.group(1)[0]
            fence_length = len(fence.group(1))
            chunks.append(line)
        elif re.match(r'^(?: {4}|\t)', line):
            flush_pending()
            chunks.append(line)
        else:
            pending.append(line)
    flush_pending()

    stripped = ''.join(chunks)
    for token, original in protected:
        stripped = stripped.replace(token, original)
    return stripped


def _safe_url(value, attribute, base_dir=None):
    """Return a safe URL for a rendered link/image attribute, or None."""
    raw = html_lib.unescape(value or '').strip()
    compact = re.sub(r'[\x00-\x20\x7f]+', '', raw)
    if not compact:
        return None
    parts = urlsplit(compact)
    scheme = parts.scheme.lower()

    if attribute == 'href':
        if parts.netloc and not scheme:
            return None
        if scheme and scheme not in {'http', 'https', 'mailto'}:
            return None
        return compact

    if scheme == 'data':
        if re.fullmatch(
            r'data:image/(?:png|jpe?g|gif|webp|bmp);base64,[a-z0-9+/=]+',
            compact,
            flags=re.IGNORECASE,
        ):
            return compact
        return None
    if scheme or parts.netloc or compact.startswith(('/', '\\')):
        return None

    if base_dir is None:
        return compact
    base_path = Path(base_dir).resolve()
    candidate = (base_path / unquote(parts.path)).resolve()
    try:
        candidate.relative_to(base_path)
    except ValueError:
        return None
    resolved = candidate.as_uri()
    if parts.query:
        resolved += '?' + parts.query
    if parts.fragment:
        resolved += '#' + parts.fragment
    return resolved


class _AllowlistHTMLSanitizer(HTMLParser):
    """Small stdlib-only HTML allowlist sanitizer for renderer output."""

    def __init__(self, base_dir=None):
        super().__init__(convert_charrefs=True)
        self.base_dir = base_dir
        self.output = []
        self.drop_depth = 0

    def _clean_attrs(self, tag, attrs):
        allowed = GLOBAL_HTML_ATTRIBUTES | TAG_HTML_ATTRIBUTES.get(tag, set())
        cleaned = []
        for name, value in attrs:
            name = name.lower()
            if name.startswith('on') or name == 'style' or name not in allowed:
                continue
            if name in BOOLEAN_HTML_ATTRIBUTES:
                cleaned.append((name, name))
                continue
            value = value or ''
            if name in {'href', 'src'}:
                value = _safe_url(value, name, self.base_dir)
                if value is None:
                    continue
            elif name in INTEGER_HTML_ATTRIBUTES:
                if not re.fullmatch(r'\d{1,6}', value.strip()):
                    continue
                value = value.strip()
            elif name == 'align' and value.lower() not in {'left', 'center', 'right'}:
                continue
            elif name == 'scope' and value.lower() not in {'col', 'row', 'colgroup', 'rowgroup'}:
                continue
            cleaned.append((name, value))
        return ''.join(
            f' {name}="{html_lib.escape(value, quote=True)}"' for name, value in cleaned
        )

    def handle_starttag(self, tag, attrs):
        tag = tag.lower()
        if self.drop_depth:
            if tag in ACTIVE_CONTENT_TAGS and tag not in ACTIVE_VOID_TAGS:
                self.drop_depth += 1
            return
        if tag in ACTIVE_CONTENT_TAGS:
            if tag not in ACTIVE_VOID_TAGS:
                self.drop_depth = 1
            return
        if tag not in ALLOWED_HTML_TAGS:
            return
        self.output.append(f'<{tag}{self._clean_attrs(tag, attrs)}>')

    def handle_startendtag(self, tag, attrs):
        tag = tag.lower()
        if self.drop_depth or tag in ACTIVE_CONTENT_TAGS or tag not in ALLOWED_HTML_TAGS:
            return
        self.output.append(f'<{tag}{self._clean_attrs(tag, attrs)}>')

    def handle_endtag(self, tag):
        tag = tag.lower()
        if self.drop_depth:
            if tag in ACTIVE_CONTENT_TAGS and tag not in ACTIVE_VOID_TAGS:
                self.drop_depth -= 1
            return
        if tag in ALLOWED_HTML_TAGS and tag not in VOID_HTML_TAGS:
            self.output.append(f'</{tag}>')

    def handle_data(self, data):
        if not self.drop_depth:
            self.output.append(html_lib.escape(data, quote=False))


def sanitize_html(rendered_html, base_dir=None):
    """Sanitize untrusted renderer output with a conservative HTML allowlist."""
    parser = _AllowlistHTMLSanitizer(base_dir=base_dir)
    parser.feed(rendered_html)
    parser.close()
    return ''.join(parser.output)


def escape_metadata(metadata):
    """HTML-escape every extracted or command-line metadata value."""
    return {
        key: html_lib.escape(str(value), quote=True) if value is not None else None
        for key, value in metadata.items()
    }


def make_heading_id(text, fallback='section'):
    """Create a deterministic, attribute-safe heading identifier."""
    normalized = unicodedata.normalize('NFKC', html_lib.unescape(text)).casefold()
    slug = ''.join(char if char.isalnum() else '-' for char in normalized)
    slug = re.sub(r'-+', '-', slug).strip('-')[:96]
    return slug or fallback


def _text_from_html(fragment):
    return html_lib.unescape(re.sub(r'<[^>]+>', '', fragment))


def add_heading_ids(rendered_html):
    """Add deterministic IDs and presentation hooks after sanitization."""
    seen = {}

    def replace(match):
        level, attrs, inner = match.group(1), match.group(2) or '', match.group(3)
        base_id = make_heading_id(_text_from_html(inner), f'section-{level}')
        count = seen.get(base_id, 0) + 1
        seen[base_id] = count
        heading_id = base_id if count == 1 else f'{base_id}-{count}'
        attrs = re.sub(r'\s+id="[^"]*"', '', attrs)
        heading = f'<h{level}{attrs} id="{html_lib.escape(heading_id, quote=True)}">{inner}</h{level}>'
        if level == '2':
            return '<div class="chapter-break"></div>\n' + heading
        return heading

    return re.sub(r'<h([23])(\s[^>]*)?>(.*?)</h\1>', replace, rendered_html, flags=re.DOTALL)


def available_markdown_renderers():
    """Return Markdown renderers available in the current environment."""
    renderers = []
    if shutil.which('pandoc'):
        renderers.append('pandoc')
    if importlib.util.find_spec('markdown2'):
        renderers.append('markdown2')
    if importlib.util.find_spec('markdown_it'):
        renderers.append('markdown-it-py')
    return renderers


def render_markdown(md_content, base_dir=None, renderer=None):
    """Render Markdown with raw HTML disabled, then sanitize the generated HTML."""
    if renderer not in {None, 'pandoc', 'markdown2', 'markdown-it-py'}:
        raise ValueError(f'Unsupported Markdown renderer: {renderer}')
    errors = []
    md_content = strip_active_html_from_markdown(md_content)

    pandoc = shutil.which('pandoc')
    if pandoc and renderer in {None, 'pandoc'}:
        result = subprocess.run(
            [pandoc, '--from=gfm-raw_html', '--to=html5'],
            input=md_content,
            capture_output=True,
            text=True,
        )
        if result.returncode == 0:
            return sanitize_html(result.stdout, base_dir=base_dir)
        errors.append(f"Pandoc: {result.stderr.strip() or 'unknown error'}")

    if renderer in {None, 'markdown2'} and importlib.util.find_spec('markdown2'):
        try:
            import markdown2
            rendered = markdown2.markdown(
                md_content,
                safe_mode='escape',
                extras=[
                    'fenced-code-blocks',
                    'tables',
                    'break-on-newline',
                    'code-friendly',
                    'cuddled-lists',
                    'strike',
                    'task_list',
                ],
            )
            return sanitize_html(rendered, base_dir=base_dir)
        except Exception as exc:
            errors.append(f"markdown2: {exc}")

    if renderer in {None, 'markdown-it-py'} and importlib.util.find_spec('markdown_it'):
        try:
            from markdown_it import MarkdownIt
            parser = MarkdownIt('commonmark', {'html': False})
            parser.enable('table')
            parser.enable('strikethrough')
            return sanitize_html(parser.render(md_content), base_dir=base_dir)
        except Exception as exc:
            errors.append(f"markdown-it-py: {exc}")

    detail = f" Detected but failed to run: {' | '.join(errors)}" if errors else ""
    raise RuntimeError(
        "No supported Markdown renderer is available. Install one of Pandoc, markdown2, "
        f"or markdown-it-py.{detail}"
    )

def get_font_paths():
    """Return paths to installed CJK font files for @font-face embedding."""
    fonts = {}
    try:
        result = subprocess.run(['fc-match', '-v', 'PingFang SC'], capture_output=True, text=True)
        for line in result.stdout.split('\n'):
            if 'file:' in line and '.ttc' in line:
                fonts['pingfang'] = line.split('"')[1]
                break
        result = subprocess.run(['fc-match', '-v', 'Songti SC'], capture_output=True, text=True)
        for line in result.stdout.split('\n'):
            if 'file:' in line and '.ttc' in line:
                fonts['songti'] = line.split('"')[1]
                break
    except Exception:
        pass
    return fonts

def extract_metadata(md_content):
    """Extract document metadata."""
    metadata = {
        'title': None,
        'eyebrow': None,
        'subtitle': None,
        'author': None,
        'date': None,
        'created_for': None,
        'based_on': None,
    }

    # Use the first H1 as the document title.
    h1_match = re.search(r'^# (.+)$', md_content, re.MULTILINE)
    if h1_match:
        metadata['title'] = h1_match.group(1).strip()

    # Read an eyebrow from a blockquote near the top of the document.
    # Limit the search to the first three lines to avoid treating body quotations as metadata.
    first_lines = '\n'.join(md_content.split('\n')[:3])
    eyebrow_match = re.search(r'^> (.+)$', first_lines, re.MULTILINE)
    if eyebrow_match:
        eyebrow_raw = eyebrow_match.group(1).strip()
        # Strip Markdown bold and italic markers.
        eyebrow_raw = re.sub(r'\*\*(.+?)\*\*', r'\1', eyebrow_raw)
        eyebrow_raw = re.sub(r'\*(.+?)\*', r'\1', eyebrow_raw)
        metadata['eyebrow'] = eyebrow_raw

    # Extract a subtitle from a standalone line enclosed in ASCII or full-width parentheses.
    subtitle_match = re.search(r'^[\uFF08(](.+?)[\uFF09)]$', md_content, re.MULTILINE)
    if subtitle_match:
        metadata['subtitle'] = subtitle_match.group(1).strip()

    # Extract metadata written as **Field**: value.
    # Creator
    creator_match = re.search(r'\*\*(?:Creator|\u521b\u5efa\u8005)\*\*:\s*(.+?)$', md_content, re.MULTILINE)
    if creator_match:
        metadata['author'] = creator_match.group(1).strip()

    # Created for
    for_match = re.search(r'\*\*(?:Created for|\u4e3a\u8c01\u521b\u5efa)\*\*:\s*(.+?)$', md_content, re.MULTILINE)
    if for_match:
        # Extract link text and URL when present.
        link_match = re.search(r'\[(.+?)\]\((.+?)\)', for_match.group(1))
        if link_match:
            metadata['created_for'] = link_match.group(1)
            metadata['created_for_url'] = link_match.group(2)
        else:
            metadata['created_for'] = for_match.group(1).strip()

    # Based on
    based_match = re.search(r'\*\*(?:Based on|\u57fa\u4e8e)\*\*:\s*(.+?)$', md_content, re.MULTILINE)
    if based_match:
        metadata['based_on'] = based_match.group(1).strip()

    # Last updated
    date_match = re.search(r'\*\*(?:Last updated|\u6700\u540e\u66f4\u65b0)\*\*:\s*(.+?)$', md_content, re.MULTILINE)
    if date_match:
        metadata['date'] = date_match.group(1).strip()

    return metadata

def extract_toc_structure(md_content):
    """Extract the numbered heading structure used for the table of contents."""
    lines = md_content.split('\n')
    toc = []
    used_ids = {}

    def unique_id(visible_heading, fallback):
        base_id = make_heading_id(visible_heading, fallback)
        count = used_ids.get(base_id, 0) + 1
        used_ids[base_id] = count
        return base_id if count == 1 else f'{base_id}-{count}'

    for line in lines:
        # Main section: a numbered "## 1. Title" or an unnumbered "## Title".
        match_h2 = re.match(r'^## (\d+)\.\s+(.+)$', line)
        if match_h2:
            num = match_h2.group(1)
            title = match_h2.group(2).strip()
            title = re.sub(r'[\U0001F300-\U0001F9FF]', '', title).strip()
            toc.append({
                'level': 2,
                'number': num,
                'title': title,
                'id': unique_id(f'{num}. {title}', f'section-{num}')
            })
        else:
            match_h2_plain = re.match(r'^## (.+)$', line)
            if match_h2_plain:
                title = match_h2_plain.group(1).strip()
                title = re.sub(r'[\U0001F300-\U0001F9FF]', '', title).strip()
                idx = str(len([t for t in toc if t['level'] == 2]) + 1)
                toc.append({
                    'level': 2,
                    'number': idx,
                    'title': title,
                    'id': unique_id(title, f'section-{idx}')
                })

        # Subsection: a numbered "### 1.1 Title" or an unnumbered "### Title".
        match_h3 = re.match(r'^### (\d+\.\d+)\s+(.+)$', line)
        if match_h3:
            num = match_h3.group(1)
            title = match_h3.group(2).strip()
            title = re.sub(r'[\U0001F300-\U0001F9FF]', '', title).strip()
            if len(title) > 50:
                title = title[:47] + '...'
            toc.append({
                'level': 3,
                'number': num,
                'title': title,
                'id': unique_id(f'{num} {title}', f'section-{num.replace(".", "-")}')
            })
        else:
            match_h3_plain = re.match(r'^### (.+)$', line)
            if match_h3_plain:
                title = match_h3_plain.group(1).strip()
                title = re.sub(r'[\U0001F300-\U0001F9FF]', '', title).strip()
                if len(title) > 50:
                    title = title[:47] + '...'
                parent_num = str(len([t for t in toc if t['level'] == 2]))
                sub_idx = str(len([t for t in toc if t['level'] == 3 and
                                   t['number'].startswith(parent_num + '.')]) + 1)
                num = f"{parent_num}.{sub_idx}"
                toc.append({
                    'level': 3,
                    'number': num,
                    'title': title,
                    'id': unique_id(title, f'section-{num.replace(".", "-")}')
                })

    # If the document has no H2 headings, promote all H3 headings and number them in order.
    has_h2 = any(t['level'] == 2 for t in toc)
    if not has_h2:
        idx = 1
        for item in toc:
            if item['level'] == 3:
                item['level'] = 2
                item['number'] = str(idx)
                idx += 1

    return toc

def generate_toc_html(toc_items):
    """Generate table-of-contents HTML."""
    if not toc_items:
        return ""

    toc_html = ""
    for item in toc_items:
        item_id = html_lib.escape(str(item['id']), quote=True)
        number = html_lib.escape(str(item['number']), quote=False)
        title = html_lib.escape(str(item['title']), quote=False)
        page = html_lib.escape(str(item.get('page', '')), quote=False)
        if item['level'] == 2:
            toc_html += f'''
            <div class="toc-item toc-h2">
                <a href="#{item_id}" class="toc-link">
                    <span class="toc-number">{number}</span>
                    <span class="toc-title">{title}</span>
                    <span class="toc-page-num">{page}</span>
                </a>
            </div>
            '''
        else:
            toc_html += f'''
            <div class="toc-item toc-h3">
                <a href="#{item_id}" class="toc-link">
                    <span class="toc-number">{number}</span>
                    <span class="toc-title">{title}</span>
                    <span class="toc-page-num">{page}</span>
                </a>
            </div>
            '''

    return toc_html

def create_cover_and_toc(metadata, toc_html):
    """Generate the cover and table-of-contents pages."""
    title = metadata.get('title', 'Document Title')
    eyebrow = metadata.get('eyebrow', '')
    subtitle = metadata.get('subtitle', '')
    author = metadata.get('author', '')
    date = metadata.get('date', '')
    created_for = metadata.get('created_for', '')
    created_for_url = metadata.get('created_for_url', '')
    based_on = metadata.get('based_on', '')

    # Parse a subtitle such as "Foundations · Instructor: Jane Smith · Core Concepts".
    # Split course details from instructor or secondary information.
    sub_parts = [p.strip() for p in subtitle.split('·')] if subtitle else []
    class_info = sub_parts[0] if len(sub_parts) > 0 else ''
    speaker_info = ' · '.join(sub_parts[1:]) if len(sub_parts) > 1 else ''

    toc_section = ""
    if toc_html and toc_html.strip():
        toc_section = f"""
        <!-- Table of contents -->
        <div class="toc-page">
            <h2 class="toc-header">Contents</h2>
            <div class="toc-content">
                {toc_html}
            </div>
        </div>
        """

    date_label = date or ''

    return f"""
    <!-- Cover -->
    <div class="cover">
        <!-- Subtle circular background motif -->
        <div class="cover-bg-circle"></div>

        <!-- Border and corner details -->
        <div class="cover-border">
            <div class="border-corner border-corner-tl"></div>
            <div class="border-corner border-corner-tr"></div>
            <div class="border-corner border-corner-bl"></div>
            <div class="border-corner border-corner-br"></div>
        </div>

        <!-- Primary title block -->
        <div class="cover-body">
            <div class="cover-eyebrow">{eyebrow}</div>

            <!-- Diamond divider -->
            <div class="cover-rule">
                <span class="rule-line"></span>
                <span class="rule-gem">◆</span>
                <span class="rule-line"></span>
            </div>

            <h1 class="cover-title">{title}</h1>
            <p class="cover-class-info">{class_info}</p>

            <div class="cover-rule">
                <span class="rule-line"></span>
                <span class="rule-gem">◆</span>
                <span class="rule-line"></span>
            </div>

            <p class="cover-speaker">{speaker_info}</p>
        </div>

        <!-- Footer metadata -->
        <div class="cover-footer">{date_label}</div>
    </div>

    {toc_section}
    """

def process_markdown(md_content, base_dir=None):
    """Prepare Markdown content for HTML rendering."""

    # Remove the first H1 because it is already used on the cover.
    md_content = re.sub(r'^# .+?\n', '', md_content, count=1, flags=re.MULTILINE)

    # Remove the eyebrow blockquote because it is already used on the cover.
    md_content = re.sub(r'^> .+?\n', '', md_content, count=1, flags=re.MULTILINE)

    # Remove the subtitle line because it is already used on the cover.
    md_content = re.sub(r'^[\uFF08(].+?[\uFF09)]\n', '', md_content, count=1, flags=re.MULTILINE)

    # Remove leading **Field**: value metadata lines.
    # These values were moved to the cover and should not be repeated in the body.
    metadata_patterns = [
        r'^\*\*(?:Creator|\u521b\u5efa\u8005)\*\*:.+?$',
        r'^\*\*(?:Created for|\u4e3a\u8c01\u521b\u5efa)\*\*:.+?$',
        r'^\*\*(?:Based on|\u57fa\u4e8e)\*\*:.+?$',
        r'^\*\*(?:Last updated|\u6700\u540e\u66f4\u65b0)\*\*:.+?$',
        r'^\*\*(?:Use cases|\u9002\u7528\u573a\u666f)\*\*:.+?$',
    ]
    for pattern in metadata_patterns:
        md_content = re.sub(pattern, '', md_content, flags=re.MULTILINE)

    # Remove emoji across the commonly used Unicode ranges.
    md_content = re.sub(
        r'[\U0001F300-\U0001FAFF'   # Miscellaneous symbols, pictographs, and transport
        r'\U00002600-\U000027BF'    # Miscellaneous symbols
        r'\U00002B00-\U00002BFF'    # Supplemental arrows and symbols
        r'\U0000FE00-\U0000FE0F'    # Variation selectors
        r'\U0001F000-\U0001F02F'    # Mahjong tiles
        r']',
        '', md_content
    )

    # Render Markdown, falling back from Pandoc to markdown2 to markdown-it-py.
    html = render_markdown(md_content, base_dir=base_dir)
    html = add_heading_ids(html)

    # Apply presentation hooks to rendered elements.
    html = re.sub(r'<table(?: class="([^"]*)")?>', lambda match: (
        f'<table class="{match.group(1)} content-table">' if match.group(1)
        else '<table class="content-table">'
    ), html)
    html = re.sub(r'<pre(?: class="([^"]*)")?>', lambda match: (
        f'<pre class="{match.group(1)} code-block">' if match.group(1)
        else '<pre class="code-block">'
    ), html)
    html = re.sub(r'<blockquote(?: class="([^"]*)")?>', lambda match: (
        f'<blockquote class="{match.group(1)} quote-block">' if match.group(1)
        else '<blockquote class="quote-block">'
    ), html)

    return html

def get_apple_css():
    """Return PDF rendering CSS for the default East Asian editorial cover.

    Font strategy for reducing CJK mojibake in iOS PDFKit:
      - Embed Songti SC through @font-face.
        WeasyPrint should emit CID TrueType fonts with Identity-H encoding.
      - Avoid the PingFang SC path, which is known to produce problematic encoding.
      - Exclude -apple-system and BlinkMacSystemFont from every font-family declaration
        so WeasyPrint does not embed .SFNS as a Type 3 font.
    """
    import os
    font_dir = os.path.expanduser('~/.workbuddy/fonts')
    font_faces = ""

    # Songti SC Regular and Bold should render as CID TrueType.
    st_reg = os.path.join(font_dir, 'Songti-SC-Regular.ttf')
    st_bold = os.path.join(font_dir, 'Songti-SC-Bold.ttf')

    if os.path.isfile(st_reg):
        font_faces += "@font-face {\n"
        font_faces += "    font-family: 'Songti SC';\n"
        font_faces += "    font-weight: 400;\n"
        font_faces += f"    src: url('file://{st_reg}');\n"
        font_faces += "}\n"
    if os.path.isfile(st_bold):
        font_faces += "@font-face {\n"
        font_faces += "    font-family: 'Songti SC';\n"
        font_faces += "    font-weight: 700;\n"
        font_faces += f"    src: url('file://{st_bold}');\n"
        font_faces += "}\n"

    return font_faces + """
    @page {
        size: A4;
        margin: 2.5cm 2cm 2cm 2cm;

        @top-left {
            content: string(doc-title);
            font-size: 8.5pt;
            color: #86868b;
            font-family: 'Songti SC', serif;
        }

        @top-right {
            content: counter(page);
            font-size: 8.5pt;
            color: #86868b;
            font-family: 'Songti SC', serif;
        }
    }

    @page:first {
        margin: 0;
        @top-left { content: none; }
        @top-right { content: none; }
    }

    @page:nth(2) {
        @top-left { content: none; }
        @top-right { content: none; }
    }

    * {
        margin: 0;
        padding: 0;
        box-sizing: border-box;
    }

    body {
        font-family: 'Songti SC', serif;
        font-size: 11pt;
        line-height: 1.7;
        color: #1d1d1f;
        background: white;
        -webkit-font-smoothing: antialiased;
    }

    /* ============================================================
       Cover — East Asian paper-and-ink style with restrained seal-red accents
       ============================================================ */
    .cover {
        height: 297mm;
        background-color: #faf8f3;
        page-break-after: always;
        position: relative;
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        overflow: hidden;
    }

    /* Small, subtle circular motif in the lower-right corner */
    .cover-bg-circle {
        position: absolute;
        bottom: 72px;
        right: 64px;
        width: 48px;
        height: 48px;
        border-radius: 50%;
        border: 1px solid rgba(60, 50, 40, 0.08);
        pointer-events: none;
    }
    .cover-bg-circle::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 24px;
        border-radius: 24px 24px 0 0;
        border-bottom: 1px solid rgba(60, 50, 40, 0.06);
        background: rgba(60, 50, 40, 0.03);
    }

    /* Fine ink-toned border */
    .cover-border {
        position: absolute;
        inset: 32px;
        border: 1.5px solid rgba(60, 50, 40, 0.15);
        pointer-events: none;
    }

    /* Dark L-shaped corner details */
    .border-corner {
        position: absolute;
        width: 20px;
        height: 20px;
    }
    .border-corner-tl { top: -1px; left: -1px; border-top: 2.5px solid rgba(60,50,40,0.5); border-left: 2.5px solid rgba(60,50,40,0.5); }
    .border-corner-tr { top: -1px; right: -1px; border-top: 2.5px solid rgba(60,50,40,0.5); border-right: 2.5px solid rgba(60,50,40,0.5); }
    .border-corner-bl { bottom: -1px; left: -1px; border-bottom: 2.5px solid rgba(60,50,40,0.5); border-left: 2.5px solid rgba(60,50,40,0.5); }
    .border-corner-br { bottom: -1px; right: -1px; border-bottom: 2.5px solid rgba(60,50,40,0.5); border-right: 2.5px solid rgba(60,50,40,0.5); }

    /* Cover body */
    .cover-body {
        position: relative;
        z-index: 1;
        text-align: center;
        padding: 0 64px;
    }

    /* Eyebrow */
    .cover-eyebrow {
        font-size: 10pt;
        color: rgba(60, 50, 40, 0.6);
        letter-spacing: 10px;
        margin-bottom: 32px;
        font-weight: 400;
    }

    /* Gradient divider */
    .cover-rule {
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 16px;
        margin: 20px 0;
    }
    .rule-line {
        flex: 1;
        max-width: 90px;
        height: 1px;
        background: linear-gradient(to right, transparent, rgba(60,50,40,0.3));
    }
    .cover-rule:last-child .rule-line {
        background: linear-gradient(to left, transparent, rgba(60,50,40,0.3));
    }
    .rule-gem {
        color: rgba(60, 50, 40, 0.4);
        font-size: 8pt;
    }

    /* Main title */
    .cover-title {
        font-size: 42pt;
        font-weight: 700;
        color: #2c2418;
        line-height: 1.25;
        letter-spacing: 6px;
        font-family: serif;
        string-set: doc-title content();
        margin: 4px 0;
    }

    /* Course details beneath the title */
    .cover-class-info {
        font-size: 11pt;
        color: rgba(60, 50, 40, 0.5);
        letter-spacing: 6px;
        margin-top: 14px;
        margin-bottom: 0;
        font-weight: 400;
        font-family: serif;
    }

    /* Instructor or secondary information */
    .cover-speaker {
        font-size: 9.5pt;
        color: rgba(60, 50, 40, 0.4);
        letter-spacing: 3px;
        margin-top: 8px;
        font-weight: 400;
    }

    /* Footer date */
    .cover-footer {
        position: absolute;
        bottom: 48px;
        left: 0;
        right: 0;
        text-align: center;
        font-size: 8.5pt;
        color: rgba(60, 50, 40, 0.25);
        letter-spacing: 4px;
    }

    /* ============================================================
       Table of contents
       ============================================================ */
    .toc-page {
        padding: 60px 50px;
        page-break-after: always;
        min-height: 100vh;
    }

    .toc-header {
        font-size: 28pt;
        font-weight: 600;
        color: #1d1d1f;
        margin-bottom: 32px;
    }

    .toc-content {
        column-count: 2;
        column-gap: 40px;
    }

    .toc-item {
        break-inside: avoid;
        margin-bottom: 6px;
    }

    .toc-h2 {
        margin-top: 14px;
        margin-bottom: 4px;
    }

    .toc-h2 .toc-link {
        font-size: 11.5pt;
        font-weight: 600;
        color: #1d1d1f;
    }

    .toc-h2 .toc-number {
        color: #6B4C3B;
        font-weight: 700;
        margin-right: 8px;
    }

    .toc-h3 {
        margin-left: 16px;
    }

    .toc-h3 .toc-link {
        font-size: 10pt;
        font-weight: 400;
        color: #424245;
    }

    .toc-h3 .toc-number {
        color: #86868b;
        margin-right: 6px;
        font-size: 9.5pt;
    }

    .toc-link {
        display: flex;
        align-items: baseline;
        text-decoration: none;
        padding: 4px 0;
    }

    .toc-number {
        font-feature-settings: "tnum";
        min-width: 2.8em;
        flex-shrink: 0;
    }

    /* ============================================================
       Body styles
       ============================================================ */
    /* Headings */
    .chapter-break {
        page-break-before: always;
        height: 0;
    }

    h2 {
        font-size: 22pt;
        font-weight: 600;
        color: #1d1d1f;
        margin-top: 0;
        margin-bottom: 28px;
        padding-bottom: 12px;
        border-bottom: 2px solid #d2d2d7;
        page-break-after: avoid;
    }

    h3 {
        font-size: 17pt;
        font-weight: 600;
        color: #1d1d1f;
        margin-top: 36px;
        margin-bottom: 18px;
        page-break-after: avoid;
    }

    h4 {
        font-size: 13pt;
        font-weight: 600;
        color: #424245;
        margin-top: 24px;
        margin-bottom: 12px;
        page-break-after: avoid;
    }

    /* Body copy */
    p {
        margin-bottom: 16px;
    }

    ul, ol {
        margin-left: 24px;
        margin-bottom: 20px;
    }

    li {
        margin-bottom: 10px;
    }

    /* Code blocks */
    .code-block {
        background: #f5f5f7;
        border: 1px solid #d2d2d7;
        border-radius: 8px;
        padding: 20px;
        margin: 24px 0;
        overflow-x: auto;
        font-family: monospace;
        font-size: 10pt;
        line-height: 1.6;
        page-break-inside: avoid;
    }

    .code-block code {
        background: none;
        padding: 0;
        color: #1d1d1f;
    }

    code {
        background: #f5f5f7;
        padding: 3px 6px;
        border-radius: 4px;
        font-family: monospace;
        font-size: 10pt;
        color: #d70050;
        font-weight: 500;
    }

    /* Tables — compact type accommodates wide tables */
    .content-table {
        width: 100%;
        border-collapse: collapse;
        margin: 20px 0;
        font-size: 8.5pt;
        table-layout: fixed;
    }

    .content-table thead {
        background: #f5f5f7;
    }

    .content-table th {
        padding: 8px 4px;
        text-align: center;
        font-weight: 600;
        border-bottom: 2px solid #d2d2d7;
        font-size: 8pt;
        word-wrap: break-word;
    }

    .content-table td {
        padding: 6px 4px;
        text-align: center;
        border-bottom: 1px solid #d2d2d7;
        color: #424245;
        font-size: 8.5pt;
        word-wrap: break-word;
    }

    /* Blockquotes */
    .quote-block {
        border-left: 3px solid #6B4C3B;
        margin: 24px 0;
        color: #424245;
        background: #FAF8F5;
        padding: 0.8em 1.2em 0.8em 1.6em;
        page-break-inside: avoid;
    }

    /* Emphasis */
    strong {
        color: #1d1d1f;
        font-weight: 600;
    }

    a {
        color: #06c;
        text-decoration: none;
    }

    hr {
        border: none;
        border-top: 1px solid #d2d2d7;
        margin: 36px 0;
    }

    /* Print-quality controls */
    p, li, .quote-block {
        orphans: 3;
        widows: 3;
    }

    h2, h3, h4 {
        page-break-after: avoid;
    }

    .code-block, .content-table, .quote-block {
        page-break-inside: avoid;
    }
    """

KUNLUN_TAIJI_SVG = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100">
  <circle cx="50" cy="50" r="49.5" fill="white" stroke="#3D2B1F" stroke-width="1"/>
  <path d="M50,0 A25,25,0,0,1,50,50 A25,25,0,0,0,50,100 A50,50,0,0,1,50,0 Z" fill="#1a1a1a"/>
  <circle cx="50" cy="25" r="8.33" fill="white"/>
  <circle cx="50" cy="75" r="8.33" fill="#1a1a1a"/>
  <circle cx="50" cy="50" r="49.5" fill="none" stroke="#3D2B1F" stroke-width="1"/>
</svg>"""


def get_kunlun_css():
    """Return CSS for the Kunlun theme.
    Intended for traditional-culture material and course handouts.
    Style: warm ivory ground, dark brown section rules, gold accents, and serif body text.
    """
    font_dir = os.path.expanduser('~/.workbuddy/fonts')
    st_reg = os.path.join(font_dir, 'Songti-SC-Regular.ttf')
    st_bold = os.path.join(font_dir, 'Songti-SC-Bold.ttf')
    font_faces = ""
    if os.path.isfile(st_reg):
        font_faces += f"@font-face {{ font-family: 'Songti SC'; font-weight: 400; src: url('file://{st_reg}'); }}\n"
    if os.path.isfile(st_bold):
        font_faces += f"@font-face {{ font-family: 'Songti SC'; font-weight: 700; src: url('file://{st_bold}'); }}\n"

    return font_faces + """
    :root {
        --bg: #faf8f3;
        --text: #3D2B1F;
        --accent: #C8960C;
        --rule-color: #7B3F1E;
        --light-border: #DDD0BC;
        --subtle: #8B6F5E;
    }

    * { box-sizing: border-box; margin: 0; padding: 0; }

    @page {
        size: A4;
        margin: 22mm 28mm 22mm 28mm;
        @top-left {
            content: string(doc-title);
            font-size: 8pt;
            color: #8B6F5E;
            font-family: 'Songti SC', serif;
        }
        @top-right {
            content: counter(page);
            font-size: 8pt;
            color: #8B6F5E;
            font-family: 'Songti SC', serif;
        }
    }
    @page:first { margin: 0; @top-left { content: none; } @top-right { content: none; } }
    @page:nth(2) { @top-left { content: none; } @top-right { content: none; } }

    body {
        font-family: 'STHeiti', 'STXihei', sans-serif;
        font-size: 10.5pt;
        line-height: 2.8;
        letter-spacing: 0.05em;
        color: var(--text);
        background: var(--bg);
    }

    /* ===== Cover ===== */
    .cover {
        height: 297mm;
        background: var(--bg);
        page-break-after: always;
        display: flex;
        flex-direction: column;
        align-items: center;
        padding: 30mm 24mm 18mm 24mm;
        position: relative;
    }
    .cover-border-outer {
        position: absolute;
        top: 11mm; left: 11mm; right: 11mm; bottom: 11mm;
        border: 1.5px solid var(--light-border);
        pointer-events: none;
    }
    .cover-border-inner {
        position: absolute;
        top: 13.5mm; left: 13.5mm; right: 13.5mm; bottom: 13.5mm;
        border: 0.5px solid var(--light-border);
        pointer-events: none;
    }
    .cover-eyebrow {
        font-size: 9.5pt;
        color: var(--subtle);
        letter-spacing: 0.35em;
        margin-bottom: 8mm;
        text-align: center;
        string-set: doc-title content();
    }
    .cover-title {
        font-size: 36pt;
        font-weight: 700;
        color: var(--text);
        text-align: center;
        letter-spacing: 0.18em;
        margin-bottom: 3mm;
        line-height: 1.25;
    }
    .cover-class-info {
        font-size: 10.5pt;
        color: var(--subtle);
        text-align: center;
        letter-spacing: 0.25em;
        margin-bottom: 8mm;
    }
    .cover-taiji {
        width: 50mm;
        height: 50mm;
        margin: 4mm 0 8mm 0;
    }
    .cover-divider {
        width: 55mm;
        height: 0;
        border-top: 1px solid var(--light-border);
        margin: 4mm 0;
    }
    .cover-speaker {
        font-size: 10.5pt;
        color: var(--text);
        text-align: center;
        letter-spacing: 0.18em;
        line-height: 2.1;
        margin-top: 2mm;
    }
    .cover-footer {
        position: absolute;
        bottom: 22mm;
        left: 0; right: 0;
        text-align: center;
        font-size: 9pt;
        color: var(--accent);
        letter-spacing: 0.35em;
    }

    /* ===== Table of contents ===== */
    .toc-page {
        padding: 8mm 0;
        page-break-after: always;
    }
    .toc-header {
        font-size: 17pt;
        font-weight: 700;
        color: var(--text);
        text-align: center;
        letter-spacing: 0.4em;
        margin-bottom: 6mm;
        padding-bottom: 4mm;
        border-bottom: 1px solid var(--light-border);
    }
    .toc-h2 { margin-bottom: 2px; }
    .toc-link {
        display: flex;
        text-decoration: none;
        color: var(--text);
        font-size: 10.5pt;
        line-height: 1.9;
        padding: 1px 0;
    }
    .toc-number { min-width: 2.8em; color: var(--accent); font-weight: 700; flex-shrink: 0; }
    .toc-title { flex: 1; }
    .toc-page-num { color: var(--subtle); margin-left: 8px; flex-shrink: 0; }

    /* ===== Body ===== */
    .content { padding-top: 2mm; }
    .chapter-break { height: 0; }

    h2 {
        font-size: 15pt;
        font-weight: 700;
        color: var(--text);
        border-left: 3.5px solid var(--rule-color);
        padding-left: 10px;
        margin-top: 44px;
        margin-bottom: 18px;
        line-height: 1.4;
        page-break-after: avoid;
    }
    h3 {
        font-size: 13pt;
        font-weight: 700;
        color: #5C3015;
        margin-top: 28px;
        margin-bottom: 12px;
        page-break-after: avoid;
    }
    h4 {
        font-size: 11pt;
        font-weight: 700;
        color: var(--text);
        margin-top: 20px;
        margin-bottom: 10px;
    }
    p { margin-bottom: 24px; text-align: justify; }
    hr { border: none; border-top: 1px solid var(--light-border); margin: 28px 0; }

    .quote-block {
        border-left: 1.5px solid var(--accent);
        padding: 2px 12px;
        margin: 12px 0;
        color: var(--subtle);
        font-size: 10.5pt;
        line-height: 1.75;
        page-break-inside: avoid;
    }
    .content-table {
        width: 100%;
        border-collapse: collapse;
        margin: 14px 0;
        font-size: 10.5pt;
        table-layout: auto;
        page-break-inside: avoid;
    }
    .content-table thead { display: table-header-group; }
    .content-table th {
        background: #EDE3D6;
        color: var(--text);
        font-weight: 700;
        padding: 7px 10px;
        border: 1px solid var(--light-border);
        text-align: left;
    }
    .content-table td {
        padding: 6px 10px;
        border: 1px solid var(--light-border);
        vertical-align: top;
    }
    .content-table tr:nth-child(even) td { background: #F5EFE6; }
    .code-block {
        background: #EDE8DF;
        border: 1px solid var(--light-border);
        border-radius: 4px;
        padding: 12px 16px;
        margin: 12px 0;
        font-size: 9.5pt;
        page-break-inside: avoid;
    }
    code {
        font-family: 'SF Mono', 'Monaco', monospace;
        font-size: 9.5pt;
        background: #EDE8DF;
        padding: 1px 4px;
        border-radius: 3px;
    }
    ul, ol { margin: 14px 0 24px 1.5em; }
    li { margin-bottom: 10px; line-height: 2.6; }
    strong { font-weight: 700; color: #2D1A0E; }
    """


def get_kunlun_chrome_css():
    """Return Chrome-specific CSS for the Kunlun theme.
    It uses the system STXihei/STHeiti stack instead of a custom @font-face,
    following the default theme path to target CIDFont TrueType with Identity-H encoding.
    """
    css = get_kunlun_css()
    css = re.sub(r'content:\s*string\([^)]+\);', 'content: none;', css)
    css = re.sub(r'string-set:[^;]+;', '', css)
    css = re.sub(r'@page:nth\(\d+\)\s*\{[^}]+\}', '', css)
    css = re.sub(r'@font-face\s*\{[^}]+\}', '', css, flags=re.DOTALL)

    # Use !important to enforce the STXihei stack, line height, and paragraph spacing.
    chrome_fixes = """
    body, h1, h2, h3, h4, p, li, td, th, .toc-link, .cover-title,
    .cover-eyebrow, .cover-class-info, .cover-speaker, .cover-footer {
        font-family: 'STXihei', 'STHeiti', sans-serif !important;
    }
    body {
        line-height: 2.2 !important;
        letter-spacing: 0.05em !important;
    }
    p {
        margin-bottom: 16px !important;
        line-height: 2.2 !important;
    }
    li {
        line-height: 2.1 !important;
        margin-bottom: 6px !important;
    }
    .quote-block {
        line-height: 1.75 !important;
        padding: 2px 12px !important;
        margin: 12px 0 !important;
        border-left: 1.5px solid #C8960C !important;
    }
    blockquote, blockquote p {
        line-height: 1.9 !important;
        margin-bottom: 0 !important;
    }
    h2 {
        margin-top: 36px !important;
        margin-bottom: 14px !important;
    }
    h3 {
        margin-top: 22px !important;
        margin-bottom: 10px !important;
    }
    .cover {
        height: 297mm;
        break-after: page !important;
        page-break-after: always !important;
    }
    .toc-page {
        min-height: 0 !important;
        break-after: page !important;
        page-break-after: always !important;
    }
    .content-table { table-layout: auto !important; }
    """
    return css + chrome_fixes


def create_kunlun_cover_and_toc(metadata, toc_html):
    """Generate Kunlun cover and table-of-contents HTML."""
    title = metadata.get('title') or 'Document Title'
    eyebrow = metadata.get('eyebrow') or ''
    subtitle = metadata.get('subtitle') or ''
    date = metadata.get('date') or ''

    sub_parts = [p.strip() for p in subtitle.split('·')] if subtitle else []
    class_info = sub_parts[0] if len(sub_parts) > 0 else ''
    speaker_info = ' · '.join(sub_parts[1:]) if len(sub_parts) > 1 else ''

    toc_section = ""
    if toc_html and toc_html.strip():
        toc_section = f"""
        <div class="toc-page">
            <h2 class="toc-header">Contents</h2>
            <div class="toc-content">{toc_html}</div>
        </div>"""

    return f"""
    <div class="cover">
        <div class="cover-border-outer"></div>
        <div class="cover-border-inner"></div>
        <div class="cover-eyebrow">{eyebrow}</div>
        <h1 class="cover-title">{title}</h1>
        <p class="cover-class-info">{class_info}</p>
        <div class="cover-divider"></div>
        <div class="cover-taiji">{KUNLUN_TAIJI_SVG}</div>
        <div class="cover-divider"></div>
        <div class="cover-speaker">{speaker_info}</div>
        <div class="cover-footer">{date}</div>
    </div>
    {toc_section}"""


def get_business_css():
    """Return CSS for the unbranded business proposal theme."""
    return """
    :root {
        --bg: #ffffff;
        --text: #231815;
        --accent: #F5E020;
        --accent-dark: #D4C010;
        --subtle: #888888;
        --border: #E0E0E0;
        --cover-bg: #231815;
        --cover-text: #ffffff;
    }

    * { box-sizing: border-box; margin: 0; padding: 0; }

    @page {
        size: A4;
        margin: 22mm 26mm 22mm 26mm;
        @top-left {
            content: string(doc-title);
            font-size: 8pt;
            color: #888888;
            font-family: 'STHeiti', sans-serif;
        }
        @top-right {
            content: counter(page);
            font-size: 8pt;
            color: #888888;
            font-family: 'STHeiti', sans-serif;
        }
    }
    @page:first { margin: 0; @top-left { content: none; } @top-right { content: none; } }
    @page:nth(2) { @top-left { content: none; } @top-right { content: none; } }

    body {
        font-family: 'STHeiti', 'STXihei', sans-serif;
        font-size: 12pt;
        line-height: 2.2;
        letter-spacing: 0.04em;
        color: var(--text);
        background: var(--bg);
    }

    /* ===== Cover — dark field with a yellow geometric circle ===== */
    img { border: none; outline: none; box-shadow: none; display: block; }
    .cover {
        height: 297mm;
        background: var(--cover-bg);
        page-break-after: always;
        position: relative;
        overflow: hidden;
        display: flex;
        flex-direction: column;
    }
    /* Absolutely positioned geometry does not affect the flex layout. */
    .cover-circle {
        position: absolute;
        top: 38mm; right: -53mm;
        width: 106mm; height: 106mm;
        border-radius: 50%;
        background: var(--accent);
    }
    .cover-ring {
        position: absolute;
        top: 24mm; right: -67mm;
        width: 134mm; height: 134mm;
        border-radius: 50%;
        border: 0.8px solid rgba(255,255,255,0.15);
        background: transparent;
    }
    /* Flex regions */
    .cover-spacer { flex: 0 0 180mm; }
    .cover-body {
        padding: 0 16mm 0;
        flex-shrink: 0;
    }
    .cover-label {
        font-size: 7.5pt;
        color: rgba(245,224,32,0.65);
        letter-spacing: 0.35em;
        margin-bottom: 4mm;
        string-set: doc-title content();
    }
    .cover-title {
        font-size: 30pt;
        font-weight: 700;
        color: #ffffff;
        line-height: 1.28;
        letter-spacing: 0.02em;
        margin-bottom: 5mm;
    }
    .cover-rule {
        width: 10mm; height: 3px;
        background: var(--accent);
    }
    .cover-subtitle {
        font-size: 10pt;
        color: rgba(255,255,255,0.45);
        margin-top: 4mm;
    }
    .cover-footer-bar {
        position: absolute;
        left: 16mm; right: 16mm; bottom: 9mm;
        padding-top: 3mm;
        border-top: 1px solid rgba(245,224,32,0.2);
        display: flex;
        justify-content: flex-start;
        align-items: center;
    }
    .cover-footer-text {
        font-size: 7.5pt;
        color: rgba(255,255,255,0.3);
        letter-spacing: 0.08em;
    }

    /* ===== Table of contents ===== */
    .toc-page {
        padding: 8mm 0;
        page-break-after: always;
    }
    .toc-header {
        font-size: 16pt;
        font-weight: 700;
        color: var(--text);
        letter-spacing: 0.2em;
        margin-bottom: 6mm;
        padding-bottom: 3mm;
        border-bottom: 2px solid var(--text);
    }
    .toc-link {
        display: flex;
        text-decoration: none;
        color: var(--text);
        font-size: 10pt;
        line-height: 2.0;
        padding: 1px 0;
    }
    .toc-number { min-width: 2.8em; color: var(--accent-dark); font-weight: 700; flex-shrink: 0; }
    .toc-title { flex: 1; }
    .toc-h3 .toc-link { padding-left: 2em; color: var(--subtle); font-size: 9.5pt; }
    .toc-page-num { color: var(--subtle); margin-left: 8px; flex-shrink: 0; }

    /* ===== Body ===== */
    .content { padding-top: 2mm; }
    .chapter-break { height: 0; }

    h2 {
        font-size: 15pt;
        font-weight: 700;
        color: var(--text);
        margin-top: 36px;
        margin-bottom: 14px;
        padding-bottom: 5px;
        border-bottom: 2px solid var(--text);
        line-height: 1.4;
        page-break-after: avoid;
    }
    h3 {
        font-size: 12.5pt;
        font-weight: 700;
        color: var(--text);
        margin-top: 22px;
        margin-bottom: 10px;
        padding-left: 8px;
        border-left: 3px solid var(--accent);
        page-break-after: avoid;
    }
    h4 {
        font-size: 10.5pt;
        font-weight: 700;
        color: var(--subtle);
        margin-top: 16px;
        margin-bottom: 8px;
    }
    p { margin-bottom: 16px; text-align: justify; }
    hr { border: none; border-top: 1px solid var(--border); margin: 22px 0; }

    .quote-block {
        border-left: 3px solid var(--accent);
        background: #FAFAF0;
        padding: 5px 14px;
        margin: 12px 0;
        color: var(--text);
        font-size: 10pt;
        line-height: 1.9;
        page-break-inside: avoid;
    }

    ul, ol { margin: 10px 0 16px 1.6em; }
    li { margin-bottom: 6px; line-height: 2.1; }

    .content-table {
        width: 100%;
        border-collapse: collapse;
        margin: 14px 0;
        font-size: 10pt;
        table-layout: auto;
        page-break-inside: avoid;
    }
    .content-table thead { display: table-header-group; }
    .content-table th {
        background: var(--text);
        color: #ffffff;
        font-weight: 700;
        padding: 7px 10px;
        border: 1px solid var(--text);
        text-align: left;
    }
    .content-table td {
        padding: 6px 10px;
        border: 1px solid var(--border);
        vertical-align: top;
    }
    .content-table tr:nth-child(even) td { background: #F8F8F8; }

    .code-block {
        background: #F5F5F5;
        border: 1px solid var(--border);
        border-left: 3px solid var(--accent);
        border-radius: 0 4px 4px 0;
        padding: 10px 14px;
        margin: 12px 0;
        font-size: 9.5pt;
        line-height: 1.7;
        page-break-inside: avoid;
    }
    code {
        font-family: 'SF Mono', 'Monaco', monospace;
        font-size: 9.5pt;
        background: #F5F5F5;
        padding: 1px 5px;
        border-radius: 3px;
    }
    strong { font-weight: 700; }
    """


def get_business_chrome_css():
    css = get_business_css()
    css = re.sub(r'content:\s*string\([^)]+\);', 'content: none;', css)
    css = re.sub(r'string-set:[^;]+;', '', css)
    css = re.sub(r'@page:nth\(\d+\)\s*\{[^}]+\}', '', css)
    css = re.sub(r'@font-face\s*\{[^}]+\}', '', css, flags=re.DOTALL)
    chrome_fixes = """
    body, h1, h2, h3, h4, p, li, td, th, .toc-link, .cover-title,
    .cover-label, .cover-subtitle, .cover-footer-text {
        font-family: 'STXihei', 'STHeiti', sans-serif !important;
    }
    body { line-height: 2.2 !important; }
    p { margin-bottom: 16px !important; line-height: 2.2 !important; }
    li { line-height: 2.1 !important; margin-bottom: 6px !important; }
    h2 { margin-top: 36px !important; margin-bottom: 14px !important; }
    h3 { margin-top: 22px !important; margin-bottom: 10px !important; }
    .quote-block { line-height: 1.9 !important; }
    .cover { height: 297mm; break-after: page !important; }
    .toc-page { min-height: 0 !important; break-after: page !important; }
    .content-table { table-layout: auto !important; }
    """
    return css + chrome_fixes


def create_business_cover_and_toc(metadata, toc_html):
    title    = metadata.get('title') or 'Brand Proposal'
    label    = metadata.get('eyebrow') or 'PROPOSAL'
    subtitle = metadata.get('subtitle') or ''
    date     = metadata.get('date') or ''
    author   = metadata.get('author') or ''

    footer_right = ' · '.join(p for p in [author, date] if p)

    toc_section = ""
    if toc_html and toc_html.strip():
        toc_section = f"""
        <div class="toc-page">
            <h2 class="toc-header">Contents</h2>
            <div class="toc-content">{toc_html}</div>
        </div>"""

    subtitle_html = f'<p class="cover-subtitle">{subtitle}</p>' if subtitle else ''

    return f"""
    <div class="cover">
    <div class="cover-ring"></div>
    <div class="cover-circle"></div>
    <div class="cover-spacer"></div>
        <div class="cover-body">
            <div class="cover-label">{label}</div>
            <h1 class="cover-title">{title}</h1>
            <div class="cover-rule"></div>
            {subtitle_html}
        </div>
        <div class="cover-footer-bar">
            <span class="cover-footer-text">{footer_right}</span>
        </div>
    </div>
    {toc_section}"""


MANUAL_PALETTES = {
    'manual':        {'accent': '#6B8C5A', 'light': '#EEF2E8', 'mid': '#C4D4B4', 'subtle': '#8A9E80', 'border': '#D0DAC4', 'text': '#2D3A35'},
    'manual-orange': {'accent': '#E07258', 'light': '#FBEEE9', 'mid': '#F0C4B4', 'subtle': '#C06448', 'border': '#E8C8BC', 'text': '#2D1A10'},
    'manual-blue':   {'accent': '#5B9EC8', 'light': '#E8F3F9', 'mid': '#B8D8EC', 'subtle': '#7AAEC8', 'border': '#C4DFF0', 'text': '#1A2D3A'},
}


def get_manual_css(theme='manual'):
    """Return CSS for the lightweight three-palette manual theme."""
    p = MANUAL_PALETTES.get(theme, MANUAL_PALETTES['manual'])
    css = _get_manual_css_base()
    css = css.replace('__ACCENT__', p['accent'])
    css = css.replace('__LIGHT__',  p['light'])
    css = css.replace('__MID__',    p['mid'])
    css = css.replace('__SUBTLE__', p['subtle'])
    css = css.replace('__BORDER__', p['border'])
    css = css.replace('__TEXT__',   p['text'])
    css = css.replace('__COVER_BG__', p['accent'])
    return css


def _get_manual_css_base():
    # Embed the Hei sans-serif font.
    import os
    font_dir = os.path.expanduser('~/.workbuddy/fonts')
    font_faces = ""

    hei_reg = os.path.join(font_dir, 'Hei-Regular.ttf')

    if os.path.isfile(hei_reg):
        font_faces += "@font-face {\n"
        font_faces += "    font-family: 'Hei';\n"
        font_faces += "    font-weight: 400;\n"
        font_faces += f"    src: url('file://{hei_reg}');\n"
        font_faces += "}\n"
        # Reuse the regular file for bold; WeasyPrint synthesizes the heavier weight.
        font_faces += "@font-face {\n"
        font_faces += "    font-family: 'Hei';\n"
        font_faces += "    font-weight: 700;\n"
        font_faces += f"    src: url('file://{hei_reg}');\n"
        font_faces += "}\n"

    return font_faces + """
    :root {
        --bg: #ffffff;
        --text: __TEXT__;
        --accent: __ACCENT__;
        --accent-light: __LIGHT__;
        --accent-mid: __MID__;
        --subtle: __SUBTLE__;
        --border: __BORDER__;
        --warn-bg: #FDF5E6;
        --warn-border: #E6A817;
        --tip-bg: __LIGHT__;
        --tip-border: __ACCENT__;
        --note-bg: #F0F2F8;
        --note-border: #6B7FC4;
    }

    * { box-sizing: border-box; margin: 0; padding: 0; }

    @page {
        size: A4;
        margin: 22mm 26mm 22mm 26mm;
        @top-left {
            content: string(doc-title);
            font-size: 8pt;
            color: #7A9490;
            font-family: 'Hei', sans-serif;
        }
        @top-right {
            content: counter(page);
            font-size: 8pt;
            color: #7A9490;
            font-family: 'Hei', sans-serif;
        }
    }
    @page:first { margin: 0; @top-left { content: none; } @top-right { content: none; } }
    @page:nth(2) { @top-left { content: none; } @top-right { content: none; } }

    body {
        font-family: 'Hei', 'Hiragino Sans GB', 'STHeiti', sans-serif;
        font-size: 10.5pt;
        line-height: 2.0;
        letter-spacing: 0.02em;
        color: var(--text);
        background: var(--bg);
    }

    /* ===== Cover ===== */
    .cover {
        height: 297mm;
        background: __COVER_BG__;
        page-break-after: always;
        display: flex;
        flex-direction: column;
        justify-content: flex-end;
        position: relative;
        overflow: hidden;
    }
    .cover-deco {
        position: absolute;
        top: 10mm;
        right: 10mm;
        width: 120mm;
        height: 120mm;
        pointer-events: none;
    }
    .cover-deco svg { width: 100%; height: 100%; }
    .cover-body {
        padding: 0 20mm 18mm 20mm;
    }
    .cover-label {
        display: inline-block;
        font-size: 8.5pt;
        color: rgba(255,255,255,0.85);
        letter-spacing: 0.25em;
        border: 1px solid rgba(255,255,255,0.4);
        border-radius: 20px;
        padding: 3px 12px;
        margin-bottom: 6mm;
        string-set: doc-title content();
    }
    .cover-title {
        font-size: 36pt;
        font-weight: 700;
        color: #ffffff;
        line-height: 1.2;
        letter-spacing: 0.04em;
        margin-bottom: 4mm;
    }
    .cover-subtitle {
        font-size: 12pt;
        color: rgba(255,255,255,0.75);
        letter-spacing: 0.08em;
        margin-bottom: 6mm;
    }
    .cover-divider {
        width: 10mm;
        height: 2.5px;
        background: rgba(255,255,255,0.6);
        border-radius: 2px;
    }
    .cover-footer-bar {
        background: rgba(0,0,0,0.15);
        padding: 4mm 20mm;
        display: flex;
        align-items: center;
    }
    .cover-footer-text {
        font-size: 8.5pt;
        color: rgba(255,255,255,0.7);
        letter-spacing: 0.12em;
    }

    /* ===== Table of contents ===== */
    .toc-page {
        padding: 8mm 0;
        page-break-after: always;
    }
    .toc-header {
        font-size: 16pt;
        font-weight: 700;
        color: var(--text);
        letter-spacing: 0.2em;
        margin-bottom: 6mm;
        padding-bottom: 3mm;
        border-bottom: 2px solid var(--accent);
    }
    .toc-content { padding: 0; border-collapse: collapse; width: 100%; }
    .toc-item {
        display: table-row;
        line-height: 2.0;
    }
    .toc-link {
        display: table-cell;
        text-decoration: none;
        color: var(--text);
        font-size: 10pt;
        vertical-align: baseline;
        padding: 2px 0;
    }
    .toc-number {
        width: 3em;
        text-align: right;
        color: var(--accent);
        font-weight: 700;
        padding-right: 0.8em;
        white-space: nowrap;
    }
    .toc-title {
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
    }
    .toc-h3 .toc-number { color: var(--subtle); font-size: 9.5pt; }
    .toc-h3 .toc-title { color: var(--subtle); font-size: 9.5pt; padding-left: 1.5em; }

    /* ===== Body ===== */
    .content { padding-top: 2mm; }
    .chapter-break { height: 0; }

    h2 {
        font-size: 15pt;
        font-weight: 700;
        color: var(--accent);
        margin-top: 36px;
        margin-bottom: 14px;
        padding-bottom: 5px;
        border-bottom: 1.5px solid var(--border);
        line-height: 1.4;
        page-break-after: avoid;
    }
    h3 {
        font-size: 12.5pt;
        font-weight: 700;
        color: var(--text);
        margin-top: 22px;
        margin-bottom: 10px;
        padding-left: 8px;
        border-left: 3px solid var(--accent-mid);
        page-break-after: avoid;
    }
    h4 {
        font-size: 10.5pt;
        font-weight: 700;
        color: var(--subtle);
        margin-top: 16px;
        margin-bottom: 8px;
        letter-spacing: 0.08em;
    }
    p { margin-bottom: 16px; text-align: justify; }
    hr { border: none; border-top: 1px solid var(--border); margin: 22px 0; }

    /* ===== Callouts ===== */
    .quote-block {
        background: #F5F5F0;
        padding: 10px 16px;
        margin: 14px 0;
        color: var(--text);
        font-size: 10pt;
        line-height: 1.8;
        border-radius: 4px;
        page-break-inside: avoid;
    }

    /* ===== Lists ===== */
    ul, ol { margin: 10px 0 16px 0; padding-left: 2.2em; }
    li { margin-bottom: 6px; line-height: 2.0; }
    /* Use a counter to align ordered-list markers precisely. */
    ol { list-style: none; counter-reset: item; }
    ol li { counter-increment: item; position: relative; padding-left: 1.8em; }
    ol li::before {
        content: counter(item);
        position: absolute;
        left: 0;
        top: 0;
        width: 1.5em;
        text-align: right;
        color: var(--accent);
        font-weight: 700;
        font-size: 10.5pt;
    }

    /* ===== Tables ===== */
    .content-table {
        width: 100%;
        border-collapse: collapse;
        margin: 14px 0;
        font-size: 10pt;
        table-layout: auto;
        page-break-inside: avoid;
    }
    .content-table thead { display: table-header-group; }
    .content-table th {
        background: var(--accent);
        color: white;
        font-weight: 700;
        padding: 7px 10px;
        border: 1px solid var(--accent);
        text-align: left;
    }
    .content-table td {
        padding: 6px 10px;
        border: 1px solid var(--border);
        vertical-align: top;
    }
    .content-table tr:nth-child(even) td { background: var(--accent-light); }

    /* ===== Code ===== */
    .code-block {
        background: #E8EDE8;
        border: 1px solid var(--border);
        border-left: 3px solid var(--accent);
        border-radius: 0 4px 4px 0;
        padding: 10px 14px;
        margin: 12px 0;
        font-size: 9.5pt;
        line-height: 1.7;
        page-break-inside: avoid;
    }
    code {
        font-family: 'SF Mono', 'Monaco', monospace;
        font-size: 9.5pt;
        background: #E8EDE8;
        padding: 1px 5px;
        border-radius: 3px;
    }
    strong { font-weight: 700; color: #1A2E28; }

    /* ===== Images ===== */
    img { border: none; outline: none; box-shadow: none; display: block; max-width: 100%; margin: 12px auto; }
    """


def get_manual_chrome_css(theme='manual'):
    """Return Chrome-specific CSS for a manual theme."""
    css = get_manual_css(theme)
    css = re.sub(r'content:\s*string\([^)]+\);', 'content: none;', css)
    css = re.sub(r'string-set:[^;]+;', '', css)
    css = re.sub(r'@page:nth\(\d+\)\s*\{[^}]+\}', '', css)
    css = re.sub(r'@font-face\s*\{[^}]+\}', '', css, flags=re.DOTALL)

    chrome_fixes = """
    body, h1, h2, h3, h4, p, li, td, th, .toc-link, .cover-title,
    .cover-label, .cover-subtitle, .cover-meta, .cover-version,
    ol li::before {
        font-family: 'STXihei', 'STHeiti', sans-serif !important;
    }
    body { line-height: 2.0 !important; }
    p { margin-bottom: 16px !important; line-height: 2.0 !important; }
    li { line-height: 2.0 !important; margin-bottom: 6px !important; }
    ol { list-style: none !important; counter-reset: item !important; padding-left: 2.2em !important; margin-left: 0 !important; }
    ol li { counter-increment: item !important; position: relative !important; padding-left: 1.8em !important; }
    ol li::before {
        content: counter(item) !important;
        position: absolute !important;
        left: 0 !important; top: 0 !important;
        width: 1.5em !important; text-align: right !important;
        color: var(--accent) !important; font-weight: 700 !important;
        font-size: 10.5pt !important;
    }
    h2 { margin-top: 36px !important; margin-bottom: 14px !important; }
    h3 { margin-top: 22px !important; margin-bottom: 10px !important; }
    .quote-block { line-height: 1.8 !important; background: #F5F5F0 !important; border-left: none !important; border-radius: 4px !important; }
    code, pre, .code-block {
        font-family: 'Monaco', 'STXihei', 'STHeiti', monospace !important;
    }
    img { display: block; max-width: 100%; margin: 12px auto; }
    .cover {
        height: 297mm;
        break-after: page !important;
        page-break-after: always !important;
    }
    .toc-link { display: table-cell !important; }
    .toc-number { width: 3em !important; text-align: right !important; padding-right: 0.8em !important; }
    .toc-title { white-space: nowrap !important; overflow: hidden !important; text-overflow: ellipsis !important; }
    .toc-h3 .toc-number { color: var(--subtle) !important; font-size: 9.5pt !important; }
    .toc-h3 .toc-title { color: var(--subtle) !important; font-size: 9.5pt !important; padding-left: 1.5em !important; }
    .toc-page {
        min-height: 0 !important;
        break-after: page !important;
        page-break-after: always !important;
    }
    .content-table { table-layout: auto !important; }
    """
    return css + chrome_fixes


MANUAL_DECO_SVG = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 300 300">
  <circle cx="220" cy="120" r="110" fill="none" stroke="rgba(255,255,255,0.15)" stroke-width="1"/>
  <circle cx="220" cy="120" r="75"  fill="none" stroke="rgba(255,255,255,0.18)" stroke-width="1"/>
  <circle cx="220" cy="120" r="40"  fill="rgba(255,255,255,0.12)" stroke="rgba(255,255,255,0.2)" stroke-width="1"/>
  <line x1="220" y1="10"  x2="220" y2="230" stroke="rgba(255,255,255,0.12)" stroke-width="1"/>
  <line x1="110" y1="120" x2="330" y2="120" stroke="rgba(255,255,255,0.12)" stroke-width="1"/>
  <line x1="142" y1="42"  x2="298" y2="198" stroke="rgba(255,255,255,0.10)" stroke-width="1"/>
  <line x1="142" y1="198" x2="298" y2="42"  stroke="rgba(255,255,255,0.10)" stroke-width="1"/>
  <circle cx="220" cy="120" r="8" fill="rgba(255,255,255,0.5)"/>
</svg>"""


def create_manual_cover_and_toc(metadata, toc_html, theme='manual'):
    """Generate manual-theme cover and table-of-contents HTML."""
    title = metadata.get('title') or 'Operating Manual'
    label = metadata.get('eyebrow') or 'MANUAL'
    subtitle = metadata.get('subtitle') or ''
    date = metadata.get('date') or ''
    author = metadata.get('author') or ''

    footer_parts = [p for p in [author, date] if p]
    footer_text = '  ·  '.join(footer_parts)

    toc_section = ""
    if toc_html and toc_html.strip():
        toc_section = f"""
        <div class="toc-page">
            <h2 class="toc-header">Contents</h2>
            <div class="toc-content">{toc_html}</div>
        </div>"""

    subtitle_html = f'<p class="cover-subtitle">{subtitle}</p>' if subtitle else ''
    return f"""
    <div class="cover">
        <div class="cover-deco">{MANUAL_DECO_SVG}</div>
        <div class="cover-body">
            <div class="cover-label">{label}</div>
            <h1 class="cover-title">{title}</h1>
            {subtitle_html}
            <div class="cover-divider"></div>
        </div>
        <div class="cover-footer-bar">
            <span class="cover-footer-text">{footer_text}</span>
        </div>
    </div>
    {toc_section}"""


def find_chrome():
    """Return the path to a Chrome or Chromium executable."""
    for command in ('google-chrome', 'google-chrome-stable', 'chromium', 'chromium-browser'):
        resolved = shutil.which(command)
        if resolved:
            return resolved

    candidates = [
        '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',
        '/Applications/Chromium.app/Contents/MacOS/Chromium',
        '/usr/bin/google-chrome',
        '/usr/bin/chromium-browser',
        '/usr/bin/chromium',
    ]
    for path in candidates:
        if os.path.isfile(path):
            return path
    return None


def verify_pdf_file(path):
    """Verify that a newly rendered file is a non-empty PDF."""
    pdf_path = Path(path)
    if not pdf_path.is_file():
        raise RuntimeError(f"The renderer did not create a PDF: {pdf_path}")
    if pdf_path.stat().st_size < 1024:
        raise RuntimeError(f"Generated PDF is unexpectedly small ({pdf_path.stat().st_size} bytes)")
    with pdf_path.open('rb') as handle:
        if handle.read(5) != b'%PDF-':
            raise RuntimeError("Output does not have a PDF file header")


def run_preflight(engine='chrome'):
    """Print dependency status and return whether the selected engine can run."""
    renderers = available_markdown_renderers()
    chrome = find_chrome()
    weasyprint_ready = importlib.util.find_spec('weasyprint') is not None

    print("Markdown renderers: " + (", ".join(renderers) if renderers else "none found"))
    print("Chrome/Chromium: " + (chrome if chrome else "not found"))
    print("WeasyPrint: " + ("available" if weasyprint_ready else "unavailable"))

    if not renderers:
        print("❌ Missing Markdown renderer: install Pandoc, markdown2, or markdown-it-py")
        return False
    if engine == 'chrome' and not chrome:
        print("❌ Chrome engine selected, but Chrome/Chromium was not found")
        return False
    if engine == 'weasyprint' and not weasyprint_ready:
        print("❌ WeasyPrint engine selected, but Python cannot import weasyprint")
        return False

    print(f"✅ Preflight passed: {engine}")
    return True


def _font_to_b64(path):
    """Convert a font file to a base64 data URI."""
    import base64
    with open(path, 'rb') as f:
        data = base64.b64encode(f.read()).decode('ascii')
    return f"data:font/truetype;base64,{data}"


def get_chrome_css():
    """Return Chrome-specific CSS that reduces CJK mojibake in iOS PDFKit.

    macOS CoreText gives PingFang SC, the primary system UI font, forced precedence.
    Chrome cannot override it through @font-face, which can produce Type 3 fonts
    with custom encoding and garbled text in some iOS PDFKit readers.

    Loading Songti SC from a TTF file through @font-face bypasses CoreText.
    The target is CIDFont TrueType with Identity-H encoding; verify the actual result in the target reader.

    Prefer Source Han Sans VF when installed through Homebrew for a clean sans-serif appearance.
    Otherwise, fall back to Songti. Both paths avoid CoreText and target CIDFont TrueType with Identity-H.
    """
    font_dir = os.path.expanduser('~/.workbuddy/fonts')

    # Font priority:
    # 1. DroidSansFallback: sans-serif style, direct TTF loading in Chrome, CIDFont TrueType output.
    # 2. Songti SC: serif fallback.
    # PingFang SC and Source Han Sans VF may be intercepted by CoreText and emitted as Type 3 fonts.
    droid = os.path.join(font_dir, 'DroidSansFallback.ttf')
    songti_reg = os.path.join(font_dir, 'Songti-SC-Regular.ttf')
    songti_bold = os.path.join(font_dir, 'Songti-SC-Bold.ttf')

    font_faces = ""
    if os.path.isfile(droid):
        # DroidSansFallback has one regular file; declare it twice and let the browser synthesize bold.
        font_faces = f"""
    @font-face {{
        font-family: 'DocSongti';
        font-weight: 400;
        src: url('file://{droid}') format('truetype');
    }}
    @font-face {{
        font-family: 'DocSongti';
        font-weight: 700;
        src: url('file://{droid}') format('truetype');
    }}
"""
    else:
        # Fall back to Songti.
        for weight, path in [(400, songti_reg), (700, songti_bold)]:
            if os.path.isfile(path):
                font_faces += f"""
    @font-face {{
        font-family: 'DocSongti';
        font-weight: {weight};
        src: url('file://{path}') format('truetype');
    }}
"""

    css = get_apple_css()
    # Remove WeasyPrint-only syntax.
    css = re.sub(r'content:\s*string\([^)]+\);', 'content: none;', css)
    css = re.sub(r'string-set:[^;]+;', '', css)
    css = re.sub(r'@page:nth\(\d+\)\s*\{[^}]+\}', '', css)
    # Replace WeasyPrint @font-face blocks with the Chrome-specific definitions.
    css = re.sub(r'@font-face\s*\{[^}]+\}', '', css, flags=re.DOTALL)
    # Normalize all font references to DocSongti, which points to the selected local font file.
    # STHeiti is an older system sans-serif that Chrome can embed as CIDFont TrueType.
    # Fall back to STSong if STHeiti is unavailable.
    for name in ("'PingFang SC'", "'Songti SC'", "'STSong'", "'SimSun'",
                 "-apple-system, BlinkMacSystemFont, 'SF Pro Text', 'PingFang SC', sans-serif",
                 "-apple-system, BlinkMacSystemFont, sans-serif",
                 "'SF Mono', 'Monaco', monospace"):
        if 'Mono' in name or 'Monaco' in name:
            replacement = "'DocSongti'"
        else:
            replacement = "'DocSongti', 'STHeiti', 'STSong', serif"
        css = css.replace(name, replacement)

    # Chrome pagination corrections.
    chrome_fixes = """
    /* Chrome handles full-page cover and contents elements more reliably with break-after. */
    .cover {
        height: 297mm;
        break-after: page !important;
        page-break-after: always !important;
    }
    .toc-page {
        min-height: 0 !important;
        padding: 36px 28px !important;
        break-after: page !important;
        page-break-after: always !important;
    }
    .toc-header {
        font-size: 20pt !important;
        margin-bottom: 12px !important;
    }
    .toc-content {
        column-gap: 20px !important;
    }
    .toc-h2 {
        margin-top: 4px !important;
        margin-bottom: 2px !important;
    }
    .toc-h2 .toc-link {
        font-size: 9pt !important;
        padding: 1px 0 !important;
    }
    .toc-h2 .toc-number {
        min-width: 2em !important;
        font-size: 9pt !important;
    }
    /* Use automatic column widths, avoid page splits where possible, and repeat table headers. */
    .content-table {
        table-layout: auto !important;
        page-break-inside: avoid !important;
    }
    .content-table thead {
        display: table-header-group;
    }
    /* Center table captions. */
    h4 {
        text-align: center !important;
    }
    /* Do not force every section onto a new page. */
    .chapter-break {
        page-break-before: avoid !important;
        break-before: avoid !important;
        height: 0 !important;
    }
    h3 {
        page-break-before: auto !important;
    }
    /* Tighten blockquote spacing so short quotations do not consume multiple pages. */
    .quote-block {
        margin: 10px 0 !important;
        padding: 0.6em 1em 0.6em 1.2em !important;
        page-break-inside: auto !important;
    }
    """
    return font_faces + css + chrome_fixes


def convert_with_chrome(full_html, output_file):
    """Render a PDF with headless Chrome and atomically replace the target after verification."""
    chrome = find_chrome()
    if not chrome:
        raise RuntimeError("Chrome/Chromium was not found; install it and try again")

    with tempfile.NamedTemporaryFile(suffix='.html', delete=False, mode='w', encoding='utf-8') as f:
        f.write(full_html)
        tmp_html = f.name

    output_path = Path(output_file).expanduser().resolve()
    with tempfile.NamedTemporaryFile(
        suffix='.pdf',
        delete=False,
        dir=output_path.parent,
    ) as pdf_handle:
        tmp_pdf = pdf_handle.name
    os.unlink(tmp_pdf)

    try:
        result = subprocess.run([
            chrome,
            '--headless=new',
            '--disable-gpu',
            f'--print-to-pdf={tmp_pdf}',
            '--no-pdf-header-footer',
            f'file://{tmp_html}'
        ], capture_output=True, text=True, timeout=60)

        if result.returncode != 0:
            raise RuntimeError(f"Chrome conversion failed: {result.stderr.strip() or 'unknown error'}")
        verify_pdf_file(tmp_pdf)
        os.replace(tmp_pdf, output_path)
    finally:
        if os.path.exists(tmp_html):
            os.unlink(tmp_html)
        if os.path.exists(tmp_pdf):
            os.unlink(tmp_pdf)


def build_document_html(metadata, cover_html, html_content):
    """Build the complete document with a restrictive CSP and escaped metadata."""
    title = metadata.get('title') or 'Document'
    csp = html_lib.escape(CONTENT_SECURITY_POLICY, quote=True)
    return f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta http-equiv="Content-Security-Policy" content="{csp}">
        <title>{title}</title>
    </head>
    <body>
        {cover_html}
        <div class="content">
            {html_content}
        </div>
    </body>
    </html>
    """


def convert_markdown_to_pdf(
    input_file,
    output_file=None,
    title=None,
    author=None,
    subtitle=None,
    engine='chrome',
    no_toc=False,
    theme='default',
    force=False,
):
    """Convert one Markdown file to PDF."""

    input_path = Path(input_file).expanduser().resolve()
    if not input_path.exists():
        raise FileNotFoundError(f"Input file does not exist: {input_path}")
    if not input_path.is_file():
        raise RuntimeError(f"Input path is not a regular file: {input_path}")
    if input_path.stat().st_size == 0:
        raise RuntimeError(f"Input file is empty: {input_path}")

    if output_file:
        output_path = Path(output_file).expanduser().resolve()
    else:
        output_path = input_path.with_suffix('.pdf')
    if output_path.suffix.lower() != '.pdf':
        raise RuntimeError(f"Output path must end in .pdf: {output_path}")
    if not output_path.parent.exists():
        raise RuntimeError(f"Output directory does not exist: {output_path.parent}")
    if output_path.exists() and not force:
        raise FileExistsError(
            f"Output file already exists: {output_path}. Re-run with --force only after confirming replacement."
        )

    # Read the input file.
    print(f"📖 Reading: {input_path}")
    try:
        md_content = input_path.read_text(encoding='utf-8')
    except UnicodeDecodeError as exc:
        raise RuntimeError("Input is not valid UTF-8; convert its encoding first") from exc

    # Strip a leading YAML frontmatter block.
    md_content = re.sub(r'^---\s*\n.*?\n---\s*\n', '', md_content, count=1, flags=re.DOTALL)

    # Extract metadata.
    print("📑 Extracting metadata...")
    metadata = extract_metadata(md_content)

    # Command-line arguments override extracted metadata.
    if title:
        metadata['title'] = title
    if author:
        metadata['author'] = author
    if subtitle:
        metadata['subtitle'] = subtitle
    if not metadata.get('title'):
        raise RuntimeError("No level-one heading found. Add `# Title` to the Markdown or use --title.")
    metadata = escape_metadata(metadata)

    # Extract the table-of-contents structure.
    print("📂 Extracting table-of-contents structure...")
    toc_structure = extract_toc_structure(md_content)
    print(f"   ✓ Found {len([t for t in toc_structure if t['level'] == 2])} main sections")
    print(f"   ✓ Found {len([t for t in toc_structure if t['level'] == 3])} subsections")

    # Generate table-of-contents HTML.
    toc_html = "" if no_toc else generate_toc_html(toc_structure)

    # Render the Markdown body.
    print("🎨 Rendering Markdown...")
    html_content = process_markdown(md_content, base_dir=input_path.parent)

    # Select cover markup by theme.
    if theme == 'kunlun':
        cover_html = create_kunlun_cover_and_toc(metadata, toc_html)
    elif theme in MANUAL_PALETTES:
        cover_html = create_manual_cover_and_toc(metadata, toc_html, theme)
    elif theme == 'business':
        cover_html = create_business_cover_and_toc(metadata, toc_html)
    else:
        cover_html = create_cover_and_toc(metadata, toc_html)

    # Build the complete HTML document.
    print("📄 Building HTML...")
    input_dir = input_path.parent
    full_html = build_document_html(metadata, cover_html, html_content)

    # Generate the PDF.
    print("📝 Generating PDF...")
    if engine == 'chrome':
        theme_labels = {
            'default': 'Default', 'kunlun': 'Kunlun',
            'manual': 'Manual Green', 'manual-orange': 'Manual Orange', 'manual-blue': 'Manual Blue',
            'business': 'Business Dark',
        }
        print(f"   Engine: Chrome · {theme_labels.get(theme, 'Default')}")
        if theme in MANUAL_PALETTES:
            chrome_css = get_manual_chrome_css(theme)
        elif theme == 'kunlun':
            chrome_css = get_kunlun_chrome_css()
        elif theme == 'business':
            chrome_css = get_business_chrome_css()
        else:
            chrome_css = get_chrome_css()
        full_html_chrome = full_html.replace(
            '</head>',
            f'<style nonce="{STYLE_NONCE}">{chrome_css}</style></head>',
        )
        convert_with_chrome(full_html_chrome, output_path)
    else:
        try:
            from weasyprint import CSS, HTML
        except ModuleNotFoundError as exc:
            raise RuntimeError(
                "WeasyPrint was selected, but the current Python environment cannot import weasyprint. "
                "Use the default Chrome engine or install the dependency after approval."
            ) from exc
        if theme in MANUAL_PALETTES:
            base_css = get_manual_css(theme)
        elif theme == 'kunlun':
            base_css = get_kunlun_css()
        elif theme == 'business':
            base_css = get_business_css()
        else:
            base_css = get_apple_css()
        css = CSS(string=base_css)
        with tempfile.NamedTemporaryFile(
            suffix='.pdf',
            delete=False,
            dir=output_path.parent,
        ) as pdf_handle:
            tmp_pdf = pdf_handle.name
        try:
            HTML(string=full_html, base_url=str(input_dir)).write_pdf(
                tmp_pdf,
                stylesheets=[css],
            )
            verify_pdf_file(tmp_pdf)
            os.replace(tmp_pdf, output_path)
        finally:
            if os.path.exists(tmp_pdf):
                os.unlink(tmp_pdf)

    verify_pdf_file(output_path)
    print(f"✅ Created: {output_path}")

    # Report file size.
    size_mb = output_path.stat().st_size / (1024 * 1024)
    print(f"📊 File size: {size_mb:.1f} MB")

def main():
    parser = argparse.ArgumentParser(
        description='Convert Markdown into a professional PDF with a cover and table of contents'
    )
    parser.add_argument('input', nargs='?', help='Input Markdown file')
    parser.add_argument('-o', '--output', help='Output PDF file (default: same basename as input)')
    parser.add_argument('--title', help='Override the document title')
    parser.add_argument('--subtitle', help='Override the document subtitle')
    parser.add_argument('--author', help='Override the document author')
    parser.add_argument(
        '--engine',
        choices=['weasyprint', 'chrome'],
        default='chrome',
        help='PDF rendering engine (default: chrome)'
    )
    parser.add_argument(
        '--check',
        action='store_true',
        help='Check Markdown renderers and PDF engines without converting a file'
    )
    parser.add_argument(
        '--force',
        action='store_true',
        help='Replace an existing output PDF'
    )
    parser.add_argument(
        '--debug',
        action='store_true',
        help='Print a complete traceback on failure'
    )
    parser.add_argument(
        '--no-toc',
        action='store_true',
        help='Omit the table-of-contents page'
    )
    parser.add_argument(
        '--theme',
        choices=['default', 'kunlun', 'manual', 'manual-orange', 'manual-blue', 'business'],
        default='default',
        help='Theme: default / kunlun / business / manual / manual-orange / manual-blue'
    )

    args = parser.parse_args()

    if args.check:
        return 0 if run_preflight(args.engine) else 1
    if not args.input:
        parser.error('Input Markdown file is required unless --check is used')

    try:
        convert_markdown_to_pdf(
            args.input,
            args.output,
            args.title,
            args.author,
            args.subtitle,
            args.engine,
            args.no_toc,
            args.theme,
            args.force,
        )
    except Exception as e:
        print(f"❌ Conversion failed: {e}")
        if args.debug:
            import traceback
            traceback.print_exc()
        return 1

    return 0

if __name__ == '__main__':
    exit(main())
