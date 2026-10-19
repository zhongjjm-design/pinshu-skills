// Run only through ego-browser nodejs, prefixed with const JOB = {...};
const fs = await import('node:fs/promises');
const task = await taskSpace(JOB.space_id);
const page = task.page(JOB.page || 'p1');
const settle = async () => page.evaluate(async () => {
  await document.fonts.ready;
  await Promise.all([...document.images].filter(i=>!i.loading||i.loading!=='lazy').map(i=>i.decode().catch(()=>{})));
  await new Promise(r=>requestAnimationFrame(()=>requestAnimationFrame(r)));
});
const metrics = async (width, dpr=1) => page.cdp('Emulation.setDeviceMetricsOverride', {
  width, height:1000, deviceScaleFactor:dpr, mobile:true, screenWidth:width, screenHeight:1000
});
let diagnosis=null;
try {
// Always reload: a page reused after scrolling may have virtualized the target away (X, 10-12).
const freshOpen = async () => {
  if (await page.url()===JOB.url) await page.reload(); else await page.goto(JOB.url);
  await page.evaluate(()=>scrollTo(0,0));
};
// Hide every visible fixed/sticky layer except the evidence and its ancestors; restored in finally.
const hideFloating = async keepSelector => page.evaluate(keep=>{
  const kept=keep?[...document.querySelectorAll(keep)]:[];window.__pinshuAutoHidden=[];
  // Browser extensions (e.g. YouMind, 10-12) inject widgets beside <body> or inside shadow roots.
  for(const e of document.documentElement.children){
    if(['HEAD','BODY','SCRIPT','STYLE'].includes(e.tagName)||getComputedStyle(e).display==='none')continue;
    // display:none — extension children may force visibility:visible over an inherited hidden.
    window.__pinshuAutoHidden.push({e,style:e.getAttribute('style')});e.style.setProperty('display','none','important');
  }
  const all=[];const walk=root=>{for(const e of root.querySelectorAll('*')){all.push(e);if(e.shadowRoot)walk(e.shadowRoot);}};
  walk(document.body);
  for(const e of all){
    const s=getComputedStyle(e);if(!['fixed','sticky'].includes(s.position)||s.display==='none')continue;
    // Zero-size fixed shells still paint overflowing children (Monica toolbar, 10-12), so size is not a filter.
    if(kept.some(k=>e.contains(k)||k.contains(e)))continue;
    window.__pinshuAutoHidden.push({e,style:e.getAttribute('style')});
    // fixed is out of flow: display:none is safe and beats children that force visibility; sticky keeps its space.
    if(s.position==='fixed')e.style.setProperty('display','none','important');else e.style.setProperty('visibility','hidden','important');
  }
  return window.__pinshuAutoHidden.map(({e})=>e.tagName.toLowerCase()+(e.id?'#'+e.id:'')+(e.getAttribute('data-testid')?'[data-testid='+e.getAttribute('data-testid')+']':''));
},keepSelector||'');
// ego draws a visible agent cursor on the page surface; park it outside the captured region.
const parkCursor = async (docTop, docBottom) => {
  const v=await page.evaluate(()=>({h:innerHeight,sy:scrollY}));
  const top=docTop-v.sy,bottom=docBottom-v.sy;
  const y=top>40?2:(bottom<v.h-40?v.h-2:null);
  if(y===null)throw Error('Region fills the whole viewport; cannot park the agent cursor outside it — capture a smaller region');
  await page.mouse.move(2,y);
};
if (JOB.action === 'capture' && JOB.clip) {
  await metrics(JOB.viewport || 390);
  if (JOB.navigate) await freshOpen();
  if (JOB.start) await page.waitForFunction(t=>document.body.innerText.includes(t),JOB.start,{timeout:20000});
  await settle();
  const [x,y,width,height]=JOB.clip;
  await page.evaluate(top=>scrollTo(0,Math.max(0,top-100)),y);await settle();
  const autoHidden=await hideFloating('');
  await parkCursor(y,y+height);
  const scale=Math.max(2,Math.ceil(1200/width));
  if(scale>8)throw Error('Region too narrow; choose a better mobile crop');
  const result=await page.cdp('Page.captureScreenshot',{format:'png',fromSurface:true,captureBeyondViewport:true,clip:{x,y,width,height,scale}});
  await fs.writeFile(JOB.temp_png,Buffer.from(result.data,'base64'));
  await fs.writeFile(JOB.result,JSON.stringify({x,y,width,height,viewport:JOB.viewport||390,scale,capture_method:'clip',
    source_url:await page.url(),captured_at:new Date().toISOString(),acquisition:'new-capture',frame_baked:false,
    purpose:JOB.purpose,auto_hidden_overlays:autoHidden,
    media_checks:'not run in clip mode; open the image and check media yourself'},null,2));
} else if (JOB.action === 'capture') {
  await metrics(JOB.viewport || 390);
  if (JOB.navigate) await freshOpen();
  await page.waitForFunction(({selector,start})=>[...document.querySelectorAll(selector)].some(e=>e.textContent.includes(start)),
    {selector:JOB.selector,start:JOB.start||''},{timeout:20000});
  if(JOB.image_source_url)await page.evaluate(({selector,url})=>{
    const items=document.querySelectorAll(selector);if(items.length!==1||items[0].tagName!=='IMG')throw Error('Source override requires exactly one image');
    const image=items[0],original=new URL(image.currentSrc||image.src),next=new URL(url);
    if(!['http:','https:'].includes(next.protocol)||original.origin!==next.origin||original.pathname!==next.pathname)
      throw Error('Original image URL must refer to the same observed source asset');
    window.__pinshuSourceRestore={image,src:image.getAttribute('src'),srcset:image.getAttribute('srcset')};
    image.removeAttribute('srcset');image.src=url;
  },{selector:JOB.selector,url:JOB.image_source_url});
  await settle();
  // Selectors and quote boundaries must come from the Agent's observed page.
  await page.evaluate(job=>{
    const roots=[...document.querySelectorAll(job.selector)].filter(e=>!job.start||e.textContent.includes(job.start));
    if(roots.length!==1)throw Error('Quoted region must match exactly one element');
    roots[0].scrollIntoView({block:'center'});
  },JOB);
  await settle();
  await page.evaluate('window.__pinshuInspectCapture = '+inspectCapture.toString()+'; null');
  const initial=await page.evaluate(inspectCapture,JOB);diagnosis=initial;
  await page.evaluate(urls=>{
    window.__pinshuCapturePosters={};
    for(const url of urls.filter(Boolean)){const image=new Image();image.src=url;window.__pinshuCapturePosters[url]=image;}
  },initial.media.filter(m=>m.kind==='video'||m.kind==='background').map(m=>m.kind==='video'?m.poster:m.url));
  try {
    await page.waitForFunction(job=>window.__pinshuInspectCapture(job).ready,JOB,{timeout:JOB.media_timeout_ms||15000});
  } catch(error) {
    diagnosis=await page.evaluate(inspectCapture,JOB);
    throw Error((diagnosis.missing_media.length?'EXPECTED_MEDIA_MISSING: ':'MEDIA_NOT_READY: ')+JSON.stringify({busy:diagnosis.busy,media:diagnosis.media,missing_media:diagnosis.missing_media}));
  }
  await settle();
  const region=await page.evaluate(inspectCapture,JOB);diagnosis=region;
  if(!region.ready)throw Error('MEDIA_NOT_READY after layout settled');
  // Quote/number evidence proves words, not picture quality; only visual-purpose captures gate on media resolution.
  if(region.low_resolution_media.length&&JOB.purpose!=='quote')throw Error('LOW_RESOLUTION_MEDIA (use --purpose quote if this capture only proves words/numbers): '+JSON.stringify(region.low_resolution_media));
  const hidden=await page.evaluate(({selectors,quoteSelector})=>{
    const result=[],targets=[];
    const quoted=[...document.querySelectorAll(quoteSelector)];
    for(const selector of selectors) {
      const matches=[...document.querySelectorAll(selector)];
      if(matches.length!==1)throw Error('Overlay selector must match exactly one element');
      const e=matches[0];
      if(!['fixed','sticky'].includes(getComputedStyle(e).position))throw Error('Only observed sticky overlays can be hidden');
      if(quoted.some(q=>e.contains(q)||q.contains(e)))throw Error('Cannot hide evidence or its ancestor');
      targets.push({e,selector,style:e.getAttribute('style')});
    }
    for(const target of targets){result.push({selector:target.selector,style:target.style});target.e.style.visibility='hidden';}
    return result;
  },{selectors:JOB.hide || [],quoteSelector:JOB.selector});
  const autoHidden=await hideFloating(JOB.selector);
  let result;
  try {
    // A little margin so text does not touch the image edge; stays inside the page width.
    const vw=await page.evaluate(()=>innerWidth),pad=10;
    const x=Math.max(0,region.x-pad),y=Math.max(0,region.y-pad);
    const width=Math.min(vw,region.x+region.width+pad)-x,height=region.height+(region.y-y)+pad;
    await parkCursor(y,y+height);
    const scale=Math.max(2,Math.ceil(1200/width));
    if(scale>8)throw Error('Region too narrow; choose a better mobile crop');
    result=await page.cdp('Page.captureScreenshot',{format:'png',fromSurface:true,captureBeyondViewport:true,clip:{x,y,width,height,scale}});
    await fs.writeFile(JOB.temp_png,Buffer.from(result.data,'base64'));
    const receipt={...region,scale,source_url:await page.url(),captured_at:new Date().toISOString(),
      acquisition:'new-capture',frame_baked:false,hidden_overlays:hidden.map(x=>x.selector),auto_hidden_overlays:autoHidden,
      purpose:JOB.purpose,low_resolution_media_accepted_for_quote:JOB.purpose==='quote'?region.low_resolution_media:[],
      font_estimate_scope:'DOM text only; embedded images and actual phone appearance require visual review'};
    await fs.writeFile(JOB.result,JSON.stringify(receipt,null,2));
  } finally {
    await page.evaluate(items=>{for(const item of [...items].reverse()){
      for(const e of document.querySelectorAll(item.selector)){
        if(item.style===null)e.removeAttribute('style');else e.setAttribute('style',item.style);
      }
    }},hidden);
  }
} else if (JOB.action === 'native-image') {
  await freshOpen();
  // Transparent X sizing proxies exist in the DOM but are never "visible".
  await page.waitForFunction(selector=>document.querySelectorAll(selector).length===1,JOB.selector,{timeout:15000});
  await page.evaluate(selector=>{
    const items=document.querySelectorAll(selector);if(items.length!==1||items[0].tagName!=='IMG')throw Error('Select exactly one observed source image');
    items[0].scrollIntoView({block:'center'});
  },JOB.selector);
  await page.waitForFunction(selector=>{
    const items=document.querySelectorAll(selector);return items.length===1&&items[0].tagName==='IMG'&&items[0].complete&&items[0].naturalWidth>0;
  },JOB.selector,{timeout:15000});
  const source=await page.evaluate(selector=>{
    const im=document.querySelector(selector);return {url:im.currentSrc||im.src,displayed_natural_width:im.naturalWidth};
  },JOB.selector);
  const url=JOB.image_source_url||source.url;
  const old=new URL(source.url),selected=new URL(url);
  if(!['http:','https:'].includes(selected.protocol)||old.origin!==selected.origin||old.pathname!==selected.pathname)
    throw Error('Original image URL must refer to the same observed source asset');
  const response=await page.fetch(url,{saveAs:JOB.temp_png});
  if(!response.ok)throw Error('Native image request failed: '+response.status);
  await fs.writeFile(JOB.result,JSON.stringify({source_url:await page.url(),native_image_url:url,
    observed_image_url:source.url,displayed_natural_width:source.displayed_natural_width,
    captured_at:new Date().toISOString(),acquisition:'new-capture',capture_method:'native-source-image',frame_baked:false},null,2));
} else if (JOB.action === 'render') {
  await page.goto(JOB.url);await page.waitForSelector('#article-body [data-reading-role]');await settle();
  const result=await page.evaluate(()=>({html:document.querySelector('#paper').outerHTML,
    title:document.querySelector('#preview-title').textContent,
    readingBlocks:[...document.querySelectorAll('#article-body [data-reading-role]')].filter(e=>!e.closest('[data-decoration]')).map(e=>e.textContent),
    themes:themes.map(t=>{const host=document.createElement('div');host.innerHTML=render(C.articles[ai],t,options());
      return {id:t.id,caption_links:host.querySelectorAll('[data-picture] [data-decoration] a').length,
        pictures:host.querySelectorAll('[data-picture]').length};})}));
  await fs.writeFile(JOB.result,JSON.stringify(result,null,2));
} else if (JOB.action === 'check') {
  const views=[],screens=[];
  for(const width of [320,375,414]){
    await metrics(width);await page.goto(JOB.url);await page.waitForSelector('#article-body');await settle();
    views.push(await page.evaluate(()=>({width:innerWidth,overflow:document.documentElement.scrollWidth>innerWidth,
      caption_links:document.querySelectorAll('[data-picture] [data-decoration] a').length,
      pictures:document.querySelectorAll('[data-picture]').length})));
  }
  await metrics(375,3);await page.reload();await settle();
  // Body figures only: the lead image (cover, data-hero) is seen in top.png and is not a body figure.
  const BODY='[data-picture]:not([data-hero])';
  const count=await page.evaluate(sel=>document.querySelectorAll(sel).length,BODY);
  for(let i=-1;i<count;i++){
    const data=await page.evaluate(async ({i,sel})=>{
      const figures=[...document.querySelectorAll(sel)],fig=i<0?null:figures[i];
      if(fig){fig.scrollIntoView({block:'start'});await fig.querySelector('img').decode();}else scrollTo(0,0);
      await new Promise(r=>requestAnimationFrame(()=>requestAnimationFrame(r)));
      if(!fig)return{position:'top'};
      const im=fig.querySelector('img'),r=im.getBoundingClientRect();
      return {position:i+1,image_width_css:r.width,image_height_css:r.height,loaded:im.complete&&im.naturalWidth>0};
    },{i,sel:BODY});
    const files=[],parts=i<0?1:Math.max(1,Math.ceil(data.image_height_css/900));
    for(let part=0;part<parts;part++){
      if(part)await page.evaluate(({index,part,sel})=>{
        const fig=document.querySelectorAll(sel)[index];
        const top=fig.getBoundingClientRect().top+scrollY;scrollTo(0,top+part*900);
      },{index:i,part,sel:BODY});
      await page.evaluate(()=>new Promise(r=>requestAnimationFrame(()=>requestAnimationFrame(r))));
      const filename=i<0?'top.png':String(i+1).padStart(2,'0')+(part?'-part'+(part+1):'')+'.png';
      const raw=await page.cdp('Page.captureScreenshot',{format:'png',fromSurface:true,captureBeyondViewport:false});
      await fs.writeFile(JOB.screen_dir+'/'+filename,Buffer.from(raw.data,'base64'));files.push(filename);
    }
    screens.push({...data,file:files[0],files,parts,device_scale_factor:3});
  }
  await fs.writeFile(JOB.result,JSON.stringify({views,screens,visual_review:'pending',wechat_phone_tested:false},null,2));
} else throw Error('Unknown browser action');
} catch(error) {
  await fs.writeFile(JOB.result,JSON.stringify({status:'FAILED',action:JOB.action,error:String(error),diagnosis},null,2));
  throw error;
} finally {
  if(['capture','check'].includes(JOB.action)) {
    await page.evaluate(()=>{
      for(const item of (window.__pinshuAutoHidden||[]).reverse()){if(item.style===null)item.e.removeAttribute('style');else item.e.setAttribute('style',item.style);}
      delete window.__pinshuAutoHidden;
      const item=window.__pinshuSourceRestore;
      if(item){for(const key of ['src','srcset']){if(item[key]===null)item.image.removeAttribute(key);else item.image.setAttribute(key,item[key]);}}
      delete window.__pinshuSourceRestore;delete window.__pinshuInspectCapture;delete window.__pinshuCapturePosters;
    });
    await page.cdp('Emulation.clearDeviceMetricsOverride',{});
  }
}
console.log(JSON.stringify({space_id:task.spaceId,page:page.label,result:JOB.result}));
