import type {Snapshot} from '../activity';
import {equipmentArt,resourceArt} from './catalog-art';
import {forgeComparison} from './expedition-guide';
import {recall,remember} from './session-preferences';
import {mountStudio,placeStudio,studioButton} from './studio-menu';
import './forge-studio.css';
type Host={state:()=>Snapshot;mutate:(body:Record<string,unknown>)=>Promise<string>;route:(key:string)=>void;close:()=>void};
const names:Record<string,string>={axe:'Hache',pickaxe:'Pioche',spear:'Lance',bag:'Sac'};
const node=(tag:string,cls:string,text='')=>{const n=document.createElement(tag);n.className=cls;n.textContent=text;return n;};
/** A dedicated forge view. Only the artwork is static; all rules and values come from the snapshot. */
export function openForgeStudio(panel:HTMLElement,host:Host){
 let selected=recall(host.state().save_owner,'forge-tool','axe'),busy=false,dead=false,notice='';const previous=document.activeElement as HTMLElement|null;
 async function upgrade(){if(busy||dead)return;const s=host.state(),next=(s.gear[selected+'_level']||1)+1,recipe=(selected==='bag'?s.bag_recipes:s.recipes)[next]??{},cost=s.forge_gold[selected==='bag'?'bag':'tool'][next]??0;if(!s.owned[selected]||next>5||s.level<(s.forge_levels[next]??0)||s.balance.wallet<cost||Object.entries(recipe).some(([n,q])=>(s.resources[n]??0)<q))return;busy=true;notice='';draw();try{notice=await host.mutate({action:'upgrade',key:selected});}catch(e){notice=e instanceof Error?e.message:String(e);}finally{busy=false;if(!dead)draw();}}
 function draw(){if(dead)return;const focused=panel.contains(document.activeElement)?document.activeElement?.getAttribute('aria-label'):null,s=host.state(),keys=Object.keys(names).filter(k=>s.catalog[k]);if(!keys.includes(selected))selected=keys[0]??'axe';remember(s.save_owner,'forge-tool',selected);
 const stage=mountStudio(panel,'forge','La forge',busy),title=node('h2','studio-title','La forge');placeStudio(stage,title,16,7.6,68,4.5);
 const tabs=node('nav','sf-tabs');tabs.setAttribute('aria-label','Outils de la forge');placeStudio(stage,tabs,14.8,32.8,73,4.9);for(const key of keys){const b=studioButton(names[key],()=>{if(!busy){selected=key;notice='';draw();}},busy);b.setAttribute('aria-pressed',String(selected===key));b.append(equipmentArt(key));tabs.append(b);}
 const current=s.gear[selected+'_level']||1,next=current+1,max=next>5,owned=!!s.owned[selected];const compare=node('section','realm-forge-compare sf-compare');compare.setAttribute('aria-label','Comparaison des outils');placeStudio(stage,compare,16.5,39.6,68,22.2);
 for(const [i,[label,tier,available]] of [['Équipement actuel',current,owned],['Prochaine amélioration',Math.min(next,5),!max]].entries()){
  const t=Number(tier),name=selected==='bag'?s.bags[String(t)]?.name:s.tools[String(t)]?.[selected],card=node('article','realm-card sf-tool');card.style.left=(i?56.6:0)+'%';card.append(node('h3','',String(label)));
  if(available){const art=equipmentArt(selected,t);art.classList.add('sf-tool-art','approved-gear-art');card.append(art);}card.append(node('strong','sf-tool-name',available?name??names[selected]:max&&i?'Palier maximum':'Non possédé'));
  const copy=selected==='bag'&&available?`${s.bags[String(t)]?.capacity??0} emplacements`:!available?'':i?`Ressources du palier ${t}`:t===1?'Outil simple mais fiable.':`Palier ${t} équipé.`;card.append(node('small','sf-tool-copy',copy));compare.append(card);
 }
 const heading=node('h3','sf-materials-heading','Matériaux nécessaires');placeStudio(stage,heading,18,62.0,66,2.2);
 const materials=node('section','realm-materials sf-materials');materials.setAttribute('aria-label','Recette d’amélioration');placeStudio(stage,materials,16.2,64.5,69,10.9);
 const recipe=(selected==='bag'?s.bag_recipes:s.recipes)[next]??{},cost=s.forge_gold[selected==='bag'?'bag':'tool'][next]??0,level=s.forge_levels[next]??0;
 for(const [name,qty] of Object.entries(recipe)){const c=node('article','sf-material');const art=resourceArt(name);if(art)c.append(art);c.append(node('span','sf-material-name',name),node('strong',(s.resources[name]??0)>=qty?'enough':'missing',`${s.resources[name]??0} / ${qty}`));materials.append(c);}
 if(max)materials.append(node('p','sf-max','Toutes les améliorations sont acquises.'));
 placeStudio(stage,node('h3','sf-cost-heading','Conditions et coût'),18,78.0,66,2.3);placeStudio(stage,node('strong','sf-cost',max?'—':`${cost} Gold`),29.5,81.0,18,2.5);placeStudio(stage,node('span','sf-level',max?'Palier maximum':`Niveau ${level} requis`),59.5,81.0,25,2.5);
 const missing=Object.entries(recipe).filter(([name,qty])=>(s.resources[name]??0)<qty).map(([name,qty])=>`${qty-(s.resources[name]??0)} ${name}`);const blockers=[!owned?'Achetez cet équipement au marché.':'',!max&&s.level<level?`Niveau ${level} requis.`:'',!max&&s.balance.wallet<cost?`${cost-s.balance.wallet} Gold manquants.`:'',missing.length?'Matériaux manquants : '+missing.join(', '):''].filter(Boolean);const diagnostic=node('p','studio-sr realm-forge-diagnostic',blockers.join(' '));diagnostic.id='studio-forge-requirements';stage.append(diagnostic);
 const action=studioButton(busy?'En cours…':'Améliorer',()=>void upgrade(),busy||!owned||max||s.level<level||s.balance.wallet<cost||!!missing.length);action.classList.add('sf-upgrade');action.setAttribute('aria-label','Améliorer');action.setAttribute('aria-describedby',diagnostic.id);action.title=blockers.join(' ')||forgeComparison(s,selected);placeStudio(stage,action,30.1,84.2,40.8,5.8);
 placeStudio(stage,studioButton('Retour en ville',()=>host.route('hub'),busy),34.2,91.8,33.5,4.0);
 const guide=studioButton('✧',()=>host.route('adventure-forge'),busy);guide.setAttribute('aria-label','Suivre une amélioration');guide.title='Préparatifs et ressources de forge';guide.classList.add('sf-guide');placeStudio(stage,guide,83,8,5,3.4);
 if(notice){const status=node('p','studio-notice',notice);status.setAttribute('role','status');placeStudio(stage,status,18,12.1,64,3.3);}
 if(focused)Array.from(panel.querySelectorAll<HTMLElement>('[aria-label]')).find(n=>n.getAttribute('aria-label')===focused)?.focus({preventScroll:true});
 }
 panel.onkeydown=e=>{if(e.key==='Escape'&&!busy){e.preventDefault();host.close();}if(e.key==='Tab'){const buttons=Array.from(panel.querySelectorAll<HTMLButtonElement>('button:not(:disabled)'));if(e.shiftKey&&document.activeElement===buttons[0]){e.preventDefault();buttons.at(-1)?.focus();}else if(!e.shiftKey&&document.activeElement===buttons.at(-1)){e.preventDefault();buttons[0]?.focus();}}};draw();return{update(){if(!busy)draw();},destroy(){dead=true;panel.onkeydown=null;document.body.classList.remove('illustrated-open');if(previous?.isConnected)previous.focus({preventScroll:true});}};
}
