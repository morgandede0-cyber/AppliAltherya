/** Subtle effects anchored to the unchanged 1672×941 authored illustration. */
export const hubArt={width:1672,height:941};
export const hubLanterns=[
 {x:79,y:89,r:42,power:.15},{x:143,y:109,r:29,power:.11},
 {x:55,y:359,r:35,power:.14},{x:53,y:490,r:44,power:.16},{x:103,y:551,r:24,power:.11},
 {x:338,y:325,r:24,power:.12},{x:367,y:329,r:26,power:.13},
 {x:554,y:405,r:39,power:.13},{x:1296,y:777,r:26,power:.15},
 {x:1408,y:696,r:33,power:.15},{x:1408,y:553,r:26,power:.12},{x:1550,y:557,r:26,power:.12},
 {x:1650,y:393,r:29,power:.11}
] as const;
export const hubJets=[
 {x0:773,y0:591,cx:803,cy:480,x1:825,y1:575},
 {x0:813,y0:578,cx:830,cy:543,x1:843,y1:579},
 {x0:911,y0:580,cx:934,cy:504,x1:953,y1:586}
] as const;
type Jet=typeof hubJets[number];
export function jetPoint(jet:Jet,u:number){const v=1-u;return{x:v*v*jet.x0+2*v*u*jet.cx+u*u*jet.x1,y:v*v*jet.y0+2*v*u*jet.cy+u*u*jet.y1};}
function glow(ctx:CanvasRenderingContext2D,x:number,y:number,r:number,alpha:number){const light=ctx.createRadialGradient(x,y,0,x,y,r);light.addColorStop(0,`rgba(255,203,100,${alpha})`);light.addColorStop(.28,`rgba(255,160,51,${alpha*.52})`);light.addColorStop(1,'rgba(255,143,45,0)');ctx.fillStyle=light;ctx.fillRect(x-r,y-r,r*2,r*2);}
export function paintHubLife(ctx:CanvasRenderingContext2D,time:number){
 ctx.save();ctx.globalCompositeOperation='screen';
 for(const [i,lamp] of hubLanterns.entries()){const pulse=.85+Math.sin(time*1.7+i*2)*.08+Math.sin(time*.73+i)*.06;glow(ctx,lamp.x,lamp.y,lamp.r,lamp.power*pulse);}
 ctx.restore();
 // Match the existing grey chimney plume, without hiding roofs or castle details.
 ctx.save();for(let i=0;i<10;i++){const life=(time*.055+i/10)%1,x=486-20*life+Math.sin(life*4+i*.1)*8,y=156-life*112,r=5+life*16,alpha=Math.sin(life*Math.PI)*.045;const smoke=ctx.createRadialGradient(x,y,0,x,y,r);smoke.addColorStop(0,`rgba(106,109,117,${alpha})`);smoke.addColorStop(1,'rgba(106,109,117,0)');ctx.fillStyle=smoke;ctx.fillRect(x-r,y-r,r*2,r*2);}ctx.restore();
 // Small travelling highlights follow the jets already painted in the fountain.
 ctx.save();ctx.lineCap='round';for(const [index,jet] of hubJets.entries()){
  ctx.strokeStyle='rgba(189,235,255,.12)';ctx.lineWidth=.8;ctx.beginPath();ctx.moveTo(jet.x0,jet.y0);ctx.quadraticCurveTo(jet.cx,jet.cy,jet.x1,jet.y1);ctx.stroke();
  for(let i=0;i<8;i++){const u=(time*.54+i/8+index*.17)%1,p=jetPoint(jet,u),next=jetPoint(jet,Math.min(1,u+.027));ctx.globalAlpha=Math.sin(u*Math.PI)*.44;ctx.strokeStyle='#e1f8ff';ctx.lineWidth=1;ctx.beginPath();ctx.moveTo(p.x,p.y);ctx.lineTo(next.x,next.y);ctx.stroke();}
  for(let i=0;i<2;i++){const u=(time*.64+i/2+index*.23)%1;ctx.globalAlpha=(1-u)*.19;ctx.strokeStyle='#dcf5ff';ctx.lineWidth=.6;ctx.beginPath();ctx.ellipse(jet.x1,jet.y1,2+u*6,.5+u*1.5,0,0,Math.PI*2);ctx.stroke();}
 }ctx.restore();
}
const owners=new WeakMap<HTMLElement,()=>void>();
export function attachHubLife(stage:HTMLElement,panel:HTMLElement){
 owners.get(stage)?.();
 const canvas=document.createElement('canvas');canvas.className='hub-life';canvas.setAttribute('aria-hidden','true');canvas.setAttribute('role','presentation');canvas.style.cssText='position:absolute;inset:0;width:100%;height:100%;pointer-events:none;z-index:1';
 let context:CanvasRenderingContext2D|null;try{context=canvas.getContext('2d');}catch{return()=>{};}if(!context)return()=>{};const ctx=context;
 stage.insertBefore(canvas,stage.querySelector('.hub-toolbar'));
 const media=window.matchMedia('(prefers-reduced-motion: reduce)');let disposed=false,active=false,raf=0,lastPaint=-Infinity,clock=0,lastTick=0,renderWidth=0,renderHeight=0,interval=1000/30;
 function clear(){ctx.setTransform(1,0,0,1,0,0);ctx.clearRect(0,0,canvas.width,canvas.height);}
 function resize(){const rect=stage.getBoundingClientRect();renderWidth=rect.width;renderHeight=rect.height;const dpr=Math.min(window.devicePixelRatio||1,1.5,Math.sqrt(1600000/Math.max(1,renderWidth*renderHeight)));canvas.width=Math.max(1,Math.floor(renderWidth*dpr));canvas.height=Math.max(1,Math.floor(renderHeight*dpr));interval=1000/(renderWidth<700?24:30);lastPaint=-Infinity;}
 function tick(now:number){if(!active||disposed)return;if(lastTick)clock+=Math.min((now-lastTick)/1000,.1);lastTick=now;if(now-lastPaint>=interval){clear();ctx.setTransform(canvas.width/hubArt.width,0,0,canvas.height/hubArt.height,0,0);paintHubLife(ctx,clock);lastPaint=now;}raf=window.requestAnimationFrame(tick);}
 function sync(){if(disposed)return;const shouldRun=stage.isConnected&&stage.dataset.scene==='hub'&&stage.getAttribute('aria-busy')!=='true'&&panel.hidden&&!document.body.classList.contains('launching')&&!document.hidden&&!media.matches&&renderWidth>0&&renderHeight>0;if(shouldRun===active)return;active=shouldRun;canvas.dataset.running=String(active);lastTick=0;if(active){lastPaint=-Infinity;raf=window.requestAnimationFrame(tick);}else{window.cancelAnimationFrame(raf);raf=0;clear();}}
 const observer=new MutationObserver(sync);observer.observe(panel,{attributes:true,attributeFilter:['hidden']});observer.observe(stage,{attributes:true,attributeFilter:['data-scene','aria-busy']});observer.observe(document.body,{attributes:true,attributeFilter:['class']});
 const resized=()=>{resize();sync();};const sizeObserver=typeof ResizeObserver==='undefined'?undefined:new ResizeObserver(resized);sizeObserver?.observe(stage);window.addEventListener('resize',resized);document.addEventListener('visibilitychange',sync);media.addEventListener('change',sync);
 function destroy(){if(disposed)return;disposed=true;active=false;window.cancelAnimationFrame(raf);observer.disconnect();sizeObserver?.disconnect();window.removeEventListener('resize',resized);document.removeEventListener('visibilitychange',sync);media.removeEventListener('change',sync);canvas.remove();if(owners.get(stage)===destroy)owners.delete(stage);}
 owners.set(stage,destroy);resize();canvas.dataset.running='false';sync();return destroy;
}
