import {assetSlice,node} from '../ui/menu-kit';
import type {Spot} from './scenes';
import '../ui/city-navigation.css';
export function attachCityNavigation(stage:HTMLElement,id:'hub'|'alley',spots:Spot[],admin:boolean,action:(key:string)=>void){
 const nav=node('nav','city-navigation');nav.setAttribute('aria-label',id==='hub'?'Lieux de Legacy':'Personnages de la ruelle');const dock=node('div','city-utilities');
 for(const spot of spots){const b=document.createElement('button');b.type='button';b.setAttribute('aria-label',spot.label);b.title=spot.label;b.onclick=()=>action(spot.action);
 if(spot.embedded){b.className='city-hit';b.style.left=`clamp(22px,${spot.x+spot.w/2}%,calc(100% - 22px))`;b.style.top=`clamp(22px,${spot.y+spot.h/2}%,calc(100% - 22px))`;b.style.width=spot.w+'%';b.style.height=spot.h+'%';b.append(node('span','city-sr',spot.label));if(id==='alley'&&spot.action!=='scene:hub'){b.classList.add('city-character');const glow=node('i','city-sign-glow');glow.setAttribute('aria-hidden','true');const rect=spot.action==='scene:thief'?[25,2,75,18]:spot.action==='scene:robber'?[18,0,80,23]:[42,0,57,23];Object.assign(glow.style,{left:rect[0]+'%',top:rect[1]+'%',width:rect[2]+'%',height:rect[3]+'%'});b.append(glow);}nav.append(b);}
 else{b.className='city-control';b.append(assetSlice('/assets/alley-live/controls.png',32,606,760,169),node('span','',spot.label));dock.append(b);}}
 if(dock.childElementCount)nav.append(dock);
 if(id==='hub'&&admin){const b=document.createElement('button');b.type='button';b.className='city-control city-admin admin-hub-button';b.setAttribute('aria-label','Admin');b.append(assetSlice('/assets/alley-live/controls.png',26,202,756,177),node('span','','Admin'));b.onclick=()=>action('admin');nav.append(b);}
 stage.classList.add('city-stage');stage.append(nav);return()=>{nav.remove();stage.classList.remove('city-stage');};
}
