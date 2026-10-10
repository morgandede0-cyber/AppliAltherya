import {assetSlice} from './assets';

/** One viewport contract for every illustrated menu, including embedded Discord windows. */
export function fitMenu(panel:HTMLElement,ratio=1.5,limit=1180,bottom=false){
 const hud=document.getElementById('hud'),top=Math.max(12,(hud?.getBoundingClientRect().bottom??36)+12),height=Math.max(100,innerHeight-top-18),width=Math.min(innerWidth-24,height*ratio,limit);
 panel.style.setProperty('--menu-width',width+'px');panel.style.setProperty('--menu-top',(bottom?Math.max(top,innerHeight-width/ratio-18):top)+'px');panel.classList.add('polished-menu');
}
export function watchMenuSize(panel:HTMLElement,onBreakpoint?:()=>void){
 let mobile=innerWidth<600;
 const resize=()=>{const next=innerWidth<600;if(next!==mobile){mobile=next;onBreakpoint?.();}if(panel.classList.contains('polished-menu'))fitMenu(panel,Number(panel.dataset.menuRatio)||1.5,Number(panel.dataset.menuLimit)||1180,panel.dataset.menuBottom==='true');};
 addEventListener('resize',resize);const viewport=window.visualViewport;viewport?.addEventListener('resize',resize);return()=>{removeEventListener('resize',resize);viewport?.removeEventListener('resize',resize);};
}
export function sizeMenu(panel:HTMLElement,ratio=1.5,limit=1180,bottom=false){panel.dataset.menuRatio=String(ratio);panel.dataset.menuLimit=String(limit);panel.dataset.menuBottom=String(bottom);fitMenu(panel,ratio,limit,bottom);}

/** Sample blank material inside the approved artwork instead of drawing opaque UI blocks. */
export function materialField(node:HTMLElement,kind:string,tone:'wood'|'blue'|'paper'='blue'){
 node.classList.add('material-field','material-'+tone);const src=tone==='paper'&&['guard','robber'].includes(kind)?'/assets/menus/'+kind+'.webp':tone==='paper'?'/assets/menus/jobs.webp':tone==='wood'?'/assets/menus/bank.webp':'/assets/menus/bank.webp';
 const crop=tone==='paper'&&kind==='guard'?[925,505,380,8]:tone==='paper'&&kind==='robber'?[960,609,305,7]:tone==='paper'?[465,345,150,5]:tone==='wood'?[355,365,108,6]:[250,561,145,5];
 const texture=assetSlice(src,...crop as [number,number,number,number]);texture.setAttribute('preserveAspectRatio','none');texture.classList.add('field-texture');node.prepend(texture);node.dataset.fieldKind=kind;return node;
}
export function fieldText(node:HTMLElement,value:string){const texture=node.querySelector('.field-texture');node.replaceChildren();if(texture)node.append(texture);node.append(document.createTextNode(value));}

export function merchantFrame(){
 const frame=assetSlice('/assets/catalog/merchant-design.webp',85,355,675,230);const clip=frame.querySelector('clipPath');if(clip){const path=document.createElementNS('http://www.w3.org/2000/svg','path');path.setAttribute('d','M0 0H675V230H0Z M36 51H100V25H300V51H639V198H300V228H100V198H36Z');path.setAttribute('clip-rule','evenodd');path.setAttribute('fill-rule','evenodd');clip.replaceChildren(path);}frame.classList.add('merchant-ornament');return frame;
}
