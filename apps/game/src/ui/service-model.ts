export function withdrawalQuote(amount:number,free:boolean){const fee=free?0:Math.max(1,Math.floor(amount*5/100));return {fee,received:amount-fee};}
export function validAmount(amount:number,max:number){return Number.isSafeInteger(amount)&&amount>0&&amount<=max&&amount<=1e9;}
export function pageSlice<T>(items:T[],page:number){return items.slice(page*4,page*4+4);}
