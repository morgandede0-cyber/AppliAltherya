import {merchantAssets} from '../ui/assets';
export type SceneId='hub'|'tavern'|'barman'|'games'|'troubadour'|'market'|'forge'|'castle'|'arena'|'champion'|'bank'|'alley'|'guard'|'thief'|'robber'|'casino'|'expeditions'|'elarwyn'|'vorak';
export type Spot={label:string;x:number;y:number;w:number;h:number;action:string;embedded?:boolean;asset?:string};
type Scene={name:string;image:string;parent?:SceneId;caption:string;spots:Spot[]};
const spot=(label:string,x:number,y:number,w:number,h:number,action:string,embedded=false):Spot=>({label,x,y,w,h,action,embedded});
export const scenes:Record<SceneId,Scene>={
 hub:{name:'Legacy · La cité d’Altherya',image:'hub-panels-clean-v1.png',caption:'Choisissez un lieu dans la cité.',spots:[spot('Ruelle sombre',3,24,12,8,'scene:alley',true),spot('Taverne',26,25,13,10,'scene:tavern',true),spot('Château',54,16,10,7,'scene:castle',true),spot('Arène',88,18,10,7,'scene:arena',true),spot('Marché',11,58,11,9,'scene:market',true),spot('Forge',70,47,11,9,'scene:forge',true),spot('Banque',82,44,11,9,'scene:bank',true),spot('Petites annonces',0,0,10,10,'jobs'),spot('Panneau central',0,0,10,10,'gazette'),spot('Monde',0,0,10,10,'world'),spot('Mon profil',0,0,10,10,'profile')]},
 tavern:{name:'Taverne de Legacy',image:'tavern-predator.png',parent:'hub',caption:'Approchez du comptoir ou écoutez les récits des voyageurs.',spots:[]},
 barman:{name:'Le tavernier',image:'barman-predator.png',parent:'tavern',caption:'Le tavernier vous accueille près du feu.',spots:[]},
 games:{name:'Les jeux de la taverne',image:'games-predator.png',parent:'tavern',caption:'Les tables de la taverne.',spots:[]},
 troubadour:{name:'Le troubadour',image:'troubadour-predator.png',parent:'tavern',caption:'Une histoire commence.',spots:[]},
 market:{name:'Marché de Legacy',image:'merchant-predator.png',parent:'hub',caption:'Choisissez Histoire, Acheter, Vendre ou Partir.',spots:[spot('Histoire',37,68,25,14,'market:story'),spot('Acheter',65,68,25,14,'market:buy'),spot('Vendre',37,83,25,14,'market:sell'),spot('Partir',65,83,25,14,'scene:hub')]},
 forge:{name:'Forge de Legacy',image:'forge-predator.png',parent:'hub',caption:'Le marteau résonne dans la forge.',spots:[]},
 castle:{name:'Château de Legacy',image:'castle.webp',parent:'hub',caption:'Les affaires du royaume vous attendent.',spots:[]},
 arena:{name:'Arène de Legacy',image:'arena.webp',parent:'hub',caption:'La foule attend son champion.',spots:[]},
 champion:{name:'Champion de Legacy',image:'arena_champion.webp',parent:'arena',caption:'Le champion vous jauge.',spots:[]},
 bank:{name:'Banque de Legacy',image:'bank-predator.png',parent:'hub',caption:'Votre bourse et les coffres du royaume.',spots:[]},
 alley:{name:'Ruelle sombre',image:'alley-panels-clean-v1.png',parent:'hub',caption:'Des regards se tournent vers vous dans la ruelle.',spots:[spot('Le voleur',3,15,22,64,'scene:thief',true),spot('Le braqueur',41,24,22,51,'scene:robber',true),spot('Le vigile',68,10,28,66,'scene:guard',true),spot('Retour au hub',1,89,18,8,'scene:hub',true)]},
 guard:{name:'Le vigile',image:'alley_guard.webp',parent:'alley',caption:'Le vigile surveille le passage.',spots:[]},
 thief:{name:'Le voleur',image:'alley_thief.webp',parent:'alley',caption:'Le voleur sait des choses.',spots:[]},
 robber:{name:'Le brigand',image:'alley_robber.webp',parent:'alley',caption:'Un marché discret se négocie.',spots:[]},
 casino:{name:'Salle clandestine',image:'casino-clandestine-live.png',parent:'guard',caption:'Derrière les portes de la ruelle.',spots:[]},
 expeditions:{name:'Expéditions',image:'expeditions.webp',parent:'hub',caption:'Choisissez une terre à découvrir.',spots:[]},
 elarwyn:{name:'Forêt d’Elarwyn',image:'elarwyn.webp',parent:'expeditions',caption:'Bûcheronnage, chasse et cueillette : préparez votre voyage.',spots:[]},
 vorak:{name:'Mont Vorak',image:'vorak.webp',parent:'expeditions',caption:'Les hauteurs du royaume.',spots:[]}
};

// Menu links are part of the same navigation graph as image hotspots.
export const sceneMenus:Partial<Record<SceneId,string>>={market:'market',tavern:'tavern',barman:'drinks',games:'games',troubadour:'story',forge:'forge',castle:'castle',arena:'arena',champion:'arena',bank:'bank',guard:'guard',thief:'thief',robber:'robber',casino:'casino',expeditions:'expedition',elarwyn:'expedition',vorak:'expedition'};
export const menuRoutes:Partial<Record<string,SceneId[]>>={world:['hub','elarwyn','vorak','expeditions'],tavern:['barman','games','troubadour'],arena:['champion'],alley:['thief','robber','guard'],guard:['casino'],expedition:['elarwyn','vorak']};
export const unavailableScenes:SceneId[]=[];



for(const button of scenes.market.spots)button.asset=merchantAssets[button.label as keyof typeof merchantAssets];
