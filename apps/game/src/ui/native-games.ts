import {assetSlice} from './assets';
import {fitArtworkText} from './artwork-layout';

export const nativeGameKinds=new Set(['blackjack','roulette','slots','horses','russian']);
const place=(n:HTMLElement,x:number,y:number,w:number,h:number)=>{n.classList.add('native-game-part');Object.assign(n.style,{left:x+'%',top:y+'%',width:w+'%',height:h+'%'});};

/** Keep the live game engine and mount its elements into the approved blank illustration. */
export function composeNativeGame(panel:HTMLElement,kind:string){
 if(!nativeGameKinds.has(kind))return;
 const table=panel.querySelector<HTMLElement>('.game-table')!;
 table.classList.add('native-game-table');panel.classList.add('native-game');
 const image=new Image();image.src='/assets/menus/'+kind+'.webp';image.alt='';image.className='native-game-background';table.prepend(image);
 const wallet=table.querySelector<HTMLElement>('.game-wallet')!;
 wallet.textContent=wallet.textContent!.replace('Portefeuille : ','');place(wallet,12,10.5,12,4);
 const controls=table.querySelector<HTMLElement>('.game-controls')!;
 const stake=controls.querySelector<HTMLElement>('.game-stake')!;
 const input=stake.querySelector<HTMLInputElement>('input')!;
 stake.replaceChildren(input);input.title='Mise en Gold';
 const minus=controls.firstElementChild as HTMLElement,plus=controls.children[2] as HTMLElement;
 controls.classList.add('native-game-controls');
 const result=table.querySelector<HTMLElement>('.game-result')!;
 const actions=table.querySelector<HTMLElement>('.game-actions')!;
 const stage=table.querySelector<HTMLElement>('.game-playfield')!;
 table.querySelector<HTMLElement>('.game-title')!.classList.add('sr-only');
 table.querySelector<HTMLElement>('.game-presets')!.classList.add('native-game-presets');
 if(kind==='blackjack'){
  place(stake,82,10.5,10,4);place(minus,74,10.5,5,4);place(plus,93,10.5,5,4);
  stage.querySelectorAll<HTMLElement>('.game-hand').forEach((hand,i)=>{place(hand,13,i===0?22:51,74,16);const heading=hand.querySelector<HTMLElement>('h3')!;heading.classList.add('native-score');heading.textContent=heading.textContent?.split(' · ')[1]??'—';});
  place(result,30,75,42,4.4);place(actions,28,81,45,10);
 }else if(kind==='roulette'){
  place(stake,74,66.2,10.5,4.5);place(minus,67,64.8,6,8);place(plus,85,64.8,6,8);
  place(stage.querySelector<HTMLElement>('.game-wheel-area')!,9,20.4,42.2,48.8);if(innerWidth>600){const area=stage.querySelector<HTMLElement>('.game-wheel-area')!,plane=document.createElement('div');plane.className='native-wheel-plane';plane.append(area.querySelector('.game-wheel')!,area.querySelector('.game-ball')!);area.append(plane);}
  place(stage.querySelector<HTMLElement>('.roulette-bets')!,60,24,36,43);
  if(innerWidth>600){const bets=stage.querySelector<HTMLElement>('.roulette-bets')!;bets.querySelectorAll<HTMLElement>('.game-choice-row button').forEach((button,i)=>{table.append(button);place(button,60+(i%2)*18,20+Math.floor(i/2)*10,17,9);button.classList.add('native-baked-hit');});const toggle=bets.querySelector<HTMLElement>('.number-bets>.compact-button')!;table.append(toggle);place(toggle,60,50,36,8);toggle.classList.add('native-baked-hit');const grid=bets.querySelector<HTMLElement>('.roulette-numbers')!;const modal=document.createElement('div');modal.className='native-number-picker';modal.append(grid);table.append(modal);toggle.onclick=()=>{modal.classList.toggle('open');};grid.addEventListener('click',()=>modal.classList.remove('open'));bets.style.display='none';}

  place(result,32,74,36,4.5);place(actions,31,82,48,10);
 }else if(kind==='slots'){
  place(stake,43,71,14,5);place(minus,35,69,7,9);place(plus,58,69,7,9);
  const cabinet=stage.querySelector<HTMLElement>('.game-slot-machine')!;place(cabinet,28.6,29.5,38,29);
  cabinet.querySelector<HTMLElement>('.slot-marquee')!.classList.add('sr-only');
  const lever=cabinet.querySelector<HTMLElement>('.slot-lever')!;table.append(lever);place(lever,77,33,8,34);lever.classList.add('native-slot-lever');
  place(result,39,59,23,4);place(actions,32,83,62,11);
 }else if(kind==='horses'){
  place(stake,43,78.7,14,4.5);place(minus,35,77,7,8);place(plus,58,77,7,8);
  place(stage.querySelector<HTMLElement>('.live-track')!,13,28,76,32);
  place(stage.querySelector<HTMLElement>('.horse-bets')!,16,67,67,7);
  place(result,29,62,43,4);place(actions,30,90,45,8);
 }else{
  place(stake,78,10.5,14,4);place(minus,7,69,7,6);place(plus,79,69,7,6);
  // The revolver and opponent are already in the illustration; the drum is a live animated detail.
  place(stage.querySelector<HTMLElement>('.game-cylinder')!,28,28,16,24);
  stage.querySelector<HTMLElement>('.casino-opponent')!.classList.add('sr-only');
  place(stage.querySelector<HTMLElement>('.cylinder-count')!,42,71,18,5);
  place(result,28,78,45,4.7);place(actions,22,84,64,10);
 }
 if(['roulette','slots','horses'].includes(kind)){const value=document.createElement('span');value.className='native-stake-value';value.textContent=input.value+' Gold';table.append(value);place(value,82,10.5,10,4);input.addEventListener('input',()=>value.textContent=input.value+' Gold');}
 // Supplemental controls stay in one small bar, outside the artwork.
 const extras=table.querySelector<HTMLElement>('.game-extras')!;
 const presets=table.querySelector<HTMLElement>('.game-presets')!;
 const bar=document.createElement('div');bar.className='native-game-footer';bar.append(presets,extras);panel.append(bar);
 if(innerWidth>600){
  if(kind==='blackjack'){bar.prepend(minus,plus);for(const button of [minus,plus]){button.classList.remove('native-game-part');button.style.cssText='';button.classList.add('native-stake-adjust');}}
  if(kind==='horses'){result.classList.remove('native-game-part');result.style.cssText='';result.classList.add('native-race-result');bar.prepend(result);}
  if(kind==='horses')stage.querySelectorAll<HTMLElement>('.horse-bets button').forEach(b=>b.classList.add('native-baked-hit'));
  const areas:Record<string,number[][]>={blackjack:[[27,81,24,10],[50,81,24,10]],roulette:[[31,79,40,11],[38,90,25,8]],slots:[[33,80.5,32,12],[65,82,21,9]],horses:[[32,86.5,32,10],[64,87.5,18,8]],russian:[[21,84,26,9],[48,84,29,9]]};
  Array.from(actions.querySelectorAll<HTMLButtonElement>('button')).forEach((button,i)=>{
   const label=button.getAttribute('aria-label')??button.textContent??'';
   const area=areas[kind][i];
   if(!area){bar.append(button);button.classList.add('native-extra-return');return;}
   const [x,y,w,h]=area;table.append(button);place(button,x,y,w,h);button.classList.add('native-art-action');
   const span=document.createElement('span');span.className='native-action-label';span.textContent=label;
   button.replaceChildren(assetSlice('/assets/menus/'+kind+'.webp',x/100*1536,y/100*1024,w/100*1536,h/100*1024),span);
  });
  actions.remove();
 }
 // Mobile has large, separately composed sections rather than unreadable scaled overlays.
 if(innerWidth<=600){
  panel.classList.add('native-game-mobile');
  image.remove();const top=document.createElement('div');top.className='native-game-mobile-title';top.append(assetSlice('/assets/menus/'+kind+'.webp',0,0,1536,190));table.prepend(top);
  wallet.classList.add('mobile-game-wallet');wallet.style.cssText='';
  for(const n of Array.from(table.querySelectorAll<HTMLElement>('.native-game-part'))){n.classList.remove('native-game-part');n.style.cssText='';}
  const mobileStake=document.createElement('div');mobileStake.className='native-mobile-stake';const label=document.createElement('span');label.textContent='Mise (Gold)';mobileStake.append(label,minus,stake,plus);table.append(mobileStake,actions,result);
  if(kind==='blackjack')stage.classList.add('native-mobile-cards');
  if(kind==='roulette')stage.classList.add('native-mobile-wheel');
  if(kind==='slots')stage.classList.add('native-mobile-slots');
  if(kind==='horses')stage.classList.add('native-mobile-race');
  if(kind==='russian'){stage.classList.add('native-mobile-russian');const scene=document.createElement('div');scene.className='native-russian-scene';scene.append(assetSlice('/assets/menus/russian.webp',0,170,1536,520));stage.prepend(scene);}
 }
 fitArtworkText(panel);
}
