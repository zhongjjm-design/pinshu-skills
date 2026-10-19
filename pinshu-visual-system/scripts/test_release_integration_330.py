"""Offline release integrations: real parser/build/JS renderer, fake browser transport only.

The DOM tests need Node + linkedom (NODE_PATH may point at an existing installation).
No browser, network, image generation or paid API is used. Phone geometry/pixels below
are deterministic transport fixtures, NOT evidence of browser/mobile visual acceptance.
"""
import json
import os
from argparse import Namespace
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest
from unittest import mock
from urllib.parse import unquote, urlparse

from bs4 import BeautifulSoup
from PIL import Image, ImageDraw

import run_article_pipeline as pipeline
from article_preview import manuscript_blocks
from capture_evidence import save_capture, sha
from prepare_article_handoff import load_layout, prepare
from record_article_review import carry_over, record
from replace_asset import replace

LAYOUT = pipeline.SKILLS / 'pinshu-wechat-layout'
NODE = shutil.which('node')
DOM_AVAILABLE = bool(NODE) and subprocess.run(
    [NODE, '-e', "require('linkedom')"], capture_output=True).returncode == 0
if os.environ.get('CI') == 'true' and not DOM_AVAILABLE:
    raise RuntimeError('CI requires Node + linkedom; renderer integration regressions may not be skipped')

# Execute the shipped renderer, not a Python imitation of its text/caption behavior.
DOM_RENDER = r'''
const fs=require('fs'),vm=require('vm'),{parseHTML}=require('linkedom');
const job=JSON.parse(fs.readFileSync(0,'utf8'));
const {document,window}=parseHTML('<html><body></body></html>');
const page=fs.readFileSync(job.page,'utf8');
const config=JSON.parse(page.match(/const C=(.*);\n/)[1]);
const ctx=vm.createContext({document,window,console});
vm.runInContext(fs.readFileSync(job.assets+'/reading-base.js','utf8')+'\n'+
 fs.readFileSync(job.assets+'/renderer.js','utf8'),ctx);
ctx.article=config.articles[0];ctx.template=job.template;
const rendered=vm.runInContext('render(article,themes.find(t=>t.id===template))',ctx);
document.body.innerHTML='<main id="paper"><article id="article-body">'+rendered+'</article></main>';
if(job.mutation){
 const target=document.querySelector(job.mutation.selector);
 if(!target)throw Error('mutation target missing');
 if(job.mutation.text!==undefined)target.textContent=job.mutation.text;
 if(job.mutation.hidden)target.setAttribute('hidden','');
 if(job.mutation.style)target.style.cssText=job.mutation.style;
}
console.log(JSON.stringify({title:ctx.article.title,html:document.body.innerHTML,
 readingBlocks:[...document.querySelectorAll('#article-body [data-reading-role]')]
  .filter(e=>!e.closest('[data-decoration]')).map(e=>e.textContent),
 themes:[{id:job.template,caption_links:0}]}));
'''


class ReleaseIntegrationTests(unittest.TestCase):
    def setUp(self):
        # Never let a test silently use the system temporary directory.
        self.tmp = tempfile.TemporaryDirectory(dir=os.environ.get('TMPDIR'))
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name).resolve()
        self.source = self.root / 'article.md'
        self.source.write_text('# Article\n\nAnchor paragraph.\n', encoding='utf-8')
        self.image = self.root / 'image.png'
        Image.new('RGB', (1080, 400), 'navy').save(self.image)
        self.plan = self.root / 'plan.json'
        self.asset: dict = {'asset_kind': 'real-photo', 'role': 'body', 'file': str(self.image),
                      'original_file': str(self.image), 'filename': 'image.png',
                      'purpose': 'Show the subject', 'after_prefix': 'Anchor paragraph.',
                      'attribution': 'Example author'}
        self.save_plan()

    def save_plan(self, **options):
        self.plan.write_text(json.dumps({'source_md': str(self.source),
            'article_sha256': sha(self.source), 'assets': [self.asset], **options}), encoding='utf-8')

    def render(self, workbench, template='approved', mutation=None):
        result = subprocess.run([NODE, '-e', DOM_RENDER], input=json.dumps({
            'page': str(workbench), 'assets': str(LAYOUT / 'assets'),
            'template': template, 'mutation': mutation}), text=True, capture_output=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        return json.loads(result.stdout)

    def run_pipeline(self, name, mutation=None, **options):
        out = self.root / name

        def transport(job):
            if job['action'] == 'render':
                page = Path(unquote(urlparse(job['url']).path))
                data = self.render(page, options.get('template', 'approved'), mutation)
            else:
                self.assertEqual(job['action'], 'check')
                # Deliberately constant pixels isolate semantic context carry-over:
                # carry_over does not require screenshots to be pixel-identical.
                screen = Path(job['screen_dir']) / 'figure.png'
                Image.new('RGB', (375, 200), 'navy').save(screen)
                data = {'views': [{'overflow': False, 'caption_links': 0}],
                        'screens': [{'position': 'figure', 'file': screen.name,
                                     'image_width_css': 289, 'loaded': True}]}
            Path(job['result']).write_text(json.dumps(data), encoding='utf-8')

        args = Namespace(draft=self.source, plan=self.plan, output_dir=out,
                         writer_skill=pipeline.SKILLS / 'pinshu-write', layout_skill=LAYOUT,
                         ready_mode=True, prepare_only=False, space_id=1, page='p1',
                         template=options.get('template', 'approved'))
        with mock.patch.object(pipeline, 'browser', side_effect=transport):
            pipeline.run(args)
        return out

    @unittest.skipUnless(DOM_AVAILABLE, 'Node + linkedom required for offline real renderer')
    def test_tables_and_prompt_cards_pass_the_actual_pipeline_comparison(self):
        self.source.write_text('# Article\n\nAnchor paragraph.\n\n'
            '| Choice | Result |\n| --- | --- |\n| First | A**bold**word（note） |\n| 1:00-2:00 | Works |\n\n'
            '> 【Prompt（hint）】\n>\n> Role: editor\n>\n> - Keep facts\n> - Preserve wording\n', encoding='utf-8')
        self.save_plan()
        out = self.run_pipeline('full')
        flow = json.loads((out / '流程核验.json').read_text())
        self.assertEqual(flow['technical_status'], 'SOURCE_AND_BROWSER_CHECK_PASS')
        preview = BeautifulSoup((out / '整篇效果预览.html').read_text(), 'html.parser')
        self.assertEqual(preview.select_one('tbody td').get_text(), 'First')
        self.assertIn('Preserve wording', preview.select_one('[data-prompt-card]').get_text())
        layout = load_layout(LAYOUT)
        self.assertEqual(manuscript_blocks(self.source, LAYOUT),
                         [pipeline.normalized(b) for b in layout.visible(layout.parse_markdown(self.source)[1])])
        self.assertEqual(manuscript_blocks(self.source.read_text(), LAYOUT), manuscript_blocks(self.source, LAYOUT))
        for selector in ('tbody td', '[data-prompt-card] > section:last-child p'):
            with self.subTest(selector=selector):
                with self.assertRaisesRegex(ValueError, 'mismatch|changed'):
                    self.run_pipeline('changed-' + str(len(list(self.root.glob('changed-*')))),
                                      mutation={'selector': selector, 'text': 'WRONG content'})

    @unittest.skipUnless(shutil.which('magick'), 'ImageMagick required for raster preview')
    def test_standalone_preview_uses_the_same_parser_contract(self):
        from article_preview import build
        self.source.write_text('# Article\n\nAnchor paragraph.\n\n'
            '| A | B |\n| --- | --- |\n| One | Two |\n\n'
            '> 【Prompt】\n>\n> Preserve the source.\n', encoding='utf-8')
        self.save_plan()
        handoff = prepare(self.plan, self.root / 'standalone-handoff', LAYOUT)
        load_layout(LAYOUT).run(handoff, self.root / 'standalone-layout')
        rendered = self.root / 'standalone-layout/source.html'
        before = (sha(self.source), sha(rendered), sha(self.image))
        with mock.patch('builtins.print'):
            build(Namespace(source=self.source, html=rendered,
                            output_dir=self.root / 'light', width=1000))
        report = json.loads((self.root / 'light/preview-report.json').read_text())
        self.assertEqual(report['status'], 'TEXT_AND_RESOURCE_CHECK_PASS')
        self.assertEqual(before, (sha(self.source), sha(rendered), sha(self.image)))
        self.assertIn('Preserve the source.', (self.root / 'light/preview.html').read_text())

    def test_real_parser_rejections_remain_fail_closed(self):
        bad = ['# Article\n\n| A | B |\n|---|---|\n| one | two | LOST |\n',
               '# Article\n\n> 【Prompt】\n> [label](https://example.com)\n',
               '# Article\n\n<script>bad()</script>\n']
        for i, text in enumerate(bad):
            with self.subTest(i=i):
                self.source.write_text(text, encoding='utf-8')
                self.save_plan()
                with self.assertRaises(ValueError):
                    prepare(self.plan, self.root / ('bad-' + str(i)), LAYOUT)
                with self.assertRaises(ValueError):
                    manuscript_blocks(self.source, LAYOUT)

    @unittest.skipUnless(DOM_AVAILABLE, 'Node + linkedom required for offline real renderer')
    def test_heading_split_reaches_real_split_template_and_validation(self):
        self.source.write_text('# Article\n\n## Main：Subtitle\n\nAnchor paragraph.\n', encoding='utf-8')
        self.save_plan(heading_split={'Main：Subtitle': ['Main', 'Subtitle']})
        handoff = prepare(self.plan, self.root / 'handoff', LAYOUT)
        workbench = load_layout(LAYOUT).run(handoff, self.root / 'layout')
        dom = BeautifulSoup(self.render(workbench, 'split')['html'], 'html.parser')
        self.assertIsNotNone(dom.select_one('[data-subtitle]'), 'heading_split was dropped before the renderer')
        self.assertEqual(dom.select_one('[data-subtitle]').get_text(), 'Subtitle')
        out = self.run_pipeline('split-pipeline', template='split')
        self.assertEqual(json.loads((out / '流程核验.json').read_text())['technical_status'],
                         'SOURCE_AND_BROWSER_CHECK_PASS')
        self.save_plan(heading_split={'Main：Subtitle': ['Wrong', 'Subtitle']})
        handoff = prepare(self.plan, self.root / 'bad-split', LAYOUT)
        with self.assertRaisesRegex(ValueError, 'must satisfy'):
            load_layout(LAYOUT).run(handoff, self.root / 'invalid-layout')

    def test_framed_reused_to_new_capture_resets_processing_through_handoff(self):
        self.asset.update(asset_kind='evidence-screenshot', acquisition='reused', frame_baked=True,
                          source_url='https://example.com/post', captured_at='2026-10-01',
                          capture_receipt={'delivery_sha256': sha(self.image), 'captured_at': '2026-10-01'},
                          processing=['old frame', 'detail montage'], composition_receipt={'old': True},
                          composition_disclosure='Old montage', caption='Old montage', mobile_review={'state': 'readable'},
                          acquisition_warning='old warning')
        self.save_plan()
        prepare(self.plan, self.root / 'old-handoff', LAYOUT)  # the legacy asset really is accepted
        raw = self.root / 'raw.png'
        im = Image.new('RGB', (1600, 900), 'white')
        ImageDraw.Draw(im).rectangle((100, 100, 1400, 700), fill='black')
        im.save(raw)
        capture = self.root / 'capture'
        save_capture(raw, {'source_url': self.asset['source_url'], 'captured_at': '2026-10-19'}, capture)
        receipt_path = capture / '截图回执.json'
        receipt = json.loads(receipt_path.read_text())
        receipt_path.write_text(json.dumps({**receipt, 'frame_baked': True}), encoding='utf-8')
        before = self.plan.read_bytes()
        with self.assertRaisesRegex(ValueError, 'must be unframed'):
            replace(self.plan, 'image.png', 'Test', 'Reject framed capture', capture_dir=capture)
        self.assertEqual(self.plan.read_bytes(), before)
        receipt_path.write_text(json.dumps(receipt), encoding='utf-8')
        replace(self.plan, 'image.png', 'Test', 'Fresh capture', capture_dir=capture)
        new = json.loads(self.plan.read_text())['assets'][0]
        # Exercise handoff BEFORE inspecting flags: old code fails at its real guard.
        prepare(self.plan, self.root / 'new-handoff', LAYOUT)
        self.assertIs(new['frame_baked'], False)
        for field in ('mobile_review', 'composition_receipt', 'composition_disclosure', 'acquisition_warning', 'caption'):
            self.assertNotIn(field, new)
        self.assertEqual(new.get('processing', []), [])
        item = json.loads((self.root / 'new-handoff/配图清单.json').read_text())['files'][0]
        self.assertEqual(item['acquisition'], 'new-capture')
        self.assertEqual(item['sha256'], sha(capture / '截图.png'))
        new['frame_baked'] = True
        data = json.loads(self.plan.read_text()); data['assets'][0] = new
        self.plan.write_text(json.dumps(data), encoding='utf-8')
        with self.assertRaisesRegex(ValueError, 'must be unframed'):
            prepare(self.plan, self.root / 'forged-frame', LAYOUT)

    @unittest.skipUnless(DOM_AVAILABLE, 'Node + linkedom required for offline real renderer')
    def test_changed_visible_alt_does_not_carry_an_old_review(self):
        # A hash-bound generated visual has no source label, so renderer falls back to alt.
        report = self.root / 'clean.json'
        report.write_text(json.dumps({'status': 'PASS', 'results': [{
            'status': 'PASS', 'pixel_difference_ae': 0, 'c2pa_markers': [],
            'publish_copy': str(self.image)}]}), encoding='utf-8')
        self.asset.update(asset_kind='generated-visual', publish_clean_report=str(report), alt='Old visible caption')
        self.save_plan()
        old = self.run_pipeline('old')
        record(old, 'image.png', 'readable', 'Looked at fixture', 'Test', [old / '手机检查/figure.png'])
        same = self.run_pipeline('same')
        self.assertEqual(carry_over(old, same)['carried_over'], ['image.png'])
        self.asset['alt'] = 'New visible caption'
        self.save_plan()
        new = self.run_pipeline('new')
        result = carry_over(old, new)
        self.assertEqual(result['carried_over'], [], 'review carried across a changed visible alt caption')
        self.assertEqual(result['needs_review'], ['image.png'])
        slot = json.loads((new / '流程核验.json').read_text())['mobile_review'][0]['slot_context']
        self.assertEqual(slot['caption'], 'New visible caption')

    @unittest.skipUnless(DOM_AVAILABLE, 'Node + linkedom required for offline real renderer')
    def test_effective_caption_uses_rendered_precedence_and_visibility(self):
        cases = [({}, '来源：Example author', None),
                 ({'caption': ''}, '', None),
                 ({'caption': 'Explicit caption'}, 'Explicit caption', None),
                 ({}, '', {'selector': '[data-reading-role="caption"]', 'hidden': True}),
                 ({}, '', {'selector': '[data-reading-role="caption"]', 'style': 'display:none'}),
                 ({}, '', {'selector': '[data-picture]', 'style': 'visibility:hidden'}),
                 ({}, '', {'selector': '#article-body', 'hidden': True}),
                 ({}, '', {'selector': '[data-reading-role="caption"]', 'style': 'display : none !important'})]
        for i, (fields, expected, mutation) in enumerate(cases):
            with self.subTest(i=i):
                self.asset.pop('caption', None)
                self.asset.update(fields, alt='Not the source caption')
                self.save_plan()
                out = self.run_pipeline('caption-' + str(i), mutation=mutation)
                slot = json.loads((out / '流程核验.json').read_text())['mobile_review'][0]['slot_context']
                self.assertEqual(slot['caption'], expected)


if __name__ == '__main__':
    unittest.main()
