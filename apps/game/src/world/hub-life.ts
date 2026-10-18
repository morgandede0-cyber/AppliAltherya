/** Effects anchored to the approved 1536×1024 predator city illustration. */
export const hubArt={width:1536,height:1024};
export const hubLanterns=[
 {x:110,y:179,r:25,power:.11},{x:114,y:377,r:28,power:.13},
 {x:186,y:394,r:22,power:.12},{x:329,y:466,r:26,power:.12},
 {x:600,y:538,r:22,power:.11},{x:1028,y:637,r:25,power:.13},
 {x:1137,y:622,r:29,power:.14},{x:1251,y:584,r:24,power:.12},
 {x:1493,y:600,r:24,power:.12}
] as const;
export const hubJets=[
 {x0:708,y0:744,cx:736,cy:656,x1:761,y1:745},
 {x0:939,y0:742,cx:958,cy:667,x1:975,y1:748}
] as const;
type Jet=typeof hubJets[number];
export function jetPoint(jet:Jet,u:number){const v=1-u;return{x:v*v*jet.x0+2*v*u*jet.cx+u*u*jet.x1,y:v*v*jet.y0+2*v*u*jet.cy+u*u*jet.y1};}
function glow(ctx:CanvasRenderingContext2D,x:number,y:number,r:number,alpha:number){const light=ctx.createRadialGradient(x,y,0,x,y,r);light.addColorStop(0,`rgba(255,203,100,${alpha})`);light.addColorStop(.28,`rgba(255,160,51,${alpha*.52})`);light.addColorStop(1,'rgba(255,143,45,0)');ctx.fillStyle=light;ctx.fillRect(x-r,y-r,r*2,r*2);}
export function paintHubLife(ctx:CanvasRenderingContext2D,time:number){
 ctx.save();ctx.globalCompositeOperation='screen';
 for(const [i,lamp] of hubLanterns.entries()){const pulse=.7+Math.sin(time*2.3+i*2)*.18+Math.sin(time*.85+i)*.12;glow(ctx,lamp.x,lamp.y,lamp.r,lamp.power*pulse*2.3);}
 ctx.restore();
 // Match the existing grey chimney plume, without hiding roofs or castle details.
 ctx.save();for(let i=0;i<12;i++){const life=(time*.13+i/12)%1,x=1140-20*life+Math.sin(life*4+i*.1)*8,y=435-life*112,r=5+life*16,alpha=Math.sin(life*Math.PI)*.13;const smoke=ctx.createRadialGradient(x,y,0,x,y,r);smoke.addColorStop(0,`rgba(106,109,117,${alpha})`);smoke.addColorStop(1,'rgba(106,109,117,0)');ctx.fillStyle=smoke;ctx.fillRect(x-r,y-r,r*2,r*2);}ctx.restore();
 // Small travelling highlights follow the jets already painted in the fountain.
 ctx.save();ctx.lineCap='round';for(const [index,jet] of hubJets.entries()){
  ctx.strokeStyle='rgba(189,235,255,.24)';ctx.lineWidth=1.1;ctx.beginPath();ctx.moveTo(jet.x0,jet.y0);ctx.quadraticCurveTo(jet.cx,jet.cy,jet.x1,jet.y1);ctx.stroke();
  for(let i=0;i<8;i++){const u=(time*.8+i/8+index*.17)%1,p=jetPoint(jet,u),next=jetPoint(jet,Math.min(1,u+.05));ctx.globalAlpha=Math.sin(u*Math.PI)*.85;ctx.strokeStyle='#e1f8ff';ctx.lineWidth=1.8;ctx.beginPath();ctx.moveTo(p.x,p.y);ctx.lineTo(next.x,next.y);ctx.stroke();}
  for(let i=0;i<2;i++){const u=(time*.64+i/2+index*.23)%1;ctx.globalAlpha=(1-u)*.32;ctx.strokeStyle='#dcf5ff';ctx.lineWidth=.9;ctx.beginPath();ctx.ellipse(jet.x1,jet.y1,2+u*6,.5+u*1.5,0,0,Math.PI*2);ctx.stroke();}
 }ctx.restore();
}
const owners=new WeakMap<HTMLElement,()=>void>();
export function attachHubLife(stage:HTMLElement,panel:HTMLElement,control?:HTMLButtonElement){
 owners.get(stage)?.();
 const canvas=document.createElement('canvas');canvas.className='hub-life';canvas.setAttribute('aria-hidden','true');canvas.setAttribute('role','presentation');canvas.style.cssText='position:absolute;inset:0;width:100%;height:100%;pointer-events:none;z-index:1';
 const unavailable=()=>{if(control){control.disabled=true;control.textContent='Sans animation';control.title='Les effets ne sont pas disponibles dans ce navigateur.';control.setAttribute('aria-pressed','false');}return()=>{};};
 let context:CanvasRenderingContext2D|null;try{context=canvas.getContext('2d');}catch{return unavailable();}if(!context)return unavailable();const ctx=context;
 const preferenceKey='altherya.hub-motion.v1';let preference='auto';try{const saved=window.localStorage.getItem(preferenceKey);if(saved==='on'||saved==='off')preference=saved;}catch{/* Storage may be blocked inside an embedded activity. */}

 stage.insertBefore(canvas,stage.querySelector('.hub-toolbar'));
 const media=window.matchMedia('(prefers-reduced-motion: reduce)');let disposed=false,active=false,raf=0,lastPaint=-Infinity,clock=0,lastTick=0,renderWidth=0,renderHeight=0,interval=1000/30;
 function clear(){ctx.setTransform(1,0,0,1,0,0);ctx.clearRect(0,0,canvas.width,canvas.height);}
 function resize(){const rect=stage.getBoundingClientRect();renderWidth=rect.width;renderHeight=rect.height;const dpr=Math.min(window.devicePixelRatio||1,1.5,Math.sqrt(1600000/Math.max(1,renderWidth*renderHeight)));canvas.width=Math.max(1,Math.floor(renderWidth*dpr));canvas.height=Math.max(1,Math.floor(renderHeight*dpr));interval=1000/(renderWidth<700?24:30);lastPaint=-Infinity;}
 function tick(now:number){if(!active||disposed)return;if(lastTick)clock+=Math.min((now-lastTick)/1000,.1);lastTick=now;if(now-lastPaint>=interval){clear();ctx.setTransform(canvas.width/hubArt.width,0,0,canvas.height/hubArt.height,0,0);paintHubLife(ctx,clock);lastPaint=now;}raf=window.requestAnimationFrame(tick);}
 function sync(){if(disposed)return;const enabled=preference==='on'||(preference==='auto'&&!media.matches);if(control){control.disabled=false;control.textContent=enabled?'Animations ✓':'Activer l’animation';control.setAttribute('aria-pressed',String(enabled));control.setAttribute('aria-label',enabled?'Mettre les animations du hub en pause':'Activer les animations du hub');control.title=enabled?'Mettre les animations en pause':media.matches&&preference==='auto'?'Les animations sont réduites par votre appareil. Cliquer pour les activer.':'Activer les animations du hub';}const shouldRun=stage.isConnected&&stage.dataset.scene==='hub'&&stage.getAttribute('aria-busy')!=='true'&&panel.hidden&&!document.body.classList.contains('launching')&&!document.hidden&&enabled&&renderWidth>0&&renderHeight>0;if(shouldRun===active)return;active=shouldRun;canvas.dataset.running=String(active);lastTick=0;if(active){clear();ctx.setTransform(canvas.width/hubArt.width,0,0,canvas.height/hubArt.height,0,0);paintHubLife(ctx,clock);lastPaint=-Infinity;raf=window.requestAnimationFrame(tick);}else{window.cancelAnimationFrame(raf);raf=0;clear();}}
 const toggle=()=>{preference=preference==='on'||(preference==='auto'&&!media.matches)?'off':'on';try{window.localStorage.setItem(preferenceKey,preference);}catch{}sync();};control?.addEventListener('click',toggle);
 const observer=new MutationObserver(sync);observer.observe(panel,{attributes:true,attributeFilter:['hidden']});observer.observe(stage,{attributes:true,attributeFilter:['data-scene','aria-busy']});observer.observe(document.body,{attributes:true,attributeFilter:['class']});
 const resized=()=>{resize();sync();};const sizeObserver=typeof ResizeObserver==='undefined'?undefined:new ResizeObserver(resized);sizeObserver?.observe(stage);window.addEventListener('resize',resized);document.addEventListener('visibilitychange',sync);media.addEventListener('change',sync);
 function destroy(){if(disposed)return;disposed=true;active=false;control?.removeEventListener('click',toggle);window.cancelAnimationFrame(raf);observer.disconnect();sizeObserver?.disconnect();window.removeEventListener('resize',resized);document.removeEventListener('visibilitychange',sync);media.removeEventListener('change',sync);canvas.remove();if(owners.get(stage)===destroy)owners.delete(stage);}
 owners.set(stage,destroy);resize();canvas.dataset.running='false';sync();return destroy;
}
