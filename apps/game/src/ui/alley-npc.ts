import type {Snapshot} from '../activity';
import {node,assetSlice,trapMenu} from './menu-kit';
import './alley-npc.css';
type Host={state:()=>Snapshot;mutate:(body:Record<string,unknown>)=>Promise<string>;route:(key:string)=>void};
export const alleyNpcKinds=new Set(['thief','robber','guard']);
export function openAlleyNpc(panel:HTMLElement,kind:string,host:Host){
 let dead=false,busy=false,dialog=false,message='',guess='',snapshot:Snapshot|null=null,received=Date.now();
 const title=kind==='thief'?'Le voleur':kind==='robber'?'Le braqueur':'Le vigile';
 const back=()=>{if(!busy)host.route('alley');};
 function button(label:string,fn:()=>void,disabled=false,wood=false){const b=document.createElement('button');b.type='button';b.className='alley-control';b.setAttribute('aria-label',label);b.disabled=disabled||busy;b.append(assetSlice('/assets/alley-live/controls.png',...(wood?[32,606,760,169]:[26,202,756,177]) as [number,number,number,number]),node('span','',label));b.onclick=()=>{if(!b.disabled)fn();};return b;}
 const remaining=(n:number)=>Math.max(0,Math.ceil(n-(Date.now()-received)/1000));
 async function run(body:Record<string,unknown>,after?:()=>void){if(busy||dead)return;busy=true;message='';draw();try{message=await host.mutate(body);if(!dead)after?.();}catch(e){message=e instanceof Error?e.message:String(e);}finally{busy=false;if(!dead)draw();}}
 function closeDialog(){if(busy)return;dialog=false;draw();panel.querySelector<HTMLButtonElement>('.alley-actions button:not(:disabled)')?.focus();}
 function showDialog(){dialog=true;message='';draw();panel.querySelector<HTMLElement>('.alley-sheet input,.alley-sheet button:not(:disabled)')?.focus();}
 function notice(){const p=node('p','alley-notice art-notice',message);p.setAttribute('role','status');return p;}
 function enter(){if(!dead&&host.state().alley.access.valid)host.route('casino');}
 function draw(){if(dead)return;const s=host.state(),a=s.alley;if(snapshot!==s){snapshot=s;received=Date.now();}const focused=panel.contains(document.activeElement)?document.activeElement?.getAttribute('aria-label'):null;
 panel.hidden=false;panel.className='alley-npc alley-'+kind;panel.dataset.kind=kind;panel.removeAttribute('style');panel.setAttribute('aria-label',title);panel.setAttribute('aria-busy',String(busy));panel.replaceChildren();document.body.classList.add('illustrated-open');
 const scenery=node('div','alley-scenery');scenery.style.backgroundImage=`url('/assets/scenes/alley-${kind}-live.png')`;panel.append(scenery);
 const heading=node('h2','alley-title');heading.append(assetSlice('/assets/alley-live/controls.png',32,606,760,169),node('span','',title));panel.append(heading);
 const actions=node('div','alley-actions');panel.append(actions);
 if(kind==='thief'){
 actions.append(button('Petit larcin',()=>void run({action:'larceny'}),remaining(a.larceny_remaining)>0||remaining(a.ban_remaining)>0),button('Voler un PNJ',showDialog,remaining(a.ban_remaining)>0),button('Voler un joueur',()=>{},true));
 const crime=button('Commettre un crime',()=>void run({action:'crime'}),remaining(a.ban_remaining)>0);crime.classList.add('alley-secondary');actions.append(crime);
 if(remaining(a.ban_remaining)>0||remaining(a.larceny_remaining)>0)actions.append(node('p','alley-caption',`Disponible dans ${remaining(a.ban_remaining)>0?remaining(a.ban_remaining):remaining(a.larceny_remaining)} s`));
 }else if(kind==='robber')actions.append(button('Planifier un braquage',showDialog));
 else{
 actions.append(button('Présenter une invitation',()=>void run({action:'guard',key:'invite'},enter),a.invitations<1||a.access.valid),button(a.access.valid?'Entrer dans la salle':a.vip?'Entrer en VIP':`Payer l’entrée · ${a.fee} Gold`,()=>{if(a.access.valid)host.route('casino');else void run({action:'guard',key:'pay'},enter);},!a.access.valid&&!a.vip&&s.balance.wallet<a.fee));
 actions.append(node('p','alley-caption',a.access.valid?'Accès autorisé jusqu’à minuit':`${a.invitations} invitation(s) · ${a.vip?'Entrée VIP offerte':`Portefeuille : ${s.balance.wallet} Gold`}`));
 }
 const footer=node('div','alley-back');footer.append(button('Retour à la ruelle',back,false,true));panel.append(footer);if(message&&!dialog)panel.append(notice());
 if(dialog){actions.inert=true;footer.inert=true;const veil=node('div','alley-veil'),sheet=node('section','alley-sheet');sheet.setAttribute('role','dialog');sheet.setAttribute('aria-modal','true');sheet.setAttribute('aria-label',kind==='robber'?'Plan du braquage':'Choisir une cible');veil.append(sheet);panel.append(veil);sheet.append(node('h3','',kind==='robber'?'Plan du braquage':'Choisir une cible'));
 if(kind==='thief'){for(const t of a.npc_targets)sheet.append(button(t.name,()=>void run({action:'npc_theft',key:t.key}),remaining(a.ban_remaining)>0));if(!a.npc_targets.length)sheet.append(node('p','','Aucune cible disponible.'));}
 else if(a.heist){const h=a.heist;sheet.append(node('p','',`${h.attempts_left} essais restants · ${h.code_length} chiffres distincts`));const input=document.createElement('input');input.type='text';input.inputMode='numeric';input.maxLength=h.code_length;input.autocomplete='off';input.setAttribute('aria-label','Combinaison du coffre');input.placeholder='•'.repeat(h.code_length);input.value=guess;input.disabled=busy;sheet.append(input);const valid=()=>new RegExp(`^\\d{${h.code_length}}$`).test(guess)&&new Set(guess).size===h.code_length;const submit=button('Tenter la combinaison',()=>void run({action:'heist_guess',guess},()=>{guess='';}),!valid());input.oninput=()=>{guess=input.value;submit.disabled=busy||!valid();};input.onkeydown=e=>{if(e.key==='Enter'&&!submit.disabled){e.preventDefault();submit.click();}};sheet.append(submit);}
 else{const allowed=['Criminel','Seigneur de la Ruelle'].includes(a.reputation.label);sheet.append(node('p','',allowed?'Trouvez la combinaison du coffre.':'Le rang Criminel est nécessaire pour préparer un braquage.'));sheet.append(button('Commencer le braquage',()=>void run({action:'heist_start'}),!allowed||remaining(a.ban_remaining)>0));}
 if(message)sheet.append(notice());sheet.append(button('Fermer',closeDialog,false,true));}
 trapMenu(panel,()=>busy,()=>dialog?closeDialog():back(),()=>panel.querySelector<HTMLElement>('.alley-sheet')??panel);
 if(focused)Array.from(panel.querySelectorAll<HTMLElement>('[aria-label]')).find(n=>n.getAttribute('aria-label')===focused)?.focus({preventScroll:true});
 }
 draw();const timer=setInterval(()=>{if(!busy&&!dialog&&(host.state().alley.ban_remaining>0||host.state().alley.larceny_remaining>0))draw();},1000);
 return{destroy(){dead=true;clearInterval(timer);panel.onkeydown=null;document.body.classList.remove('illustrated-open');},update(){if(!busy)draw();}};
}
