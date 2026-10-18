import {openCasinoRoom} from './ui/casino-room';
import {openAlleyNpc,alleyNpcKinds} from './ui/alley-npc';
import {openRealmMenu,realmKinds} from './ui/realm-menu';
import {openUpdateJournal} from './ui/update-journal';
import {openCampaignMenu} from './ui/campaign-menu';
import {createQuestTracker} from './ui/quest-tracker';
import {attachHubLife} from './world/hub-life';
import {launchScreen,preloadLaunchAssets} from './ui/launch-screen';
import {sceneViewport} from './ui/responsive';
import {hubAssets,uiAsset} from './ui/assets';
import {isDiscordActivity,connectionError} from './discord/context';
import {openAdmin} from './ui/admin';
import {menuButton} from './ui/menu-framework';
import {openTutorial} from './ui/tutorial';
import {watchMenuSurface} from './ui/menu-surface';
import {openRefined,refinedKinds} from './ui/refined-menus';
import {ornamentButton} from './ui/menu-kit';
import {scenes,sceneMenus,type SceneId} from './world/scenes';
import {request,type Snapshot} from './activity';
import {chime} from './audio/sound';
import {connect} from './discord/session';
import './ui/style.css';
import {openCommerce} from './ui/commerce';
import {openService} from './ui/services';
import {openIllustrated,illustratedKinds} from './ui/illustrated';
import {skinButton} from './ui/assets';
import type {CommerceMode} from './ui/commerce-model';
const $=(id:string)=>document.getElementById(id)!;
const panel=$('panel');let commerce:ReturnType<typeof openCommerce>|undefined;let service:ReturnType<typeof openService>|undefined;let state!:Snapshot,current:SceneId='hub',busy=false,timer:number,stateVersion=0;
function notify(message:string){$('toast').textContent=message;clearTimeout(timer);timer=window.setTimeout(()=>$('toast').textContent='',6000);}
const hubMotionControl=document.createElement('button');hubMotionControl.id='hub-motion-toggle';hubMotionControl.type='button';hubMotionControl.textContent='Animations';hubMotionControl.disabled=true;
const questTracker=createQuestTracker({route:key=>{if(key.startsWith('market:')){commerceMenu(key.slice(7) as CommerceMode);return;}serviceMenu(key);}});
const dailyQuestTracker=createQuestTracker({claimDaily:claimDailyQuests,route:key=>{if(key.startsWith('market:')){commerceMenu(key.slice(7) as CommerceMode);return;}serviceMenu(key);}},true);
async function claimDailyQuests(){if(busy)throw new Error('Opération en cours.');stateVersion++;busy=true;try{const r=await request({action:'quests_claim'});state=r.state;hud();return r.message;}catch(e){await refresh().catch(()=>{});throw e;}finally{busy=false;}}
function hud(){if(!state)return;questTracker.update(state);dailyQuestTracker.update(state);const name=document.createElement('span');name.className='hud-name';name.textContent=state.name;const details=document.createElement('span');details.className='hud-details';for(const [text,cls] of [[`Niv. ${state.level}`,'hud-level'],[`XP ${state.xp}/${state.xp_needed}`,'hud-xp'],[`${state.balance.wallet} Gold`,'hud-gold'],[`Banque ${state.balance.bank}`,'hud-bank']]){const item=document.createElement('span');item.className=cls;item.textContent=text;details.append(item);}const identity=document.createElement('span');identity.className='hud-identity';identity.append(name);if(current==='hub')identity.append(hubMotionControl);$('hud').replaceChildren(identity,details);$('objective').textContent=scenes[current].name;}
function clearCommerce(){service?.destroy();service=undefined;commerce?.destroy();commerce=undefined;panel.className='';panel.onkeydown=null;panel.replaceChildren();panel.removeAttribute('data-kind');panel.removeAttribute('aria-busy');panel.removeAttribute('aria-label');panel.style.removeProperty('--art-ratio');}
function close(){if(panel.dataset.kind==='tutorial'&&!state.tutorial.completed)return;if(!busy){clearCommerce();panel.hidden=true;}}
function closeService(){close();if(current!=='hub'&&current!=='market')void navigate(scenes[current].parent??'hub');}
function show(title:string,text:string){clearCommerce();panel.className='native-welcome';panel.replaceChildren();const h=document.createElement('h2');h.textContent=title;const p=document.createElement('p');p.textContent=text;panel.append(h,p);panel.hidden=false;}
function button(label:string,fn:()=>void,disabled=false){const b=document.createElement('button');b.textContent=label;b.disabled=disabled;b.onclick=()=>{if(!busy){chime();fn();}};return b;}
function actions(...buttons:HTMLButtonElement[]){const a=document.createElement('div');a.className='actions';a.append(...buttons);panel.append(a);}
function row(text:string,...buttons:HTMLButtonElement[]){const r=document.createElement('div');r.className='item';const p=document.createElement('span');p.textContent=text;r.append(p,...buttons);panel.append(r);}
function end(back:()=>void=close){actions(button('Retour',back));}
async function refresh(){const version=stateVersion;const result=await request();if(version!==stateVersion)return;state=result.state;if(!state.admin)document.querySelector('.admin-hub-button')?.remove();hud();commerce?.update();service?.update();}
function serviceMenu(kind:string,location='elarwyn',title=''){if(kind==='market'){market();return;}if(kind==='tutorial'){void tutorialMenu(true);return;}clearCommerce();const host={refresh,state:()=>state,close:closeService,route:(key:string)=>{if(key==='tutorial'){void tutorialMenu(true);return;}if(key.startsWith('market:')){commerceMenu(key.slice(7) as CommerceMode);return;}if(key in scenes){void navigate(key as SceneId);return;}if(key==='drinks'){void navigate('barman');return;}if(illustratedKinds.has(key)||refinedKinds.has(key)||['campaign','profile','journal','story','world'].includes(key))serviceMenu(key,location);else void navigate(key as SceneId);},mutate:async (body:Record<string,unknown>)=>{if(busy)throw new Error('Opération en cours.');stateVersion++;busy=true;try{const r=await request(body);state=r.state;hud();return r.message;}catch(e){await refresh().catch(()=>{});throw e;}finally{busy=false;}}};if(kind==='casino'){service=openCasinoRoom(panel,host);return;}if(alleyNpcKinds.has(kind)){service=openAlleyNpc(panel,kind,host);return;}if(realmKinds.has(kind)&&kind!=='bank'){service=openRealmMenu(panel,kind,host);return;}if(kind==='campaign'){service=openCampaignMenu(panel,host);return;}if(refinedKinds.has(kind)){service=openRefined(panel,kind,{...host,close:kind==='market'?()=>void navigate('hub'):['guard','robber'].includes(kind)?close:closeService});return;}if(illustratedKinds.has(kind)){service=openIllustrated(panel,kind,host,location);return;}service=openService(panel,kind,host,location,title);}

async function tutorialMenu(replay=false){
 if(busy)return;
 const mutate=async(body:Record<string,unknown>)=>{if(busy)throw new Error('Opération en cours.');stateVersion++;busy=true;try{const r=await request(body);state=r.state;hud();return r.message;}finally{busy=false;}};
 if(replay){try{await mutate({action:'tutorial_replay'});}catch(e){notify(String(e));return;}}
 clearCommerce();service=openTutorial(panel,{state:()=>state,mutate,notify,done:()=>{close();void navigate('hub');}});
}
function enterGame(){close();if(!state.tutorial.completed||state.tutorial.replay)void tutorialMenu();}
function adminMenu(){if(!state.admin)return;clearCommerce();service=openAdmin(panel,{close:()=>{close();void navigate('hub');},refresh,allowed:()=>state.admin});}
function updatesMenu(){clearCommerce();service=openUpdateJournal(panel,close);}
function profile(){serviceMenu('profile');}
function market(){commerceMenu('buy');}
function commerceMenu(mode:CommerceMode){clearCommerce();commerce=openCommerce(panel,mode,{state:()=>state,sound:()=>chime(),exit:()=>void navigate('hub'),back:()=>void navigate('hub'),switchMode:commerceMenu,trade:async body=>{stateVersion++;busy=true;try{const r=await request(body);state=r.state;hud();return r.message;}catch(e){try{state=(await request()).state;hud();}catch{}throw e;}finally{busy=false;}}});}
function shop(){commerceMenu('buy');}
function sales(){commerceMenu('sell');}
function world(){serviceMenu('world');}
function storyShop(){commerceMenu('story');}
function jobs(){serviceMenu('jobs');}
function unavailable(title:string){serviceMenu('unavailable','elarwyn',title);}
function interact(id:string){if(!panel.hidden||busy||$('scene-stage').getAttribute('aria-busy')==='true')return;if(id.startsWith('scene:')){void navigate(id.slice(6) as SceneId);return;}const handlers:Record<string,()=>void>={admin:adminMenu,'market:story':storyShop,'market:buy':shop,'market:sell':sales,profile,world,jobs,gazette:updatesMenu};(handlers[id]??(()=>unavailable(scenes[current].name)))();}
function fitScene(){const stage=$('scene-stage'),view=sceneViewport(innerWidth,innerHeight,Number(stage.dataset.ratio)||1.777);document.body.classList.toggle('portrait-view',view.portrait);stage.style.width=view.width+'px';stage.style.height=view.height+'px';}
let navigationVersion=0,hubLife:(()=>void)|undefined;
async function navigate(id:SceneId,failHard=false){const scene=scenes[id];if(!scene||busy)return;const version=++navigationVersion;close();current=id;hud();const stage=$('scene-stage');stage.classList.add('changing');stage.setAttribute('aria-busy','true');const img=new Image();img.alt=scene.name;try{await new Promise<void>((resolve,reject)=>{const timeout=setTimeout(()=>reject(new Error('Chargement trop long : '+scene.name)),15000);img.onload=()=>{clearTimeout(timeout);resolve();};img.onerror=()=>{clearTimeout(timeout);reject(new Error('Décor inaccessible : '+scene.image));};img.src='/assets/scenes/'+scene.image;});if(version!==navigationVersion)return;hubLife?.();hubLife=undefined;stage.replaceChildren(img);stage.dataset.scene=id;$('game').style.setProperty('--scene-background',`url('/assets/scenes/${scene.image}')`);const spotContainer=id==='hub'?document.createElement('div'):stage;if(id==='hub'){spotContainer.className='hub-toolbar';stage.append(spotContainer);}stage.dataset.ratio=String(img.naturalWidth/img.naturalHeight);fitScene();for(const spot of sceneMenus[id]?[]:scene.spots){const b=button(spot.label,()=>interact(spot.action));b.className='hotspot'+(spot.embedded?' embedded':'');b.setAttribute('aria-label',spot.label);b.title=spot.label;b.style.left=spot.x+'%';b.style.top=spot.y+'%';b.style.width=spot.w+'%';b.style.height=spot.h+'%';const span=document.createElement('span');span.textContent=spot.label;b.replaceChildren(span);if(spot.asset)skinButton(b,spot.asset,spot.label);spotContainer.append(b);}if(id==='hub'&&state.admin){const admin=menuButton('Admin',()=>interact('admin'));admin.classList.add('admin-hub-button');stage.append(admin);}if(id==='hub')hubLife=attachHubLife(stage,panel,hubMotionControl);$('scene-copy').hidden=true;$('scene-copy').textContent='';if(sceneMenus[id])serviceMenu(sceneMenus[id]!,id==='vorak'?'vorak':'elarwyn');}catch(e){if(failHard)throw e;show('Chargement interrompu',String(e));end();}finally{if(version===navigationVersion){stage.classList.remove('changing');stage.setAttribute('aria-busy','false');}}}
$('game').innerHTML='<div id="scene-stage"></div><div id="scene-copy"></div>';
watchMenuSurface(panel,$('scene-stage'));
window.addEventListener('resize',fitScene);
window.visualViewport?.addEventListener('resize',fitScene);
fitScene();
window.addEventListener('keydown',e=>{if(starting||startup||e.defaultPrevented)return;if(commerce){if(e.key==='Escape')panel.onkeydown?.call(panel,e);return;}if(e.target instanceof HTMLInputElement)return;if(e.key==='Escape'){if(service&&!['guard','robber'].includes(current))closeService();else close();}if(e.key.toLowerCase()==='i'&&panel.hidden&&!busy&&$('scene-stage').getAttribute('aria-busy')!=='true')profile();});
let starting=false,startup:ReturnType<typeof launchScreen>|undefined;
async function startGame(){
 if(starting)return;starting=true;startup?.destroy();startup=launchScreen(()=>void startGame());
 try{
  const discord=isDiscordActivity();if(!discord)startup.local();
  startup.update(3,'Connexion au royaume…',0);await refresh();
  if(discord){await connect(stage=>{const steps={ready:[10,'Connexion à Discord…'],authorize:[20,'Autorisation Discord…'],server:[35,'Vérification du personnage…'],authenticate:[50,'Validation de la session…']} as const;const [progress,label]=steps[stage];startup?.update(progress,label,progress<35?0:1);});await refresh();if(!state.discord)throw new Error('La connexion Discord a été autorisée, mais la session n’a pas été conservée. Vérifiez que le correctif des cookies Activity est déployé.');}
  if(state.tutorial.discord_required&&!state.tutorial.discord_verified)throw new Error('Connexion Discord requise. Ouvrez le jeu depuis Discord pour retrouver votre personnage et votre progression.');
  startup.update(65,'Personnage retrouvé · Préparation du monde…',2);
  await preloadLaunchAssets(['/assets/scenes/hub-clean.webp','/assets/launch/royal-crest.png','/assets/faithful/ornaments.png','/assets/faithful/tavern-frame.png','/assets/faithful/jobs-frame.png','/assets/faithful/tavern-scenes.png','/assets/faithful/job-scenes.png',...Object.values(hubAssets).map(uiAsset)],(done,total)=>startup?.update(65+Math.round(done/total*30),'Chargement de la cité…',2));
  await navigate('hub',true);startup.update(100,'Bienvenue à Legacy',3);startup.destroy();startup=undefined;enterGame();
  window.setInterval(()=>{if(!busy)void refresh().catch(()=>notify('Connexion au serveur interrompue.'));},15000);
 }catch(e){startup?.error(connectionError(e));}finally{starting=false;}
}
await startGame();

import './ui/polished-menus.css';

import "./ui/native-menus.css";

import './ui/alignment.css';

import './ui/menu-framework.css';

import './ui/native-all-menus.css';

import './ui/arena-menu.css';

import './ui/tutorial.css';

import './ui/launch-responsive.css';
