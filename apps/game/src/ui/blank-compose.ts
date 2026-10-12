import type {Snapshot} from '../activity';
import {assetSlice} from './assets';
import {equipmentArt,resourceArt} from './catalog-art';
import {raritySeal,sizeMenu} from './menu-layout';
import {menuTitles,blankHeading,mountMenu,menuCard,menuGrid,menuStat,menuProgress,node} from './menu-framework';

const names:Record<string,string>={axe:'Hache',pickaxe:'Pioche',spear:'Lance',bag:'Sac'};
const navigation=new Set('tavern games castle arena alley thief casino expedition market'.split(' '));
const backLabels=/^(Retour|Quitter|Partir)/;
/** Recompose live controls from the existing engines; listeners, validation and server actions are retained. */
export function composeBlankMenu(panel:HTMLElement,s:Snapshot){
 const kind=panel.dataset.kind??'';if(panel.classList.contains('game-menu')||panel.classList.contains('live-game')||['world','profile','story','khaz','ashkar'].includes(kind))return;
 // A signed mission is a standalone parchment, never the announcements board.
 if(kind==='jobs'&&s.pending){
  const paper=panel.querySelector<HTMLElement>('.mission-active');
  const actions=Array.from(panel.querySelectorAll<HTMLButtonElement>('.compact-dock button'));
  if(paper){panel.replaceChildren(paper);panel.className='game-menu gm-active-contract';panel.setAttribute('aria-label','Contrat signé');const footer=node('footer','gm-footer');for(const b of actions){skinBlankButton(b);footer.append(b);}panel.append(footer);sizeMenu(panel,0,660);return;}
 }
 const old=Array.from(panel.querySelectorAll<HTMLButtonElement>('button')).filter(n=>!n.closest('.art-extra'));
 const inputs=Array.from(panel.querySelectorAll<HTMLInputElement>('input')).filter(n=>!n.closest('.art-extra'));
 const modal=panel.querySelector<HTMLElement>('.art-extra');
 const notice=panel.querySelector<HTMLElement>('.art-notice');
 const overlays=Array.from(panel.querySelectorAll<HTMLElement>('.art-overlay'));
 const timers=Array.from(panel.querySelectorAll<HTMLElement>('[data-deadline]')).filter(n=>!n.closest('.art-extra'));
 const busy=panel.getAttribute('aria-busy')==='true';
 const title=panel.getAttribute('aria-label')||menuTitles[kind]||kind;
 const byLabel=(label:string)=>old.find(n=>n.getAttribute('aria-label')===label);
 const used=new Set<HTMLButtonElement>();
 const {body,footer}=mountMenu(panel,kind,title,busy);sizeMenu(panel,0,1020);
 function button(b:HTMLButtonElement|undefined,parent:HTMLElement){if(!b||used.has(b))return;used.add(b);skinBlankButton(b);parent.append(b);return b;}
 function action(label:string,parent=footer){return button(byLabel(label),parent);}
 function controls(parent:HTMLElement,labels:string[]){const row=node('div','gm-actions');for(const label of labels)action(label,row);parent.append(row);return row;}
 function field(parent:HTMLElement,input:HTMLInputElement,label:string){input.removeAttribute('style');input.className='gm-input';const l=node('label','gm-input-label',label);l.append(input);parent.append(l);return input;}
 function timer(parent:HTMLElement,n:HTMLElement){n.className='gm-timer'+(n.classList.contains('drink-timer')?' drink-timer':'');n.removeAttribute('style');const wrapped=n.querySelector<HTMLElement>('.native-field-text');if(wrapped)n.replaceChildren(wrapped.textContent??'');parent.append(n);}
 function art(card:HTMLElement,content:Node){const n=node('div','gm-art');n.append(content);card.prepend(n);}
 const tabRow=()=>{const n=node('nav','gm-tabs');n.setAttribute('aria-label','Choix du menu');body.append(n);return n;};
 const gearName=(key:string,t:number)=>key==='bag'?s.bags[String(t)]?.name:s.tools[String(t)]?.[key];
 function card(parent:HTMLElement,title:string,copy='',icon?:Node){const n=menuCard(parent,title,copy,icon);n.dataset.material=kind==='bank'?'blue':'wood';const material=kind==='bank'?assetSlice('/assets/blank-ui/bank.png',190,450,440,200):navigation.has(kind)?assetSlice('/assets/blank-ui/navigation.png',215,565,230,80):assetSlice('/assets/blank-ui/forge.png',415,450,275,160);material.classList.add('gm-material');material.setAttribute('preserveAspectRatio','none');n.prepend(material);return n;}
 if(navigation.has(kind)){
  const choices=old.filter(b=>!backLabels.test(b.getAttribute('aria-label')??''));
  const grid=menuGrid(body,['tavern','castle','market'].includes(kind)?3:2);
  const hints:Record<string,string>={'Le tavernier':'Choisir une boisson','Les jeux':'Jouer à la taverne','Le troubadour':'Lire les chapitres débloqués','Tableau de bord':'Vos objectifs et votre progression',Podium:'Le classement des aventuriers',Acheter:'Outils, consommables et divers',Vendre:'Ressources des métiers',Histoire:'Objets séparés par chapitre'};
  for(const [i,b] of choices.entries()){
   const label=b.getAttribute('aria-label')??'';if(label==='Jeu contre un ami indisponible'){used.add(b);continue;}const c=card(grid,label,hints[label]??'');
   if(kind==='expedition'&&i<3)art(c,equipmentArt(['axe','pickaxe','spear'][i],s.gear[['axe_level','pickaxe_level','spear_level'][i]]||1));
   if(kind==='arena'&&i<2)art(c,assetSlice('/assets/menus/arena.webp',i===0?65:820,220,650,480));
   if(kind==='tavern'){const files=['tavern_barman.webp','tavern_games.webp','tavern_troubadour.webp'];const im=new Image();im.src='/assets/scenes/'+files[i];im.alt='';im.className='gm-scene';art(c,im);}
   button(b,c);
  }
 }else if(kind==='bank'){
  const ledger=node('div','gm-ledger');for(const [label,value] of [['Portefeuille',s.balance.wallet],['Banque',s.balance.bank],['Fortune',s.balance.wallet+s.balance.bank]] as const)menuStat(ledger,label,`${value} Gold`);body.append(ledger);
  const grid=menuGrid(body);for(const mode of ['deposit','withdraw']){const depositing=mode==='deposit',label=depositing?'Montant à déposer':'Montant à retirer',input=inputs.find(n=>n.getAttribute('aria-label')===label),c=card(grid,depositing?'Déposer':'Retirer');const amountControls=node('div','gm-actions gm-amount-controls');const minus=button(byLabel('Diminuer '+mode),amountControls);if(minus)minus.querySelector('.gm-button-label')!.textContent='−';if(input)field(amountControls,input,label);const plus=button(byLabel('Augmenter '+mode),amountControls);if(plus)plus.querySelector('.gm-button-label')!.textContent='+';c.append(amountControls);
   const presets=controls(c,['100 '+mode,'500 '+mode,'Tout '+mode]);presets.classList.add('gm-bank-presets');for(const n of Array.from(presets.querySelectorAll<HTMLElement>('.gm-button-label')))n.textContent=n.textContent!.startsWith('Tout')?'Tout':n.textContent!.split(' ')[0];
   if(!depositing){const note=overlays.find(n=>/Premier retrait|Frais :|Banque vide|montant valide/.test(n.textContent??''));if(note)c.append(node('p','gm-copy',note.textContent??''));}
   action(depositing?'Confirmer le dépôt':'Confirmer le retrait',c);
  }
 }else if(kind==='forge'){
  const keys=Object.keys(names).filter(k=>s.catalog[k]),tabs=tabRow();for(const key of keys){const b=byLabel(names[key]);if(b){const chosen=b.classList.contains('selected');button(b,tabs);b.setAttribute('aria-pressed',String(chosen));}}
  const selected=keys.find(k=>byLabel(names[k])?.getAttribute('aria-pressed')==='true')??keys[0],current=s.gear[selected+'_level'],next=current+1,max=next>5,owned=s.owned[selected];
  const grid=menuGrid(body);card(grid,'Équipement actuel',owned?`${gearName(selected,current)}\nPalier ${current}`:'Non possédé',owned?equipmentArt(selected,current):undefined);card(grid,'Amélioration',max?'Palier maximum atteint':`${gearName(selected,next)}\nPalier ${next}`,equipmentArt(selected,Math.min(next,5)));
  const recipe=(selected==='bag'?s.bag_recipes:s.recipes)[next]??{},c=card(body,'Matériaux requis');for(const [name,qty] of Object.entries(recipe)){const row=node('div','gm-resource'),icon=resourceArt(name);row.append(icon??node('span'),node('span','',name),node('strong',(s.resources[name]??0)>=qty?'enough':'missing',`${s.resources[name]??0} / ${qty}`));c.append(row);}if(max)c.append(node('p','gm-copy','Palier maximum atteint'));
  const ledger=node('div','gm-ledger');menuStat(ledger,'Niveau requis',String(s.forge_levels[next]??0));menuStat(ledger,'Coût',`${s.forge_gold[selected==='bag'?'bag':'tool'][next]??0} Gold`);menuStat(ledger,'Portefeuille',`${s.balance.wallet} Gold`);c.append(ledger);action('Améliorer');
 }else if(kind==='drinks'){
  const grid=menuGrid(body,3);for(const [i,d] of s.tavern.drinks_catalog.entries()){const c=card(grid,d.name,'',assetSlice('/assets/menus/drinks.webp',140+(i%3)*445,180+Math.floor(i/3)*348,385,215));const b=byLabel(d.name);const chosen=b?.classList.contains('selected');button(b,c);b?.setAttribute('aria-pressed',String(chosen));}menuStat(body,'Services restants',String(s.tavern.remaining_today));for(const n of timers)timer(body,n);action('Commander');
 }else if(kind==='jobs'){
  if(s.pending){const c=card(body,s.pending.job.title,`${s.pending.job.reward} Gold · Contrat signé`);for(const n of timers)timer(c,n);const p=menuProgress(c,3600-s.pending.remaining,3600,'Progression du contrat');p.classList.add('mission-progress');action('Récupérer la récompense');}
  else{const grid=menuGrid(body);for(const b of old.filter(n=>(n.getAttribute('aria-label')??'').startsWith('Accepter '))){const title=(b.getAttribute('aria-label')??'').slice(9),j=s.board.jobs.find(j=>j.title===title);const c=card(grid,title,j?`${j.reward} Gold · 1 heure`:'',j?raritySeal(j.rarity):undefined);button(b,c);}const p=overlays.find(n=>/^\d+\/\d+$/.test(n.textContent?.trim()??''));const row=controls(body,['Page précédente','Page suivante']);if(p)row.insertBefore(node('span','gm-copy',p.textContent??''),row.lastElementChild);}
 }else if(kind==='dashboard'){
  const ledger=node('div','gm-ledger');menuStat(ledger,'Niveau',String(s.level));menuStat(ledger,'Portefeuille',`${s.balance.wallet} Gold`);menuStat(ledger,'Banque',`${s.balance.bank} Gold`);body.append(ledger);const c=card(body,'Expérience',`${s.xp} / ${s.xp_needed} XP`);menuProgress(c,s.xp,s.xp_needed,'Progression du niveau');const grid=menuGrid(body),done=s.quests.filter(q=>q.progress>=q.target).length,q=card(grid,'Quêtes quotidiennes',`${done} / ${s.quests.length} terminées`);menuProgress(q,done,s.quests.length,'Quêtes accomplies');controls(q,['Quêtes quotidiennes','Réclamer les quêtes']);card(grid,'Activités',`${s.active?s.active.name:'Aucune expédition'}\n${s.stats.wins} victoires · ${s.stats.losses} défaites`);action('Actualiser');
 }else if(kind==='podium'){
  const grid=menuGrid(body,3);for(const rank of [1,0,2]){const e=s.podium[rank];card(grid,`${rank+1}${rank===0?'er':'e'} — ${e?.name??'Place libre'}`,e?`${e.total} Gold`:'—');}action('Actualiser');
 }else if(kind==='guard'||kind==='robber'){
  const c=card(body,kind==='guard'?'Salle clandestine':'Banque de IV',kind==='guard'?(s.alley.access.valid?'Accès valable jusqu’à minuit':s.alley.vip?'Entrée VIP gratuite':`${s.alley.fee} Gold · jusqu’à minuit`):'Préparez votre opération et trouvez la combinaison du coffre.',assetSlice('/assets/menus/'+kind+'.webp',...(kind==='guard'?[70,210,670,470]:[80,305,650,350]) as [number,number,number,number]));for(const b of old.filter(n=>!backLabels.test(n.getAttribute('aria-label')??'')))button(b,c);
 }else if(kind==='combat'){
  const grid=menuGrid(body);for(const f of s.play.fighters??[]){const c=card(grid,f.name,`${f.hp} / ${f.max_hp} PV`);menuProgress(c,f.hp,f.max_hp,'PV de '+f.name);}menuStat(body,'Tour',String(s.play.turn??0));const c=card(body,'Journal des attaques'),log=node('div','gm-battle-log');for(const t of (s.play.logs??[]).slice(-8))log.append(node('p','',t.replaceAll('*','')));c.append(log);for(const b of old)button(b,footer);
 }else if(kind==='techniques'){
  const grid=menuGrid(body,3);for(const [key,skill] of Object.entries(s.arena.skills)){const c=card(grid,skill.name,`Puissance : ${skill.power}${key==='ultimate'?'\nRecharge : '+(s.play.fighters?.[0]?.ultimate_cd??0)+' tour(s)':''}`);action('Utiliser '+skill.name,c);}
 }else if(kind==='accessories'){
  const grid=menuGrid(body);card(grid,'Accessoire 1','Aucun objet disponible');card(grid,'Accessoire 2','Aucun objet disponible');
 }else if(kind==='live'){
  const a=s.active;if(a){const c=card(body,a.name);const scene=overlays.map(o=>o.querySelector('img')).find(Boolean);if(scene){scene.className='gm-scene';c.prepend(scene);}for(const n of timers)timer(c,n);menuProgress(c,s.server_now-a.started_at,a.ends_at-a.started_at,'Progression du voyage');const grid=menuGrid(body);card(grid,'Ressources découvertes',Object.entries(a.revealed_loot).map(([k,v])=>`${k} × ${v}`).join('\n')||'Aucune ressource découverte');card(grid,'Journal du voyage',a.log.slice(-5).map(l=>`${l.resource_name} +${l.quantity}`).join('\n')||'Le voyage commence…');}else card(body,'Expédition terminée','Les gains ont été ajoutés à votre personnage.');
 }else if(['tools','destinations','departure'].includes(kind)){
  const content=card(body,menuTitles[kind]);
  for(const o of overlays){if(o.matches('.art-extra *'))continue;const artNode=o.querySelector<SVGSVGElement>(':scope > svg:not(.native-field-text svg)');if(o.classList.contains('native-equipment')&&artNode){art(content,artNode);continue;}const scene=o.querySelector('img');if(scene){scene.className='gm-scene';scene.removeAttribute('style');content.prepend(scene);continue;}
   const copy=o.querySelector<HTMLElement>('.native-field-text')?.textContent??o.textContent??'';if(copy.trim()&&!o.querySelector('input,progress'))content.append(node('p','gm-copy',copy));const progress=o.querySelector('progress');if(progress){progress.className='gm-progress';content.append(progress);}}
  for(const n of timers)timer(content,n);
  const tabs=tabRow();for(const b of old){const label=b.getAttribute('aria-label')??'';if(label==='Palier non disponible'){used.add(b);continue;}button(b,/^Palier \d+$/.test(label)?tabs:footer);}
 }else{
  for(const o of overlays){const copy=o.textContent?.trim();if(copy&&!o.querySelector('input'))card(body,copy);}
 }
 // Existing return actions remain attached to their original handlers.
 for(const b of old)if(!used.has(b))button(b,footer);
 if(notice){notice.removeAttribute('style');notice.className='gm-notice';if(!modal?.contains(notice))body.append(notice);}
 if(modal){skinBlankModal(modal);panel.append(modal);}sizeMenu(panel,0,1020);
}
export function skinBlankButton(b:HTMLButtonElement){const label=b.getAttribute('aria-label')??b.textContent??'';b.removeAttribute('style');b.className='gm-button';b.setAttribute('aria-label',label);b.replaceChildren(node('span','gm-button-label',label));}
export function skinBlankModal(modal:HTMLElement){modal.removeAttribute('style');modal.classList.add('gm-modal');for(const b of Array.from(modal.querySelectorAll<HTMLButtonElement>('button')))skinBlankButton(b);const paper=modal.querySelector<HTMLElement>('.mission-parchment');if(paper){paper.classList.add('gm-dialog','gm-contract');}else{const wrapper=node('section','gm-dialog');wrapper.append(...Array.from(modal.childNodes));modal.append(wrapper);}for(const input of Array.from(modal.querySelectorAll<HTMLInputElement>('input'))){input.removeAttribute('style');input.className='gm-input';}}

export function composeBlankCommerce(panel:HTMLElement,s:Snapshot){
 const kind=panel.dataset.kind??'market-buy';const mode=kind.slice(7),tabs=panel.querySelector<HTMLElement>('.merchant-tabs'),pager=panel.querySelector<HTMLElement>('.merchant-pager'),cards=Array.from(panel.querySelectorAll<HTMLElement>('.merchant-card')),buttons=Array.from(panel.querySelectorAll<HTMLButtonElement>('.merchant-footer>button')),modal=panel.querySelector<HTMLElement>('.merchant-modal'),status=panel.querySelector<HTMLElement>('.merchant-status');
 const {body,footer}=mountMenu(panel,kind,mode==='sell'?'Vendre au marché':mode==='story'?'Objets d’histoire':'Boutique de Legacy',panel.getAttribute('aria-busy')==='true');sizeMenu(panel,0,1020);
 menuStat(body,'Portefeuille',`${s.balance.wallet} Gold`);
 if(tabs){tabs.removeAttribute('style');tabs.className='gm-tabs';for(const b of Array.from(tabs.querySelectorAll<HTMLButtonElement>('button')))skinBlankButton(b);body.append(tabs);}
 const grid=menuGrid(body);for(const c of cards){c.removeAttribute('style');c.className='gm-card merchant-card';const svg=c.querySelector<SVGSVGElement>('.merchant-item-icon>svg'),info=c.querySelector<HTMLElement>('.merchant-item-info'),trade=c.querySelector<HTMLButtonElement>('button'),empty=c.querySelector<HTMLElement>('.native-empty');c.replaceChildren();if(svg){const art=node('div','gm-art');art.append(svg);c.append(art);}if(info){const h=info.querySelector('h3');if(h){h.className='gm-card-title';c.append(h);}for(const n of Array.from(info.children)){n.removeAttribute('style');n.className=n.classList.contains('merchant-chapter')?'gm-copy merchant-chapter':'gm-copy';c.append(n);}}if(empty){empty.className='gm-copy';empty.removeAttribute('style');c.append(empty);}if(trade){skinBlankButton(trade);c.append(trade);}grid.append(c);}
 if(pager){pager.removeAttribute('style');pager.className='gm-actions gm-pager';for(const b of Array.from(pager.querySelectorAll<HTMLButtonElement>('button')))skinBlankButton(b);const p=pager.querySelector<HTMLElement>(':scope > span');if(p){p.className='gm-copy';pager.insertBefore(p,pager.children[1]);}Array.from(pager.querySelectorAll<HTMLElement>('.gm-button-label')).forEach((n,i)=>n.textContent=i===0?'‹':'›');body.append(pager);}
 for(const b of buttons){skinBlankButton(b);footer.append(b);}if(status){status.className='gm-notice';body.append(status);}
 if(modal){modal.removeAttribute('style');modal.className='merchant-modal gm-modal';const content=modal.querySelector<HTMLElement>('.merchant-confirm')!;content.removeAttribute('style');content.className='merchant-confirm gm-dialog gm-contract';for(const b of Array.from(content.querySelectorAll<HTMLButtonElement>('button')))skinBlankButton(b);for(const i of Array.from(content.querySelectorAll<HTMLInputElement>('input')))i.className='gm-input';panel.append(modal);}sizeMenu(panel,0,1020);
}

export function composeBlankGame(panel:HTMLElement,title:string){
 panel.className='game-menu live-game blank-game';sizeMenu(panel,0,1120);
 const table=panel.querySelector<HTMLElement>('.game-table')!;table.classList.add('gm-game-table');
 const heading=table.querySelector<HTMLElement>('.game-title');if(heading){heading.classList.remove('compact-button','sr-only');const plaque=blankHeading(title);heading.replaceChildren(...Array.from(plaque.childNodes));heading.classList.add('gm-title-plaque');}
 for(const b of Array.from(table.querySelectorAll<HTMLButtonElement>('button.compact-button'))){if(b.classList.contains('slot-lever'))continue;const classes=Array.from(b.classList).filter(c=>!['compact-button','art-button'].includes(c)),gestures=Array.from(b.querySelectorAll<SVGSVGElement>('svg[data-gesture]'));skinBlankButton(b);b.classList.add(...classes);for(const g of gestures)b.prepend(g);}sizeMenu(panel,0,1120);
}
