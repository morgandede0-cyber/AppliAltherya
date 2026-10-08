export const WHEEL=[0,32,15,19,4,21,2,25,17,34,6,27,13,36,11,30,8,23,10,5,24,16,33,1,20,14,31,9,22,18,29,7,28,12,35,3,26];
export const RED=new Set([1,3,5,7,9,12,14,16,18,19,21,23,25,27,30,32,34,36]);
export function wheelRotation(number:number,previous=0){const index=WHEEL.indexOf(number);if(index<0)throw new Error('Numéro invalide');const target=(360-index*360/37)%360;return Math.ceil(previous/360)*360+5*360+target;}
export function timeLabel(seconds:number){const t=Math.max(0,Math.ceil(seconds));return `${Math.floor(t/3600)} h ${Math.floor(t%3600/60)} min ${t%60} s`;}
export function raceProgress(elapsed:number,winner:number){const t=Math.max(0,Math.min(1,elapsed));return Array.from({length:4},(_,i)=>Math.min(1,(t+.07*Math.sin(Math.PI*t)*Math.sin(2*Math.PI*t+i*1.9))*(i===winner?1:0.84+i*0.02)));}

export function slotKey(key:string){return ({'🍒':'cherry','🔔':'bell','💎':'diamond','👑':'crown','7️⃣':'seven'} as Record<string,string>)[key]??key;}
/** Tavern server persists French gesture names; normalize before choosing an asset. */
export function gestureKey(key:string){return ({pierre:'rock',feuille:'paper',ciseaux:'scissors'} as Record<string,string>)[key]??key;}
export function outcomeTone(payout:number,wager:number){return payout>wager?'win':payout===wager?'tie':'loss';}
export function coinRotation(face:string){return 6*360+(face==='face'?180:0);}
