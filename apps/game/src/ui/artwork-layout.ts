import {assetSlice} from './assets';

type Region = [number, number, number, number];
/** Mobile reuses sections of the same artwork, with each live control mounted once. */
const sections: Record<string, Region[]> = {
 merchant:[[10,0,80,23],[6,23,70,12],[76,23,23,12],[3.5,35,47,22.5],[49.5,35,47,22.5],[3.5,57.5,47,22.5],[49.5,57.5,47,22.5],[27,80,46,8],[19,88,62,12]],
 forge:[[8,0,84,25],[7,25,86,12],[1,36,40,34],[60,36,38,34],[6.5,70,66,16],[71,70,24,16],[13,85.5,45,13.5],[57.5,86,29.5,12]],
 dashboard:[[8,0,84,18],[0,18,100,17],[0,35,50,17],[50,35,50,17],[0,52,50,18],[50,52,50,18],[0,69,50,18],[50,69,50,18],[10,87,80,13]],
 podium:[[10,0,80,23],[2,24,96,60],[12,85,79,15]],
 drinks:[[25,0,50,15],[6,15,29,34],[35,15,29,34],[64,15,30,34],[6,49,29,34],[35,49,29,34],[64,49,30,34],[28,83,45,17]],
 guard:[[7,0,86,31],[4,31,91,42],[5,73,90,14],[33,87,34,11]],
 robber:[[8,0,85,35],[6,35,88,40],[5,75,91,17]],
 techniques:[[15,0,70,16],[1.5,16,32.5,55.5],[33.5,16,32.5,55.5],[65.5,16,33,55.5],[18,71.5,64,18.5],[32,90,36,10]],
 combat:[[33,0,34,13],[0,1,34,18],[66,1,34,18],[41,13,18,6],[0,20,100,51],[27,71,46,10],[0,81,28.5,13],[27.5,81,24,13],[50,81,25,13],[73.5,81,26.5,13],[25,95,51,5]],
 tools:[[8,0,84,25],[4,25,92,37],[13,62,74,13],[21,75,60,11],[21,86,64,14]],
 destinations:[[8,0,84,25],[3,25,94,35],[15,60,70,11],[26,72,47,13],[13,86,77,14]],
 accessories:[[7,0,86,26],[11,26,77,24],[11,50,77,26],[25,77,50,8],[13,85,75,15]],
 departure:[[9,0,82,25],[10,25,42,31],[51,25,38,31],[11,56,78,11],[28,68,45,16],[12,85,77,15]],
 live:[[8,0,84,23],[10,23,80,22],[11,45,77,15],[11,60,39,24],[50,60,39,24],[10,84,80,16]],
 arena:[[10,0,80,25],[0,25,50,51],[50,25,50,51],[25,77,50,20]],
 castle:[[10,0,80,25],[2,25,32,52],[34,25,32,52],[66,25,32,52],[25,78,50,18]],
 games:[[12,0,76,25],[3,25,31,31],[34,25,31,31],[65,25,32,31],[3,60,31,31],[34,60,31,31],[65,60,32,31],[28,91,45,8]],
 expedition:[[12,0,76,23],[2,23,32,54],[34,23,32,54],[66,23,32,54],[31,77,39,22]],
 casino:[[8,0,84,25],[0,25,34,25],[33,25,34,25],[66,25,34,25],[0,52,34,27],[33,52,34,27],[66,52,34,27]],
 tavern:[[0,42,35,28],[34,42,32,28],[65,42,35,28],[32,70,36,23]],
 alley:[[0,35,26,32],[25,35,25,32],[49,35,25,32],[73,35,27,32],[35,68,30,27]],
 thief:[[0,34,26,34],[25,34,25,34],[49,34,25,34],[73,34,27,34],[34,70,32,25]],
};

export function reflowArtwork(stage:HTMLElement,kind:string){
 if(innerWidth>600||!sections[kind])return;
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
  if(kind==='forge'&&index===4){
   // Keep the heading and corners at native proportions; only the empty wood body stretches.
   section.classList.add('forge-material-panel');section.style.aspectRatio='auto';section.style.height='150px';section.replaceChildren();
   for(const [part,sy,sh] of [['heading',720,70],['body',790,70],['base',860,30]] as const){
    const art=assetSlice(source,100,sy,1010,sh);art.classList.add('forge-panel-'+part);art.setAttribute('preserveAspectRatio','none');section.append(art);
   }
  }
  for(const node of overlays){
   if(node.dataset.reflowed)continue;
   const left=parseFloat(node.style.left),top=parseFloat(node.style.top),width=parseFloat(node.style.width),height=parseFloat(node.style.height);
   if(![left,top,width,height].every(Number.isFinite))continue;
   const cx=left+width/2,cy=top+height/2;
   if(cx<x||cx>x+w||cy<y||cy>y+h)continue;
   node.dataset.reflowed='true';
   Object.assign(node.style,{left:(left-x)/w*100+'%',top:(top-y)/h*100+'%',width:width/w*100+'%',height:height/h*100+'%'});
   if(kind==='forge'&&index===4&&node.classList.contains('forge-materials'))Object.assign(node.style,{left:'8%',top:'38px',width:'84%',height:'90px'});
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
  for(const n of Array.from(panel.querySelectorAll<HTMLElement>('.art-overlay,.art-hit'))){if(!n.style.left)continue;for(const key of ['left','top','width','height']){const v=n.style.getPropertyValue(key);if(v)n.style.setProperty(key,v,'important');}n.style.setProperty('position','absolute','important');}

  for(const input of Array.from(panel.querySelectorAll<HTMLInputElement>('.art-overlay input,.game-stake input'))){const base=parseFloat(getComputedStyle(input).fontSize),fit=input.clientWidth/Math.max(1,input.value.length*.65);if(input.clientWidth)input.style.setProperty('font-size',Math.max(11,Math.min(base,fit))+'px','important');}
  for(const n of Array.from(panel.querySelectorAll<HTMLElement>('.art-overlay:not(:has(input)):not(:has(svg))'))){
   if(!n.textContent?.trim()||!n.clientWidth||!n.clientHeight)continue;
   let font=parseFloat(getComputedStyle(n).fontSize);
   while(font>9&&(n.scrollWidth>n.clientWidth+1||n.scrollHeight>n.clientHeight+1)){
    font-=.5;n.style.setProperty('font-size',font+'px','important');
   }
  }
 });
}
