import {assetSlice} from './assets';
type Rect=readonly[number,number,number,number];
type Sign={desktop:Rect;mobile:Rect;shape?:'blackjack'|'slots'};
export const casinoSignRects:Record<string,Sign>={
 russian:{desktop:[312,148,210,64],mobile:[129,195,287,64]},
 horses:{desktop:[1090,150,232,62],mobile:[609,196,288,66]},
 roulette:{desktop:[718,523,257,66],mobile:[386,801,257,77]},
 blackjack:{desktop:[137,715,315,124],mobile:[84,1213,302,85],shape:'blackjack'},
 slots:{desktop:[1423,179,219,91],mobile:[608,1211,349,85],shape:'slots'},
 leave:{desktop:[642,829,385,67],mobile:[254,1387,519,109]}
};
export function casinoSignBounds(key:string,portrait=false){const [x,y,w,h]=casinoSignRects[key][portrait?'mobile':'desktop'],sw=portrait?1024:1672,sh=portrait?1536:941;return[(x+w/2)/sw*100,(y+h/2)/sh*100,w/sw*100,h/sh*100];}
/** Original sign pixels, clipped into an independent transparent SVG control. */
export function casinoSignArt(key:string,portrait=false){
 const sign=casinoSignRects[key],[x,y,w,h]=sign[portrait?'mobile':'desktop'];
 const svg=assetSlice(portrait?'/assets/casino-live/room-mobile.png':'/assets/scenes/casino-clandestine-live.png',x,y,w,h,portrait?1024:1672,portrait?1536:941);svg.classList.add('casino-sign-art',portrait?'casino-sign-mobile':'casino-sign-desktop');
 const normal=[[0,50],[8,32],[7,20],[15,18],[18,0],[82,0],[86,18],[94,20],[92,35],[100,50],[92,66],[94,80],[84,82],[82,100],[18,100],[15,83],[7,81],[8,67]];
 const angled=sign.shape==='blackjack'?[[1,57],[7,47],[10,31],[86,2],[91,14],[97,19],[100,36],[94,49],[90,67],[15,97],[8,84],[3,80]]:[[1,49],[7,36],[8,21],[89,1],[96,16],[98,35],[100,51],[93,68],[92,80],[11,99],[7,83],[0,76]];
 const points=!portrait&&sign.shape?angled:normal,polygon=document.createElementNS('http://www.w3.org/2000/svg','polygon');polygon.setAttribute('points',points.map(([px,py])=>`${px/100*w},${py/100*h}`).join(' '));svg.querySelector('clipPath')!.replaceChildren(polygon);return svg;
}
