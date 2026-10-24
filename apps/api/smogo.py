"""Smogo's knowledge wagers. Private answers and atomic, one-shot settlement."""
import hashlib,json,re,secrets,time,unicodedata
from game_clock import today,ZONE
from datetime import datetime,timedelta
MIN_WAGER=1
MAX_WAGER=500
DAILY_LIMIT=1
DURATION=120
# Multiple accepted words cover genuine synonyms, never approximate guesses.
RIDDLES=(
 ('echo','Je répète tes paroles dans la montagne sans avoir de bouche. Qui suis-je ?',('écho',),'Un écho renvoie le son de votre voix.'),
 ('ombre','Je reproduis ta silhouette sur les pavés quand une lumière te frappe. Qui suis-je ?',('ombre',),'Une ombre se forme lorsque votre corps arrête la lumière.'),
 ('bougie','J’ai une mèche, je donne de la lumière et mon corps de cire fond. Qui suis-je ?',('bougie','chandelle'),'La cire de la bougie fond autour de sa mèche.'),
 ('eponge','Je suis pleine de trous et pourtant je retiens l’eau. Qui suis-je ?',('éponge',),'Les pores de l’éponge retiennent l’eau.'),
 ('serviette','Plus je sèche les mains des voyageurs, plus je deviens mouillée. Qui suis-je ?',('serviette','torchon','essuie-mains'),'Le tissu absorbe l’eau des mains.'),
 ('carte','Je montre des villes sans habitants et des rivières sans eau, sur une feuille. Qui suis-je ?',('carte','carte géographique','plan'),'Une carte représente les lieux sans les contenir.'),
 ('silence','Il suffit de parler pour me briser. Qui suis-je ?',('silence',),'Une parole met fin au silence.'),
 ('avenir','Je désigne le temps qui n’est pas encore arrivé. Qui suis-je ?',('avenir','futur'),'Le futur est le temps à venir.'),
 ('sablier','Deux ampoules de verre et du sable me permettent de mesurer le temps. Qui suis-je ?',('sablier',),'Le sable du sablier passe d’une ampoule à l’autre.'),
 ('cle','Petite pièce de métal taillée pour une serrure, j’ouvre une porte sans la briser. Qui suis-je ?',('clé','clef'),'La clé actionne le mécanisme de la serrure.'),
 ('livre','Mes feuilles ne poussent sur aucun arbre : elles sont reliées et portent des chapitres. Qui suis-je ?',('livre','grimoire','ouvrage'),'Les pages reliées forment un livre.'),
 ('ancre','Reliée au navire par une chaîne, je repose au fond pour le retenir. Qui suis-je ?',('ancre',),'L’ancre empêche le navire de dériver.'),
 ('boussole','Mon aiguille aimantée montre le nord aux voyageurs. Qui suis-je ?',('boussole','compas'),'L’aiguille d’une boussole s’oriente vers le nord magnétique.'),
 ('lune','Satellite de votre monde, je brille la nuit grâce à la lumière du soleil. Qui suis-je ?',('lune',),'La Lune réfléchit la lumière du Soleil.'),
 ('horloge','Mes aiguilles ne cousent pas : elles indiquent les heures. Qui suis-je ?',('horloge','montre','pendule'),'Les aiguilles d’une horloge indiquent l’heure.'),
 ('traces','Mes empreintes restent dans la neige derrière le voyageur qui marche. Que sont-elles ?',('pas','traces','empreintes','traces de pas'),'Les pas laissent des empreintes.'),
 ('secret','Je suis une information cachée. Si tout le monde me connaît, je ne le suis plus. Qui suis-je ?',('secret',),'Un secret cesse d’être caché quand il est connu de tous.'),
 ('fumee','Née d’un feu, je monte dans l’air et me disperse au vent. Je ne suis pas la flamme. Qui suis-je ?',('fumée',),'La fumée s’élève puis se disperse dans l’air.'),
 ('fleuve','Je suis un grand cours d’eau qui se jette directement dans la mer. Qui suis-je ?',('fleuve',),'Un fleuve se jette dans la mer, contrairement à une rivière qui rejoint un autre cours d’eau.'),
 ('noeud','Je suis un entrelacement serré de corde que le marin fait puis défait. Qui suis-je ?',('nœud','noeud'),'Le marin noue la corde pour former un nœud.'),
 ('library-021', 'Sur les côtes, ma lumière tourne en haut d’une tour pour guider les navires la nuit. Qui suis-je ?', ('phare',), 'Le phare signale la côte et guide les navires.'),
 ('library-022', 'Tendu au-dessus du pont du navire, je prends le vent pour le faire avancer. Qui suis-je ?', ('voile',), 'La voile transforme la poussée du vent en mouvement.'),
 ('library-023', 'Longue pièce plate plongée dans l’eau, je fais avancer la barque quand le rameur me tire. Qui suis-je ?', ('rame', 'aviron'), 'La rame pousse l’eau et déplace la barque.'),
 ('library-024', 'Fixé à l’arrière du navire et relié à la barre, je change sa direction dans l’eau. Qui suis-je ?', ('gouvernail',), 'Le gouvernail permet de diriger le navire.'),
 ('library-025', 'Je suis la pièce principale dressée verticalement sur le pont, qui porte les voiles. Qui suis-je ?', ('mât',), 'Le mât porte les voiles et leur gréement.'),
 ('library-026', 'Je suis une petite embarcation manœuvrée avec des rames, sans voile ni moteur. Qui suis-je ?', ('barque', 'canot'), 'Une barque ou un canot se déplace à la rame.'),
 ('library-027', 'Je suis le lieu abrité où les navires viennent s’amarrer, charger et décharger. Qui suis-je ?', ('port',), 'Le port accueille les navires et leurs marchandises.'),
 ('library-028', 'Je suis une réserve de nourriture que le marin cuit en galette : mes grains moulus deviennent une poudre blanche. Qui suis-je ?', ('farine',), 'La farine est obtenue par mouture des grains.'),
 ('library-029', 'Le boulanger me pétrit avec de l’eau et de la farine avant de me cuire pour servir des miches. Que suis-je une fois cuit ?', ('pain',), 'La pâte cuite donne le pain.'),
 ('library-030', 'Je suis le foyer fermé du boulanger où les miches cuisent. Qui suis-je ?', ('four',), 'Le four apporte la chaleur nécessaire à la cuisson.'),
 ('library-031', 'Je suis le meuble de la taverne sur lequel on pose les assiettes pour manger assis. Qui suis-je ?', ('table',), 'Les convives mangent autour de la table.'),
 ('library-032', 'À la taverne, je suis un siège sans dossier, souvent placé devant le comptoir. Qui suis-je ?', ('tabouret',), 'Le tabouret est un siège sans dossier.'),
 ('library-033', 'J’ai une anse et je contiens la boisson du client ; on me porte aux lèvres pour boire. Qui suis-je ?', ('tasse', 'chope', 'mug'), 'La tasse et la chope sont des récipients à anse.'),
 ('library-034', 'Je suis le grand récipient de bois cerclé de métal où le tavernier conserve sa boisson. Qui suis-je ?', ('tonneau', 'fût', 'barrique'), 'Les douves et les cercles composent un tonneau.'),
 ('library-035', 'Je suis la petite pièce que l’on retire du goulot d’une bouteille pour l’ouvrir. Qui suis-je ?', ('bouchon',), 'Le bouchon ferme le goulot.'),
 ('library-036', 'Je suis le récipient à large ouverture et à anse que l’on descend dans le puits pour remonter l’eau. Qui suis-je ?', ('seau',), 'Le seau permet de puiser et transporter l’eau.'),
 ('library-037', 'Je suis le passage creusé dans le sol pour atteindre l’eau souterraine avec un seau. Qui suis-je ?', ('puits',), 'Le puits donne accès à une réserve d’eau souterraine.'),
 ('library-038', 'Je suis le petit ouvrage qui permet de franchir la rivière sans se mouiller les pieds. Qui suis-je ?', ('pont', 'passerelle'), 'Un pont relie les deux rives.'),
 ('library-039', 'Je suis un escalier mobile à deux montants et des barreaux, que l’on appuie contre un mur. Qui suis-je ?', ('échelle',), 'L’échelle permet de monter en prenant appui sur ses barreaux.'),
 ('library-040', 'Je suis la plaque mobile, fixée sur des gonds, qui ferme l’entrée d’une maison. Qui suis-je ?', ('porte',), 'La porte pivote sur ses gonds.'),
 ('library-041', 'Je suis l’ouverture vitrée d’une maison qui laisse entrer le jour. Qui suis-je ?', ('fenêtre',), 'La fenêtre laisse passer la lumière.'),
 ('library-042', 'Je couvre la maison tout en haut et protège ses habitants de la pluie. Qui suis-je ?', ('toit', 'toiture'), 'Le toit abrite le bâtiment des intempéries.'),
 ('library-043', 'Je suis le conduit qui évacue la fumée du foyer au-dessus du toit. Qui suis-je ?', ('cheminée',), 'La cheminée évacue les fumées du feu.'),
 ('library-044', 'Je suis une lampe protégée par des parois transparentes, que le veilleur porte par une anse. Qui suis-je ?', ('lanterne',), 'La lanterne protège sa flamme tout en laissant passer la lumière.'),
 ('library-045', 'Je suis un bâton dont l’extrémité enflammée éclaire le couloir de pierre. Qui suis-je ?', ('torche', 'flambeau'), 'Une torche porte une flamme à son extrémité.'),
 ('library-046', 'Je suis la barre de métal qui bloque une porte quand on me fait coulisser dans mon logement. Qui suis-je ?', ('verrou', 'loquet'), 'Le verrou bloque l’ouverture de la porte.'),
 ('library-047', 'Je suis la protection portée sur le bras pour arrêter les coups de l’adversaire. Qui suis-je ?', ('bouclier',), 'Le bouclier sert à parer les coups.'),
 ('library-048', 'Je suis l’arme à lame longue et à poignée que le guerrier porte dans un fourreau. Qui suis-je ?', ('épée', 'glaive'), 'Une épée possède une lame et se range dans un fourreau.'),
 ('library-049', 'Je suis l’étui porté à la ceinture dans lequel on range la lame d’une épée. Qui suis-je ?', ('fourreau',), 'Le fourreau protège la lame et son porteur.'),
 ('library-050', 'Je suis l’arme courbe dont on tend la corde pour lancer une flèche. Qui suis-je ?', ('arc',), 'La tension de l’arc propulse la flèche.'),
 ('library-051', 'Je suis le projectile empenné que l’archer place sur la corde de son arc. Qui suis-je ?', ('flèche',), 'Les plumes stabilisent la flèche en vol.'),
 ('library-052', 'Je suis l’étui dans lequel l’archer transporte ses flèches. Qui suis-je ?', ('carquois',), 'Le carquois rassemble les flèches.'),
 ('library-053', 'Je suis la protection rigide portée sur la tête du combattant. Qui suis-je ?', ('casque', 'heaume'), 'Le casque protège la tête.'),
 ('library-054', 'Je suis la protection articulée de métal qui enveloppe la main du chevalier. Qui suis-je ?', ('gantelet',), 'Le gantelet est le gant métallique de l’armure.'),
 ('library-055', 'Je suis le vêtement défensif formé de petits anneaux de métal entrelacés. Qui suis-je ?', ('cotte de mailles', 'cotte de maille', 'haubert'), 'La cotte de mailles est constituée d’anneaux entrelacés.'),
 ('library-056', 'À la forge, je suis le lourd bloc de métal sur lequel on frappe le fer chaud. Qui suis-je ?', ('enclume',), 'L’enclume reçoit les coups du forgeron.'),
 ('library-057', 'À la forge, je suis l’outil à manche qui frappe le métal posé sur l’enclume. Qui suis-je ?', ('marteau',), 'Le marteau façonne le métal par percussion.'),
 ('library-058', 'Je suis le dispositif à poche souple qui envoie de l’air sur les braises de la forge. Qui suis-je ?', ('soufflet',), 'Le soufflet apporte de l’air au feu.'),
 ('library-059', 'Je suis le petit récipient résistant à la chaleur dans lequel on fait fondre le métal. Qui suis-je ?', ('creuset',), 'Le creuset contient le métal en fusion.'),
 ('library-060', 'Je suis l’outil à deux mâchoires qui permet au forgeron de tenir le fer brûlant à distance. Qui suis-je ?', ('tenaille', 'tenailles', 'pince', 'pinces'), 'Les tenailles maintiennent les pièces chaudes.'),
 ('library-061', 'Je suis le trou creusé pour extraire le minerai du sous-sol. Qui suis-je ?', ('mine',), 'Une mine permet d’extraire les minerais.'),
 ('library-062', 'Je suis l’outil du mineur, à manche et à tête pointue, qui attaque la roche. Qui suis-je ?', ('pioche',), 'La pioche sert à briser la roche.'),
 ('library-063', 'Je suis l’outil à lame fixé à un manche avec lequel le bûcheron abat les arbres. Qui suis-je ?', ('hache',), 'La hache coupe le bois.'),
 ('library-064', 'Je suis la partie d’un arbre qui reste enracinée après qu’on a coupé le tronc près du sol. Qui suis-je ?', ('souche',), 'La souche est la base restante de l’arbre abattu.'),
 ('library-065', 'Je suis la partie de l’arbre qui s’étend sous terre et absorbe l’eau. Qui suis-je ?', ('racine', 'racines'), 'Les racines puisent l’eau dans le sol.'),
 ('library-066', 'Je suis le fruit du chêne, coiffé d’une petite cupule. Qui suis-je ?', ('gland',), 'Le gland est le fruit du chêne.'),
 ('library-067', 'Je suis le fruit du pin, formé d’écailles de bois qui protègent ses graines. Qui suis-je ?', ('pomme de pin', 'cône', 'cône de pin'), 'Le cône du pin porte les graines entre ses écailles.'),
 ('library-068', 'Je suis le liquide sucré fabriqué par les abeilles et conservé dans leurs rayons. Qui suis-je ?', ('miel',), 'Les abeilles produisent le miel.'),
 ('library-069', 'Je suis l’abri construit par l’apiculteur pour héberger sa colonie d’abeilles. Qui suis-je ?', ('ruche',), 'La ruche abrite les abeilles domestiques.'),
 ('library-070', 'Je suis la demeure d’oiseau faite de brindilles qui accueille ses œufs. Qui suis-je ?', ('nid',), 'Le nid accueille les œufs et les oisillons.'),
 ('library-071', 'Je suis l’enveloppe dure et cassante qui protège le contenu de l’œuf. Qui suis-je ?', ('coquille', 'coquille d’œuf'), 'La coquille protège l’œuf.'),
 ('library-072', 'Je suis le fil que l’araignée tisse pour prendre ses proies. Quel ouvrage forme ce fil ?', ('toile', 'toile d’araignée'), 'La toile sert de piège à l’araignée.'),
 ('library-073', 'Je suis le mammifère volant qui se repère grâce aux échos de ses cris dans l’obscurité. Qui suis-je ?', ('chauve-souris', 'chauve souris'), 'Les chauves-souris utilisent l’écholocation.'),
 ('library-074', 'Je suis le rapace nocturne reconnaissable à mes aigrettes, petites touffes dressées sur la tête. Qui suis-je ?', ('hibou',), 'Le hibou porte des aigrettes, contrairement à la chouette.'),
 ('library-075', 'Je suis la partie rigide et cornée qui couvre le pied du cheval. Qui suis-je ?', ('sabot',), 'Le sabot protège le pied du cheval.'),
 ('library-076', 'Je suis la pièce de métal en forme de U que le maréchal fixe sous le sabot. Qui suis-je ?', ('fer à cheval', 'fer'), 'Le fer protège le sabot contre l’usure.'),
 ('library-077', 'Je suis le siège fixé sur le dos du cheval pour accueillir le cavalier. Qui suis-je ?', ('selle',), 'La selle soutient le cavalier.'),
 ('library-078', 'Je suis l’une des deux boucles suspendues à la selle dans lesquelles le cavalier pose les pieds. Qui suis-je ?', ('étrier', 'étriers'), 'Les étriers soutiennent les pieds du cavalier.'),
 ('library-079', 'Je suis la courroie que le cavalier tient en main pour diriger son cheval. Qui suis-je ?', ('rêne', 'rênes'), 'Les rênes transmettent les indications du cavalier.'),
 ('library-080', 'Je suis la voiture à deux roues que tire un cheval pour transporter un chargement. Qui suis-je ?', ('charrette',), 'La charrette est un véhicule de transport à deux roues.'),
 ('library-081', 'Je suis l’objet rond fixé sur un axe qui permet à la charrette de rouler. Qui suis-je ?', ('roue',), 'La roue tourne autour de son axe.'),
 ('library-082', 'Je suis la poudre grise, résidu froid du bois entièrement brûlé dans le foyer. Qui suis-je ?', ('cendre', 'cendres'), 'Les cendres restent après la combustion du bois.'),
 ('library-083', 'Je suis l’eau devenue solide sous l’effet du froid. Qui suis-je ?', ('glace',), 'L’eau gèle et devient de la glace.'),
 ('library-084', 'Je suis le dépôt de gouttelettes qui se forme sur l’herbe au petit matin, sans pluie. Qui suis-je ?', ('rosée',), 'La rosée résulte de la condensation de l’humidité.'),
 ('library-085', 'Je suis la pluie de petits grains de glace qui frappent les toits pendant un orage. Qui suis-je ?', ('grêle',), 'La grêle est une précipitation de grains de glace.'),
 ('library-086', 'Je suis l’arc coloré visible quand la lumière du soleil traverse les gouttes de pluie. Qui suis-je ?', ('arc-en-ciel', 'arc en ciel'), 'Les gouttes décomposent la lumière en couleurs.'),
 ('library-087', 'Je suis la lumière soudaine qui traverse le ciel pendant l’orage, avant qu’on entende le bruit. Qui suis-je ?', ('éclair', 'foudre'), 'L’éclair est la manifestation lumineuse de la décharge électrique.'),
 ('library-088', 'Je suis le grondement de l’orage, entendu après l’éclair. Qui suis-je ?', ('tonnerre',), 'Le tonnerre est le bruit produit par la décharge.'),
 ('library-089', 'Je suis le brouillard à très basse température qui dépose de fins cristaux blancs sur les branches. Quel dépôt laisse-t-il ?', ('givre',), 'Le givre forme des cristaux de glace sur les surfaces froides.'),
 ('library-090', 'Je suis le vent très violent qui tourne en colonne étroite et touche le sol sous un nuage. Qui suis-je ?', ('tornade',), 'La tornade forme une colonne d’air tourbillonnante.'),
 ('library-091', 'Une course compte dix cavaliers. Tu dépasses celui qui est deuxième. Quelle place occupes-tu ? Réponds en chiffres.', ('2',), 'Tu prends la place du deuxième cavalier, donc la deuxième place.'),
 ('library-092', 'Une marchande a trois filles. Chacune de ses filles a un frère, et c’est le même pour toutes. Combien a-t-elle d’enfants ? Réponds en chiffres.', ('4',), 'Trois filles et leur frère commun font quatre enfants.'),
 ('library-093', 'Deux pères et deux fils se partagent trois pommes : chacun en reçoit une. Quel est le nombre minimal de personnes ? Réponds en chiffres.', ('3',), 'Un grand-père, son fils et son petit-fils représentent deux pères et deux fils.'),
 ('library-094', 'Un escargot monte de trois mètres le jour et glisse de deux mètres chaque nuit. Il part du pied d’un mur de dix mètres. Quel jour atteint-il le sommet ? Réponds en chiffres.', ('8',), 'Il gagne un mètre par cycle. Au matin du huitième jour il est à sept mètres et atteint dix mètres sans redescendre.'),
 ('library-095', 'Trois chats attrapent trois souris en trois minutes. Chaque chat chasse au même rythme. Combien de minutes faut-il à six chats pour attraper six souris ? Réponds en chiffres.', ('3',), 'Chaque chat attrape une souris en trois minutes, même avec six chats.'),
 ('library-096', 'Un coffre contient cinq gemmes rouges et cinq bleues, indiscernables au toucher. Dans le noir, combien faut-il en prendre au minimum pour être certain d’en avoir deux de la même couleur ? Réponds en chiffres.', ('3',), 'Avec trois gemmes et seulement deux couleurs, deux ont forcément la même couleur.'),
 ('library-097', 'Deux cordes brûlent chacune en exactement une heure, mais de façon irrégulière. Tu allumes la première aux deux bouts et la seconde à un seul bout. Quand la première s’éteint, tu allumes l’autre bout de la seconde. Après combien de minutes au total s’éteint la seconde ? Réponds en chiffres.', ('45',), 'La première dure trente minutes. Il reste trente minutes à la seconde ; allumée aux deux bouts, elle finit en quinze minutes de plus.'),
 ('library-098', 'Un médecin donne trois potions à prendre à trente minutes d’intervalle, la première immédiatement. Après combien de minutes prends-tu la dernière ? Réponds en chiffres.', ('60',), 'Les prises ont lieu à zéro, trente et soixante minutes.'),
 ('library-099', 'Sur une balance, une brique pèse un kilogramme plus la moitié de son propre poids. Combien de kilogrammes pèse-t-elle ? Réponds en chiffres.', ('2',), 'La moitié de la brique pèse un kilogramme ; la brique entière en pèse deux.'),
 ('library-100', 'Un nénuphar double de surface chaque jour et couvre entièrement l’étang au trentième jour. Quel jour en couvrait-il exactement la moitié ? Réponds en chiffres.', ('29',), 'La veille du dernier doublement, la surface couverte était la moitié.'),
)

def normalise(text):
 text=unicodedata.normalize('NFKD',text.casefold().replace('œ','oe'))
 text=''.join(x for x in text if not unicodedata.combining(x))
 words=re.findall(r'[a-z0-9]+',text)
 while words and words[0] in ('un','une','le','la','les','des','l'):words.pop(0)
 return ' '.join(words)

class Smogo:
 def __init__(self,a):
  self.a=a
  with a.conn() as c:
   c.execute('CREATE TABLE IF NOT EXISTS activity_smogo(user_id INTEGER PRIMARY KEY,revision INTEGER NOT NULL DEFAULT 0,day TEXT NOT NULL DEFAULT "",attempts INTEGER NOT NULL DEFAULT 0,payload TEXT NOT NULL DEFAULT "{}")')
   c.execute('CREATE TABLE IF NOT EXISTS activity_smogo_questions(signature TEXT PRIMARY KEY)')
 def presence(self,c):
  now=time.time();date=datetime.fromtimestamp(now,ZONE).date();day=date.isoformat()
  c.execute('CREATE TABLE IF NOT EXISTS activity_smogo_visits(day TEXT PRIMARY KEY,windows TEXT NOT NULL)')
  record=c.execute('SELECT windows FROM activity_smogo_visits WHERE day=?',(day,)).fetchone()
  if not record:
   start=datetime.combine(date,datetime.min.time(),ZONE).timestamp()
   end=datetime.combine(date+timedelta(days=1),datetime.min.time(),ZONE).timestamp()
   span=(end-start)/3;windows=[]
   for i in range(3):
    opening=start+i*span+secrets.randbelow(max(1,int(span-3600)))
    windows.append([opening,opening+3600])
   c.execute('INSERT OR IGNORE INTO activity_smogo_visits VALUES(?,?)',(day,json.dumps(windows)))
   record=c.execute('SELECT windows FROM activity_smogo_visits WHERE day=?',(day,)).fetchone()
  windows=json.loads(record[0]);closing=next((b for a,b in windows if a<=now<b),None)
  return dict(available=closing is not None,available_until=closing)
 def row(self,c,uid):
  c.execute('INSERT OR IGNORE INTO activity_smogo(user_id) VALUES(?)',(uid,))
  return c.execute('SELECT * FROM activity_smogo WHERE user_id=?',(uid,)).fetchone()
 def consumed(self,r,p):
  # Preserve legacy participation even when its old daily counter has reset.
  return bool(r["attempts"] or p.get("round") or p.get("seen"))
 def snapshot(self,uid):
  with self.a.conn() as c:
   r=self.row(c,uid);p=json.loads(r['payload']);round=p.get('round');public=None
   if round:
    expired=round['status']=='active' and time.time()>=round['expires_at']
    public={k:round[k] for k in ('id','question','wager','started_at','expires_at')}
    public['status']='finished' if expired else round['status']
    if public['status']=='finished':
     public.update(won=False if expired else round['won'],payout=0 if expired else round['payout'],net_gold=-round['wager'] if expired else round['payout']-round['wager'],reason='timeout' if expired else round['reason'],solution=round['answers'][0],explanation=round['explanation'],submitted=round.get('submitted',''))
   consumed=self.consumed(r,p);completed=consumed and (not public or public['status']=='finished')
   presence=self.presence(c) if not completed else dict(available=False,available_until=None)
   return dict(revision=r['revision'],remaining=0 if consumed else 1,completed=completed,min_wager=MIN_WAGER,max_wager=MAX_WAGER,limit=1,duration=DURATION,reset_at=None,round=public,**presence)
 def question(self,c,seen):
  def signature(text):return hashlib.sha256(normalise(text).encode()).hexdigest()
  reserved={r[0] for r in c.execute('SELECT signature FROM activity_smogo_questions WHERE signature IN ('+','.join('?' for _ in RIDDLES)+')',tuple(signature(q[1]) for q in RIDDLES))}
  static=[q for q in RIDDLES if signature(q[1]) not in reserved and q[0] not in seen[-12:]]
  families=[k for k in ('cargo','coins','bridge','torches','market','runes') if k not in seen[-2:]]
  for _ in range(128):
   q=secrets.choice(static+[(k,None,None,None) for k in families])
   if q[1] is None:
    a=secrets.randbelow(48)+3;b=secrets.randbelow(18)+2;d=secrets.randbelow(a)+1
    if q[0]=='cargo':
     answer=a*b-d;q=('cargo',f'{a} caisses contiennent chacune {b} lingots. Le capitaine retire {d} lingots du chargement entier. Combien restent ? Répondez en chiffres.',(str(answer),),f'{a} × {b} − {d} = {answer}.')
    elif q[0]=='coins':
     answer=(a-1)*b+d;q=('coins',f'Je possède {a} bourses de {b} pièces. Je donne une bourse au passeur, puis il me rend {d} pièces de monnaie. Combien de pièces me restent en tout ? Répondez en chiffres.',(str(answer),),f'({a} − 1) × {b} + {d} = {answer}.')
    elif q[0]=='bridge':
     answer=a+b-d;q=('bridge',f'Un messager avance de {a} dalles sur un pont, recule de {d} dalles puis avance encore de {b} dalles. À quelle distance de son départ se trouve-t-il, en dalles ? Répondez en chiffres.',(str(answer),),f'{a} − {d} + {b} = {answer}.')
    elif q[0]=='torches':
     answer=a+b-d;q=('torches',f'Une salle contient {a} torches allumées. Le gardien en ajoute et allume {b}, puis le vent en éteint {d}. Combien brûlent encore ? Répondez en chiffres.',(str(answer),),f'{a} + {b} − {d} = {answer}.')
    elif q[0]=='market':
     answer=a*b+d;q=('market',f'Un marchand vend {a} sacs pour {b} Gold chacun. Il demande en plus {d} Gold de livraison pour la commande entière. Quel est le prix total ? Répondez en chiffres.',(str(answer),),f'{a} × {b} + {d} = {answer}.')
    else:
     answer=a*b+d;q=('runes',f'Un coffre porte ce code : multiplie {a} par {b}, puis ajoute {d}. Quel nombre ouvre le coffre ? Répondez en chiffres.',(str(answer),),f'{a} × {b} + {d} = {answer}.')
   if c.execute('INSERT OR IGNORE INTO activity_smogo_questions VALUES(?)',(signature(q[1]),)).rowcount:return q
  raise ValueError('Smogo prépare une nouvelle énigme. Réessayez sans changer votre mise.')
 def action(self,uid,body):
  with self.a.conn() as c:
   r=self.row(c,uid)
   if type(body.get('revision')) is not int or body['revision']!=r['revision']:raise ValueError('Votre énigme a changé. Actualisez Smogo.')
   p=json.loads(r['payload']);round=p.get('round');now=time.time();day=today();attempts=r['attempts'] if r['day']==day else 0;action=body['action']
   if action=='smogo_start':
    if round and round['status']=='active' and now<round['expires_at']:raise ValueError('Répondez à votre énigme en cours ou abandonnez-la.')
    if self.consumed(r,p):raise ValueError('Vous avez déjà participé à l’énigme unique de Smogo.')
    if not self.presence(c)['available']:raise ValueError('Smogo reste introuvable. Revenez explorer la ruelle plus tard.')
    wager=body.get('wager')
    if type(wager) is not int or not MIN_WAGER<=wager<=MAX_WAGER:raise ValueError('La mise doit être un entier de 1 à 500 Gold.')
    if not c.execute('UPDATE players SET wallet_gold=wallet_gold-? WHERE user_id=? AND wallet_gold>=?',(wager,uid,wager)).rowcount:raise ValueError('Votre portefeuille ne contient pas assez de Gold.')
    key,question,answers,explanation=self.question(c,p.get('seen',[]));p['seen']=(p.get('seen',[])+[key])[-20:]
    p['round']=dict(id=secrets.token_hex(16),status='active',question=question,answers=list(answers),explanation=explanation,wager=wager,started_at=now,expires_at=now+DURATION)
    attempts+=1;message='Smogo : « Ta mise est engagée. Deux minutes, une seule réponse… »'
   elif action in ('smogo_answer','smogo_giveup','smogo_timeout'):
    if not round or body.get('key')!=round['id'] or round['status']!='active':raise ValueError('Cette énigme est déjà réglée ou ne vous appartient pas.')
    expired=now>=round['expires_at'];answer=''
    if action=='smogo_timeout' and not expired:raise ValueError('Votre temps de réflexion n’est pas écoulé.')
    if action=='smogo_answer' and not expired:
     answer=body.get('answer')
     if not isinstance(answer,str) or not 1<=len(answer)<=160 or not normalise(answer):raise ValueError('Indiquez une réponse de 1 à 160 caractères.')
    won=not expired and action=='smogo_answer' and any((bool(re.fullmatch(r'\d+',answer.strip())) and int(answer.strip())==int(a)) if a.isdigit() else normalise(answer)==normalise(a) for a in round['answers'])
    payout=2*round['wager'] if won else 0
    if payout:c.execute('UPDATE players SET wallet_gold=wallet_gold+? WHERE user_id=?',(payout,uid))
    reason='correct' if won else 'timeout' if expired else 'abandon' if action=='smogo_giveup' else 'wrong'
    round.update(status='finished',won=won,payout=payout,reason=reason,submitted=answer)
    message=f'Bonne réponse ! {payout} Gold versés : votre mise rendue et {round["wager"]} Gold de bénéfice.' if won else f'Réponse incorrecte. Vous perdez votre mise de {round["wager"]} Gold.' if reason=='wrong' else f'Temps écoulé. Votre mise de {round["wager"]} Gold est perdue.' if expired else f'Vous abandonnez : mise de {round["wager"]} Gold perdue.'
   else:raise ValueError('Action de Smogo inconnue.')
   c.execute('UPDATE activity_smogo SET revision=revision+1,day=?,attempts=?,payload=? WHERE user_id=?',(day,attempts,json.dumps(p,ensure_ascii=False),uid))
   return message
