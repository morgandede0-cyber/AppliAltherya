import {dressGuild} from './guild-menu';
import {recall,remember} from './session-preferences';
import {decoratePredator} from './predator-art';
import {approvedCard,decorateApproved} from './approved-art';
import {mountRealm,realmButton} from './realm-menu';
import {generatedItemArt} from './generated-item-art';
import {watchMenuSize} from './menu-layout';
import type {Snapshot} from '../activity';
import {categories,products,pageItems,clampQuantity,tradeBlock,tradeBody,type CommerceMode,type Product} from './commerce-model';
import {itemArt} from './item-art';
import {equipmentArt,resourceArt} from './catalog-art';
import './commerce.css';
import './commerce-live.css';

type Host={state:()=>Snapshot;trade:(body:Record<string,unknown>)=>Promise<string>;exit:()=>void;back:()=>void;sound:()=>void;switchMode:(mode:CommerceMode)=>void};
export function openCommerce(root:HTMLElement,mode:CommerceMode,host:Host){
 let category=categories(mode)[0],page=0,selected:Product|undefined,quantity=1,busy=false,message='',dead=false;
 const saved=recall(host.state().save_owner,'commerce:'+mode,{category,page});if(categories(mode).includes(saved.category))category=saved.category;page=saved.page;
 const el=(tag:string,cls='',text='')=>{const n=document.createElement(tag);n.className=cls;n.textContent=text;return n;};
 const art=(p:Product)=>['axe','pickaxe','spear','bag'].includes(p.icon)?equipmentArt(p.icon):generatedItemArt(p.name)??resourceArt(p.name)??itemArt(p.icon);
 const button=(label:string,fn:()=>void,disabled=false)=>{const b=realmButton(label,()=>{if(!busy){host.sound();fn();}},busy||disabled);return b;};
 async function submit(){
  if(!selected||busy||tradeBlock(selected,mode,host.state().balance.wallet,quantity))return;
  busy=true;draw();
  try{message=await host.trade(tradeBody(selected,mode,quantity));selected=undefined;}
  catch(e){message=String(e);}
  finally{busy=false;if(!dead)draw();}
 }
 function draw(){
  if(dead)return;remember(host.state().save_owner,'commerce:'+mode,{category,page});
  const scroll=root.dataset.kind==='market-'+mode?(root.querySelector('.realm-body')?.scrollTop??0):0,focused=root.contains(document.activeElement)?document.activeElement?.getAttribute('aria-label'):null;
  const {body,footer:realmFooter}=mountRealm(root,'market-'+mode,'Le marchand',busy);
  const stage=el('section','realm-commerce-stage');body.append(stage);const productGrid=el('div','realm-commerce-grid');
  const place=(node:HTMLElement,_x:number,_y:number,_w:number,_h:number)=>{stage.append(node);return node;};
  const wallet=el('div','realm-muted approved-wallet',`Portefeuille : ${host.state().balance.wallet} Gold`);wallet.setAttribute('aria-label','Portefeuille');stage.append(wallet);
  const modes=el('nav','guild-commerce-modes');modes.setAttribute('aria-label','Commerce');
  for(const [value,label] of [['buy','Acheter'],['sell','Vendre'],['story','Histoire']] as const){const b=button(label,()=>host.switchMode(value));b.setAttribute('aria-pressed',String(mode===value));modes.append(b);}stage.append(modes);
  const tabs=el('nav','realm-tabs');tabs.setAttribute('role','tablist');tabs.setAttribute('aria-label',mode==='sell'?'Métiers':'Rayons');stage.append(tabs);
  categories(mode).forEach(c=>{
   const b=document.createElement('button');b.type='button';b.className='native-tab';b.disabled=busy;b.setAttribute('role','tab');b.setAttribute('aria-label',c);b.setAttribute('aria-selected',String(c===category));b.classList.toggle('selected',c===category);b.onclick=()=>{category=c;page=0;selected=undefined;message='';draw();};
   b.textContent=c;
   tabs.append(b);
  });
  const all=products(host.state(),mode).filter(p=>p.category===category||(mode==='buy'&&category==='Outils'&&p.icon==='bag')).sort((a,b)=>mode==='buy'&&category==='Outils'?['axe','pickaxe','spear','bag'].indexOf(a.icon)-['axe','pickaxe','spear','bag'].indexOf(b.icon):0),slice=pageItems(all,page);page=slice.page;
  stage.append(productGrid);
  for(let i=0;i<4;i++){
   const product=slice.items[i],card=el('article','realm-product'+(!product?' empty-product':''));productGrid.append(card);approvedCard(card);
   if(!product){card.append(el('span','native-empty',slice.items.length?'Emplacement libre':mode==='sell'?'Aucune ressource':category==='Consommables'?'Aucun consommable':'Aucun objet'));continue;}
   const icon=el('div','realm-item-icon');icon.append(art(product));card.append(icon);
   const info=el('div','realm-item-info');info.append(el('h3','',product.name.replace(/^[^\p{L}\p{N}]+/u,'')));
   if(product.chapter)info.append(el('span','merchant-chapter',`Chapitre ${product.chapter}`));
   info.append(el('p','merchant-price',`${product.price} Gold${mode==='sell'?' / unité':''}`));
   if(mode==='sell')info.append(el('small','',`Stock : ${product.stock}`));else info.append(el('small','approved-item-description',({axe:'Pour le bûcheronnage',pickaxe:'Pour le minage',spear:'Pour la chasse',bag:'Pour vos expéditions'} as Record<string,string>)[product.icon]??(product.chapter?'Objet du chapitre '+product.chapter:'')));card.append(info);
   const block=tradeBlock(product,mode,host.state().balance.wallet,1),label=block||(mode==='sell'?'Vendre':'Acheter');
   const trade=document.createElement('button');trade.type='button';trade.className='native-trade-button';trade.textContent=label;trade.setAttribute('aria-label',label);trade.title=label+' '+product.name;trade.disabled=busy||!!block;trade.onclick=()=>{selected=product;quantity=1;draw();};card.append(trade);
  }
  const pager=place(el('nav','realm-tabs'),28,80.5,44,7);pager.setAttribute('aria-label','Pages des objets');
  for(const [label,step] of [['Objets précédents',-1],['Objets suivants',1]] as const){const b=document.createElement('button');b.type='button';b.className='realm-button';b.textContent=label==='Objets précédents'?'←':'→';b.setAttribute('aria-label',label);b.disabled=busy||(step===-1?page===0:page===slice.last);b.onclick=()=>{page+=step;draw();};pager.append(b);}
  pager.append(el('span','native-page-label',`Page ${page+1} / ${slice.last+1}`));
  const footer=realmFooter;
  const back=document.createElement('button');back.className='native-market-back';back.setAttribute('aria-label','Retour au marchand');back.textContent='Retour au marchand';back.disabled=busy;back.onclick=host.back;footer.append(back);

  if(message){const status=el('p','merchant-status',message);status.setAttribute('role','status');root.append(status);}
  if(selected){
   const backdrop=el('div','merchant-modal realm-trade-modal'),dialog=el('section','merchant-confirm realm-trade-dialog');dialog.setAttribute('role','dialog');dialog.setAttribute('aria-modal','true');dialog.setAttribute('aria-label',mode==='sell'?'Confirmer la vente':'Confirmer l’achat');
   dialog.append(el('h2','',mode==='sell'?'Confirmer la vente':'Confirmer l’achat'),art(selected),el('p','',selected.name));
   if(selected.chapter)dialog.append(el('span','merchant-chapter',`Chapitre ${selected.chapter}`));
   if(mode==='sell'){
    const q=el('label','trade-quantity','Quantité : '),input=document.createElement('input');input.type='number';input.min='1';input.max=String(selected.stock);input.step='1';input.value=String(quantity);input.setAttribute('aria-label','Quantité à vendre');input.disabled=busy;
    input.onchange=()=>{quantity=clampQuantity(Number(input.value),selected!.stock);input.value=String(quantity);const total=dialog.querySelector('.trade-total');if(total)total.textContent=`${quantity*selected!.price} Gold`;const confirm=dialog.querySelector<HTMLButtonElement>('.realm-trade-actions button');if(confirm)confirm.disabled=busy||!!tradeBlock(selected!,mode,host.state().balance.wallet,quantity);};q.append(input);dialog.append(q);
   }
   dialog.append(el('strong','trade-total',`${quantity*selected.price} Gold`));
   const actions=el('div','realm-trade-actions');actions.append(button(busy?'En cours…':'Confirmer',()=>void submit(),!!tradeBlock(selected,mode,host.state().balance.wallet,quantity)),button('Annuler',()=>{selected=undefined;draw();}));dialog.append(actions);backdrop.append(dialog);root.append(backdrop);stage.inert=true;
   requestAnimationFrame(()=>dialog.querySelector<HTMLButtonElement>('button:not(:disabled)')?.focus({preventScroll:true}));
  }else if(focused)Array.from(root.querySelectorAll<HTMLElement>('[aria-label]')).find(n=>n.getAttribute('aria-label')===focused)?.focus({preventScroll:true});
  decorateApproved(root);decoratePredator(root);dressGuild(root,'market-'+mode,host.state());body.scrollTop=scroll;
 }
 const stopSize=watchMenuSize(root,draw);
 root.onkeydown=e=>{
  if(e.key==='Escape'&&!busy){e.preventDefault();if(selected){selected=undefined;draw();}else host.exit();}
  if(e.key==='Tab'){const scope=root.querySelector('.merchant-confirm')??root;const nodes=Array.from(scope.querySelectorAll<HTMLElement>('button:not(:disabled),input:not(:disabled)')),first=nodes[0],last=nodes.at(-1);if(e.shiftKey&&document.activeElement===first){e.preventDefault();last?.focus();}else if(!e.shiftKey&&document.activeElement===last){e.preventDefault();first?.focus();}}
 };
 draw();root.scrollTop=0;root.querySelector<HTMLButtonElement>('button:not(:disabled)')?.focus({preventScroll:true});
 return{update(){if(!busy&&!(document.activeElement instanceof HTMLInputElement&&root.contains(document.activeElement))){if(selected)selected=products(host.state(),mode).find(p=>p.key===selected!.key);draw();}},destroy(){dead=true;stopSize();document.body.classList.remove('illustrated-open');root.onkeydown=null;}};
}
