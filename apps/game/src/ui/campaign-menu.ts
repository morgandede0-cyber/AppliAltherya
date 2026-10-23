import type {Snapshot} from '../activity';
import {trapMenu} from './menu-kit';
import {questWorldArt} from './quest-world-art';
import './campaign-menu.css';
import './campaign-world.css';
type Host={state:()=>Snapshot;mutate:(body:Record<string,unknown>)=>Promise<string>;close:()=>void;route:(key:string)=>void};
const el=(tag:string,text='',cls='')=>{const n=document.createElement(tag);n.textContent=text;n.className=cls;return n;};
/** Read-only journal. All progress is made through an interaction in a scene. */
export function openCampaignMenu(panel:HTMLElement,host:Host){
 let tab='mission',dead=false;
 function draw(){if(dead)return;panel.hidden=false;panel.className='campaign-menu campaign-journal';panel.dataset.kind='campaign';panel.setAttribute('aria-label','Carnet de route');panel.replaceChildren();const c=host.state().campaign,q=c?.quest;
  panel.append(el('p','LES ROUTES DES TROIS TERRES','campaign-kicker'),el('h2','Carnet de route'));
  const nav=el('div','','campaign-tabs');for(const [key,label] of [['mission','Ma quête'],['places','Lieux découverts'],['evidence','Objets et preuves']]){const b=btn(label,()=>{tab=key;draw();});b.setAttribute('aria-pressed',String(tab===key));nav.append(b);}panel.append(nav);
  if(!c)panel.append(el('p','Synchronisation de votre aventure…'));
  else if(tab==='places'){for(const p of c.locations??[]){const row=el('article','','campaign-evidence');row.append(el('h3',p.name),el('p',p.description));if(p.can_enter)row.append(btn('Se rendre sur place',()=>host.route('quest:'+p.id)));else row.append(el('p',p.level_allowed?'Une piste doit vous y conduire.':`Niveau ${p.min_level} requis`));panel.append(row);}}
  else if(tab==='evidence'){panel.append(el('p','Les objets d’enquête sont conservés à part : ils ne peuvent être ni vendus ni mis au commerce.'));for(const item of c.world?.items??[]){const row=el('article','','campaign-evidence campaign-quest-item'),art=questWorldArt(item.item_id);if(art)row.append(art);const text=el('div');text.append(el('h3',item.name),el('p',item.delivered_at?'✓ Remis au destinataire':'Dans votre sac de quête'));row.append(text);panel.append(row);}if(!c.evidence?.length)panel.append(el('p','Votre carnet de preuves est encore vierge.'));for(const proof of c.evidence??[]){const row=el('details','','campaign-place-proof');row.append(el('summary',proof.title),el('p',proof.text));panel.append(row);}for(const r of q?.decision_history??c.decision_history??[])panel.append(el('h3',r.choice),el('p',r.reaction));}
  else if(c.complete)panel.append(el('h3','Les routes sont ouvertes'),el('p',`${c.completed}/${c.total} quêtes accomplies. Vos décisions sont conservées.`));
  else if(q){panel.append(el('p',`Saison ${q.season} · Chapitre ${q.chapter}`,'campaign-kicker'),el('h3',q.title),el('p',q.scene),el('p',`${q.gold} Gold · ${q.xp} XP · Niveau ${q.min_level}`,'campaign-meta'));if(q.context)panel.append(el('p',q.context));const list=el('ol','','campaign-objectives');for(const [i,s] of q.steps.entries())list.append(el('li',(i<c.stage?'✓ ':'')+s.label,i<c.stage?'done':i===c.stage?'active':''));panel.append(list);
   const w=c.world;if(w){panel.append(el('h3',c.accepted&&c.stage<q.steps.length?'Votre prochaine destination':c.accepted?'Retour auprès du commanditaire':'Rencontrer le commanditaire'),el('p',w.target_name,'campaign-place'));if(!c.level_allowed&&!c.accepted)panel.append(el('p',`Atteignez le niveau ${q.min_level} pour poursuivre.`));panel.append(btn('Rejoindre : '+w.target_name,()=>host.route('quest:'+w.target),!c.accepted&&!c.level_allowed));}panel.append(el('p','Le carnet vous guide. Parlez aux personnages et examinez les objets directement dans les lieux.','campaign-context'));
  }
  panel.append(btn('Fermer le carnet',host.close));
 }
 function btn(label:string,fn:()=>void,disabled=false){const b=el('button',label) as HTMLButtonElement;b.type='button';b.disabled=disabled;b.onclick=fn;return b;}
 trapMenu(panel,()=>false,host.close);draw();return{update:draw,destroy(){dead=true;panel.onkeydown=null;}};
}
/** Local dialogue / encounter, opened by clicking the actual NPC or object. */
export function openCampaignInteraction(panel:HTMLElement,host:Host,scene:string){
 let busy=false,dead=false,notice='',offset=host.state().server_now-Date.now()/1000;
 const initial=host.state().campaign,identity=initial?.quest?.id+':'+initial?.stage+':'+initial?.accepted;
 function button(label:string,fn:()=>void,disabled=false){const b=el('button',label) as HTMLButtonElement;b.type='button';b.disabled=busy||disabled;b.onclick=fn;return b;}
 async function run(action:string,extra:Record<string,unknown>={}){const c=host.state().campaign;if(busy||!c?.quest||c.world?.scene!==scene)return;busy=true;draw();try{notice=await host.mutate({action,quest_id:c.quest.id,revision:c.revision,world_token:c.world.token,...extra});offset=host.state().server_now-Date.now()/1000;}catch(e){notice=e instanceof Error?e.message:String(e);}finally{busy=false;if(!dead)draw();}}
 function countdown(deadline:number,label:string){const n=el('p','','campaign-timer');n.dataset.deadline=String(deadline);n.dataset.label=label;panel.append(n);}
 function draw(){if(dead)return;const s=host.state(),c=s.campaign,q=c?.quest;panel.hidden=false;panel.className='campaign-menu campaign-encounter';panel.dataset.kind='campaign';panel.setAttribute('aria-label','Interaction de quête');panel.setAttribute('aria-busy',String(busy));panel.replaceChildren();
  if(!c||!q||c.world?.scene!==scene||c.world.target!==scene){panel.append(el('h2','Votre prochaine étape vous attend'),el('p',notice||'Cet échange est terminé.'),button('Revenir dans le lieu',host.close));return;}
  panel.append(el('p',c.world.target_name,'campaign-kicker'),el('h2',q.title));
  if(identity!==q.id+':'+c.stage+':'+c.accepted){panel.append(el('p',notice||'Votre carnet a été mis à jour.'),el('p','Prochain objectif : '+(q.steps[c.stage]?.label??'Remettre la quête')),button('Revenir dans le lieu',host.close));return;}
  if(!c.accepted){panel.append(el('blockquote',q.dialogue),el('p',q.scene),el('p',`${q.gold} Gold · ${q.xp} XP`),button('Accepter la quête',()=>void run('campaign_accept'),!c.level_allowed));}
  else{const step=q.steps[c.stage];if(!step){panel.append(el('p',q.resolution));const b=button(`Remettre la quête · ${q.gold} Gold + ${q.xp} XP`,()=>void run('campaign_claim'));panel.append(b);}
   else{panel.append(el('h3',step.label));if(step.text)panel.append(el('p',step.text));
    if(step.kind==='talk')panel.append(button('Poursuivre cet échange',()=>void run('campaign_step')));
    else if(step.kind==='choice'||step.kind==='puzzle'){if(step.question)panel.append(el('p',step.question));for(const [i,o] of (step.options??[]).entries())panel.append(button(o,()=>void run('campaign_step',{option:i})));}
    else if(step.kind==='collect')panel.append(el('p','Cet objet se récupère directement dans le décor. Revenez dans le lieu pour le prendre.'));
    else if(step.kind==='deliver')panel.append(el('p',`${s.resources[step.resource??'']??0}/${step.quantity} · ${step.resource}`),button('Remettre les ressources',()=>void run('campaign_step'),(s.resources[step.resource??'']??0)<(step.quantity??0)));
    else if(step.kind==='expedition')panel.append(el('p','Effectuez un nouveau voyage à la destination indiquée et récupérez sa récolte. Le rapport se remet ici.'),button('Préparer une expédition',()=>host.route(step.world_scene==='vorak'?'vorak':'elarwyn')),button('Remettre le rapport',()=>void run('campaign_step'),!c.expedition_ready));
    else if(step.kind==='port')panel.append(button('Poursuivre l’enquête du port',()=>host.route('port')),button('Remettre le dossier authentifié',()=>void run('campaign_step'),!s.port?.complete));
    else if(step.kind==='explore')panel.append(el('p','Les points à examiner se trouvent dans le décor. Fermez cet échange pour poursuivre la recherche.'));
    else if(step.kind==='battle'){const battle=c.battle;if(battle){for(const f of battle.fighters){const row=el('div','','campaign-fighter');row.append(el('span',`${f.name} · ${f.hp}/${f.max_hp} PV`));const meter=document.createElement('progress');meter.max=f.max_hp;meter.value=f.hp;meter.setAttribute('aria-label',f.name);row.append(meter);panel.append(row);}const log=el('ol','','campaign-log');log.setAttribute('aria-live','polite');for(const line of battle.log)log.append(el('li',line.replace(/\*\*/g,'')));panel.append(log);}if(!battle||battle.finished)panel.append(button('Engager le combat',()=>void run('campaign_battle',{key:'start'})));else{const controls=el('div','','campaign-combat-actions');for(const [key,label] of [['light','Coup rapide'],['heavy','Coup puissant'],['ultimate','Frappe décisive'],['defend','Garde'],['abandon','Se replier']])controls.append(button(battle.skills?.[key]?.name??label,()=>void run('campaign_battle',{key}),key==='ultimate'&&battle.ultimate_cd>0));panel.append(controls);}}
    else{if(step.work_points?.length)panel.append(el('p',`${(c.work??[]).length}/${step.work_points.length} actions de terrain. Interagissez avec les points du décor pour les effectuer.`));if(c.deadline)countdown(c.deadline,'Travail en cours');else panel.append(el('p',`Durée : ${Math.ceil((step.duration??0)/60)} min. Revenez sur place pour récupérer le résultat.`));const workReady=!step.work_points?.some(point=>!(c.work??[]).includes(point.id));const b=button(c.deadline?'Récupérer le résultat':step.prop?'Détacher et récupérer : '+step.prop.name:step.work_points?.length?'Effectuer les actions dans le décor':'Commencer sur place',()=>void run('campaign_step'),!workReady);if(c.deadline&&workReady)b.dataset.readyAt=String(c.deadline);panel.append(b);}
    if(c.retry_at>Date.now()/1000+offset){countdown(c.retry_at,'Nouvelle tentative');panel.querySelectorAll<HTMLButtonElement>('button').forEach(b=>b.dataset.readyAt=String(c.retry_at));}
   }
  }
  if(notice){const n=el('p',notice,'campaign-notice');n.setAttribute('role','status');panel.append(n);}panel.append(button('Revenir dans le lieu',host.close));tick();
 }
 function tick(){panel.querySelectorAll<HTMLButtonElement>('[data-ready-at]').forEach(b=>b.disabled=busy||Number(b.dataset.readyAt)>Date.now()/1000+offset);panel.querySelectorAll<HTMLElement>('[data-deadline]').forEach(n=>{const t=Math.max(0,Math.ceil(Number(n.dataset.deadline)-Date.now()/1000-offset));n.textContent=t?`${n.dataset.label} : ${Math.floor(t/3600)} h ${Math.floor(t%3600/60)} min ${t%60} s`:'Vous pouvez poursuivre cet échange.';});}
 trapMenu(panel,()=>busy,host.close);draw();panel.querySelector<HTMLButtonElement>('button:not(:disabled)')?.focus();const timer=window.setInterval(tick,1000);return{update(){if(!busy)draw();},destroy(){dead=true;clearInterval(timer);panel.onkeydown=null;}};
}
