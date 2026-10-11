import {assetSlice} from './assets';

type Region = [number, number, number, number];
/** Mobile reuses sections of the same artwork, with each live control mounted once. */
const sections: Record<string, Region[]> = {
 merchant:[[14,0,72,23],[7,23,69,12],[77,23,21,12],[5.5,35,44,22.5],[50.5,35,44,22.5],[5.5,57.5,44,22.5],[50.5,57.5,44,22.5],[27,80,46,8],[19,88,62,12]],
 forge:[[8,0,84,25],[7,25,86,13],[3,38,40,30],[61,38,37,30],[8,69,65,16],[77,68,20,18],[10,86,80,13]],
 dashboard:[[8,0,84,18],[4,18,92,16],[4,35,44,17],[51,35,45,17],[4,52,44,18],[51,52,45,18],[4,69,44,18],[51,69,45,18],[10,87,80,13]],
 podium:[[10,0,80,23],[2,24,96,60],[12,85,79,15]],
 drinks:[[25,0,50,15],[6,15,29,34],[35,15,29,34],[64,15,30,34],[6,49,29,34],[35,49,29,34],[64,49,30,34],[28,83,45,17]],
 guard:[[7,0,86,31],[4,31,91,42],[5,73,90,14],[33,87,34,11]],
 robber:[[8,0,85,35],[6,35,88,40],[5,75,91,17]],
 techniques:[[15,0,70,18],[3,18,31,62],[35,18,31,62],[67,18,30,62],[14,81,72,19]],
 combat:[[0,0,100,21],[0,21,100,48],[11,69,78,16],[1,85,27,10],[28,85,26,10],[54,85,26,10],[80,85,19,10],[25,95,51,5]],
 tools:[[8,0,84,25],[4,25,92,37],[13,62,74,13],[21,75,60,11],[21,86,64,14]],
 destinations:[[8,0,84,25],[3,25,94,35],[15,60,70,11],[26,72,47,13],[13,86,77,14]],
 accessories:[[7,0,86,26],[11,26,77,24],[11,50,77,26],[25,77,50,8],[13,85,75,15]],
 departure:[[9,0,82,25],[10,25,42,31],[51,25,38,31],[11,56,78,11],[28,68,45,16],[12,85,77,15]],
 live:[[8,0,84,23],[10,23,80,22],[11,45,77,15],[11,60,39,24],[50,60,39,24],[10,84,80,16]],
 arena:[[10,0,80,25],[2,25,48,51],[50,25,48,51],[25,77,50,20]],
 castle:[[10,0,80,25],[2,25,32,52],[34,25,32,52],[66,25,32,52],[25,78,50,18]],
 games:[[12,0,76,25],[3,25,31,31],[34,25,31,31],[65,25,32,31],[3,60,31,31],[34,60,31,31],[65,60,32,31],[28,91,45,8]],
 expedition:[[12,0,76,23],[2,23,32,54],[34,23,32,54],[66,23,32,54],[31,77,39,22]],
 casino:[[8,0,84,25],[0,25,34,25],[33,25,34,25],[66,25,34,25],[0,52,34,27],[33,52,34,27],[66,52,34,27]],
 tavern:[[0,42,35,28],[34,42,32,28],[65,42,35,28],[32,70,36,23]],
 alley:[[0,35,26,32],[25,35,25,32],[49,35,25,32],[73,35,27,32],[35,68,30,27]],
 thief:[[0,34,26,34],[25,34,25,34],[49,34,25,34],[73,34,27,34],[34,70,32,25]],
};

export function reflowArtwork(stage:HTMLElement,kind:string){
 if(innerWidth>=600||!sections[kind])return;
 const img=stage.querySelector<HTMLImageElement>(':scope > .art-image');
 if(!img)return;
 const source=img.getAttribute('src')!;
 const sourceWidth=['alley','thief'].includes(kind)?2172:kind==='tavern'?1984:1536;
 const sourceHeight=['alley','thief'].includes(kind)?724:kind==='tavern'?793:1024;
 const overlays=Array.from(stage.children).filter((n):n is HTMLElement=>n instanceof HTMLElement&&n!==img&&!n.classList.contains('art-extra'));
 stage.classList.add('art-mobile-stack');img.remove();
 for(const [index,[x,y,w,h]] of sections[kind].entries()){
  const section=document.createElement('section');section.className='art-section';section.dataset.section=String(index);
  section.append(assetSlice(source,x/100*sourceWidth,y/100*sourceHeight,w/100*sourceWidth,h/100*sourceHeight,sourceWidth,sourceHeight));
  section.style.aspectRatio=String(w*sourceWidth/(h*sourceHeight));
  for(const node of overlays){
   if(node.dataset.reflowed)continue;
   const left=parseFloat(node.style.left),top=parseFloat(node.style.top),width=parseFloat(node.style.width),height=parseFloat(node.style.height);
   if(![left,top,width,height].every(Number.isFinite))continue;
   const cx=left+width/2,cy=top+height/2;
   if(cx<x||cx>x+w||cy<y||cy>y+h)continue;
   node.dataset.reflowed='true';
   Object.assign(node.style,{left:(left-x)/w*100+'%',top:(top-y)/h*100+'%',width:width/w*100+'%',height:height/h*100+'%'});
   section.append(node);
  }
  stage.append(section);
 }
 for(const node of overlays)if(!node.dataset.reflowed){stage.append(node);node.classList.add('art-unplaced');}
}

/** Shrink only overflowing text, rather than covering or truncating the original frames. */
export function fitArtworkText(panel:HTMLElement){
 requestAnimationFrame(()=>{
  if(!panel.isConnected)return;
  for(const n of Array.from(panel.querySelectorAll<HTMLElement>('.art-overlay:not(:has(input)):not(:has(svg))'))){
   if(!n.textContent?.trim()||!n.clientWidth||!n.clientHeight)continue;
   let font=parseFloat(getComputedStyle(n).fontSize);
   while(font>9&&(n.scrollWidth>n.clientWidth+1||n.scrollHeight>n.clientHeight+1)){
    font-=.5;n.style.fontSize=font+'px';
   }
  }
 });
}
