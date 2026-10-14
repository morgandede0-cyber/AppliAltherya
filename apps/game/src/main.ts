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
function hud(){if(!state)return;$('hud').textContent=`${state.name} · Niv. ${state.level} · XP ${state.xp}/${state.xp_needed} · ${state.balance.wallet} Gold · Banque ${state.balance.bank} · Mode test`;$('objective').textContent=scenes[current].name;}
function clearCommerce(){service?.destroy();service=undefined;commerce?.destroy();commerce=undefined;panel.className='';panel.onkeydown=null;panel.replaceChildren();panel.removeAttribute('data-kind');panel.removeAttribute('aria-busy');panel.removeAttribute('aria-label');panel.style.removeProperty('--art-ratio');}
function close(){if(panel.dataset.kind==='tutorial'&&!state.tutorial.completed)return;if(!busy){clearCommerce();panel.hidden=true;}}
function closeService(){close();if(current!=='hub'&&current!=='market')void navigate(scenes[current].parent??'hub');}
function show(title:string,text:string){clearCommerce();panel.className='native-welcome';panel.replaceChildren();const h=document.createElement('h2');h.textContent=title;const p=document.createElement('p');p.textContent=text;panel.append(h,p);panel.hidden=false;}
function button(label:string,fn:()=>void,disabled=false){const b=document.createElement('button');b.textContent=label;b.disabled=disabled;b.onclick=()=>{if(!busy){chime();fn();}};return b;}
function actions(...buttons:HTMLButtonElement[]){const a=document.createElement('div');a.className='actions';a.append(...buttons);panel.append(a);}
function row(text:string,...buttons:HTMLButtonElement[]){const r=document.createElement('div');r.className='item';const p=document.createElement('span');p.textContent=text;r.append(p,...buttons);panel.append(r);}
function end(back:()=>void=close){actions(button('Retour',back));}
async function refresh(){const version=stateVersion;const result=await request();if(version!==stateVersion)return;state=result.state;if(!state.admin)document.querySelector('.admin-hub-button')?.remove();hud();commerce?.update();service?.update();}
function serviceMenu(kind:string,location='elarwyn',title=''){if(kind==='tutorial'){void tutorialMenu(true);return;}clearCommerce();const host={refresh,state:()=>state,close:closeService,route:(key:string)=>{if(key==='tutorial'){void tutorialMenu(true);return;}if(key.startsWith('market:')){commerceMenu(key.slice(7) as CommerceMode);return;}if(key in scenes){void navigate(key as SceneId);return;}if(key==='drinks'){void navigate('barman');return;}if(illustratedKinds.has(key)||refinedKinds.has(key)||['profile','journal','story','world'].includes(key))serviceMenu(key,location);else void navigate(key as SceneId);},mutate:async (body:Record<string,unknown>)=>{if(busy)throw new Error('Opération en cours.');stateVersion++;busy=true;try{const r=await request(body);state=r.state;hud();return r.message;}catch(e){await refresh().catch(()=>{});throw e;}finally{busy=false;}}};if(refinedKinds.has(kind)){service=openRefined(panel,kind,{...host,close:kind==='market'?()=>void navigate('hub'):['guard','robber'].includes(kind)?close:closeService});return;}if(illustratedKinds.has(kind)){service=openIllustrated(panel,kind,host,location);return;}service=openService(panel,kind,{state:()=>state,close:closeService,route:key=>{if(key==='tutorial'){void tutorialMenu(true);return;}if(['profile','journal','jobs','story','expedition'].includes(key))serviceMenu(key);else void navigate(key as SceneId);},mutate:async body=>{stateVersion++;busy=true;try{const r=await request(body);state=r.state;hud();return r.message;}catch(e){try{state=(await request()).state;hud();}catch{}throw e;}finally{busy=false;}}},location,title);}
async function tutorialMenu(replay=false){
 if(busy)return;
 const mutate=async(body:Record<string,unknown>)=>{if(busy)throw new Error('Opération en cours.');stateVersion++;busy=true;try{const r=await request(body);state=r.state;hud();return r.message;}finally{busy=false;}};
 if(replay){try{await mutate({action:'tutorial_replay'});}catch(e){notify(String(e));return;}}
 clearCommerce();service=openTutorial(panel,{state:()=>state,mutate,notify,done:()=>{close();void navigate('hub');}});
}
function enterGame(){close();if(!state.tutorial.completed||state.tutorial.replay)void tutorialMenu();}
function adminMenu(){if(!state.admin)return;clearCommerce();service=openAdmin(panel,{close:()=>{close();void navigate('hub');},refresh,allowed:()=>state.admin});}
function profile(){serviceMenu('profile');}
function market(){serviceMenu('market');}
function commerceMenu(mode:CommerceMode){clearCommerce();commerce=openCommerce(panel,mode,{state:()=>state,sound:()=>chime(),exit:market,back:market,switchMode:commerceMenu,trade:async body=>{stateVersion++;busy=true;try{const r=await request(body);state=r.state;hud();return r.message;}catch(e){try{state=(await request()).state;hud();}catch{}throw e;}finally{busy=false;}}});}
function shop(){commerceMenu('buy');}
function sales(){commerceMenu('sell');}
function world(){serviceMenu('world');}
function storyShop(){commerceMenu('story');}
function jobs(){serviceMenu('jobs');}
function unavailable(title:string){serviceMenu('unavailable','elarwyn',title);}
function interact(id:string){if(!panel.hidden||busy||$('scene-stage').getAttribute('aria-busy')==='true')return;if(id.startsWith('scene:')){void navigate(id.slice(6) as SceneId);return;}const handlers:Record<string,()=>void>={admin:adminMenu,'market:story':storyShop,'market:buy':shop,'market:sell':sales,profile,world,jobs,gazette:()=>serviceMenu('journal')};(handlers[id]??(()=>unavailable(scenes[current].name)))();}
function fitScene(){const stage=$('scene-stage'),ratio=Number(stage.dataset.ratio)||1.777,w=Math.min(innerWidth,innerHeight*ratio);stage.style.width=w+'px';stage.style.height=w/ratio+'px';}
let navigationVersion=0;
async function navigate(id:SceneId){const scene=scenes[id];if(!scene||busy)return;const version=++navigationVersion;close();current=id;hud();const stage=$('scene-stage');stage.classList.add('changing');stage.setAttribute('aria-busy','true');const img=new Image();img.alt=scene.name;try{await new Promise<void>((resolve,reject)=>{const timeout=setTimeout(()=>reject(new Error('Chargement trop long : '+scene.name)),15000);img.onload=()=>{clearTimeout(timeout);resolve();};img.onerror=()=>{clearTimeout(timeout);reject(new Error('Décor inaccessible : '+scene.image));};img.src='/assets/scenes/'+scene.image;});if(version!==navigationVersion)return;stage.replaceChildren(img);stage.dataset.scene=id;const spotContainer=id==='hub'?document.createElement('div'):stage;if(id==='hub'){spotContainer.className='hub-toolbar';stage.append(spotContainer);}stage.dataset.ratio=String(img.naturalWidth/img.naturalHeight);fitScene();for(const spot of sceneMenus[id]?[]:scene.spots){const b=button(spot.label,()=>interact(spot.action));b.className='hotspot'+(spot.embedded?' embedded':'');b.setAttribute('aria-label',spot.label);b.title=spot.label;b.style.left=spot.x+'%';b.style.top=spot.y+'%';b.style.width=spot.w+'%';b.style.height=spot.h+'%';const span=document.createElement('span');span.textContent=spot.label;b.replaceChildren(span);if(spot.asset)skinButton(b,spot.asset,spot.label);spotContainer.append(b);}if(id==='hub'&&state.admin){const admin=menuButton('Admin',()=>interact('admin'));admin.classList.add('admin-hub-button');stage.append(admin);}$('scene-copy').hidden=true;$('scene-copy').textContent='';if(['robber','guard'].includes(id)){const bar=document.createElement('div');bar.className='scene-actionbar';bar.append(ornamentButton(id==='robber'?'Planifier un braquage':'Parler au vigile',()=>serviceMenu(id)),ornamentButton('Retour à la ruelle',()=>void navigate('alley')));stage.append(bar);}else if(sceneMenus[id])serviceMenu(sceneMenus[id]!,id==='vorak'?'vorak':'elarwyn');}catch(e){show('Chargement interrompu',String(e));end();}finally{if(version===navigationVersion){stage.classList.remove('changing');stage.setAttribute('aria-busy','false');}}}
$('game').innerHTML='<div id="scene-stage"></div><div id="scene-copy"></div>';
watchMenuSurface(panel,$('scene-stage'));
window.addEventListener('resize',fitScene);
window.addEventListener('keydown',e=>{if(e.defaultPrevented||commerce||e.target instanceof HTMLInputElement)return;if(e.key==='Escape'){if(service&&!['guard','robber'].includes(current))closeService();else close();}if(e.key.toLowerCase()==='i'&&panel.hidden&&!busy&&$('scene-stage').getAttribute('aria-busy')!=='true')profile();});
let starting=false;
async function startGame(){if(starting)return;starting=true;try{await refresh();if(isDiscordActivity()){show('Connexion à Discord','Identification de votre personnage…');await connect();await refresh();if(!state.discord)throw new Error('La connexion Discord a été autorisée, mais la session n’a pas été conservée. Vérifiez que le correctif des cookies Activity est déployé.');}if(state.tutorial.discord_required&&!state.tutorial.discord_verified){show('Connexion Discord requise','Ouvrez le jeu depuis Discord pour retrouver votre personnage et votre progression.');actions(button('Réessayer',()=>void startGame()));return;}await navigate('hub');enterGame();window.setInterval(()=>{if(!busy)void refresh().catch(()=>notify('Connexion au serveur interrompue.'));},15000);}catch(e){show('Connexion interrompue',connectionError(e));actions(button('Réessayer',()=>void startGame()));}finally{starting=false;}}
await startGame();

import './ui/polished-menus.css';

import "./ui/native-menus.css";

import './ui/alignment.css';

import './ui/menu-framework.css';

import './ui/native-all-menus.css';

import './ui/arena-menu.css';

import './ui/tutorial.css';
