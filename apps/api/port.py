"""Port des Brumes. Campaign-gated investigation with private atomic progress.

No additional currency, attempts or techniques are awarded here: the campaign
receipt remains the only reward for the associated main quest.
"""
import copy,json,time
from dataclasses import asdict
from arena_engine import Fighter,BattleState,resolve_action,bot_choose_action
from arena_techniques import ArenaFighter,book,resolve
from progression import level_from_xp

QUEST_ID='S1-Q08'
SCENES={'port':'Port des Brumes','capitainerie':'La capitainerie','entrepots':'Les entrepôts','passeur':'Le passeur','quai':'Le quai abandonné','popie':'Popie · la contrebandière'}
CLUES={
 'crate':dict(scene='entrepots',title='Caisse au sceau réutilisé',text='La corde a été renouée au-dessus de l’ancienne empreinte. Le chargement a été ouvert après son arrivée au port.'),
 'register':dict(scene='entrepots',title='Deux sorties pour une même caisse',text='Le registre porte deux sorties du même lot : une vers Legacy et une vers la Lisière des Chênes. Le second reçu a été présenté après la fermeture des portes.'),
 'seal':dict(scene='entrepots',title='Sceau de remplacement',text='Le sceau cassé ne correspond pas au cachet officiel du port. Son motif reprend la marque trouvée sur les caisses d’Elarwyn.'),
 'quay_crate':dict(scene='quai',title='Lot de Legacy dissimulé',text='Sous une toile détrempée, vous retrouvez le numéro du lot destiné à Legacy. La cargaison n’a jamais quitté le port par la route officielle.'),
 'pouch':dict(scene='quai',title='Ordre de livraison falsifié',text='La sacoche contient la copie du second reçu et un rendez-vous à la Lisière des Chênes. Un intermédiaire doit y détourner les convoyeurs.'),
 'boat':dict(scene='quai',title='Une embarcation qui revient à vide',text='La cale porte des traces fraîches des mêmes caisses. Le navire annoncé disparu a bien accosté ; une petite embarcation a déplacé son chargement de nuit.'),
}
WAREHOUSE={'crate','register','seal'}
QUAY={'quay_crate','pouch','boat'}
GOALS=['Présenter le mandat à la capitainerie','Examiner les trois indices des entrepôts','Interroger le passeur sur le transfert nocturne','Examiner les trois indices du quai abandonné','Choisir comment intervenir','Arrêter les détourneurs de cargaisons','Remettre le dossier à Panda','Enquête terminée : poursuivre la quête principale']

def port_quest(q):
 """Edition 4 only; don't mutate catalogs or accepted earlier editions."""
 if q['id']!=QUEST_ID:return q
 q=copy.deepcopy(q)
 q['locations']='Elarwyn → Port des Brumes → Château'
 q['scene']+=' Le double reçu porte aussi le cachet du Port des Brumes : la capitainerie doit en vérifier l’origine.'
 q['steps'].insert(1,dict(id='S1-Q08-PORT',kind='port',label='Résoudre l’enquête de la cargaison au Port des Brumes',place='Port des Brumes',scene_image='../port/port.png',text='Présentez le mandat à la capitainerie, réunissez les preuves et revenez avec le dossier.'))
 return q

class Port:
 def __init__(self,a):
  self.a=a
  from popie import Popie
  self.popie=Popie(a)
  with a.conn() as c:c.execute('CREATE TABLE IF NOT EXISTS activity_port(user_id INTEGER PRIMARY KEY,revision INTEGER NOT NULL DEFAULT 0,unlocked_at REAL NOT NULL,payload TEXT NOT NULL DEFAULT "{}")')
 def eligible(self,c,uid):
  from campaign import QUESTS,effective_quest
  row=c.execute('SELECT * FROM campaign_progress WHERE user_id=?',(uid,)).fetchone()
  if not row:return False
  idx=next(i for i,q in enumerate(QUESTS) if q['id']==QUEST_ID)
  if row['quest_index']>idx or c.execute('SELECT 1 FROM campaign_receipts WHERE user_id=? AND quest_id=?',(uid,QUEST_ID)).fetchone():return True
  if row['quest_index']!=idx or row['accepted_at'] is None:return False
  q=effective_quest(row,json.loads(row['payload']))
  level=level_from_xp(c.execute('SELECT xp FROM castle_profiles WHERE user_id=?',(uid,)).fetchone()[0])[0]
  # Reach the actual port objective. Older accepted editions can investigate
  # once their first receipt-verification objective has been completed.
  return level>=q['min_level'] and row['stage']>=1
 def row(self,c,uid):
  row=c.execute('SELECT * FROM activity_port WHERE user_id=?',(uid,)).fetchone()
  if not row and self.eligible(c,uid):
   c.execute('INSERT INTO activity_port(user_id,unlocked_at) VALUES(?,?)',(uid,time.time()));row=c.execute('SELECT * FROM activity_port WHERE user_id=?',(uid,)).fetchone()
  return row
 def active_in(self,c,uid):
  row=c.execute('SELECT payload FROM activity_port WHERE user_id=?',(uid,)).fetchone();b=json.loads(row[0]).get('battle') if row else None
  return bool(b and not b['finished'])
 def active(self,uid):
  with self.a.conn() as c:return self.active_in(c,uid)
 def complete_in(self,c,uid):
  row=c.execute('SELECT payload FROM activity_port WHERE user_id=?',(uid,)).fetchone()
  return bool(row and json.loads(row[0]).get('phase',0)>=7)
 def snapshot(self,uid):
  with self.a.conn() as c:
   row=self.row(c,uid)
   if not row:return dict(unlocked=False,reason='Poursuivez l’histoire principale : une piste doit vous conduire au Port des Brumes.',quest_id=QUEST_ID)
   p=json.loads(row['payload']);phase=p.get('phase',0);found=p.get('clues',[]);battle=p.get('battle');public=None
   if battle:public=dict(fighters=[dict(name=f['name'],hp=f['hp'],max_hp=f['max_hp']) for f in battle['fighters']],turn=battle['turn_no'],finished=battle['finished'],won=battle['winner_index']==0 if battle['finished'] else None,ultimate_cd=battle['fighters'][0]['ultimate_cd'],logs=battle['log'][-12:],skills=p.get('skills',{}))
   actions=[]
   for key,data in CLUES.items():
    if data['scene']=='entrepots' and phase>=1 or data['scene']=='quai' and phase>=3:actions.append(dict(key=key,title=data['title'],scene=data['scene'],found=key in found))
   choices=[dict(key='discreet',title='Suivre les détourneurs',description='Intervenir seul sur le quai et identifier leur liaison avec l’intermédiaire d’Elarwyn.'),dict(key='guards',title='Prévenir la capitainerie',description='Faire intervenir les gardes dans les entrepôts. Leur appui retire 10 % des PV initiaux de l’adversaire.')]
   scene=p.get('scene','port');where='entrepots' if p.get('choice')=='guards' else 'quai'
   return dict(unlocked=True,popie=self.popie.snapshot_in(c,uid),unlocked_at=row['unlocked_at'],revision=row['revision'],phase=phase,complete=phase>=7,scene=scene,goal=GOALS[phase],choice=p.get('choice',''),choices=choices,clues=[dict(key=k,**CLUES[k]) for k in found if k in CLUES],inspect=actions,scenes=[dict(key=k,name=v,available=k!='quai' or phase>=3) for k,v in SCENES.items()],battle=public,battle_scene=where,retry_at=p.get('retry_at',0),can_resume_campaign=phase>=7,dialogue=p.get('dialogue','Le mandat du château vous conduit à Panda, le maître du port.').replace('Maître du port :','Panda :').replace('vous conduit au maître du port.','vous conduit à Panda, le maître du port.'),quest_id=QUEST_ID,reward_note='Enquête comprise dans la récompense de la quête principale. Aucun paiement supplémentaire au port.')
 def action(self,uid,body):
  action=body['action'];key=body.get('key','')
  with self.a.conn() as c:
   row=self.row(c,uid)
   if not row:raise ValueError('Le Port des Brumes est verrouillé par l’histoire principale.')
   if type(body.get('revision')) is not int or body['revision']!=row['revision']:raise ValueError('Votre enquête a changé. Actualisez le port avant de réessayer.')
   p=json.loads(row['payload']);phase=p.get('phase',0);scene=p.get('scene','port');found=set(p.get('clues',[]));message=''
   if action.startswith('port_popie_'):
    if scene!='popie':raise ValueError('Rejoignez le comptoir de Popie dans les entrepôts.')
    if self.active_in(c,uid):raise ValueError('Terminez le combat du port avant de commercer.')
    message=self.popie.action_in(c,uid,body)
   elif action=='port_enter':
    if self.active_in(c,uid) and key!=('entrepots' if p.get('choice')=='guards' else 'quai'):raise ValueError('Terminez ou abandonnez ce combat avant de quitter le lieu de l’intervention.')
    if key not in SCENES or key=='quai' and phase<3:raise ValueError('Cette partie du port est encore inaccessible.')
    p['scene']=key;message='Vous entrez : '+SCENES[key]+'.'
   elif self.active_in(c,uid) and action!='port_battle':raise ValueError('Terminez ou abandonnez le combat du port avant de poursuivre l’enquête.')
   elif action=='port_talk':
    expected={'captain':'capitainerie','foreman':'entrepots','ferryman':'passeur'}
    if expected.get(key)!=scene:raise ValueError('Rejoignez le personnage avant de lui parler.')
    if key=='captain':
     if phase==0:p['phase']=1;message='Panda : « Le navire a accosté. Pourtant, Legacy attend toujours sa cargaison. Vérifiez les caisses, le registre et les cachets dans nos entrepôts. »'
     elif phase==6:
      p['phase']=7;p['completed_at']=time.time();message='Panda : « Le second reçu était faux. L’ordre trouvé sur le quai désigne la Lisière des Chênes : prévenez les convoyeurs. Votre dossier est authentifié. »'
     elif phase>=7:message='Panda : « Votre dossier est conservé. Le port vous reste ouvert ; les autorisations de traversée viendront avec la suite de votre histoire. »'
     else:message='Panda : « Revenez avec les indices du détournement. Le passeur connaît les mouvements du quai. »'
    elif key=='foreman':message='Contremaître : « On m’a montré un reçu en règle. Mais j’ai trouvé deux sorties pour le même lot. Examinez vous-même le registre, cette caisse et le sceau cassé. »'
    elif phase==2:
     p['phase']=3;message='Passeur : « J’ai vu des caisses passer dans une barque après la fermeture des entrepôts. Elle accostait au vieux quai. Faites attention : ceux qui l’utilisent ne veulent aucun témoin. »'
    elif phase<2:message='Passeur : « Apportez-moi les références du lot et la preuve du transfert. Je pourrai vous dire quelle embarcation chercher. »'
    else:message='Passeur : « La barque du vieux quai transportait les caisses. Mes traversées vers les îles restent fermées en attendant les autorisations de navigation. »'
    p['dialogue']=message
   elif action=='port_inspect':
    clue=CLUES.get(key)
    if not clue or clue['scene']!=scene or scene=='entrepots' and phase!=1 or scene=='quai' and phase!=3:raise ValueError('Cet indice ne correspond pas à votre objectif actuel.')
    if key in found:raise ValueError('Cet indice est déjà consigné.')
    found.add(key);p['clues']=sorted(found);message=clue['text'];p['dialogue']=message
    if phase==1 and WAREHOUSE<=found:p['phase']=2
    if phase==3 and QUAY<=found:p['phase']=4
   elif action=='port_choose':
    if phase!=4 or scene!='quai' or key not in ('discreet','guards'):raise ValueError('Réunissez les preuves du quai avant de décider de l’intervention.')
    p['choice']=key;p['phase']=5;p['scene']='entrepots' if key=='guards' else 'quai';message='Les gardes vous rejoignent dans les entrepôts.' if key=='guards' else 'Vous attendez les détourneurs sur le quai abandonné.';p['dialogue']=message
   elif action=='port_battle':
    if phase!=5 or scene!=('entrepots' if p.get('choice')=='guards' else 'quai'):raise ValueError('Aucun affrontement n’est prévu ici pour le moment.')
    if time.time()<p.get('retry_at',0):raise ValueError('Le groupe se disperse. Nouvelle tentative dans une minute.')
    if key=='start':
     if self.active_in(c,uid):raise ValueError('Un combat du port est déjà en cours.')
     if self.a.khaz.active(c,uid):raise ValueError('Terminez votre autre combat ou partie avant d’intervenir au port.')
     level=level_from_xp(c.execute('SELECT xp FROM castle_profiles WHERE user_id=?',(uid,)).fetchone()[0])[0]
     name=(self.a.discord_profile(uid) or {}).get('display_name','Aventurier');skills=book(c,uid,level,0)['skills']
     player=ArenaFighter(uid,name,'arena_fighter',max_hp=100+10*(level-1),player_level=level,**self.a.khaz.bonuses_in(c,uid));player.loadout=skills
     enemy=Fighter(None,'Détourneur de cargaisons','traqueur',max_hp=125,equipment_atk_pct=18)
     if p.get('choice')=='guards':enemy.hp=round(enemy.max_hp*.9)
     battle=BattleState('port:'+str(uid),'port',0,[player,enemy],0);battle.log.append('Les gardes couvrent votre intervention : adversaire à 90 % de ses PV.' if p.get('choice')=='guards' else 'Vous bloquez la fuite du détourneur sur le quai.');p['battle']=asdict(battle);p['skills']=skills;message='Le combat commence. Aucune mise, aucune technique à dérober.'
    else:
     raw=p.get('battle')
     if not raw or raw['finished']:raise ValueError('Lancez le combat avant de choisir une technique.')
     fighters=[]
     for i,f in enumerate(raw['fighters']):
      obj=(ArenaFighter if i==0 else Fighter)(**f);obj.hp=f['hp'];obj.max_hp=f['max_hp'];fighters.append(obj)
     fighters[0].loadout=p['skills'];battle=BattleState(**{**raw,'fighters':fighters})
     if key=='abandon':battle.finished=True;battle.winner_index=1;battle.log.append('Vous vous repliez sans perdre vos indices.')
     elif key not in ('light','heavy','ultimate','defend'):raise ValueError('Technique inconnue.')
     else:
      if key=='ultimate' and fighters[0].ultimate_cd:raise ValueError('Technique encore en recharge.')
      battle.log.extend(resolve(battle,key,resolve_action))
      if not battle.finished:battle.switch();battle.log.extend(resolve_action(battle,bot_choose_action(battle.actor(),battle.target())))
      if not battle.finished:battle.switch()
     if battle.turn_no>=100 and not battle.finished:battle.finished=True;battle.winner_index=1;battle.log.append('Les détourneurs se replient. Votre dossier reste intact.')
     p['battle']=asdict(battle)
     if battle.finished:
      if battle.winner_index==0:p['phase']=6;message='Victoire ! Le chargement est sécurisé. Retournez à la capitainerie faire authentifier le dossier.'
      else:p['retry_at']=time.time()+60;message='Vous vous repliez. Aucun indice ni Gold perdu. Nouvelle tentative dans une minute.'
     else:message='Tour résolu.'
   else:raise ValueError('Action du port inconnue.')
   c.execute('UPDATE activity_port SET revision=revision+1,payload=? WHERE user_id=?',(json.dumps(p,ensure_ascii=False),uid));return message
