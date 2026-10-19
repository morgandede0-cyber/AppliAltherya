"""Persistent Activity adapter for the original ten-floor Tower of Ashkar."""
import json,time
from datetime import datetime,timedelta
from zoneinfo import ZoneInfo
from progression import level_from_xp,ASHKAR_FLOOR_XP
from arena_engine import arena_player_skills
import arena_techniques,ashkar_arena
from tower_techniques import FLOORS
ZONE=ZoneInfo('Europe/Paris')
def today():return datetime.now(ZONE).date().isoformat()
def reset_at():
 now=datetime.now(ZONE);return datetime.combine(now.date()+timedelta(days=1),datetime.min.time(),ZONE).timestamp()
class Ashkar:
 def __init__(self,a):
  self.a=a
  with a.conn() as c:
   c.execute('CREATE TABLE IF NOT EXISTS ashkar_progress(user_id INTEGER PRIMARY KEY,max_floor INTEGER NOT NULL DEFAULT 0)')
   c.execute('CREATE TABLE IF NOT EXISTS ashkar_daily(user_id INTEGER NOT NULL,day TEXT NOT NULL,cleared INTEGER NOT NULL DEFAULT 0,PRIMARY KEY(user_id,day))')
   c.execute('CREATE TABLE IF NOT EXISTS activity_ashkar(user_id INTEGER PRIMARY KEY,revision INTEGER NOT NULL DEFAULT 0,payload TEXT NOT NULL DEFAULT "{}")')
   c.execute('CREATE TABLE IF NOT EXISTS activity_ashkar_receipts(user_id INTEGER NOT NULL,floor INTEGER NOT NULL,gold INTEGER NOT NULL,xp INTEGER NOT NULL,pouciel INTEGER NOT NULL,completed_at REAL NOT NULL,PRIMARY KEY(user_id,floor))')
 def row(self,c,uid):
  c.execute('INSERT OR IGNORE INTO ashkar_progress(user_id) VALUES(?)',(uid,));c.execute('INSERT OR IGNORE INTO ashkar_daily(user_id,day) VALUES(?,?)',(uid,today()));c.execute('INSERT OR IGNORE INTO activity_ashkar(user_id) VALUES(?)',(uid,));return dict(c.execute('SELECT * FROM activity_ashkar WHERE user_id=?',(uid,)).fetchone())
 def active_in(self,c,uid):
  r=c.execute('SELECT payload FROM activity_ashkar WHERE user_id=?',(uid,)).fetchone();return bool(r and json.loads(r[0]).get('status')=='active')
 def active(self,uid):
  with self.a.conn() as c:return self.active_in(c,uid)
 def elsewhere(self,c,uid):
  r=c.execute('SELECT payload FROM activity_play WHERE user_id=?',(uid,)).fetchone()
  if r and json.loads(r[0]).get('status')=='active':return True
  r=c.execute('SELECT payload FROM campaign_progress WHERE user_id=?',(uid,)).fetchone();b=json.loads(r[0]).get('battle') if r else None
  return bool(b and not b['finished'])
 def snapshot(self,uid):
  with self.a.conn() as c:
   r=self.row(c,uid);p=json.loads(r['payload']);floor=c.execute('SELECT max_floor FROM ashkar_progress WHERE user_id=?',(uid,)).fetchone()[0];cleared=c.execute('SELECT cleared FROM ashkar_daily WHERE user_id=? AND day=?',(uid,today())).fetchone()[0];level=level_from_xp(c.execute('SELECT xp FROM castle_profiles WHERE user_id=?',(uid,)).fetchone()[0])[0];busy=self.elsewhere(c,uid)
   reason='Niveau 5 requis' if level<5 else 'Les dix étages sont terminés' if floor>=10 else 'Trois étages validés aujourd’hui' if cleared>=3 else 'Terminez votre autre partie ou combat' if busy else 'Reprenez votre combat en cours' if p.get('status')=='active' else ''
   battle=None
   if p.get('battle'):
    b=p['battle'];battle={k:b[k] for k in ('floor','player_name','player_level','player_hp','player_max_hp','enemy_hp','enemy_max_hp','ultimate_cd','enemy_enraged')}
   return dict(available=level>=5,level_required=5,revision=r['revision'],progress=floor,daily_cleared=cleared,daily_limit=3,remaining=max(0,3-cleared),reset_at=reset_at(),day=today(),complete=floor>=10,status=p.get('status','idle'),can_start=not reason,start_reason=reason,floor=p.get('floor',min(floor+1,10)),battle=battle,skills=p.get('skills') or arena_player_skills(battle['player_level'] if battle else level),logs=p.get('logs',[]),result=p.get('result'),combat=ashkar_arena.public(p,r['revision']),floors=[dict(floor=n,**e,xp=ASHKAR_FLOOR_XP[n],cleared=n<=floor,current=n==floor+1,technique=arena_techniques.TOWER_CATALOG.get(n,{}).get('name'),technique_owned=n%10==0 and bool(c.execute('SELECT 1 FROM activity_ashkar_techniques WHERE user_id=? AND floor=?',(uid,n)).fetchone())) for n,e in FLOORS.items()])
 def action(self,uid,body):
  action=body['action']
  if action not in ('ashkar_start','ashkar_step'):raise ValueError('Action de tour inconnue.')
  with self.a.conn() as c:
   c.execute('BEGIN IMMEDIATE');r=self.row(c,uid);p=json.loads(r['payload'])
   if type(body.get('revision')) is not int or body['revision']!=r['revision']:raise ValueError('Le combat a changé. Actualisez la tour.')
   level=level_from_xp(c.execute('SELECT xp FROM castle_profiles WHERE user_id=?',(uid,)).fetchone()[0])[0]
   if level<5:raise ValueError('Niveau 5 requis pour la Tour d’Ashkar.')
   floor=c.execute('SELECT max_floor FROM ashkar_progress WHERE user_id=?',(uid,)).fetchone()[0]+1
   if action=='ashkar_start':
    if p.get('status')=='active':raise ValueError('Reprenez votre combat en cours.')
    requested=body.get('floor')
    if type(requested) is not int or not 1<=requested<=10 or requested>floor:raise ValueError('Cet étage est verrouillé.')
    replay=requested<floor;floor=requested
    if not replay and c.execute('SELECT cleared FROM ashkar_daily WHERE user_id=? AND day=?',(uid,today())).fetchone()[0]>=3:raise ValueError('Vous avez validé trois étages aujourd’hui.')
    if self.elsewhere(c,uid):raise ValueError('Terminez votre autre partie ou combat avant d’entrer.')
    name=c.execute('SELECT name FROM activity_sessions WHERE user_id=?',(uid,)).fetchone()[0];skills=arena_techniques.book(c,uid,level,0)['skills']
    p=ashkar_arena.create(uid,name,level,self.a.khaz.bonuses_in(c,uid),floor,skills);p['replay']=replay;message='Vous affrontez '+FLOORS[floor]['name']+'.'
   else:
    if p.get('status')!='active':raise ValueError('Aucun combat de tour en cours.')
    key=body.get('key')
    if key not in ('light','heavy','ultimate','defend','abandon'):raise ValueError('Technique inconnue.')
    if p.get('engine')!=2:
     old=p;raw=old['battle'];old_skills={k:{**v,'id':'base_'+k} for k,v in arena_player_skills(raw['player_level']).items()}
     p=ashkar_arena.create(uid,raw['player_name'],raw['player_level'],self.a.khaz.bonuses_in(c,uid),old['floor'],old_skills,raw);p['arena_battle']['log']=old.get('logs',[]);p['logs']=old.get('logs',[]);p['replay']=False
    floor=p['floor'];finished,won=ashkar_arena.step(p,key);lost=finished and not won;message='Tour résolu.'
    if won:
     current=c.execute('SELECT max_floor FROM ashkar_progress WHERE user_id=?',(uid,)).fetchone()[0];e=FLOORS[floor];xp=ASHKAR_FLOOR_XP[floor];replay=p.get('replay',False)
     if not replay:
      if current!=floor-1:raise ValueError('Cet étage a déjà été validé.')
      if not c.execute('UPDATE ashkar_daily SET cleared=cleared+1 WHERE user_id=? AND day=? AND cleared<3',(uid,today())).rowcount:raise ValueError('Limite quotidienne atteinte.')
      c.execute('INSERT INTO activity_ashkar_receipts VALUES(?,?,?,?,?,?)',(uid,floor,e['gold'],xp,e['pouciel'],time.time()));c.execute('UPDATE ashkar_progress SET max_floor=? WHERE user_id=?',(floor,uid));c.execute('UPDATE players SET wallet_gold=wallet_gold+? WHERE user_id=?',(e['gold'],uid));c.execute('UPDATE legacy_wallet SET pouciel=pouciel+? WHERE user_id=?',(e['pouciel'],uid));self.a.castle.add_xp(uid,xp);self.a.castle.record(uid,'tower_clear',1)
     technique=arena_techniques.grant_tower(c,uid,floor);p['status']='won';p['result']=dict(won=True,gold=0 if replay else e['gold'],xp=0 if replay else xp,pouciel=0 if replay else e['pouciel'],floor=floor,replay=replay,technique_unlocked=technique);ashkar_arena.report(p,p['result'],current if replay else floor);message='Victoire !'+(' Technique dérobée : '+technique['name'] if technique else '')
    elif lost:
     p['status']='lost';p['result']=dict(won=False,abandoned=key=='abandon',gold=0,xp=0,pouciel=0,floor=floor);ashkar_arena.report(p,p['result'],c.execute('SELECT max_floor FROM ashkar_progress WHERE user_id=?',(uid,)).fetchone()[0]);message='Repli.' if key=='abandon' else 'Défaite. Vos étages acquis sont conservés.'
   c.execute('UPDATE activity_ashkar SET revision=revision+1,payload=? WHERE user_id=?',(json.dumps(p,ensure_ascii=False),uid));c.commit();return message
