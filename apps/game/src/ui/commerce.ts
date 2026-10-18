import {generatedItemArt} from './generated-item-art';
import {composeBlankCommerce} from './blank-compose';
import {sizeMenu,watchMenuSize} from './menu-layout';
import type {Snapshot} from '../activity';
import {categories,products,pageItems,clampQuantity,tradeBlock,tradeBody,type CommerceMode,type Product} from './commerce-model';
import {itemArt} from './item-art';
import {equipmentArt,resourceArt} from './catalog-art';
import {skinButton,tabAssets} from './assets';
import {ornamentButton} from './menu-kit';
import {reflowArtwork,fitArtworkText} from './artwork-layout';
import './commerce.css';
import './commerce-live.css';

type Host={state:()=>Snapshot;trade:(body:Record<string,unknown>)=>Promise<string>;exit:()=>void;back:()=>void;sound:()=>void;switchMode:(mode:CommerceMode)=>void};
export function openCommerce(root:HTMLElement,mode:CommerceMode,host:Host){
 let category=categories(mode)[0],page=0,selected:Product|undefined,quantity=1,busy=false,message='',dead=false;
 const el=(tag:string,cls='',text='')=>{const n=document.createElement(tag);n.className=cls;n.textContent=text;return n;};
 const art=(p:Product)=>['axe','pickaxe','spear','bag'].includes(p.icon)?equipmentArt(p.icon):generatedItemArt(p.name)??resourceArt(p.name)??itemArt(p.icon);
 const button=(label:string,fn:()=>void,disabled=false)=>{const b=ornamentButton(label,()=>{if(!busy){host.sound();fn();}},busy||disabled);return b;};
 async function submit(){
  if(!selected||busy||tradeBlock(selected,mode,host.state().balance.wallet,quantity))return;
  busy=true;draw();
  try{message=await host.trade(tradeBody(selected,mode,quantity));selected=undefined;}
  catch(e){message=String(e);}
  finally{busy=false;if(!dead)draw();}
 }
 function draw(){
  if(dead)return;
  const scroll=root.dataset.kind==='market-'+mode?root.scrollTop:0,focused=root.contains(document.activeElement)?document.activeElement?.getAttribute('aria-label'):null;
  root.hidden=false;root.dataset.kind='market-'+mode;root.className='commerce-panel native-commerce';sizeMenu(root,1.5,1180);
  root.replaceChildren();root.setAttribute('aria-busy',String(busy));root.setAttribute('aria-label',mode==='sell'?'Vendre au marché':mode==='story'?'Objets d’histoire':'Boutique de Legacy');document.body.classList.add('illustrated-open');
  const stage=el('section','art-stage commerce-art');root.append(stage);
  const image=new Image();image.src='/assets/catalog/merchant-blank.webp';image.className='art-image';image.alt='Marchand de IV';stage.append(image);
  if(mode!=='buy'){const ns='http://www.w3.org/2000/svg',defs=document.createElementNS(ns,'svg'),clip=document.createElementNS(ns,'clipPath'),path=document.createElementNS(ns,'path'),id='merchant-tabs-'+Math.random().toString(36).slice(2);defs.setAttribute('width','0');defs.setAttribute('height','0');defs.style.position='absolute';clip.id=id;clip.setAttribute('clipPathUnits','objectBoundingBox');path.setAttribute('d','M0 0H1V1H0Z M.065 .23H.77V.35H.065Z');path.setAttribute('clip-rule','evenodd');path.setAttribute('fill-rule','evenodd');clip.append(path);defs.append(clip);stage.append(defs);image.style.setProperty('clip-path',`url(#${id})`,'important');}

  const place=(node:HTMLElement,x:number,y:number,w:number,h:number)=>{Object.assign(node.style,{left:x+'%',top:y+'%',width:w+'%',height:h+'%'});stage.append(node);return node;};
  const wallet=place(el('div','art-overlay merchant-wallet',`${host.state().balance.wallet} Gold`),85,30,11,4);
  wallet.setAttribute('aria-label','Portefeuille');
  const tabs=place(el('nav','merchant-tabs'),7,23,69,12);tabs.setAttribute('role','tablist');tabs.setAttribute('aria-label',mode==='sell'?'Métiers':'Rayons');
  categories(mode).forEach((c,i)=>{
   const b=document.createElement('button');b.type='button';b.className='native-tab';b.disabled=busy;b.setAttribute('role','tab');b.setAttribute('aria-label',c);b.setAttribute('aria-selected',String(c===category));b.classList.toggle('selected',c===category);b.onclick=()=>{category=c;page=0;selected=undefined;message='';draw();};
   if(mode==='buy')b.classList.add('native-baked-tab');else skinButton(b,tabAssets[c],c);
   tabs.append(b);
  });
  const all=products(host.state(),mode).filter(p=>p.category===category),slice=pageItems(all,page);page=slice.page;
  for(let i=0;i<4;i++){
   const product=slice.items[i],card=el('article','merchant-card native-product'+(!product?' empty-product':''));place(card,i%2===0?5.5:50.5,i<2?35:57.5,44,22.5);
   if(!product){card.append(el('span','native-empty',slice.items.length?'Emplacement libre':mode==='sell'?'Aucune ressource':category==='Consommables'?'Aucun consommable':'Aucun objet'));continue;}
   const icon=el('div','merchant-item-icon');icon.append(art(product));card.append(icon);
   const info=el('div','merchant-item-info');info.append(el('h3','',product.name.replace(/^[^\p{L}\p{N}]+/u,'')));
   if(product.chapter)info.append(el('span','merchant-chapter',`Chapitre ${product.chapter}`));
   info.append(el('p','merchant-price',`${product.price} Gold${mode==='sell'?' / unité':''}`));
   if(mode==='sell')info.append(el('small','',`Stock : ${product.stock}`));card.append(info);
   const block=tradeBlock(product,mode,host.state().balance.wallet,1),label=block||(mode==='sell'?'Vendre':'Acheter');
   const trade=document.createElement('button');trade.type='button';trade.className='native-trade-button';trade.textContent=label;trade.setAttribute('aria-label',label);trade.title=label+' '+product.name;trade.disabled=busy||!!block;trade.onclick=()=>{selected=product;quantity=1;draw();};card.append(trade);
  }
  const pager=place(el('nav','merchant-pager'),28,80.5,44,7);pager.setAttribute('aria-label','Pages des objets');
  for(const [label,step] of [['Objets précédents',-1],['Objets suivants',1]] as const){const b=document.createElement('button');b.type='button';b.className='native-page-hit';b.setAttribute('aria-label',label);b.disabled=busy||(step===-1?page===0:page===slice.last);b.onclick=()=>{page+=step;draw();};pager.append(b);}
  pager.append(el('span','native-page-label',`Page ${page+1} / ${slice.last+1}`));
  const footer=place(el('div','merchant-footer'),20,88,60,11);
  const switcher=document.createElement('button');switcher.className='native-market-switch';switcher.textContent=mode==='sell'?'Acheter':'Vendre';switcher.setAttribute('aria-label',switcher.textContent);switcher.disabled=busy;switcher.onclick=()=>host.switchMode(mode==='sell'?'buy':'sell');
  const back=document.createElement('button');back.className='native-market-back';back.setAttribute('aria-label','Retour au marché');back.disabled=busy;back.onclick=host.back;footer.append(switcher,back);
  reflowArtwork(stage,'merchant');fitArtworkText(root);
  if(message){const status=el('p','merchant-status',message);status.setAttribute('role','status');root.append(status);}
  if(selected){
   const backdrop=el('div','merchant-modal'),dialog=el('section','merchant-confirm mission-parchment');dialog.setAttribute('role','dialog');dialog.setAttribute('aria-modal','true');dialog.setAttribute('aria-label',mode==='sell'?'Confirmer la vente':'Confirmer l’achat');
   dialog.append(el('h2','',mode==='sell'?'Confirmer la vente':'Confirmer l’achat'),art(selected),el('p','',selected.name));
   if(selected.chapter)dialog.append(el('span','merchant-chapter',`Chapitre ${selected.chapter}`));
   if(mode==='sell'){
    const q=el('label','trade-quantity','Quantité : '),input=document.createElement('input');input.type='number';input.min='1';input.max=String(selected.stock);input.step='1';input.value=String(quantity);input.setAttribute('aria-label','Quantité à vendre');input.disabled=busy;
    input.onchange=()=>{quantity=clampQuantity(Number(input.value),selected!.stock);draw();};q.append(input);dialog.append(q);
   }
   dialog.append(el('strong','trade-total',`${quantity*selected.price} Gold`));
   const actions=el('div','trade-confirm-actions');actions.append(button(busy?'En cours…':'Confirmer',()=>void submit(),!!tradeBlock(selected,mode,host.state().balance.wallet,quantity)),button('Annuler',()=>{selected=undefined;draw();}));dialog.append(actions);backdrop.append(dialog);root.append(backdrop);stage.inert=true;
   requestAnimationFrame(()=>dialog.querySelector<HTMLButtonElement>('button:not(:disabled)')?.focus({preventScroll:true}));
  }else if(focused)Array.from(root.querySelectorAll<HTMLElement>('[aria-label]')).find(n=>n.getAttribute('aria-label')===focused)?.focus({preventScroll:true});
  composeBlankCommerce(root,host.state());root.scrollTop=scroll;
 }
 const stopSize=watchMenuSize(root,draw);
 root.onkeydown=e=>{
  if(e.key==='Escape'&&!busy){e.preventDefault();if(selected){selected=undefined;draw();}else host.exit();}
  if(e.key==='Tab'){const scope=root.querySelector('.merchant-confirm')??root;const nodes=Array.from(scope.querySelectorAll<HTMLElement>('button:not(:disabled),input:not(:disabled)')),first=nodes[0],last=nodes.at(-1);if(e.shiftKey&&document.activeElement===first){e.preventDefault();last?.focus();}else if(!e.shiftKey&&document.activeElement===last){e.preventDefault();first?.focus();}}
 };
 draw();root.scrollTop=0;root.querySelector<HTMLButtonElement>('button:not(:disabled)')?.focus({preventScroll:true});
 return{update(){if(!busy&&!(document.activeElement instanceof HTMLInputElement&&root.contains(document.activeElement))){if(selected)selected=products(host.state(),mode).find(p=>p.key===selected!.key);draw();}},destroy(){dead=true;stopSize();document.body.classList.remove('illustrated-open');root.onkeydown=null;}};
}
