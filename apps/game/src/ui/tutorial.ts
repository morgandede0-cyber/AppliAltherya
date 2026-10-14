import type {Snapshot} from '../activity';
import {mountMenu,menuCard,menuButton,node,watchFramework} from './menu-framework';
import {sizeMenu} from './menu-layout';
type Host={state:()=>Snapshot;mutate:(body:Record<string,unknown>)=>Promise<string>;done:()=>void;notify:(message:string)=>void};
// Restored from TutorialIntro/Navigation/Profile/Start/Places/RewardView in the bot.
const pages=[
 {title:'Aux portes de Legacy',lead:'Le garde vous accueille',sections:[['Première visite ?', '« Je vais t’éviter de tourner en rond pendant trois jours. »'],['Votre aventure commence ici','Apprenez à vous déplacer, à faire progresser votre personnage et à gagner vos premiers Gold. Quelques minutes pour connaître l’essentiel.']]},
 {title:'Se repérer',lead:'1 / 5 · Votre point de départ',sections:[['Legacy','Le cœur de votre aventure et l’accès aux activités.'],['Monde','Rejoignez les destinations extérieures depuis la carte.'],['Retour','Revenez à l’écran précédent sans perdre votre progression.'],['PC et mobile','Les menus s’adaptent à la place disponible. Commencez par les activités accessibles : les niveaux ouvriront de nouvelles possibilités.']]},
 {title:'Votre personnage',lead:'2 / 5 · Les informations essentielles',sections:[['PV, niveau et XP','Les PV sont vos points de vie en combat. Jouez aux activités pour gagner de l’XP ; les niveaux débloquent progressivement le contenu.'],['Gold et ressources','Les Gold servent à acheter et à jouer. Les matériaux récoltés permettent notamment d’améliorer vos outils à la Forge.'],['Inventaire et équipement','Vos objets et ressources sont conservés dans votre profil. L’équipement améliore vos possibilités dans certaines activités.'],['Réputations','Vos actions influencent la manière dont les habitants vous considèrent.']]},
 {title:'Bien démarrer',lead:'3 / 5 · Vos premières minutes',sections:[['Au Château','Récupérez votre récompense quotidienne et consultez votre tableau de bord.'],['En expédition','Commencez mains nues : aucun équipement n’est nécessaire pour votre première récolte.'],['Aux Petites annonces','Choisissez un contrat, signez-le puis revenez chercher la récompense à la fin du délai.'],['À la Taverne et à l’Arène','Découvrez les activités de la Taverne, puis testez votre personnage face au champion lorsque vous êtes prêt.']]},
 {title:'Les lieux à connaître',lead:'4 / 5 · Pas besoin de tout mémoriser',sections:[['Château et Banque','Votre tableau de bord et la récompense quotidienne au Château ; la gestion de vos Gold à la Banque.'],['Marché et Forge','Achetez ou vendez au Marché. Améliorez vos outils et votre sac à la Forge.'],['Taverne et Petites annonces','Jeux, boissons, récits et contrats pour donner une direction à vos prochaines activités.'],['Arène, Monde et Ruelle sombre','Combattez le champion, découvrez les destinations de la carte et mesurez les risques avant d’agir dans la Ruelle. Certains accès demandent de progresser.']]},
 {title:'Prêt pour Legacy',lead:'5 / 5 · Les portes sont ouvertes',sections:[['Si vous êtes perdu','Commencez par le Château, une expédition, les Petites annonces et la Taverne.'],['À retenir','Les niveaux ouvrent de nouvelles possibilités. Évitez de risquer tous vos Gold dans les jeux ; les activités de la Ruelle ont aussi leurs conséquences.'],['Le garde','« Maintenant, écris ta propre histoire. » Vous pourrez relire ce tutoriel depuis votre profil.']]},
];
export function openTutorial(panel:HTMLElement,host:Host){
 let locked=false,destroyed=false,error='';
 async function perform(action:string){if(locked||destroyed)return;const step=host.state().tutorial.step;locked=true;error='';draw();try{const message=await host.mutate({action,step});if(destroyed)return;if(message)host.notify(message);const t=host.state().tutorial;if((action==='tutorial_finish'||action==='tutorial_cancel')&&t.completed&&!t.replay){host.done();return;}}catch(e){error=e instanceof Error?e.message:String(e);}finally{locked=false;if(!destroyed){draw();panel.querySelector<HTMLButtonElement>('button:not(:disabled)')?.focus({preventScroll:true});}}}
 function draw(){
  if(destroyed)return;const t=host.state().tutorial,index=Math.max(0,Math.min(5,t.step)),page=pages[index],scroll=panel.querySelector('.gm-body')?.scrollTop??0;
  const focused=panel.contains(document.activeElement)?document.activeElement?.getAttribute('aria-label'):null;const previous=Number(panel.dataset.tutorialStep);const {body,footer}=mountMenu(panel,'tutorial',page.title,locked);panel.dataset.tutorialStep=String(index);
  const lead=node('p','tutorial-lead',page.lead);body.append(lead);
  const steps=node('div','tutorial-steps');steps.setAttribute('aria-label',`Tutoriel : ${index===0?'accueil':`étape ${index} sur 5`}`);for(let i=1;i<=5;i++){const dot=node('span',i<=index?'done':'',String(i));if(i===index)dot.setAttribute('aria-current','step');steps.append(dot);}body.append(steps);
  const grid=node('div','tutorial-sections');for(const [title,copy] of page.sections)menuCard(grid,title,copy);body.append(grid);
  if(index===0||index===5){const reward=node('p','tutorial-reward',t.reward_claimed?'Récompense de bienvenue déjà obtenue. La relecture ne donne aucun gain supplémentaire.':`${t.gold} Gold + ${t.xp} XP à la fin de votre premier parcours.`);body.append(reward);}
  if(error){const notice=node('p','gm-notice',error);notice.setAttribute('role','alert');body.prepend(notice);}
  if(page.sections.length>2&&(innerWidth<=700||innerHeight<=650))footer.append(node('p','tutorial-scroll-hint','Faites défiler le panneau pour lire la suite.'));
  const label=index===0?'Commencer le tutoriel':index===5?'Entrer dans Legacy':'Continuer le tutoriel';footer.append(menuButton(locked?'Enregistrement…':label,()=>void perform(index===5?'tutorial_finish':'tutorial_next'),locked));
  if(t.replay)footer.append(menuButton('Fermer le tutoriel',()=>void perform('tutorial_cancel'),locked));
  sizeMenu(panel,0,800);body.scrollTop=!error&&previous===index?scroll:0;if(focused&&!locked)Array.from(panel.querySelectorAll<HTMLButtonElement>('button')).find(b=>b.getAttribute('aria-label')===focused)?.focus({preventScroll:true});
 }
 const stop=watchFramework(panel,()=>locked,()=>{if(host.state().tutorial.replay)void perform('tutorial_cancel');});draw();
 panel.querySelector<HTMLButtonElement>('button')?.focus({preventScroll:true});
 return {destroy(){destroyed=true;stop();document.body.classList.remove('illustrated-open');},update(){if(!locked)draw();}};
}
