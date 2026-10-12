import {assetSlice} from './assets';
let ornamentSequence=0;
/** Reuses the approved ornamental button artwork with a live label. */
export function decorateButton(button:HTMLButtonElement,label:string){
 const ns='http://www.w3.org/2000/svg',svg=document.createElementNS(ns,'svg');
 svg.setAttribute('viewBox','40 388 655 175');svg.setAttribute('aria-hidden','true');
 const defs=document.createElementNS(ns,'defs'),gradient=document.createElementNS(ns,'linearGradient');
 const gradientId='compact-button-blue-'+(++ornamentSequence);gradient.id=gradientId;gradient.setAttribute('x2','0');gradient.setAttribute('y2','1');
 for(const [offset,color] of [['0','#073f7a'],['.5','#062955'],['1','#031d41']]){const stop=document.createElementNS(ns,'stop');stop.setAttribute('offset',offset);stop.setAttribute('stop-color',color);gradient.append(stop);}defs.append(gradient);const clip=document.createElementNS(ns,'clipPath'),clipId='compact-clip-'+(++ornamentSequence),bounds=document.createElementNS(ns,'rect');clip.id=clipId;bounds.setAttribute('x','40');bounds.setAttribute('y','388');bounds.setAttribute('width','655');bounds.setAttribute('height','175');clip.append(bounds);defs.append(clip);svg.append(defs);
 const image=document.createElementNS(ns,'image');image.setAttribute('href','/assets/menus/tavern.webp');image.setAttribute('width','1984');image.setAttribute('height','793');image.setAttribute('clip-path',`url(#${clipId})`);svg.append(image);
 const mask=document.createElementNS(ns,'rect');mask.setAttribute('x','166');mask.setAttribute('y','436');mask.setAttribute('width','424');mask.setAttribute('height','79');mask.setAttribute('rx','2');mask.setAttribute('fill',`url(#${gradientId})`);svg.append(mask);
 const text=document.createElement('span');text.textContent=label;button.replaceChildren(svg,text);button.classList.add('compact-button');button.setAttribute('aria-label',label);button.title=label;return button;
}
export function themedHeader(file:string){const n=assetSlice('/assets/catalog/'+file+'.webp',250,0,1040,240);n.classList.add('themed-header');return n;}

/** Align labels to the blue interior after the SVG's meet/letterbox scaling. */
export function alignCompactButtons(root:HTMLElement){
 for(const b of Array.from(root.querySelectorAll<HTMLElement>('.compact-button'))){
  const svg=b.querySelector<SVGSVGElement>(':scope > svg'),label=b.querySelector<HTMLElement>(':scope > span');if(!svg||!label||!b.clientWidth||!b.clientHeight)continue;
  const view=svg.viewBox.baseVal,scale=Math.min(b.clientWidth/view.width,b.clientHeight/view.height),ox=(b.clientWidth-view.width*scale)/2,oy=(b.clientHeight-view.height*scale)/2;
  const width=424*scale,height=79*scale;
  Object.assign(label.style,{position:'absolute',left:ox+(166-view.x)*scale+'px',top:oy+(436-view.y)*scale+'px',width:width+'px',height:height+'px',display:'flex',alignItems:'center',justifyContent:'center',padding:'0',margin:'0',lineHeight:'1.05',whiteSpace:'normal',textAlign:'center'});
  let font=Math.min(parseFloat(getComputedStyle(b).fontSize),height*.7);label.style.fontSize=font+'px';
  while(font>9&&(label.scrollWidth>width+1||label.scrollHeight>height+1)){font-=.5;label.style.fontSize=font+'px';}
 }
}
