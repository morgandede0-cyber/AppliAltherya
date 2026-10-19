export const GESTURES=['rock','paper','scissors'] as const;
export type Gesture=typeof GESTURES[number];
export const GESTURE_LABELS:Record<Gesture,string>={rock:'Pierre',paper:'Feuille',scissors:'Ciseaux'};
export const RPS_DURATION=3.05;
export function parseGesture(value:unknown):Gesture|undefined{return({rock:'rock',paper:'paper',scissors:'scissors',pierre:'rock',feuille:'paper',ciseaux:'scissors'} as Record<string,Gesture>)[String(value)];}
export function gestureFrame(g:Gesture){return GESTURES.indexOf(g);}
/** Three synchronized preparatory beats; neither result is shown before the reveal. */
export function rpsMotion(seconds:number){const t=Math.max(0,Math.min(RPS_DURATION,seconds)),pre=t<2.1,beat=pre?Math.min(2,Math.floor((t+1e-8)/.7)):3,u=pre?(t-beat*.7)/.7:0,wave=pre?Math.sin(Math.PI*u)**2:0,reveal=Math.max(0,Math.min(1,(t-2.1)/.24)),settle=t>2.34&&t<RPS_DURATION?Math.sin((t-2.34)*16)*Math.exp(-(t-2.34)*8):0;return{beat,lift:wave*30,playerAngle:-8*wave-4*Math.sin(reveal*Math.PI)+settle,foxAngle:7*wave+3*Math.sin(reveal*Math.PI)-settle,reveal,contacts:pre?beat:3,stopped:t>=RPS_DURATION};}
export function rpsOutcome(a:Gesture,b:Gesture){return a===b?'tie':({rock:'scissors',paper:'rock',scissors:'paper'} as Record<Gesture,Gesture>)[a]===b?'win':'loss';}
