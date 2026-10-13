const node=(tag:string,cls='')=>{const n=document.createElement(tag);n.className=cls;return n;};
const path='/assets/menu-components/';
const headings=new Set('forge jobs castle arena games robber guard drinks podium dashboard techniques expedition tools destinations accessories departure live combat alley thief blackjack roulette russian slots horses'.split(' '));
const labels:Record<string,string>={
 'Le tavernier':'action-tavern-0','Les jeux':'action-tavern-1','Le troubadour':'action-tavern-2',
 'Le voleur':'action-alley-0','Le braqueur':'action-alley-1','Le vigile':'action-alley-2','Panneau de la ruelle':'action-alley-3',
 'Petit larcin':'action-thief-0','Voler un PNJ':'action-thief-1','Voler un joueur':'action-thief-2','Commettre un crime':'action-thief-3',
 'Tableau de bord':'action-castle-0','Podium':'action-castle-1','Récompense quotidienne':'action-castle-2',
 'Affronter le champion':'action-arena-0','Affronter un ami':'action-arena-1',
 'Bûcheron':'action-expedition-0','Mineur':'action-expedition-1','Chasseur':'action-expedition-2',
 'Lancer de dés':'action-games-0','Pile ou face':'action-games-1','Pierre feuille ciseaux':'action-games-2',
 'Black Jack':'action-casino-0','Roulette':'action-casino-1','Roulette russe':'action-casino-2','Machine à sous':'action-casino-3','Courses':'action-casino-4',
 'Hache':'forge-tab-0','Pioche':'forge-tab-1','Lance':'forge-tab-2','Sac':'forge-tab-3',
};
export function nativeHeading(kind:string,title:string){if(!headings.has(kind))return null;const h=node('h2','native-heading');const img=new Image();img.src=path+'title-'+kind+'.webp';img.alt=title;h.append(img);return h;}
export function nativeButton(button:HTMLButtonElement,kind=''){const label=button.getAttribute('aria-label')??'',name=labels[label];
 if(label==='Diminuer la mise'||label==='Augmenter la mise'){const image=new Image();image.src='/assets/bank-ui/'+(label==='Diminuer la mise'?'minus':'plus')+'.webp';image.alt='';image.className='native-button-art';button.classList.add('native-art-button','native-step-button');button.replaceChildren(image);return true;}
 const tradeTabs:Record<string,string>={Outils:'tab-tools.webp',Consommables:'tab-consumables.webp',Divers:'tab-misc.webp',Bûcheron:'tab-woodcutter.webp',Mineur:'tab-miner.webp',Chasseur:'tab-hunter.webp'};
 const marketHome:Record<string,string>={Acheter:'merchant-buy.webp',Vendre:'merchant-sell.webp',Histoire:'merchant-story.webp',Partir:'merchant-leave.webp'};
 const market=kind==='market'?marketHome[label]:kind.startsWith('market-')?tradeTabs[label]:undefined;
 if(!market&&(!name||(['Bûcheron','Mineur','Chasseur'].includes(label)&&kind!=='expedition')))return false;
 const image=new Image();image.src=market?'/assets/ui/'+market:path+name+'.webp';image.alt='';image.className='native-button-art';button.classList.add('native-art-button');button.replaceChildren(image);return true;}
