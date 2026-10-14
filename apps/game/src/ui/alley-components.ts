import {assetSlice} from './assets';
/** Complete silhouettes from the original atlas. Polygon masks exclude touching neighbouring cells. */
const cells:Record<string,[number,number,number,number]>={
 title:[602,98,846,174],
 'Le voleur':[12,286,511,132],
 'Le braqueur':[511,286,510,132],
 'Le vigile':[991,286,483,132],
 'Panneau de la ruelle':[1451,286,591,132],
 'Retour en ville':[749,444,551,134],
};
export function alleyComponent(label:string){
 const box=cells[label];if(!box)return null;
 const [x,y,w,h]=box.map(value=>Math.round(value*2172/2048)),svg=assetSlice('/assets/menus/alley.webp',x,y,w,h,2172,724);
 const clip=svg.querySelector('clipPath')!,ns='http://www.w3.org/2000/svg',polygon=document.createElementNS(ns,'polygon');
 // Side diamonds retain their tips; the empty rectangle corners are omitted.
 polygon.setAttribute('points',label==='title'?`0,${h/2} 62,24 ${w/2-18},24 ${w/2},0 ${w/2+18},24 ${w-62},24 ${w},${h/2} ${w-62},${h-4} 62,${h-4}`:label==='Retour en ville'?`0,${h/2} 55,12 ${w/2-18},12 ${w/2},0 ${w/2+18},12 ${w-55},12 ${w},${h/2} ${w-55},${h-4} 55,${h-4}`:`0,${h/2} 50,8 ${w-50},8 ${w},${h/2} ${w-50},${h-4} 50,${h-4}`);
 clip.replaceChildren(polygon);svg.classList.add('native-button-art','alley-complete-art');svg.dataset.component=label;return svg;
}
