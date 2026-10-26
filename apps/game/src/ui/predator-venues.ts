import type {Snapshot} from '../activity';
import {predatorButton,predatorFrame} from './predator-art';
type Kind='market'|'tavern'|'games';
type Host={state:()=>Snapshot;route:(key:string)=>void;close:()=>void};
export function openPredatorVenue(panel:HTMLElement,kind:Kind,host:Host){
 const title=kind==='market'?'Le marchand':kind==='tavern'?'La taverne':'Les jeux de la taverne';
 panel.hidden=false;panel.className='predator-venue predator-'+kind;panel.dataset.kind=kind;panel.setAttribute('role','dialog');panel.setAttribute('aria-modal','true');panel.setAttribute('aria-label',title);panel.setAttribute('aria-busy','false');panel.replaceChildren();document.body.classList.add('illustrated-open');
 const canvas=document.createElement('section');canvas.className='predator-canvas';const img=new Image();img.alt=title;img.src='/assets/predator-venues/'+(kind==='market'?'merchant-home':kind==='games'?'tavern-games':'tavern-home')+'.png';canvas.append(img);panel.append(canvas);
 const nav=document.createElement('nav');nav.className='predator-choices';nav.setAttribute('aria-label',title);canvas.append(nav);
 const route=(key:string)=>host.route(key);
 const entries: [string,string,number,number,number,number][]=kind==='market'?[['Histoire','market:story',21.5,74.4,18.5,10],['Acheter','market:buy',41,74.4,18.5,10],['Vendre','market:sell',60.5,74.4,18.5,10],['Partir','hub',41.8,87.3,16.2,8],['Comptoir des joueurs','trade',61,87.3,28,8]]:kind==='tavern'?[['Le tavernier','barman',16.5,63.4,14.7,11],['Le troubadour','troubadour',46.4,23,13.5,7.5],['Les jeux','games',75,64,15,11],['Retour au hub','hub',41.8,87.6,16.5,8]]:[['Lancer de dés','dice',14,76,24,10],['Pile ou face','coin',39,76,23,10],['Pierre feuille ciseaux','rps',63,76,25,10],['Retour à la taverne','tavern',38,89,24,8]];
 for(const [label,key,x,y,w,h] of entries){const b=predatorButton(label,()=>route(key),kind!=='market',key==='hub'||key==='tavern');b.style.left=x+'%';b.style.top=y+'%';b.style.width=w+'%';b.style.height=h+'%';b.style.setProperty('--venue-x',x+'%');b.style.setProperty('--venue-y',y+'%');b.style.setProperty('--venue-w',w+'%');b.style.setProperty('--venue-h',h+'%');if(kind==='tavern')b.classList.add('predator-embedded');nav.append(b);}
 if(kind!=='tavern'){const h=document.createElement('h2');h.className='predator-venue-title';h.append(predatorFrame(kind==='games','title'));const span=document.createElement('span');span.textContent=title;h.append(span);canvas.append(h);}
 panel.onkeydown=e=>{if(e.key==='Escape'){e.preventDefault();e.stopPropagation();route(kind==='games'?'tavern':'hub');}if(e.key==='Tab'){const buttons=Array.from(panel.querySelectorAll<HTMLButtonElement>('button')),first=buttons[0],last=buttons.at(-1);if(e.shiftKey&&document.activeElement===first){e.preventDefault();last?.focus();}else if(!e.shiftKey&&document.activeElement===last){e.preventDefault();first?.focus();}}};
 requestAnimationFrame(()=>panel.querySelector<HTMLButtonElement>('button')?.focus({preventScroll:true}));
 return{update(){},destroy(){panel.onkeydown=null;document.body.classList.remove('illustrated-open');}};
}
