import {walkable} from './map';
export type Point={x:number;y:number};
export const GRID=16;
const key=(p:Point)=>`${p.x},${p.y}`;
export function findPath(start:Point,end:Point):Point[]{
 const cell=(p:Point)=>({x:Math.round(p.x/GRID),y:Math.round(p.y/GRID)}),a=cell(start),goal=cell(end);
 const valid=(p:Point)=>walkable(p.x*GRID,p.y*GRID);
 if(!valid(goal))return [];
 const open=[a],came=new Map<string,Point>(),cost=new Map([[key(a),0]]),closed=new Set<string>();let count=0;
 const h=(p:Point)=>Math.abs(p.x-goal.x)+Math.abs(p.y-goal.y);
 while(open.length&&count++<7000){open.sort((x,y)=>(cost.get(key(x))!+h(x))-(cost.get(key(y))!+h(y)));const p=open.shift()!,k=key(p);if(closed.has(k))continue;closed.add(k);
 if(k===key(goal)){const result:Point[]=[];let n=p;while(key(n)!==key(a)){result.push({x:n.x*GRID,y:n.y*GRID});n=came.get(key(n))!;}return result.reverse();}
 for(const [dx,dy] of [[1,0],[-1,0],[0,1],[0,-1]]){const n={x:p.x+dx,y:p.y+dy},nk=key(n);if(closed.has(nk)||!valid(n))continue;const c=cost.get(k)!+1;if(c<(cost.get(nk)??Infinity)){cost.set(nk,c);came.set(nk,p);open.push(n);}}
 }return [];
}
export const places=[
 {id:'market',name:'Mira · Marché',x:288,y:416,row:1},
 {id:'forge',name:'Borin · Forge',x:576,y:352,row:2},
 {id:'tavern',name:'Taverne',x:320,y:688,row:1},
 {id:'castle',name:'Château',x:416,y:336,row:3},
 {id:'bank',name:'Banque',x:528,y:624,row:3},
 {id:'arena',name:'Maître de l’arène',x:736,y:560,row:3},
 {id:'alley',name:'Ruelle sombre',x:384,y:848,row:0},
 {id:'jobs',name:'Petites annonces',x:640,y:720,row:-1},
 {id:'world',name:'Monde d’Elyndor',x:944,y:576,row:-1},
 {id:'expeditions',name:'Départ en expédition',x:1136,y:816,row:3}
] as const;
