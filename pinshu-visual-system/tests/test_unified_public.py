import unittest,json,tempfile,subprocess,sys,hashlib,shutil
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from visual_compiler import ROOT,compile_plan,load_configs
from select_styles import select,handoff
class UnifiedPublicTests(unittest.TestCase):
 def test_all_25_short_names_compile_without_trial_flag(self):
  r,_=load_configs()
  with tempfile.TemporaryDirectory() as tmp:
   d=Path(tmp);(d/'identity.png').write_bytes(b'fixture');(d/'identity.json').write_text(json.dumps(dict(id='user-test',status='approved',identity_asset='identity.png',identity_sha256=hashlib.sha256((d/'identity.png').read_bytes()).hexdigest(),approval_quote='Test fixture authorization only',tested_modes=['character-presenter'],dominant_hand='right',constraints=['Keep the supplied identity.'])))
   for m in r['modes']:
    platform=next((x for x in m.get('allowed_platforms',[]) if x in ['wechat-article','xiaohongshu','wechat-cover-primary']), 'wechat-cover-primary' if m['id']=='literary-crayon-editorial' else 'wechat-article')
    p=compile_plan('A person compares the draft with its source.',platform,m['short_name'],'single-claim',units=1,character_profile=d/'identity.json' if m['character_policy']=='required' else None)
    self.assertEqual(p['visual_card']['mode'],m['id']);self.assertTrue(p['prompt']);self.assertEqual(p['acceptance']['human_review'],'pending')
 def test_unified_pool_excludes_held_and_retired(self):
  r,_=load_configs();ids={x['id'] for x in select('wechat-article','single-claim')['options']}
  self.assertTrue(ids.isdisjoint(r['held_routes']+r['retired_routes']));self.assertIn('soft-volume-editorial',ids);self.assertIn('gimi-quirky-sketch-none',ids)
 def test_missing_dependency_is_visible_and_cannot_execute(self):
  with tempfile.TemporaryDirectory() as tmp:
   xs=select('wechat-article','single-claim',skills_dir=tmp)['options'];self.assertTrue(any(x['kind']=='external' and not x['available'] for x in xs))
   with self.assertRaisesRegex(ValueError,'dependency missing'):handoff('怪诞','Original source','wechat-article','single-claim',tmp)
 def test_actual_dependency_handoff_binds_entry_and_source(self):
  with tempfile.TemporaryDirectory() as tmp:
   p=Path(tmp)/'gimi-illustration';p.mkdir();(p/'SKILL.md').write_text('# Fixture dependency: read before execution')
   x=handoff('怪诞','Original source','wechat-article','single-claim',tmp)
   self.assertEqual(x['status'],'pending-dependency-execution');self.assertEqual(x['style']['dependency_sha256'],hashlib.sha256((p/'SKILL.md').read_bytes()).hexdigest());self.assertIsNone(x['actual_model']);self.assertEqual(x['platform'],'wechat-article');self.assertEqual(x['structure'],'single-claim');self.assertEqual(x['platform_profile']['ratio'],'16:9');self.assertTrue(x['platform_profiles_sha256'])
 def test_photo_handoff_requires_actual_source_image(self):
  with tempfile.TemporaryDirectory() as tmp:
   p=Path(tmp)/'heytea-style';p.mkdir();(p/'SKILL.md').write_text('# Fixture')
   with self.assertRaisesRegex(ValueError,'source image required'):handoff('实物涂鸦','Original source','wechat-article','single-claim',tmp)
 def test_platform_scope_and_supplied_character_are_preserved(self):
  with self.assertRaisesRegex(ValueError,'not available'):compile_plan('A cat rests.','wechat-cover-primary','柔和体积','single-claim',units=1)
  with self.assertRaisesRegex(ValueError,'requires'):compile_plan('A person explains.','wechat-article','角色讲解','single-claim',units=1)
 def test_relocated_clean_copy_does_not_read_home_configuration(self):
  with tempfile.TemporaryDirectory() as tmp:
   p=Path(tmp)/'test-skills'/'pinshu-visual-system';shutil.copytree(ROOT,p,ignore=shutil.ignore_patterns('__pycache__','work'))
   empty=Path(tmp)/'empty-skills';empty.mkdir()
   proc=subprocess.run([sys.executable,'-B',str(p/'scripts/select_styles.py'),'--platform','wechat-article','--skills-dir',str(empty)],capture_output=True,text=True,cwd=tmp)
   self.assertEqual(proc.returncode,0,proc.stderr);data=json.loads(proc.stdout);self.assertTrue(all(not x['available'] for x in data['options'] if x['kind']=='external'))
 def test_no_private_paths_or_dangling_symlinks_in_candidate(self):
  from audit_public_bundle import audit_root
  result=audit_root(ROOT)
  self.assertEqual(result['hits'],[],result)
  self.assertFalse(any(x.is_symlink() for x in ROOT.rglob('*')))

 def test_changed_identity_is_rejected(self):
  with tempfile.TemporaryDirectory() as tmp:
   p=Path(tmp);(p/'id.png').write_bytes(b'original');spec=dict(id='user-test',status='approved',identity_asset='id.png',identity_sha256=hashlib.sha256((p/'id.png').read_bytes()).hexdigest(),approval_quote='Test fixture only',tested_modes=['character-presenter'],dominant_hand='right',constraints=['Keep identity.']);(p/'profile.json').write_text(json.dumps(spec));(p/'id.png').write_bytes(b'changed')
   with self.assertRaisesRegex(ValueError,'hash missing or changed'):compile_plan('A person explains.','wechat-article','角色讲解','single-claim',units=1,character_profile=p/'profile.json')
 def test_cli_transaction_has_no_half_output_on_write_failure(self):
  import importlib.util
  from unittest import mock
  import visual_compiler
  with tempfile.TemporaryDirectory() as tmp:
   d=Path(tmp);source=d/'source.md';source.write_text('A person reviews a draft.');out=d/'output';argv=['visual_compiler.py','--content-file',str(source),'--platform','wechat-article','--mode','柔和体积','--structure','single-claim','--units','1','--output-dir',str(out)];original=Path.write_text
   def fail_prompt(path,*args,**kwargs):
    if path.name=='prompt-final.txt':raise OSError('simulated storage failure')
    return original(path,*args,**kwargs)
   with mock.patch.object(sys,'argv',argv),mock.patch.object(Path,'write_text',fail_prompt),self.assertRaises(SystemExit):visual_compiler.main()
   self.assertFalse(out.exists());self.assertFalse(list(d.glob('.visual-plan-*')))

 def test_compiled_prompt_keeps_source_relationships_and_complete_medium(self):
  p=compile_plan('Two craft workers fold one continuous paper strip together.','wechat-article','柔和体积','single-claim',units=1)
  self.assertIn('Two craft workers fold one continuous paper strip together.',p['prompt'])
  self.assertIn('participants, actions and physical connections',p['prompt'])
  self.assertIn('绘画化',p['prompt'])

 def test_shortened_actual_image_request_is_rejected(self):
  from verify_generation_input import verify
  p=compile_plan('Two people fold a continuous paper strip.','wechat-article','柔和体积','single-claim',units=1)
  cut=p['prompt'].replace('## 文字与验收','')
  with self.assertRaisesRegex(ValueError,'missing or shortened'):verify(p,dict(prompt=cut))
 def test_full_prompt_with_recorded_extra_requirements_is_allowed(self):
  from verify_generation_input import verify
  p=compile_plan('Two people fold a continuous paper strip.','wechat-article','柔和体积','single-claim',units=1)
  self.assertEqual(verify(p,dict(prompt=p['prompt']+'\nNo visible text.'))['status'],'PASS')

 def test_mixed_source_instructions_are_not_visible_copy(self):
  source='两位手艺人共同折纸。公开原创假想场景，无日期、无品牌、无文字。'
  p=compile_plan(source,'wechat-article','柔和体积','single-claim',units=1)
  self.assertEqual(p['image_text_policy']['raster_labels'],[])
  self.assertFalse(p['image_text_policy']['source_is_caption'])
  self.assertIn(source,p['prompt'])
  self.assertIn('picture-only illustration',p['prompt'])
  self.assertIn('context only',p['prompt'])
 def test_single_label_has_explicit_raster_allowlist(self):
  p=compile_plan('先核对原文，再看缩略图。','wechat-article','手帐','single-claim',units=1,exact_text=['核对原文'])
  self.assertEqual(p['image_text_policy']['raster_labels'],['核对原文'])
  self.assertEqual(p['image_text_policy']['composite_labels'],[])
 def test_editable_labels_are_not_raster_copy(self):
  labels=['核对原文','审看缩略图']
  p=compile_plan('核对原文，审看缩略图。','wechat-article','手帐','process',units=2,exact_text=labels)
  self.assertEqual(p['image_text_policy']['raster_labels'],[])
  self.assertEqual(p['image_text_policy']['composite_labels'],labels)
  self.assertIn('picture-only illustration',p['prompt'])
 def test_method_source_notes_are_not_implicit_poster_text(self):
  from visual_compiler import compile_method_candidate
  p=compile_method_candidate('A person makes paper. Fictional production scene.','xiaohongshu','oriental-material-craft','single-claim',candidate_test=True)
  self.assertEqual(p['image_text_policy']['raster_labels'],[])
  titled=compile_method_candidate('A person makes paper.','xiaohongshu','oriental-material-craft','single-claim',title='Paper',candidate_test=True)
  self.assertEqual(titled['image_text_policy']['raster_labels'],['Paper'])
