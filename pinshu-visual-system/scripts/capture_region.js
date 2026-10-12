// Closure-free browser function, injected only for one capture operation.
function inspectCapture(job) {
  const matches=[...document.querySelectorAll(job.selector)].filter(e=>!job.start||e.textContent.includes(job.start));
  if(matches.length!==1)throw Error('Quoted region must match exactly one element');
  const root=matches[0];let selected=root,nodes=[],text='';
  const walker=document.createTreeWalker(root,NodeFilter.SHOW_TEXT);let node;
  while((node=walker.nextNode())){nodes.push({node,start:text.length});text+=node.data;}
  let first=0,end=text.length;
  if(job.start){
    first=text.indexOf(job.start);const last=job.end?text.indexOf(job.end,first+job.start.length):-1;
    if(first<0||text.indexOf(job.start,first+1)>=0||job.end&&last<0)throw Error('Quote boundaries missing or ambiguous');
    end=job.end?last+job.end.length:text.length;
    const point=(offset,isEnd=false)=>{const n=isEnd?nodes.find(n=>offset<=n.start+n.node.data.length):[...nodes].reverse().find(n=>n.start<=offset);return[n.node,offset-n.start];};
    selected=document.createRange();selected.setStart(...point(first));selected.setEnd(...point(end,true));
  }
  const r=selected.getBoundingClientRect();
  if(r.width<30||r.height<10||r.left<0||r.right>innerWidth+1)throw Error('Region is empty or horizontally clipped');
  const visible=e=>{const s=getComputedStyle(e),b=e.getBoundingClientRect();return s.display!=='none'&&s.visibility!=='hidden'&&parseFloat(s.opacity)!==0&&b.width>0&&b.height>0;};
  const intersects=e=>{const b=e.getBoundingClientRect();return visible(e)&&b.right>r.left&&b.left<r.right&&b.bottom>r.top&&b.top<r.bottom;};
  const geometryIntersects=e=>{const b=e.getBoundingClientRect();return b.width>0&&b.height>0&&b.right>r.left&&b.left<r.right&&b.bottom>r.top&&b.top<r.bottom;};
  const media=[];
  // X uses transparent <img> sizing proxies over visible CSS backgrounds.
  // Opacity zero must not make their source pixels disappear from the audit.
  for(const im of document.querySelectorAll('img'))if(geometryIntersects(im)){
    const b=im.getBoundingClientRect(),overlap=Math.min(b.right,r.right)-Math.max(b.left,r.left);
    // Small avatars/icons are recorded, but do not govern content-image quality.
    const critical=im===root||b.width>=96&&b.height>=48;
    media.push({kind:'img',url:im.currentSrc||im.src,loaded:im.complete&&im.naturalWidth>0,
      natural_width:im.naturalWidth,natural_height:im.naturalHeight,display_width_css:b.width,
      projected_delivery_width:1080*overlap/r.width,critical});
  }
  const candidates=[root,...root.querySelectorAll('*')];let parent=root.parentElement;
  for(let i=0;parent&&i<4;i++,parent=parent.parentElement)candidates.push(parent);
  for(const e of candidates)if(intersects(e)){
    const background=getComputedStyle(e).backgroundImage;
    for(const match of background.matchAll(/url\(["']?([^"')]+)["']?\)/g)){
      const url=match[1],bitmap=window.__pinshuCapturePosters?.[url],b=e.getBoundingClientRect();
      const proxy=[...document.images].find(im=>(im.currentSrc||im.src)===url&&im.complete&&im.naturalWidth>0);
      const nativeWidth=bitmap?.naturalWidth||proxy?.naturalWidth||0;
      media.push({kind:'background',url,loaded:!!nativeWidth,natural_width:nativeWidth,
        display_width_css:b.width,projected_delivery_width:1080*(Math.min(b.right,r.right)-Math.max(b.left,r.left))/r.width,
        critical:b.width>=96&&b.height>=48||root.tagName==='IMG'});
    }
  }
  for(const video of document.querySelectorAll('video'))if(intersects(video)){
    const b=video.getBoundingClientRect(),poster=window.__pinshuCapturePosters?.[video.poster];
    const frame=video.readyState>=2&&video.videoWidth>0;
    const posterReady=!!(poster?.complete&&poster.naturalWidth>0);
    media.push({kind:'video',url:video.currentSrc||'',poster:video.poster,loaded:frame||posterReady,
      ready_state:video.readyState,frame_ready:frame,poster_ready:posterReady,
      natural_width:frame?video.videoWidth:poster?.naturalWidth||0,
      projected_delivery_width:1080*(Math.min(b.right,r.right)-Math.max(b.left,r.left))/r.width,
      display_width_css:b.width,critical:true});
  }
  const busy=[...document.querySelectorAll('[role="progressbar"],[aria-busy="true"]')].filter(intersects)
    .map(e=>({role:e.getAttribute('role'),aria_busy:e.getAttribute('aria-busy')}));
  // A site's error panel may have replaced the observed video entirely.
  // Expectations refer to the selected region, not the rest of the post.
  const expected_media=job.expect_media||{};
  const loaded_media_counts={video:media.filter(m=>m.kind==='video'&&m.loaded).length,
    image:new Set(media.filter(m=>['img','background'].includes(m.kind)&&m.critical&&m.loaded).map(m=>m.url)).size};
  const missing_media=Object.entries(expected_media).filter(([kind,count])=>loaded_media_counts[kind]<count)
    .map(([kind,count])=>({kind,expected:count,loaded:loaded_media_counts[kind]}));
  const fonts=nodes.filter(n=>n.start<end&&n.start+n.node.data.length>first&&n.node.data.trim())
    .map(n=>parseFloat(getComputedStyle(n.node.parentElement).fontSize)).filter(Number.isFinite);
  return {x:r.left+scrollX,y:r.top+scrollY,width:r.width,height:r.height,viewport:innerWidth,
    text:job.start?selected.toString():root.innerText||'',min_source_font_px:fonts.length?Math.min(...fonts):null,
    media,busy,expected_media,loaded_media_counts,missing_media,
    ready:busy.length===0&&missing_media.length===0&&media.every(m=>m.loaded),
    low_resolution_media:media.filter(m=>m.loaded&&m.critical&&m.projected_delivery_width>m.natural_width*1.05)};
}
