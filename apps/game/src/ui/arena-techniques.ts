import type {Snapshot,ArenaSkill} from '../activity';
import {mountMenu,node,menuButton,blankHeading} from './menu-framework';
import {watchMenuSize} from './menu-layout';
type Host={state:()=>Snapshot;mutate:(body:Record<string,unknown>)=>Promise<string>;route:(key:string)=>void};
const slots=[['light','Attaque rapide'],['heavy','Attaque puissante'],['ultimate','Ultime'],['defend','Garde']];
export function openArenaTechniqueBook(panel:HTMLElement,host:Host){
 let slot='light',pending:ArenaSkill|undefined,locked=false,dead=false,notice='';
 const btn=(label:string,fn:()=>void,disabled=false)=>menuButton(label,fn,disabled||locked);
 const info=(s:ArenaSkill)=>s.power===undefined?'Technique défensive':`Puissance : ${s.power} · Précision : ${Math.round((s.accuracy??1)*100)} %`;
 async function equip(){if(locked||!pending)return;const id=pending.id;locked=true;draw();try{notice=await host.mutate({action:'arena_equip',slot,technique:id,loadout_revision:host.state().arena.loadout_revision});pending=undefined;}catch(e){notice=String(e);pending=undefined;}finally{locked=false;if(!dead)draw();}}
 function draw(){
  const s=host.state(),active=s.play.kind==='combat'&&s.play.status==='active',current=s.arena.skills[slot],{body,footer}=mountMenu(panel,'combat','Techniques',locked);panel.classList.add('arena-combat','arena-technique-book');panel.querySelector('.gm-header')?.replaceChildren(blankHeading('Techniques'));
  body.append(node('p','arena-book-intro','Une victoire, une technique dérobée. Quatre emplacements, un style à composer. Les techniques remplacées restent dans votre collection.'));
  if(active)body.append(node('p','arena-next','Votre équipement est figé pour ce combat. Remplacez vos techniques après le duel.'));
  const tabs=node('div','arena-book-slots');tabs.setAttribute('role','group');tabs.setAttribute('aria-label','Emplacements de techniques');
  for(const [key,label] of slots){const b=btn(`${label} · ${s.arena.skills[key].name}`,()=>{slot=key;pending=undefined;draw();});b.setAttribute('aria-pressed',String(slot===key));tabs.append(b);}body.append(tabs);
  body.append(node('h2','arena-book-heading',`Équipée : ${current.name}`));
  const base:ArenaSkill={...s.arena.base_skills![slot],id:'base_'+slot,unlocked:true,source:'Apprentissage par niveau',description:slot==='defend'?'Réduction du prochain impact : 40 %.':slot==='ultimate'?'Recharge : 2 actions.':'Technique de base évoluant avec votre niveau.',limit:'Toujours disponible ; peut être rééquipée gratuitement.'};
  const list=node('section','arena-book-cards');list.setAttribute('aria-label','Techniques disponibles');
  for(const skill of [base,...(s.arena.techniques??[]).filter(t=>t.slot===slot)]){
   const card=node('article','arena-book-card'+(!skill.unlocked?' is-locked':''));card.append(node('span','arena-eyebrow',skill.source??''),node('h3','',skill.name),node('p','arena-book-power',info(skill)),node('p','',skill.description??''),node('p','arena-book-limit',skill.limit??''));
   const equipped=current.id===skill.id;
   const b=btn(equipped?'Équipée':!skill.unlocked?`Vaincre le champion ${skill.champion}`:`Équiper ${skill.name}`,()=>{pending=skill;draw();panel.querySelector('.arena-book-confirm')?.scrollIntoView({block:'nearest'});},equipped||!skill.unlocked||active);b.setAttribute('aria-label',equipped?`${skill.name} · équipée`:!skill.unlocked?`${skill.name} · verrouillée`:`Équiper ${skill.name}`);card.append(b);list.append(card);
  }body.append(list);
  if(pending){const box=node('section','arena-book-confirm');box.setAttribute('aria-label','Confirmer le remplacement');box.append(node('h3','',`Remplacer ${current.name} par ${pending.name} ?`),node('p','',`${info(current)} → ${info(pending)}`),node('p','','L’ancienne technique reste disponible. Aucun Gold demandé.'),btn('Confirmer le remplacement',()=>void equip(),active),btn('Annuler le remplacement',()=>{pending=undefined;draw();}));body.append(box);}
  const status=node('p','arena-combat-notice',locked?'Enregistrement…':notice);status.setAttribute('role','status');body.append(status);footer.append(btn('Retour à l’arène',()=>host.route('arena')));
 }
 const stop=watchMenuSize(panel);draw();panel.scrollTop=0;
 return {update(){if(!locked&&!dead)draw();},destroy(){dead=true;stop();panel.classList.remove('arena-technique-book');document.body.classList.remove('illustrated-open');}};
}
