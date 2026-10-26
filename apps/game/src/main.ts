import {createHotbar} from './ui/hotbar';
import {openQuestLibrary} from './ui/quest-library';
import {attachAlleyPresence,alleyArtwork,smogoIsPresent} from './world/alley-presence';
import {openSmogo} from './ui/smogo';
import {openPort} from './ui/port-menu';
import {openAdventure} from './ui/adventure-menu';
import {installComfort,sceneAmbience} from './audio/ambience';
import {startupAssets,warmVenue} from './ui/asset-priority';
import {openCombatHistory} from './ui/combat-history';
import {openTrading} from './ui/player-market';
import {openMailbox} from './ui/mailbox';
import {maintenanceReason,maintenancePanel,serviceBanner} from './ui/maintenance';
import {openPredatorVenue} from './ui/predator-venues';
import {attachCityNavigation} from './world/city-navigation';
import {openCasinoRoom} from './ui/casino-room';
import {openAlleyNpc,alleyNpcKinds} from './ui/alley-npc';
import {openRealmMenu,realmKinds} from './ui/realm-menu';
import {openUpdateJournal} from './ui/update-journal';
import {openCampaignInteraction} from './ui/campaign-menu';
import {attachQuestWorld,questParents,watchQuestMenuAccess} from './world/quest-world';
import {createQuestTracker} from './ui/quest-tracker';
import {attachHubLife} from './world/hub-life';
import {launchScreen,preloadLaunchAssets} from './ui/launch-screen';
import {sceneViewport} from './ui/responsive';
import {isDiscordActivity,connectionError} from './discord/context';
import {openAdmin} from './ui/admin';
import {openTutorial} from './ui/tutorial';
import {watchMenuSurface} from './ui/menu-surface';
import {openRefined,refinedKinds} from './ui/refined-menus';
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
const mailToggle=document.createElement('button');mailToggle.id='mail-toggle';mailToggle.type='button';mailToggle.setAttribute('aria-label','Boîte aux lettres');mailToggle.disabled=true;mailToggle.innerHTML='<svg viewBox="0 0 24 24" aria-hidden="true"><rect x="2" y="4" width="20" height="16" rx="2"/><path d="m3 6 9 7 9-7"/></svg>';const mailBadge=document.createElement('span');mailBadge.className='mail-badge';mailBadge.setAttribute('aria-hidden','true');mailToggle.append(mailBadge);document.body.append(mailToggle);const mailHudObserver=new ResizeObserver(()=>document.documentElement.style.setProperty('--mail-hud-bottom',$('hud').getBoundingClientRect().bottom+'px'));mailHudObserver.observe($('hud'));mailToggle.onclick=()=>{if(busy||!panel.hidden||!state.tutorial.completed||blockMaintenance(['mail']))return;clearCommerce();service=openMailbox(panel,{state:()=>state,refresh,close,mutate:async body=>{stateVersion++;busy=true;try{const result=await request(body);state=result.state;hud();return result.message;}catch(e){await refresh().catch(()=>{});throw e;}finally{busy=false;}}});};
const hubMotionControl=document.createElement('button');hubMotionControl.id='hub-motion-toggle';hubMotionControl.type='button';hubMotionControl.textContent='Animations';hubMotionControl.disabled=true;
const dailyQuestTracker=createQuestTracker({claimDaily:claimDailyQuests,route:key=>{if(key.startsWith('market:')){commerceMenu(key.slice(7) as CommerceMode);return;}serviceMenu(key);}},true);
const hudbar=createHotbar({mail:mailToggle,motion:hubMotionControl,daily:()=>{if(!busy&&panel.hidden)dailyQuestTracker.open();},route:key=>{if(busy||!panel.hidden||!state?.tutorial.completed||state.tutorial.replay)return;serviceMenu(key);}});
async function claimDailyQuests(){if(busy)throw new Error('Opération en cours.');stateVersion++;busy=true;try{const r=await request({action:'quests_claim'});state=r.state;hud();return r.message;}catch(e){await refresh().catch(()=>{});throw e;}finally{busy=false;}}
let alleyPresence:ReturnType<typeof attachAlleyPresence>|undefined;
function syncSmogo(){alleyPresence?.update();}
let questWorld:ReturnType<typeof attachQuestWorld>|undefined;
function hud(){if(!state)return;questWorld?.update();syncSmogo();const mailCount=state.mail?.attention??0;mailBadge.textContent=mailCount>99?'99+':String(mailCount);mailBadge.hidden=mailCount===0;mailToggle.title=mailCount?`${mailCount} courrier(s) à consulter`:'Boîte aux lettres';mailToggle.disabled=!state.tutorial.completed||!!maintenanceReason(state,['mail']);dailyQuestTracker.update(state);hudbar.update(state,current);$('objective').textContent=scenes[current].name;}
function blockMaintenance(keys:string[]){const reason=maintenanceReason(state,keys);if(!reason)return false;clearCommerce();maintenancePanel(panel,reason,refresh,()=>{close();void navigate('hub');});return true;}
function syncMaintenance(){serviceBanner(state);const keys=[panel.dataset.maintenanceScope??'',panel.dataset.kind??'',current];if(maintenanceReason(state,keys)){blockMaintenance(keys);}else if(panel.dataset.kind==='maintenance'){clearCommerce();panel.hidden=true;if(!starting&&!startup)void navigate('hub');}}
function clearCommerce(){service?.destroy();service=undefined;commerce?.destroy();commerce=undefined;panel.className='';panel.onkeydown=null;panel.replaceChildren();panel.removeAttribute('data-kind');panel.removeAttribute('data-guild');panel.removeAttribute('aria-busy');panel.removeAttribute('aria-label');panel.style.removeProperty('--art-ratio');}
function close(){if(panel.dataset.kind==='maintenance'&&maintenanceReason(state,['global']))return;if(panel.dataset.kind==='tutorial'&&!state.tutorial.completed)return;if(!busy){clearCommerce();panel.hidden=true;}}
function closeService(){close();if(current!=='hub'&&current!=='market')void navigate(scenes[current].parent??'hub');}
function show(title:string,text:string){clearCommerce();panel.className='native-welcome';panel.replaceChildren();const h=document.createElement('h2');h.textContent=title;const p=document.createElement('p');p.textContent=text;panel.append(h,p);panel.hidden=false;}
function button(label:string,fn:()=>void,disabled=false){const b=document.createElement('button');b.textContent=label;b.disabled=disabled;b.onclick=()=>{if(!busy){chime();fn();}};return b;}
function actions(...buttons:HTMLButtonElement[]){const a=document.createElement('div');a.className='actions';a.append(...buttons);panel.append(a);}
function end(back:()=>void=close){actions(button('Retour',back));}
async function refresh(){const version=stateVersion;const result=await request();if(version!==stateVersion)return;state=result.state;if(!state.admin)document.querySelector('.admin-hub-button')?.remove();hud();commerce?.update();service?.update();syncMaintenance();}
function serviceMenu(kind:string,location='elarwyn',title=''){if(kind.startsWith('quest:')){void navigate(kind.slice(6) as SceneId);return;}if(['khaz','ashkar','port'].includes(kind)&&current!==kind){void navigate(kind as SceneId);return;}if(blockMaintenance([kind]))return;if(kind==='tutorial'){void tutorialMenu(true);return;}clearCommerce();const host={refresh,state:()=>state,close:closeService,route:(key:string)=>{if(key==='tutorial'){void tutorialMenu(true);return;}if(key.startsWith('market:')){commerceMenu(key.slice(7) as CommerceMode);return;}if(key in scenes){void navigate(key as SceneId);return;}if(key==='drinks'){void navigate('barman');return;}if(key.startsWith('adventure-')){serviceMenu(key,location);return;}if(illustratedKinds.has(key)||refinedKinds.has(key)||['campaign','chronicles','profile','journal','story','world','trade','combat-history','adventure','port'].includes(key))serviceMenu(key,location);else void navigate(key as SceneId);},mutate:async (body:Record<string,unknown>)=>{if(busy)throw new Error('Opération en cours.');stateVersion++;busy=true;try{const r=await request(body);state=r.state;hud();return r.message;}catch(e){await refresh().catch(()=>{});throw e;}finally{busy=false;}}};if(kind==='adventure'||kind.startsWith('adventure-')){service=openAdventure(panel,host,({training:'Entraînement',forge:'Forge',voyage:'Voyage',daily:'Défis',market:'Recherches'} as Record<string,string>)[kind.slice(10)]??'Métier');return;}if(kind==='smogo'){service=openSmogo(panel,host);return;}if(kind==='port'){service=openPort(panel,host);return;}if(kind==='combat-history'){service=openCombatHistory(panel,host);return;}if(kind==='trade'){service=openTrading(panel,host);return;}if(['market','tavern'].includes(kind)){service=openPredatorVenue(panel,kind as 'market'|'tavern',host);return;}if(kind==='casino'){service=openCasinoRoom(panel,host);return;}if(alleyNpcKinds.has(kind)){service=openAlleyNpc(panel,kind,host);return;}if(realmKinds.has(kind)&&kind!=='bank'){service=openRealmMenu(panel,kind,host);return;}if(kind==='campaign'||kind==='chronicles'){service=openQuestLibrary(panel,host,kind==='campaign'?'main':undefined);return;}if(refinedKinds.has(kind)){service=openRefined(panel,kind,{...host,close:kind==='market'?()=>void navigate('hub'):['guard','robber'].includes(kind)?close:closeService});return;}if(illustratedKinds.has(kind)){service=openIllustrated(panel,kind,host,location);return;}service=openService(panel,kind,host,location,title);}

async function tutorialMenu(replay=false){
 if(busy)return;
 const mutate=async(body:Record<string,unknown>)=>{if(busy)throw new Error('Opération en cours.');stateVersion++;busy=true;try{const r=await request(body);state=r.state;hud();return r.message;}finally{busy=false;}};
 if(replay){try{await mutate({action:'tutorial_replay'});}catch(e){notify(String(e));return;}}
 clearCommerce();service=openTutorial(panel,{state:()=>state,mutate,notify,done:()=>{close();void navigate('hub');}});
}
function enterGame(){if(blockMaintenance([]))return;close();if(!state.tutorial.completed||state.tutorial.replay)void tutorialMenu();}
function adminMenu(){if(!state.admin)return;clearCommerce();service=openAdmin(panel,{close:()=>{close();void navigate('hub');},refresh,allowed:()=>state.admin});}
function updatesMenu(){clearCommerce();service=openUpdateJournal(panel,close);}
function profile(){serviceMenu('profile');}
function commerceMenu(mode:CommerceMode){if(blockMaintenance(['market']))return;clearCommerce();commerce=openCommerce(panel,mode,{state:()=>state,sound:()=>chime(),exit:()=>void navigate('market'),back:()=>void navigate('market'),switchMode:commerceMenu,trade:async body=>{stateVersion++;busy=true;try{const r=await request(body);state=r.state;hud();return r.message;}catch(e){try{state=(await request()).state;hud();}catch{}throw e;}finally{busy=false;}}});}
function shop(){commerceMenu('buy');}
function sales(){commerceMenu('sell');}
function world(){serviceMenu('world');}
function storyShop(){commerceMenu('story');}
function jobs(){serviceMenu('jobs');}
function unavailable(title:string){serviceMenu('unavailable','elarwyn',title);}
async function questMutate(body:Record<string,unknown>){if(busy)throw new Error('Opération en cours.');stateVersion++;busy=true;try{const r=await request(body);state=r.state;hud();return r.message;}catch(e){await refresh().catch(()=>{});throw e;}finally{busy=false;}}
function questEncounter(){if(busy)return;clearCommerce();service=openCampaignInteraction(panel,{state:()=>state,mutate:questMutate,close:()=>{close();const kind=sceneMenus[current];if(kind)serviceMenu(kind,current==='vorak'?'vorak':'elarwyn');},route:key=>{if(key==='port'&&current==='port'){serviceMenu('port');return;}void navigate(key as SceneId);}},current);}
function interact(id:string){if(!panel.hidden||busy||$('scene-stage').getAttribute('aria-busy')==='true')return;if(id.startsWith('scene:')){void navigate(id.slice(6) as SceneId);return;}const handlers:Record<string,()=>void>={admin:adminMenu,'market:story':storyShop,'market:buy':shop,'market:sell':sales,profile,world,jobs,gazette:updatesMenu};(handlers[id]??(()=>unavailable(scenes[current].name)))();}
function fitScene(){const stage=$('scene-stage'),view=sceneViewport(innerWidth,innerHeight,Number(stage.dataset.ratio)||1.777);document.body.classList.toggle('portrait-view',view.portrait);stage.style.width=view.width+'px';stage.style.height=view.height+'px';const bar=document.getElementById('legacy-hotbar');stage.style.setProperty('--scene-ui-bottom',(bar&&!bar.hidden?Math.max(0,stage.getBoundingClientRect().bottom-bar.getBoundingClientRect().top+10):0)+'px');}
let navigationVersion=0,hubLife:(()=>void)|undefined;
async function navigate(id:SceneId,failHard=false){if(blockMaintenance([id,questParents[id]??'']))return;const scene=scenes[id];if(!scene||busy)return;const version=++navigationVersion;close();current=id;hud();const stage=$('scene-stage');stage.classList.add('changing');stage.setAttribute('aria-busy','true');const artwork=id==='alley'?(smogoIsPresent(state)?alleyArtwork.present:alleyArtwork.absent):'/assets/scenes/'+scene.image;const img=new Image();img.fetchPriority='high';img.decoding='async';img.alt=scene.name;try{await new Promise<void>((resolve,reject)=>{const timeout=setTimeout(()=>reject(new Error('Chargement trop long : '+scene.name)),15000);img.onload=()=>{clearTimeout(timeout);resolve();};img.onerror=()=>{clearTimeout(timeout);reject(new Error('Décor inaccessible : '+scene.image));};img.src=artwork;});if(version!==navigationVersion)return;if(state.tutorial.completed&&!state.tutorial.replay){stateVersion++;busy=true;let r;try{r=await request({action:'campaign_world_enter',scene:id});}finally{busy=false;}if(version!==navigationVersion)return;state=r.state;hud();}alleyPresence?.destroy();alleyPresence=undefined;questWorld?.destroy();questWorld=undefined;hubLife?.();hubLife=undefined;stage.replaceChildren(img);stage.dataset.scene=id;$('game').style.setProperty('--scene-background',`url('${artwork}')`);stage.dataset.ratio=String(img.naturalWidth/img.naturalHeight);fitScene();if(id==='hub'||id==='alley'){attachCityNavigation(stage,id,scene.spots,state.admin,interact);if(id==='alley')alleyPresence=attachAlleyPresence(stage,()=>state,$('game'));syncSmogo();}else{stage.classList.remove('city-stage');for(const spot of sceneMenus[id]?[]:scene.spots){const b=button(spot.label,()=>interact(spot.action));b.className='hotspot'+(spot.embedded?' embedded':'');b.setAttribute('aria-label',spot.label);b.title=spot.label;b.style.left=spot.x+'%';b.style.top=spot.y+'%';b.style.width=spot.w+'%';b.style.height=spot.h+'%';const span=document.createElement('span');span.textContent=spot.label;b.replaceChildren(span);if(spot.asset)skinButton(b,spot.asset,spot.label);stage.append(b);}}if(state.campaign?.accepted&&(state.campaign?.quest?.steps[state.campaign.stage]?.kind==='explore'||!!state.campaign?.quest?.steps[state.campaign.stage]?.work_points?.length||!!state.campaign?.quest?.steps[state.campaign.stage]?.prop)&&state.campaign.world?.target===id)window.dispatchEvent(new CustomEvent('quest-tracker-open',{detail:'world-exploration'}));questWorld=attachQuestWorld(stage,{scene:id,parent:id==='alley'?undefined:scene.parent,state:()=>state,route:key=>void navigate(key as SceneId),open:questEncounter,mutate:questMutate,notify});if(id==='hub')hubLife=attachHubLife(stage,panel,hubMotionControl);$('scene-copy').hidden=true;$('scene-copy').textContent='';warmVenue(id);sceneAmbience(id);if(sceneMenus[id])serviceMenu(sceneMenus[id]!,id==='vorak'?'vorak':'elarwyn');}catch(e){if(failHard)throw e;show('Chargement interrompu',String(e));end();}finally{if(version===navigationVersion){stage.classList.remove('changing');stage.setAttribute('aria-busy','false');}}}
$('game').innerHTML='<div id="scene-stage"></div><div id="scene-copy"></div>';
watchMenuSurface(panel,$('scene-stage'));
watchQuestMenuAccess(panel,$('scene-stage'),()=>sceneMenus[current],close);
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
  await preloadLaunchAssets(startupAssets,(done,total)=>startup?.update(65+Math.round(done/total*30),'Chargement de la cité…',2));
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

installComfort();

// Last layer: common materials and accessible controls, without replacing venue artwork.
import './ui/realm-theme.css';

// Approved guild skins are the final layer, scoped to their live menus.
import './ui/guild-menu.css';

import './ui/studio-menu.css';
import './ui/forge-studio.css';
