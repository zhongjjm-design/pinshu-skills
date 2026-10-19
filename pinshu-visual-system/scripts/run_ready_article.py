#!/usr/bin/env python3
"""Consume the explicitly paired ready article and publishing kit; record progress.

Asset files and outputs stay inside the article's process folder. Never selects
latest, rewrites the authoritative article, generates assets, or publishes.
"""
import argparse
from argparse import Namespace
from datetime import datetime, date
import hashlib
import json
from pathlib import Path
import re
import sys
from portable import local_now, ensure_utf8_mode

SKILLS = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(SKILLS/'pinshu-wechat-layout/scripts'))
from article_header import read_metadata
from run_article_pipeline import run

START = '<!-- pinshu-visual-progress:start -->'
END = '<!-- pinshu-visual-progress:end -->'


def resolve(base, value):
    path = Path(value).expanduser()
    return (path if path.is_absolute() else base/path).resolve()


def kit_requirements_sha(kit):
    # Progress is a view of execution, not a changing image requirement.
    text=kit.read_text(encoding='utf-8-sig').replace('\r\n','\n')
    text=re.sub(r'^## 配图排版进度[^\S\n]*\n.*?(?=^## |\Z)', '', text, flags=re.M|re.S)
    return hashlib.sha256(text.strip().encode('utf-8')).hexdigest()


def validate_preview(preview, process, article, plan):
    preview=preview.resolve()
    if not preview.is_relative_to(process) or not preview.is_file():
        raise ValueError('Preview must exist in this article process folder')
    candidates=[preview.parent/'流程核验.json',preview.parent/'试排记录.json']
    receipt=next((x for x in candidates if x.is_file()),None)
    if not receipt:
        raise ValueError('Preview needs an adjacent pipeline or layout receipt')
    data=json.loads(receipt.read_text(encoding='utf-8'))
    full=hashlib.sha256(article.read_bytes()).hexdigest()
    from article_header import split_header
    body=hashlib.sha256(split_header(article.read_bytes())[1]).hexdigest()
    if data.get('source_sha256') not in {full,body} or data.get('status') in {'FAILED','RUNNING','CAPTURE_PENDING'}:
        raise ValueError('Preview receipt does not bind the current article or successful layout')
    if data.get('preview')!=str(preview) or data.get('preview_sha256')!=hashlib.sha256(preview.read_bytes()).hexdigest():
        raise ValueError('Preview file/path differs from its receipt')
    if receipt.name=='流程核验.json':
        if data.get('preview')!=str(preview) or data.get('plan_sha256')!=hashlib.sha256(plan.read_bytes()).hexdigest():
            raise ValueError('Preview path/plan differs from its pipeline receipt')
    else:
        if preview.name!='公众号图文排版预览.html':
            raise ValueError('Independent build preview must be the recorded layout workbench')
        assets=json.loads(plan.read_text(encoding='utf-8'))['assets']
        expected=sorted(hashlib.sha256(resolve(plan.parent,a['file']).read_bytes()).hexdigest() for a in assets)
        actual=sorted(a['sha256'] for a in data.get('images_verified',[]))
        if expected!=actual:
            raise ValueError('Independent preview images differ from current image plan')
    return preview


def binding(article, kit, output=None, require_kit_hash=True):
    article, kit = article.resolve(), kit.resolve()
    if kit != article.with_name(article.stem+'·发布物料包.md'):
        raise ValueError('Publishing kit must be beside the explicitly selected article with its paired filename')
    info, _ = read_metadata(article.read_bytes())
    for key in ('账号', '定稿日期', '写手模型', '过程文件夹', '配图排版进度'):
        if not info.get(key):
            raise ValueError('Article file information missing: '+key)
    if not re.fullmatch(r'\d{4}-\d{2}-\d{2}',info['定稿日期']):
        raise ValueError('定稿日期 must be YYYY-MM-DD')
    try:
        date.fromisoformat(info['定稿日期'])
    except ValueError:
        raise ValueError('定稿日期 must be YYYY-MM-DD')
    if article.parent.name!=info['账号'] or not article.name.startswith(info['定稿日期']+'_'):
        raise ValueError('Ready article account/date differs from folder or filename')
    if article.parent.parent.name!='08_定稿待发':
        raise ValueError('Ready article must be in <workspace>/08_定稿待发/[账号]')
    material, _ = read_metadata(kit.read_bytes())
    if resolve(kit.parent, material.get('正文路径', '')) != article:
        raise ValueError('Publishing kit points to another article')
    process = resolve(article.parent, info['过程文件夹'])
    if not process.is_dir():
        raise ValueError('Article process folder does not exist')
    if not material.get('配图任务路径'):
        raise ValueError('Publishing kit missing 配图任务路径')
    plan = resolve(kit.parent, material['配图任务路径'])
    if not plan.is_relative_to(process) or not plan.is_file():
        raise ValueError('Image plan must exist inside the article process folder')
    data = json.loads(plan.read_text(encoding='utf-8'))
    original = resolve(plan.parent, data['source_md'])
    if original != article or hashlib.sha256(article.read_bytes()).hexdigest() != data['article_sha256']:
        raise ValueError('Image plan must bind the selected ready article and its current hash; review anchors first')
    if require_kit_hash and (resolve(plan.parent,data.get('publishing_kit',''))!=kit or
            data.get('publishing_kit_sha256')!=kit_requirements_sha(kit)):
        raise ValueError('Publishing kit requirements changed or are unbound; reconcile image needs and use --bind-kit')
    if output and not output.resolve().is_relative_to(process):
        raise ValueError('Output must stay inside the article process folder')
    for asset in data['assets']:
        for key in ('file','original_file','publish_clean_report','editable_source','render_receipt'):
            if asset.get(key) and not resolve(plan.parent, asset[key]).is_relative_to(process):
                raise ValueError('Article screenshot/image must stay in its process folder: '+key)
    return process, plan


def record_progress(kit, state, preview=None, note='', expected=None):
    raw = kit.read_bytes()
    if expected is not None and raw != expected:
        raise ValueError('Publishing kit changed during this run; progress was not overwritten')
    text = raw.decode('utf-8-sig')
    timestamp = local_now().isoformat(timespec='seconds')
    block = START+'\n更新：'+timestamp+'\n\n'+state+'\n'
    if preview:
        preview = preview.resolve()
        block += '\n[一键打开排版预览](<'+str(preview)+'>)\n'
    if note:
        block += '\n待办/说明：'+note+'\n'
    block += '\n用户审美/微信真机：未据此确认；未发布。\n'+END
    if START in text or END in text:
        if text.count(START)!=1 or text.count(END)!=1 or text.index(START)>text.index(END):
            raise ValueError('Malformed publishing-kit progress markers')
        a, b = text.index(START), text.index(END)+len(END)
        text = text[:a]+block+text[b:]
    else:
        heading = re.search(r'^## 配图排版进度\s*$', text, re.M)
        if heading:
            text = text[:heading.end()]+'\n\n'+block+text[heading.end():]
        else:
            text += '\n\n## 配图排版进度\n\n'+block+'\n'
    # Recheck immediately before atomic replacement; no article/body mutation.
    if kit.read_bytes()!=raw:
        raise ValueError('Publishing kit changed before progress write')
    temporary = kit.with_name(kit.name+'.progress-tmp')
    temporary.write_text(text, encoding='utf-8')
    temporary.replace(kit)


def check_format(article, kit):
    """Only check the 08 pair's file-information format; nothing is generated. Returns a list of problems in plain words."""
    problems=[]
    article, kit = article.resolve(), kit.resolve()
    if not article.is_file(): return ['正文不存在：'+str(article)]
    if kit != article.with_name(article.stem+'·发布物料包.md'):
        problems.append('物料包文件名要是「正文文件名·发布物料包.md」，并和正文放在同一个文件夹')
    if not kit.is_file(): return problems+['物料包不存在：'+str(kit)]
    try:
        info, _ = read_metadata(article.read_bytes())
    except Exception as exc:
        return problems+['正文开头的文件信息格式不对（要平铺的 YAML，值用双引号）：'+str(exc)]
    for key in ('账号', '定稿日期', '写手模型', '过程文件夹', '配图排版进度'):
        if not info.get(key): problems.append('正文文件信息缺「'+key+'」')
    day=info.get('定稿日期','')
    if day and not re.fullmatch(r'\d{4}-\d{2}-\d{2}',day): problems.append('定稿日期要写成 YYYY-MM-DD')
    if info.get('账号') and article.parent.name!=info['账号']: problems.append('正文所在文件夹名和「账号」不一致')
    if day and not article.name.startswith(day+'_'): problems.append('正文文件名要以「定稿日期_」开头')
    if article.parent.parent.name!='08_定稿待发': problems.append('正文要放在 <workspace>/08_定稿待发/[账号]/ 下')
    if info.get('过程文件夹') and not resolve(article.parent, info['过程文件夹']).is_dir(): problems.append('「过程文件夹」指向的目录不存在')
    try:
        material, _ = read_metadata(kit.read_bytes())
    except Exception as exc:
        return problems+['物料包开头的文件信息格式不对：'+str(exc)]
    if not material.get('正文路径'): problems.append('物料包文件信息缺「正文路径」')
    elif resolve(kit.parent, material['正文路径'])!=article: problems.append('物料包的「正文路径」指向了别的文件')
    if not material.get('配图任务路径'): problems.append('物料包文件信息缺「配图任务路径」')
    return problems


def execute(args):
    if getattr(args,'check_format',False):
        problems=check_format(args.article,args.kit)
        if problems:
            raise SystemExit('格式不对，共 %d 处：\n- '%len(problems)+'\n- '.join(problems))
        return '格式检查通过：正文和物料包的文件信息齐全、互相配对。（只查格式，没有做配图或排版）'

    process, plan = binding(args.article, args.kit, args.output_dir,require_kit_hash=not getattr(args,'bind_kit',False))
    if getattr(args,'bind_kit',False):
        data=json.loads(plan.read_text(encoding='utf-8'))
        data.update(publishing_kit=str(args.kit.resolve()),publishing_kit_sha256=kit_requirements_sha(args.kit))
        plan.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
        return plan
    before = args.kit.read_bytes()
    if args.record_progress:
        preview = args.preview
        if preview:
            preview=validate_preview(preview,process,args.article,plan)
        record_progress(args.kit, args.record_progress, preview, args.note, before)
        return args.kit
    if not args.output_dir:
        raise ValueError('Rendering needs --output-dir inside the process folder')
    if not args.prepare_only and args.space_id is None:
        raise ValueError('Use existing ego TaskSpace --space-id, or --prepare-only')
    try:
        result = run(Namespace(draft=args.article, plan=plan, output_dir=args.output_dir,
            writer_skill=SKILLS/'pinshu-write', layout_skill=SKILLS/'pinshu-wechat-layout',
            ready_mode=True,prepare_only=args.prepare_only, space_id=args.space_id, page=args.page, template=args.template))
    except Exception as exc:
        record_progress(args.kit, '配图/排版：本轮失败', note=str(exc), expected=before)
        raise
    flow = json.loads((args.output_dir/'流程核验.json').read_text(encoding='utf-8'))
    status = flow['status']
    carried = None
    if getattr(args,'carry_reviews_from',None) and status.startswith('TECHNICAL_CHECKS_PASS'):
        from record_article_review import carry_over
        previous=args.carry_reviews_from.resolve()
        if not previous.is_relative_to(process):
            raise ValueError('--carry-reviews-from must be an earlier output folder of this article')
        carried=carry_over(previous,args.output_dir)
    if status == 'CAPTURE_PENDING':
        record_progress(args.kit, '配图：待截图；排版：待配图', note='待截图清单：'+str(result)+'；交能截图的 Agent 或 CleanShot X；禁止 AI 顶替。', expected=before)
    else:
        note='本地试排已生成，当前图意、手机可读性和用户选择仍按回执待审。'
        if carried:
            note+='沿用上一轮审看 %d 张；需重新看图：%s。'%(len(carried['carried_over']),'、'.join(carried['needs_review']) or '无')
        record_progress(args.kit, '配图：已生成交接；排版：'+status, result, note, before)
    if carried:
        print(json.dumps(carried,ensure_ascii=False))
    return result


if __name__ == '__main__':
    ensure_utf8_mode()
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--article', type=Path, required=True)
    p.add_argument('--kit', type=Path, required=True)
    p.add_argument('--output-dir', type=Path)
    p.add_argument('--prepare-only', action='store_true')
    p.add_argument('--space-id', type=int)
    p.add_argument('--page', default='p1')
    p.add_argument('--template', choices=['approved','warm','green','orange','blue','classic','split'], default='approved')
    p.add_argument('--carry-reviews-from',type=Path,help='earlier output folder of this article: images whose bytes, template, slot and paragraph did not change keep their review; only changed ones need a new look')
    p.add_argument('--bind-kit',action='store_true',help='Agent has reconciled the kit image needs and plan; bind their current version')
    p.add_argument('--check-format',action='store_true',help='Only check the 08 article/kit file information and pairing; generates nothing')
    p.add_argument('--record-progress', help='Record actual partial progress without rendering')
    p.add_argument('--preview', type=Path)
    p.add_argument('--note', default='')
    print(execute(p.parse_args()))
