// Single shared typography foundation; write inline so HTML export retains it.
const ReadingBase=Object.freeze({
 version:'1.10.0',font:'Optima-Regular,PingFangTC-light,"PingFang TC","PingFang SC",-apple-system,BlinkMacSystemFont,"Microsoft YaHei",sans-serif',classicFont:'Optima-Regular,"PingFang TC",sans-serif',classicTracking:0.5,
 body:16,line:2.15,letterSpacing:0.4,paragraphGap:42,bodyColor:'#111111',outerGutter:20,innerGutter:16,heading:22,headingLine:1.45,source:12.5,sourceLine:1.7,sourceFont:'Georgia,"Songti SC","STSong",serif',sourceColor:'#8c8c86',caption:12,chapterNumber:30,chapterNumberLine:1.15,chapterNumberGap:9,
 apply(root,{showSources=true}={}){
  if(!showSources){
   const marker=[...root.querySelectorAll('h3,h4,p')].find(e=>/^(资料来源|参考文章|参考资料)$/.test(e.textContent.trim()));
   if(marker){
    const previous=marker.previousElementSibling;
    const boundary=previous&&(previous.tagName==='HR'||previous.matches('[data-decoration]')&&!previous.textContent.trim())?previous:marker;
    const cut=root.ownerDocument.createRange();cut.setStartBefore(boundary);cut.setEndAfter(root.lastChild);cut.deleteContents();
   }
  }
  // Account identity belongs in platform metadata, never an extra body banner.
  for(const e of root.querySelectorAll('.brand,[data-brand],[data-role="brand"],[data-decoration]')){if(e.closest('[data-picture],[data-hero],figure'))continue;if(e.matches('.brand,[data-brand],[data-role="brand"]')||e.textContent.trim()==='品叔')e.remove();}
  const font=this.font,classicLayout=!!root.querySelector('[data-chapter-style="classic"]');
  const type=(e,size,line,weight=400,align='justify',tracking=0)=>{
   Object.assign(e.style,{fontFamily:font,fontSize:size+'px',lineHeight:String(line),fontWeight:String(weight),letterSpacing:tracking+'px',wordSpacing:'0px',textIndent:'0px',textAlign:align,textAlignLast:'left',textJustify:'inter-ideograph',overflowWrap:'break-word'});
   for(const c of e.querySelectorAll('span,strong,b,a,em,i,code')){
    if(c.closest('[data-decoration]')||c.dataset.subtitle!==undefined)continue;
    Object.assign(c.style,{fontFamily:'inherit',fontSize:'inherit',lineHeight:'inherit',letterSpacing:'inherit',wordSpacing:'0px',fontWeight:c.matches('strong,b')?'600':'inherit'});
   }
  };
  // One chapter-number contract: readable size, above a full-width title.
  const chapterTitles=[...root.querySelectorAll('[data-chapter-title],h2')].filter(e=>e.textContent.trim()!=='资料来源');
  chapterTitles.forEach((heading,i)=>{
   let group=heading.closest('[data-chapter]');
   const table=heading.closest('table');
   if(!group&&table?.parentElement.tagName==='SECTION'&&table.parentElement.children.length===1){group=table.parentElement;group.dataset.chapter='true';}
   if(!group){
    group=root.ownerDocument.createElement('section');group.dataset.chapter='true';
    if(table){table.replaceWith(group);}else{heading.before(group);}
   }
   const oldNumber=group.querySelector('[data-chapter-number],[data-decoration]')||table?.querySelector('[data-decoration]');
   const accent=oldNumber?.style.color||heading.style.color||'inherit';
   const title=heading.cloneNode(true);
   for(const e of title.querySelectorAll('[data-decoration]'))e.remove();
   while(title.firstChild?.nodeType===3&&!title.firstChild.textContent.trim())title.firstChild.remove();
   Object.assign(title.style,{display:'block',width:'100%',maxWidth:'100%',margin:'0',float:'none',position:'static'});
   title.dataset.chapterTitle='true';
   const style=group.dataset.chapterStyle;
   const imageNumber=style==='classic'&&i<6;
   const number=root.ownerDocument.createElement(imageNumber?'img':'p');
   number.dataset.decoration='true';number.dataset.chapterNumber='true';number.dataset.readingRole='chapter-number';
   if(imageNumber){
    const label=String(i+1).padStart(2,'0');
    number.src='章号/'+label+'.png';number.alt='第'+label+'章';
    Object.assign(number.style,{display:'block',width:'100%',height:'auto',margin:'0 0 3px',padding:'0',border:'0',background:'none'});
   }else{
    number.textContent=String(i+1).padStart(2,'0');
    type(number,this.chapterNumber,this.chapterNumberLine,600,'left');
    Object.assign(number.style,{color:accent,fontStyle:'normal',display:'block',margin:'0 0 '+this.chapterNumberGap+'px',padding:'0',border:'0',background:'none',width:'auto'});
   }
   Object.assign(group.style,{display:'block',width:'100%',marginTop:'42px',marginBottom:'24px',textAlign:'left'});
   group.replaceChildren(number,title);
   if(style==='double-rule')Object.assign(title.style,{padding:'11px 2px 12px',borderTop:'1px solid #90a99a',borderBottom:'1px solid #90a99a',background:'none'});
   if(style==='approved')Object.assign(group.style,{borderTop:'1px solid #b7c0ad',paddingTop:'12px'});
   if(style==='warm'||style==='orange'){ // Aidan 2026-10-15: a line floating above the number separated nothing and the 2px orange one glared; use the double-rule structure of 松绿双线 with lines paler than the text.
    const rule=style==='warm'?'#d9c9b4':'#eccdb9';
    Object.assign(number.style,{fontSize:'28px',fontWeight:'400',margin:'0 0 8px'});
    Object.assign(title.style,{padding:'11px 2px 12px',borderTop:'1px solid '+rule,borderBottom:'1px solid '+rule,background:'none'});
   }

   if(style==='split'){ // WeChat-safe single H2 (columns 22/78, Aidan 2026-10-15: 25% left a visible gap before the rule). Inline blocks survive WeChat cleaning; no flex/table/grid/positioned cells for a replaced video to enter.
    const numberSpan=root.ownerDocument.createElement('span'),titleText=root.ownerDocument.createElement('span');
    numberSpan.textContent=number.textContent;numberSpan.dataset.decoration='true';numberSpan.dataset.chapterNumber='true';numberSpan.dataset.readingRole='chapter-number';
    Object.assign(numberSpan.style,{display:'inline-block',boxSizing:'border-box',width:'22%',margin:'0',padding:'0 12px 0 0',border:'0',borderRight:'1px solid #dfe1e4',background:'none',fontFamily:font,fontSize:'42px',fontWeight:'300',lineHeight:'1.18',letterSpacing:'-2px',color:'#8a8f98',verticalAlign:'middle',whiteSpace:'nowrap',wordBreak:'keep-all',overflowWrap:'normal',textAlign:'left'});
    while(title.firstChild)titleText.append(title.firstChild);titleText.dataset.chapterTitle='true';Object.assign(titleText.style,{display:'inline-block',boxSizing:'border-box',width:'78%',margin:'0',padding:'0 0 0 16px',verticalAlign:'middle'});
    delete title.dataset.chapterTitle;Object.assign(title.style,{display:'block',boxSizing:'border-box',width:'100%',margin:'0',padding:'0',fontSize:'20px',lineHeight:'1.45',whiteSpace:'normal'});
    title.append(numberSpan,titleText);group.replaceChildren(title);group.style.marginTop='48px';
   }
   if(style==='blue'){ // Aidan 2026-10-15: no tinted block (heavy, and a light fill turns grey in WeChat dark mode); one thin blue line between number and title, like the line-divided templates.
    Object.assign(number.style,{color:'#7895aa',margin:'0 0 10px',padding:'0 0 8px',borderBottom:'1px solid #7895aa'});Object.assign(title.style,{padding:'2px 0 0'});
   }
   if(style==='classic')Object.assign(group.style,{background:'none',border:'0',padding:'0',marginBottom:'45px'});
   if(style==='classic')title.style.color='#111111';
  });
  if(root.id==='review-body')root.style.padding='0 '+(this.outerGutter+this.innerGutter)+'px 20px';
  for(const paper of root.querySelectorAll('[data-paper]'))paper.style.padding='0';
  type(root,this.body,this.line,400,'justify',this.letterSpacing);
  let source=false;
  for(const e of root.querySelectorAll('p,li,blockquote,h2,h3,h4,[data-chapter-title]')){
   if(e.dataset&&e.dataset.videoSlot!==undefined){Object.assign(e.style,{fontSize:'0',lineHeight:'0',marginTop:'0',marginBottom:this.paragraphGap+'px'});continue;}
   if(/^(资料来源|参考文章|参考资料)$/.test(e.textContent.trim()))source=true;
   if(e.closest('[data-decoration]')){if(e.closest('[data-picture],[data-hero],figure')){type(e,this.caption,1.5,400,'center');e.style.textAlignLast='center';e.dataset.readingRole='caption';}continue;}
   if(e.matches('[data-chapter-title],h2,h3,h4')){
    const classic=!!e.closest('[data-chapter-style="classic"]');
    const split=!!e.closest('[data-chapter-style="split"]');type(e,classic?21:split?20:this.heading,classic?34.4/21:split?1.45:this.headingLine,classic?400:700,'left',classic?1:0);
    if(classic){e.style.lineHeight='34.4px';for(const c of e.querySelectorAll('strong,b')){c.style.fontWeight='400';c.style.lineHeight='inherit';}}
    e.dataset.readingRole='heading';continue;
   }
   if(e.closest('[data-chapter]')||e.querySelector('img'))continue;
   if(e.closest('[data-picture],[data-hero],figure')){
    type(e,this.caption,1.5,400,'center');e.style.textAlignLast='center';e.dataset.readingRole='caption';continue;
   }
   const size=source?this.source:this.body,line=source?this.sourceLine:this.line;
   const emphasis=e.dataset.role==='judgment'||Number(e.style.fontWeight)>=600;
   type(e,size,line,emphasis?600:400,source?'left':'justify',source?0:this.letterSpacing);e.dataset.readingRole=source?'source':'body';
   // Keep the light face, while preserving the shared justified body baseline.
   if(classicLayout&&!source){
    Object.assign(e.style,{fontFamily:this.classicFont,fontWeight:emphasis?'600':'300',letterSpacing:this.classicTracking+'px',textAlign:'justify'});
    for(const c of e.querySelectorAll('span,strong,b,a,em,i,code')){
     if(c.closest('[data-decoration]'))continue;
     Object.assign(c.style,{fontFamily:'inherit',letterSpacing:'inherit',fontWeight:c.matches('strong,b')?'600':'inherit'});
    }
   }
   if(!source&&!emphasis&&!e.closest('blockquote'))e.style.color=this.bodyColor;
   // References read as a quiet appendix: a different face, grey, smaller, italic.
   if(source)Object.assign(e.style,{fontFamily:this.sourceFont,fontStyle:'italic',color:this.sourceColor,fontWeight:'400',textAlign:'left',textAlignLast:'left'});
   e.style.marginTop='0';e.style.marginBottom=(source||e.tagName==='LI'?8:this.paragraphGap)+'px';
  }
  root.dataset.readingBase=this.version;return root;
 }
});
