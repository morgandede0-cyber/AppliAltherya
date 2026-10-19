import {WHEEL,RED} from './game-model';
export {WHEEL,RED};
export type RouletteBet={type:string;amount:number;numbers?:number[]};
export const outsideBets=[['low','1–18'],['even','Pair'],['red','Rouge'],['black','Noir'],['odd','Impair'],['high','19–36'],['dozen1','1re douzaine'],['dozen2','2e douzaine'],['dozen3','3e douzaine'],['column1','1re colonne'],['column2','2e colonne'],['column3','3e colonne']];
export function covered(type:string,numbers:number[]=[]):number[]{const all=Array.from({length:36},(_,i)=>i+1);if(type==='red')return all.filter(n=>RED.has(n));if(type==='black')return all.filter(n=>!RED.has(n));if(type==='even'||type==='odd')return all.filter(n=>n%2===(type==='even'?0:1));if(type==='low'||type==='high')return all.filter(n=>type==='low'?n<=18:n>=19);if(/^dozen[123]$/.test(type)){const i=Number(type.at(-1));return all.filter(n=>n>(i-1)*12&&n<=i*12);}if(/^column[123]$/.test(type))return all.filter(n=>(n-1)%3===Number(type.at(-1))-1);
 if(numbers.some(n=>!Number.isInteger(n)||n<0||n>36)||new Set(numbers).size!==numbers.length)return[];const ns=[...numbers].sort((a,b)=>a-b),a=ns[0],b=ns[1];if(type==='number'&&ns.length===1)return ns;if(type==='split'&&ns.length===2&&((a===0&&b>=1&&b<=3)||(a>0&&(b-a===3||b-a===1&&Math.floor((a-1)/3)===Math.floor((b-1)/3)))))return ns;if(type==='street'&&(ns.join() ==='0,1,2'||ns.join()==='0,2,3'||ns.length===3&&a>0&&a%3===1&&ns.every((n,i)=>n===a+i)))return ns;if(type==='corner'&&(ns.join()==='0,1,2,3'||ns.length===4&&a>0&&a%3!==0&&ns.join()===[a,a+1,a+3,a+4].join()))return ns;if(type==='six_line'&&ns.length===6&&a>0&&a%3===1&&ns.every((n,i)=>n===a+i))return ns;return[];}
export function betKey(b:RouletteBet){return b.type+':'+(b.numbers??[]).join(',');}
export function targetRotation(n:number,previous=0){const i=WHEEL.indexOf(n);if(i<0)throw Error('Numéro invalide');return Math.ceil(previous/360)*360+2160-i*360/37;}
/** End angle of the selected pocket, where zero degrees points upwards. */
export function pocketAngle(n:number,rotation:number){return((WHEEL.indexOf(n)*360/37+rotation)%360+360)%360;}
export function ballPosition(rotation:number,radius:number){const a=(rotation-90)*Math.PI/180;return{x:500+radius*Math.cos(a),y:500+radius*Math.sin(a)};}
export function spinFrame(n:number,begin:number,end:number,t:number){const angle=begin+(end-begin)*(1-Math.pow(1-t,3));let ballAngle:number,r:number;if(t<.78){const u=t/.78;ballAngle=-2520*(1-Math.pow(1-u,1.55));r=420-30*Math.pow(u,6);}else{const u=(t-.78)/.22,lockStart=begin+(end-begin)*(1-Math.pow(.22,3))+WHEEL.indexOf(n)*360/37,offset=-360*Math.round((lockStart+2520)/360),delta=-2520-(lockStart+offset);ballAngle=angle+WHEEL.indexOf(n)*360/37+offset+delta*Math.pow(1-u,3);r=390-50*(1-Math.pow(1-u,2))+Math.sin(u*5*Math.PI)*9*(1-u);}return{angle,ballAngle,r};}

/** Position of a combined wager on the classic horizontal mat or a 12-number mobile page. */
export function betAnchor(type:string,numbers:number[],compact=false,page=0){
 const visible=numbers.filter(n=>n===0||!compact||Math.floor((n-1)/12)===page);
 if(!visible.length)return {x:0,y:0,visible:false};
 const point=(n:number)=>compact?(n===0?{x:50,y:10}:{x:((n-1)%3+.5)/3*100,y:(Math.floor(((n-1)%12)/3)+1.5)/5*100}):(n===0?{x:50/13,y:50}:{x:(Math.floor((n-1)/3)+1.5)/13*100,y:(2.5-(n-1)%3)/3*100});
 let x=0,y=0;for(const n of visible){const p=point(n);x+=p.x;y+=p.y;}x/=visible.length;y/=visible.length;
 if(compact){if(visible.length<numbers.length)y=numbers.some(n=>n>(page+1)*12)?100:20;if(numbers.includes(0)){y=20;x=type==='split'?point(numbers.find(n=>n!==0)!).x:50;}else if(type==='street'||type==='six_line')x=100;}
 else{if(numbers.includes(0)){x=100/13;y=type==='split'?point(numbers.find(n=>n!==0)!).y:50;}else if(type==='street'||type==='six_line')y=100;}
 return{x,y,visible:true};
}

/** Perspective mat geometry shared by cells and combined wager markers. */
export function sceneCell(n:number){
 const row=n===0?-1:Math.floor((n-1)/3),col=n===0?0:(n-1)%3;
 const top=n===0?0:8+row*92/12,bottom=n===0?8:8+(row+1)*92/12;
 const edge=(y:number)=>22*(1-(y-8)/92);
 const lt=n===0?22:edge(top),lb=n===0?22:edge(bottom);
 const a=n===0?22:lt+(100-2*lt)*col/3,b=n===0?78:lt+(100-2*lt)*(col+1)/3;
 const c=n===0?22:lb+(100-2*lb)*col/3,d=n===0?78:lb+(100-2*lb)*(col+1)/3;
 const left=Math.min(a,c),right=Math.max(b,d),width=right-left;
 return {x:(a+b+c+d)/4,y:(top+bottom)/2,right:(b+d)/2,style:{left:left+'%',top:top+'%',width:width+'%',height:(bottom-top)+'%'},points:`${(a-left)/width*100},0 ${(b-left)/width*100},0 ${(d-left)/width*100},100 ${(c-left)/width*100},100`};
}
export function sceneAnchor(type:string,ns:number[]){const cells=ns.map(sceneCell);let x=cells.reduce((s,c)=>s+c.x,0)/cells.length,y=cells.reduce((s,c)=>s+c.y,0)/cells.length;if(ns.includes(0)&&ns.length>1){x=ns.length===2?sceneCell(ns[1]).x:50;y=8;}if(type==='street'||type==='six_line')x=100-22*(1-(y-8)/92);return{x,y,visible:true};}
