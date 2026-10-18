const ns='http://www.w3.org/2000/svg';
export function nineSliceFrame(src:string,[x,y,w,h]:[number,number,number,number]){
 const svg=document.createElementNS(ns,'svg');svg.classList.add('predator-frame');svg.dataset.nineSlice='';svg.setAttribute('aria-hidden','true');svg.setAttribute('focusable','false');svg.setAttribute('preserveAspectRatio','none');const edge=80;
 for(let row=0;row<3;row++)for(let col=0;col<3;col++){
  const part=document.createElementNS(ns,'svg'),im=document.createElementNS(ns,'image');
  const sx=x+(col===0?0:col===1?edge:w-edge),sy=y+(row===0?0:row===1?edge:h-edge),sw=col===1?w-2*edge:edge,sh=row===1?h-2*edge:edge;
  part.setAttribute('viewBox',`${sx} ${sy} ${sw} ${sh}`);part.setAttribute('preserveAspectRatio','none');part.setAttribute('overflow','hidden');part.style.overflow='hidden';
  im.setAttribute('href',src);im.setAttribute('width','1536');im.setAttribute('height','1024');part.append(im);svg.append(part);
 }
 layout(svg,300,200);return svg;
}
function layout(svg:SVGSVGElement,w:number,h:number){const edge=Math.min(12,w/4,h/4);svg.setAttribute('viewBox',`0 0 ${w} ${h}`);Array.from(svg.children).forEach((part,i)=>{const row=Math.floor(i/3),col=i%3;part.setAttribute('x',String(col===0?0:col===1?edge:w-edge));part.setAttribute('y',String(row===0?0:row===1?edge:h-edge));part.setAttribute('width',String(col===1?w-2*edge:edge));part.setAttribute('height',String(row===1?h-2*edge:edge));});}
export function fitNineSlices(panel:HTMLElement){for(const svg of Array.from(panel.querySelectorAll<SVGSVGElement>('svg[data-nine-slice]'))){const r=svg.getBoundingClientRect();if(r.width>0&&r.height>0)layout(svg,r.width,r.height);}}
