export type ChamberEvent={chamber:number;actor:'player'|'opponent';spent:boolean};
export function remaining(step:number){return Math.max(0,6-Math.max(0,Math.min(6,Math.floor(step))));}
export function chamberState(index:number,step:number,events:ChamberEvent[]){if(index>=step)return'unknown';return events.find(e=>e.chamber===index+1)?.spent?'spent':'empty';}
export function pendingEvents(events:ChamberEvent[],previous:number){return events.filter(e=>e.chamber>previous).sort((a,b)=>a.chamber-b.chamber);}
