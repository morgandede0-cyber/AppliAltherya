export const items = {
 potion:{name:'Potion de soin',icon:'✦',description:'Restaure 35 PV.',price:12,sell:5},
 fang:{name:'Croc de loup',icon:'❧',description:'Un trophée de la forêt.',price:0,sell:8},
 ore:{name:'Minerai de fer',icon:'◆',description:'Pour la forge de Borin.',price:0,sell:4},
 parcel:{name:'Colis perdu',icon:'▣',description:'Le sceau de Mira est intact.',price:0,sell:0},
 sword:{name:'Lame de la garde',icon:'⚔',description:'+5 attaque une fois équipée.',price:45,sell:20}
} as const;
export type Item = keyof typeof items;
export const quests = [
 {id:'wolves',name:'Les loups de la forêt',description:'Éliminer 3 loups puis retrouver le garde.',target:3,gold:35,xp:60,npc:'Garde'},
 {id:'parcel',name:'Le colis perdu',description:'Retrouver le colis au pied du vieux chêne et revenir chez Mira.',target:1,gold:20,xp:30,npc:'Mira'},
 {id:'ore',name:'Le forgeron inquiet',description:'Ramasser 3 minerais et les rapporter à Borin.',target:3,gold:25,xp:40,npc:'Borin'}
] as const;
export function xpNeeded(level:number){return [0,100,175,275,400,575,800][level] ?? Math.round((250+75*(level-1)**1.55)/25)*25;}
export type State={version:1;name:string;appearance:number;x:number;y:number;hp:number;level:number;xp:number;gold:number;inventory:Record<Item,number>;equipped:boolean;quests:Record<string,{active:boolean;progress:number;claimed:boolean}>;collected:string[]};
export const maxHp=(s:State)=>60+(s.level-1)*8;
export const attack=(s:State)=>11+(s.level-1)*2+(s.equipped?5:0);
export function fresh(name='Aventurier',appearance=0):State{return {version:1,name,appearance,x:530,y:600,hp:60,level:1,xp:0,gold:30,inventory:{potion:3,fang:0,ore:0,parcel:0,sword:0},equipped:false,quests:Object.fromEntries(quests.map(q=>[q.id,{active:false,progress:0,claimed:false}])),collected:[]};}
export function grantXP(s:State,n:number){s.xp+=n;let levels=0;while(s.xp>=xpNeeded(s.level)){s.xp-=xpNeeded(s.level);s.level++;levels++;s.hp=maxHp(s);}return levels;}
export function progress(s:State,id:string,n=1){const q=s.quests[id];if(q?.active&&!q.claimed)q.progress+=n;}
export function claim(s:State,id:string){const def=quests.find(q=>q.id===id),q=s.quests[id];if(!def||!q||q.claimed||!q.active||q.progress<def.target)return false;if(id==='ore'&&s.inventory.ore<3||id==='parcel'&&s.inventory.parcel<1)return false;if(id==='ore')s.inventory.ore-=3;if(id==='parcel')s.inventory.parcel--;q.claimed=true;s.gold+=def.gold;grantXP(s,def.xp);return true;}
export function buy(s:State,id:Item){const p=items[id].price;if(p<=0||s.gold<p)return false;s.gold-=p;s.inventory[id]++;return true;}
export function sell(s:State,id:Item){const p=items[id].sell;if(p<=0||s.inventory[id]<=0)return false;s.inventory[id]--;s.gold+=p;if(id==='sword'&&!s.inventory.sword)s.equipped=false;return true;}
