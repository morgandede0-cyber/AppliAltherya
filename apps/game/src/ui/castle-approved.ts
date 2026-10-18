import type {Snapshot} from '../activity';
import {node as el} from './menu-framework';
import {assetSlice} from './assets';
import {approvedCard} from './approved-art';
import {arenaIcon,arenaPlayerName,playerPortrait} from './arena-skin';
import './castle-approved.css';

type Button=(label:string,action:()=>void,disabled?:boolean)=>HTMLButtonElement;
const number=(n:number|string)=>typeof n==='number'?n.toLocaleString('fr-FR'):n;
function row(parent:HTMLElement,label:string,value:string,icon:number){
 const n=el('div','castle-data-row');n.append(arenaIcon(icon),el('span','castle-data-label',label),el('strong','',value));parent.append(n);return n;
}
function group(parent:HTMLElement,title:string){const n=el('section','castle-group');approvedCard(n);n.append(el('h3','',title));parent.append(n);return n;}

export function castleHome(body:HTMLElement,s:Snapshot,button:Button,route:(key:string)=>void,claim:()=>void){
 const grid=el('div','realm-grid castle-paths');
 const entries=[['Tableau de bord','Voir mon parcours','dashboard'],['Podium','Voir le classement','podium'],['Récompense quotidienne',s.daily_available?'Récupérer':'Déjà récupérée','daily']];
 for(const [i,[title,label,key]] of entries.entries()){
  const c=el('article','realm-card castle-path');approvedCard(c);
  c.append(el('h3','',title));
  const scene=el('div','castle-scene');scene.setAttribute('aria-hidden','true');
  const rects=[[195,380,355,320],[589,380,355,320],[987,380,355,320]];
  const [x,y,w,h]=rects[i];const art=assetSlice('/assets/castle-approved/castle-reference.png',x,y,w,h,1536,1024);art.setAttribute('preserveAspectRatio','xMidYMid slice');scene.append(art);c.append(scene);
  if(key==='daily')c.append(el('p','castle-daily-value',`${s.daily_reward?.gold??10} Gold · ${s.daily_reward?.xp??20} XP`));
  c.append(button(label,()=>key==='daily'?claim():route(key),key==='daily'&&!s.daily_available));grid.append(c);
 }
 body.append(grid);
}

export function castleDashboard(body:HTMLElement,s:Snapshot,button:Button,claim:()=>void){
 const identity=el('section','realm-identity castle-identity');approvedCard(identity);identity.append(playerPortrait(s));
 const name=el('div','castle-player-name');name.append(el('h3','',arenaPlayerName(s)),el('span','',`Niveau ${s.level}`));identity.append(name);
 const xp=el('div','castle-experience'),progress=document.createElement('progress');progress.max=Math.max(1,s.xp_needed);progress.value=Math.min(progress.max,Math.max(0,s.xp));progress.setAttribute('aria-label','Progression vers le prochain niveau');xp.append(progress,el('span','',`${number(s.xp)} / ${number(s.xp_needed)} XP`));identity.append(xp);body.append(identity);
 const columns=el('div','castle-dashboard-columns'),activities=group(columns,'Activités'),evolution=group(columns,'Progression');
 row(activities,'Expéditions terminées',String(number(s.stats.expeditions??0)),0);
 row(activities,'Quêtes accomplies',String(number(s.stats.quests_completed??0)),2);
 row(activities,'Champions vaincus',String(number(s.arena.champion_wins??0)),1);
 row(evolution,'Histoire',`${s.chapters.filter(c=>c.unlocked).length} chapitre(s) débloqué(s)`,2);
 row(evolution,'Taverne',s.tavern.label,3);
 row(evolution,'Ruelle sombre',s.alley.reputation.label,4);body.append(columns);
 const current=group(body,'En cours');row(current,'Expédition',s.active?.name??'Aucune en cours',0);row(current,'Contrat',s.pending?.job.title??'Aucun contrat actif',2);
 const wallet=el('div','castle-balances');wallet.append(el('span','',`Portefeuille : ${number(s.balance.wallet)} Gold`),el('span','',`Banque : ${number(s.balance.bank)} Gold`));body.append(wallet);
 const quests=group(body,'Quêtes quotidiennes');const done=s.quests.filter(q=>q.progress>=q.target).length;
 for(const q of s.quests)row(quests,q.label,`${q.progress} / ${q.target}`,2);
 const claimed=s.quests.length>0&&s.quests.every(q=>q.claimed);quests.append(button(claimed?'Récompense déjà récupérée':'Réclamer les quêtes',claim,!s.quests.length||done<s.quests.length||claimed));
}

export function castlePodium(body:HTMLElement,s:Snapshot){
 body.append(el('p','castle-ranking-subtitle','Classement des fortunes'));
 const top=el('div','realm-podium castle-podium');
 for(const rank of [1,0,2]){
  const entry=s.podium[rank],c=el('article','realm-card castle-pedestal');c.dataset.rank=String(rank+1);
  const art=assetSlice('/assets/castle-approved/podium-sprites.png',([1,0,2].indexOf(rank))*724,0,724,724,2172,724);art.setAttribute('preserveAspectRatio','none');art.classList.add('castle-pedestal-art');c.append(art);
  const profile={...s,name:entry?.name??'Place libre',discord:entry?.avatar_url?{username:entry.name,display_name:entry.name,avatar_url:entry.avatar_url}:null};
  c.append(playerPortrait(profile),el('span','realm-rank',String(rank+1)),el('h3','',entry?.name??'Place libre'),el('p','castle-ranking-gold',entry?`${number(entry.total)} Gold`:'—'));top.append(c);
 }
 body.append(top);const fortune=el('div','castle-own-fortune');approvedCard(fortune);fortune.append(el('span','','Votre fortune'),el('strong','',`${number(s.balance.wallet+s.balance.bank)} Gold`));body.append(fortune);
 if(s.podium.length>3){const list=el('ol','realm-ranking castle-ranking');list.setAttribute('start','4');for(const [i,p] of s.podium.slice(3).entries()){const li=el('li','');li.append(el('span','',`${i+4}. ${p.name}`),el('strong','',`${number(p.total)} Gold`));list.append(li);}body.append(list);}
}
