"""Physical destinations and private quest props, independent of trade inventory."""
import copy
SCENES={
 'hub':('Place centrale de Legacy',1),'market':('Le marchand',1),'bank':('Banque de Legacy',1),
 'barman':('Le tavernier',1),'troubadour':('Le troubadour',1),'thief':('Le voleur',1),
 'guard':('Le vigile',1),'robber':('Le braqueur',1),'forge':('Forge de Legacy',1),
 'castle':('Château de Legacy',1),'elarwyn':('Forêt d’Elarwyn',1),'vorak':('Mont Vorak',1),
 'khaz':('Thorgar · KHAZ’GORAM',3),'ashkar':('Tour d’Ashkar',5),'port':('Port des Brumes',1),
 'convois':('Bureau des convois',1),'archives':('Archives de la banque',1),'lisiere':('Halte de la Lisière',2),
 'sceaux':('Atelier des sceaux',5),'relais':('Relais de la Pierre Fendue',6),'veille':('Belvédère des Veilleurs',8),
 'tavern':('Taverne',1),'alley':('Ruelle sombre',1),'arena':('Arène',1),'champion':('Champion',1),
 'games':('Jeux de taverne',1),'casino':('Salle clandestine',1),'smogo':('Smogo',1),'expeditions':('Expéditions',1),
}
PARENTS={'convois':'market','archives':'bank','lisiere':'elarwyn','sceaux':'khaz','relais':'vorak','veille':'ashkar'}
GIVERS={'Marchand':'market','Tavernier':'barman','Voleur':'thief','Thorgar':'khaz','Troubadour':'troubadour',
 'Panneau des petites annonces':'hub','Joueur, au retour d’expédition':'forge','Mission des galeries':'vorak',
 'Joueur':'vorak','Dossier Ashkar':'ashkar','Intermédiaire':'castle','Mission finale':'vorak'}
# Every prop is bound to an actual search step and a later recipient. Not saleable.
PROPS={
 'S1-Q01-O2-I1':('recu','Double du reçu suspect','S1-Q01-O3'),
 'S1-Q02-O1-I3':('attestation','Attestation de la banque','S1-Q02-O3'),
 'S1-Q05-O3':('plaque','Plaque de transport','S1-Q06-O1'),
 'S2-Q06-O1-I3':('journal','Fragments du journal de convoi','S2-Q06-O2'),
}
WORK={
 'S1-Q03-O2':[('Écouter le premier voyageur','Le premier voyageur décrit une caisse portant une marque repeinte.'),('Écouter le second voyageur','Le second confirme la même route, mais une autre commande.')],
 'S1-Q08-O1':[('Examiner le chargement','Le chargement porte le numéro d’un seul lot.'),('Comparer les deux reçus','Deux reçus prétendent couvrir ce même lot.'),('Interroger le convoyeur','Le convoyeur confirme n’avoir reçu qu’un ordre de départ.')],
 'S2-Q07-O2':[('Évaluer la voûte','La voûte doit être étayée avant de déplacer les gravats.'),('Consolider les étais','Vous consolidez l’appui près de la galerie.'),('Ouvrir la sortie','Une voie de repli reste dégagée pour les secours.')],
 'S3-Q02-O1':[('Relever le sommet occidental','Le relief occidental fournit le premier axe de visée.'),('Relever le sommet central','Le sommet central coupe le tracé ancien.'),('Relever le sommet oriental','Le troisième point permet de comparer les orientations.')],
 'S3-Q03-O1':[('Vérifier la première balise','La marque du convoi est visible sur le bois.'),('Suivre les traces de roues','Les traces convergent vers le passage de Vorak.'),('Noter l’horaire du passage','Le guetteur vous transmet l’heure du dernier chariot.')],
 'S3-Q03-O2':[('Vérifier la balise du col','La balise porte la même marque qu’à Elarwyn.'),('Observer la direction des traces','Les chariots se dirigent vers le col.'),('Interroger le guetteur','Son horaire peut être confronté au relevé d’Elarwyn.')],
 'S3-Q08-O1':[('Prévenir les ouvriers','Les ouvriers cessent le travail et rejoignent l’abri.'),('Libérer la sortie','Le passage de secours est dégagé.'),('Protéger les pièces','Les pièces conservées sont mises hors de portée des assaillants.')],
 'S4-Q01-O2':[('Interroger les voyageurs','Les derniers départs concernaient des convoyeurs de Legacy.'),('Lire le carnet du comptoir','Le carnet donne l’heure et la composition du groupe.'),('Comparer les fournitures','Les réserves manquantes indiquent un trajet plus long qu’annoncé.')],
 'S4-Q05-O1':[('Repérer les voyageurs','Vous distinguez les voyageurs des hommes armés.'),('Vérifier le signal convenu','Les équipes de secours attendent le signal prévu par votre plan.'),('Sécuriser le repli','Une voie de retour est disponible avant l’intervention.')],
 'S4-Q07-O2':[('Rassembler les rescapés','Les personnes présentes sont regroupées à l’abri.'),('Baliser le retour','Vous indiquez le passage sécurisé.'),('Accompagner le dernier groupe','Aucun voyageur n’est laissé sur le passage instable.')],
 'witness-account':[('Recueillir les témoignages','Les personnes secourues reconstituent l’intervention.'),('Faire signer le relevé','Les témoins valident le relevé destiné au château.')],
 'plan-check':[('Vérifier le premier poste','Le premier poste confirme que les voyageurs sont hors du danger immédiat.'),('Vérifier la voie de secours','Le groupe de secours dispose d’un accès libre.')],
}
# Coordinates follow the existing paintings: ledger, counter, crate, trail, workbench.
SEARCH_POSITIONS={
 'convois':[[58,74],[82,77],[32,42]],'archives':[[45,67],[65,73],[83,58]],
 'lisiere':[[43,73],[12,52],[86,61]],'sceaux':[[43,63],[65,58],[83,77]],
 'relais':[[57,74],[40,37],[14,49]],'veille':[[54,23],[61,60],[33,73]],
}
STEP_POSITIONS={
 'S1-Q05-O1':[[83,48],[76,68],[90,78]],
 'S2-Q06-O1':[[13,47],[34,49],[10,66]],
 'S3-Q07-O1':[[84,33],[64,76],[67,39]],
}
def destination(step):
 if step.get('place_id'):return step['place_id']
 if step['kind']=='port':return 'port'
 place=step.get('place','').casefold()
 for needle,scene in [('thorgar','khaz'),('khaz','khaz'),('ashkar','ashkar'),('troubadour','troubadour'),('tavernier','barman'),('voleur','thief'),('vigile','guard'),('braqueur','robber'),('banque','bank'),('march','market'),('forge','forge'),('château','castle'),('vorak','vorak'),('convoi','vorak'),('elarwyn','elarwyn'),('lisière','elarwyn'),('taverne','barman')]:
  if needle in place:return scene
 return 'hub'

def decorate(q,new=False):
 q=copy.deepcopy(q)
 q['giver_scene']=GIVERS.get(q['giver'],'castle')
 q['giver_name']=q['giver'] if q['giver_scene']=='hub' else SCENES[q['giver_scene']][0]
 for step in q['steps']:
  # Fix the physical extraction location without rewriting accepted legacy steps.
  if new and step['id']=='S1-Q05-O3':step.update(kind='collect',place='Halte de la Lisière',place_id='lisiere',scene_image='quest-place-lisiere-v1.png')
  if new and step['id']=='S2-Q08-O2':step.update(place='Château de Legacy',scene_image='castle.webp')
  step['world_scene']=destination(step)
  step['world_name']=SCENES[step['world_scene']][0]
  if new and step['kind']=='mission' and step['id'] in WORK:
   step['work_points']=[dict(id=str(i),label=label,text=text,position=[[25,60],[52,47],[77,62]][i%3]) for i,(label,text) in enumerate(WORK[step['id']])]
  if step['id'] in PROPS:step['prop']={'id':PROPS[step['id']][0],'name':PROPS[step['id']][1],'position':[76,68]}
  if step.get('clues'):
   for i,clue in enumerate(step['clues']):
    clue['position']=STEP_POSITIONS.get(step['id'],SEARCH_POSITIONS.get(step.get('place_id'),[[24,62],[55,51],[78,62]]))[i%3]
    if clue['id'] in PROPS:clue['prop']={'id':PROPS[clue['id']][0],'name':PROPS[clue['id']][1]}
 q['return_scene']=q['steps'][-1]['world_scene'] if q['giver']=='Joueur' else q['giver_scene']
 return q

def target(q,row):
 if row['accepted_at'] is None:return q['giver_scene']
 if row['stage']>=len(q['steps']):return q.get('return_scene',q['giver_scene'])
 return q['steps'][row['stage']]['world_scene']

def maintenance_scene(scene):return {'barman':'tavern','troubadour':'story','ashkar':'tower'}.get(scene,scene)
