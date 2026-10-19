import {casinoSignArt,casinoSignBounds} from './casino-signs';
import type {Snapshot} from '../activity';
import {assetSlice,node,trapMenu} from './menu-kit';
import './casino-room.css';
type Host={state:()=>Snapshot;route:(key:string)=>void};
export const casinoStations=[
 {key:'russian',label:'Roulette russe'}, {key:'horses',label:'Courses de chevaux'},
 {key:'roulette',label:'Roulette'}, {key:'blackjack',label:'Blackjack'}, {key:'slots',label:'Machines à sous'}
].map(s=>({...s,desktop:casinoSignBounds(s.key),mobile:casinoSignBounds(s.key,true)}));
export function openCasinoRoom(panel:HTMLElement,host:Host){
 let dead=false,last:Snapshot|undefined,received=Date.now(),accessWasValid=false;
 panel.hidden=false;panel.className='casino-room';panel.dataset.kind='casino';panel.removeAttribute('style');panel.setAttribute('aria-label','Salle clandestine');panel.setAttribute('aria-busy','false');document.body.classList.add('illustrated-open');
 const backdrop=node('div','casino-room-backdrop'),map=node('section','casino-room-map');map.setAttribute('aria-label','Tables de la salle clandestine');panel.replaceChildren(backdrop,map);
 const picture=document.createElement('picture'),source=document.createElement('source');source.media='(orientation: portrait) and (max-width: 900px)';source.srcset='/assets/casino-live/room-mobile-clean-v1.png';const image=new Image();image.src='/assets/scenes/casino-room-clean-v1.png';image.alt='Salle clandestine : tables de blackjack, roulette et roulette russe, hippodrome miniature et machines à sous.';image.draggable=false;picture.append(source,image);map.append(picture);
 const targets=new Map<string,HTMLButtonElement>();
 for(const station of casinoStations){const b=document.createElement('button');b.type='button';b.className='casino-room-hit casino-station-'+station.key;b.setAttribute('aria-label',station.label);b.title=station.label;const sr=node('span','casino-room-sr',station.label);b.append(casinoSignArt(station.key),casinoSignArt(station.key,true),sr);for(const [i,prop] of ['x','y','w','h'].entries()){b.style.setProperty('--'+prop,station.desktop[i]+'%');b.style.setProperty('--m'+prop,station.mobile[i]+'%');}b.onclick=()=>{if(!b.disabled&&valid())host.route(station.key);else update();};map.append(b);targets.set(station.key,b);}
 const leave=document.createElement('button');leave.type='button';leave.className='casino-room-hit casino-room-leave';leave.setAttribute('aria-label','Retour à la ruelle');leave.title='Retour à la ruelle';leave.append(casinoSignArt('leave'),casinoSignArt('leave',true),node('span','casino-room-sr','Retour à la ruelle'));for(const [i,prop] of ['x','y','w','h'].entries()){leave.style.setProperty('--'+prop,casinoSignBounds('leave')[i]+'%');leave.style.setProperty('--m'+prop,casinoSignBounds('leave',true)[i]+'%');}leave.onclick=()=>host.route('alley');map.append(leave);
 const bar=node('div','casino-live-bar'),wallet=node('output','casino-room-wallet'),resume=document.createElement('button');wallet.setAttribute('aria-label','Portefeuille');wallet.append(assetSlice('/assets/alley-live/controls.png',32,606,760,169),node('span'));resume.type='button';resume.className='casino-room-resume';resume.append(assetSlice('/assets/alley-live/controls.png',26,202,756,177),node('span'));bar.append(wallet,resume);panel.append(bar);
 const locked=node('div','casino-room-locked');locked.setAttribute('role','status');locked.append(node('p','','Votre accès à la salle a expiré.'),node('button','',''));const guard=locked.querySelector('button')!;guard.textContent='Voir le vigile';guard.onclick=()=>host.route('guard');panel.append(locked);
 function valid(){const s=host.state();return s.alley.access.valid&&s.alley.access.seconds_left-(Date.now()-received)/1000>0;}
 function update(){if(dead)return;const s=host.state();if(s!==last){last=s;received=Date.now();}const allowed=valid();accessWasValid=allowed;panel.classList.toggle('casino-room-inaccessible',!allowed);for(const b of targets.values())b.disabled=!allowed;locked.hidden=allowed;wallet.querySelector('span')!.textContent=`${s.balance.wallet.toLocaleString('fr-FR')} Gold`;const game=casinoStations.find(g=>g.key===s.play.kind);resume.hidden=s.play.status!=='active'||!game||!allowed;resume.querySelector('span')!.textContent=`Reprendre · ${game?.label??''}`;resume.setAttribute('aria-label',`Reprendre · ${game?.label??''}`);resume.onclick=()=>{if(!resume.hidden&&valid()&&game)host.route(game.key);};}
 update();trapMenu(panel,()=>false,()=>host.route('alley'));const timer=setInterval(()=>{if(!dead&&accessWasValid!==valid())update();},1000);
 return{update,destroy(){dead=true;clearInterval(timer);panel.onkeydown=null;document.body.classList.remove('illustrated-open');}};
}
