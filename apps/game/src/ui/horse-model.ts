export const FINISH_ANGLE=.24;
export function lanePoint(lane:number,progress:number){const rx=[603,645,690,737][lane],ry=[105,125,145,165][lane],cy=[375,389,403,417][lane],a=FINISH_ANGLE-lane*.03-progress*2*Math.PI,c=Math.cos(.07),s=Math.sin(.07);return{x:835+rx*Math.cos(a)*c-ry*Math.sin(a)*s,y:cy+rx*Math.cos(a)*s+ry*Math.sin(a)*c,dx:rx*Math.sin(a)*c+ry*Math.cos(a)*s,dy:rx*Math.sin(a)*s-ry*Math.cos(a)*c,scale:.76+.24*(Math.sin(a)+1)/2};}
export function runnerProgress(seconds:number,finish:number,runner:number){const effective=(t:number)=>t-.32*(1-Math.exp(-t/.32)),p=Math.min(1,Math.max(0,effective(seconds)/effective(finish)));if(seconds>=finish)return 1+.045*(1-Math.exp(-(seconds-finish)*1.2));return p+.022*Math.sin(p*Math.PI)*Math.sin(p*Math.PI*2.8+runner*1.7);}
export function viewDirection(dx:number,dy:number){const left=dx<0,r=Math.abs(dy)/(Math.abs(dx)+1);if(r<.18)return{row:0,flip:left};if(dy<0&&r>1.2)return{row:2,flip:false};return{row:dy<0?1:3,flip:left};}
export function gaitFrame(distance:number){return Math.floor(Math.max(0,distance)/12.5)%8;}
export function raceOrder(winner:number){return[winner,...[0,1,2,3].filter(i=>i!==winner)];}
