// Seven Pinshu review layouts. Typography and chapter normalization use ReadingBase.
const F={sans:ReadingBase.font,serif:'"Songti SC","STSong","SimSun",Georgia,serif'};
const themes=[
 {id:'green',name:'松绿双线',scene:'',desc:'松绿章号上置，章节标题夹在两道细线之间；正文图与青灰手记同样用圆角细框，配色为松绿。',origin:'',accent:'#294c40',heading:'#294c40',caption:'#6f8075',figure:'green'},
 {id:'approved',name:'青灰手记',scene:'',desc:'青灰章号与全宽章题；正文图用圆角细框和图注。',origin:'',accent:'#747d5c',heading:'#343b2e',caption:'#7c8272',figure:'approved'},
 {id:'warm',name:'暖纸杂志',scene:'',desc:'棕色章题、暖色细线图片框和舒展的留白。',origin:'',accent:'#9b7955',heading:'#6f4c32',caption:'#86776a',figure:'warm'},
 {id:'orange',name:'橙线手记',scene:'',desc:'橙色章号与章节线，正文图用浅暖色细线框。',origin:'',accent:'#c55d2d',heading:'#533d32',caption:'#916f60',figure:'orange'},
 {id:'blue',name:'蓝白专题',scene:'',desc:'章号与章题之间一条蓝色细线，统一的浅蓝图片边框。',origin:'',accent:'#213b50',heading:'#213b50',caption:'#73899b',figure:'blue'},
 {id:'classic',name:'首席品牌官经典版',scene:'',desc:'图片章号、黑白正文、轻字重章题与浅蓝细框图片。',origin:'',accent:'#111111',heading:'#111111',caption:'#777777',figure:'classic'},
 {id:'split',name:'数字分栏',scene:'',desc:'数字在左、灰色浅竖线分隔、章题在右；章题可带一行小字副题（需作者指定拆分）。',origin:'',accent:'#6b7280',heading:'#111111',caption:'#6b7280',figure:'neutral'},
];
// Underline for author-chosen key sentences: thin and bright, never the dark body colour.
const HIGHLIGHT={approved:'#E9A23B',warm:'#E58A3A',green:'#E9A23B',orange:'#F0B429',blue:'#F0B429',classic:'#E9A23B'};
const SOURCE_MARK=/^(资料来源|参考文章|参考资料)$/;
const esc=s=>String(s??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
function el(tag,style,html=''){const e=document.createElement(tag);e.style.cssText=style;e.innerHTML=html;return e;}
function deco(tag,style,html=''){const e=el(tag,style,html);e.dataset.decoration='true';return e;}
function textStyle(t,size=15){return `font-family:${F.sans};font-size:${size}px;line-height:1.95;font-weight:400;color:#484d43;letter-spacing:0;word-spacing:0;text-align:left;text-indent:0;overflow-wrap:break-word;`;}
function sourceOf(a){return a.sourceHTML.replace(/@@IMG_(\d+)@@/g,(_,i)=>a.images[Number(i)]);}
function picture(im,t,framing=true){
 framing=framing&&im.dataset.frameBaked!=='true';
 const margin=t.figure==='classic'?'30px 0 34px':t.figure==='blue'?'22px 0 24px':t.figure==='orange'?'17px 0 21px':t.figure==='green'?'16px 0 19px':'26px 0 28px';
 const hero=im.dataset.hero==='true';
 const fig=el('section',`margin:${hero?'0 0 30px':margin};padding:0;`);fig.dataset.picture='true';if(hero)fig.dataset.hero='true';
 const styles={approved:'padding:4px;border:1px solid #bec3b4;border-radius:8px;background:none;',green:'padding:4px;border:1px solid #8fb6a1;border-radius:8px;background:none;',warm:'padding:4px;border:1px solid #ddd0bf;border-radius:8px;background:none;',orange:'padding:4px;border:1px solid #ecd8ca;border-radius:8px;background:none;',blue:'padding:4px;border:1px solid #cddde8;border-radius:8px;background:none;',classic:'padding:4px;border:1px solid #cddde8;border-radius:8px;background:none;',neutral:'padding:4px;border:1px solid #dcdee1;border-radius:8px;background:none;'};
 // Lead image and body figures share the selected template frame (Aidan 2026-10-12).
 // No tinted mat behind images: WeChat dark mode turns a light mat into a thick light-grey band (measured 10-12); line, radius and gap only.
 const surround=el('section',`margin:0;line-height:0;${framing?styles[t.figure]:'padding:0;border:0;background:none;'}`);
 const image=im.cloneNode(true);image.style.cssText='display:block;width:100%;max-width:100%;height:auto;margin:0;padding:0;border:0;'+(framing?'border-radius:8px;':'');surround.append(image);fig.append(surround);
 // Source URLs stay in the handoff/provenance. Reader captions are plain text.
 const captionText=im.hasAttribute('data-caption')?im.dataset.caption:(im.dataset.sourceLabel?'来源：'+im.dataset.sourceLabel:im.alt);
 const captionStyle=`font-family:${F.sans};font-size:12px;line-height:1.5;font-weight:400;color:${t.caption};letter-spacing:0;text-align:center;margin:8px 0 0;padding:0;`;
 if(captionText)fig.append(deco('p',captionStyle,esc(captionText)));
 return fig;
}
// Reader-safe video card. Keep it as a full-width plain paragraph plus a separate clear spacer:
// replacing a section/flex/table container in WeChat can merge the video with the next split chapter.
const VIDEO_MARKER=/^【此处(?:在后台)?插入视频：(.+)】$/;
function videoCard(label,t){
 const CD=CARD[t.figure]||CARD.approved,frag=document.createDocumentFragment();
 const card=deco('p',`display:block;clear:both;width:100%;box-sizing:border-box;margin:8px 0 0;padding:18px 20px;border:1px solid ${CD.line};border-radius:${CD.radius||8}px;background:none;font-family:${F.sans};font-size:15px;line-height:1.7;font-weight:500;color:${CD.title};letter-spacing:0;text-align:left;`,`<span style="display:inline-block;margin-right:10px;color:${CD.label};font-size:17px;">▶</span>${esc(label)}`);
 card.dataset.videoCard=label;
 const clear=deco('p','display:block;clear:both;width:100%;height:1px;min-height:1px;line-height:1px;font-size:1px;margin:0 0 30px;padding:0;overflow:hidden;','&nbsp;');
 clear.dataset.videoClear='true';frag.append(card,clear);return frag;
}
// Prompt card (Aidan 2026-10-15): a blockquote whose first line is 【title（hint）】 becomes a quiet card, part of the article rather than a highlight.
// It is the same family as the template's picture frame (same line colour and the same 8px corner in every template, Aidan 2026-10-15), with no fill, no spine and no title band:
// a dark or tinted block overpowers coloured figures on a light page, and a light fill turns into a grey band in WeChat dark mode.
// Plain text only (no code/pre) so a long press selects it in WeChat; nothing is added or reworded, the hint is the author's own parenthesis.
const FQ=F.sans.replace(/"/g,"'"); // font list holds double quotes; style="…" strings need single ones
const CARD={
 green:{line:'#8fb6a1',radius:8,title:'#5f7f70',hint:'#8a9a90',text:'#484d43',label:'#4f7f68'},
 approved:{line:'#bec3b4',radius:8,title:'#747d5c',hint:'#9aa08d',text:'#484d43',label:'#6b7a42'},
 warm:{line:'#ddd0bf',radius:8,title:'#9b7955',hint:'#a89a8c',text:'#484d43',label:'#a8743a'},
 orange:{line:'#ecd8ca',radius:8,title:'#b8704a',hint:'#b39a8d',text:'#484d43',label:'#c55d2d'},
 blue:{line:'#cddde8',radius:8,title:'#5f7d93',hint:'#93a6b5',text:'#484d43',label:'#3f6f94'},
 classic:{line:'#cddde8',radius:8,title:'#555555',hint:'#999999',text:'#333333',label:'#555555'},
 neutral:{line:'#dcdee1',radius:8,title:'#6b7280',hint:'#9aa0a6',text:'#484d43',label:'#5f6672'},
};
function promptLines(bq){
 const lines=[];
 for(const c of bq.children){
  if(c.tagName==='P'){if(lines.length&&bq.children[0]!==c&&c.previousElementSibling?.tagName==='P')lines.push('');for(const l of c.textContent.split('\n'))if(l.trim())lines.push(l.trim());}
  else if(c.tagName==='UL'){for(const li of c.children){const [head,...rest]=li.textContent.split('\n').map(x=>x.trim()).filter(Boolean);lines.push('- '+head);lines.push(...rest);}} // lines right under a list item are lazy continuations in Markdown: they are separate prompt lines
  else if(c.tagName==='OL'){let n=1;for(const li of c.children){const [head,...rest]=li.textContent.split('\n').map(x=>x.trim()).filter(Boolean);lines.push((n++)+'. '+head);lines.push(...rest);}}
  else{const x=c.textContent.trim();if(x)lines.push(x);} // never drop content silently (build.py already refuses these)
 }
 return lines;
}
function promptCard(bq,t){
 const CD=CARD[t.figure]||CARD.approved;
 const lines=promptLines(bq),first=lines.shift(),head=first.match(/^【(.+?)】(.*)$/),inner=head?head[1]:first,m=inner.match(/^(.*?)\s*[（(](.*)[）)]$/);
 const title=m?m[1]:inner,hint=m?m[2]:'';
 if(head&&head[2].trim())lines.unshift(head[2].trim()); // text after 】 on the same line stays in the body
 const base=`font-family:${FQ};font-weight:400;font-style:normal;letter-spacing:0;word-spacing:0;text-indent:0;`;
 const card=deco('section',`margin:0 0 24px;padding:0;border:1px solid ${CD.line};border-radius:${CD.radius}px;`);card.dataset.promptCard='true';
 const bar=el('section',base+`margin:0;padding:10px 14px 9px;border-bottom:1px solid ${CD.line};font-size:12.5px;line-height:1.5;color:${CD.title};text-align:left;`,esc(title)+(hint?`<span style="font-size:12px;color:${CD.hint};margin-left:10px;">${esc(hint)}</span>`:''));
 const html=lines.map(l=>{const k=l.match(/^([^：:，。；、\s]{2,6})：(.*)$/);return k?`<span style="color:${CD.label};">${esc(k[1])}：</span>${esc(k[2])}`:esc(l);}).join('<br>');
 const text=el('section','margin:0;padding:12px 14px 13px;-webkit-user-select:text;user-select:text;',`<p style="${base}margin:0;padding:0;font-size:14px;line-height:1.85;color:${CD.text};text-align:left;overflow-wrap:break-word;">${html}</p>`);
 card.append(bar,text);return card;
}
// Data table (Aidan 2026-10-15): 2 to 4 columns, fixed layout with locked column ratios so a phone never squeezes it into a vertical strip or scrolls sideways.
const TABLE_LINE={approved:'#bec3b4',green:'#8fb6a1',warm:'#d5c6b2',orange:'#e6cdbd',blue:'#b9cddb',classic:'#cfcfcf',neutral:'#d4d6da'};
const COLS={2:[30,70],3:[22,38,40],4:[16,28,28,28]};
function cellHTML(td,first){
 const text=td.textContent.trim(),range=text.match(/^(\d+[.:]\d+)\s*-\s*(\d+[.:]\d+)$/);
 if(first&&range)return `<span style="white-space:nowrap;">${esc(range[1])} -</span><br>${esc(range[2])}`;
 return esc(text).replace(/（[^（）]*）$/,x=>`<span style="color:#8a917c;">${x}</span>`);
}
function dataTable(tb,t){
 const rows=[...tb.querySelectorAll('tr')].map(r=>[...r.children]),n=rows[0].length,w=COLS[n]||rows[0].map(()=>100/n),line=TABLE_LINE[t.figure]||'#bec3b4';
 const ink=t.figure==='classic'?'#111111':'#484d43',cell=(td,i,head,first)=>{
  const tag=head?'th':'td',css=`width:${w[i]}%;box-sizing:border-box;padding:8px 5px;border:1px solid ${line};${head?`border-bottom:1px solid ${t.accent};`:''}text-align:left;vertical-align:top;font-family:${FQ};font-size:13px;line-height:${head?1.5:1.6};font-weight:400;font-style:normal;letter-spacing:0;color:${head?t.accent:ink};background:none;overflow-wrap:break-word;word-break:normal;`;
  return `<${tag} style="${css}">${head?esc(td.textContent.trim()):cellHTML(td,i===0)}</${tag}>`;
 };
 const head=tb.querySelector('thead tr')?rows.shift():null;
 const html=`<table style="width:100%;table-layout:fixed;border-collapse:collapse;border-spacing:0;margin:0;padding:0;border:1px solid ${line};"><colgroup>${w.map(x=>`<col width="${x}%">`).join('')}</colgroup>`+
  (head?`<thead><tr>${tb.querySelector('thead tr')&&[...tb.querySelector('thead tr').children].map((td,i)=>cell(td,i,true)).join('')}</tr></thead>`:'')+
  `<tbody>${rows.map(r=>`<tr>${r.map((td,i)=>cell(td,i,false)).join('')}</tr>`).join('')}</tbody></table>`;
 return deco('section','margin:0 0 24px;padding:0;',html);
}
function chapter(title,n,t,compact,layout={}){
 const s=el('section',`margin:${compact?28:36}px 0 20px;padding:0;`);s.dataset.chapter='true';s.dataset.chapterStyle=t.id==='green'?'double-rule':t.id;
 const number=deco('p',`font-family:${F.sans};font-size:28px;line-height:1.15;font-weight:500;letter-spacing:0;color:${t.accent};text-align:left;margin:0 0 8px;padding:0;`,String(n).padStart(2,'0'));number.dataset.chapterNumber='true';
 // Keep each meaningful phrase together; phrases share a line when space permits.
 const phrases=layout.headingPhrases||{};
 const h=el('h2',textStyle(t,19)+`font-weight:600;line-height:1.5;color:${t.heading};margin:0;padding:0;`);h.dataset.chapterTitle='true';
 const split=(layout.headingSplit||{})[title];
 if(t.id==='split'&&split){h.append(el('span',`font-family:${F.sans};font-size:20px;line-height:1.45;font-weight:600;color:${t.heading};letter-spacing:0;`,esc(split[0])));const sub=el('span',`display:block;margin-top:4px;font-family:${F.sans};font-size:13px;line-height:1.6;font-weight:400;color:#454a52;letter-spacing:0;`,esc(split[1]));sub.dataset.subtitle='true';h.append(sub);}
 else if(phrases[title])for(const phrase of phrases[title])h.append(el('span',`font-family:${F.sans};font-size:19px;line-height:1.5;font-weight:600;color:${t.heading};letter-spacing:0;white-space:nowrap;`,esc(phrase)));
 else h.innerHTML=title;
 s.append(number,h);return s;
}
function readingParts(e,readingBreaks=[]){
 if(e.tagName!=='P'||e.querySelector('img'))return [e];
 const text=e.textContent,entry=readingBreaks.find(([prefix])=>text.startsWith(prefix));if(!entry)return [e];
 const cuts=[0];for(const anchor of entry[1]){const i=text.indexOf(anchor,cuts[cuts.length-1]+1);if(i<0)return [e];cuts.push(i);}cuts.push(text.length);
 const walker=document.createTreeWalker(e,NodeFilter.SHOW_TEXT),nodes=[];let node,total=0;
 while((node=walker.nextNode())){nodes.push({node,start:total,end:total+node.data.length});total+=node.data.length;}
 const point=offset=>{const item=nodes.find(x=>offset<=x.end);return [item.node,offset-item.start];};
 return cuts.slice(0,-1).map((start,i)=>{const part=e.cloneNode(false),range=document.createRange();range.setStart(...point(start));range.setEnd(...point(cuts[i+1]));part.append(range.cloneContents());part.dataset.readingChunk=String(i+1);return part;});
}
function markPhrases(e,chosenPhrases=[],accent='#cc773d'){
 // Exact source phrases selected for this real article; no generated claims or rewritten sentences.
 for(const phrase of chosenPhrases){
  const walker=document.createTreeWalker(e,NodeFilter.SHOW_TEXT);let node;
  while((node=walker.nextNode())){if(node.parentElement.closest('strong,a,[data-emphasis]'))continue;const index=node.data.indexOf(phrase);if(index<0)continue;
   const before=document.createTextNode(node.data.slice(0,index)),after=document.createTextNode(node.data.slice(index+phrase.length));
   const mark=el('span',`font-family:inherit;font-size:inherit;line-height:inherit;font-weight:inherit;color:inherit;border-bottom:1px solid ${accent};padding:0 0 2px;margin:0;`,esc(phrase));mark.dataset.emphasis='true';node.replaceWith(before,mark,after);break;
  }
 }
}
function styleContent(e,t,role,source,layout={}){
 const tag=e.tagName.toLowerCase(),f=textStyle(t);
 if(tag==='hr')return deco('section','height:0;margin:28px 0 0;padding:0;');
 let st=f+'margin:0 0 24px;padding:0;';
 if(['h3','h4'].includes(tag))st=textStyle(t,17)+'font-weight:600;color:#414936;line-height:1.5;margin:24px 0 13px;padding:0;';
 if(['ul','ol'].includes(tag))st=f+'margin:0 0 18px;padding-left:21px;';
 if(tag==='li')st=f+'margin:0 0 8px;padding:0;';
 if(tag==='blockquote')st=f+'margin:25px 0;padding:0 0 0 12px;border-left:2px solid #9da48d;';
 e.style.cssText=st;
 for(const p of e.querySelectorAll('p,li'))styleContent(p,t,'normal',source,layout);
 for(const strong of e.querySelectorAll('strong,b'))strong.style.cssText='font-family:inherit;font-size:inherit;line-height:inherit;font-weight:650;color:#343b2e;';
 for(const a of e.querySelectorAll('a'))a.style.cssText='font-family:inherit;font-size:inherit;line-height:inherit;color:#69705f;text-decoration:underline;';
 if(source){e.style.cssText=textStyle(t,12)+'line-height:1.65;color:#747b69;margin:0 0 8px;'+(['ul','ol'].includes(tag)?'padding-left:18px;':'padding:0;');return e;}
 if(role==='first')e.style.cssText=f+'color:#454d3b;margin:0 0 24px;padding:0;';
 if(role==='judgment'){
  e.dataset.role='judgment';e.style.cssText=textStyle(t,16)+'font-weight:600;line-height:1.95;color:#424937;margin:27px 0;padding:0;';
 }
 if(role==='quote'){e.dataset.role='quote';e.style.cssText=f+'color:#4c5540;margin:25px 0;padding:0 0 0 12px;border-left:1px solid #bec3b4;';}
 if(role==='last'){e.style.color='#424a37';e.style.fontWeight='600';e.style.marginTop='23px';}
 if(['p','li','blockquote'].includes(tag)){e.style.textAlign='justify';e.style.textJustify='inter-ideograph';e.style.textAlignLast='left';}
 markPhrases(e,layout.emphasis||[],HIGHLIGHT[t.id]||'#E9A23B');return e;
}
function render(a,t,options={}){
 const layout=a.layout||{};const src=document.createElement('div');src.innerHTML=sourceOf(a);const out=el('section','margin:0;padding:8px;background-color:#ffffff;');out.dataset.paper='true';
 let n=0,pn=0,source=false;const nodes=[...src.children];const marker=nodes.findIndex(e=>SOURCE_MARK.test(e.textContent.trim()));const visibleNodes=layout.showSources===false&&marker>=0?nodes.slice(0,marker-(nodes[marker-1]?.tagName==='HR'?1:0)):nodes;
 for(let i=0;i<visibleNodes.length;i++){
  const e=visibleNodes[i],text=e.textContent.trim();
  // The reference block is never a chapter, whatever heading level the writer used (Aidan 2026-10-12): grey, italic, smaller than body.
  // A short accent rule ends the body before the reference block (Aidan 2026-10-12 picked this over a full-width rule or dots).
  if(SOURCE_MARK.test(text)&&!source){const rule=el('section',`margin:48px auto 28px;width:40px;height:0;padding:0;border-top:1px solid ${t.accent};`);rule.dataset.decoration='true';rule.dataset.sourceRule='true';out.append(rule);}
  if(e.tagName==='H2'&&SOURCE_MARK.test(text)){source=true;const head=document.createElement('p');head.textContent=text;out.append(styleContent(head,t,'normal',true,layout));continue;}
  if(e.tagName==='H2'){out.append(chapter(e.innerHTML,++n,t,options.compact,layout));continue;}
  if(SOURCE_MARK.test(text))source=true;
  const videoMarker=text.match(VIDEO_MARKER);
  if(e.tagName==='P'&&videoMarker&&!source){out.append(videoCard(videoMarker[1].trim(),t));continue;}
  if(e.tagName==='P'&&e.hasAttribute('data-video-slot')){out.append(videoCard((e.getAttribute('data-video-slot')||'视频').trim(),t));continue;}
  if(e.tagName==='IMG'||(e.tagName==='P'&&e.querySelector('img')&&!text)){for(const im of e.tagName==='IMG'?[e]:e.querySelectorAll('img'))out.append(picture(im,t,options.framing!==false));continue;}
  if(e.tagName==='TABLE'){out.append(dataTable(e,t));continue;}
  if(e.tagName==='BLOCKQUOTE'&&/^【.+】/.test(text)&&!source){out.append(promptCard(e,t));continue;}
  let role='normal';if(e.tagName==='P'&&!e.querySelector('img')){if(pn++===0)role='first';if((a.judgment||[]).some(k=>text.startsWith(k)))role='judgment';if((a.quote||[]).some(k=>text.startsWith(k)))role='quote';if(nodes[i+1]?.tagName==='HR')role='last';}
  for(const [j,part] of (source?[e]:readingParts(e,layout.readingBreaks||[])).entries())out.append(styleContent(part,t,role==='first'&&j>0?'normal':role,source,layout));
 }
 ReadingBase.apply(out);out.style.padding='0';
 if(t.id==='classic')for(const number of out.querySelectorAll('img[data-chapter-number]')){const id=number.alt.match(/\d+/)?.[0];if(!CHAPTER_IMAGES[id])throw Error('缺少第 '+id+' 章的图像章号');number.src=CHAPTER_IMAGES[id];}
 return out.outerHTML;
}
function nightPreview(container){for(const e of container.querySelectorAll('*')){if(e.style.color&&!e.hasAttribute('data-chapter-accent'))e.style.color='#c9cec0';if(e.style.backgroundColor)e.style.backgroundColor='#292d25';for(const edge of ['Top','Right','Bottom','Left'])if(e.style['border'+edge+'Width'])e.style['border'+edge+'Color']='#828b74';}}
