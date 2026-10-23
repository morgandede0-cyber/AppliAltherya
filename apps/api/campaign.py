"""Transactional main campaign: server-owned steps, clocks, battles and receipts."""
import json,time,secrets
from pathlib import Path
from dataclasses import asdict
from progression import level_from_xp
from campaign_story import enrich,consequences,playable_branch
from campaign_world import decorate,target,SCENES,PARENTS,PROPS,maintenance_scene
from arena_engine import Fighter,BattleState,resolve_action,bot_choose_action
from arena_techniques import ArenaFighter,book,resolve as technique_action
from campaign_rewards import quote as reward_quote,VERSION as REWARD_VERSION
CATALOG=json.loads(Path(__file__).with_name('campaign_catalog.json').read_text(encoding='utf8'))
QUESTS=CATALOG['quests']
LEGACY_QUESTS=json.loads(Path(__file__).with_name('campaign_catalog_v1.json').read_text(encoding='utf8'))['quests']
def effective_quest(row,payload):
 # Already accepted missions keep their original steps and level gate until claimed.
 q=(LEGACY_QUESTS if row['accepted_at'] is not None and payload.get('edition',1)<2 else QUESTS)[row['quest_index']]
 q=playable_branch(q,payload.get('choices',{})) if row['accepted_at'] is None or payload.get('edition',1)>=3 else q
 if row['accepted_at'] is None or payload.get('edition',1)>=4:
  from port import port_quest
  q=port_quest(q)
 if row['accepted_at'] is None:q={**q,**reward_quote(q)}
 elif payload.get('reward_quote'):q={**q,**payload['reward_quote']}
 return decorate(q,row['accepted_at'] is None or payload.get('edition',1)>=6)

class Campaign:
 def __init__(self,a):
  self.a=a
  with a.conn() as c:
   c.execute('CREATE TABLE IF NOT EXISTS campaign_progress(user_id INTEGER PRIMARY KEY,quest_index INTEGER NOT NULL DEFAULT 0,stage INTEGER NOT NULL DEFAULT 0,accepted_at REAL,entered_at REAL NOT NULL DEFAULT 0,revision INTEGER NOT NULL DEFAULT 0,payload TEXT NOT NULL DEFAULT "{}")')
   c.execute('CREATE TABLE IF NOT EXISTS campaign_receipts(user_id INTEGER NOT NULL,quest_id TEXT NOT NULL,gold INTEGER NOT NULL,xp INTEGER NOT NULL,completed_at REAL NOT NULL,PRIMARY KEY(user_id,quest_id))')
   c.execute('CREATE TABLE IF NOT EXISTS campaign_evidence(user_id INTEGER NOT NULL,quest_id TEXT NOT NULL,step_id TEXT NOT NULL,clue_id TEXT NOT NULL,place_id TEXT NOT NULL,title TEXT NOT NULL,text TEXT NOT NULL,found_at REAL NOT NULL,PRIMARY KEY(user_id,quest_id,step_id,clue_id))')
   c.execute('CREATE TABLE IF NOT EXISTS campaign_visits(user_id INTEGER NOT NULL,place_id TEXT NOT NULL,entered_at REAL NOT NULL,PRIMARY KEY(user_id,place_id))')
   c.execute('CREATE TABLE IF NOT EXISTS campaign_world(user_id INTEGER PRIMARY KEY,scene TEXT NOT NULL,token TEXT NOT NULL,entered_at REAL NOT NULL)')
   c.execute('CREATE TABLE IF NOT EXISTS campaign_items(user_id INTEGER NOT NULL,item_id TEXT NOT NULL,name TEXT NOT NULL,source TEXT NOT NULL,obtained_at REAL NOT NULL,delivered_at REAL,PRIMARY KEY(user_id,item_id))')
 def world_snapshot(self,c,uid,q,row):
  location=c.execute('SELECT scene,token FROM campaign_world WHERE user_id=?',(uid,)).fetchone()
  items=[dict(r) for r in c.execute('SELECT item_id,name,source,delivered_at FROM campaign_items WHERE user_id=? ORDER BY obtained_at',(uid,))]
  scene=target(q,row)
  return dict(scene=location['scene'] if location else None,token=location['token'] if location else None,target=scene,target_name=SCENES[scene][0],items=items)
 def world_enter(self,uid,body):
  scene=body.get('scene')
  if not isinstance(scene,str) or scene not in SCENES:raise ValueError('Destination inconnue.')
  with self.a.conn() as c:
   c.execute('BEGIN IMMEDIATE');row=self.row(c,uid);payload=json.loads(row['payload'])
   level=level_from_xp(c.execute('SELECT xp FROM castle_profiles WHERE user_id=?',(uid,)).fetchone()[0])[0]
   if level<SCENES[scene][1]:raise ValueError(f'Niveau {SCENES[scene][1]} requis pour ce lieu.')
   if scene in PARENTS:
    active=None
    if row['quest_index']<len(QUESTS) and row['accepted_at'] is not None:
     q=effective_quest(row,payload)
     if row['stage']<len(q['steps']):active=q['steps'][row['stage']].get('place_id')
    place=next(p for p in self.journal(c,uid,level,active)['locations'] if p['id']==scene)
    if not place['can_enter']:raise ValueError('Une quête doit vous ouvrir ce lieu avant d’y entrer.')
    c.execute('INSERT OR IGNORE INTO campaign_visits VALUES(?,?,?)',(uid,scene,time.time()))
   if scene=='port' and not self.a.port.eligible(c,uid):raise ValueError('Le Port des Brumes n’est pas encore ouvert.')
   c.execute('INSERT INTO campaign_world VALUES(?,?,?,?) ON CONFLICT(user_id) DO UPDATE SET scene=excluded.scene,token=excluded.token,entered_at=excluded.entered_at',(uid,scene,secrets.token_urlsafe(24),time.time()))
  return 'Vous rejoignez : '+SCENES[scene][0]+'.'
 def require_world(self,c,uid,body,scene):
  row=c.execute('SELECT scene,token FROM campaign_world WHERE user_id=?',(uid,)).fetchone()
  if not row or row['scene']!=scene or not isinstance(body.get('world_token'),str) or not secrets.compare_digest(row['token'].encode(),body['world_token'].encode()):raise ValueError('Rejoignez le lieu de l’objectif et interagissez sur place.')
 def collect(self,c,uid,source,now):
  if source in PROPS:
   item,name,_=PROPS[source]
   c.execute('INSERT OR IGNORE INTO campaign_items VALUES(?,?,?,?,?,NULL)',(uid,item,name,source,now))
 def journal(self,c,uid,level,active_place=None):
  evidence=[dict(r) for r in c.execute('SELECT quest_id,step_id,clue_id,place_id,title,text FROM campaign_evidence WHERE user_id=? ORDER BY found_at,quest_id,clue_id',(uid,))]
  visited={r[0] for r in c.execute('SELECT place_id FROM campaign_visits WHERE user_id=?',(uid,))}
  discovered={e['place_id'] for e in evidence}|visited
  completed={r[0] for r in c.execute('SELECT quest_id FROM campaign_receipts WHERE user_id=?',(uid,))}
  locations=[]
  for place in CATALOG.get('locations',[]):
   first=next(q['id'] for q in QUESTS if any(s.get('place_id')==place['id'] for s in q['steps']))
   story_allowed=place['id']==active_place or place['id'] in discovered or first in completed
   locations.append({**place,'level_allowed':level>=place['min_level'],'story_allowed':story_allowed,'can_enter':level>=place['min_level'] and story_allowed,'visited':place['id'] in visited,'discovered':place['id'] in discovered,'active':place['id']==active_place})
  return dict(locations=locations,evidence=evidence)
 def row(self,c,uid):
  c.execute('INSERT OR IGNORE INTO campaign_progress(user_id) VALUES(?)',(uid,));return dict(c.execute('SELECT * FROM campaign_progress WHERE user_id=?',(uid,)).fetchone())
 def _expedition_done(self,c,uid,step,since,prior=None):
  rows=c.execute('SELECT run_id,loot_json FROM expedition_runs WHERE user_id=? AND expedition_key=? AND claimed=1 AND NOT EXISTS (SELECT 1 FROM activity_admin_cancelled_expeditions x WHERE x.run_id=expedition_runs.run_id) AND started_at>=?',(uid,step['destination'],int(since) if prior is not None else since)).fetchall()
  return any(r['run_id'] not in (prior or []) and sum(json.loads(r['loot_json']).values())>0 for r in rows)
 def expedition_boundary(self,c,uid,q,stage,payload,entered):
  if stage<len(q['steps']) and q['steps'][stage]['kind']=='expedition':
   payload['expedition_prior']=[r[0] for r in c.execute('SELECT run_id FROM expedition_runs WHERE user_id=? AND expedition_key=? AND started_at>=?',(uid,q['steps'][stage]['destination'],int(entered)))]

 def snapshot(self,uid):
  with self.a.conn() as c:
   row=self.row(c,uid);idx=row['quest_index'];payload=json.loads(row['payload']);done=c.execute('SELECT COUNT(*) FROM campaign_receipts WHERE user_id=?',(uid,)).fetchone()[0]
   level=level_from_xp(c.execute('SELECT xp FROM castle_profiles WHERE user_id=?',(uid,)).fetchone()[0])[0]
   if idx>=len(QUESTS):return dict(world=self.world_snapshot(c,uid,{'giver_scene':'troubadour','steps':[]},row),**self.journal(c,uid,level),decision_history=consequences(payload.get('choices',{}),QUESTS),complete=True,title=CATALOG['title'],completed=done,total=len(QUESTS),choices=payload.get('choices',{}),revision=row['revision'])
   q=enrich(dict(effective_quest(row,payload)),payload.get('choices',{}),QUESTS);stage=row['stage'];step=q['steps'][stage] if stage<len(q['steps']) else None
   if q['id']=='S4-Q08':
    outcome=payload.get('choices',{}).get('S4-Q07','')
    q['resolution']+=' Le Faussaire sera jugé.' if outcome.startswith('Secourir') else ' Le Faussaire a disparu ; les relevés sont préservés.'
   public_steps=[{**{k:v for k,v in s.items() if k not in ('answer','clues','work_points')},**({'clues':[{k:v for k,v in clue.items() if k!='text'} for clue in s['clues']]} if 'clues' in s else {}),**({'work_points':[{k:v for k,v in point.items() if k!='text'} for point in s['work_points']]} if 'work_points' in s else {})} for s in q['steps']]
   exp_ready=bool(step and step['kind']=='expedition' and row['accepted_at'] is not None and self._expedition_done(c,uid,step,row['entered_at'],payload.get('expedition_prior')))
   level=level_from_xp(c.execute('SELECT xp FROM castle_profiles WHERE user_id=?',(uid,)).fetchone()[0])[0]
   battle=payload.get('battle');public_battle=None
   if battle:public_battle={'skills':payload.get('skills'), 'fighters':[{'name':f['name'],'hp':f['hp'],'max_hp':f['max_hp']} for f in battle['fighters']],'log':battle['log'][-10:],'finished':battle['finished'],'won':battle['winner_index']==0 if battle['finished'] else None,'turn':battle['turn_no'],'ultimate_cd':battle['fighters'][0]['ultimate_cd']}
   return dict(world=self.world_snapshot(c,uid,q,row),**self.journal(c,uid,level,step.get('place_id') if step and row['accepted_at'] is not None else None),edition=payload.get('edition',1) if row['accepted_at'] is not None else 6,work=payload.get('work',[]),complete=False,title=CATALOG['title'],completed=done,total=len(QUESTS),revision=row['revision'],quest={**{k:v for k,v in q.items() if k!='steps'},'steps':public_steps},stage=stage,accepted=row['accepted_at'] is not None,level_allowed=level>=q['min_level'],deadline=payload.get('deadline',0),retry_at=payload.get('retry_at',0),claim_at=(row['accepted_at'] or 0)+q['min_duration'],expedition_ready=exp_ready,battle=public_battle,choices=payload.get('choices',{}))
 def action(self,uid,body):
  if body['action']=='campaign_world_enter':return self.world_enter(uid,body)
  if body['action']=='campaign_enter':return self.world_enter(uid,{**body,'scene':body.get('place_id')})
  now=time.time()
  with self.a.conn() as c:
   c.execute('BEGIN IMMEDIATE');row=self.row(c,uid);idx=row['quest_index']
   if idx>=len(QUESTS):raise ValueError('La campagne est terminée.')
   payload=json.loads(row['payload']);q=effective_quest(row,payload);stage=row['stage'];accepted=row['accepted_at'];entered=row['entered_at'];action=body['action']
   if type(body.get('revision')) is not int or body['revision']!=row['revision'] or body.get('quest_id')!=q['id']:raise ValueError('La quête a changé. Actualisez le journal avant de réessayer.')
   self.require_world(c,uid,body,target(q,row))
   if action=='campaign_accept':
    if accepted is not None:raise ValueError('Cette quête est déjà acceptée.')
    level=level_from_xp(c.execute('SELECT xp FROM castle_profiles WHERE user_id=?',(uid,)).fetchone()[0])[0]
    if level<q['min_level']:raise ValueError(f"Niveau {q['min_level']} requis pour cette quête.")
    payload['edition']=6;payload['reward_quote']={k:q[k] for k in ('gold','xp')};payload['reward_version']=REWARD_VERSION;accepted=now;entered=now;message='Quête acceptée. Les objectifs se réalisent dans l’ordre.'
   elif action=='campaign_claim':
    if accepted is None or stage!=len(q['steps']):raise ValueError('Terminez tous les objectifs avant de remettre la quête.')
    if now<accepted+q['min_duration']:raise ValueError('La mission est encore en cours. Consultez le délai du journal.')
    if c.execute('SELECT 1 FROM campaign_receipts WHERE user_id=? AND quest_id=?',(uid,q['id'])).fetchone():
     if not payload.get('admin_replay'):raise ValueError('Récompense déjà récupérée.')
     c.execute('UPDATE campaign_progress SET quest_index=quest_index+1,stage=0,accepted_at=NULL,entered_at=?,revision=revision+1,payload=? WHERE user_id=?',(now,json.dumps({'choices':payload.get('choices',{}),'admin_replay':True}),uid))
     return 'Quête rejouée : récompense déjà versée, progression restaurée sans nouveau paiement.'
    c.execute('INSERT INTO campaign_receipts VALUES(?,?,?,?,?)',(uid,q['id'],q['gold'],q['xp'],now))
    c.execute('UPDATE players SET wallet_gold=wallet_gold+? WHERE user_id=?',(q['gold'],uid))
    before=c.execute('SELECT xp FROM castle_profiles WHERE user_id=?',(uid,)).fetchone()[0]
    c.execute('UPDATE castle_profiles SET xp=xp+?,quests_completed=quests_completed+1 WHERE user_id=?',(q['xp'],uid));self.a.castle._queue_levelups(c,uid,before,before+q['xp']);self.a.castle._sync_level(c,uid)
    idx+=1;stage=0;accepted=None;entered=now;payload={**{'choices':payload.get('choices',{})},**({'admin_replay':True} if payload.get('admin_replay') else {})};message=f"{q['resolution']} +{q['gold']} Gold et +{q['xp']} XP."
   else:
    if accepted is None or stage>=len(q['steps']):raise ValueError('Aucun objectif actif.')
    step=q['steps'][stage];kind=step['kind'];advance=False;message=''
    if now<payload.get('retry_at',0):raise ValueError('Préparez une nouvelle tentative avant de réessayer.')
    if action=='campaign_step':
     if kind=='talk':advance=True;message=step.get('text') or q['dialogue']
     elif kind=='collect':advance=True;message='Vous récupérez '+step['prop']['name']+'. L’objet rejoint votre sac de quête.'
     elif kind=='port':
      if not self.a.port.complete_in(c,uid):raise ValueError('Résolvez l’enquête du Port des Brumes et remettez le dossier à la capitainerie.')
      advance=True;message='Le dossier du port authentifie le second reçu. Rejoignez les convoyeurs à Elarwyn.'
     elif kind in ('inspect','mission'):
      if step.get('work_points') and any(point['id'] not in payload.get('work',[]) for point in step['work_points']):raise ValueError('Effectuez les actions dans le décor avant de remettre le rapport.')
      if not payload.get('deadline'):payload['deadline']=now+step['duration'];message='Mission lancée. Vous pouvez poursuivre vos autres activités pendant ce délai.'
      elif now<payload['deadline']:raise ValueError('La reconnaissance n’est pas terminée.')
      else:advance=True;message='Rapport de mission récupéré et conservé dans le journal.'
     elif kind in ('choice','puzzle'):
      option=body.get('option')
      if type(option) is not int or not 0<=option<len(step['options']):raise ValueError('Choisissez une réponse proposée.')
      if kind=='puzzle' and option!=step['answer']:
       payload['retry_at']=now+60;message='Cette conclusion ne correspond pas aux indices. Relisez le témoignage ; nouvelle tentative dans une minute.'
      else:
       if kind=='choice':
        if q['id']=='S1-Q04' and option==1:
         if not c.execute('UPDATE players SET wallet_gold=wallet_gold-25 WHERE user_id=? AND wallet_gold>=25',(uid,)).rowcount:raise ValueError('25 Gold requis, ou choisissez le service de renseignement.')
        payload.setdefault('choices',{})[q['id']]=step['options'][option]
       advance=True;message='Décision enregistrée.' if kind=='choice' else 'Les preuves confirment votre conclusion.'
     elif kind=='explore':
      count=c.execute('SELECT COUNT(*) FROM campaign_evidence WHERE user_id=? AND quest_id=? AND step_id=?',(uid,q['id'],step['id'])).fetchone()[0]
      if count<len(step['clues']):raise ValueError('Explorez tous les points du lieu et consignez leurs indices avant de poursuivre.')
      advance=True;message='Les indices sont conservés dans votre carnet. Vous pouvez poursuivre l’enquête.'
     elif kind=='deliver':
      result=c.execute('UPDATE resources SET quantity=quantity-? WHERE user_id=? AND resource_name=? AND quantity>=?',(step['quantity'],uid,step['resource'],step['quantity']))
      if not result.rowcount:raise ValueError(f"Réunissez {step['quantity']} {step['resource']} pour cette livraison.")
      advance=True;message='Le matériel est remis au destinataire.'
     elif kind=='expedition':
      if not self._expedition_done(c,uid,step,entered,payload.get('expedition_prior')):raise ValueError('Terminez l’expédition indiquée après le début de cet objectif, puis récupérez votre rapport.')
      advance=True;message='Votre rapport d’expédition est remis et ajouté au dossier.'
     else:raise ValueError('Cet objectif demande un combat.')
    elif action=='campaign_work':
     point=next((point for point in step.get('work_points',[]) if point['id']==body.get('point_id')),None)
     if not point:raise ValueError('Action de terrain inconnue pour cet objectif.')
     if point['id'] in payload.get('work',[]):raise ValueError('Cette action de terrain est déjà terminée.')
     payload.setdefault('work',[]).append(point['id']);payload.setdefault('deadline',now+step['duration']);message=point['text']
    elif action=='campaign_explore':
     if kind!='explore':raise ValueError('Ce lieu ne fait pas partie de votre objectif actif.')
     if not c.execute('SELECT 1 FROM campaign_visits WHERE user_id=? AND place_id=?',(uid,step['place_id'])).fetchone():raise ValueError('Entrez dans le lieu avant de chercher ses indices.')
     clue=next((x for x in step['clues'] if x['id']==body.get('clue_id')),None)
     if not clue:raise ValueError('Point d’enquête inconnu pour ce lieu.')
     if not c.execute('INSERT OR IGNORE INTO campaign_evidence VALUES(?,?,?,?,?,?,?,?)',(uid,q['id'],step['id'],clue['id'],step['place_id'],clue['label'],clue['text'],now)).rowcount:raise ValueError('Cet indice est déjà dans votre carnet.')
     self.collect(c,uid,clue['id'],now)
     message=clue['text']
    elif action=='campaign_battle':
     if kind!='battle':raise ValueError('Aucun combat prévu pour cet objectif.')
     key=body.get('key')
     if key=='start':
      if payload.get('battle') and not payload['battle']['finished']:raise ValueError('Un combat est déjà en cours.')
      level=level_from_xp(c.execute('SELECT xp FROM castle_profiles WHERE user_id=?',(uid,)).fetchone()[0])[0]
      name=c.execute('SELECT name FROM activity_sessions WHERE user_id=? LIMIT 1',(uid,)).fetchone()[0]
      saved_choices=payload.get('choices',{})
      rescue=saved_choices.get('S2-Q07')=='Secourir directement les convoyeurs' and q['id']=='S4-Q05'
      defense=saved_choices.get('S4-Q03')=='Préparer un barrage autorisé' and q['id']=='S4-Q05'
      enemy=Fighter(None,step['enemy'],'gardien' if step.get('boss') or defense else 'ravageur',max_hp=round((100+10*(q['min_level']-1))*(1.3 if step.get('boss') else 1.05)*(.9 if rescue else 1)),equipment_atk_pct=8+5*q['min_level'])
      player=ArenaFighter(uid,name,'arena_fighter',max_hp=100+10*(level-1),player_level=level,**self.a.khaz.bonuses_in(c,uid));payload['skills']=book(c,uid,level,0)['skills'];player.loadout=payload['skills']
      battle=BattleState(q['id']+':'+str(stage),'campaign',0,[player,enemy],0)
      payload['battle']=asdict(battle);message='L’adversaire se met en garde. À vous de jouer.'
     else:
      raw=payload.get('battle')
      if not raw or raw['finished']:raise ValueError('Lancez un combat avant de choisir une technique.')
      if key not in ('light','heavy','ultimate','defend','abandon'):raise ValueError('Technique inconnue.')
      fighters=[]
      for i,f in enumerate(raw['fighters']):
       fighter=(ArenaFighter if i==0 and payload.get('skills') else Fighter)(**f);fighter.hp=f['hp'];fighter.max_hp=f['max_hp'];fighters.append(fighter)
      if payload.get('skills'):fighters[0].loadout=payload['skills']
      battle=BattleState(**{**raw,'fighters':fighters})
      if key=='ultimate' and fighters[0].ultimate_cd>0:raise ValueError('Technique encore en recharge.')
      if key=='abandon':battle.finished=True;battle.winner_index=1;battle.log.append('Vous vous repliez.')
      else:
       battle.log.extend(technique_action(battle,key,resolve_action) if payload.get('skills') else resolve_action(battle,key))
       if not battle.finished:battle.switch();battle.log.extend(resolve_action(battle,bot_choose_action(battle.actor(),battle.target())))
       if not battle.finished:battle.switch()
      payload['battle']=asdict(battle)
      if battle.finished:
       advance=battle.winner_index==0
       if not advance:payload['retry_at']=now+60
       message='Victoire : objectif validé.' if advance else 'Défaite : aucune preuve perdue. Nouvelle tentative dans une minute.'
      else:message='Tour résolu.'
    else:raise ValueError('Action de campagne inconnue.')
    if advance:
     self.collect(c,uid,step['id'],now)
     for item,name,recipient in PROPS.values():
      if recipient==step['id']:c.execute('UPDATE campaign_items SET delivered_at=? WHERE user_id=? AND item_id=? AND delivered_at IS NULL',(now,uid,item))
     stage+=1;entered=now;payload={k:v for k,v in payload.items() if k in ('choices','edition','admin_replay','reward_quote','reward_version')}
   if action=='campaign_accept' or accepted is not None and stage!=row['stage']:self.expedition_boundary(c,uid,q,stage,payload,entered)
   c.execute('UPDATE campaign_progress SET quest_index=?,stage=?,accepted_at=?,entered_at=?,revision=revision+1,payload=? WHERE user_id=?',(idx,stage,accepted,entered,json.dumps(payload,ensure_ascii=False),uid))
   c.commit();return message
