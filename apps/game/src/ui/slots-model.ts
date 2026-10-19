export const SLOT_KEYS=['cherry','bell','diamond','crown','seven'];
export const symbolKey=(key:string)=>({'🍒':'cherry','🔔':'bell','💎':'diamond','👑':'crown','7️⃣':'seven'} as Record<string,string>)[key]??key;
export function stopPlan(start:number,seconds:number){const index=Math.ceil(start+5*seconds)+1;return{start,index,end:index-1,seconds};}
export function stopDistance(plan:ReturnType<typeof stopPlan>,u:number){u=Math.max(0,Math.min(1,u));return plan.start+(u*u*u-2*u*u+u)*10*plan.seconds+(-2*u*u*u+3*u*u)*(plan.end-plan.start);}
export function winningReels(reels:string[],payout:number,wager:number){if(payout<wager)return[];if(reels.length===3&&reels.every(x=>x===reels[0]))return[0,1,2];return reels.map((x,i)=>symbolKey(x)==='seven'?i:-1).filter(i=>i>=0);}

/** Stop left to right with enough time to read each symbol before the next. */
export const REEL_WARMUP_MS=900;
export function reelStopSeconds(reel:number){return 3+reel*1.6;}
