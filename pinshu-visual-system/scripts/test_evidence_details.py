"""Disclosure, source-pixel integrity and separate semantic/phone review regressions."""
import copy
import json
from pathlib import Path
import tempfile
import unittest
from PIL import Image, ImageDraw
from capture_evidence import sha
from compose_evidence import compose, compose_pixels, validate_montage
from prepare_article_handoff import prepare
from record_article_review import record, summarize

SKILLS=Path(__file__).resolve().parents[2]


class EvidenceDetailTests(unittest.TestCase):
    def setUp(self):
        t=tempfile.TemporaryDirectory();self.addCleanup(t.cleanup);self.root=Path(t.name)
        self.source=self.root/'body.md';self.source.write_text('# 标题\n\n三条片子的评论差很多。\n')
        self.original=self.root/'original.png';im=Image.new('RGB',(80,40),'white')
        d=ImageDraw.Draw(im);d.rectangle((0,0,19,19),fill='navy');d.rectangle((60,20,79,39),fill='red');im.save(self.original)
        self.recipe={'delivery_size':[50,20],'caption':'截图来源：作者｜封面与评论列节选（局部拼接，顺序未变）',
            'regions_native_pixels':[{'role':'封面','source_box':[0,0,20,20],'paste_xy':[0,0]},
                                     {'role':'评论列','source_box':[60,20,80,40],'paste_xy':[30,0]}]}
        self.recipe_path=self.root/'recipe.json';self.recipe_path.write_text(json.dumps(self.recipe))
        self.asset={'role':'body','asset_kind':'evidence-screenshot','file':str(self.original),'filename':'05.png',
            'original_file':str(self.original),'source_url':'https://example.com/post','attribution':'作者',
            'purpose':'对比三条片子评论','after_prefix':'三条片子','captured_at':'2026-10-09T12:00:00Z',
            'acquisition':'reused','mobile_review':{'state':'readable','image_sha256':sha(self.original)},
            'capture_receipt':{'source_url':'https://example.com/post','captured_at':'2026-10-09T12:00:00Z',
                'original_sha256':sha(self.original),'delivery_sha256':sha(self.original)}}
        self.plan={'source_md':str(self.source),'article_sha256':sha(self.source),'assets':[self.asset]}
        self.plan_path=self.root/'plan.json';self.save_plan()

    def save_plan(self):self.plan_path.write_text(json.dumps(self.plan,ensure_ascii=False))

    def make(self):
        compose(self.plan_path,'05.png',self.recipe_path,self.root/'montage')
        return json.loads(self.plan_path.read_text())['assets'][0]

    def test_composition_updates_one_asset_without_recapturing_or_upscaling(self):
        self.plan['assets'].append({'asset_kind':'evidence-screenshot','filename':'pending.png'})
        self.save_plan();before=self.original.read_bytes();asset=self.make()
        with Image.open(asset['file']) as image:self.assertEqual(image.size,(50,20))
        self.assertEqual(self.original.read_bytes(),before)
        self.assertEqual(asset['captured_at'],'2026-10-09T12:00:00Z')
        self.assertEqual(asset['acquisition'],'reused');self.assertEqual(asset['mobile_review']['state'],'pending')
        self.assertIn('processed_at',asset['capture_receipt'])
        self.assertTrue((self.root/'montage/输入配图任务.json').exists())
        self.assertEqual(json.loads(self.plan_path.read_text())['assets'][1],self.plan['assets'][1])

    def test_missing_disclosure_and_stale_source_stop_without_mutating_plan(self):
        before=self.plan_path.read_bytes();self.recipe['caption']='没有披露的普通图注'
        self.recipe_path.write_text(json.dumps(self.recipe))
        with self.assertRaisesRegex(ValueError,'局部拼接'):self.make()
        self.assertEqual(self.plan_path.read_bytes(),before);self.assertFalse((self.root/'montage').exists())
        self.source.write_text('changed')
        with self.assertRaisesRegex(ValueError,'Article changed'):self.make()

    def test_bounds_and_overlap_are_rejected(self):
        for key,value in [('source_box',[0,0,81,20]),('paste_xy',[40,0]),('paste_xy',[10,0])]:
            recipe=copy.deepcopy(self.recipe);recipe['regions_native_pixels'][1][key]=value
            with self.assertRaises(ValueError):compose_pixels(self.original,recipe)

    def test_forged_success_hash_does_not_bypass_pixel_reconstruction(self):
        asset=self.make();target=Path(asset['file']);im=Image.open(target).convert('RGB');im.putpixel((31,1),(0,0,0));im.save(target)
        asset['capture_receipt']['delivery_sha256']=sha(target)
        with self.assertRaisesRegex(ValueError,'pixels differ'):validate_montage(asset,target,self.original)

    def test_handoff_automatically_discloses_empty_or_missing_caption(self):
        asset=self.make()
        for i,caption in enumerate([None,'','截图来源：作者']):
            plan=json.loads(self.plan_path.read_text())
            if caption is None:plan['assets'][0].pop('caption')
            else:plan['assets'][0]['caption']=caption
            self.plan_path.write_text(json.dumps(plan))
            out=self.root/f'handoff{i}';prepare(self.plan_path,out,SKILLS/'pinshu-wechat-layout')
            placement=json.loads((out/'排版交接.json').read_text())['body_images'][0]
            item=json.loads((out/'配图清单.json').read_text())['files'][0]
            self.assertIn('局部拼接',placement['caption']);self.assertFalse(placement['frame_baked'])
            self.assertEqual(item['evidence_context']['after_paragraph'],'三条片子的评论差很多。')

    def test_montage_review_requires_meaning_legibility_and_disclosure_observations(self):
        root=self.root/'run';(root/'配图交接').mkdir(parents=True);(root/'手机检查').mkdir()
        image=root/'配图交接/05.png';Image.new('RGB',(50,20),'navy').save(image)
        view=root/'手机检查/05.png';Image.new('RGB',(1125,3000),'white').save(view)
        (root/'整篇效果预览.html').write_text('preview')
        item={'filename':'05.png','image_sha256':sha(image),'screen_files':['05.png'],'screen_sha256':{'05.png':sha(view)},
            'image_width_css':289,'acquisition':'reused','asset_kind':'evidence-screenshot','estimated_phone_font_px':None,
            'review_requirements':{'meaning':True,'legibility':True,'composition':True}}
        flow=root/'流程核验.json';flow.write_text(json.dumps({'status':'TECHNICAL_CHECKS_PASS_VISUAL_REVIEW_PENDING','template':'approved','mobile_review':[item]}))
        before=flow.read_bytes()
        for kwargs,missing in [({},'meaning'),({'meaning_note':'对应评论差距'},'legibility'),
                ({'meaning_note':'对应评论差距','legibility_note':'397等可读'},'composition')]:
            with self.assertRaisesRegex(ValueError,missing+'_review_missing'):
                record(root,'05.png','readable','看过','Codex',[view],**kwargs)
        self.assertFalse((root/'审看记录.jsonl').exists())
        result=record(root,'05.png','readable','当前完整图已看','Codex',[view],
            meaning_note='原封面与评论一一对应正文差距',legibility_note='11/397/8和片名直接可读',composition_note='局部拼接图注明示，顺序与原图一致')
        self.assertTrue(result['ready_for_user_review']);self.assertEqual(flow.read_bytes(),before)
        # An old generic readable declaration cannot satisfy new review requirements.
        event=json.loads((root/'审看记录.jsonl').read_text());event.pop('composition_note')
        (root/'审看记录.jsonl').write_text(json.dumps(event)+'\n')
        self.assertFalse(summarize(root)['ready_for_user_review'])


if __name__=='__main__':unittest.main()
