import {assetSlice} from './assets';

/** One viewport contract for every illustrated menu, including embedded Discord windows. */
export function fitMenu(panel:HTMLElement,ratio=1.5,limit=1180,bottom=false){
 panel.classList.add('polished-menu');
 if(panel.hasAttribute('data-modal-open'))return;
 const viewport=window.visualViewport;
 const screenWidth=viewport?.width??innerWidth,screenHeight=viewport?.height??innerHeight;
 const hud=document.getElementById('hud'),safeTop=Math.max(12,(hud?.getBoundingClientRect().bottom??36)+12);
 const available=Math.max(120,screenHeight-safeTop-16),mobile=innerWidth<=600;
 const width=mobile?Math.min(screenWidth-16,limit):Math.min(screenWidth-32,limit,ratio>0?Math.max(Math.min(680,screenWidth-32),(available-56)*ratio):limit);
 const artHeight=ratio>0?width/ratio:panel.scrollHeight;
 const extras=ratio>0?Array.from(panel.children).filter(n=>n instanceof HTMLElement&&!n.matches('.art-stage,.game-table,.menu-content')).reduce((sum,n)=>sum+(n as HTMLElement).getBoundingClientRect().height,0):0;
 const contentHeight=Math.min(available,Math.max(artHeight+extras,120));
 const top=mobile?safeTop:bottom?Math.max(safeTop,screenHeight-contentHeight-16):safeTop+Math.max(0,(available-contentHeight)/2);
 panel.style.setProperty('--menu-width',width+'px');panel.style.setProperty('--menu-top',top+'px');panel.style.setProperty('--menu-height',available+'px');panel.classList.add('polished-menu');
}
export function watchMenuSize(panel:HTMLElement,onBreakpoint?:()=>void){
 let mobile=innerWidth<=600;
 const resize=()=>{const next=innerWidth<=600;if(next!==mobile){mobile=next;onBreakpoint?.();}if(panel.classList.contains('polished-menu'))fitMenu(panel,panel.dataset.menuRatio===undefined?1.5:Number(panel.dataset.menuRatio),Number(panel.dataset.menuLimit)||1180,panel.dataset.menuBottom==='true');};
 let frame=0;const schedule=()=>{cancelAnimationFrame(frame);frame=requestAnimationFrame(()=>{if(panel.isConnected&&!panel.hidden)resize();});};
 const geometry=new ResizeObserver(schedule);geometry.observe(panel);const hud=document.getElementById('hud');if(hud)geometry.observe(hud);
 const changes=new MutationObserver(schedule);changes.observe(panel,{childList:true,attributes:true,attributeFilter:['data-modal-open']});
 addEventListener('resize',resize);const viewport=window.visualViewport;viewport?.addEventListener('resize',resize);return()=>{cancelAnimationFrame(frame);geometry.disconnect();changes.disconnect();removeEventListener('resize',resize);viewport?.removeEventListener('resize',resize);};
}
export function sizeMenu(panel:HTMLElement,ratio=1.5,limit=1180,bottom=false){panel.dataset.menuRatio=String(ratio);panel.dataset.menuLimit=String(limit);panel.dataset.menuBottom=String(bottom);fitMenu(panel,ratio,limit,bottom);}

/** Material samples belong to the menu being composed; they repeat at native scale. */
let materialId=0;
const woodSamples:Record<string,[string,number,number,number,number]>={
 tools:['tools',1010,274,145,58],destinations:['tools',1010,274,145,58],accessories:['tools',1010,274,145,58],departure:['tools',1010,274,145,58],
 forge:['forge',321,644,228,36],merchant:['forge',321,644,228,36],bank:['bank',355,365,108,6],robber:['robber',404,708,90,13]
};
export function materialTexture(kind:string,tone:'wood'|'blue'|'paper'|'seal',width=400,height=160){
 const ns='http://www.w3.org/2000/svg',svg=document.createElementNS(ns,'svg'),defs=document.createElementNS(ns,'defs'),pattern=document.createElementNS(ns,'pattern'),im=document.createElementNS(ns,'image'),rect=document.createElementNS(ns,'rect');
 let sample:[string,number,number,number,number]=tone==='seal'?['jobs',...((kind==='seal:rare'?[861,263,38,8]:kind==='seal:uncommon'?[184,546,38,8]:kind==='seal:epic'||kind==='seal:legendary'?[861,546,38,8]:[184,263,38,8]) as [number,number,number,number])]:tone==='wood'?(woodSamples[kind]??woodSamples.tools):tone==='paper'?kind==='departure'?['departure',1090,500,95,18]:kind==='guard'?['guard',925,505,380,8]:kind==='robber'?['robber',960,609,305,7]:['jobs',465,345,150,5]:['podium',722,324,94,60];
 const [file,x,y,w,h]=sample,id='native-material-'+(++materialId);svg.setAttribute('viewBox',`0 0 ${width} ${height}`);svg.setAttribute('preserveAspectRatio','none');svg.setAttribute('aria-hidden','true');svg.setAttribute('focusable','false');
 pattern.id=id;pattern.setAttribute('patternUnits','userSpaceOnUse');pattern.setAttribute('width',String(w*2));pattern.setAttribute('height',String(h*2));
 const src=file.startsWith('catalog/')?'/assets/'+file+'.webp':'/assets/menus/'+file+'.webp';
 for(const transform of ['',`translate(${w*2} 0) scale(-1 1)`,`translate(0 ${h*2}) scale(1 -1)`,`translate(${w*2} ${h*2}) scale(-1 -1)`]){
  const tile=document.createElementNS(ns,'svg'),picture=document.createElementNS(ns,'image');tile.setAttribute('viewBox',`${x} ${y} ${w} ${h}`);tile.setAttribute('width',String(w));tile.setAttribute('height',String(h));tile.setAttribute('overflow','hidden');if(transform)tile.setAttribute('transform',transform);picture.setAttribute('href',src);picture.setAttribute('width','1536');picture.setAttribute('height','1024');tile.append(picture);pattern.append(tile);
 }
 defs.append(pattern);rect.setAttribute('width',String(width));rect.setAttribute('height',String(height));rect.setAttribute('fill',`url(#${id})`);svg.append(defs,rect);return svg;
}
export function materialField(node:HTMLElement,kind:string,tone:'wood'|'blue'|'paper'|'seal'='blue'){
 node.classList.add('material-field','material-'+tone);
 if(kind!=='merchant'&&!kind.startsWith('seal:')){node.classList.add('native-live-field');return node;}
 const width=parseFloat(node.style.width)*15.36||400,height=parseFloat(node.style.height)*10.24||160;
 const texture=materialTexture(kind,tone,width,height);texture.classList.add('field-texture');node.prepend(texture);node.dataset.fieldKind=kind;return node;
}

/** Keep the original frame and labels, and clear the sample tool inside its frame. */
export function toolBackdrop(){const img=new Image();img.src='/assets/menus/tools.webp';img.alt='';img.className='art-image native-tool-background';return img;}
export function fieldText(node:HTMLElement,value:string){const texture=node.querySelector('.field-texture');node.replaceChildren();if(texture)node.append(texture);node.append(document.createTextNode(value));}

export function merchantFrame(){
 const frame=assetSlice('/assets/catalog/merchant-design.webp',85,355,675,230);const clip=frame.querySelector('clipPath');if(clip){const path=document.createElementNS('http://www.w3.org/2000/svg','path');path.setAttribute('d','M0 0H675V230H0Z M46 60H638V204H46Z M115 53H298V226H115Z');path.setAttribute('clip-rule','evenodd');path.setAttribute('fill-rule','evenodd');clip.replaceChildren(path);}frame.classList.add('merchant-ornament');return frame;
}

export function merchantMedallion(){const frame=assetSlice('/assets/catalog/merchant-design.webp',85,355,675,230),clip=frame.querySelector('clipPath')!,ns='http://www.w3.org/2000/svg',path=document.createElementNS(ns,'path');path.setAttribute('d','M297 134a94 94 0 1 0-188 0a94 94 0 1 0 188 0 M283 134a80 80 0 1 0-160 0a80 80 0 1 0 160 0');path.setAttribute('clip-rule','evenodd');path.setAttribute('fill-rule','evenodd');clip.replaceChildren(path);frame.classList.add('merchant-medallion');return frame;}

export function raritySeal(rarity:string){
 const pos=rarity==='rare'?[828,242]:rarity==='uncommon'?[151,531]:['epic','legendary'].includes(rarity)?[828,531]:[151,242];
 const seal=assetSlice('/assets/menus/jobs.webp',pos[0],pos[1],110,135),clip=seal.querySelector('clipPath')!,ns='http://www.w3.org/2000/svg',cut=document.createElementNS(ns,'path');cut.setAttribute('d','M0 0H110V135H0Z M15 22H95V72H15Z');cut.setAttribute('clip-rule','evenodd');cut.setAttribute('fill-rule','evenodd');clip.replaceChildren(cut);
 const fill=materialTexture('seal:'+rarity,'seal',80,50);fill.setAttribute('x','15');fill.setAttribute('y','22');fill.setAttribute('width','80');fill.setAttribute('height','50');seal.insertBefore(fill,seal.querySelector('image'));return seal;
}
