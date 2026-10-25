"""Team meeting 2026-10-12 reflow: one-image replacement, review carry-over, rejected captures,
structured failure receipts and portability helpers."""
import hashlib
import importlib
import json
from argparse import Namespace
from pathlib import Path
import sys
import tempfile
import unittest
from unittest import mock

from PIL import Image

import portable
from capture_evidence import reject_capture, failures_for, MAX_ATTEMPTS
from record_article_review import carry_over, record, summarize
from replace_asset import replace
from run_article_pipeline import run, SKILLS


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


class ReplaceAssetTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(); self.addCleanup(self.tmp.cleanup)
        self.process = Path(self.tmp.name).resolve() / '过程'
        (self.process / '配图').mkdir(parents=True)
        self.files = []
        for i, colour in enumerate(('navy', 'red', 'green'), 1):
            f = self.process / '配图' / f'0{i}.png'; Image.new('RGB', (60, 30), colour).save(f); self.files.append(f)
        self.plan = self.process / '配图任务.json'
        assets = [{'role': 'body', 'asset_kind': 'real-photo', 'file': str(f), 'original_file': str(f),
                   'attribution': '测试', 'purpose': '测试', 'after_prefix': f'第{i}段', 'filename': f.name,
                   'mobile_review': {'state': 'readable', 'image_sha256': sha(f)}} for i, f in enumerate(self.files, 1)]
        self.plan.write_text(json.dumps({'source_md': 'x.md', 'article_sha256': 'x', 'assets': assets}, ensure_ascii=False), encoding='utf-8')

    def test_only_the_target_changes_and_revision_is_recorded(self):
        before = json.loads(self.plan.read_text(encoding='utf-8'))['assets']
        hashes = [sha(f) for f in self.files]
        new = self.process / '配图' / '02_修正.png'; Image.new('RGB', (60, 30), 'orange').save(new)
        result = replace(self.plan, '02.png', 'Claude', '原图偏色，重做', file=new)
        after = json.loads(self.plan.read_text(encoding='utf-8'))['assets']
        self.assertEqual(result['unchanged_assets'], 2)
        self.assertEqual(after[0], before[0]); self.assertEqual(after[2], before[2])
        self.assertEqual(after[1]['file'], str(new))
        self.assertNotIn('mobile_review', after[1])
        revision = after[1]['revisions'][-1]
        self.assertEqual((revision['by'], revision['old_sha256'], revision['new_sha256']), ('Claude', hashes[1], sha(new)))
        self.assertEqual([sha(f) for f in self.files], hashes)  # old files untouched

    def test_fix_left_in_another_workspace_is_refused(self):
        outside = Path(self.tmp.name) / 'Codex工作区' / '02.png'; outside.parent.mkdir()
        Image.new('RGB', (60, 30), 'orange').save(outside)
        before = self.plan.read_bytes()
        with self.assertRaisesRegex(ValueError, 'inside the article process folder'):
            replace(self.plan, '02.png', 'Codex', '重截', file=outside)
        self.assertEqual(self.plan.read_bytes(), before)

    def test_needs_who_why_one_target_and_a_real_change(self):
        with self.assertRaisesRegex(ValueError, '--by and --reason'):
            replace(self.plan, '02.png', '', '', file=self.files[1])
        with self.assertRaisesRegex(ValueError, 'exactly one image'):
            replace(self.plan, '09.png', 'A', 'b', file=self.files[1])
        with self.assertRaisesRegex(ValueError, 'identical'):
            replace(self.plan, '02.png', 'A', 'b', file=self.files[1])

    def test_screenshot_must_come_with_its_capture_receipt(self):
        data = json.loads(self.plan.read_text(encoding='utf-8'))
        data['assets'][0].update(asset_kind='evidence-screenshot', source_url='https://example.com/p')
        del data['assets'][0]['filename']  # like the real 10-12 plan: no explicit output name
        self.plan.write_text(json.dumps(data, ensure_ascii=False), encoding='utf-8')
        with self.assertRaisesRegex(ValueError, 'capture-dir'):
            replace(self.plan, '01.png', 'A', 'b', file=self.files[1])
        cap = self.process / '配图' / '截图_01_重截'; cap.mkdir()
        Image.new('RGB', (60, 30), 'white').save(cap / '截图.png'); Image.new('RGB', (60, 30), 'white').save(cap / '原始截图.png')
        receipt = {'source_url': 'https://translate.goog/p', 'original_url': 'https://example.com/p',
                   'captured_at': '2026-10-12T12:00:00Z', 'delivery_sha256': sha(cap / '截图.png')}
        (cap / '截图回执.json').write_text(json.dumps(receipt), encoding='utf-8')
        replace(self.plan, '01.png', 'Claude', '原图被底部按钮栏遮住', capture_dir=cap)
        asset = json.loads(self.plan.read_text(encoding='utf-8'))['assets'][0]
        self.assertEqual((asset['file'], asset['captured_at'], asset['acquisition']), (str(cap / '截图.png'), receipt['captured_at'], 'new-capture'))
        self.assertEqual(asset['filename'], '01.png')  # the capture's 截图.png never becomes the output name
        receipt['original_url'] = 'https://example.com/other'
        (cap / '截图回执.json').write_text(json.dumps(receipt), encoding='utf-8')
        with self.assertRaisesRegex(ValueError, 'another page'):
            replace(self.plan, '01.png', 'Claude', 'x', capture_dir=cap)


class CarryOverTests(unittest.TestCase):
    """Two images reviewed; one replaced; only that one goes back to pending."""

    def make_run(self, root, colours, template='approved', paragraphs=None):
        (root / '配图交接').mkdir(parents=True); (root / '手机检查').mkdir()
        (root / '整篇效果预览.html').write_text('<html>' + ''.join(colours) + '</html>', encoding='utf-8')
        items = []
        for i, colour in enumerate(colours, 1):
            im = root / '配图交接' / f'0{i}.png'; Image.new('RGB', (1080, 400), colour).save(im)
            view = root / '手机检查' / f'0{i}.png'; Image.new('RGB', (1125, 900), colour).save(view)
            items.append({'filename': im.name, 'image_sha256': sha(im), 'screen_files': [view.name],
                          'screen_sha256': {view.name: sha(view)}, 'image_width_css': 303, 'acquisition': 'reused',
                          'asset_kind': 'real-photo', 'estimated_phone_font_px': 14,
                          'evidence_context': None,
                          'slot_context': {'after_prefix': f'第{i}段', 'caption': '', 'source_label': '测试',
                                           'after_paragraph': (paragraphs or {}).get(i, f'第{i}段正文')}})
        (root / '流程核验.json').write_text(json.dumps({'status': 'TECHNICAL_CHECKS_PASS_VISUAL_REVIEW_PENDING',
            'template': template, 'mobile_review': items}, ensure_ascii=False), encoding='utf-8')
        return root

    def test_only_the_changed_image_needs_a_new_look(self):
        with tempfile.TemporaryDirectory() as tmp:
            old = self.make_run(Path(tmp) / 'run1', ['navy', 'red'])
            for name in ('01.png', '02.png'):
                record(old, name, 'readable', '看过，可读', '测试', [old / '手机检查' / name])
            self.assertTrue(summarize(old)['ready_for_user_review'])
            new = self.make_run(Path(tmp) / 'run2', ['navy', 'orange'])
            result = carry_over(old, new)
            self.assertEqual((result['carried_over'], result['needs_review']), (['01.png'], ['02.png']))
            status = summarize(new)
            self.assertFalse(status['ready_for_user_review'])
            self.assertEqual([i['filename'] for i in status['open_issues'] if i['blocking']], ['02.png'])
            event = json.loads((new / '审看记录.jsonl').read_text(encoding='utf-8').splitlines()[0])
            self.assertTrue(event['carried_over_from']['same_phone_pixels'])
            record(new, '02.png', 'readable', '新图看过', '测试', [new / '手机检查' / '02.png'])
            self.assertTrue(summarize(new)['ready_for_user_review'])

    def test_moved_or_rewritten_paragraph_or_old_receipt_carries_nothing(self):
        with tempfile.TemporaryDirectory() as tmp:
            old = self.make_run(Path(tmp) / 'run1', ['navy'])
            record(old, '01.png', 'readable', '看过', '测试', [old / '手机检查' / '01.png'])
            new = self.make_run(Path(tmp) / 'run2', ['navy'], paragraphs={1: '第1段正文改写了'})
            self.assertEqual(carry_over(old, new)['needs_review'], ['01.png'])
            legacy = self.make_run(Path(tmp) / 'run3', ['navy'])
            flow = json.loads((legacy / '流程核验.json').read_text(encoding='utf-8'))
            del flow['mobile_review'][0]['slot_context']
            (legacy / '流程核验.json').write_text(json.dumps(flow, ensure_ascii=False), encoding='utf-8')
            self.assertEqual(carry_over(old, legacy)['needs_review'], ['01.png'])

    def test_repeated_carry_never_overrides_this_rounds_rejection(self):
        with tempfile.TemporaryDirectory() as tmp:
            old = self.make_run(Path(tmp) / 'run1', ['navy'])
            record(old, '01.png', 'readable', '看过', '测试', [old / '手机检查' / '01.png'])
            new = self.make_run(Path(tmp) / 'run2', ['navy'])
            self.assertEqual(carry_over(old, new)['carried_over'], ['01.png'])
            record(new, '01.png', 'needs-reframe', '这轮看字太小', '测试', [new / '手机检查' / '01.png'])
            again = carry_over(old, new)
            self.assertEqual((again['carried_over'], again['already_reviewed_this_round']), ([], ['01.png']))
            self.assertFalse(summarize(new)['ready_for_user_review'])

    def test_template_change_carries_nothing(self):
        with tempfile.TemporaryDirectory() as tmp:
            old = self.make_run(Path(tmp) / 'run1', ['navy'])
            record(old, '01.png', 'readable', '看过', '测试', [old / '手机检查' / '01.png'])
            new = self.make_run(Path(tmp) / 'run2', ['navy'], template='classic')
            self.assertEqual(carry_over(old, new)['carried_over'], [])


class RejectedCaptureTests(unittest.TestCase):
    def test_looked_and_rejected_counts_toward_the_limit(self):
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / '截图_07'; out.mkdir()
            args = Namespace(selector='article', clip=None, start='', end='', purpose='quote', describe='结论段',
                             translate_to=None, viewport=390)
            for attempt in range(1, MAX_ATTEMPTS + 1):
                for name in ('截图.png', '原始截图.png'):
                    Image.new('RGB', (40, 40), 'white').save(out / name)
                (out / '截图回执.json').write_text('{}', encoding='utf-8')
                if attempt < MAX_ATTEMPTS:
                    count, aside = reject_capture(out, 'https://note.com/x', args, '底部按钮栏压住正文')
                    self.assertEqual(count, attempt)
                    self.assertTrue((aside / '截图.png').is_file())
                    self.assertFalse((out / '截图.png').exists())
                else:
                    with self.assertRaises(SystemExit) as stop:
                        reject_capture(out, 'https://note.com/x', args, '仍被遮住')
                    self.assertIn('STOP_MANUAL', str(stop.exception))
            _, items = failures_for(out, 'https://note.com/x')
            self.assertEqual(len(items), MAX_ATTEMPTS)
            self.assertTrue(all(i['error'].startswith('opened and rejected') for i in items))
            self.assertTrue((Path(tmp) / '人工截图指引_截图_07.md').is_file())

    def test_nothing_to_reject_or_no_reason(self):
        with tempfile.TemporaryDirectory() as tmp:
            args = Namespace(selector='a', clip=None, start='', end='', purpose='quote', describe='', translate_to=None, viewport=390)
            with self.assertRaisesRegex(ValueError, 'reason'):
                reject_capture(Path(tmp), 'https://a.b', args, ' ')
            with self.assertRaisesRegex(ValueError, 'No successful capture'):
                reject_capture(Path(tmp), 'https://a.b', args, '遮挡')


class FailureReceiptTests(unittest.TestCase):
    @unittest.skipUnless((SKILLS / 'pinshu-write/scripts/export_article.py').is_file(),
                         'SKIP: optional public pinshu-write exporter absent; maintainer integration only')
    def test_failure_names_last_good_step_and_how_to_resume(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            draft = root / 'draft.md'; draft.write_text('# 标题\n\n正文。', encoding='utf-8')
            plan = root / 'plan.json'; plan.write_text(json.dumps({'source_md': str(draft), 'article_sha256': 'wrong', 'assets': []}), encoding='utf-8')
            args = Namespace(draft=draft, plan=plan, output_dir=root / 'run', writer_skill=SKILLS / 'pinshu-write',
                             layout_skill=SKILLS / 'pinshu-wechat-layout', prepare_only=True)
            with self.assertRaises(ValueError):
                run(args)
            status = json.loads((root / 'run' / '流程核验.json').read_text(encoding='utf-8'))
            self.assertEqual(status['status'], 'FAILED')
            self.assertEqual(status['failed_stage'], '稿件与任务绑定')
            self.assertEqual(status['last_successful_stage'], '正文导出')
            self.assertEqual(status['error_code'], 'ValueError')
            self.assertIn('NEW output folder', status['resume_from'])
            self.assertIn('正文导出', status['existing_outputs'])


class PortabilityTests(unittest.TestCase):
    def test_modules_import_without_fcntl_like_on_windows(self):
        names = ['portable', 'record_article_review', 'article_preview']
        saved = {n: sys.modules.pop(n) for n in names if n in sys.modules}
        try:
            with mock.patch.dict(sys.modules, {'fcntl': None}):
                fresh = importlib.import_module('portable')
                self.assertIsNone(fresh.fcntl)
                importlib.import_module('record_article_review'); importlib.import_module('article_preview')
                with tempfile.TemporaryDirectory() as tmp:
                    fresh.append_line(Path(tmp) / 'log.jsonl', '{"状态": "可读"}')
                    self.assertEqual((Path(tmp) / 'log.jsonl').read_text(encoding='utf-8'), '{"状态": "可读"}\n')
        finally:
            for n in names:
                sys.modules.pop(n, None)
            sys.modules.update(saved)

    def test_local_time_without_tz_database(self):
        with mock.patch('zoneinfo.ZoneInfo', side_effect=Exception('no tzdata')):
            self.assertIsNotNone(portable.local_now().utcoffset())

    def test_utf8_mode_rerun_only_on_windows_without_it(self):
        with mock.patch('subprocess.call', return_value=0) as call:
            portable.ensure_utf8_mode('posix', 0)
            portable.ensure_utf8_mode('nt', 1)
            call.assert_not_called()
            with mock.patch.dict('os.environ', {}, clear=False):
                with self.assertRaises(SystemExit):
                    portable.ensure_utf8_mode('nt', 0)
            self.assertIn('-X', call.call_args[0][0])
            self.assertEqual(call.call_args[1]['env']['PYTHONUTF8'], '1')


class ContactSheetTests(unittest.TestCase):
    """Round 2: a batch planned as 4 ended as 3, and nobody could see the pictures."""

    def test_folder_count_mismatch_is_named(self):
        from contact_sheet import build
        with tempfile.TemporaryDirectory() as tmp:
            folder = Path(tmp) / '模块图'; folder.mkdir()
            for i in (1, 2, 3):
                Image.new('RGB', (120, 80), 'navy').save(folder / f'模块{i}.png')
            result = build(folder=folder, expect=4)
            self.assertEqual(result['found'], 3)
            self.assertIn('应有 4 张，实际找到 3 张', result['problems'])
            page = Path(result['page']).read_text(encoding='utf-8')
            self.assertIn('120×80 像素', page)
            self.assertEqual(page.count('<img '), 3)
            with self.assertRaisesRegex(ValueError, 'not overwritten'):
                build(folder=folder, expect=4, out=Path(result['page']))

    def test_plan_flags_missing_outside_and_case_twins(self):
        from contact_sheet import build
        with tempfile.TemporaryDirectory() as tmp:
            process = Path(tmp) / '过程'; process.mkdir()
            good = process / '01.png'; Image.new('RGB', (50, 50), 'red').save(good)
            outside = Path(tmp) / '别人工作区.png'; Image.new('RGB', (50, 50), 'red').save(outside)
            plan = process / '配图任务.json'
            plan.write_text(json.dumps({'assets': [
                {'file': str(good), 'filename': '图A.png', 'purpose': '说明', 'review_state': '待确认',
                 'revisions': [{'at': '2026-10-12T21:00', 'by': 'Claude', 'reason': '重截'}]},
                {'file': str(outside), 'filename': '图a.png', 'purpose': '说明'},
                {'file': str(process / '没有.png'), 'filename': '03.png'}]}, ensure_ascii=False), encoding='utf-8')
            result = build(plan=plan)
            text = '\n'.join(result['problems'])
            for expected in ('找不到文件：03.png', '不在本篇过程文件夹里：图a.png', '同名冲突：图A.png 和 图a.png', '应有 3 张，实际找到 2 张'):
                self.assertIn(expected, text)
            page = Path(result['page']).read_text(encoding='utf-8')
            self.assertIn('Claude：重截', page)
            self.assertIn("src='01.png'", page)


if __name__ == '__main__':
    unittest.main()
