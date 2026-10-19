"""Transactional main campaign: server-owned steps, clocks, battles and receipts."""
import json,time
from pathlib import Path
from dataclasses import asdict
from progression import level_from_xp
from arena_engine import Fighter,BattleState,resolve_action,bot_choose_action
CATALOG=json.loads(Path(__file__).with_name('campaign_catalog.json').read_text(encoding='utf8'))
QUESTS=CATALOG['quests']
LEGACY_QUESTS=json.loads(Path(__file__).with_name('campaign_catalog_v1.json').read_text(encoding='utf8'))['quests']
def effective_quest(row,payload):
 # Already accepted missions keep their original steps and level gate until claimed.
 return (LEGACY_QUESTS if row['accepted_at'] is not None and payload.get('edition',1)<2 else QUESTS)[row['quest_index']]

class Campaign:
 def __init__(self,a):
  self.a=a
  with a.conn() as c:
   c.execute('CREATE TABLE IF NOT EXISTS campaign_progress(user_id INTEGER PRIMARY KEY,quest_index INTEGER NOT NULL DEFAULT 0,stage INTEGER NOT NULL DEFAULT 0,accepted_at REAL,entered_at REAL NOT NULL DEFAULT 0,revision INTEGER NOT NULL DEFAULT 0,payload TEXT NOT NULL DEFAULT "{}")')
   c.execute('CREATE TABLE IF NOT EXISTS campaign_receipts(user_id INTEGER NOT NULL,quest_id TEXT NOT NULL,gold INTEGER NOT NULL,xp INTEGER NOT NULL,completed_at REAL NOT NULL,PRIMARY KEY(user_id,quest_id))')
   c.execute('CREATE TABLE IF NOT EXISTS campaign_evidence(user_id INTEGER NOT NULL,quest_id TEXT NOT NULL,step_id TEXT NOT NULL,clue_id TEXT NOT NULL,place_id TEXT NOT NULL,title TEXT NOT NULL,text TEXT NOT NULL,found_at REAL NOT NULL,PRIMARY KEY(user_id,quest_id,step_id,clue_id))')
   c.execute('CREATE TABLE IF NOT EXISTS campaign_visits(user_id INTEGER NOT NULL,place_id TEXT NOT NULL,entered_at REAL NOT NULL,PRIMARY KEY(user_id,place_id))')
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
 def _expedition_done(self,c,uid,step,since):
  return bool(c.execute('SELECT 1 FROM expedition_runs WHERE user_id=? AND expedition_key=? AND claimed=1 AND started_at>=? LIMIT 1',(uid,step['destination'],int(since))).fetchone())
 def snapshot(self,uid):
  with self.a.conn() as c:
   row=self.row(c,uid);idx=row['quest_index'];payload=json.loads(row['payload']);done=c.execute('SELECT COUNT(*) FROM campaign_receipts WHERE user_id=?',(uid,)).fetchone()[0]
   level=level_from_xp(c.execute('SELECT xp FROM castle_profiles WHERE user_id=?',(uid,)).fetchone()[0])[0]
   if idx>=len(QUESTS):return dict(**self.journal(c,uid,level),complete=True,title=CATALOG['title'],completed=done,total=len(QUESTS),choices=payload.get('choices',{}),revision=row['revision'])
   q=dict(effective_quest(row,payload));stage=row['stage'];step=q['steps'][stage] if stage<len(q['steps']) else None
   if q['id']=='S4-Q08':
    outcome=payload.get('choices',{}).get('S4-Q07','')
    q['resolution']+=' Le Faussaire sera jugé.' if outcome.startswith('Secourir') else ' Le Faussaire a disparu ; les relevés sont préservés.'
   public_steps=[{**{k:v for k,v in s.items() if k not in ('answer','clues')},**({'clues':[{'id':clue['id'],'label':clue['label']} for clue in s['clues']]} if 'clues' in s else {})} for s in q['steps']]
   exp_ready=bool(step and step['kind']=='expedition' and row['accepted_at'] is not None and self._expedition_done(c,uid,step,row['entered_at']))
   level=level_from_xp(c.execute('SELECT xp FROM castle_profiles WHERE user_id=?',(uid,)).fetchone()[0])[0]
   battle=payload.get('battle');public_battle=None
   if battle:public_battle={'fighters':[{'name':f['name'],'hp':f['hp'],'max_hp':f['max_hp']} for f in battle['fighters']],'log':battle['log'][-10:],'finished':battle['finished'],'won':battle['winner_index']==0 if battle['finished'] else None,'turn':battle['turn_no'],'ultimate_cd':battle['fighters'][0]['ultimate_cd']}
   return dict(**self.journal(c,uid,level,step.get('place_id') if step and row['accepted_at'] is not None else None),edition=payload.get('edition',1) if row['accepted_at'] is not None else 2,complete=False,title=CATALOG['title'],completed=done,total=len(QUESTS),revision=row['revision'],quest={**{k:v for k,v in q.items() if k!='steps'},'steps':public_steps},stage=stage,accepted=row['accepted_at'] is not None,level_allowed=level>=q['min_level'],deadline=payload.get('deadline',0),retry_at=payload.get('retry_at',0),claim_at=(row['accepted_at'] or 0)+q['min_duration'],expedition_ready=exp_ready,battle=public_battle,choices=payload.get('choices',{}))
 def enter(self,uid,body):
  with self.a.conn() as c:
   c.execute('BEGIN IMMEDIATE');row=self.row(c,uid);payload=json.loads(row['payload']);active=None
   if row['quest_index']<len(QUESTS) and row['accepted_at'] is not None:
    q=effective_quest(row,payload)
    if row['stage']<len(q['steps']):active=q['steps'][row['stage']].get('place_id')
   level=level_from_xp(c.execute('SELECT xp FROM castle_profiles WHERE user_id=?',(uid,)).fetchone()[0])[0]
   place=next((p for p in self.journal(c,uid,level,active)['locations'] if p['id']==body.get('place_id')),None)
   if not place or not place['can_enter']:raise ValueError('Ce lieu demande le niveau et l’avancement d’histoire indiqués dans le journal.')
   c.execute('INSERT OR IGNORE INTO campaign_visits VALUES(?,?,?)',(uid,place['id'],time.time()));c.commit();return 'Vous entrez : '+place['name']+'.'
 def action(self,uid,body):
  if body['action']=='campaign_enter':return self.enter(uid,body)
  now=time.time()
  with self.a.conn() as c:
   c.execute('BEGIN IMMEDIATE');row=self.row(c,uid);idx=row['quest_index']
   if idx>=len(QUESTS):raise ValueError('La campagne est terminée.')
   payload=json.loads(row['payload']);q=effective_quest(row,payload);stage=row['stage'];accepted=row['accepted_at'];entered=row['entered_at'];action=body['action']
   if type(body.get('revision')) is not int or body['revision']!=row['revision'] or body.get('quest_id')!=q['id']:raise ValueError('La quête a changé. Actualisez le journal avant de réessayer.')
   if action=='campaign_accept':
    if accepted is not None:raise ValueError('Cette quête est déjà acceptée.')
    level=level_from_xp(c.execute('SELECT xp FROM castle_profiles WHERE user_id=?',(uid,)).fetchone()[0])[0]
    if level<q['min_level']:raise ValueError(f"Niveau {q['min_level']} requis pour cette quête.")
    payload['edition']=2;accepted=now;entered=now;message='Quête acceptée. Les objectifs se réalisent dans l’ordre.'
   elif action=='campaign_claim':
    if accepted is None or stage!=len(q['steps']):raise ValueError('Terminez tous les objectifs avant de remettre la quête.')
    if now<accepted+q['min_duration']:raise ValueError('La mission est encore en cours. Consultez le délai du journal.')
    if c.execute('SELECT 1 FROM campaign_receipts WHERE user_id=? AND quest_id=?',(uid,q['id'])).fetchone():raise ValueError('Récompense déjà récupérée.')
    c.execute('INSERT INTO campaign_receipts VALUES(?,?,?,?,?)',(uid,q['id'],q['gold'],q['xp'],now))
    c.execute('UPDATE players SET wallet_gold=wallet_gold+? WHERE user_id=?',(q['gold'],uid))
    before=c.execute('SELECT xp FROM castle_profiles WHERE user_id=?',(uid,)).fetchone()[0]
    c.execute('UPDATE castle_profiles SET xp=xp+?,quests_completed=quests_completed+1 WHERE user_id=?',(q['xp'],uid));self.a.castle._queue_levelups(c,uid,before,before+q['xp']);self.a.castle._sync_level(c,uid)
    idx+=1;stage=0;accepted=None;entered=now;payload={'choices':payload.get('choices',{})};message=f"{q['resolution']} +{q['gold']} Gold et +{q['xp']} XP."
   else:
    if accepted is None or stage>=len(q['steps']):raise ValueError('Aucun objectif actif.')
    step=q['steps'][stage];kind=step['kind'];advance=False;message=''
    if now<payload.get('retry_at',0):raise ValueError('Préparez une nouvelle tentative avant de réessayer.')
    if action=='campaign_step':
     if kind=='talk':advance=True;message=q['dialogue']
     elif kind in ('inspect','mission'):
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
      if not self._expedition_done(c,uid,step,entered):raise ValueError('Terminez l’expédition indiquée après le début de cet objectif, puis récupérez votre rapport.')
      advance=True;message='Votre rapport d’expédition est remis et ajouté au dossier.'
     else:raise ValueError('Cet objectif demande un combat.')
    elif action=='campaign_explore':
     if kind!='explore':raise ValueError('Ce lieu ne fait pas partie de votre objectif actif.')
     if not c.execute('SELECT 1 FROM campaign_visits WHERE user_id=? AND place_id=?',(uid,step['place_id'])).fetchone():raise ValueError('Entrez dans le lieu avant de chercher ses indices.')
     clue=next((x for x in step['clues'] if x['id']==body.get('clue_id')),None)
     if not clue:raise ValueError('Point d’enquête inconnu pour ce lieu.')
     if not c.execute('INSERT OR IGNORE INTO campaign_evidence VALUES(?,?,?,?,?,?,?,?)',(uid,q['id'],step['id'],clue['id'],step['place_id'],clue['label'],clue['text'],now)).rowcount:raise ValueError('Cet indice est déjà dans votre carnet.')
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
      battle=BattleState(q['id']+':'+str(stage),'campaign',0,[Fighter(uid,name,'arena_fighter',max_hp=100+10*(level-1),player_level=level,**self.a.khaz.bonuses_in(c,uid)),enemy],0)
      payload['battle']=asdict(battle);message='L’adversaire se met en garde. À vous de jouer.'
     else:
      raw=payload.get('battle')
      if not raw or raw['finished']:raise ValueError('Lancez un combat avant de choisir une technique.')
      if key not in ('light','heavy','ultimate','defend','abandon'):raise ValueError('Technique inconnue.')
      fighters=[]
      for f in raw['fighters']:
       fighter=Fighter(**f);fighter.hp=f['hp'];fighter.max_hp=f['max_hp'];fighters.append(fighter)
      battle=BattleState(**{**raw,'fighters':fighters})
      if key=='ultimate' and fighters[0].ultimate_cd>0:raise ValueError('Technique encore en recharge.')
      if key=='abandon':battle.finished=True;battle.winner_index=1;battle.log.append('Vous vous repliez.')
      else:
       battle.log.extend(resolve_action(battle,key))
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
     stage+=1;entered=now;payload={k:v for k,v in payload.items() if k in ('choices','edition')}
   c.execute('UPDATE campaign_progress SET quest_index=?,stage=?,accepted_at=?,entered_at=?,revision=revision+1,payload=? WHERE user_id=?',(idx,stage,accepted,entered,json.dumps(payload,ensure_ascii=False),uid))
   c.commit();return message
