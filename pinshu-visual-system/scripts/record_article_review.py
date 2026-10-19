#!/usr/bin/env python3
"""Append a source/context-bound visual review; never edit pipeline receipts."""
import argparse
from datetime import datetime, timezone
from portable import append_line, ensure_utf8_mode
import json
from pathlib import Path
from capture_evidence import sha


def read(path):
    return json.loads(path.read_text())


def phone_view_issue(root, item):
    names=set(item['screen_files']);hashes=item.get('screen_sha256',{})
    if not names or set(hashes)!=names:
        return 'phone_views_unbound'
    for name in names:
        path=root/'手机检查'/name
        if not path.is_file() or sha(path)!=hashes[name]:
            return 'phone_view_changed'
    return None


def review_detail_issue(item, event):
    for key, required in item.get('review_requirements', {}).items():
        value = event.get(key + '_note', '')
        if required and (not isinstance(value, str) or not value.strip()):
            return key + '_review_missing'
    return None


def summarize(root):
    flow_path=root/'流程核验.json';flow=read(flow_path)
    if flow['status'] in {'FAILED','CAPTURE_PENDING','PREPARED_ONLY'}:
        return {'status':flow['status'],'ready_for_user_review':False,'open_issues':flow.get('open_issues',[]),
                'pipeline_receipt_sha256':sha(flow_path),'publication':'none'}
    preview=root/'整篇效果预览.html';context_hash=sha(preview)
    entries=[];log=root/'审看记录.jsonl'
    if log.exists():entries=[json.loads(line) for line in log.read_text().splitlines() if line.strip()]
    issues=[];resolved=[]
    for item in flow['mobile_review']:
        file=root/'配图交接'/item['filename'];actual=sha(file)
        if actual!=item['image_sha256']:
            issues.append({'filename':item['filename'],'kind':'asset_changed','blocking':True});continue
        problem=phone_view_issue(root,item)
        if problem:
            issues.append({'filename':item['filename'],'kind':problem,'blocking':True});continue
        matches=[e for e in entries if e['filename']==item['filename'] and e['image_sha256']==actual
            and e['preview_html_sha256']==context_hash and e['template']==flow['template']
            and e['image_width_css']==item['image_width_css']]
        if item.get('asset_kind')=='evidence-screenshot' and item['acquisition']=='unknown':
            issues.append({'filename':item['filename'],'kind':'acquisition_unknown','blocking':True})
        if not matches:
            issues.append({'filename':item['filename'],'kind':'current_context_review_pending','blocking':True})
            if item.get('needs_reframe'):
                issues.append({'filename':item['filename'],'kind':'needs_reframe','blocking':True})
        else:
            latest=matches[-1];resolved.append(latest)
            if latest['state']!='readable':issues.append({'filename':item['filename'],'kind':latest['state'],'note':latest['note'],'blocking':True})
            elif (problem := review_detail_issue(item, latest)):
                issues.append({'filename':item['filename'],'kind':problem,'blocking':True})
        if item.get('estimated_phone_font_px') is None:
            issues.append({'filename':item['filename'],'kind':'font_estimate_unavailable','blocking':False,
                           'note':'DOM estimate unavailable; actual visual review is required'})
    return {'status':'VISUAL_REVIEW_PENDING' if any(i['blocking'] for i in issues) else 'READY_FOR_USER_REVIEW',
            'ready_for_user_review':not any(i['blocking'] for i in issues),'open_issues':issues,'reviews':resolved,
            'pipeline_receipt_sha256':sha(flow_path),'preview_html_sha256':context_hash,
            'review_log_sha256':sha(log) if log.exists() else None,'user_acceptance':'pending',
            'wechat_phone_tested':False,'publication':'none'}


def record(root, filename, state, note, reviewer, views, meaning_note='', legibility_note='', composition_note=''):
    flow=read(root/'流程核验.json')
    if flow['status'] in {'FAILED','CAPTURE_PENDING','PREPARED_ONLY'}:raise ValueError('No completed phone preview to review')
    matches=[m for m in flow['mobile_review'] if m['filename']==filename]
    if len(matches)!=1:raise ValueError('Filename must match one body image')
    item=matches[0];file=root/'配图交接'/filename
    if sha(file)!=item['image_sha256']:raise ValueError('Image changed after pipeline; rebuild first')
    expected={str((root/'手机检查'/name).resolve()) for name in item['screen_files']}
    supplied={str(p.resolve()) for p in views}
    if expected!=supplied:raise ValueError('Review must name all current phone segments for this image')
    problem=phone_view_issue(root,item)
    if problem:raise ValueError(problem+': phone views do not match pipeline receipt; rebuild first')
    details={'meaning_note':meaning_note,'legibility_note':legibility_note,'composition_note':composition_note}
    if state=='readable' and (problem := review_detail_issue(item, details)):
        raise ValueError(problem+': record the actual paragraph/image and phone observations')
    event={'at':datetime.now(timezone.utc).isoformat(),'filename':filename,'image_sha256':sha(file),
           'preview_html_sha256':sha(root/'整篇效果预览.html'),'template':flow['template'],
           'image_width_css':item['image_width_css'],'state':state,'note':note,'reviewer':reviewer,
           'view_files':[{'file':str(p.resolve()),'sha256':sha(p)} for p in views]}
    event.update(details)
    append_line(root/'审看记录.jsonl',json.dumps(event,ensure_ascii=False))
    result=summarize(root)
    (root/'交付状态.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
    return result


def carry_over(old_root, new_root):
    """After one image was replaced and the pipeline re-run into a new folder, keep the reviews of
    images that did not change. A review carries over only when the image bytes, template, slot width
    and the paragraph it follows are all the same as when it was reviewed; everything else stays
    pending (meeting 2026-10-12, IMG-05: changing one picture must not reopen every picture)."""
    old_root,new_root=Path(old_root).resolve(),Path(new_root).resolve()
    old_flow,new_flow=read(old_root/'流程核验.json'),read(new_root/'流程核验.json')
    for flow in (old_flow,new_flow):
        if flow['status'] in {'FAILED','CAPTURE_PENDING','PREPARED_ONLY'}:raise ValueError('Both runs need a completed phone preview')
    old_log=old_root/'审看记录.jsonl'
    events=[json.loads(l) for l in old_log.read_text(encoding='utf-8').splitlines() if l.strip()] if old_log.exists() else []
    old_preview=sha(old_root/'整篇效果预览.html');new_preview=sha(new_root/'整篇效果预览.html')
    new_log=new_root/'审看记录.jsonl'
    current=[json.loads(l) for l in new_log.read_text(encoding='utf-8').splitlines() if l.strip()] if new_log.exists() else []
    carried,pending,kept=[],[],[]
    for item in new_flow['mobile_review']:
        before=[m for m in old_flow['mobile_review'] if m['filename']==item['filename']]
        # Every condition must hold; a run without slot_context (older version) never carries over.
        # Phone pixels are recorded but are not a condition: the browser does not render pixel-identically
        # from run to run even when nothing changed (checked on the 10-12 real article).
        same=(len(before)==1 and before[0]['image_sha256']==item['image_sha256']
              and old_flow['template']==new_flow['template'] and before[0]['image_width_css']==item['image_width_css']
              and before[0].get('evidence_context')==item.get('evidence_context')
              and item.get('slot_context') is not None and before[0].get('slot_context')==item['slot_context'])
        if any(e['filename']==item['filename'] for e in current):
            kept.append(item['filename']);continue  # this round already has its own look; never override it
        reviewed=[e for e in events if same and e['filename']==item['filename'] and e['image_sha256']==item['image_sha256']
                  and e['preview_html_sha256']==old_preview and e['template']==old_flow['template']]
        if not reviewed or phone_view_issue(new_root,item):
            pending.append(item['filename']);continue
        latest=dict(reviewed[-1])
        views=[new_root/'手机检查'/name for name in item['screen_files']]
        latest.update(at=datetime.now(timezone.utc).isoformat(),preview_html_sha256=new_preview,
            view_files=[{'file':str(v.resolve()),'sha256':sha(v)} for v in views],
            carried_over_from={'run_dir':str(old_root),'reviewed_at':reviewed[-1]['at'],
                'same_phone_pixels':sorted(before[0].get('screen_sha256',{}).values())==sorted(item.get('screen_sha256',{}).values())})
        append_line(new_root/'审看记录.jsonl',json.dumps(latest,ensure_ascii=False))
        carried.append(item['filename'])
    result=summarize(new_root)
    (new_root/'交付状态.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    return {'carried_over':carried,'already_reviewed_this_round':kept,'needs_review':pending,'status':result['status']}


if __name__=='__main__':
    ensure_utf8_mode()
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--run-dir',type=Path,required=True)
    p.add_argument('--carry-over-from',type=Path,help='earlier output folder: keep reviews of images that did not change, then stop')
    p.add_argument('--filename');p.add_argument('--state',choices=['readable','needs-reframe','context-check-needed'])
    p.add_argument('--note');p.add_argument('--reviewer')
    p.add_argument('--view',action='append',type=Path)
    p.add_argument('--meaning-note',default='',help='对应正文哪句话；画面是否支持同一对象/条件/含义')
    p.add_argument('--legibility-note',default='',help='当前手机图槽里实际能读到什么，关键行是否完整')
    p.add_argument('--composition-note',default='',help='局部拼接对应关系与读者图注是否清楚')
    a=p.parse_args()
    if a.carry_over_from:
        print(json.dumps(carry_over(a.carry_over_from,a.run_dir),ensure_ascii=False,indent=2));raise SystemExit(0)
    missing=[n for n in ('filename','state','note','reviewer','view') if not getattr(a,n)]
    if missing:p.error('recording a review needs --'+', --'.join(missing))
    print(json.dumps(record(a.run_dir.resolve(),a.filename,a.state,a.note,a.reviewer,a.view,
        a.meaning_note,a.legibility_note,a.composition_note),ensure_ascii=False))
