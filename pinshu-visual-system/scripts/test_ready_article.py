"""Ready-folder end-to-end regressions for file info, pairing and progress."""
import hashlib
import json
from pathlib import Path
import tempfile
import unittest
from argparse import Namespace
from run_ready_article import execute, binding, record_progress, kit_requirements_sha
from article_file_info import split_header


class ReadyTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory();self.addCleanup(self.temp.cleanup)
        self.root=Path(self.temp.name)/'workspace/08_定稿待发/测试账号';self.root.mkdir(parents=True)
        self.process=self.root/'过程';self.process.mkdir()
        self.article=self.root/'2026-10-11_九步实操.md'
        self.article.write_text('---\n账号: "测试账号"\n定稿日期: "2026-10-11"\n写手模型: "测试写手"\n过程文件夹: '+json.dumps(str(self.process))+'\n配图排版进度: "详见物料包"\n---\n# 九步实操\n\n开篇。\n\n'+''.join(f'## 第{i}步\n\n步骤{i}的完整段落。\n\n' for i in range(1,10))+'### 资料来源\n\n[来源](https://example.com)\n')
        self.plan=self.process/'配图任务.json'
        self.plan.write_text(json.dumps({'source_md':str(self.article),'article_sha256':hashlib.sha256(self.article.read_bytes()).hexdigest(),'assets':[]},ensure_ascii=False))
        self.kit=self.article.with_name(self.article.stem+'·发布物料包.md')
        self.kit.write_text('---\n正文路径: '+json.dumps(str(self.article))+'\n配图任务路径: '+json.dumps(str(self.plan))+'\n---\n# 发布物料包\n\n人工选的摘要保持。\n\n## 配图排版进度\n\n人工备注保留。\n\n## 其他\n\n不要覆盖。\n')

        data=json.loads(self.plan.read_text());data.update(publishing_kit=str(self.kit),publishing_kit_sha256=kit_requirements_sha(self.kit));self.plan.write_text(json.dumps(data,ensure_ascii=False))

    def args(self, **kw):
        args=dict(article=self.article,kit=self.kit,output_dir=self.process/'试排',prepare_only=True,space_id=None,page='p1',template='approved',record_progress=None,preview=None,note='')
        return Namespace(**(args|kw))

    def test_ready_nine_chapter_roundtrip_separates_header_and_records_preview(self):
        before=self.article.read_bytes();result=execute(self.args())
        self.assertTrue(result.exists());self.assertEqual(self.article.read_bytes(),before)
        exported=self.process/'试排/正文导出/正文.md'
        self.assertEqual(exported.read_bytes(),split_header(before)[1])
        source=(self.process/'试排/六款试排/source.html').read_text()
        self.assertNotIn('写手模型',source);self.assertNotIn('过程文件夹',source)
        self.assertEqual(source.count('<h2>'),9)
        kit=self.kit.read_text();self.assertIn(str(result),kit);self.assertIn('PREPARED_ONLY',kit)
        self.assertIn('人工备注保留',kit);self.assertIn('不要覆盖',kit)
        self.preview=result

    def test_pair_source_hash_and_output_boundaries(self):
        with self.assertRaisesRegex(ValueError,'paired'):binding(self.article,self.plan)
        with self.assertRaisesRegex(ValueError,'process folder'):binding(self.article,self.kit,self.root/'outside')
        self.article.write_text(self.article.read_text()+'新增内容')
        with self.assertRaisesRegex(ValueError,'hash'):binding(self.article,self.kit)

    def test_kit_changed_progress_is_not_overwritten(self):
        before=self.kit.read_bytes();self.kit.write_text(self.kit.read_text()+'作者刚改的内容')
        with self.assertRaisesRegex(ValueError,'changed'):record_progress(self.kit,'done',expected=before)
        self.assertIn('作者刚改的内容',self.kit.read_text())

    def test_unclosed_header_and_bom_crlf(self):
        with self.assertRaisesRegex(ValueError,'Unclosed'):split_header(b'---\naccount: test\n# title')
        header,body=split_header(b'\xef\xbb\xbf---\r\naccount: "test"\r\n---\r\n# title\r\n\r\nbody\r\n')
        self.assertEqual(body,b'# title\r\n\r\nbody\r\n')

    def test_capture_pending_kit_has_queue_not_false_preview(self):
        data=json.loads(self.plan.read_text());data['assets']=[{'asset_kind':'evidence-screenshot','role':'body','purpose':'展示原话','source_url':'https://example.com/post','filename':'01.png','capture_region':'精确原话始末','after_paragraph':'步骤1的完整段落。','after_prefix':'步骤1','review_state':'capture-pending'}]
        self.plan.write_text(json.dumps(data,ensure_ascii=False));execute(self.args())
        text=self.kit.read_text();self.assertIn('待截图',text);self.assertNotIn('一键打开排版预览',text)
        self.assertIn('CleanShot X',text)

    def test_partial_progress_is_idempotent_and_preserves_manual_notes(self):
        execute(self.args(output_dir=None,record_progress='配图完成；排版待做'))
        execute(self.args(output_dir=None,record_progress='配图返修；排版待做'))
        text=self.kit.read_text();self.assertEqual(text.count('pinshu-visual-progress:start'),1)
        self.assertNotIn('配图完成；排版待做',text);self.assertIn('人工备注保留',text)

    def test_new_screenshot_cannot_bake_frame(self):
        from PIL import Image
        from prepare_article_handoff import prepare
        image=self.process/'screen.png';Image.new('RGB',(1080,400),'navy').save(image)
        data=json.loads(self.plan.read_text())
        data['assets']=[{'asset_kind':'evidence-screenshot','role':'body','purpose':'证据',
            'file':str(image),'original_file':str(image),'source_url':'https://example.com',
            'captured_at':'2026-10-11','attribution':'测试来源','acquisition':'new-capture',
            'frame_baked':True,'after_prefix':'步骤1'}]
        self.plan.write_text(json.dumps(data))
        with self.assertRaisesRegex(ValueError,'unframed'):
            prepare(self.plan,self.process/'handoff',Path(__file__).resolve().parents[2]/'pinshu-wechat-layout')

    def test_ready_does_not_call_writer_exporter(self):
        from unittest.mock import patch
        with patch('run_article_pipeline.load_export',side_effect=AssertionError('writer must not run')):
            self.assertTrue(execute(self.args()).exists())

    def test_changed_kit_requirements_refuse_old_plan_until_agent_rebinds(self):
        self.kit.write_text(self.kit.read_text().replace('人工选的摘要保持。','截图区域已改。'))
        with self.assertRaisesRegex(ValueError,'requirements changed'):execute(self.args())
        execute(self.args(output_dir=None,bind_kit=True))
        self.assertTrue(execute(self.args()).exists())

    def test_cross_article_or_unreceipted_preview_refused(self):
        other=Path(self.temp.name)/'别篇.html';other.write_text('<html>wrong</html>')
        with self.assertRaisesRegex(ValueError,'process folder'):
            execute(self.args(output_dir=None,record_progress='完成',preview=other))
        local=self.process/'错稿.html';local.write_text('<html>wrong</html>')
        with self.assertRaisesRegex(ValueError,'adjacent'):
            execute(self.args(output_dir=None,record_progress='完成',preview=local))
        result=execute(self.args())
        execute(self.args(output_dir=None,record_progress='试排待审',preview=result))
        result.write_text(result.read_text()+'changed')
        with self.assertRaisesRegex(ValueError,'differs'):
            execute(self.args(output_dir=None,record_progress='完成',preview=result))

    def test_account_date_and_ready_directory_checked(self):
        before=self.article.read_text()
        for changed in [before.replace('账号: "测试账号"','账号: "别的账号"'),before.replace('定稿日期: "2026-10-11"','定稿日期: "bad"')]:
            self.article.write_text(changed)
            with self.assertRaises(ValueError):binding(self.article,self.kit)
        self.article.write_text(before)
        outside=Path(self.temp.name)/self.article.name;outside.write_text(before)
        kit=outside.with_name(outside.stem+'·发布物料包.md');kit.write_text(self.kit.read_text())
        with self.assertRaisesRegex(ValueError,'account/date'):binding(outside,kit)

    def test_unquoted_metadata_and_empty_key_refused(self):
        from article_header import read_metadata
        for raw in [b'---\na: bare\n---\nbody',b'---\n: "bad"\n---\nbody',b"---\na: 'single'\n---\nbody"]:
            with self.assertRaises(ValueError):read_metadata(raw)

    def test_tables_of_two_to_four_columns_parse_and_wider_ones_are_refused(self):
        from prepare_article_handoff import load_layout
        parser=load_layout(Path(__file__).resolve().parents[2]/'pinshu-wechat-layout')
        for table in ['名称 | 数值\n--- | ---\n甲 | 1','名称 | 数值\n:--- | ---:\n甲 | 1','| 名称 | 数值 |\n| --- | --- |\n| 甲 | 1 |','| 一 | 二 | 三 | 四 |\n| - | - | - | - |\n| 1 | 2 | 3 | 4 |']:
            source=self.process/'table.md';source.write_text('# 表格\n\n'+table+'\n')
            title,blocks=parser.parse_markdown(source)
            self.assertEqual(title,'表格');self.assertTrue(any(b.name=='table' for b in blocks))
        source=self.process/'table.md';source.write_text('# 表格\n\n| a | b | c | d | e |\n| - | - | - | - | - |\n| 1 | 2 | 3 | 4 | 5 |\n')
        with self.assertRaisesRegex(ValueError,'2 to 4 columns'):parser.parse_markdown(source)

    def test_markdown_capture_anchor_works_without_layout_parser(self):
        self.article.write_text(self.article.read_text().replace('步骤1的完整段落。','**步骤1**的完整段落。'))
        data=json.loads(self.plan.read_text());data['article_sha256']=hashlib.sha256(self.article.read_bytes()).hexdigest()
        data['assets']=[{'asset_kind':'evidence-screenshot','role':'body','purpose':'证据','source_url':'https://example.com','filename':'01.png','capture_region':'准确区域','after_paragraph':'**步骤1**的完整段落。','after_prefix':'步骤1','review_state':'capture-pending'}]
        self.plan.write_text(json.dumps(data))
        self.assertTrue(execute(self.args()).exists())

    def test_production_receipts_must_stay_in_process_folder(self):
        external=Path(self.temp.name)/'receipt.json';external.write_text('{}')
        data=json.loads(self.plan.read_text());data['assets']=[{'publish_clean_report':str(external)}];self.plan.write_text(json.dumps(data))
        with self.assertRaisesRegex(ValueError,'process folder'):binding(self.article,self.kit)

    def test_draft_exporter_cannot_silently_change_body(self):
        from unittest.mock import patch
        from run_article_pipeline import run,SKILLS
        def bad_export(source,out):
            out.mkdir();(out/'正文.md').write_text('# 被改过的正文\n\n内容丢失。')
        args=Namespace(draft=self.article,plan=self.plan,output_dir=self.process/'bad-export',
            writer_skill=SKILLS/'pinshu-write',layout_skill=SKILLS/'pinshu-wechat-layout',prepare_only=True)
        with patch('run_article_pipeline.load_export',return_value=bad_export):
            with self.assertRaisesRegex(ValueError,'changed article body'):run(args)

    def test_failure_is_written_to_kit(self):
        self.process.joinpath('试排').mkdir()
        with self.assertRaises(FileExistsError):execute(self.args())
        self.assertIn('本轮失败',self.kit.read_text())


if __name__=='__main__':unittest.main()
