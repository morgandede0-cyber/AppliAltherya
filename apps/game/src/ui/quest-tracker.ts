import type {Snapshot} from '../activity';
import './quest-tracker.css';
type Tab='story'|'chronicles'|'daily'|'activity'|'progression';
export function storyObjective(s:Pick<Snapshot,'chapters'>){
 const next=s.chapters.find(c=>!c.unlocked);return next?{title:`Chapitre ${next.chapter} · ${next.title}`,missing:next.missing,ready:next.can_unlock,complete:false}:{title:'Chroniques débloquées',missing:[],ready:false,complete:true};
}
/** Read-only view of server progress. Rewards are claimed through existing menus. */
export function createQuestTracker(host:{route:(key:string)=>void},dailyOnly=false){
 const root=document.createElement('aside');root.id=dailyOnly?'daily-quest-tracker':'quest-tracker';root.hidden=true;root.setAttribute('aria-label',dailyOnly?'Quêtes quotidiennes':'Suivi des quêtes');
 const toggle=document.createElement('button');toggle.type='button';toggle.className='quest-toggle';toggle.setAttribute('aria-controls',dailyOnly?'daily-quest-tracker-body':'quest-tracker-body');
 const body=document.createElement('div');body.id=dailyOnly?'daily-quest-tracker-body':'quest-tracker-body';
 const heading=document.createElement('h2');heading.textContent=dailyOnly?'Quêtes quotidiennes':'Journal de route';
 const tabs=document.createElement('div');tabs.className='quest-tabs';tabs.setAttribute('aria-label','Catégories du suivi');
 const content=document.createElement('section');content.className='quest-content';
 const footer=document.createElement('button');footer.type='button';footer.className='quest-journal';
 body.append(heading,tabs,content,footer);root.append(toggle,body);document.body.append(root);
 let state:Snapshot|undefined,tab:Tab=dailyOnly?'daily':'story',page=0,expanded=!window.matchMedia('(max-width: 700px), (max-height: 520px)').matches;
 const preference=dailyOnly?'altherya.daily-tracker.v1':'altherya.quest-tracker.v1';try{const p=window.localStorage.getItem(preference);if(p==='open'||p==='closed')expanded=p==='open';}catch{}
 const tabButtons=new Map<Tab,HTMLButtonElement>();
 for(const [key,label] of (dailyOnly?[]:[['story','Aventure'],['chronicles','Chroniques'],['activity','Missions'],['progression','Objectifs']]) as [Tab,string][]){const b=document.createElement('button');b.type='button';b.textContent=label;b.onclick=()=>{tab=key;page=0;draw();};tabs.append(b);tabButtons.set(key,b);}
 function fold(){body.hidden=!expanded;toggle.textContent=dailyOnly?(expanded?'‹  Quotidiennes':'›  Quotidiennes'):(expanded?'Quêtes  ›':'Quêtes  ‹');toggle.setAttribute('aria-expanded',String(expanded));toggle.setAttribute('aria-label',dailyOnly?(expanded?'Replier les quêtes quotidiennes':'Ouvrir les quêtes quotidiennes'):(expanded?'Replier le suivi des quêtes':'Ouvrir le suivi des quêtes'));if(expanded&&window.matchMedia('(max-width: 700px), (max-height: 520px)').matches)window.dispatchEvent(new window.CustomEvent('quest-tracker-open',{detail:root.id}));}
 const anotherOpened=(event:Event)=>{if((event as CustomEvent).detail!==root.id&&expanded){expanded=false;fold();}};window.addEventListener('quest-tracker-open',anotherOpened);
 toggle.onclick=()=>{expanded=!expanded;try{window.localStorage.setItem(preference,expanded?'open':'closed');}catch{}fold();};
 root.addEventListener('keydown',e=>{if(e.key==='Escape'&&expanded&&!document.body.classList.contains('menu-open')){e.preventDefault();e.stopPropagation();expanded=false;fold();toggle.focus();}});
 function node(tag:string,text:string,cls=''){const n=document.createElement(tag);n.textContent=text;if(cls)n.className=cls;return n;}
 function route(key:string){if(window.matchMedia('(max-width: 700px), (max-height: 520px)').matches){expanded=false;fold();}host.route(key);queueMicrotask(()=>document.querySelector<HTMLElement>('#panel:not([hidden]) button')?.focus());}
 function draw(){if(!state)return;const s=state;root.hidden=!s.tutorial.completed||s.tutorial.replay;for(const [k,b] of tabButtons)b.setAttribute('aria-pressed',String(k===tab));content.replaceChildren();
  footer.onclick=()=>route(tab==='progression'?'journal':tab==='story'&&s.campaign?'campaign':tab==='story'||tab==='chronicles'?'story':tab==='daily'?'castle':'journal');footer.textContent=tab==='progression'?'Voir ma progression':tab==='story'&&s.campaign?'Ouvrir la quête':tab==='story'||tab==='chronicles'?'Voir le troubadour':tab==='daily'?'Voir les récompenses':'Ouvrir le journal';
  if(tab==='progression'){
   content.append(node('p','Vos prochains pas','quest-kicker'));
   for(const goal of (s.objectives??[]).slice(0,4)){const card=node('article','','quest-goal');card.append(node('h3',(goal.ready?'✓ ':'')+goal.title),node('p',goal.detail,'quest-note'));const meter=document.createElement('progress');meter.max=Math.max(1,goal.target);meter.value=Math.min(goal.current,meter.max);meter.setAttribute('aria-label',goal.title);const b=node('button',goal.ready?'Y aller · prêt':'Voir l’objectif') as HTMLButtonElement;b.type='button';b.onclick=()=>route(goal.route);card.append(meter,b);content.append(card);}
  }else if(tab==='story'&&s.campaign){
   const c=s.campaign,q=c.quest;content.append(node('p',`Campagne · ${c.completed}/${c.total}`,'quest-kicker'));
   if(c.complete)content.append(node('h3','Les routes des Trois Terres'),node('p','✓ Campagne terminée. Vos choix sont conservés.','quest-ready'));
   else if(q){content.append(node('h3',q.title),node('p',`Saison ${q.season} · Niveau ${q.min_level}`,'quest-note'));
    if(!c.accepted)content.append(node('p',c.level_allowed?'Quête disponible · ouvrez le journal pour l’accepter.':`Atteignez le niveau ${q.min_level} pour poursuivre.`));
    else{const list=document.createElement('ul');for(const [i,step] of q.steps.entries())list.append(node('li',`${i<c.stage?'✓ ':''}${step.label}`,i<c.stage?'quest-done':''));content.append(list);if(c.stage===q.steps.length)content.append(node('p','Objectifs terminés · remettez la quête dans le journal.','quest-ready'));}
    content.append(node('p',`${q.gold} Gold · ${q.xp} XP`,'quest-note'));
   }
  }else if(tab==='story'||tab==='chronicles'){
   const q=storyObjective(s);content.append(node('p','Chroniques · Saison 1','quest-kicker'),node('h3',q.title));
   if(q.complete)content.append(node('p','Tous les chapitres sont débloqués. Retrouvez-les dans le livre du troubadour.'));
   else if(q.ready)content.append(node('p','✓ Collection réunie. Débloquez ce chapitre chez le troubadour.','quest-ready'));
   else{content.append(node('p',`${q.missing.length} objet${q.missing.length>1?'s':''} à obtenir au marché.`));const list=document.createElement('ul');for(const name of q.missing.slice(0,3))list.append(node('li',name));content.append(list);if(q.missing.length>3)content.append(node('p',`+ ${q.missing.length-3} autre objet · détails chez le troubadour`,'quest-note'));const b=node('button','Aller au marché') as HTMLButtonElement;b.type='button';b.onclick=()=>route('market:story');content.append(b);}
  }else if(tab==='daily'){
   const qs=s.quests,done=qs.filter(q=>q.progress>=q.target).length;content.append(node('p',`Objectifs du jour · ${done}/${qs.length}`,'quest-kicker'));
   if(!qs.length)content.append(node('p','Aucun objectif quotidien disponible.'));
   page=Math.min(page,Math.max(0,Math.ceil(qs.length/3)-1));const list=document.createElement('ul');for(const q of qs.slice(page*3,page*3+3)){const li=node('li',`${q.progress>=q.target?'✓ ':''}${q.label}`);li.append(node('span',`${Math.min(q.progress,q.target)}/${q.target}`,'quest-count'));if(q.progress>=q.target)li.className='quest-done';list.append(li);}content.append(list);
   if(qs.length>3){const nav=document.createElement('div');nav.className='quest-pages';for(const [label,delta] of [['Précédent',-1],['Suivant',1]] as const){const b=node('button',label) as HTMLButtonElement;b.type='button';b.disabled=delta<0?page===0:(page+1)*3>=qs.length;b.onclick=()=>{page+=delta;draw();};nav.append(b);}content.append(nav);}
   if(qs.length&&qs.every(q=>q.claimed))content.append(node('p','✓ Récompense déjà récupérée.','quest-ready'));else if(qs.length&&done===qs.length)content.append(node('p','✓ Récompense à récupérer au château.','quest-ready'));
  }else{
   content.append(node('p','Activités suivies','quest-kicker'));
   if(s.pending)content.append(node('h3',s.pending.job.title),node('p',s.pending.ready?'✓ Contrat terminé : récompense disponible.':'Contrat en cours. Consultez le contrat pour son délai.'));
   if(s.active)content.append(node('h3',s.active.name),node('p','Expédition en cours · progression dans le journal de voyage.'));
   if(!s.pending&&!s.active)content.append(node('p','Aucun contrat ni expédition en cours.'));
   if(s.pending){const b=node('button','Voir le contrat') as HTMLButtonElement;b.type='button';b.onclick=()=>route('jobs');content.append(b);}if(s.active){const b=node('button','Voir l’expédition') as HTMLButtonElement;b.type='button';b.onclick=()=>route('expedition');content.append(b);}
  }
 }
 fold();return{update(s:Snapshot){state=s;draw();},destroy(){window.removeEventListener('quest-tracker-open',anotherOpened);root.remove();}};
}
