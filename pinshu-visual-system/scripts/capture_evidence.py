#!/usr/bin/env python3
"""Capture an observed source region in an existing ego TaskSpace, without a baked frame."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import tempfile
import time
import os
import shutil
from PIL import Image, ImageStat

HERE = Path(__file__).resolve().parent
EGO = os.environ.get('PINSHU_EGO_BROWSER') or shutil.which('ego-browser') or os.path.expanduser('~/.local/bin/ego-browser')


def browser(job):
    code = 'const JOB = ' + json.dumps(job, ensure_ascii=False) + ';\n' + (HERE/'capture_region.js').read_text() + '\n' + (HERE/'article_browser.mjs').read_text()
    subprocess.run([EGO, 'nodejs'], input=code, text=True, check=True, timeout=90)


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def parse_media_expectations(values):
    expectations={}
    for value in values:
        kind,separator,number=value.partition(':')
        if kind not in {'video','image'} or not separator or not number.isdecimal() or int(number)<1:
            raise ValueError('--expect-media requires video:N or image:N, with N >= 1')
        if kind in expectations:raise ValueError('Declare each media kind once')
        expectations[kind]=int(number)
    return expectations


def save_capture(raw, receipt, out):
    """Keep original pixels; downsample only. An empty frame is not evidence."""
    if receipt.get('ready') is False or receipt.get('busy') or receipt.get('missing_media'):
        raise ValueError('Source media not ready; no successful screenshot')
    if receipt.get('low_resolution_media') and receipt.get('purpose')!='quote':
        raise ValueError('Embedded raster source is too small; higher screenshot scale cannot restore detail')
    with Image.open(raw) as image:
        image.load()
        if image.width < 1080:
            raise ValueError('Capture narrower than 1080; recapture, never upscale')
        gray = image.convert('L')
        ink = gray.point(lambda p: 255 if p < 225 else 0)
        if ImageStat.Stat(ink).mean[0] / 255 < .005:
            raise ValueError('Near-blank capture; inspect source and crop again')
        original_size = list(image.size)
        delivery = image.convert('RGB').resize((1080, round(image.height*1080/image.width)), Image.Resampling.LANCZOS)
    out.mkdir(parents=True, exist_ok=True)
    (out/'原始截图.png').write_bytes(raw.read_bytes());delivery.save(out/'截图.png')
    receipt.update(raw_size=original_size, delivery_size=list(delivery.size),
        original_sha256=sha(out/'原始截图.png'), delivery_sha256=sha(out/'截图.png'),
        mobile_review={'state':'pending','reason':'高清不等于手机字大；需查看模板内375px截图'}, frame_baked=False)
    (out/'截图回执.json').write_text(json.dumps(receipt,ensure_ascii=False,indent=2)+'\n')
    return out/'截图.png'


def save_native_image(raw, receipt, out, crop=None):
    """Crop native source pixels, never resample them upward to claim 1080px."""
    with Image.open(raw) as image:
        image.load();native_size=list(image.size)
        box=tuple(crop) if crop else (0,0,image.width,image.height)
        x,y,w,h=box if crop else (0,0,image.width,image.height)
        if min(x,y)<0 or min(w,h)<=0 or x+w>image.width or y+h>image.height:
            raise ValueError('Native crop falls outside the source pixels')
        delivered=image.crop((x,y,x+w,y+h)).convert('RGB')
        delivered.thumbnail((1080,100000),Image.Resampling.LANCZOS)
        suffix={'JPEG':'.jpg','PNG':'.png','WEBP':'.webp'}.get(image.format)
        if not suffix:raise ValueError('Native source must be JPEG, PNG or WebP')
    out.mkdir(parents=True,exist_ok=True)
    original=out/('来源原图'+suffix);original.write_bytes(raw.read_bytes());delivered.save(out/'截图.png')
    receipt.update(native_size=native_size,crop_native_pixels={'x':x,'y':y,'width':w,'height':h},
        original_file=str(original),original_sha256=sha(original),delivery_size=list(delivered.size),
        delivery_sha256=sha(out/'截图.png'),frame_baked=False,
        resolution_rule='原始栅格只裁切/缩小；原像素不足1080则按实际宽度交付，不伪称1080高清',
        mobile_review={'state':'pending','reason':'原图细节、上下文及手机可读性仍需实际看图'})
    (out/'截图回执.json').write_text(json.dumps(receipt,ensure_ascii=False,indent=2)+'\n')
    return out/'截图.png'


MAX_ATTEMPTS = 3


def failure_ledger(out):
    return out.parent/'截图失败记录.json'


def failures_for(out, url):
    path=failure_ledger(out)
    data=json.loads(path.read_text()) if path.exists() else {}
    return data, data.get(url, [])


def record_failure(out, url, args, error):
    data,items=failures_for(out,url)
    items.append({'time':time.strftime('%Y-%m-%d %H:%M:%S'),'output_dir':str(out),'error':str(error)[:500],
        'selector':args.selector,'clip':args.clip,'start':args.start,'end':args.end,'purpose':args.purpose})
    data[url]=items
    failure_ledger(out).write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n')
    return len(items)


def write_manual_guide(out, url, args, items):
    """After repeated failures a person takes over this one capture; everything else carries on."""
    slug=out.name
    target=out.parent/'人工截图'/(slug+'.png')
    if args.describe:
        region=args.describe
    elif args.start:
        region='从原话「'+args.start+'」开始'+('，到「'+args.end+'」结束' if args.end else '，截到这一段末尾')
    elif args.clip:
        region='页面宽度 %spx 时，坐标 x=%s y=%s 宽 %s 高 %s 的那一块（参考最后一次失败时页面）'%(args.viewport,*args.clip)
    else:
        region='选择器 '+(args.selector or '')+' 对应的那一块'
    lines=['# 人工截图指引：'+slug,'',
        '自动截图对这个网址已经失败 %d 次，停止自动重试。其余配图和排版照常往下做，这一张等人工补。'%len(items),'',
        '1. 打开网址：'+url,
        '2. 要截哪一块：'+region+'。'+('这张用来证明原话和数字，文字和浏览量清楚即可。' if args.purpose=='quote' else '这张用来展示画面，画面要清楚。'),
        *(['3a. 先翻译：这是外文页面，给中文读者看要截中文版。在页面上点右键选“翻译成中文”（X 帖子点帖子下方的“翻译帖子”），等译文出来再截；图注写“原文为外文，截图为机器翻译”，另截一张外文原图留底。'] if args.translate_to else []),
        '3. 怎么截：浏览器窗口拉窄到手机宽度（约 390px），关掉或滚开浮在页面上的按钮栏、登录提示，用 CleanShot X 或系统截图（Shift+Command+4）框选这一块；不要加边框，不要把小图放大。',
        '4. 存到哪：'+str(target),
        '5. 文件名：'+target.name+'（PNG）',
        '6. 截完告诉 Agent。Agent 打开看图、核原话，再登记进配图任务并回写物料包进度。','',
        '## 自动截图失败记录','']
    lines+=['- %s：%s'%(i['time'],i['error'].splitlines()[0][:200]) for i in items]
    target.parent.mkdir(parents=True,exist_ok=True)
    guide=out.parent/('人工截图指引_'+slug+'.md')
    guide.write_text('\n'.join(lines)+'\n')
    data,_=failures_for(out,url);data.setdefault('_guides',{})[url]=str(guide)
    failure_ledger(out).write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n')
    return guide


def reject_capture(out, url, args, reason):
    """The script said success but the image failed a look (cover, cut-off, blank, wrong post). That counts as a
    failed attempt toward the same limit; the rejected files move aside and are kept, never deleted."""
    if not reason.strip():raise ValueError('--reject needs a reason: what was wrong when you opened the image')
    files=[f for f in out.glob('*') if f.is_file() and (f.name in {'截图.png','原始截图.png','截图回执.json'} or f.name.startswith('来源原图'))]
    if not (out/'截图.png').is_file():raise ValueError('No successful capture to reject in '+str(out))
    stamp=time.strftime('%Y%m%d-%H%M%S');aside=out/('看过不合格_'+stamp);n=1
    while aside.exists():n+=1;aside=out/('看过不合格_%s_%d'%(stamp,n))
    aside.mkdir()
    for f in files:f.rename(aside/f.name)
    count=record_failure(out,url,args,'opened and rejected: '+reason.strip())
    if count>=MAX_ATTEMPTS:
        _,items=failures_for(out,url)
        guide=write_manual_guide(out,url,args,items)
        raise SystemExit('STOP_MANUAL: 第 %d 次失败（含看过不合格），停止自动截图。人工截图指引：%s'%(count,guide))
    return count,aside


def translated_url(url, target):
    """Google Translate proxy page, e.g. note.com -> note-com.translate.goog. Some sites block it; that counts as a failure."""
    from urllib.parse import urlsplit, urlunsplit
    u=urlsplit(url);host=u.hostname.replace('-','--').replace('.','-')+'.translate.goog'
    query=(u.query+'&' if u.query else '')+'_x_tr_sl=auto&_x_tr_tl=%s&_x_tr_hl=%s'%(target,target)
    return urlunsplit((u.scheme,host,u.path,query,''))


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--space-id',type=int,help='existing ego TaskSpace (not needed with --reject)');p.add_argument('--page',default='p1')
    p.add_argument('--reject',metavar='REASON',help='after opening the image: it failed the look (cover, cut-off, blank, wrong post); counts as a failed attempt')
    p.add_argument('--url',required=True);p.add_argument('--selector',help='CSS selector of the observed evidence. Whole card (e.g. an X post with author and views): selector alone. One passage only: add --start/--end')
    p.add_argument('--clip',nargs=4,type=float,metavar=('X','Y','WIDTH','HEIGHT'),help='Capture a page region by CSS-pixel coordinates instead of a selector')
    p.add_argument('--purpose',choices=['visual','quote'],default='visual',help='quote = proves words/numbers, low-res embedded video is recorded not rejected')
    p.add_argument('--translate-to',help='e.g. zh-CN: capture the machine-translated page for Chinese readers; caption must say it is a machine translation')
    p.add_argument('--describe',help='Plain-language region for a human, e.g. 主帖整张卡片，从头像到浏览量那一行; used in the manual guide')
    p.add_argument('--allow-more-attempts',action='store_true',help='Only when the user asks to keep trying after %d failures'%MAX_ATTEMPTS)
    p.add_argument('--start',default='',help='exact text where the capture BEGINS (it also picks the one matching element); anything above it, such as an avatar or author name, is cut off. With --clip: only waited for')
    p.add_argument('--end',default='',help='exact text where the capture ends (needs --start)')
    p.add_argument('--hide',action='append',default=[]);p.add_argument('--viewport',type=int,default=390)
    p.add_argument('--output-dir',type=Path,required=True)
    p.add_argument('--media-timeout-ms',type=int,default=15000)
    p.add_argument('--expect-media',action='append',default=[],help='Observed media in selected region: video:N / image:N; images count distinct content URLs')
    p.add_argument('--native-image',action='store_true',help='Extract the observed native raster instead of photographing enlarged browser pixels')
    p.add_argument('--image-source-url',help='An observed same-asset original URL, e.g. X CDN name=orig')
    p.add_argument('--native-crop',nargs=4,type=int,metavar=('X','Y','WIDTH','HEIGHT'))
    args=p.parse_args()
    if args.reject is not None:
        count,aside=reject_capture(args.output_dir.resolve(),args.url,args,args.reject)
        print('已记为第 %d 次失败（满 %d 次转人工），不合格的图移到：%s。用同一条命令重截。'%(count,MAX_ATTEMPTS,aside));return
    if args.space_id is None:p.error('--space-id is required (open an ego TaskSpace first)')
    expected_media=parse_media_expectations(args.expect_media)
    if bool(args.selector)==bool(args.clip):raise ValueError('Give exactly one of --selector or --clip')
    if args.clip and (args.native_image or args.hide or args.end or expected_media):raise ValueError('--clip only works with --start (wait text) and --purpose')
    if not 320<=args.viewport<=500:raise ValueError('Capture a mobile-width region, 320–500px')
    if args.end and not args.start:raise ValueError('--end requires --start')
    if args.native_crop and not args.native_image:raise ValueError('Native crop requires --native-image')
    if args.native_image and (args.start or args.end or args.hide):raise ValueError('Native image extraction is separate from page text/overlay capture')
    if args.native_image and expected_media:raise ValueError('--expect-media applies to page-region capture, not native-image extraction')
    if not 100<=args.media_timeout_ms<=30000:raise ValueError('Media wait must be bounded, 100–30000ms')
    out=args.output_dir.resolve()
    if out.exists():
        # Rerunning the same command after a failure is the natural retry; only a successful capture is protected.
        if any(out.glob('截图.png')) or any(out.glob('截图回执.json')):raise FileExistsError('已有成功截图，不覆盖：%s'%out)
        for i,old in enumerate(sorted(out.glob('采集失败.json')),1):
            old.rename(out/('采集失败_%s.json'%time.strftime('%H%M%S')))
    page_url=translated_url(args.url,args.translate_to) if args.translate_to else args.url
    _,previous=failures_for(out,args.url)
    if len(previous)>=MAX_ATTEMPTS and not args.allow_more_attempts:
        data,_=failures_for(out,args.url)
        guide=data.get('_guides',{}).get(args.url) or write_manual_guide(out,args.url,args,previous)
        raise SystemExit('STOP_MANUAL: 这个网址已自动失败 %d 次，不再重试。人工截图指引：%s'%(len(previous),guide))
    # ego writes to /tmp first; copy into the article folder after pixel validation.
    with tempfile.TemporaryDirectory(prefix='pinshu-capture-') as tmp:
        raw=Path(tmp)/'raw.png';record=Path(tmp)/'receipt.json'
        try:
            browser(dict(action='native-image' if args.native_image else 'capture',space_id=args.space_id,page=args.page,
                navigate=True,selector=args.selector,url=page_url,clip=args.clip,purpose=args.purpose,start=args.start,end=args.end,hide=args.hide,
                image_source_url=args.image_source_url,
                viewport=args.viewport,media_timeout_ms=args.media_timeout_ms,expect_media=expected_media,temp_png=str(raw),result=str(record)))
            receipt=json.loads(record.read_text())
            receipt.update(original_url=args.url,machine_translated_to=args.translate_to,
                caption_note='原文为外文，截图为浏览器机器翻译' if args.translate_to else None)
            image=(save_native_image(raw,receipt,out,args.native_crop) if args.native_image
                  else save_capture(raw,receipt,out))
            print(image)
            print('下一步：打开这张图看一遍（有没有遮挡、截断、空白、原话是否完整），没问题才算截完。')
        except Exception as exc:
            args.output_dir.mkdir(parents=True,exist_ok=True)
            failure=json.loads(record.read_text()) if record.exists() else {'status':'FAILED','error':str(exc)}
            failure['status']='FAILED';failure['successful_image']=None
            (args.output_dir/'采集失败.json').write_text(json.dumps(failure,ensure_ascii=False,indent=2)+'\n')
            count=record_failure(out,args.url,args,failure.get('error') or exc)
            if count>=MAX_ATTEMPTS:
                _,items=failures_for(out,args.url)
                guide=write_manual_guide(out,args.url,args,items)
                raise SystemExit('STOP_MANUAL: 第 %d 次失败，停止自动截图。人工截图指引：%s\n失败原因：%s'%(count,guide,failure.get('error') or exc))
            print('截图失败（这个网址第 %d 次，满 %d 次会自动转人工）：%s'%(count,MAX_ATTEMPTS,failure.get('error') or exc))
            raise


if __name__=='__main__':
    from portable import ensure_utf8_mode
    ensure_utf8_mode()
    main()
