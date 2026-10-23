import {node} from './menu-kit';
import './popie.css';
export type PopieState={day:string;reset_at:number;order_done:boolean;orders:{key:string;item:string;quantity:number;gold:number;xp:number;owned:number}[];exchanges:{key:string;give:string;give_qty:number;receive:string;receive_qty:number;owned:number}[];exchanges_left:number;mission_done:boolean;mission:null|{id:string;route:string;title:string;ready_at:number;gold:number;xp:number;chance:number;ready:boolean};routes:{key:string;title:string;duration:number;chance:number;gold:number;xp:number}[];cargo:{item:string;quantity:number;owned:number};last_result:string};
export type PopieView={tab:'orders'|'exchange'|'missions';confirm?:{action:string;key:string;text:string}};
export function renderPopie(root:HTMLElement,p:PopieState,view:PopieView,opts:{busy:boolean;now:()=>number;notice:string;run:(action:string,key:string)=>void;redraw:()=>void}){
 const wrap=node('section','popie-counter');wrap.setAttribute('aria-label','Comptoir de Popie');root.append(wrap);
 const button=(label:string,fn:()=>void,disabled=false)=>{const b=document.createElement('button');b.type='button';b.className='popie-button';b.textContent=label;b.setAttribute('aria-label',label);b.disabled=disabled||opts.busy;b.onclick=fn;return b;};
 const tabs=node('div','popie-tabs');tabs.setAttribute('role','group');tabs.setAttribute('aria-label','Services de Popie');for(const [key,label] of [['orders','Commandes'],['exchange','Échanges'],['missions','Livraisons']] as const){const b=button(label,()=>{view.tab=key;view.confirm=undefined;opts.redraw();});b.setAttribute('aria-pressed',String(view.tab===key));tabs.append(b);}wrap.append(tabs);
 const paper=node('div','popie-sheet');wrap.append(paper);const content=node('div','popie-content');paper.append(content);
 content.append(node('h3','',view.tab==='orders'?'Le carnet de commandes':view.tab==='exchange'?'Le troc de Popie':'Les chemins de contrebande'));
 const prepare=(action:string,key:string,text:string)=>{view.confirm={action,key,text};opts.redraw();};
 if(opts.notice){const n=node('p','popie-notice',opts.notice);n.setAttribute('role','status');content.append(n);}
 if(view.confirm){const c=node('section','popie-confirm');c.setAttribute('aria-label','Confirmation de la transaction');c.append(node('p','',view.confirm.text),button('Confirmer',()=>opts.run(view.confirm!.action,view.confirm!.key)),button('Annuler',()=>{view.confirm=undefined;opts.redraw();}));content.append(c);}
 else if(view.tab==='orders'){
  content.append(node('p','popie-hint','Une commande par jour, parmi ces trois demandes. Renouvellement à minuit, heure de Paris.'));
  if(p.order_done)content.append(node('strong','popie-complete','Commande du jour honorée'));
  for(const o of p.orders){const row=node('article','popie-row');row.append(node('strong','',`${o.quantity} × ${o.item}`),node('p','',`Inventaire : ${o.owned} · ${o.gold} Gold + ${o.xp} XP`),button('Livrer '+o.item,()=>prepare('port_popie_order',o.key,`Remettre ${o.quantity} × ${o.item} à Popie contre ${o.gold} Gold et ${o.xp} XP ? Les objets seront retirés de votre inventaire.`),p.order_done||o.owned<o.quantity));content.append(row);}
 }else if(view.tab==='exchange'){
  content.append(node('p','popie-hint',`${p.exchanges_left}/3 échanges restants aujourd’hui. Les objets d’histoire et de quête sont exclus.`));
  for(const o of p.exchanges){const row=node('article','popie-row');row.append(node('strong','',`${o.give_qty} × ${o.give}`),node('p','',`Recevoir ${o.receive_qty} × ${o.receive} · En stock : ${o.owned}`),button('Échanger '+o.give,()=>prepare('port_popie_exchange',o.key,`Échanger ${o.give_qty} × ${o.give} contre ${o.receive_qty} × ${o.receive} ?`),!p.exchanges_left||o.owned<o.give_qty));content.append(row);}
 }else{
  content.append(node('p','popie-hint',`Un convoyage par jour. Cargaison : ${p.cargo.quantity} × ${p.cargo.item}, retirés au départ. Vous en possédez ${p.cargo.owned}.`));
  if(p.mission){const m=p.mission;const row=node('article','popie-row popie-mission');row.append(node('strong','',m.title));const timer=node('p','popie-timer');timer.dataset.popieDeadline=String(m.ready_at);timer.setAttribute('role','timer');row.append(timer);const claim=button('Récupérer le résultat',()=>opts.run('port_popie_claim',m.id));claim.dataset.popieClaim=String(m.ready_at);row.append(claim);content.append(row);}
  else if(p.mission_done)content.append(node('strong','popie-complete','Convoyage du jour terminé'));
  else for(const r of p.routes){const row=node('article','popie-row');row.append(node('strong','',r.title),node('p','',`${r.duration/60} min · ${r.chance} % de réussite · ${r.gold} Gold + ${r.xp} XP`),node('p','popie-risk',r.chance<100?'En cas d’échec : cargaison perdue, aucune récompense.':'Livraison garantie à la fin du trajet.'),button(r.chance===100?'Choisir le trajet sûr':'Choisir le trajet risqué',()=>prepare('port_popie_start',r.key,`Confier ${p.cargo.quantity} × ${p.cargo.item} pour « ${r.title} » ? ${r.chance} % de réussite. ${r.chance<100?'La cargaison est perdue en cas d’échec.':'Récompense garantie.'} Un seul départ par jour.`),p.cargo.owned<p.cargo.quantity));content.append(row);}
  if(p.last_result)content.append(node('p','popie-notice',p.last_result));
 }
 function tick(){const now=opts.now();for(const n of Array.from(wrap.querySelectorAll<HTMLElement>('[data-popie-deadline]'))){const seconds=Math.max(0,Math.ceil(Number(n.dataset.popieDeadline)-now));n.textContent=seconds?`Convoyage en cours · ${Math.floor(seconds/60)} min ${String(seconds%60).padStart(2,'0')} s`:'Le convoyeur est revenu.';}for(const b of Array.from(wrap.querySelectorAll<HTMLButtonElement>('[data-popie-claim]')))b.disabled=opts.busy||Number(b.dataset.popieClaim)>now;}
 tick();return tick;
}
