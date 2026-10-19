import {assetSlice} from './assets';
import './predator-venues.css';
export function predatorFrame(tavern=false,kind:'title'|'action'|'back'|'card'='action'){
 const r: [number,number,number,number]=tavern?(kind==='title'?[24,224,490,140]:kind==='back'?[1045,235,470,130]:kind==='card'?[20,520,505,390]:[542,235,474,130]):(kind==='title'?[22,88,536,174]:kind==='back'?[1090,114,430,148]:kind==='card'?[40,338,502,595]:[572,115,506,146]);
 const svg=assetSlice('/assets/predator-venues/'+(tavern?'tavern':'merchant')+'-ui.png',...r);svg.classList.add('predator-frame');svg.setAttribute('preserveAspectRatio','none');return svg;
}
export function predatorButton(label:string,fn:()=>void,tavern=false,back=false){const b=document.createElement('button');b.type='button';b.className='predator-button';b.setAttribute('aria-label',label);b.append(predatorFrame(tavern,back?'back':'action'));const text=document.createElement('span');text.textContent=label;b.append(text);b.onclick=()=>{if(!b.disabled)fn();};return b;}
/** Dress real controls without changing their handlers, disabled states or dynamic text. */
export function decoratePredator(root:HTMLElement,tavern=false){
 root.classList.add(tavern?'predator-drinks':'predator-commerce');
 root.querySelectorAll('.approved-heading-divider').forEach(n=>n.remove());
 for(const b of Array.from(root.querySelectorAll<HTMLButtonElement>('button'))){
  const label=b.getAttribute('aria-label')??'';const span=document.createElement('span');span.className='predator-button-content';
  const content=b.querySelector('.approved-button-content');if(content)span.append(...Array.from(content.childNodes));else{b.querySelector('.predator-frame')?.remove();span.append(...Array.from(b.childNodes));}
  b.replaceChildren(predatorFrame(tavern,/Retour|Annuler/.test(label)?'back':'action'),span);b.classList.add('predator-button');b.classList.remove('approved-button','approved-round');
 }
 for(const card of Array.from(root.querySelectorAll<HTMLElement>('.realm-product,.realm-card'))){card.querySelector('.approved-card-fill')?.remove();card.prepend(predatorFrame(tavern,'card'));card.classList.add('predator-card');}
 const header=root.querySelector('.realm-header');if(header)header.prepend(predatorFrame(tavern,'title'));
}
