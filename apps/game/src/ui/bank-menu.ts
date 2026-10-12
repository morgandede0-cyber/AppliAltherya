import type {Snapshot} from '../activity';
import {bankMarkup} from './bank-markup';
import {sizeMenu,watchMenuSize} from './menu-layout';
import {trapMenu} from './menu-kit';
import {validAmount,withdrawalQuote} from './service-model';
import './bank-menu.css';

type BankMode='deposit'|'withdraw';
type Host={state:()=>Snapshot;mutate:(body:Record<string,unknown>)=>Promise<string>;close:()=>void;route:(key:string)=>void};
/** Bank components keep their original artwork; balances and actions belong to the server. */
export function openBankMenu(panel:HTMLElement,host:Host){
 let busy=false,dead=false;
 panel.hidden=false;panel.className='bank-menu';panel.dataset.kind='bank';panel.setAttribute('aria-label','Banque de IV');panel.innerHTML=bankMarkup;
 const root=panel.querySelector<HTMLElement>('#bank-polished')!,status=root.querySelector<HTMLElement>('.status')!;
 const forms=Array.from(root.querySelectorAll<HTMLFormElement>('form'));
 const returnButton=root.querySelector<HTMLButtonElement>('.back')!;
 const feeNote=root.querySelector<HTMLElement>('[data-withdraw-quote]')!;
 const format=(n:number)=>n.toLocaleString('fr-FR')+' Gold';
 for(const form of forms){const mode=form.dataset.mode as BankMode,input=form.querySelector<HTMLInputElement>('input')!;input.value=String(Math.min(100,mode==='deposit'?host.state().balance.wallet:host.state().balance.bank));}
 function update(){
  if(dead)return;
  const balance=host.state().balance;
  root.querySelector<HTMLOutputElement>('[data-wallet]')!.value=format(balance.wallet);
  root.querySelector<HTMLOutputElement>('[data-bank]')!.value=format(balance.bank);
  root.querySelector<HTMLOutputElement>('[data-fortune]')!.value=format(balance.wallet+balance.bank);
  panel.setAttribute('aria-busy',String(busy));returnButton.disabled=busy;
  for(const form of forms){
   const mode=form.dataset.mode as BankMode,input=form.querySelector<HTMLInputElement>('input')!,amount=Number(input.value),max=mode==='deposit'?balance.wallet:balance.bank;
   input.max=String(Math.min(max,1e9));input.disabled=busy;
   for(const button of Array.from(form.querySelectorAll<HTMLButtonElement>('button')))button.disabled=busy;
   form.querySelector<HTMLButtonElement>('[type=submit]')!.disabled=busy||!validAmount(amount,max);
   if(mode==='withdraw'){
    const quote=withdrawalQuote(amount,balance.free_withdrawal_available);
    feeNote.textContent=max===0?'Banque vide':!validAmount(amount,max)?'Indiquez un montant valide':balance.free_withdrawal_available?'Premier retrait gratuit':`Frais : ${format(quote.fee)} · Reçu : ${format(quote.received)}`;
   }
  }
  sizeMenu(panel,0,1020);
 }
 for(const form of forms){
  const mode=form.dataset.mode as BankMode,input=form.querySelector<HTMLInputElement>('input')!;
  input.addEventListener('input',()=>{status.textContent='';update();});
  for(const button of Array.from(form.querySelectorAll<HTMLButtonElement>('[data-step],[data-preset]')))button.addEventListener('click',()=>{
   if(busy||dead)return;const balance=host.state().balance,max=mode==='deposit'?balance.wallet:balance.bank;
   const preset=button.dataset.preset;
   input.value=String(preset?(preset==='all'?Math.min(max,1e9):Number(preset)):Math.max(1,Math.min(max,1e9,(Number(input.value)||0)+Number(button.dataset.step))));
   status.textContent='';update();
  });
  form.addEventListener('submit',async event=>{
   event.preventDefault();if(busy||dead)return;
   const balance=host.state().balance,amount=Number(input.value),max=mode==='deposit'?balance.wallet:balance.bank;
   if(!validAmount(amount,max)){status.textContent='Indiquez un montant entier disponible.';update();return;}
   busy=true;status.textContent='Opération en cours…';update();
   try{const message=await host.mutate({action:mode,amount});if(!dead)status.textContent=message;}
   catch(error){if(!dead)status.textContent=error instanceof Error?error.message:String(error);}
   finally{busy=false;if(!dead)update();}
  });
 }
 returnButton.addEventListener('click',()=>{if(!busy&&!dead)host.route('hub');});
 document.body.classList.add('illustrated-open');
 trapMenu(panel,()=>busy,host.close);
 const stop=watchMenuSize(panel,update);update();
 for(const img of Array.from(root.querySelectorAll<HTMLImageElement>('img')))img.addEventListener('load',()=>{if(!dead)sizeMenu(panel,0,1020);},{once:true});
 forms[0].querySelector<HTMLInputElement>('input')?.focus({preventScroll:true});
 return{update,destroy(){dead=true;stop();panel.onkeydown=null;document.body.classList.remove('illustrated-open');}};
}
