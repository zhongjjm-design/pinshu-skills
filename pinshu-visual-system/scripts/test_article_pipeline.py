"""Regression for image legibility boundaries, provenance and draft binding."""
import hashlib
import base64
import json
from pathlib import Path
import tempfile
import unittest
from argparse import Namespace
from PIL import Image, ImageDraw
from capture_evidence import save_capture, save_native_image, parse_media_expectations
from run_article_pipeline import rebind_plan, load_export, SKILLS, run, make_light
from prepare_article_handoff import prepare
from record_article_review import record, summarize


_WRITER_EXPORT=Path(__file__).resolve().parents[2]/'pinshu-write/scripts/export_article.py'
_NEEDS_WRITER=unittest.skipUnless(_WRITER_EXPORT.exists(),'SKIP: needs pinshu-write scripts/export_article.py (trial mode only)')

class PipelineTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup);self.root=Path(self.tmp.name)

    def test_media_declaration_rejects_missing_or_invalid_kind_count(self):
        self.assertEqual(parse_media_expectations(['video:1','image:2']),{'video':1,'image':2})
        for values in [['video:0'],['video'],['video:no'],['audio:1'],['video:1','video:2']]:
            with self.assertRaises(ValueError):parse_media_expectations(values)
        raw=self.root/'raw.png';Image.new('RGB',(1200,600),'navy').save(raw)
        with self.assertRaises(ValueError):save_capture(raw,{'ready':True,'missing_media':[{'kind':'video','expected':1,'loaded':0}]},self.root/'bad')

    def test_capture_rejects_low_resolution_and_blank_pixels(self):
        for size,name in [((600,400),'small'),((1200,500),'blank')]:
            raw=self.root/(name+'.png');Image.new('RGB',size,'white').save(raw)
            with self.assertRaises(ValueError):save_capture(raw,{},self.root/name)
            self.assertFalse((self.root/name).exists())

    def test_capture_downsamples_and_preserves_original(self):
        raw=self.root/'raw.png';im=Image.new('RGB',(1600,1000),'white')
        ImageDraw.Draw(im).rectangle((100,100,1400,700),fill='black');im.save(raw);before=raw.read_bytes()
        save_capture(raw,{'acquisition':'new-capture'},self.root/'capture')
        self.assertEqual((self.root/'capture/原始截图.png').read_bytes(),before)
        with Image.open(self.root/'capture/截图.png') as image:
            self.assertEqual(image.size,(1080,675))
        receipt=json.loads((self.root/'capture/截图回执.json').read_text())
        self.assertFalse(receipt['frame_baked']);self.assertEqual(receipt['mobile_review']['state'],'pending')

    @_NEEDS_WRITER

    def test_export_bind_and_stale_plan_rejection(self):
        draft=self.root/'v8.md';draft.write_bytes('# 原稿\r\n\r\n正文。\r\n===EDITOR NOTES===\r\n保留备注\r\n'.encode())
        load_export(SKILLS/'pinshu-write')(draft,self.root/'export')
        body=self.root/'export/正文.md';self.assertEqual(body.read_bytes(),'# 原稿\r\n\r\n正文。\r\n'.encode())
        plan=self.root/'plan.json';plan.write_text(json.dumps({'source_md':str(body),'article_sha256':hashlib.sha256(body.read_bytes()).hexdigest(),'assets':[]}))
        self.assertEqual(rebind_plan(plan,draft,body)['source_md'],str(body))
        another=self.root/'different.md';another.write_text('# 另一篇\n\n完全不同。')
        with self.assertRaisesRegex(ValueError,'differs'):rebind_plan(plan,another,another)
        body.write_text(body.read_text()+'改了正文')
        with self.assertRaisesRegex(ValueError,'changed'):rebind_plan(plan,draft,body)

    def test_screenshot_provenance_survives_handoff(self):
        source=self.root/'body.md';source.write_text('# 标题\n\n唯一段落。\n')
        image=self.root/'screen.png';Image.new('RGB',(1080,500),'navy').save(image)
        plan=self.root/'plan.json';plan.write_text(json.dumps({'source_md':str(source),'article_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),
          'assets':[{'asset_kind':'evidence-screenshot','role':'body','purpose':'测试原文证据','after_prefix':'唯一段落',
          'file':str(image),'original_file':str(image),'source_url':'https://example.com/source','captured_at':'2026-10-10',
          'attribution':'测试作者','acquisition':'reused','mobile_review':{'state':'needs-reframe','image_sha256':hashlib.sha256(image.read_bytes()).hexdigest()},'caption':'截图来源：测试作者'}]}))
        prepare(plan,self.root/'out',SKILLS/'pinshu-wechat-layout')
        manifest=json.loads((self.root/'out/配图清单.json').read_text())['files'][0]
        self.assertEqual(manifest['acquisition'],'reused');self.assertEqual(manifest['mobile_review']['state'],'needs-reframe')
        self.assertEqual(manifest['source_url'],'https://example.com/source');self.assertFalse(manifest['frame_baked'])
        handoff=json.loads((self.root/'out/排版交接.json').read_text())
        self.assertEqual(handoff['body_images'][0]['source_url'],'https://example.com/source')

    @_NEEDS_WRITER

    def test_missing_evidence_routes_to_capture_queue(self):
        source=self.root/'draft.md';source.write_text('# 标题\n\n唯一段落。\n\n===EDITOR NOTES===\n不要混进正文。')
        plan=self.root/'plan.json';plan.write_text(json.dumps({'source_md':str(source),
          'article_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'assets':[{'asset_kind':'evidence-screenshot',
          'role':'body','purpose':'原话证据','source_url':'https://example.com/source','filename':'01.png',
          'capture_region':'从第一句到完整末句','after_paragraph':'唯一段落。','after_prefix':'唯一段落','review_state':'capture-pending'}]}))
        out=self.root/'pipeline';before=source.read_bytes()
        result=run(Namespace(draft=source,plan=plan,output_dir=out,writer_skill=SKILLS/'pinshu-write',layout_skill=SKILLS/'pinshu-wechat-layout',prepare_only=True))
        self.assertTrue(result.exists());self.assertEqual(source.read_bytes(),before)
        self.assertEqual(json.loads((out/'流程核验.json').read_text())['status'],'CAPTURE_PENDING')
        self.assertFalse((out/'配图交接').exists())

    def test_unsorted_plan_does_not_swap_evidence(self):
        folder=self.root/'配图交接';folder.mkdir()
        for name,color in [('hero.png','green'),('first.png','red'),('second.png','blue')]:
            Image.new('RGB',(1080,500),color).save(folder/name)
        def uri(name):return 'data:image/png;base64,'+base64.b64encode((folder/name).read_bytes()).decode()
        render={'title':'标题','readingBlocks':['正文。'],'themes':[{'caption_links':0}],
          'html':'<div id="paper"><article id="article-body"><section data-picture="true" data-hero="true"><img src="'+uri('hero.png')+'"></section><p data-reading-role="normal">正文。</p>'+
          ''.join('<section data-picture="true"><img src="'+uri(name)+'"></section>' for name in ['first.png','second.png'])+'</article></div>'}
        handoff={'body_images':[{'filename':'second.png'},{'filename':'first.png'}]}
        preview,rows=make_light(render,handoff,self.root,['正文。'])
        self.assertEqual([row['filename'] for row in rows],['first.png','second.png'])
        self.assertLess(preview.read_text().index('配图交接/first.png'),preview.read_text().index('配图交接/second.png'))

    def test_pending_media_and_low_native_pixels_are_rejected(self):
        raw=self.root/'raw.png';Image.new('RGB',(1420,900),'navy').save(raw)
        for receipt in [{'ready':False,'media':[{'kind':'video','loaded':False}]},
                        {'ready':True,'low_resolution_media':[{'natural_width':680,'projected_delivery_width':1080}]}]:
            with self.assertRaises(ValueError):save_capture(raw,receipt,self.root/'failed')
            self.assertFalse((self.root/'failed').exists())

    def test_native_crop_never_upscales_and_preserves_source(self):
        raw=self.root/'raw.png';Image.new('RGB',(680,400),'navy').save(raw);before=raw.read_bytes()
        save_native_image(raw,{},self.root/'crop',[10,20,340,200])
        with Image.open(self.root/'crop/截图.png') as image:self.assertEqual(image.size,(340,200))
        self.assertEqual((self.root/'crop/来源原图.png').read_bytes(),before)
        with self.assertRaises(ValueError):save_native_image(raw,{},self.root/'bad',[0,0,681,200])

    def test_unbound_capture_and_review_degrade_to_unknown(self):
        source=self.root/'body.md';source.write_text('# 标题\n\n唯一段落。\n')
        image=self.root/'screen.png';Image.new('RGB',(1080,500),'navy').save(image)
        plan=self.root/'plan.json';plan.write_text(json.dumps({'source_md':str(source),'article_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),
          'assets':[{'asset_kind':'evidence-screenshot','role':'body','purpose':'原话','after_prefix':'唯一段落','file':str(image),
          'original_file':str(image),'source_url':'https://example.com/post','captured_at':'2026-10-10','attribution':'作者',
          'acquisition':'new-capture','capture_receipt':{},'mobile_review':{'state':'agent-readable','note':'旧结论'}}]}))
        prepare(plan,self.root/'out',SKILLS/'pinshu-wechat-layout')
        item=json.loads((self.root/'out/配图清单.json').read_text())['files'][0]
        self.assertEqual(item['acquisition'],'unknown');self.assertEqual(item['mobile_review']['state'],'unknown')
        self.assertEqual(item['mobile_review']['unverified_previous_record']['note'],'旧结论')

    @_NEEDS_WRITER

    def test_failed_pipeline_has_top_level_failure_receipt(self):
        draft=self.root/'draft.md';draft.write_text('# 标题\n\n正文。')
        plan=self.root/'plan.json';plan.write_text(json.dumps({'source_md':str(draft),'article_sha256':'wrong','assets':[]}))
        args=Namespace(draft=draft,plan=plan,output_dir=self.root/'run',writer_skill=SKILLS/'pinshu-write',layout_skill=SKILLS/'pinshu-wechat-layout',prepare_only=True)
        with self.assertRaises(ValueError):run(args)
        status=json.loads((args.output_dir/'流程核验.json').read_text())
        self.assertEqual(status['status'],'FAILED');self.assertFalse(status['ready_for_user_review'])

    def test_review_is_separate_bound_and_requires_every_long_image_segment(self):
        root=self.root/'run';(root/'配图交接').mkdir(parents=True);(root/'手机检查').mkdir()
        im=root/'配图交接/img.png';Image.new('RGB',(1080,400),'navy').save(im)
        preview=root/'整篇效果预览.html';preview.write_text('<html>preview</html>')
        views=[root/'手机检查/01.png',root/'手机检查/01-part2.png']
        for p in views:Image.new('RGB',(1125,3000),'white').save(p)
        flow=root/'流程核验.json';flow.write_text(json.dumps({'status':'TECHNICAL_CHECKS_PASS_VISUAL_REVIEW_PENDING','template':'approved',
          'mobile_review':[{'filename':'img.png','image_sha256':hashlib.sha256(im.read_bytes()).hexdigest(),
          'screen_files':[p.name for p in views],'screen_sha256':{p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in views},'image_width_css':289,'acquisition':'reused',
          'asset_kind':'evidence-screenshot','estimated_phone_font_px':None}]}))
        before=flow.read_bytes()
        with self.assertRaisesRegex(ValueError,'all current phone segments'):record(root,'img.png','readable','实际看过','测试审核',views[:1])
        status=record(root,'img.png','needs-reframe','字小','测试审核',views)
        self.assertFalse(status['ready_for_user_review']);self.assertEqual(flow.read_bytes(),before)
        status=record(root,'img.png','readable','完整区间可读','测试审核',views)
        self.assertTrue(status['ready_for_user_review']);self.assertEqual(flow.read_bytes(),before)
        preview.write_text('<html>different template/context</html>')
        self.assertFalse(summarize(root)['ready_for_user_review'])

    def test_phone_view_replacement_is_rejected_before_and_after_review(self):
        root=self.root/'run';(root/'配图交接').mkdir(parents=True);(root/'手机检查').mkdir()
        im=root/'配图交接/img.png';Image.new('RGB',(1080,400),'navy').save(im)
        (root/'整篇效果预览.html').write_text('<html>preview</html>')
        view=root/'手机检查/01.png';Image.new('RGB',(1125,3000),'white').save(view);original=view.read_bytes()
        item={'filename':'img.png','image_sha256':hashlib.sha256(im.read_bytes()).hexdigest(),
          'screen_files':['01.png'],'screen_sha256':{'01.png':hashlib.sha256(original).hexdigest()},
          'image_width_css':289,'acquisition':'reused','asset_kind':'evidence-screenshot','estimated_phone_font_px':None}
        flow=root/'流程核验.json';flow.write_text(json.dumps({'status':'TECHNICAL_CHECKS_PASS_VISUAL_REVIEW_PENDING','template':'approved','mobile_review':[item]}))
        Image.new('RGB',(1125,3000),'red').save(view)
        with self.assertRaisesRegex(ValueError,'phone_view_changed'):record(root,'img.png','readable','看过','测试',[view])
        self.assertFalse((root/'审看记录.jsonl').exists())
        view.write_bytes(original);self.assertTrue(record(root,'img.png','readable','看过','测试',[view])['ready_for_user_review'])
        Image.new('RGB',(1125,3000),'red').save(view)
        self.assertFalse(summarize(root)['ready_for_user_review'])
        view.write_bytes(original);del item['screen_sha256']
        flow.write_text(json.dumps({'status':'TECHNICAL_CHECKS_PASS_VISUAL_REVIEW_PENDING','template':'approved','mobile_review':[item]}))
        with self.assertRaisesRegex(ValueError,'phone_views_unbound'):record(root,'img.png','readable','旧回执','测试',[view])


if __name__=='__main__':unittest.main()
