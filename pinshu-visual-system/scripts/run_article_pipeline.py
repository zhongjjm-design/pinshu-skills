#!/usr/bin/env python3
"""Selected draft -> byte-preserving export -> asset handoff -> styled, light phone preview.

Assets must already exist in the Agent-maintained plan. This does not write,
generate, approve or publish an article. Use one existing ego TaskSpace.
"""
import argparse
import base64
import hashlib
import html
import importlib.util
import json
from pathlib import Path
import time
from PIL import Image
from bs4 import BeautifulSoup
from article_preview import manuscript_blocks, normalized, check_rendered_text
from prepare_article_handoff import prepare, load_layout, export_capture_requests
from capture_evidence import browser, sha
from record_article_review import summarize

SKILLS=Path(__file__).resolve().parents[2]


def write_json(path,data):
    path.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')


def load_export(writer):
    spec=importlib.util.spec_from_file_location('pinshu_export',writer/'scripts/export_article.py')
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
    return module.export


def rebind_plan(plan_path, draft, exported):
    plan=json.loads(plan_path.read_text())
    original=Path(plan['source_md']);original=(original if original.is_absolute() else plan_path.parent/original).resolve()
    if sha(original)!=plan['article_sha256']:raise ValueError('Image plan source changed; review affected anchors first')
    if sha(original) not in {sha(draft),sha(exported)}:
        raise ValueError('Selected draft/body differs from the image plan; no silent hash replacement')
    plan['source_md']=str(exported);plan['article_sha256']=sha(exported)
    for item in plan['assets']:
        for key in ('file','original_file','publish_clean_report','editable_source','render_receipt'):
            if item.get(key):
                path=Path(item[key]);item[key]=str((path if path.is_absolute() else plan_path.parent/path).resolve())
    return plan


def visible_caption(image):
    """Bind review context to the final caption DOM (including explicit suppression).

    The renderer resolves caption -> source label -> alt. Reading its result avoids
    a second implementation drifting from that precedence; hidden ancestors suppress it.
    """
    figure = image.find_parent(attrs={'data-picture': True})
    if figure is None:
        return ''
    def hidden(element):
        style = {}
        for declaration in str(element.get('style', '')).lower().split(';'):
            if ':' in declaration:
                key, value = declaration.split(':', 1)
                style[key.strip()] = value.split('!')[0].strip()
        return (element.has_attr('hidden') or style.get('display') == 'none'
                or style.get('visibility') in {'hidden', 'collapse'})

    if any(hidden(parent) for parent in figure.parents if getattr(parent, 'attrs', None) is not None):
        return ''
    copy = BeautifulSoup(str(figure), 'html.parser')
    for element in list(copy.find_all(True)):
        if element.attrs is not None and hidden(element):
            element.decompose()
    return normalized(' '.join(e.get_text() for e in copy.select('[data-reading-role="caption"], figcaption')))


def make_light(render, handoff, output, expected, source=None, layout_skill=None):
    if source is not None:
        check_rendered_text(source, render['html'], layout_skill, handoff.get('heading_split'))
    elif [normalized(x) for x in render['readingBlocks']]!=expected:
        raise ValueError('Rendered body/source mismatch; no completed preview')
    if any(x['caption_links'] for x in render['themes']):raise ValueError('Caption contains external links')
    soup=BeautifulSoup(render['html'],'html.parser');images=soup.select('[data-picture]:not([data-hero]) img')  # lead image (cover) is checked as a cover, not a body figure
    if len(images)!=len(handoff['body_images']):raise ValueError('Figure count mismatch')
    (output/'轻量图片').mkdir();rows=[]
    remaining=list(handoff['body_images'])
    for i,image in enumerate(images,1):
        # Plans need not be listed in paragraph order. Bind the rendered pixels,
        # not the list index, so an unsorted plan cannot swap evidence images.
        src=image.get('src','')
        if not src.startswith('data:image/') or ';base64,' not in src:raise ValueError('Expected actual renderer image bytes')
        image_hash=hashlib.sha256(base64.b64decode(src.split(';base64,',1)[1],validate=True)).hexdigest()
        candidates=[item for item in remaining if sha(output/'配图交接'/item['filename'])==image_hash
            and item.get('source_url','')==image.get('data-source-url','')]
        if not candidates:raise ValueError('Rendered picture differs from the asset handoff')
        item=candidates[0];remaining.remove(item)
        original=output/'配图交接'/item['filename']
        with Image.open(original) as im:
            im=im.convert('RGB');im.thumbnail((1080,100000),Image.Resampling.LANCZOS)
            dest=output/'轻量图片'/f'{i:02d}.jpg';im.save(dest,quality=88,optimize=True)
            size=list(im.size)
        image['src']=f'轻量图片/{i:02d}.jpg';image['width'],image['height']=map(str,size)
        image['loading']='eager' if i==1 else 'lazy';image['decoding']='sync' if i==1 else 'async'
        # Local zoom is a preview aid. It is not a caption or an external source link.
        a=soup.new_tag('a',href='配图交接/'+item['filename']);a['target']='_blank';a['aria-label']='放大查看截图';image.wrap(a)
        rows.append({'filename':item['filename'],'sha256':sha(original),'preview_size':size,'preview_bytes':dest.stat().st_size,
                     'caption':visible_caption(image)})
    if source is not None:
        check_rendered_text(source, str(soup), layout_skill, handoff.get('heading_split'))
    else:
        actual=[normalized(e.get_text()) for e in soup.select('#article-body [data-reading-role]') if not e.find_parent(attrs={'data-decoration':'true'}) and not e.has_attr('data-decoration')]
        if actual!=expected:raise ValueError('Light preview changed source text')
    css='''*{box-sizing:border-box}body{margin:0;background:#f2f3f4;font-family:-apple-system,"PingFang SC",sans-serif}.paper{width:375px;max-width:100%;margin:auto;background:white}.paper header{padding:25px 22px 0}.paper header h1{font-size:25px;line-height:1.4;margin:0 0 12px}.paper header p{font-size:13px;color:#8b8b81;margin:0 0 25px}#article-body{padding:0 36px 24px;overflow-wrap:break-word}#article-body img{max-width:100%}[data-picture] a{display:block;line-height:0}.preview-note{max-width:375px;margin:auto;padding:16px 20px;font-size:12px;line-height:1.7;color:#65705f}'''
    dest=output/'整篇效果预览.html'
    dest.write_text('<!doctype html><html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>'+html.escape(render['title'])+'</title><style>'+css+'</style></head><body><div class="preview-note">整篇本地试排 · 点击图片可放大 · 未发布</div>'+str(soup)+'</body></html>')
    return dest,rows


def _run_pipeline(args):
    started=time.monotonic();out=args.output_dir.resolve();out.mkdir(parents=True,exist_ok=False)
    timings=[]
    def step(name,fn):
        begin=time.monotonic();state='failed'
        try:
            value=fn();state='completed';return value
        finally:
            timings.append({'stage':name,'state':state,'seconds':round(time.monotonic()-begin,3)})
            write_json(out/'阶段耗时.json',{'timings':timings,'scope':'仅本入口工具耗时，不含之前构思/采集/人工审看'})
    step('初始化状态',lambda:write_json(out/'流程核验.json',{'status':'RUNNING','stage':'initialization','ready_for_user_review':False,'publication':'none'}))
    draft=args.draft.resolve();plan_path=args.plan.resolve();input_hashes={str(draft):sha(draft),str(plan_path):sha(plan_path)}
    from article_file_info import split_header
    original_bytes=draft.read_bytes()
    source=out/'正文导出/正文.md'
    if getattr(args,'ready_mode',False):
        if any(line.rstrip(b'\r\n')==b'===EDITOR NOTES===' for line in original_bytes.splitlines(keepends=True)):
            raise ValueError('Ready article must not contain editor notes')
        header,body=split_header(original_bytes)
        source.parent.mkdir()
        source.write_bytes(body)
        if source.read_bytes()!=split_header(original_bytes)[1]:
            raise ValueError('Ready article body bytes changed during export')
        write_json(source.parent/'正文导出记录.json',{'draft_md':str(draft),
            'draft_sha256':sha(draft),'source_md':str(source),'article_sha256':sha(source),
            'file_information_separated':bool(header),'article_bytes_preserved':True,
            'preservation_scope':'exact body and sources after YAML header',
            'article_state':'指定待发布正文；用户定稿状态来自明确输入'})
    else:
        step('正文导出',lambda:load_export(args.writer_skill)(draft,out/'正文导出'))
        lines=original_bytes.splitlines(keepends=True)
        markers=[i for i,line in enumerate(lines) if line.rstrip(b'\r\n')==b'===EDITOR NOTES===']
        expected=b''.join(lines[:markers[0]]) if markers else original_bytes
        if source.read_bytes()!=expected:
            raise ValueError('Writer exporter changed article body/source bytes')
        header,body=split_header(source.read_bytes())
        if header:
            source.write_bytes(body)
            receipt_path=source.parent/'正文导出记录.json'
            receipt=json.loads(receipt_path.read_text())
            receipt.update(article_sha256=sha(source),file_information_separated=True,
                article_bytes_preserved=True,preservation_scope='exact body and sources after YAML header')
            write_json(receipt_path,receipt)
    plan=step('稿件与任务绑定',lambda:rebind_plan(plan_path,draft,source));write_json(out/'配图任务.json',plan)
    if any(a.get('asset_kind')=='evidence-screenshot' and (not a.get('file') or a.get('review_state')=='capture-pending') for a in plan['assets']):
        request=step('待截图交接',lambda:export_capture_requests(out/'配图任务.json',out/'待截图交接'))
        write_json(out/'流程核验.json',{'status':'CAPTURE_PENDING','capture_requests':str(request),
            'source_sha256':sha(source),'original_sha256':sha(draft),'plan_sha256':sha(plan_path),'timings':timings,'publication':'none','user_acceptance':'pending','ready_for_user_review':False})
        return request
    handoff_path=step('配图交接',lambda:prepare(out/'配图任务.json',out/'配图交接',args.layout_skill))
    layout=load_layout(args.layout_skill)
    workbench=step('七款试排',lambda:layout.run(handoff_path,out/'六款试排'))
    if args.prepare_only:
        write_json(out/'流程核验.json',{'status':'PREPARED_ONLY','browser_check':'pending','user_acceptance':'pending','source_sha256':sha(source),
            'original_sha256':sha(draft),'plan_sha256':sha(plan_path),'preview':str(workbench),'preview_sha256':sha(workbench),'timings':timings,'ready_for_user_review':False})
        return workbench
    render_path=out/'浏览器渲染记录.json'
    step('实际模板渲染',lambda:browser(dict(action='render',space_id=args.space_id,page=args.page,
        url=workbench.as_uri()+'?template='+args.template,result=str(render_path))))
    expected=manuscript_blocks(source, args.layout_skill)
    handoff=json.loads(handoff_path.read_text());render=json.loads(render_path.read_text())
    preview,images=step('轻量整篇预览',lambda:make_light(render,handoff,out,expected,source,args.layout_skill))
    screens=out/'手机检查';screens.mkdir()
    step('手机取景检查',lambda:browser(dict(action='check',space_id=args.space_id,page=args.page,
        url=preview.as_uri(),result=str(out/'浏览器核验.json'),screen_dir=str(screens))))
    checked=json.loads((out/'浏览器核验.json').read_text())
    if any(x['overflow'] or x['caption_links'] for x in checked['views']):raise ValueError('Phone overflow/caption link failure')
    if any(not x.get('loaded',True) for x in checked['screens']):raise ValueError('Phone image did not load')
    manifest=json.loads((out/'配图交接/配图清单.json').read_text())
    mobile=[]
    figures=[s for s in checked['screens'] if s['position']!='top']
    # zip() would silently drop or shift images; each body image must have exactly its own phone view.
    if len(figures)!=len(images):raise ValueError('Phone views (%d) do not match body images (%d); the lead image must not be counted as a body figure'%(len(figures),len(images)))
    by_name={f['filename']:f for f in manifest['files']}
    placed={b['filename']:b for b in handoff['body_images']}
    for image_info,figure in zip(images,figures):
        item=by_name[image_info['filename']]
        placement=placed.get(item['filename'],{})
        prefix=normalized(placement.get('after_prefix',''))
        # Where the picture sits and what the reader sees under it; a review only carries over if this is unchanged.
        slot={'after_prefix':placement.get('after_prefix',''),'caption':image_info['caption'],
              'source_label':placement.get('source_label'),
              'after_paragraph':next((b for b in expected if prefix and b.startswith(prefix)),None)}
        receipt=item.get('capture_receipt',{});width=receipt.get('width') or receipt.get('region',{}).get('width')
        font=receipt.get('min_source_font_px');effective=round(font*figure['image_width_css']/width,1) if font and width else None
        mobile.append({'filename':item['filename'],'acquisition':item.get('acquisition','unknown'),
            'asset_kind':item['asset_kind'],
            'evidence_context':item.get('evidence_context'),'slot_context':slot,
            'review_requirements':{'meaning':True,'legibility':True,
                'composition':bool(item.get('composition_disclosure'))} if item['asset_kind']=='evidence-screenshot' else {},
            'composition_disclosure':item.get('composition_disclosure'),
            'review':{'state':'unknown' if item.get('mobile_review',{}).get('state')=='unknown' else 'pending',
                      'reason':'Current template/slot/preview context has not been reviewed',
                      'prior_image_review':item.get('mobile_review',{'state':'pending'})},'screenshot':figure['file'],
            'screen_files':figure.get('files',[figure['file']]),'image_sha256':item['sha256'],
            'screen_sha256':{name:sha(screens/name) for name in figure.get('files',[figure['file']])},
            'image_width_css':figure['image_width_css'],
            'estimated_phone_font_px':effective,'needs_reframe':True if item.get('mobile_review',{}).get('state')=='needs-reframe' else (effective<12 if effective is not None else None),
            'rule':'低于12px是返修提示；DOM估算不覆盖嵌入图片，也不替代看图。放大入口不等于正文可读通过。'})
    for path,digest in input_hashes.items():
        if sha(Path(path))!=digest:raise ValueError('Input changed during pipeline')
    open_issues=[]
    for item in mobile:
        open_issues.append({'filename':item['filename'],'kind':'current_context_review_pending','blocking':True})
        if item['asset_kind']=='evidence-screenshot' and item['acquisition']=='unknown':open_issues.append({'filename':item['filename'],'kind':'acquisition_unknown','blocking':True})
        if item['needs_reframe']:open_issues.append({'filename':item['filename'],'kind':'needs_reframe','blocking':True})
        if item['estimated_phone_font_px'] is None:open_issues.append({'filename':item['filename'],'kind':'font_estimate_unavailable','blocking':False})
    write_json(out/'流程核验.json',{'status':'TECHNICAL_CHECKS_PASS_VISUAL_REVIEW_PENDING' if images else 'TECHNICAL_CHECKS_PASS_NO_BODY_IMAGES',
        'technical_status':'SOURCE_AND_BROWSER_CHECK_PASS','ready_for_user_review':not images,'open_issues':open_issues,'source_sha256':sha(source),
        'original_sha256':sha(draft),'plan_sha256':sha(plan_path),'preview':str(preview),'preview_sha256':sha(preview),
        'source_blocks':len(expected),'images':images,'mobile_review':mobile,'template':args.template,
        'caption_external_links':0,'source_urls_preserved_in_manifest':True,'six_template_checks':render['themes'],
        'asset_operation_this_run':'reuse-prepared-assets; this pipeline does not recapture sources',
        'timings':timings,'tool_elapsed_seconds':round(time.monotonic()-started,3),
        'timing_scope':'本入口执行耗时；不含之前采集、构思与人工审看',
        'visual_review':'pending','user_acceptance':'pending','wechat_phone_tested':False,'publication':'none'})
    write_json(out/'交付状态.json',summarize(out))
    return preview


# Catch failures outside every stage too, without touching a pre-existing run.
def run(args):
    out=args.output_dir.resolve()
    if out.exists():raise FileExistsError('Output directory already exists: '+str(out))
    try:return _run_pipeline(args)
    except Exception as exc:
        if out.exists():
            timings_path=out/'阶段耗时.json'
            timings=json.loads(timings_path.read_text()).get('timings',[]) if timings_path.exists() else []
            stage=timings[-1]['stage'] if timings else 'initialization'
            done=[t['stage'] for t in timings if t['state']=='completed']
            # Same field names as pinshu-write's stage log, so one reader understands both.
            failure={'status':'FAILED','stage':stage,'failed_stage':stage,'last_successful_stage':done[-1] if done else None,
                     'error':str(exc),'error_code':type(exc).__name__,'ready_for_user_review':False,
                     'input_paths':[str(args.draft.resolve()),str(args.plan.resolve())],
                     'existing_outputs':sorted(p.name for p in out.iterdir()),
                     'resume_from':'fix the cause above, then run the same command into a NEW output folder; prepared assets are reused, nothing is re-captured',
                     'partial_outputs':True,'publication':'none','timings':timings}
            write_json(out/'流程核验.json',failure);write_json(out/'交付状态.json',failure)
        raise


if __name__=='__main__':
    from portable import ensure_utf8_mode
    ensure_utf8_mode()
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--draft',type=Path,required=True);p.add_argument('--plan',type=Path,required=True)
    p.add_argument('--output-dir',type=Path,required=True);p.add_argument('--space-id',type=int)
    p.add_argument('--page',default='p1');p.add_argument('--template',choices=['approved','warm','green','orange','blue','classic','split'],default='approved')
    p.add_argument('--writer-skill',type=Path,default=SKILLS/'pinshu-write')
    p.add_argument('--layout-skill',type=Path,default=SKILLS/'pinshu-wechat-layout')
    p.add_argument('--prepare-only',action='store_true',help='Explicit fallback: output seven-template workbench; browser/visual checks remain pending')
    args=p.parse_args()
    if not args.prepare_only and args.space_id is None:p.error('Use the current ego TaskSpace --space-id; do not create extra spaces')
    print(run(args))
