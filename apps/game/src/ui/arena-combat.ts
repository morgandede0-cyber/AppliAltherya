import type {Snapshot,PlayState,ArenaResult} from '../activity';
import {mountMenu,node,menuButton,menuStat,blankHeading} from './menu-framework';
import {watchMenuSize} from './menu-layout';
import {championRank} from './arena-view';
import './arena-combat.css';
type Host={state:()=>Snapshot;mutate:(body:Record<string,unknown>)=>Promise<string>;route:(key:string)=>void;close:()=>void;refresh:()=>Promise<void>};
const descriptions:Record<string,string>={light:'Une attaque précise pour maintenir la pression.',heavy:'Plus puissante, mais moins précise. Attention à la garde adverse.',ultimate:'Frappe décisive, avec deux actions de recharge après utilisation.',defend:'Réduit de 40 % le prochain impact reçu. Fait avancer la recharge.'};
const signed=(n:number)=>`${n>0?'+':''}${n}`;
const duration=(n:number)=>`${Math.floor(n/60)} min ${n%60} s`;

export function openArenaCombat(panel:HTMLElement,host:Host,initialHelp=false,reviewLast=false){
 let dead=false,locked=false,help=initialHelp,resultVisible=reviewLast||host.state().play.status==='finished',confirm=false,notice='',logOpen=false,lastRevision=-1;
 let previous:PlayState|undefined;let observedServer=host.state().server_now,serverOffset=observedServer*1000-Date.now();
 const button=(label:string,fn:()=>void,disabled=false)=>menuButton(label,fn,disabled||locked);
 function route(key:string){if(!locked)host.route(key);}
 async function act(key:string){
  if(locked)return;locked=true;confirm=false;draw();
  try{notice=await host.mutate({action:'battle_step',key,revision:host.state().play.revision});if(host.state().play.status==='finished')resultVisible=true;}
  catch(e){notice=String(e);}finally{locked=false;if(!dead)draw();}
 }
 function health(f:NonNullable<PlayState['fighters']>[number],index:number,s:Snapshot,level:number){
  const c=node('article',`arena-fighter arena-fighter-${index}`);c.dataset.fighter=String(index);
  const portrait=node('div','arena-portrait');
  if(index===0&&s.discord){const img=new Image();img.src=s.discord.avatar_url;img.alt='';portrait.append(img);}
  else portrait.append(node('span','arena-sigil',index===0?'⚔':championRank(level)));
  const copy=node('div','arena-fighter-copy');copy.append(node('span','arena-eyebrow',index===0?'VOTRE COMBATTANT':`CHAMPION ${championRank(level)}`),node('h3','arena-fighter-name',index===0?s.name:f.name));
  const hp=node('div','arena-hp');hp.setAttribute('role','progressbar');hp.setAttribute('aria-label',`PV de ${index===0?s.name:f.name}`);hp.setAttribute('aria-valuemin','0');hp.setAttribute('aria-valuemax',String(f.max_hp));hp.setAttribute('aria-valuenow',String(f.hp));
  const track=node('div','arena-hp-track'),fill=node('span','arena-hp-fill');fill.style.width=`${Math.max(0,100*f.hp/f.max_hp)}%`;if(f.hp/f.max_hp<.3)c.classList.add('low-health');track.append(fill);hp.append(track,node('strong','arena-hp-value',`${f.hp} / ${f.max_hp} PV`));
  const statuses=node('div','arena-statuses');for(const status of f.statuses??[])statuses.append(node('span','arena-status',status.label));
  copy.append(hp,statuses);c.append(portrait,copy);return c;
 }
 function logs(parent:HTMLElement,p:PlayState){
  const section=node('section','arena-log');section.append(node('h3','','Journal du combat'));
  const list=node('ol','arena-log-list');list.setAttribute('aria-label','Dernières actions');
  if(p.events?.length){for(const e of p.events.slice(-12)){const li=node('li',`arena-event arena-event-${e.kind}`);li.append(node('span','arena-event-turn',`M${e.round}`),node('span','',e.text));list.append(li);}}
  else for(const line of p.logs??[])list.append(node('li','',line.replaceAll('*','')));
  if(!list.childElementCount)list.append(node('li','arena-log-empty','Le sable est calme. Choisissez votre première technique.'));
  section.append(list);parent.append(section);list.scrollTop=list.scrollHeight;
 }
 function result(parent:HTMLElement,r:ArenaResult,p:PlayState){
  const summary=node('section',`arena-result ${r.won?'victory':'defeat'}`);summary.setAttribute('aria-label','Résultat du combat');
  summary.append(node('span','arena-result-seal',r.won?'⚜':'⚔'),node('h2','',r.won?'Victoire !':r.abandoned?'Combat abandonné':'Défaite'),node('p','arena-result-opponent',`${r.champion.name} · Champion ${championRank(r.champion.level)}`),node('p','arena-result-copy',r.won?`Bravo, ${host.state().name}. Le champion s’incline !`:'Le combat est terminé. Préparez votre prochaine rencontre.'));
  const awards=node('div','arena-result-awards');menuStat(awards,'Résultat net',`${signed(r.net_gold)} Gold`);menuStat(awards,'XP gagnée',`+${r.xp} XP`);menuStat(awards,'Classement',`${signed(r.rating_delta)} · ${r.rating_after} pts`);summary.append(awards);
  const details=node('dl','arena-result-ledger');for(const [label,value] of [['Mise engagée',`${r.wager} Gold`],['Versement, mise comprise',`${r.payout} Gold`],['Manches',String(r.rounds)],['Durée',duration(r.duration)],['PV restants',`${r.hp} / ${r.max_hp}`],['Champions vaincus',`${r.wins_before} → ${r.wins_after} / 10`]])details.append(node('dt','',label),node('dd','',value));summary.append(details);
  const stats=node('div','arena-result-stats');for(const [index,title] of ['Vous',r.champion.name].entries()){const stat=r.stats[index];if(!stat)continue;const side=node('section','');side.append(node('h3','',title),node('p','',`${stat.damage} dégâts infligés · ${stat.hits} impacts · ${stat.critical} critiques · ${stat.guards} gardes · ${stat.misses} attaques manquées`));stats.append(side);}summary.append(stats);
  summary.append(node('p','arena-next',r.won?(r.circuit_complete?'Circuit des dix champions terminé. Le Roi reste disponible pour vos futurs défis.':`Prochain adversaire : ${r.next_champion.name} · Champion ${championRank(r.next_champion.level)}.`):`Votre revanche vous attend contre ${r.champion.name}.`));
  const delay=node('p','arena-next-delay');delay.dataset.ready=String(host.state().server_now+host.state().arena.remaining);summary.append(delay);parent.append(summary);
  if(logOpen)logs(parent,p);
 }
 function draw(){
  if(dead)return;if(host.state().server_now!==observedServer){observedServer=host.state().server_now;serverOffset=observedServer*1000-Date.now();}const s=host.state(),saved=reviewLast?s.arena.recent?.[0]:undefined,p:PlayState=saved?{kind:'combat',status:'finished',revision:-1,champion:saved.champion,round:saved.rounds,phase:1,result:saved,fighters:saved.fighters,events:saved.events,logs:saved.logs,skills:saved.skills,message:saved.won?'Victoire !':'Défaite.'}:s.play,focus=panel.contains(document.activeElement)?document.activeElement?.getAttribute('aria-label'):null,scroll=panel.scrollTop;
  const {body,footer}=mountMenu(panel,'combat','Combat',locked);panel.classList.add('arena-combat');panel.querySelector('.gm-header')?.replaceChildren(blankHeading(initialHelp?'Techniques de combat':'Combat d’arène'));panel.style.setProperty('--champion-accent',p.champion?.color??'#d9b16b');
  if(p.kind!=='combat'||(!p.fighters?.length&&!p.result)){if(initialHelp){body.append(node('h2','arena-guide-title',`Vos techniques · niveau ${s.level}`));for(const key of ['light','heavy','ultimate','defend']){const skill=s.arena.skills[key];if(!skill)continue;const card=node('article','arena-guide');card.append(node('h3','',skill.name),node('p','',descriptions[key]),node('p','',key==='defend'?'Réduction du prochain impact : 40 %':`Puissance : ${skill.power} · Précision : ${Math.round((skill.accuracy??1)*100)} %`));body.append(card);}}else body.append(node('p','','Aucun combat en cours.'));if(p.status==='refunded')body.append(node('p','arena-next',p.message??'Votre mise a été remboursée.'));footer.append(button('Retour à l’arène',()=>route('arena')));return;}
  const top=node('div','arena-combat-top');top.append(node('p','arena-round',`Manche ${p.round??Math.max(1,Math.ceil((p.turn??1)/2))}`),node('p','arena-phase',`${p.champion?.role??'Duel de champion'} · Phase ${p.phase??1}${p.champion?.phases?'/'+p.champion.phases:''}`));body.append(top);
  const board=node('div','arena-duel');for(const [i,f] of (p.fighters??[]).entries())board.append(health(f,i,s,p.champion?.level??s.arena.champion_level));if(!resultVisible||p.status!=='finished'||!p.result)body.append(board);
  if(resultVisible&&p.status==='finished'&&p.result){result(body,p.result,p);footer.append(button(logOpen?'Masquer le journal':'Voir le journal',()=>{logOpen=!logOpen;draw();}),button('Relire le combat',()=>{resultVisible=false;draw();}),button('Retour à l’arène',()=>route('arena')));}
  else{
   const intent=node('section','arena-intent');intent.append(node('span','arena-eyebrow',p.status==='active'?'INTENTION DU CHAMPION':'RENCONTRE TERMINÉE'),node('h3','',p.status==='active'?(p.intent?.name??'Se prépare'):p.message??'Combat terminé'),node('p','',p.champion?.hint??'Préparez votre prochaine technique.'));body.append(intent);
   if(p.phase===2)intent.append(node('span','arena-phase-badge','Seconde phase active'));
   const skills=p.skills??s.arena.skills,actions=node('section','arena-techniques');actions.setAttribute('aria-label','Techniques de combat');
   for(const key of ['light','heavy','ultimate','defend']){const skill=skills[key];if(!skill)continue;const cd=key==='ultimate'?(p.fighters?.[0]?.ultimate_cd??0):0;const b=button(skill.name,()=>void act(key),p.status!=='active'||cd>0);b.dataset.action=key;b.title=descriptions[key];b.replaceChildren(node('span','arena-technique-name',skill.name));const tile=node('article','arena-technique');tile.append(b,node('span','arena-technique-values arena-values-full',key==='defend'?'Garde · réduit le prochain impact':`${skill.power??0} puissance · ${Math.round((skill.accuracy??1)*100)} % précision`),node('span','arena-technique-values arena-values-compact',key==='defend'?'Réduction 40 %':`Puiss. ${skill.power??0} · ${Math.round((skill.accuracy??1)*100)} %`),node('span','arena-technique-availability'+(cd?'':' ready'),cd?`Recharge : ${cd} action${cd>1?'s':''}`:'Disponible'));actions.append(tile);}body.append(actions);
   const utilities=node('div','arena-utilities');utilities.append(button(help?'Masquer les techniques':'Détails des techniques',()=>{help=!help;draw();}),button('Replier le combat',()=>route('arena')));body.append(utilities);
   if(help){const hints=node('section','arena-technique-help');for(const key of ['light','heavy','ultimate','defend'])hints.append(node('p','',`${skills[key]?.name??key} : ${descriptions[key]}`));body.append(hints);}
   logs(body,p);
   if(p.status==='finished'&&!p.result)body.append(node('p','arena-next',`Ancien combat : bilan détaillé non enregistré. Résultat net connu : ${signed((p.payout??0)-(p.wager??0))} Gold. Le règlement déjà effectué est conservé.`));
   if(p.status==='active')footer.append(button('Abandonner le combat',()=>{confirm=true;draw();}));else footer.append(button('Voir le résultat',()=>{resultVisible=true;draw();},!p.result),button('Retour à l’arène',()=>route('arena')));
  }
  const status=node('p','arena-combat-notice',locked?'Résolution du tour…':notice||'');status.setAttribute('role','status');body.append(status);
  if(confirm){const dialog=node('section','arena-confirm');dialog.setAttribute('role','dialog');dialog.setAttribute('aria-modal','true');dialog.setAttribute('aria-label','Abandonner le combat');dialog.append(node('h3','','Abandonner ce combat ?'),node('p','',`La mise de ${p.wager??0} Gold sera perdue.`),button('Continuer le combat',()=>{confirm=false;draw();}),button('Confirmer l’abandon',()=>void act('abandon')));body.append(dialog);for(const b of Array.from(panel.querySelectorAll<HTMLButtonElement>('button')))if(!dialog.contains(b))b.disabled=true;dialog.querySelector<HTMLButtonElement>('button')?.focus();}
  const newlyFinished=p.status==='finished'&&previous?.status==='active';tick();panel.scrollTop=newlyFinished?0:scroll;if(newlyFinished){const summary=panel.querySelector<HTMLElement>('.arena-result');summary?.setAttribute('tabindex','-1');summary?.focus({preventScroll:true});}
  if(focus&&!confirm)Array.from(panel.querySelectorAll<HTMLButtonElement>('button')).find(b=>b.getAttribute('aria-label')===focus&&!b.disabled)?.focus({preventScroll:true});
  if(p.revision!==lastRevision&&!locked){animate(p,previous);previous=structuredClone(p);lastRevision=p.revision;}
 }
 function animate(p:PlayState,old?:PlayState){
  if(!old||window.matchMedia('(prefers-reduced-motion: reduce)').matches)return;
  for(const [i,f] of (p.fighters??[]).entries()){
   const card=panel.querySelector<HTMLElement>(`[data-fighter="${i}"]`),before=old.fighters?.[i];if(!card||!before)continue;
   const fill=card.querySelector<HTMLElement>('.arena-hp-fill');if(fill?.animate&&before.hp!==f.hp)fill.animate([{width:`${100*before.hp/before.max_hp}%`},{width:`${100*f.hp/f.max_hp}%`}],{duration:650,easing:'ease-out'});
   const lost=before.hp-f.hp;if(lost>0){const amount=node('span','arena-floating-damage',`−${lost}`);card.append(amount);card.classList.add('arena-hit');window.setTimeout(()=>{amount.remove();card.classList.remove('arena-hit');},950);}
  }
 }
 function tick(){for(const n of Array.from(panel.querySelectorAll<HTMLElement>('[data-ready]'))){const remaining=Math.max(0,Math.ceil(Number(n.dataset.ready)-(Date.now()+serverOffset)/1000));n.textContent=remaining?`Prochain défi dans ${duration(remaining)}. Consultez vos techniques en attendant.`:'Un nouveau défi est disponible à l’arène.';}}
 const clock=window.setInterval(tick,1000),stop=watchMenuSize(panel);
 panel.onkeydown=e=>{if(e.key==='Escape'&&!locked){e.preventDefault();if(confirm){confirm=false;draw();}else if(help){help=false;draw();}else route('arena');}if(e.key==='Tab'){const scope=panel.querySelector('.arena-confirm')??panel,buttons=Array.from(scope.querySelectorAll<HTMLButtonElement>('button:not(:disabled)'));if(e.shiftKey&&document.activeElement===buttons[0]){e.preventDefault();buttons.at(-1)?.focus();}else if(!e.shiftKey&&document.activeElement===buttons.at(-1)){e.preventDefault();buttons[0]?.focus();}}};
 draw();panel.scrollTop=0;panel.querySelector<HTMLButtonElement>('button:not(:disabled)')?.focus({preventScroll:true});
 return{update(){if(!locked){if(host.state().play.status==='finished'&&previous?.status==='active')resultVisible=true;draw();}},destroy(){dead=true;stop();clearInterval(clock);panel.onkeydown=null;document.body.classList.remove('illustrated-open');}};
}
