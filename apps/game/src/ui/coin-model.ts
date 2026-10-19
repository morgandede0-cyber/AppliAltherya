export type CoinSide='pile'|'face';
export const COIN_DURATION=3.8;
/** Server chooses the face. This trajectory only presents that settled result. */
export function coinMotion(seconds:number,side:CoinSide){
 const t=Math.max(0,Math.min(COIN_DURATION,seconds)),target=side==='face'?180:0;
 const end=2160+target;
 let height=0,angle=end,wobble=0,contacts=0;
 if(t<2.6){const u=t/2.6;height=195*4*u*(1-u);angle=end*(1-Math.pow(1-u,1.15));}
 else{const u=t-2.6;contacts=1;if(u<.52){height=38*Math.sin(u/.52*Math.PI);wobble=32*Math.sin(u/.52*Math.PI)*Math.cos(u*14);}
 else if(u<.88){contacts=2;height=12*Math.sin((u-.52)/.36*Math.PI);wobble=15*Math.sin((u-.52)/.36*Math.PI)*Math.cos(u*19);}
 else{contacts=3;wobble=6*Math.sin((u-.88)*40)*Math.max(0,1-(u-.88)/.32);}}
 if(t>=COIN_DURATION)wobble=0;
 return{height,rx:42+angle+wobble,rz:t<2.6?18*Math.sin(t/2.6*Math.PI):wobble*.35,contacts,stopped:t>=COIN_DURATION};
}
export function coinTransform(seconds:number,side:CoinSide){const m=coinMotion(seconds,side);return `rotateX(${m.rx}deg) rotateZ(${m.rz}deg)`;}
export function visibleCoinSide(rx:number):CoinSide{return Math.cos(rx*Math.PI/180)>=0?'pile':'face';}
