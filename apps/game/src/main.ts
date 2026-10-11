import {mountExploration} from './world/exploration';
import {interiors,type Encounter} from './world/interiors';
import {watchMenuSurface} from './ui/menu-surface';
import {openRefined,refinedKinds} from './ui/refined-menus';
import {trapMenu} from './ui/menu-kit';
import {scenes,type SceneId} from './world/scenes';
import {request,type Snapshot} from './activity';
import {chime} from './audio/sound';
import {connect} from './discord/session';
import './ui/style.css';
import {openCommerce} from './ui/commerce';
import {openService} from './ui/services';
import {openIllustrated,illustratedKinds} from './ui/illustrated';
import type {CommerceMode} from './ui/commerce-model';
const $=(id:string)=>document.getElementById(id)!;
const panel=$('panel');let commerce:ReturnType<typeof openCommerce>|undefined;let service:ReturnType<typeof openService>|undefined;let state!:Snapshot,current:SceneId='hub',busy=false,timer:number,stateVersion=0;
function notify(message:string){$('toast').textContent=message;clearTimeout(timer);timer=window.setTimeout(()=>$('toast').textContent='',6000);}
function hud(){if(!state)return;const hud=$('hud');hud.replaceChildren();const name=document.createElement('strong');name.textContent=state.name;const level=document.createElement('span');level.textContent=`Niv. ${state.level}`;const gold=document.createElement('span');gold.className='hud-gold';gold.textContent=`${state.balance.wallet.toLocaleString('fr-FR')} Gold`;const track=document.createElement('div');track.className='hud-xp';track.title=`XP ${state.xp} / ${state.xp_needed}`;const fill=document.createElement('span');fill.style.width=Math.min(100,state.xp/Math.max(1,state.xp_needed)*100)+'%';track.append(fill);hud.append(name,level,gold,track);$('objective').textContent=scenes[current].name;}
function clearCommerce(){service?.destroy();service=undefined;commerce?.destroy();commerce=undefined;panel.className='';panel.onkeydown=null;panel.replaceChildren();panel.removeAttribute('data-kind');panel.removeAttribute('aria-busy');panel.removeAttribute('aria-label');panel.style.removeProperty('--art-ratio');}
function close(){if(!busy){clearCommerce();panel.hidden=true;}}
function closeService(){close();}
function show(title:string,text:string){clearCommerce();panel.replaceChildren();const h=document.createElement('h2');h.textContent=title;const p=document.createElement('p');p.textContent=text;panel.append(h,p);panel.hidden=false;}
function button(label:string,fn:()=>void,disabled=false){const b=document.createElement('button');b.textContent=label;b.disabled=disabled;b.onclick=()=>{if(!busy){chime();fn();}};return b;}
function actions(...buttons:HTMLButtonElement[]){const a=document.createElement('div');a.className='actions';a.append(...buttons);panel.append(a);}
function end(back:()=>void=close){actions(button('Retour',back));}
async function refresh(){const version=stateVersion;const result=await request();if(version!==stateVersion)return;state=result.state;hud();commerce?.update();service?.update();}
async function act(body:Record<string,unknown>,after:()=>void){if(busy)return;stateVersion++;busy=true;panel.setAttribute('aria-busy','true');panel.querySelectorAll('button').forEach(b=>b.disabled=true);try{const r=await request(body);state=r.state;notify(r.message);hud();}catch(e){notify(String(e));}finally{busy=false;panel.setAttribute('aria-busy','false');after();}}
function serviceMenu(kind:string,location='elarwyn',title=''){clearCommerce();const host={refresh,state:()=>state,close:closeService,route:(key:string)=>{if(key.startsWith('market:')){commerceMenu(key.slice(7) as CommerceMode);return;}if(key in scenes){void navigate(key as SceneId);return;}if(key==='drinks'){void navigate('barman');return;}if(illustratedKinds.has(key)||refinedKinds.has(key)||['profile','journal','story','world'].includes(key))serviceMenu(key,location);else void navigate(key as SceneId);},mutate:async (body:Record<string,unknown>)=>{if(busy)throw new Error('Opération en cours.');stateVersion++;busy=true;try{const r=await request(body);state=r.state;hud();return r.message;}catch(e){await refresh().catch(()=>{});throw e;}finally{busy=false;}}};if(refinedKinds.has(kind)){service=openRefined(panel,kind,{...host,close:kind==='market'?close:['guard','robber'].includes(kind)?close:closeService});return;}if(illustratedKinds.has(kind)){service=openIllustrated(panel,kind,host,location);return;}service=openService(panel,kind,{state:()=>state,close:closeService,route:key=>{if(['profile','journal','jobs','story','expedition'].includes(key))serviceMenu(key);else void navigate(key as SceneId);},mutate:async body=>{stateVersion++;busy=true;try{const r=await request(body);state=r.state;hud();return r.message;}catch(e){try{state=(await request()).state;hud();}catch{}throw e;}finally{busy=false;}}},location,title);}
function profile(){serviceMenu('profile');}
function market(){serviceMenu('market');}
function commerceMenu(mode:CommerceMode){clearCommerce();commerce=openCommerce(panel,mode,{state:()=>state,sound:()=>chime(),exit:market,back:market,switchMode:commerceMenu,trade:async body=>{stateVersion++;busy=true;try{const r=await request(body);state=r.state;hud();return r.message;}catch(e){try{state=(await request()).state;hud();}catch{}throw e;}finally{busy=false;}}});}
function world(){serviceMenu('world');}
function fitScene(){const stage=$('scene-stage');stage.style.width='100vw';stage.style.height='100dvh';const plane=stage.querySelector<HTMLElement>('.interior-plane');if(plane){plane.style.width=Math.max(innerWidth,innerHeight*(Number(stage.dataset.ratio)||1.777))+'px';plane.style.height=innerHeight+'px';}}
function adventureRoute(route:string){close();if(route.startsWith('scene:'))void navigate(route.slice(6) as SceneId);else if(route.startsWith('market:'))commerceMenu(route.slice(7) as CommerceMode);else serviceMenu(route.replace('menu:',''),current==='vorak'?'vorak':'elarwyn');}
function encounter(e:Encounter){if(busy||!panel.hidden)return;clearCommerce();panel.className='adventure-dialogue';panel.setAttribute('aria-label',e.speaker);panel.hidden=false;const heading=document.createElement('h2');heading.textContent=e.speaker;const text=document.createElement('p');text.textContent=e.text;panel.append(heading,text);actions(...e.choices.map(c=>button(c.label,()=>adventureRoute(c.route))),button('À bientôt',close));trapMenu(panel,()=>busy,close);panel.querySelector('button')?.focus({preventScroll:true});}
function worldInteraction(id:string){if(id in scenes){void navigate(id as SceneId);return;}serviceMenu(id);}

let exploration:ReturnType<typeof mountExploration>|undefined;
let navigationVersion=0;
async function navigate(id:SceneId){const scene=scenes[id];if(!scene||busy)return;const version=++navigationVersion;close();current=id;hud();const stage=$('scene-stage');stage.classList.add('changing');stage.setAttribute('aria-busy','true');const img=new Image();img.alt=scene.name;try{await new Promise<void>((resolve,reject)=>{const timeout=setTimeout(()=>reject(new Error('Chargement trop long : '+scene.name)),15000);img.onload=()=>{clearTimeout(timeout);resolve();};img.onerror=()=>{clearTimeout(timeout);reject(new Error('Décor inaccessible : '+scene.image));};img.src='/assets/scenes/'+scene.image;});if(version!==navigationVersion)return;exploration?.destroy();exploration=undefined;stage.replaceChildren();stage.dataset.scene=id;stage.dataset.ratio=String(img.naturalWidth/img.naturalHeight);fitScene();
if(id==='hub'){exploration=mountExploration(stage,{state:()=>state,blocked:()=>!panel.hidden||busy||stage.getAttribute('aria-busy')==='true',interact:worldInteraction,notify});}
else{const viewport=document.createElement('div');viewport.className='interior-viewport';const plane=document.createElement('div');plane.className='interior-plane';viewport.append(plane);stage.append(viewport);img.className='interior-background';plane.append(img);fitScene();viewport.scrollLeft=(plane.clientWidth-innerWidth)/2;const glow=document.createElement('div');glow.className='interior-atmosphere';plane.append(glow);for(const e of interiors[id]??[]){const b=button(e.label,()=>encounter(e));b.className='encounter-point';b.style.left=e.x+'%';b.style.top=e.y+'%';b.setAttribute('aria-label',e.label);const marker=document.createElement('span');marker.className='encounter-marker';marker.textContent='✦';const label=document.createElement('span');label.className='encounter-label';label.textContent=e.label;b.replaceChildren(marker,label);plane.append(b);}const back=button('← '+(scenes[scene.parent??'hub'].name.split(' · ')[0]),()=>void navigate(scene.parent??'hub'));back.className='interior-exit';stage.append(back);}
$('scene-copy').hidden=true;$('scene-copy').textContent='';}catch(e){show('Chargement interrompu',String(e));end();}finally{if(version===navigationVersion){stage.classList.remove('changing');stage.setAttribute('aria-busy','false');}}}
$('game').innerHTML='<div id="scene-stage"></div><div id="scene-copy"></div>';
watchMenuSurface(panel,$('scene-stage'));
const quick=document.createElement('nav');quick.className='adventure-quick';quick.setAttribute('aria-label','Équipement et voyage');quick.append(button('Mon profil',profile),button('Monde',world),button('Gazette',()=>serviceMenu('journal')));document.body.append(quick);

window.addEventListener('resize',fitScene);
window.addEventListener('keydown',e=>{if(e.defaultPrevented||commerce||e.target instanceof HTMLInputElement)return;if(e.key==='Escape'){if(service&&!['guard','robber'].includes(current))closeService();else close();}if(e.key.toLowerCase()==='i'&&panel.hidden&&!busy&&$('scene-stage').getAttribute('aria-busy')!=='true')profile();});
try{await refresh();await navigate('hub');if(state.name==='Aventurier'){show('Bienvenue à Altherya','Choisissez votre nom. La progression est conservée sur ce serveur de test.');const i=document.createElement('input');i.maxLength=24;i.value='Aventurier';i.setAttribute('aria-label','Nom du personnage');panel.append(i);actions(button('Entrer dans Legacy',()=>void act({action:'name',name:i.value.trim()||'Aventurier'},close)));}connect().then(s=>{if(s){void refresh();notify('Discord connecté : '+s.user.username);}}).catch(e=>notify('Connexion Discord : '+String(e)));window.setInterval(()=>{if(!busy)void refresh().catch(()=>notify('Connexion au serveur interrompue.'));},15000);}catch(e){show('Le jeu n’a pas pu démarrer','Gardez le serveur Python ouvert et rechargez la page. '+String(e));}

import './ui/polished-menus.css';

import "./ui/native-menus.css";

import './ui/adventure.css';
