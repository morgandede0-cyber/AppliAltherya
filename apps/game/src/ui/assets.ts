export const uiAsset=(file:string)=>'/assets/ui/'+file;
export const merchantAssets={Histoire:'merchant-story.webp',Acheter:'merchant-buy.webp',Vendre:'merchant-sell.webp',Partir:'merchant-leave.webp'};
export const tabAssets:Record<string,string>={Outils:'tab-tools.webp',Consommables:'tab-consumables.webp',Divers:'tab-misc.webp','Bûcheron':'tab-woodcutter.webp',Mineur:'tab-miner.webp',Chasseur:'tab-hunter.webp',Histoire:'merchant-story.webp'};
export const hubAssets:Record<string,string>={'scene:tavern':'hub-tavern.webp','scene:forge':'hub-forge.webp','scene:castle':'hub-castle.webp','scene:arena':'hub-arena.webp','scene:market':'hub-market.webp','scene:bank':'hub-bank.webp',jobs:'hub-jobs.webp','scene:alley':'hub-alley.webp',gazette:'hub-board.webp',world:'hub-world.webp',profile:'hub-profile.webp'};
export function skinButton(button:HTMLButtonElement,file:string,label:string){
 const img=document.createElement('img');img.src=uiAsset(file);img.alt='';img.draggable=false;
 button.replaceChildren(img);button.setAttribute('aria-label',label);button.title=label;button.classList.add('image-button');return button;
}
export function skinFrameControl(button:HTMLButtonElement,part:'close'|'previous'|'next'){
 const ns='http://www.w3.org/2000/svg';const svg=document.createElementNS(ns,'svg');
 const boxes={close:'1410 48 120 112',previous:'5 430 90 112',next:'1442 430 90 112'};
 svg.setAttribute('viewBox',boxes[part]);svg.setAttribute('aria-hidden','true');svg.setAttribute('focusable','false');
 const image=document.createElementNS(ns,'image');image.setAttribute('href',uiAsset('shop-frame.webp'));image.setAttribute('width','1536');image.setAttribute('height','1024');svg.append(image);
 button.replaceChildren(svg);button.classList.add('image-button','frame-control');return button;
}

/** Explicit clipping keeps adjacent atlas cells out of letterboxed SVG viewports. */
let clips=0;
export function assetSlice(src:string,x:number,y:number,w:number,h:number,sourceW=1536,sourceH=1024){const ns='http://www.w3.org/2000/svg',s=document.createElementNS(ns,'svg');s.setAttribute('viewBox',`0 0 ${w} ${h}`);s.setAttribute('aria-hidden','true');s.setAttribute('focusable','false');const defs=document.createElementNS(ns,'defs'),clip=document.createElementNS(ns,'clipPath'),rect=document.createElementNS(ns,'rect'),id='asset-slice-'+(++clips);clip.id=id;rect.setAttribute('width',String(w));rect.setAttribute('height',String(h));clip.append(rect);defs.append(clip);s.append(defs);const im=document.createElementNS(ns,'image');im.setAttribute('href',src);im.setAttribute('x',String(-x));im.setAttribute('y',String(-y));im.setAttribute('width',String(sourceW));im.setAttribute('height',String(sourceH));im.setAttribute('clip-path',`url(#${id})`);s.append(im);return s;}
