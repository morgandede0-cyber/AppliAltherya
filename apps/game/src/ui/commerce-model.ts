import type {Snapshot} from '../activity';
export type CommerceMode='buy'|'sell'|'story';
export type Product={key:string;name:string;price:number;stock:number;owned:boolean;category:string;icon:string;description:string;chapter?:number};
export const categories=(mode:CommerceMode)=>mode==='story'?['Histoire']:mode==='sell'?['Bûcheron','Mineur','Chasseur']:['Outils','Consommables','Divers'];
export function resourceCategory(name:string){
 if(/Pierre|Minerai|Diamant|Cristal/.test(name))return 'Mineur';
 if(/Viande|Peau|Croc|Griffe|Défense|Trophée/.test(name))return 'Chasseur';
 return 'Bûcheron';
}
export function resourceIcon(name:string){
 if(/Bois|Brindille/.test(name))return 'wood';if(/Champignon/.test(name))return 'mushroom';
 if(/Baies|fleur|Herbes/.test(name))return 'herb';if(/Peau/.test(name))return 'hide';
 if(/Viande/.test(name))return 'meat';if(/Diamant|Cristal/.test(name))return 'gem';
 if(/Croc|Griffe|Défense/.test(name))return 'fang';if(/Trophée/.test(name))return 'trophy';return 'ore';
}
export function products(state:Snapshot,mode:CommerceMode):Product[]{
 if(mode==='sell')return Object.entries(state.resources).filter(([name,n])=>n>0&&state.prices[name]>0).map(([name,n])=>({key:name,name,price:state.prices[name],stock:n,owned:false,category:resourceCategory(name),icon:resourceIcon(name),description:'Ressource de voyage. Conservez les matériaux nécessaires à vos prochaines améliorations.'}));
 const story=state.story_items.map(i=>({key:i.name,name:i.name,price:i.price,stock:1,owned:i.owned,category:'Histoire',chapter:i.chapter,icon:'scroll',description:'Objet d’histoire. Réunissez la collection pour débloquer le prochain récit du troubadour.'}));
 if(mode==='story')return story;
 return Object.entries(state.catalog).map(([key,i])=>({key,name:i.name,price:i.price,stock:1,owned:state.owned[key],category:key==='bag'?'Divers':'Outils',icon:key,description:({pickaxe:'Permet de miner au Mont Vorak. Un sac est nécessaire pour rapporter les ressources.',axe:'Permet de couper du bois à Elarwyn. Un sac est nécessaire pour rapporter les ressources.',spear:'Permet de chasser à Elarwyn et au Mont Vorak. Un sac est nécessaire pour le butin.',bag:`Contient ${'capacity' in state.bags['1']?state.bags['1'].capacity:8} ressources au premier palier. Améliorable à la forge.`} as Record<string,string>)[key]??'Équipement de voyage.'}));
}
export function clampQuantity(value:number,stock:number){return Math.min(Math.max(1,Math.trunc(Number.isFinite(value)?value:1)),Math.max(1,stock));}
export function pageItems(items:Product[],page:number,size=4){const last=Math.max(0,Math.ceil(items.length/size)-1);return {page:Math.min(Math.max(0,page),last),last,items:items.slice(Math.min(Math.max(0,page),last)*size,(Math.min(Math.max(0,page),last)+1)*size)};}
export function tradeBlock(product:Product|undefined,mode:CommerceMode,wallet:number,quantity:number){if(!product)return 'Choisissez un objet';if(mode!=='sell'&&product.owned)return 'SOLD OUT';if(mode==='sell'&&product.stock<quantity)return 'Stock insuffisant';if(mode!=='sell'&&wallet<product.price)return 'Gold insuffisant';return '';}
export function tradeBody(product:Product,mode:CommerceMode,quantity:number){return mode==='sell'?{action:'sell',key:product.key,amount:clampQuantity(quantity,product.stock)}:{action:product.icon==='scroll'?'story_buy':'buy',key:product.key};}
