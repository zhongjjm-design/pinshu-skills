"""Build a self-contained Qinghui Notes preview from local article inputs.

Python standard library only; does not read retired engines or Skill backups.
"""
from pathlib import Path
from html.parser import HTMLParser
from urllib.parse import urlparse, unquote
import argparse
import base64
import hashlib
import html
import json
import mimetypes
import re

ENGINE = Path(__file__).resolve().parent.parent / 'assets'


def image_url(path):
    mime = mimetypes.guess_type(path.name)[0]
    if mime not in {'image/png', 'image/jpeg', 'image/webp'}:
        raise ValueError('Unsupported local image: ' + str(path))
    return 'data:' + mime + ';base64,' + base64.b64encode(path.read_bytes()).decode()


class ArticleInput(HTMLParser):
    """Keep source text and image order, remove input presentation styles."""
    allowed = {'p', 'h2', 'h3', 'h4', 'img', 'hr', 'br', 'strong', 'b', 'em',
               'i', 'a', 'span', 'ul', 'ol', 'li', 'blockquote', 'code',
               'table', 'thead', 'tbody', 'tr', 'th', 'td'}

    def __init__(self, folder):
        super().__init__(convert_charrefs=False)
        self.folder, self.parts, self.images, self.files = folder, [], [], []
        self.titles, self.paragraphs, self.current = [], [], None

    def handle_starttag(self, tag, attrs):
        if tag not in self.allowed:
            raise ValueError('Unsupported article element: ' + tag)
        if tag in {'h2', 'p'}:
            self.current = (tag, [])
        attrs = [(k, v) for k, v in attrs if k in {'alt', 'title', 'href', 'src'} or
                 (tag == 'p' and k == 'data-video-slot') or
                 (tag == 'img' and k in {'data-frame-baked', 'data-caption', 'data-hero',
                                         'data-source-url', 'data-source-label'})]
        source_url = dict(attrs).get('data-source-url', '')
        if source_url and (urlparse(source_url).scheme not in {'https', 'http'} or not urlparse(source_url).netloc):
            raise ValueError('Image source URL must be HTTP(S)')
        if tag == 'a':
            href = dict(attrs).get('href', '')
            if urlparse(href).scheme not in {'', 'https', 'http', 'mailto'}:
                raise ValueError('Unsupported link scheme')
        if tag == 'img':
            src = dict(attrs).get('src', '')
            # A Windows path such as E:\\pics\\a.png parses as scheme "e"; it is a local file, not a URL
            # (colleague's Windows run, 2026-10-13: every image failed to load).
            parsed = urlparse('' if re.match(r'^[A-Za-z]:[\\/]', src) else src)
            if parsed.scheme not in {'', 'file'}:
                raise ValueError('Expected an original local image')
            path = Path(unquote(parsed.path if parsed.scheme else src))
            if not path.is_absolute():
                path = self.folder / path
            path = path.resolve()
            token = '@@IMG_' + str(len(self.images)) + '@@'
            self.images.append(image_url(path))
            self.files.append(path)
            attrs = [(k, v) for k, v in attrs if k != 'src'] + [('src', token)]
        self.parts.append('<' + tag + ''.join(
            ' ' + k + ('="' + html.escape(v, quote=True) + '"' if v is not None else '')
            for k, v in attrs) + '>')

    def handle_startendtag(self, tag, attrs):
        self.handle_starttag(tag, attrs)

    def handle_endtag(self, tag):
        if self.current and self.current[0] == tag:
            text = ''.join(self.current[1]).strip()
            (self.titles if tag == 'h2' else self.paragraphs).append(text)
            self.current = None
        if tag not in {'br', 'hr', 'img'}:
            self.parts.append('</' + tag + '>')

    def handle_data(self, data):
        self.parts.append(data)
        if self.current:
            self.current[1].append(data)

    def handle_entityref(self, name):
        self.parts.append('&' + name + ';')
        if self.current:
            self.current[1].append(html.unescape('&' + name + ';'))

    def handle_charref(self, name):
        self.parts.append('&#' + name + ';')
        if self.current:
            self.current[1].append(html.unescape('&#' + name + ';'))


def validate_layout(layout, parser):
    """A per-article plan may add breaks, never replace source wording."""
    for title, phrases in layout.get('headingPhrases', {}).items():
        if title not in parser.titles or ''.join(phrases) != title:
            raise ValueError('Heading phrases must exactly reproduce an input heading: ' + title)
    for title, parts in layout.get('headingSplit', {}).items():
        # Subtitle split: main + one separator + sub must reproduce the heading, so no wording is added or lost.
        if title not in parser.titles or len(parts) != 2 or not all(parts):
            raise ValueError('Heading split must name an input heading with two non-empty parts: ' + title)
        if not any(parts[0] + sep + parts[1] == title for sep in ('，', ',', '：', ':', '｜', '|', '；', ';', '')):
            raise ValueError('Heading split must satisfy big + one separator (， ： ｜ ； or none) + small == heading. Heading: %s; got: %s | %s' % (title, parts[0], parts[1]))
    for prefix, anchors in layout.get('readingBreaks', []):
        matches = [p for p in parser.paragraphs if p.startswith(prefix)]
        if len(matches) != 1:
            raise ValueError('Reading prefix must match one paragraph: ' + prefix)
        position = 0
        for anchor in anchors:
            position = matches[0].find(anchor, position + 1)
            if position < 0:
                raise ValueError('Reading anchor is absent or out of order: ' + anchor)


def build(input_path, meta_path, layout_path, output_path):
    original = input_path.read_text(encoding='utf-8')
    match = re.search(r'<body\b[^>]*>([\s\S]*?)</body>', original, re.I)
    body = match[1] if match else original
    first_title = re.match(r'^\s*<h1\b[^>]*>([\s\S]*?)</h1>', body, re.I)
    inferred_title = html.unescape(re.sub('<[^>]+>', '', first_title[1])) if first_title else input_path.stem
    if first_title:
        body = body[first_title.end():]
    # Subsequent first-level headings become chapter headings.
    body = re.sub(r'<(/?)h1\b', r'<\1h2', body, flags=re.I)
    meta = json.loads(meta_path.read_text(encoding='utf-8')) if meta_path else {}
    layout = json.loads(layout_path.read_text(encoding='utf-8')) if layout_path else {}
    parser = ArticleInput(input_path.parent)
    parser.feed(body)
    parser.close()
    validate_layout(layout, parser)
    protected = [input_path, *parser.files]
    if meta_path:
        protected.append(meta_path)
    if layout_path:
        protected.append(layout_path)

    def cover(key):
        item = meta.get(key)
        if not item:
            return ''
        path = Path(item['file'] if isinstance(item, dict) else item)
        if not path.is_absolute():
            path = (meta_path.parent if meta_path else input_path.parent) / path
        protected.append(path.resolve())
        return image_url(path)

    article = dict(id='1', title=meta.get('title', inferred_title), author=meta.get('author', ''),
                   digest=meta.get('digest', ''), sourceHTML=''.join(parser.parts),
                   images=parser.images, cover=cover('cover_landscape'), square=cover('cover_square'),
                   layout=layout, judgment=layout.get('judgment', []), quote=layout.get('quote', []))
    if output_path in protected or output_path.with_suffix('.build.json') in protected:
        raise ValueError('Output must not overwrite an input, metadata, layout plan or original image')
    shell = (ENGINE / 'preview.html').read_text(encoding='utf-8')
    config = json.dumps({'articles': [article]}, ensure_ascii=False).replace('<', '\\u003c')
    chapter_files = [ENGINE / 'chapter' / f'{number:02}.png' for number in range(1, 7)]
    chapter_images = {path.stem: image_url(path) for path in chapter_files}
    chapter_js = 'const CHAPTER_IMAGES=' + json.dumps(chapter_images) + ';\n'
    page = shell.replace('@@CONFIG@@', config).replace('@@RENDERER@@', chapter_js + (ENGINE / 'reading-base.js').read_text(encoding='utf-8') + '\n' + (ENGINE / 'renderer.js').read_text(encoding='utf-8'))
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(page, encoding='utf-8')
    record = dict(template_set='seven-layout-review', version='0.4.0-rc.3', reading_base='1.10.0',
                  templates=['松绿双线','青灰手记','暖纸杂志','橙线手记','蓝白专题','首席品牌官经典版','数字分栏'],
                  default_template='青灰手记', template_selection_status='pending-per-article',
                  article_specific_acceptance=False, wechat_phone_tested=False,
                  template_source=str(ENGINE), input=str(input_path), output=str(output_path),
                  source_files=[dict(path=str(p), sha256=hashlib.sha256(p.read_bytes()).hexdigest())
                                for p in dict.fromkeys([*protected,*chapter_files])])
    output_path.with_suffix('.build.json').write_text(json.dumps(record, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    return output_path


if __name__ == '__main__':
    cli = argparse.ArgumentParser(description='七款同级版式：从本地正文生成可复制的图文模板预览')
    cli.add_argument('--input', type=Path, required=True, help='HTML 正文；配图可用相对路径')
    cli.add_argument('--meta', type=Path, help='标题、作者、摘要和原封面 JSON，可省略')
    cli.add_argument('--layout', type=Path, help='该篇文章的断行、分段、强调计划，可省略')
    cli.add_argument('--output', type=Path, required=True)
    args = cli.parse_args()
    print(build(args.input.resolve(), args.meta.resolve() if args.meta else None,
                args.layout.resolve() if args.layout else None, args.output.resolve()))
