import type {Snapshot} from '../activity';
import './game-feedback.css';
/** Completes existing controls and rule books; never displays an unanimated result. */
export function gameFeedback(panel:HTMLElement,kind:string,state:()=>Snapshot){
 const document=panel.ownerDocument;let dead=false,scheduled=false,active=false,paused=false;const uid='game-feedback-'+kind;
 function paint(){scheduled=false;if(dead||active)return;active=true;observer.disconnect();try{if(panel.getAttribute('aria-busy')==='true')return;
  for(const input of Array.from(panel.querySelectorAll<HTMLInputElement>('input[type=number]'))){if(input.disabled||kind==='roulette')continue;const label=input.closest('label');if(!label)continue;let hint=label.querySelector<HTMLElement>('.game-wager-feedback');if(!hint){hint=document.createElement('small');hint.className='game-wager-feedback';hint.id=uid;hint.setAttribute('role','status');label.append(hint);input.setAttribute('aria-describedby',uid);}const s=state(),max=Math.min(s.balance.wallet,['dice','coin','rps'].includes(kind)?500:s.casino.max_bet),n=input.valueAsNumber,invalid=!Number.isInteger(n)||n<1||n>max;
   input.setAttribute('aria-invalid',String(invalid));hint.textContent=max<1?'Portefeuille vide : aucune mise possible.':!Number.isInteger(n)||n<1?'Saisissez une mise entière d’au moins 1 Gold.':n>max?`Mise trop élevée : maximum ${max} Gold.`:`Maximum disponible : ${max} Gold`;hint.classList.toggle('is-invalid',invalid);
  }
  const notes=state().game_fairness?.notes[kind];for(const dialog of Array.from(panel.querySelectorAll<HTMLElement>('[role=dialog]'))){if(dialog===panel||dialog.querySelector('.game-rule-math')||!notes)continue;const info=document.createElement('section');info.className='game-rule-math';info.append(Object.assign(document.createElement('h4'),{textContent:'Comprendre le pari'}));for(const text of [...notes,'Les retours annoncés comprennent la mise initiale. Le gain net correspond au retour moins la mise.'])info.append(Object.assign(document.createElement('p'),{textContent:text}));const close=Array.from(dialog.children).find(n=>n.tagName==='BUTTON')??null;dialog.insertBefore(info,close);}
  const busy=panel.getAttribute('aria-busy')==='true';if(!busy)paused=false;
 }finally{active=false;if(!dead)observer.observe(panel,{subtree:true,childList:true,attributes:true,attributeFilter:['aria-busy','disabled']});}}
 function schedule(){if(!scheduled&&!dead){scheduled=true;queueMicrotask(paint);}}
 const observer=new panel.ownerDocument.defaultView!.MutationObserver(schedule);panel.addEventListener('input',schedule);
 // Retain a clear presentation state when the Activity is backgrounded mid-animation.
 const visibility=()=>{if(document.hidden&&panel.getAttribute('aria-busy')==='true')paused=true;else if(paused){panel.querySelectorAll<HTMLElement>('[role=status]').forEach(n=>{if(!n.textContent?.includes('Erreur'))n.setAttribute('aria-live','polite');});schedule();}};
 document.addEventListener('visibilitychange',visibility);paint();
 return{update:schedule,destroy(){dead=true;observer.disconnect();panel.removeEventListener('input',schedule);document.removeEventListener('visibilitychange',visibility);}};
}
