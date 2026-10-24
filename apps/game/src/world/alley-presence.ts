import type {Snapshot} from '../activity';

type PresenceState=Pick<Snapshot,'server_now'|'smogo'|'save_owner'>;
export const alleyArtwork={absent:'/assets/scenes/alley-smogo-absent-v2.png',present:'/assets/scenes/alley-smogo-present-v2.png'};
export function smogoIsPresent(s:PresenceState,now=s.server_now){const p=s.smogo;if(p?.completed||p?.remaining===0&&(!p.round||p.round.status==='finished'||now>=p.round.expires_at))return false;return p?.available===true&&(!p.available_until||now<p.available_until);}
export function smogoHasRound(s:PresenceState,now=s.server_now){const r=s.smogo?.round;return r?.status==='active'&&now<r.expires_at;}

/** Swap the whole scene only once its matching artwork is decoded. No NPC overlay. */
export function attachAlleyPresence(stage:HTMLElement,state:()=>PresenceState,background:HTMLElement){
 const image=stage.querySelector<HTMLImageElement>(':scope > img')!;
 const character=stage.querySelector<HTMLButtonElement>('[data-smogo-character]')!;
 const resume=stage.querySelector<HTMLButtonElement>('[data-smogo-resume]')!;
 let dead=false,generation=0,target='',snapshot:PresenceState,anchor=0,stamp=0;
 const clock=()=>{const next=state();if(next!==snapshot){snapshot=next;anchor=next.server_now;stamp=performance.now();}return anchor+(performance.now()-stamp)/1000;};
 const show=(present:boolean)=>{
  stage.dataset.smogoPresence=present?'present':'absent';
  character.hidden=!present;character.disabled=!present;
  const pending=!present&&smogoHasRound(state(),clock());resume.hidden=!pending;resume.disabled=!pending;
  if(!present&&document.activeElement===character){const fallback=pending?resume:stage.querySelector<HTMLButtonElement>('[aria-label="Retour au hub"]');fallback?.focus({preventScroll:true});}
 };
 function update(){
  if(dead)return;
  const now=clock(),present=smogoIsPresent(state(),now),src=present?alleyArtwork.present:alleyArtwork.absent;
  // Disable stale access immediately, even while the replacement image loads.
  if(!present){character.disabled=true;character.hidden=true;}
  const pending=!present&&smogoHasRound(state(),now);resume.hidden=!pending;resume.disabled=!pending;
  if(target===src)return;
  target=src;const version=++generation;
  if(image.getAttribute('src')===src){show(present);return;}
  const replacement=new Image();replacement.decoding='async';replacement.fetchPriority='high';
  replacement.onload=async()=>{
   try{await replacement.decode();}catch{/* onload already confirms a valid image */}
   if(dead||version!==generation||!stage.contains(image))return;
   if(smogoIsPresent(state(),clock())!==present){target='';update();return;}
   image.src=src;background.style.setProperty('--scene-background',`url('${src}')`);show(present);
  };
  replacement.onerror=()=>{if(!dead&&version===generation){target='';character.hidden=true;character.disabled=true;stage.dataset.smogoPresence='unavailable';}};
  replacement.src=src;
 }
 const tick=window.setInterval(update,500);
 const visible=()=>{if(!document.hidden)update();};document.addEventListener('visibilitychange',visible);
 update();
 return{update,destroy(){dead=true;generation++;window.clearInterval(tick);document.removeEventListener('visibilitychange',visible);}};
}
