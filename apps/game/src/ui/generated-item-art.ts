import manifest from './item-manifest.json';
import {assetSlice} from './assets';
export const normalizeItemName=(name:string)=>name.normalize('NFKD').replace(/\p{M}/gu,'').replace(/[^\p{L}\p{N}]+/gu,' ').trim().toLocaleLowerCase('fr-FR');
const exact=new Map(manifest.items.map(entry=>[entry.name,entry]));
const entries=new Map<string,(typeof manifest.items)[number]>();for(const entry of manifest.items){const key=normalizeItemName(entry.name);if(!entries.has(key))entries.set(key,entry);}
export function generatedItemInfo(name:string){return exact.get(name)??entries.get(normalizeItemName(name));}
export function generatedItemArt(name:string){const entry=generatedItemInfo(name);if(!entry)return undefined;const sheet=manifest.sheets[entry.sheet as keyof typeof manifest.sheets];const w=sheet.width/manifest.columns,h=sheet.height/manifest.rows;const art=assetSlice('/assets/items/'+sheet.file,entry.column*w,entry.row*h,w,h,sheet.width,sheet.height);art.classList.add('item-asset');art.dataset.item=entry.name;return art;}
export function storyItemChapter(name:string){return generatedItemInfo(name)?.chapter;}
const questObjects:Record<string,string>={
'S1-Q01':'Reçu marchand','S1-Q02':'Faux contrat','S1-Q03':'Caisses de voyage','S1-Q04':'Reçu marchand','S1-Q05':'Plaque de transport','S1-Q06':'Rivets anciens','S1-Q07':'Plan de protection','S1-Q08':'Reçu marchand',
'S2-Q01':'Assemblage ancien','S2-Q02':'Journal de Seraph','S2-Q03':'Étais de mission','S2-Q04':'Rapport de secours','S2-Q05':'Étais de mission','S2-Q06':'Journal de Seraph','S2-Q07':'Plan de protection','S2-Q08':'Rapport de secours',
'S3-Q01':'Relevé d’Ashkar','S3-Q02':'Relevé d’Ashkar','S3-Q03':'Balise d’Elarwyn','S3-Q04':'Plan de protection','S3-Q05':'Faux contrat','S3-Q06':'Rapport de secours','S3-Q07':'Faux contrat','S3-Q08':'Plan de protection',
'S4-Q01':'Mandat de secours','S4-Q02':'Dossier de mandat','S4-Q03':'Plan de protection','S4-Q04':'Balise d’Elarwyn','S4-Q05':'Pièces volées','S4-Q06':'Pièces volées','S4-Q07':'Mandat de secours','S4-Q08':'Gazette'};
/** Illustrations only: narrative props are not added to inventory or rewards. */
export function questObjectArt(id:string){const name=questObjects[id];return name?generatedItemArt(name):undefined;}
