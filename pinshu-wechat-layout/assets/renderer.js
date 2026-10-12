// Six Pinshu review layouts. Typography and chapter normalization use ReadingBase.
const F={sans:ReadingBase.font,serif:'"Songti SC","STSong","SimSun",Georgia,serif'};
const themes=[
 {id:'approved',name:'青灰手记',scene:'',desc:'青灰章号与全宽章题；正文图用圆角细框和图注。',origin:'',accent:'#747d5c',heading:'#343b2e',caption:'#7c8272',figure:'approved'},
 {id:'warm',name:'暖纸杂志',scene:'',desc:'棕色章题、暖纸色图片衬底和舒展的留白。',origin:'',accent:'#9b7955',heading:'#6f4c32',caption:'#86776a',figure:'warm'},
 {id:'green',name:'青绿刊页',scene:'',desc:'青绿章号上置，章节标题夹在两道细线之间。',origin:'',accent:'#294c40',heading:'#294c40',caption:'#6f8075',figure:'green'},
 {id:'orange',name:'橙线手记',scene:'',desc:'橙色章号与章节线，正文图保留浅暖色衬框。',origin:'',accent:'#c55d2d',heading:'#533d32',caption:'#916f60',figure:'orange'},
 {id:'blue',name:'蓝白专题',scene:'',desc:'浅蓝章题底衬、蓝色侧线与统一的浅蓝图片边框。',origin:'',accent:'#213b50',heading:'#213b50',caption:'#73899b',figure:'blue'},
 {id:'classic',name:'首席品牌官经典版',scene:'',desc:'图片章号、黑白正文、轻字重章题与浅蓝细框图片。',origin:'',accent:'#111111',heading:'#111111',caption:'#777777',figure:'classic'},
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
 const styles={approved:'padding:6px;border:1px solid #bec3b4;border-radius:8px;background:#fdfef9;',warm:'padding:8px;border:1px solid #d3c3ae;background:#f5f0e7;',green:'padding:6px;border:1px solid #a9bdb1;border-radius:4px;background:#f2f6f3;',orange:'padding:8px;border:1px solid #e4cbb9;background:#fbf5f0;',blue:'padding:6px;border:1px solid #bed2e0;background:#edf3f7;',classic:'padding:6px;border:1px solid #bed2e0;background:#edf3f7;'};
 // Lead image and body figures share the selected template frame (Aidan 2026-10-12).
 const surround=el('section',`margin:0;line-height:0;${framing?styles[t.figure]:'padding:0;border:0;background:none;'}`);
 const image=im.cloneNode(true);image.style.cssText='display:block;width:100%;max-width:100%;height:auto;margin:0;padding:0;border:0;'+(framing&&t.figure==='approved'?'border-radius:5px;':'');surround.append(image);fig.append(surround);
 // Source URLs stay in the handoff/provenance. Reader captions are plain text.
 const captionText=im.hasAttribute('data-caption')?im.dataset.caption:(im.dataset.sourceLabel?'来源：'+im.dataset.sourceLabel:im.alt);
 const captionStyle=`font-family:${F.sans};font-size:12px;line-height:1.5;font-weight:400;color:${t.caption};letter-spacing:0;text-align:center;margin:8px 0 0;padding:0;`;
 if(captionText)fig.append(deco('p',captionStyle,esc(captionText)));
 return fig;
}
function chapter(title,n,t,compact,layout={}){
 const s=el('section',`margin:${compact?28:36}px 0 20px;padding:0;`);s.dataset.chapter='true';s.dataset.chapterStyle=t.id==='green'?'double-rule':t.id;
 const number=deco('p',`font-family:${F.sans};font-size:28px;line-height:1.15;font-weight:500;letter-spacing:0;color:${t.accent};text-align:left;margin:0 0 8px;padding:0;`,String(n).padStart(2,'0'));number.dataset.chapterNumber='true';
 // Keep each meaningful phrase together; phrases share a line when space permits.
 const phrases=layout.headingPhrases||{};
 const h=el('h2',textStyle(t,19)+`font-weight:600;line-height:1.5;color:${t.heading};margin:0;padding:0;`);h.dataset.chapterTitle='true';
 if(phrases[title])for(const phrase of phrases[title])h.append(el('span',`font-family:${F.sans};font-size:19px;line-height:1.5;font-weight:600;color:${t.heading};letter-spacing:0;white-space:nowrap;`,esc(phrase)));
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
  if(e.tagName==='H2'){out.append(chapter(e.innerHTML,++n,t,options.compact,layout));continue;}
  if(SOURCE_MARK.test(text))source=true;
  if(e.tagName==='IMG'||(e.tagName==='P'&&e.querySelector('img')&&!text)){for(const im of e.tagName==='IMG'?[e]:e.querySelectorAll('img'))out.append(picture(im,t,options.framing!==false));continue;}
  let role='normal';if(e.tagName==='P'&&!e.querySelector('img')){if(pn++===0)role='first';if((a.judgment||[]).some(k=>text.startsWith(k)))role='judgment';if((a.quote||[]).some(k=>text.startsWith(k)))role='quote';if(nodes[i+1]?.tagName==='HR')role='last';}
  for(const [j,part] of (source?[e]:readingParts(e,layout.readingBreaks||[])).entries())out.append(styleContent(part,t,role==='first'&&j>0?'normal':role,source,layout));
 }
 ReadingBase.apply(out);out.style.padding='0';
 if(t.id==='classic')for(const number of out.querySelectorAll('img[data-chapter-number]')){const id=number.alt.match(/\d+/)?.[0];if(!CHAPTER_IMAGES[id])throw Error('缺少第 '+id+' 章的图像章号');number.src=CHAPTER_IMAGES[id];}
 return out.outerHTML;
}
function nightPreview(container){for(const e of container.querySelectorAll('*')){if(e.style.color&&!e.hasAttribute('data-chapter-accent'))e.style.color='#c9cec0';if(e.style.backgroundColor)e.style.backgroundColor='#292d25';for(const edge of ['Top','Right','Bottom','Left'])if(e.style['border'+edge+'Width'])e.style['border'+edge+'Color']='#828b74';}}
