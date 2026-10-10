import {gameMenuButton,gameCrop} from './game-art';
import {openLiveGame,liveGameKinds} from './live-games';
import {decorateButton} from './compact-menu';
import type {Snapshot} from '../activity';
import {withdrawalQuote,validAmount,pageSlice} from './service-model';
import {timeLabel} from './game-model';
import './illustrated.css';
import {itemArt} from './item-art';
import {equipmentArt} from './catalog-art';
import {menuHeading,assetSlice} from './menu-kit';
type Host={state:()=>Snapshot;mutate:(body:Record<string,unknown>)=>Promise<string>;close:()=>void;route:(key:string)=>void;refresh:()=>Promise<void>};
export const illustratedKinds=new Set('bank jobs tavern games castle dashboard podium arena combat techniques alley thief casino blackjack roulette russian slots horses expedition tools destinations accessories departure live dice coin rps'.split(' '));
export function openIllustrated(panel:HTMLElement,initial:string,host:Host,location='elarwyn'){
 let kind=initial,selected='beer',amount=100,withdraw=100,page=0,tool='axe',tier=1,destination='',wager=10,choice:string|number='red',number=0,locked=false,notice='',destroyed=false,animationUntil=0,animationStarted=0,rotation=0,spinRevision=-1,dialog='',acknowledgedResult=-1,offset=host.state().server_now*1000-Date.now();
 const el=(tag:string,text='',cls='')=>{const n=document.createElement(tag);n.className=cls;n.textContent=text;return n;};let stage:HTMLElement,dock:HTMLElement;let live:ReturnType<typeof openLiveGame>|undefined,liveKind='';
 const cleanKinds=new Set(['bank','jobs','dashboard','podium','combat','techniques','destinations','accessories','departure','live']);
 const cleanMode=()=>false;
 const box=(x:number,y:number,w:number,h:number,text='',cls='art-mask')=>{const n=el('div',text,'art-overlay '+cls);if(cleanMode()){n.classList.add('integrated-value');if(kind==='jobs'&&w===7)return n;}Object.assign(n.style,{left:x+'%',top:y+'%',width:w+'%',height:h+'%'});stage.append(n);return n;};
 const button=(label:string,fn:()=>void,disabled=false)=>{const n=el('button',label,'art-button') as HTMLButtonElement;n.disabled=disabled||locked||Date.now()<animationUntil;n.onclick=fn;decorateButton(n,label);return n;};
 const hit=(label:string,x:number,y:number,w:number,h:number,fn:()=>void,disabled=false,chosen=false)=>{
  if(cleanMode()){const n=button(label,fn,disabled);if(kind==='jobs'&&label.startsWith('Accepter ')){const labelNode=n.querySelector('span');if(labelNode)labelNode.textContent='Voir le contrat';stage.querySelector('.integrated-value:last-child')?.append(n);}else dock.append(n);return n;}
const n=el('button','','art-hit'+(chosen?' selected':'')) as HTMLButtonElement;n.setAttribute('aria-label',label);n.title=label;n.disabled=disabled||locked||Date.now()<animationUntil;Object.assign(n.style,{left:x+'%',top:y+'%',width:w+'%',height:h+'%'});n.onclick=fn;stage.append(n);return n;};
 const route=(key:string)=>{dialog='';host.route(key);};
 function change(next:string){kind=next;dialog='';page=0;notice='';draw();}
 async function run(body:Record<string,unknown>,after?:()=>void,animate=false){if(locked||Date.now()<animationUntil)return;const revision=host.state().play.revision;locked=true;draw();try{notice=await host.mutate({...body,...((String(body.action).startsWith('game_')||String(body.action).startsWith('battle_'))?{revision}:{})});if(animate){animationStarted=Date.now();animationUntil=animationStarted+(matchMedia('(prefers-reduced-motion: reduce)').matches?10:kind==='russian'?1000:4000);}after?.();}catch(e){notice=String(e);}finally{locked=false;if(!destroyed)draw();}}
 function input(parent:HTMLElement,value:number,label:string,max:number,onChange:(v:number)=>void,min=1){const n=document.createElement('input');n.type='number';n.min=String(min);n.max=String(max);n.step='1';n.value=String(value);n.setAttribute('aria-label',label);n.onchange=()=>{onChange(Number(n.value));draw();};parent.append(n);return n;}
 function controls(parent:HTMLElement,...nodes:HTMLElement[]){const n=el('div','','art-buttons');n.append(...nodes);(parent.closest('.art-extra')?parent:dock).append(n);}
 function closeDialog(){if(dialog==='battle-result')acknowledgedResult=host.state().play.revision;dialog='';draw();}
 function refresh(){void host.refresh().catch(e=>{notice=String(e);draw();});}
 function footer(back:string,x=35,y=88,w=30,h=8){const action=()=>['expedition','tools','destinations','accessories','departure','live'].includes(back)?change(back):route(back);if(kind==='jobs'&&host.state().pending)dock.append(button('Retour en ville',action));else hit(back==='hub'?'Retour en ville':'Retour',x,y,w,h,action);}
 function text(parent:HTMLElement,value:string){parent.append(el('p',value));}
 function progress(parent:HTMLElement,value:number,max:number){const n=document.createElement('progress');n.className='art-progress';n.max=Math.max(1,max);n.value=value;n.setAttribute('aria-label',`${value} sur ${max}`);parent.append(n);}
 function draw(){
  if(destroyed)return;if(liveGameKinds.has(kind)){if(live&&liveKind===kind)live.update();else{live?.destroy();liveKind=kind;live=openLiveGame(panel,kind,{...host,route:(key)=>liveGameKinds.has(key)||['casino','games'].includes(key)?change(key):host.route(key)});}return;}live?.destroy();live=undefined;const s=host.state(),p=s.play;if(s.active&&['expedition','tools','destinations','accessories','departure'].includes(kind))kind='live';let art=kind;if(['dice','coin','rps'].includes(kind))art='games';panel.className='illustrated restored-art';panel.hidden=false;panel.style.setProperty('--art-ratio',['tavern','alley','thief','casino'].includes(art)?'2.667':'1.5');panel.replaceChildren();stage=el('div','','art-stage');const img=new Image();img.className='art-image';img.alt='';img.src='/assets/menus/'+art+'.webp';img.onload=()=>{if(!destroyed)panel.style.setProperty('--art-ratio',String(img.naturalWidth/img.naturalHeight));};stage.append(img);panel.append(stage);dock=el('div','','compact-dock');dock.setAttribute('aria-label','Actions du menu');panel.append(dock);panel.dataset.kind=kind;document.body.classList.add('illustrated-open');
  const navigation:Record<string,{title:string;items:[string,()=>void,boolean?][]}>={
   tavern:{title:'La taverne',items:[['Le tavernier',()=>route('drinks')],['Les jeux',()=>route('games')],['Le troubadour',()=>route('troubadour')],['Retour en ville',()=>route('hub')]]},
   castle:{title:'Château de IV',items:[['Tableau de bord',()=>route('dashboard')],['Podium',()=>route('podium')],[s.daily_available?'Récompense quotidienne':'Déjà récupérée',()=>void run({action:'daily'}),!s.daily_available],['Retour en ville',()=>route('hub')]]},
   alley:{title:'Ruelle sombre',items:[['Le voleur',()=>route('thief')],['Le braqueur',()=>route('robber')],['Le vigile',()=>route('guard')],['Panneau de la ruelle',()=>{dialog='record';draw();}],['Retour en ville',()=>route('hub')]]},
   arena:{title:'Arène de IV',items:[['Affronter le champion',()=>{if(p.kind==='combat'&&p.status==='active')change('combat');else{dialog='champion';draw();}},s.arena.remaining>0&&!(p.kind==='combat'&&p.status==='active')],['Affronter un ami',()=>{},true],['Retour en ville',()=>route('hub')]]},
   games:{title:'Les jeux de la taverne',items:[['Lancer de dés',()=>{choice='red';change('dice');}],['Pile ou face',()=>{choice='pile';change('coin');}],['Pierre feuille ciseaux',()=>{choice='rock';change('rps');}],['Retour à la taverne',()=>route('tavern')]]},
   thief:{title:'Le voleur',items:[['Petit larcin',()=>void run({action:'larceny'}),s.alley.larceny_remaining>0||s.alley.ban_remaining>0],['Voler un PNJ',()=>{dialog='npc';draw();},s.alley.ban_remaining>0],['Voler un joueur',()=>{},true],['Commettre un crime',()=>void run({action:'crime'}),s.alley.ban_remaining>0],['Retour à la ruelle',()=>route('alley')]]},
   expedition:{title:'Préparer une expédition',items:[...(['axe','pickaxe','spear'] as const).map((key):[string,()=>void]=>[key==='axe'?'Bûcheron':key==='pickaxe'?'Mineur':'Chasseur',()=>{tool=key;tier=s.gear[key+'_level']||1;change('tools');}]),['Cueillette',()=>{tool='hands';destination='elarwyn_foraging';change('departure');}],['Retour au monde',()=>route('world')]]},
   casino:{title:'Salle clandestine',items:[...(['blackjack','roulette','russian','slots','horses'] as const).map((k,i):[string,()=>void,boolean]=>[['Black Jack','Roulette','Roulette russe','Machine à sous','Courses'][i],()=>{choice=k==='horses'?0:'red';change(k);},!s.alley.access.valid]),['Quitter la salle',()=>route('guard')]]}
  };
  if(navigation[kind]){
   const nav=navigation[kind];stage.setAttribute('aria-label',nav.title);
   const areas:Record<string,number[][]>={
    tavern:[[2,50,33,20],[35,50,30,20],[65,50,33,20],[36,71,28,17]],
    alley:[[1,47,24,17],[26,47,23,17],[50,47,23,17],[74,47,25,17],[38,70,24,17]],
    thief:[[1,45,24,19],[26,45,23,19],[50,45,23,19],[74,45,25,19],[38,72,24,17]],
    castle:[[4,26,30,49],[35,26,30,49],[66,26,30,49],[28,78,45,13]],
    arena:[[3,28,47,48],[51,28,47,48],[29,80,42,13]],
    expedition:[[3,23,31,53],[35,23,31,53],[67,23,30,53],[35,78,30,7],[35,88,31,9]],
    games:[[4,26,30,28],[35,26,30,28],[66,26,30,28],[32,90,37,7]],
    casino:[[1,28,31,18],[34,28,31,18],[67,28,32,18],[1,57,31,18],[34,57,31,18],[67,57,32,18]]
   };
   nav.items.forEach(([label,fn,disabled],i)=>{const [x,y,w,h]=areas[kind][i];hit(label,x,y,w,h,fn,!!disabled);});
   if(kind==='games')for(let i=0;i<3;i++)hit('Jeu contre un ami indisponible',4+31*i,64,30,25,()=>{},true);
   if(dialog)drawDialog(s);if(notice&&!dialog){const n=el('div',notice,'art-notice');n.setAttribute('role','status');panel.append(n);}tick();return;
  }
  img.classList.add('compact-art');
  if(cleanMode()){panel.classList.add('clean-information');img.remove();const titles:Record<string,string>={bank:'Banque de IV',jobs:'Petites annonces',dashboard:'Tableau de bord',podium:'Podium',combat:'Combat',techniques:'Techniques',destinations:'Choisir la destination',accessories:'Accessoires',departure:'Départ de l’expédition',live:'Expédition en cours'};stage.append(menuHeading(titles[kind]));if(kind==='bank'){const header=assetSlice('/assets/menus/bank.webp',220,0,1100,250);header.classList.add('bank-original-title');stage.querySelector('.menu-heading')?.replaceWith(header);}}

  if(kind==='bank'){
   [s.balance.wallet,s.balance.bank,s.balance.wallet+s.balance.bank].forEach((v,i)=>box(21+i*28,32,13,5,`${v} Gold`,'art-mask art-wood'));
   for(const [mode,value] of [['deposit',amount],['withdraw',withdraw]] as const){
    const max=mode==='deposit'?s.balance.wallet:s.balance.bank,x=mode==='deposit'?8:66;
    const field=box(x+5,54,16,7,'','bank-amount');input(field,value,mode==='deposit'?'Montant à déposer':'Montant à retirer',max,v=>{if(mode==='deposit')amount=v;else withdraw=v;});
    const set=(v:number)=>{if(mode==='deposit')amount=v;else withdraw=v;draw();};
    hit('Diminuer '+mode,x,54,5,7,()=>set(Math.max(1,value-100)),value<=1);hit('Augmenter '+mode,x+22,54,5,7,()=>set(Math.min(max,value+100)),value>=max);
    [100,500,max].forEach((v,i)=>hit((i===2?'Tout':String(v))+' '+mode,x+i*9,63,8,6,()=>set(v),v<1));
    const q=withdrawalQuote(value,s.balance.free_withdrawal_available);box(x,69,27,4,mode==='deposit'?`Disponible : ${max} Gold`:`Frais : ${q.fee} · Reçu : ${q.received} Gold`,'art-mask art-small');
    hit(mode==='deposit'?'Confirmer le dépôt':'Confirmer le retrait',x-2,75,31,9,()=>void run({action:mode,amount:value}),!validAmount(value,max));
   }footer('hub',36,90,28,8);
  }else if(kind==='jobs'){
   if(s.pending){
    img.hidden=true;panel.classList.add('pending-contract');const n=el('section','','mission-parchment mission-active');stage.append(n);
    n.append(el('p','Contrat signé','contract-kicker'),el('h2','Mission en cours'),el('p',s.pending.job.title,'contract-title'));
    const reward=el('p',`Récompense : ${s.pending.job.reward} Gold`,'mission-reward');n.append(reward);
    const clock=el('div','','mission-clock');const hourglass=el('span','','mission-hourglass');hourglass.setAttribute('aria-hidden','true');hourglass.innerHTML='<svg viewBox="0 0 40 48" width="30" height="36" fill="none" stroke="#82591f" stroke-width="2.5"><path d="M7 3h26M7 45h26M10 4v7c0 7 10 10 10 13S10 30 10 37v7M30 4v7c0 7-10 10-10 13s10 6 10 13v7"/><path d="M12 11h16l-8 10zM12 40l8-10 8 10z" fill="#b98c3f" stroke="none"/></svg>';clock.append(hourglass,el('p','Temps restant','mission-clock-label'));
    const t=el('p','','mission-countdown');t.dataset.deadline=String(Date.now()+s.pending.remaining*1000);t.dataset.missionTimer='true';clock.append(t);n.append(clock);
    const bar=document.createElement('progress');bar.className='mission-progress';bar.max=3600;bar.value=Math.max(0,3600-s.pending.remaining);bar.setAttribute('aria-label','Progression du contrat');n.append(bar,el('p',s.pending.ready?'Mission terminée · votre récompense vous attend.':'Votre personnage accomplit le contrat.','mission-state'));
    const claim=button('Récupérer la récompense',()=>void run({action:'job_claim'}),!s.pending.ready);claim.dataset.missionClaim='true';dock.append(claim);
   }
   else{page=Math.min(page,Math.max(0,Math.ceil(s.board.jobs.length/4)-1));const jobs=pageSlice(s.board.jobs,page);for(let i=0;i<4;i++){const j=jobs[i],x=i%2===0?25:69,y=i<2?27:55;box(x,y,21,14,j?`${j.title}\n${({common:'Commun',uncommon:'Peu commun',rare:'Rare',epic:'Épique',legendary:'Légendaire'} as Record<string,string>)[j.rarity]??j.rarity} · ${j.reward} Gold\n1 heure`:'Aucune annonce','art-mask art-paper art-small');hit(j?'Accepter '+j.title:'Aucune annonce',x,y+15,21,7,()=>{if(j){selected=j.job_id;dialog='contract';draw();}},!j);const labels:Record<string,string>={common:'Commun',uncommon:'Peu commun',rare:'Rare',epic:'Épique',legendary:'Légendaire'};box(i%2===0?11:55,i<2?27:55,7,7,j?labels[j.rarity]??j.rarity:'Vide','art-mask art-small');}hit('Page précédente',30,81,10,7,()=>{page--;draw();},page===0);box(41,81,16,7,`${page+1}/${Math.max(1,Math.ceil(s.board.jobs.length/4))}`,'art-mask art-wood');hit('Page suivante',60,81,10,7,()=>{page++;draw();},(page+1)*4>=s.board.jobs.length);}footer('hub',35,90,33,7);
  }else if(kind==='dashboard'){
   box(23,22,16,8,`Niveau ${s.level}`);const lvl=box(41,24,30,5);progress(lvl,s.xp,s.xp_needed);box(73,22,16,8,`${s.xp}/${s.xp_needed} XP`);box(26,42,18,6,`${s.balance.wallet} Gold`);box(71,42,20,6,`${s.balance.bank} Gold`);const done=s.quests.filter(q=>q.progress>=q.target).length,q=box(24,59,22,8,`${done}/6 terminées`);progress(q,done,6);box(72,59,20,8,s.quests.every(q=>q.claimed)?'Récupérée':done===6?'Disponible':'En cours');hit('Quêtes quotidiennes',7,51,41,17,()=>{dialog='quests';draw();});hit('Réclamer les quêtes',52,51,41,17,()=>void run({action:'quests_claim'}),done<6||s.quests.every(q=>q.claimed));box(22,77,24,6,s.active?s.active.name:'Aucune expédition','art-mask art-small');box(67,77,25,6,`${s.stats.wins} victoires · ${s.stats.losses} défaites`,'art-mask art-small');hit('Actualiser',18,89,29,8,refresh);footer('castle',54,89,29,8);
  }else if(kind==='podium'){
   [1,0,2].forEach((rank,i)=>{const entry=s.podium[rank],x=i===0?14:i===1?42:74,y=i===1?62:67,w=i===1?17:15;box(x,y,w,5,entry?.name??'Place libre');box(x,i===1?70:73,w,5,entry?`${entry.total} Gold`:'—');});hit('Actualiser',19,88,31,8,refresh);footer('castle',54,88,35,8);
  }else if(kind==='combat'){
   const fighters=p.kind==='combat'?p.fighters??[]:[];for(let i=0;i<2;i++){const f=fighters[i],n=box(i===0?12:70,3,23,15,'','art-mask combat-fighter');text(n,f?`${f.name} · ${f.hp}/${f.max_hp} PV`:'Aucun combat');if(f)progress(n,f.hp,f.max_hp);}box(44,13,14,5,`Tour ${p.turn??0}`,'art-mask combat-turn');const logs=box(13,70,74,15,'','art-mask art-log combat-log');(p.logs??[]).slice(-4).forEach(l=>text(logs,l.replaceAll('*','')));hit('Attaque rapide',5,85,23,10,()=>void run({action:'battle_step',key:'light'}),p.status!=='active');hit('Techniques',30,85,23,10,()=>change('techniques'),p.status!=='active');hit('Se protéger',55,85,24,10,()=>void run({action:'battle_step',key:'defend'}),p.status!=='active');hit('Abandonner',80,85,16,10,()=>{dialog='abandon';draw();},p.status!=='active');box(29,95,44,4,p.status==='finished'?`${p.message} · ${p.payout??0} Gold`:'À votre tour','art-mask art-small combat-status');if(p.status==='finished'){dock.replaceChildren(button('Voir le résultat',()=>{dialog='battle-result';draw();}),button('Retour à l’arène',()=>route('arena')));}
  }else if(kind==='techniques'){
   ['light','heavy','ultimate'].forEach((key,i)=>{const sk=s.arena.skills[key],x=6+i*32;box(x,20,25,9,sk.name);box(x,58,25,11,`Puissance : ${sk.power}\n${key==='ultimate'?'Recharge : '+(p.fighters?.[0]?.ultimate_cd??0)+' tour(s)':''}`,'art-mask art-small');hit('Utiliser '+sk.name,x,69,26,11,()=>void run({action:'battle_step',key},()=>change('combat')),p.status!=='active'||key==='ultimate'&&(p.fighters?.[0]?.ultimate_cd??0)>0);});box(17,83,67,8,'Les techniques évoluent avec votre niveau.','art-mask art-small');hit('Retour au combat',30,91,39,7,()=>change('combat'));
  }
  else if(['expedition','tools','destinations','accessories','departure','live'].includes(kind))expeditions(s);
  if(['combat','techniques'].includes(kind)&&p.kind==='combat'&&p.status==='finished'&&acknowledgedResult!==p.revision)dialog='battle-result';if(dialog)drawDialog(s);dock.inert=!!dialog;dock.setAttribute('aria-hidden',String(!!dialog));if(notice&&!dialog){const n=el('div',Date.now()<animationUntil?'Animation en cours…':notice,'art-notice');n.setAttribute('role','status');panel.append(n);}tick();
 }
 function expeditions(s:Snapshot){
  if(s.active&&kind!=='live'){kind='live';draw();return;}
  if(kind==='expedition'){['axe','pickaxe','spear'].forEach((key,i)=>hit(s.catalog[key]?.name??key,3+i*32,28,30,50,()=>{tool=key;tier=s.gear[key+'_level']||1;change('tools');}));const n=box(22,79,58,7);controls(n,button('Cueillette à mains nues',()=>{tool='hands';destination='elarwyn_foraging';change('departure');}));footer('world',36,89,34,8);}
  else if(kind==='tools'){
   const max=s.gear[tool+'_level']||0;
   box(33,22,35,5,tool==='axe'?'Bûcheron':tool==='pickaxe'?'Mineur':'Chasseur','art-mask art-small');
   const art=box(22,29,56,24,'','art-mask art-wood');art.append(equipmentArt(tool,tier));
   box(29,53,42,9,s.tools[String(tier)]?.[tool]??s.catalog[tool]?.name,'art-mask art-small');
   hit('Palier précédent',3,28,14,33,()=>{tier--;draw();},tier<=1);hit('Palier suivant',83,28,14,33,()=>{tier++;draw();},tier>=max);
   [1,2,3,4,5].forEach(t=>hit(`Palier ${t}`,15+(t-1)*14,68,13,12,()=>{tier=t;draw();},t>max,tier===t));
   box(29,82,42,5,!s.owned[tool]?'Achetez cet outil au marché.':!s.owned.bag?'Un sac est nécessaire.':`Palier ${tier} possédé`,'art-mask art-small');
   hit('Choisir cet outil',23,89,49,8,()=>change('destinations'),!s.owned[tool]||!s.owned.bag||tier>max);footer('expedition',75,91,22,6);
  }else if(kind==='destinations'){
   const ds=Object.entries(s.destinations).filter(([,d])=>d.location_key===location&&d.tools.includes(tool));page=Math.max(0,Math.min(page,ds.length-1));const d=ds[page];if(d){destination=d[0];box(26,21,49,10,s.tools[String(tier)]?.[tool]??tool);box(25,48,52,20,`${d[1].name}\nNiveau ${d[1].level} · ${d[1].duration_label}`);box(23,74,59,13,`Destination ${page+1}/${ds.length} · ${location==='vorak'?'Vorak':'Elarwyn'}`,'art-mask art-wood');hit('Destination précédente',3,31,14,31,()=>{page--;draw();},page===0);hit('Destination suivante',84,31,13,31,()=>{page++;draw();},page>=ds.length-1);hit('Choisir cette destination',24,89,51,8,()=>change('accessories'),s.level<d[1].level);}else box(17,36,68,35,'Aucune destination disponible.');footer('tools',77,91,20,6);
  }else if(kind==='accessories'){
   box(25,23,52,10,s.destinations[destination]?.name??'');box(10,37,80,43,'Les accessoires ne sont pas disponibles pour le moment.\nEmplacement 1 : Aucun objet\nEmplacement 2 : Aucun objet');box(23,80,54,7,'Aucun effet supplémentaire','art-mask art-small');hit('Continuer',23,88,49,10,()=>change('departure'));footer('destinations',77,91,20,6);
  }else if(kind==='departure'){
   const d=s.destinations[destination],bare=tool==='hands';box(27,49,28,5,d?.name??'Destination indisponible','art-mask art-wood art-small');box(57,28,25,35,`Métier : ${bare?'Cueillette':tool==='axe'?'Bûcheron':tool==='pickaxe'?'Mineur':'Chasseur'}\nOutil : ${bare?'Mains nues':s.tools[String(tier)]?.[tool]}\n${bare?'Sans sac':s.bags[String(s.gear.bag_level)]?.name}\nDurée : ${d?.duration_label??''}`,'art-mask art-paper');box(29,79,43,8,'Les découvertes seront révélées durant le voyage.','art-mask art-wood art-small');hit('Lancer l’expédition',17,88,55,10,()=>void run({action:'start',key:destination,tool,...(!bare?{tool_level:tier,bag_level:s.gear.bag_level}:{}),object1:'none',object2:'none'},()=>{if(host.state().active)change('live');}),!d||s.level<d.level);footer('expedition',75,90,21,7);
  }else if(kind==='live'){
   const a=s.active;if(!a){box(13,28,75,57,'Expédition terminée. Les ressources et l’XP ont été ajoutées à votre personnage.');footer('world',48,89,41,8);return;}box(21,14,59,8,a.name);const t=box(21,43,60,8);t.dataset.deadline=String(a.ends_at*1000-offset);const prog=box(20,51,61,7);progress(prog,Math.max(0,s.server_now-a.started_at),a.ends_at-a.started_at);box(20,63,28,17,Object.entries(a.revealed_loot).map(([k,v])=>`${k} ×${v}`).join('\n')||'Aucune ressource découverte','art-mask art-paper art-small');box(54,63,27,17,a.log.slice(-3).map(l=>`${l.resource_name} +${l.quantity}`).join('\n')||'Le voyage commence…','art-mask art-paper art-small');hit('Actualiser',14,86,35,10,refresh);footer('world',51,86,37,10);
  }
 }
 function drawDialog(s:Snapshot){const n=el('div','','art-extra');n.setAttribute('role','dialog');n.setAttribute('aria-modal','true');stage.append(n);
  if(dialog==='battle-result'){
   panel.append(n);n.classList.add('battle-result');n.setAttribute('aria-label','Résultat du combat');
   const won=s.play.outcome==='victory'||(!s.play.outcome&&s.play.message?.startsWith('Victoire')),fighter=s.play.fighters?.[1];
   const title=won?'Victoire !':'Défaite',heading=el('h2','','compact-button result-title result-banner'),ornament=decorateButton(document.createElement('button'),title);heading.append(...Array.from(ornament.childNodes));n.classList.toggle('victory',!!won);n.append(el('span',won?'⚜':'⚔','result-emblem'),heading,el('p',won?`Bravo, ${s.name} ! Vous avez vaincu ${fighter?.name??'le champion'}.`:`Courage, ${s.name}. ${fighter?.name??'Le champion'} remporte ce combat.`),el('p',won?'La foule acclame votre victoire !':'Revenez plus fort pour prendre votre revanche.'));
   const summary=el('dl','','result-summary');for(const [label,value] of [['Gold reçus',`${s.play.payout??0} Gold`],['Tours',String(s.play.turn??0)],['PV restants',`${s.play.fighters?.[0]?.hp??0} / ${s.play.fighters?.[0]?.max_hp??0}`]])summary.append(el('dt',label),el('dd',value));n.append(summary);
   controls(n,button('Voir les attaques',closeDialog),button('Retour à l’arène',()=>{acknowledgedResult=s.play.revision;route('arena');}));
  }
  else if(dialog==='number'){text(n,'Choisissez un numéro de 0 à 36');input(n,number,'Numéro',36,v=>number=v,0);controls(n,button('Confirmer',closeDialog,!Number.isInteger(number)||number<0||number>36));}
  else if(dialog==='contract'){
   n.classList.add('contract-backdrop');n.setAttribute('aria-label','Contrat de mission');
   const paper=el('article','','mission-parchment');n.append(paper);
   paper.append(el('span','Petites annonces · Altherya','contract-kicker'),el('h2','Contrat de mission'));
   const j=s.board.jobs.find(j=>j.job_id===selected);
   paper.append(el('h3',j?.title??'Cette annonce n’est plus disponible','contract-title'));
   if(j){
    const terms=el('dl','','contract-terms');
    for(const [label,value] of [['Aventurier',s.name],['Durée','1 heure après signature'],['Rémunération',`${j.reward} Gold`],['Rareté',({common:'Commun',uncommon:'Peu commun',rare:'Rare',epic:'Épique',legendary:'Légendaire'} as Record<string,string>)[j.rarity]??j.rarity]])terms.append(el('dt',label),el('dd',value));
    paper.append(terms,el('p','En signant, vous acceptez cette mission. À la fin du délai, revenez aux petites annonces pour récupérer votre récompense.','contract-clause'));
    const signature=el('div','','contract-signature');signature.append(el('span','Signature de l’aventurier'),el('strong',s.name));paper.append(signature);
    controls(paper,button(locked?'Signature en cours…':'Signer et commencer',()=>void run({action:'job_accept',key:selected,batch:s.board.batch_id},()=>{if(host.state().pending)dialog='';}),!!s.pending));
   }
   controls(paper,button('Revenir aux annonces',closeDialog));
   for(const child of Array.from(stage.children)){if(child!==n&&(child instanceof HTMLElement))child.inert=true;}
   requestAnimationFrame(()=>{if(n.isConnected){n.querySelector<HTMLButtonElement>('button:not(:disabled)')?.focus({preventScroll:true});n.scrollTop=0;}});
  }
  else if(dialog==='champion'){text(n,`Champion ${s.arena.champion_level} · Classement : ${s.arena.rating}`);text(n,'Mise facultative : 0 à 500 Gold');input(n,wager,'Mise du combat',Math.min(500,s.balance.wallet),v=>wager=v,0);controls(n,button('Commencer le combat',()=>void run({action:'battle_start',wager},()=>{if(host.state().play.kind==='combat'&&host.state().play.status==='active')change('combat');}),!Number.isInteger(wager)||wager<0||wager>500||wager>s.balance.wallet));}
  else if(dialog==='abandon'){text(n,'Abandonner ce combat ? La mise sera perdue.');controls(n,button('Abandonner',()=>void run({action:'battle_step',key:'abandon'},()=>{dialog='';})));}
  else if(dialog==='npc'){text(n,'Choisissez votre cible');controls(n,...s.alley.npc_targets.map(t=>button(t.name,()=>void run({action:'npc_theft',key:t.key},()=>{dialog='';}))));}
  else if(dialog==='record'){text(n,`Réputation : ${s.alley.reputation.label}`);Object.entries(s.alley.record).filter(([k])=>k!=='user_id').forEach(([k,v])=>text(n,`${({theft_success:'Vols réussis',theft_fail:'Vols ratés',crimes_success:'Crimes réussis',heists_success:'Braquages réussis',gold_stolen:'Gold volé',loot:'Butin',caught:'Arrestations'} as Record<string,string>)[k]??k} : ${v}`));}
  else if(dialog==='quests'){text(n,'Quêtes quotidiennes');s.quests.forEach(q=>text(n,`${q.label} · ${q.progress}/${q.target}`));text(n,`Récompense : ${s.quest_reward.gold} Gold + ${s.quest_reward.xp} XP`);}if(!['contract','battle-result'].includes(dialog))controls(n,button('Retour',closeDialog));
 }
 function tick(){panel.querySelectorAll<HTMLElement>('[data-deadline]').forEach(n=>{const seconds=Math.max(0,Math.ceil((Number(n.dataset.deadline)-Date.now())/1000));if(n.dataset.missionTimer){n.textContent=seconds>0?`${String(Math.floor(seconds/3600)).padStart(2,'0')} : ${String(Math.floor(seconds%3600/60)).padStart(2,'0')} : ${String(seconds%60).padStart(2,'0')}`:'Terminée';const bar=panel.querySelector<HTMLProgressElement>('.mission-progress');if(bar)bar.value=3600-seconds;if(seconds===0){const claim=panel.querySelector<HTMLButtonElement>('[data-mission-claim]');if(claim&&!locked)claim.disabled=false;const message=panel.querySelector('.mission-state');if(message)message.textContent='Mission terminée · votre récompense vous attend.';}}else n.textContent=timeLabel(seconds);});if(animationUntil&&Date.now()>=animationUntil){animationUntil=0;draw();}}
 const clock=window.setInterval(tick,100);panel.onkeydown=e=>{if(e.key==='Escape'&&!locked){e.preventDefault();dialog?closeDialog():host.close();}if(e.key==='Tab'){const root=panel.querySelector('.art-extra')??panel,nodes=Array.from(root.querySelectorAll<HTMLElement>('button:not(:disabled),input:not(:disabled)')),first=nodes[0],last=nodes.at(-1);if(e.shiftKey&&document.activeElement===first){e.preventDefault();last?.focus();}else if(!e.shiftKey&&document.activeElement===last){e.preventDefault();first?.focus();}}};draw();panel.querySelector<HTMLElement>('button')?.focus();return {destroy(){destroyed=true;live?.destroy();document.body.classList.remove('illustrated-open');clearInterval(clock);panel.onkeydown=null;},update(){offset=host.state().server_now*1000-Date.now();if(document.activeElement instanceof HTMLInputElement&&panel.contains(document.activeElement))return;if(!locked&&Date.now()>=animationUntil)draw();}};
}
