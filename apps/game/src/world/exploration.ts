import {findPath,places,type Point} from './exploration-model';
import {walkable,WIDTH,HEIGHT} from './map';
import type {Snapshot} from '../activity';
let remembered:Point={x:448,y:576};
export function mountExploration(stage:HTMLElement,host:{state:()=>Snapshot;blocked:()=>boolean;interact:(id:string)=>void;notify:(s:string)=>void}){
 const canvas=document.createElement('canvas');canvas.className='exploration-canvas';canvas.tabIndex=0;canvas.setAttribute('aria-label','Explorer Legacy. Flèches ou ZQSD pour marcher, E pour interagir.');stage.append(canvas);const ctx=canvas.getContext('2d')!;const bg=new Image();bg.src='/assets/region.png';const atlas=new Image();atlas.src='/assets/actors-exploration.png';atlas.onerror=()=>host.notify('Les personnages n’ont pas pu être chargés. Recharge la page.');
 function actor(x:number,y:number,row:number,walking:boolean){ctx.save();ctx.translate(x,y);ctx.fillStyle='#0005';ctx.beginPath();ctx.ellipse(0,0,16,5,0,0,7);ctx.fill();if(atlas.complete&&atlas.naturalWidth){const cw=atlas.naturalWidth/4,ch=atlas.naturalHeight/6,frame=walking?Math.floor(time*8)%4:0;if(row===0&&facing<0)ctx.scale(-1,1);ctx.drawImage(atlas,frame*cw,row*ch,cw,ch,-36,-66,72,72);}ctx.restore();}

 const help=document.createElement('div');help.className='exploration-help';help.textContent='Clique pour marcher · ZQSD / flèches · E pour interagir';stage.append(help);
 const action=document.createElement('button');action.className='world-interact';action.hidden=true;stage.append(action);
 const accessible=document.createElement('div');accessible.className='world-accessibility';accessible.setAttribute('aria-label','Destinations accessibles');stage.append(accessible);
 for(const place of places){const b=document.createElement('button');b.textContent=place.name;b.onclick=()=>go(place);accessible.append(b);}
 const stick=document.createElement('div');stick.className='world-stick';stick.setAttribute('aria-label','Déplacement tactile');stick.innerHTML='<span></span>';stage.append(stick);
 let position:Point={...remembered},camera={...remembered},path:Point[]=[],target:typeof places[number]|undefined,nearest:typeof places[number]|undefined,keys=new Set<string>(),joystick={x:0,y:0},time=0,previous=performance.now(),raf=0,dead=false,scale=1,facing=1;let marker:Point|undefined;
 function go(place:typeof places[number]){if(host.blocked())return;target=place;path=findPath(position,place);if(!path.length&&Math.hypot(position.x-place.x,position.y-place.y)>64){host.notify('Approche-toi par le chemin.');target=undefined;}canvas.focus({preventScroll:true});}
 function activate(){if(!host.blocked()&&nearest)host.interact(nearest.id);}
 action.onclick=activate;
 function resize(){const r=stage.getBoundingClientRect(),d=Math.min(devicePixelRatio,2);canvas.width=r.width*d;canvas.height=r.height*d;canvas.style.width=r.width+'px';canvas.style.height=r.height+'px';scale=Math.max(.75,Math.min(1.4,r.width/850));}
 const observer=new ResizeObserver(resize);observer.observe(stage);resize();
 function down(e:KeyboardEvent){if(host.blocked()||e.target instanceof HTMLInputElement)return;const k=e.key.toLowerCase();if(['arrowup','arrowdown','arrowleft','arrowright','z','q','s','d','w','a','e','enter',' '].includes(k)){e.preventDefault();keys.add(k);if((k==='e'||k==='enter')&&!e.repeat)activate();}}
 function up(e:KeyboardEvent){keys.delete(e.key.toLowerCase());}
 function blur(){keys.clear();joystick={x:0,y:0};}
 window.addEventListener('keydown',down);window.addEventListener('keyup',up);window.addEventListener('blur',blur);
 canvas.onclick=e=>{if(host.blocked())return;const r=canvas.getBoundingClientRect(),p={x:(e.clientX-r.left-r.width/2)/scale+camera.x,y:(e.clientY-r.top-r.height/2)/scale+camera.y};const place=places.find(n=>Math.hypot(n.x-p.x,n.y-p.y)<45);if(place){go(place);return;}target=undefined;path=findPath(position,p);marker=path.at(-1);canvas.focus({preventScroll:true});};
 const touch=(e:PointerEvent)=>{const r=stick.getBoundingClientRect();let x=(e.clientX-r.left-r.width/2)/35,y=(e.clientY-r.top-r.height/2)/35,l=Math.hypot(x,y);if(l>1){x/=l;y/=l;}joystick={x,y};(stick.firstElementChild as HTMLElement).style.transform=`translate(${x*28}px,${y*28}px)`;};
 stick.onpointerdown=e=>{if(host.blocked())return;stick.setPointerCapture(e.pointerId);touch(e);};stick.onpointermove=e=>{if(stick.hasPointerCapture(e.pointerId))touch(e);};stick.onpointerup=stick.onpointercancel=()=>{joystick={x:0,y:0};(stick.firstElementChild as HTMLElement).style.transform='';};
 function frame(now:number){if(dead)return;const dt=Math.min(.04,(now-previous)/1000);previous=now;time+=dt;let moving=false;
 if(!host.blocked()){
 let dx=(keys.has('d')||keys.has('arrowright')?1:0)-(keys.has('q')||keys.has('a')||keys.has('arrowleft')?1:0)+joystick.x,dy=(keys.has('s')||keys.has('arrowdown')?1:0)-(keys.has('z')||keys.has('w')||keys.has('arrowup')?1:0)+joystick.y;
 if(dx||dy){path=[];target=undefined;const l=Math.hypot(dx,dy);dx/=Math.max(1,l);dy/=Math.max(1,l);}
 else if(path.length){const p=path[0],l=Math.hypot(p.x-position.x,p.y-position.y);if(l<4)path.shift();else{dx=(p.x-position.x)/l;dy=(p.y-position.y)/l;}}
 if(dx)facing=Math.sign(dx);const speed=155*dt;if(dx||dy){const x=position.x+dx*speed,y=position.y+dy*speed;if(walkable(x,position.y)){position.x=x;moving=true;}if(walkable(position.x,y)){position.y=y;moving=true;}}
 nearest=places.find(n=>Math.hypot(n.x-position.x,n.y-position.y)<64);action.hidden=!nearest;action.textContent=nearest?'E · '+nearest.name:'';
 if(target&&nearest===target){target=undefined;path=[];activate();}
 }else{keys.clear();joystick={x:0,y:0};}
 const w=canvas.clientWidth,h=canvas.clientHeight,d=canvas.width/w;camera.x+=(position.x-camera.x)*Math.min(1,dt*8);camera.y+=(position.y-camera.y)*Math.min(1,dt*8);const halfW=w/scale/2,halfH=h/scale/2;camera.x=Math.max(Math.min(WIDTH/2,halfW),Math.min(WIDTH-Math.min(WIDTH/2,halfW),camera.x));camera.y=Math.max(Math.min(HEIGHT/2,halfH),Math.min(HEIGHT-Math.min(HEIGHT/2,halfH),camera.y));
 ctx.setTransform(d,0,0,d,0,0);ctx.fillStyle='#111b1a';ctx.fillRect(0,0,w,h);ctx.translate(w/2,h/2);ctx.scale(scale,scale);ctx.translate(-camera.x,-camera.y);if(bg.complete&&bg.naturalWidth)ctx.drawImage(bg,0,0,WIDTH,HEIGHT);
 if(marker&&path.length){ctx.strokeStyle='#ffe09e';ctx.lineWidth=2;ctx.beginPath();ctx.ellipse(marker.x,marker.y,12,5,0,0,7);ctx.stroke();}
 const sorted=[...places.map(p=>({p,y:p.y})),{p:null,y:position.y}].sort((a,b)=>a.y-b.y);
 for(const item of sorted){if(!item.p){actor(position.x,position.y,0,moving);continue;}const p=item.p;if(p.row>=0)actor(p.x,p.y,p.row,false);else{ctx.fillStyle='#57391d';ctx.fillRect(p.x-3,p.y-40,6,40);ctx.fillStyle='#b78d4b';ctx.fillRect(p.x-16,p.y-40,32,25);ctx.fillStyle='#302719';ctx.font='20px Georgia';ctx.textAlign='center';ctx.fillText(p.id==='jobs'?'!':'↗',p.x,p.y-20);}
 if(Math.hypot(p.x-position.x,p.y-position.y)<230){ctx.fillStyle=p===nearest?'#ffdf95':'#eed7a9';ctx.font='12px Georgia';ctx.textAlign='center';ctx.strokeStyle='#10130e';ctx.lineWidth=4;ctx.strokeText(p.name,p.x,p.y-76);ctx.fillText(p.name,p.x,p.y-76);}}
 // Lantern motes remain cosmetic and never grant economic rewards.
 ctx.fillStyle='#ffd783';for(let i=0;i<15;i++){const x=280+i*69,y=350+Math.sin(time*.8+i)*13+(i%3)*120;ctx.globalAlpha=.3+Math.sin(time+i)*.2;ctx.beginPath();ctx.arc(x,y,1.8,0,7);ctx.fill();}ctx.globalAlpha=1;
 stage.dataset.playerX=position.x.toFixed(1);stage.dataset.playerY=position.y.toFixed(1);stage.dataset.nearby=nearest?.id??'';raf=requestAnimationFrame(frame);
 }
 raf=requestAnimationFrame(frame);
 return {destroy(){remembered={...position};dead=true;cancelAnimationFrame(raf);observer.disconnect();window.removeEventListener('keydown',down);window.removeEventListener('keyup',up);window.removeEventListener('blur',blur);},};
}
