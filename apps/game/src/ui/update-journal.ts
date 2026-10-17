import {updateNotes,type UpdateNote} from './update-notes';
import './update-journal.css';
const node=(tag:string,cls:string,text='')=>{const n=document.createElement(tag);n.className=cls;n.textContent=text;return n;};
export function openUpdateJournal(panel:HTMLElement,close:()=>void,notes:UpdateNote[]=updateNotes){
 const previous=document.activeElement as HTMLElement|null;let page=0;let selected:string|undefined=notes[0]?.id;const size=3;
 panel.className='update-journal';panel.dataset.kind='updates';panel.hidden=false;panel.setAttribute('aria-label','Le Journal d’Altherya');panel.setAttribute('role','dialog');panel.setAttribute('aria-modal','true');
 function draw(focus?:string){
  panel.replaceChildren();const content=node('div','uj-content');const header=node('header','uj-header');header.append(node('h2','','Le Journal d’Altherya'),node('p','','Les dernières évolutions du jeu'));content.append(header);
  const list=node('div','uj-timeline');const slice=notes.slice(page*size,(page+1)*size);
  for(const entry of slice){const row=node('article','uj-entry');const time=document.createElement('time');time.className='uj-date';time.dateTime=entry.date;const date=new Date(entry.date+'T12:00:00Z');time.append(node('strong','',String(date.getUTCDate())),node('span','',new Intl.DateTimeFormat('fr-FR',{month:'long',timeZone:'UTC'}).format(date)),node('small','',String(date.getUTCFullYear())));row.append(time);
   const card=node('div','uj-card');const toggle=document.createElement('button');toggle.type='button';toggle.className='uj-toggle';toggle.dataset.note=entry.id;toggle.setAttribute('aria-expanded',String(selected===entry.id));toggle.setAttribute('aria-controls','uj-'+entry.id);const label=node('span','uj-label');label.append(node('small','uj-badge',entry.category),node('span','uj-title',entry.title));toggle.append(label,node('span','uj-chevron',selected===entry.id?'⌄':'›'));toggle.onclick=()=>{selected=selected===entry.id?undefined:entry.id;draw(entry.id);};card.append(toggle);
   const details=node('div','uj-details');details.id='uj-'+entry.id;details.hidden=selected!==entry.id;details.append(node('p','uj-summary',entry.summary));const changes=node('ul','uj-changes');for(const text of entry.changes)changes.append(node('li','',text));details.append(changes);card.append(details);row.append(card);list.append(row);
  }
  if(!notes.length)list.append(node('p','uj-empty','Aucune mise à jour publiée pour le moment.'));content.append(list);
  const footer=node('footer','uj-footer');const pager=node('nav','uj-pager');pager.setAttribute('aria-label','Pages des mises à jour');const count=Math.max(1,Math.ceil(notes.length/size));
  for(const direction of [-1,0,1]){if(!direction){const status=node('span','uj-page',`${page+1} / ${count}`);status.setAttribute('aria-live','polite');pager.append(status);continue;}const b=document.createElement('button');b.type='button';b.className='uj-arrow';b.textContent=direction<0?'‹':'›';b.setAttribute('aria-label',direction<0?'Mises à jour précédentes':'Mises à jour suivantes');b.disabled=direction<0?page===0:page===count-1;b.onclick=()=>{page+=direction;selected=notes[page*size]?.id;draw();panel.querySelector<HTMLElement>('.uj-toggle')?.focus();};pager.append(b);}
  const back=document.createElement('button');back.type='button';back.className='uj-back';back.textContent='Retour au hub';back.onclick=close;footer.append(pager,back);content.append(footer);panel.append(content);
  if(focus)Array.from(panel.querySelectorAll<HTMLElement>('[data-note]')).find(n=>n.dataset.note===focus)?.focus();
 }
 panel.onkeydown=e=>{if(e.key==='Escape'){e.preventDefault();close();return;}if(e.key==='Tab'){const buttons=Array.from(panel.querySelectorAll<HTMLButtonElement>('button:not(:disabled)')).filter(b=>!b.closest('[hidden]'));const first=buttons[0],last=buttons.at(-1);if(e.shiftKey&&document.activeElement===first){e.preventDefault();last?.focus();}else if(!e.shiftKey&&document.activeElement===last){e.preventDefault();first?.focus();}}};
 draw();panel.querySelector<HTMLElement>('.uj-toggle,.uj-back')?.focus();return {update(){},destroy(){panel.onkeydown=null;if(previous?.isConnected)previous.focus();}};
}
