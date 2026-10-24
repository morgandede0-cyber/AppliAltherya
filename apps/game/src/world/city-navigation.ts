import {assetSlice,node} from '../ui/menu-kit';
import type {Spot} from './scenes';
import '../ui/city-navigation.css';
import {citySignRects} from './city-panels';
export function attachCityNavigation(stage:HTMLElement,id:'hub'|'alley',spots:Spot[],admin:boolean,action:(key:string)=>void){
 const nav=node('nav','city-navigation');nav.setAttribute('aria-label',id==='hub'?'Lieux de Legacy':'Personnages de la ruelle');const dock=node('div','city-utilities');
 for(const spot of spots){if(id==='hub'&&['profile','world','jobs'].includes(spot.action))continue;const b=document.createElement('button');b.type='button';b.setAttribute('aria-label',spot.label);b.title=spot.label;b.onclick=()=>action(spot.action);
 if(id==='alley'&&spot.action==='scene:smogo'){
 b.className='city-hit city-smogo-character';b.dataset.smogoCharacter='';b.hidden=true;b.disabled=true;
 b.style.left=spot.x+'%';b.style.top=spot.y+'%';b.style.width=spot.w+'%';b.style.height=spot.h+'%';
 const label=node('span','city-smogo-label');label.append(assetSlice('/assets/city-panels/smogo-sign-v1.png',38,127,2041,460,2117,743));b.append(label,node('span','city-sr','Smogo'));nav.append(b);
 const resume=document.createElement('button');resume.type='button';resume.className='city-control city-smogo-resume';resume.dataset.smogoResume='';resume.hidden=true;resume.disabled=true;resume.setAttribute('aria-label','Reprendre l’énigme');resume.append(assetSlice('/assets/alley-live/controls.png',32,606,760,169),node('span','','Reprendre l’énigme'));resume.onclick=()=>action(spot.action);dock.append(resume);
 }
 else if(spot.embedded){
 const rect=citySignRects[id][spot.action];
 b.className='city-hit city-panel-button';
 b.style.left=(rect[0]/1536*100)+'%';b.style.top=(rect[1]/1024*100)+'%';
 b.style.width=(rect[2]/1536*100)+'%';b.style.height=(rect[3]/1024*100)+'%';
 const sprite=assetSlice('/assets/city-panels/'+id+'-signs.png',...rect);
 const clip=sprite.querySelector('clipPath')!;clip.replaceChildren();
 const polygon=document.createElementNS('http://www.w3.org/2000/svg','polygon');
 const silhouette=[[6,0],[94,0],[96,8],[100,14],[98,23],[98,77],[100,86],[95,92],[94,100],[6,100],[5,93],[0,85],[2,77],[2,23],[0,14],[5,8]];
 polygon.setAttribute('points',silhouette.map(([x,y])=>`${x/100*rect[2]},${y/100*rect[3]}`).join(' '));clip.append(polygon);
 b.append(sprite,node('span','city-sr',spot.label));
 nav.append(b);
 }
 else{b.className='city-control';b.append(assetSlice('/assets/alley-live/controls.png',32,606,760,169),node('span','',spot.label));dock.append(b);}}
 if(dock.childElementCount)nav.append(dock);
 if(id==='hub'&&admin){const b=document.createElement('button');b.type='button';b.className='city-control city-admin admin-hub-button';b.setAttribute('aria-label','Admin');b.append(assetSlice('/assets/alley-live/controls.png',26,202,756,177),node('span','','Admin'));b.onclick=()=>action('admin');nav.append(b);}
 stage.classList.add('city-stage');stage.append(nav);return()=>{nav.remove();stage.classList.remove('city-stage');};
}
