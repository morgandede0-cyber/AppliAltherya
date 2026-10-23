import type {Snapshot} from '../activity';
import {node} from './menu-framework';
import {resourceArt} from './catalog-art';
import './service-improvements.css';
export function expeditionResources(s:Snapshot,destination:string,tool:string,tier:number){const table=(s.expedition_loot?.[destination]?.[tool]??[]).filter(e=>e.min_tier<=tier);const total=table.reduce((n,e)=>n+e.weight,0);return table.map(e=>({...e,chance:total?100*e.weight/total:0}));}
export function expeditionGuide(panel:HTMLElement,s:Snapshot,kind:string,tool:string,tier:number,destination:string){
 const parent=panel.querySelector<HTMLElement>('.gm-body');if(!parent)return;
 if(kind==='live'&&s.active){const row=node('section','preparation-guide');const discovered=Object.values(s.active.revealed_loot).reduce((n,v)=>n+v,0);row.append(node('h3','','Votre sac se remplit'),node('p','',`${discovered} / ${s.active.capacity} ressources découvertes · Les prochains résultats restent inconnus jusqu’à leur découverte.`));parent.append(row);return;}
 if(!['tools','destinations','departure'].includes(kind)||!s.expedition_loot)return;
 const keys=kind==='tools'?Object.keys(s.destinations).filter(k=>s.destinations[k].tools.includes(tool)&&s.destinations[k].location_key===panel.dataset.expeditionLocation):[destination];
 const group=node('details','preparation-guide');(group as HTMLDetailsElement).open=kind==='departure';group.append(node('summary','','Ressources, sac et préparation'));
 const capacity=tool==='hands'?6:s.bags[String(s.gear.bag_level)]?.capacity??0;group.append(node('p','',`Sac : ${capacity} emplacements · Un tirage remplit un emplacement. Les probabilités concernent chaque tirage, pas un butin garanti.`));
 for(const key of keys){const zone=s.destinations[key];if(!zone)continue;const section=node('section','preparation-destination');section.append(node('h3','',zone.name),node('p','',`Niveau ${zone.level} · ${zone.duration_label} · ${s.level>=zone.level?'Niveau atteint':'Niveau non atteint'}`));const list=node('div','preparation-resources');for(const r of expeditionResources(s,key,tool,tool==='hands'?0:tier)){const row=node('div','preparation-resource');const art=resourceArt(r.name);if(art)row.append(art);row.append(node('span','',r.name),node('strong','',r.chance.toLocaleString('fr-FR',{maximumFractionDigits:1})+' %'));list.append(row);}section.append(list);group.append(section);}
 if(!keys.length)group.append(node('p','','Aucune destination pour ce métier dans cette région.'));parent.append(group);
}
export function forgeComparison(s:Snapshot,key:string){const current=s.gear[key+'_level']||1,next=Math.min(5,current+1);if(key==='bag'){const before=s.bags[String(current)]?.capacity??0,after=s.bags[String(next)]?.capacity??before;return `Capacité : ${before} → ${after} emplacements${after>before?' (+'+(after-before)+')':''}`;}const names=new Set<string>();for(const tools of Object.values(s.expedition_loot??{}))for(const entry of tools[key]??[])if(entry.min_tier===next)names.add(entry.name);return `Accès aux ressources : palier ${current} → ${next}.`+(next>current&&names.size?' Nouvelles ressources selon la destination : '+[...names].join(', ')+'.':'');}
