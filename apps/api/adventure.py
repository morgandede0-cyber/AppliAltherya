"""Activity progression and comfort. All mutations join Activity's atomic receipt."""
import hashlib,json,time,os,statistics
from pathlib import Path
from arena_engine import Fighter,BattleState,resolve_action,arena_player_skills
from arena_techniques import ArenaFighter,book,resolve
from trading import ITEMS
from castle_engine import QUESTS
from expedition_engine import EXPEDITIONS,LOOT_TABLES
from progression import level_from_xp

PROFESSIONS={'axe':'Bûcheron','pickaxe':'Mineur','spear':'Chasseur','hands':'Cueilleur'}
SPECIALIZATIONS={'steady':('Méticuleux','Une poche de collecte et une ressource supplémentaire tous les 5 voyages terminés après spécialisation.'),'swift':('Éclaireur','Vos futures expéditions durent 5 % moins longtemps.')}
TITLES={'traveler':('Voyageur',5),'veteran':('Vétéran',20),'master':('Maître des routes',50)}

def digest(text):return int(hashlib.sha256(text.encode()).hexdigest()[:12],16)
def dump(value):return json.dumps(value,ensure_ascii=False)

class Adventure:
 def __init__(self,a):
  self.a=a
  with a.conn() as c:
   c.execute('CREATE TABLE IF NOT EXISTS activity_adventure(user_id INTEGER PRIMARY KEY,payload TEXT NOT NULL)')
   c.execute('CREATE TABLE IF NOT EXISTS activity_journey_choices(run_id TEXT PRIMARY KEY,user_id INTEGER NOT NULL,choice TEXT NOT NULL DEFAULT "",settled INTEGER NOT NULL DEFAULT 0)')
   c.execute('CREATE TABLE IF NOT EXISTS activity_watch(user_id INTEGER NOT NULL,item TEXT NOT NULL,day TEXT NOT NULL DEFAULT "",PRIMARY KEY(user_id,item))')
   c.execute('CREATE INDEX IF NOT EXISTS activity_watch_item ON activity_watch(item)')
   c.execute('CREATE TABLE IF NOT EXISTS activity_runtime_errors(id INTEGER PRIMARY KEY,created_at REAL NOT NULL,code TEXT NOT NULL)')
 def read(self,c,uid):
  row=c.execute('SELECT payload FROM activity_adventure WHERE user_id=?',(uid,)).fetchone()
  return json.loads(row[0]) if row else {}
 def save(self,c,uid,data):c.execute('INSERT INTO activity_adventure VALUES(?,?) ON CONFLICT(user_id) DO UPDATE SET payload=excluded.payload',(uid,dump(data)))
 def counts(self,c,uid):
  return dict(c.execute("SELECT tool_key,COUNT(*) FROM expedition_runs r WHERE user_id=? AND claimed=1 AND NOT EXISTS(SELECT 1 FROM activity_admin_cancelled_expeditions x WHERE x.run_id=r.run_id) GROUP BY tool_key",(uid,)))
 def event(self,c,uid):
  row=c.execute('SELECT * FROM expedition_runs WHERE user_id=? AND claimed=0 ORDER BY started_at DESC LIMIT 1',(uid,)).fetchone()
  if not row:return None
  saved=c.execute('SELECT choice FROM activity_journey_choices WHERE run_id=?',(row['run_id'],)).fetchone()
  return dict(run_id=row['run_id'],name=EXPEDITIONS[row['expedition_key']]['name'],ready=time.time()>=row['started_at']+(row['ends_at']-row['started_at'])/2,ends_at=row['ends_at'],choice=saved[0] if saved else '',options=[dict(key='observe',label='Examiner la piste',detail='À l’arrivée : une poche temporaire de collecte et une ressource accessible supplémentaire.'),dict(key='hurry',label='Prendre le raccourci',detail='Réduit de 5 % la durée totale restante, sans bonus de ressource.')])
 def training_public(self,t):
  if not t:return None
  raw=t['battle'];return dict(revision=t['revision'],finished=raw['finished'],turn=raw['turn_no'],fighters=[dict(name=f['name'],hp=f['hp'],max_hp=f['max_hp']) for f in raw['fighters']],logs=raw['log'][-12:],skills=t['skills'],mode=t['mode'])
 def snapshot(self,uid):
  with self.a.conn() as c:
   data=self.read(c,uid);counts=self.counts(c,uid);total=sum(counts.values());day=self.a.castle._today()
   jobs=[]
   for key,name in PROFESSIONS.items():
    n=counts.get(key,0);rank=min(5,n//5);spec=data.get('specializations',{}).get(key,{})
    jobs.append(dict(key=key,name=name,runs=n,rank=rank,progress=n%5,target=5,unlocked=n>=5,specialization=spec.get('key',''),choices=[dict(key=k,name=v[0],description=v[1]) for k,v in SPECIALIZATIONS.items()]))
   watches=[r[0] for r in c.execute('SELECT item FROM activity_watch WHERE user_id=? ORDER BY item',(uid,))]
   prices=[]
   # Only completed player sales; no offer prices or fabricated reference value.
   for item in watches:
    sold=c.execute("SELECT price,quantity FROM activity_trade_offers WHERE item=? AND status='sold' ORDER BY closed_at DESC LIMIT 20",(item,)).fetchall()
    prices.append(dict(item=item,sales=len(sold),unit_median=round(statistics.median(r[0]/r[1] for r in sold),2) if sold else None,available=c.execute("SELECT COUNT(*) FROM activity_trade_offers WHERE item=? AND status='active' AND expires_at>? AND seller<>?",(item,time.time(),uid)).fetchone()[0]))
   return dict(professions=jobs,titles=[dict(key=k,name=v[0],required=v[1],unlocked=total>=v[1]) for k,v in TITLES.items()],title=data.get('title',''),goal=data.get('goal',''),favorites=prices,trade_items=sorted(ITEMS),daily_changed=data.get('daily_day')==day,event=self.event(c,uid),training=self.training_public(data.get('training')),total_expeditions=total,combos=['Charge puis attaque lourde : le bonus préparé augmente la prochaine frappe.','Garde et contre : la riposte se prépare seulement si un impact est bloqué.','Perce-garde : choisissez-la contre une cible protégée ; gardez votre exécution pour une cible affaiblie.'])
 def prepare(self,uid):
  """Called after an actual successful start; apply only future travel specialization."""
  with self.a.conn() as c:
   run=c.execute('SELECT * FROM expedition_runs WHERE user_id=? AND claimed=0 ORDER BY started_at DESC LIMIT 1',(uid,)).fetchone()
   if not run:return
   c.execute('INSERT OR IGNORE INTO activity_journey_choices(run_id,user_id) VALUES(?,?)',(run['run_id'],uid))
   spec=self.read(c,uid).get('specializations',{}).get(run['tool_key'],{})
   if spec.get('key')=='steady' and (self.counts(c,uid).get(run['tool_key'],0)-spec.get('since',0)+1)%5==0:c.execute('UPDATE expedition_runs SET capacity=capacity+1 WHERE run_id=?',(run['run_id'],))
   if spec.get('key')=='swift':
    end=run['started_at']+round((run['ends_at']-run['started_at'])*.95)
    c.execute('UPDATE expedition_runs SET ends_at=? WHERE run_id=?',(end,run['run_id']))
    c.execute('UPDATE expedition_drop_events SET drop_at=MIN(drop_at,?) WHERE run_id=?',(end,run['run_id']))
 def finish(self,uid,run):
  with self.a.conn() as c:
   row=c.execute('SELECT * FROM activity_journey_choices WHERE run_id=? AND user_id=?',(run.run_id,uid)).fetchone()
   if not row or row['settled']:return
   if not c.execute('UPDATE activity_journey_choices SET settled=1 WHERE run_id=? AND settled=0',(run.run_id,)).rowcount:return
   spec=self.read(c,uid).get('specializations',{}).get(run.tool_key,{})
   after=self.counts(c,uid).get(run.tool_key,0)-spec.get('since',0)+1
   bonus=int(row['choice']=='observe')+int(spec.get('key')=='steady' and after>0 and after%5==0)
   loot=json.loads(c.execute('SELECT loot_json FROM expedition_runs WHERE run_id=?',(run.run_id,)).fetchone()[0]);space=max(0,run.capacity-sum(loot.values()))
   candidates=[n for n,t,w in LOOT_TABLES.get(run.expedition_key,{}).get(run.tool_key,[]) if t<=run.tool_level]
   if candidates and bonus and space:
    name=candidates[digest(run.run_id)%len(candidates)];qty=min(space,bonus)
    # Credit directly within the same unit as finalize_run; never alter hidden event draws.
    c.execute('INSERT INTO resources VALUES(?,?,?) ON CONFLICT(user_id,resource_name) DO UPDATE SET quantity=quantity+excluded.quantity',(uid,name,qty))
 def alert(self,c,seller,item):
  day=self.a.castle._today()
  for row in c.execute('SELECT user_id,day FROM activity_watch WHERE item=? AND user_id<>?',(item,seller)).fetchall():
   if row['day']==day:continue
   uid=row['user_id'];self.a.mailbox.send(c,[uid],dict(title='Objet recherché disponible',text=item+' est disponible au comptoir. Le lot peut être vendu entre-temps.',gold=0,xp=0,pouciel=0,item='',quantity=0),'Comptoir des joueurs',f'watch:{uid}:{item}:{day}')
   c.execute('UPDATE activity_watch SET day=? WHERE user_id=? AND item=?',(day,uid,item))
 def daily(self,c,uid,key):
  data=self.read(c,uid);day=self.a.castle._today();qs,_=self.a.castle.quests(uid)
  old=next((q for q in qs if q['key']==key),None)
  if data.get('daily_day')==day or not old or old['progress'] or any(q['claimed'] for q in qs):raise ValueError('Un seul remplacement par jour, avant toute progression de ce défi et avant la récompense.')
  used={q['key'] for q in qs};candidates=[k for k in QUESTS if k not in used and not (k=='arena_win' and 'combat' in used or k=='combat' and 'arena_win' in used)]
  candidates=[k for k in candidates if not c.execute('SELECT 1 FROM castle_daily_progress WHERE user_id=? AND day=? AND quest_key=? AND progress>0',(uid,day,k)).fetchone()]
  if not candidates:raise ValueError('Aucun autre défi classique disponible aujourd’hui.')
  target=sorted(candidates)[digest(f'{uid}:{day}')%len(candidates)];plan=json.loads(c.execute('SELECT plan_json FROM castle_daily_plans WHERE user_id=? AND day=?',(uid,day)).fetchone()[0]);del plan[key];plan[target]=QUESTS[target]
  c.execute('UPDATE castle_daily_plans SET plan_json=? WHERE user_id=? AND day=?',(dump(plan),uid,day));c.execute('DELETE FROM castle_daily_progress WHERE user_id=? AND day=? AND quest_key=?',(uid,day,key));data['daily_day']=day;self.save(c,uid,data)
  return 'Défi remplacé. Récompense quotidienne inchangée.'
 def action(self,uid,b):
  action=b['action'];key=b.get('key','')
  with self.a.conn() as c:
   data=self.read(c,uid)
   if action=='adventure_daily':return self.daily(c,uid,key)
   if action=='adventure_specialize':
    tool=b.get('tool');counts=self.counts(c,uid)
    if tool not in PROFESSIONS or key not in SPECIALIZATIONS or counts.get(tool,0)<5:raise ValueError('Cinq expéditions de ce métier sont requises.')
    if tool in data.get('specializations',{}):raise ValueError('Votre spécialisation de métier est déjà choisie.')
    data.setdefault('specializations',{})[tool]=dict(key=key,since=counts[tool]);message='Spécialisation choisie pour vos prochains voyages.'
   elif action=='adventure_title':
    if key and (key not in TITLES or sum(self.counts(c,uid).values())<TITLES[key][1]):raise ValueError('Titre verrouillé.')
    data['title']=key;message='Titre du profil modifié.'
   elif action=='adventure_goal':
    if key not in ('','axe','pickaxe','spear','bag'):raise ValueError('Équipement invalide.')
    data['goal']=key;message='Objectif de forge enregistré.'
   elif action=='adventure_favorite':
    if key not in ITEMS:raise ValueError('Objet non échangeable.')
    if c.execute('SELECT 1 FROM activity_watch WHERE user_id=? AND item=?',(uid,key)).fetchone():c.execute('DELETE FROM activity_watch WHERE user_id=? AND item=?',(uid,key));return 'Recherche retirée.'
    if c.execute('SELECT COUNT(*) FROM activity_watch WHERE user_id=?',(uid,)).fetchone()[0]>=8:raise ValueError('Huit recherches maximum.')
    c.execute('INSERT INTO activity_watch(user_id,item) VALUES(?,?)',(uid,key));return 'Recherche suivie. Une alerte par objet et par jour au maximum.'
   elif action=='adventure_event':
    e=self.event(c,uid)
    if not e or not e['ready'] or e['ends_at']<=time.time() or e['run_id']!=b.get('run_id') or e['choice'] or key not in ('observe','hurry'):raise ValueError('Cette rencontre n’est plus disponible.')
    c.execute('INSERT OR IGNORE INTO activity_journey_choices(run_id,user_id) VALUES(?,?)',(e['run_id'],uid))
    if not c.execute('UPDATE activity_journey_choices SET choice=? WHERE run_id=? AND user_id=? AND choice="" AND settled=0',(key,e['run_id'],uid)).rowcount:raise ValueError('Décision déjà enregistrée.')
    if key=='observe':c.execute('UPDATE expedition_runs SET capacity=capacity+1 WHERE run_id=?',(e['run_id'],))
    if key=='hurry':
     row=c.execute('SELECT started_at,ends_at FROM expedition_runs WHERE run_id=?',(e['run_id'],)).fetchone();end=max(int(time.time())+1,int(row[1]-(row[1]-row[0])*.05))
     c.execute('UPDATE expedition_runs SET ends_at=? WHERE run_id=?',(end,e['run_id']));c.execute('UPDATE expedition_drop_events SET drop_at=MIN(drop_at,?) WHERE run_id=?',(end,e['run_id']))
    return 'Votre décision de voyage est enregistrée.'
   elif action=='adventure_training':
    level=level_from_xp(self.a.castle.profile(uid)['xp'])[0]
    if key=='start':
     mode=b.get('mode','balanced')
     if mode not in ('balanced','guard','aggressive'):raise ValueError('Mannequin inconnu.')
     skills=book(c,uid,level,0)['skills'];name=(self.a.discord_profile(uid) or {}).get('display_name','Aventurier');player=ArenaFighter(uid,name,'arena_fighter',max_hp=100+10*(level-1),player_level=level,**self.a.khaz.bonuses_in(c,uid));player.loadout=skills
     enemy=Fighter(None,'Mannequin d’entraînement','gardien',max_hp=100+10*(level-1),player_level=level)
     battle=BattleState('training','training',0,[player,enemy],0)
     from dataclasses import asdict
     data['training']=dict(battle=asdict(battle),skills=skills,revision=data.get('training',{}).get('revision',0)+1,mode=mode);message='Entraînement lancé : aucun gain, aucune tentative consommée.'
    else:
     t=data.get('training')
     if not t or t['battle']['finished'] or type(b.get('revision')) is not int or b['revision']!=t['revision']:raise ValueError('Entraînement terminé ou actualisé.')
     raw=t['battle'];fighters=[]
     for i,f in enumerate(raw['fighters']):
      obj=(ArenaFighter if i==0 else Fighter)(**f);obj.hp=f['hp'];obj.max_hp=f['max_hp'];fighters.append(obj)
     fighters[0].loadout=t['skills'];battle=BattleState(**{**raw,'fighters':fighters})
     if key=='stop':battle.finished=True;battle.winner_index=1
     elif key not in arena_player_skills(level):raise ValueError('Technique inconnue.')
     else:
      if key=='ultimate' and fighters[0].ultimate_cd:raise ValueError('Technique encore en recharge.')
      battle.log.extend(resolve(battle,key,resolve_action))
      if not battle.finished:
       battle.switch();enemykey='defend' if t['mode']=='guard' else 'heavy' if t['mode']=='aggressive' else ('light','heavy','defend')[(battle.turn_no//2)%3];battle.log.extend(resolve_action(battle,enemykey))
      if not battle.finished:battle.switch()
     if battle.turn_no>=100:battle.finished=True;battle.log.append('Limite d’entraînement atteinte : entraînez-vous à nouveau pour poursuivre.')
     from dataclasses import asdict
     t['battle']=asdict(battle);t['revision']+=1;message='Tour d’entraînement résolu. Aucun gain.'
   else:raise ValueError('Action inconnue.')
   self.save(c,uid,data);return message
 def health(self):
  folder=Path(os.getenv('ACTIVITY_BACKUP_DIR',str(self.a.path.parent/'backups')));files=sorted(folder.glob(self.a.path.name+'.*.sqlite3'),key=lambda p:p.stat().st_mtime) if folder.exists() else []
  with self.a.conn() as c:
   check=c.execute('PRAGMA quick_check').fetchone()[0]
   errors=[dict(r) for r in c.execute('SELECT created_at,code FROM activity_runtime_errors ORDER BY id DESC LIMIT 10')]
   wealth=[r[0] for r in c.execute('SELECT wallet_gold+bank_gold FROM players ORDER BY wallet_gold+bank_gold DESC')]
   operations=c.execute('SELECT COUNT(*) FROM activity_operations').fetchone()[0]
   pending=c.execute('SELECT COUNT(*) FROM activity_admin_previews WHERE result IS NULL AND expires>?',(time.time(),)).fetchone()[0]
  return dict(errors=errors,integrity=check,backup_count=len(files),last_backup_at=files[-1].stat().st_mtime if files else None,players=len(wealth),total_gold=sum(wealth),median_gold=statistics.median(wealth) if wealth else 0,top_ten_share=round(sum(wealth[:10])/sum(wealth)*100,2) if sum(wealth) else 0,operations=operations,pending_admin=pending,note='État de cette base Activity. Erreurs API depuis cette version uniquement, sans données sensibles. Les incidents extérieurs au processus et les requêtes non reçues ne sont pas mesurés.')
