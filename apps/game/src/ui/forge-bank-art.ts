import {decoratePredator,predatorFrame} from './predator-art';
import './forge-bank.css';
/** Keep service controls and server state; replace only their presentation. */
export function decorateWorkshop(panel:HTMLElement,kind:'forge'|'bank'){
 decoratePredator(panel);
 panel.classList.remove('predator-commerce');panel.classList.add('predator-'+kind);
 const fields=kind==='bank'?'.bank-account,.bank-transfer':'.realm-materials';
 for(const field of Array.from(panel.querySelectorAll<HTMLElement>(fields))){
  field.querySelector(':scope>.approved-card-fill')?.remove();
  field.classList.add('workshop-field');field.prepend(predatorFrame(false,'card'));
 }
}
