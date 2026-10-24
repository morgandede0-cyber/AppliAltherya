"""Guided Activity onboarding, persistent discoveries and one-time welcome reward."""
import os,json
from pathlib import Path
from tutorial_engine import TutorialStore, TUTORIAL_GOLD, TUTORIAL_XP

TUTORIAL_REVISION='wolf-twelve-required-20261024-v1'
# One global rollout: old completions are invalid for this revision; reward receipts survive.
GUIDE=json.loads(Path(__file__).with_name('tutorial-guide.json').read_text())
LAST_STEP=len(GUIDE)-1
GUIDE_CATALOG='wolf-twelve-20261024'

class ActivityTutorial:
 destinations=tuple(s['destination'] for s in GUIDE)
 def __init__(self, activity):
  self.a=activity;self.store=TutorialStore(activity.path)
  with self.a.conn() as c:
   c.execute('CREATE TABLE IF NOT EXISTS activity_tutorial_revision(user_id INTEGER PRIMARY KEY,revision TEXT NOT NULL,finished INTEGER NOT NULL DEFAULT 0)')
   c.execute('CREATE TABLE IF NOT EXISTS activity_tutorial_receipts(identity_key TEXT PRIMARY KEY,user_id INTEGER NOT NULL,discord_id TEXT,name TEXT NOT NULL,claimed_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,gold_paid INTEGER NOT NULL DEFAULT 0,xp_paid INTEGER NOT NULL DEFAULT 0)')
   c.execute('CREATE TABLE IF NOT EXISTS activity_tutorial_steps(user_id INTEGER PRIMARY KEY,step INTEGER NOT NULL DEFAULT 0,replay INTEGER NOT NULL DEFAULT 0)')
   c.execute('CREATE TABLE IF NOT EXISTS activity_tutorial_visits(user_id INTEGER NOT NULL,step INTEGER NOT NULL,destination TEXT NOT NULL,PRIMARY KEY(user_id,step))')
   c.execute('CREATE TABLE IF NOT EXISTS activity_tutorial_catalog(user_id INTEGER PRIMARY KEY,catalog TEXT NOT NULL)')
 @staticmethod
 def discord_required():
  return bool(os.getenv('DISCORD_CLIENT_ID','').strip() or os.getenv('DISCORD_CLIENT_SECRET','').strip())
 def identity(self, uid):
  p=self.a.discord_profile(uid);return ('discord:'+p['discord_id'],p['discord_id']) if p else ('local:'+str(uid),None)
 def state(self, uid):
  old=self.store.state(uid)
  key,discord_id=self.identity(uid)
  with self.a.conn() as c:
   c.execute('BEGIN IMMEDIATE')
   if old['reward_claimed'] or old['gold_claimed'] or old['xp_claimed']:
    name=c.execute('SELECT name FROM activity_sessions WHERE user_id=? LIMIT 1',(uid,)).fetchone()
    c.execute('INSERT OR IGNORE INTO activity_tutorial_receipts(identity_key,user_id,discord_id,name,claimed_at,gold_paid,xp_paid) VALUES(?,?,?,?,COALESCE(?,CURRENT_TIMESTAMP),?,?)',(key,uid,discord_id,name[0] if name else 'Aventurier',old['completed_at'],TUTORIAL_GOLD if old['gold_claimed'] or old['reward_claimed'] else 0,TUTORIAL_XP if old['xp_claimed'] or old['reward_claimed'] else 0))
   receipt=c.execute('SELECT * FROM activity_tutorial_receipts WHERE identity_key=?',(key,)).fetchone()
   if receipt and receipt['gold_paid']>=TUTORIAL_GOLD and receipt['xp_paid']>=TUTORIAL_XP and not old['reward_claimed']:
    c.execute('UPDATE tutorial_progress SET completed=1,reward_claimed=1,gold_claimed=1,xp_claimed=1,completed_at=COALESCE(completed_at,?) WHERE user_id=?',(receipt['claimed_at'],uid))
    old={**old,'completed':1,'reward_claimed':1}
   c.execute('INSERT OR IGNORE INTO activity_tutorial_steps(user_id) VALUES(?)',(uid,))
   version=c.execute('SELECT revision,finished FROM activity_tutorial_revision WHERE user_id=?',(uid,)).fetchone()
   if not version or version['revision']!=TUTORIAL_REVISION:
    c.execute('INSERT INTO activity_tutorial_revision VALUES(?,?,0) ON CONFLICT(user_id) DO UPDATE SET revision=excluded.revision,finished=0',(uid,TUTORIAL_REVISION))
    c.execute('UPDATE activity_tutorial_steps SET step=0,replay=0 WHERE user_id=?',(uid,))
    c.execute('DELETE FROM activity_tutorial_visits WHERE user_id=?',(uid,))
   version=c.execute('SELECT finished FROM activity_tutorial_revision WHERE user_id=?',(uid,)).fetchone()
   row=c.execute('SELECT step,replay FROM activity_tutorial_steps WHERE user_id=?',(uid,)).fetchone()
   catalog=c.execute('SELECT catalog FROM activity_tutorial_catalog WHERE user_id=?',(uid,)).fetchone()
   if not catalog or catalog[0]!=GUIDE_CATALOG:
    # Remap recorded discoveries by destination, never reinterpret an old index.
    discoveries={r[0] for r in c.execute('SELECT destination FROM activity_tutorial_visits WHERE user_id=?',(uid,))}
    c.execute('DELETE FROM activity_tutorial_visits WHERE user_id=?',(uid,))
    for step,destination in enumerate(self.destinations):
     if destination in discoveries:c.execute('INSERT INTO activity_tutorial_visits VALUES(?,?,?)',(uid,step,destination))
    if not (old['completed'] and version['finished']) or row['replay']:
     next_step=next((i for i,d in enumerate(self.destinations) if d not in discoveries),LAST_STEP)
     c.execute('UPDATE activity_tutorial_steps SET step=? WHERE user_id=?',(next_step,uid))
     row=c.execute('SELECT step,replay FROM activity_tutorial_steps WHERE user_id=?',(uid,)).fetchone()
    c.execute('INSERT INTO activity_tutorial_catalog VALUES(?,?) ON CONFLICT(user_id) DO UPDATE SET catalog=excluded.catalog',(uid,GUIDE_CATALOG))
   visited=[r[0] for r in c.execute('SELECT step FROM activity_tutorial_visits WHERE user_id=? ORDER BY step',(uid,))]
   if not (old['completed'] and version['finished']) and row['step']>0 and not visited:
    c.execute('UPDATE activity_tutorial_steps SET step=0 WHERE user_id=?',(uid,))
    row=c.execute('SELECT step,replay FROM activity_tutorial_steps WHERE user_id=?',(uid,)).fetchone()
  return dict(total_steps=len(GUIDE),visited=visited,completed=bool(old['completed'] and version['finished']),reward_claimed=bool(old['reward_claimed']),step=row['step'],replay=bool(row['replay']),gold=TUTORIAL_GOLD,xp=TUTORIAL_XP,discord_required=self.discord_required(),discord_verified=bool(discord_id))
 def action(self, uid, body):
  self.state(uid)
  action=body['action'];expected=body.get('step')
  if self.discord_required() and not self.a.discord_profile(uid):raise ValueError('Connexion Discord requise pour suivre le tutoriel.')
  key,discord_id=self.identity(uid)
  if action in ('tutorial_next','tutorial_previous','tutorial_finish','tutorial_visit') and (type(expected) is not int or not 0<=expected<=LAST_STEP):raise ValueError('Étape du tutoriel invalide.')
  with self.a.conn() as c:
   c.execute('BEGIN IMMEDIATE')
   progress=c.execute('SELECT * FROM tutorial_progress WHERE user_id=?',(uid,)).fetchone()
   row=c.execute('SELECT step,replay FROM activity_tutorial_steps WHERE user_id=?',(uid,)).fetchone()
   version=c.execute('SELECT finished FROM activity_tutorial_revision WHERE user_id=?',(uid,)).fetchone()
   completed=bool(progress['completed'] and version['finished'])
   if action=='tutorial_replay':
    if not completed:raise ValueError('Terminez d’abord votre premier tutoriel.')
    if not row['replay']:
     c.execute('UPDATE activity_tutorial_steps SET step=0,replay=1 WHERE user_id=?',(uid,))
     c.execute('DELETE FROM activity_tutorial_visits WHERE user_id=?',(uid,))
    return 'Tutoriel ouvert.'
   if action=='tutorial_cancel':
    if not completed:raise ValueError('Terminez le tutoriel pour entrer dans Legacy.')
    c.execute('UPDATE activity_tutorial_steps SET replay=0 WHERE user_id=?',(uid,));return 'Tutoriel fermé.'
   if completed and not row['replay']:return 'Tutoriel déjà terminé. Récompense déjà enregistrée.'
   if expected!=row['step']:return 'Votre progression a été actualisée.'
   if action=='tutorial_visit':
    destination=body.get('destination')
    if destination!=self.destinations[expected]:raise ValueError('Ce lieu ne correspond pas à l’étape du tutoriel.')
    c.execute('INSERT OR IGNORE INTO activity_tutorial_visits VALUES(?,?,?)',(uid,expected,destination))
    return 'Découverte enregistrée. Reviens au guide pour poursuivre.'
   if action=='tutorial_next' or (action=='tutorial_finish' and expected!=LAST_STEP):
    visited=c.execute('SELECT 1 FROM activity_tutorial_visits WHERE user_id=? AND step=?',(uid,expected)).fetchone()
    if not visited:raise ValueError('Ouvrez d’abord la fonction indiquée par le guide.')
   if action=='tutorial_previous':
    if expected<=0:raise ValueError('Vous êtes au début du tutoriel.')
    c.execute('UPDATE activity_tutorial_steps SET step=step-1 WHERE user_id=?',(uid,));return ''
   if action=='tutorial_next':
    if expected>=LAST_STEP:raise ValueError('Validez la dernière étape du tutoriel.')
    if expected==0:c.execute('UPDATE tutorial_progress SET runs=runs+1,last_started_at=CURRENT_TIMESTAMP WHERE user_id=?',(uid,))
    c.execute('UPDATE activity_tutorial_steps SET step=step+1 WHERE user_id=?',(uid,));return ''
   if action!='tutorial_finish' or expected!=LAST_STEP:raise ValueError('Parcourez les étapes du tutoriel avant de terminer.')
   for step,destination in enumerate(self.destinations[:-1]):
    if not c.execute('SELECT 1 FROM activity_tutorial_visits WHERE user_id=? AND step=? AND destination=?',(uid,step,destination)).fetchone():raise ValueError('Découvrez toutes les fonctions du guide avant de terminer.')
   c.execute('INSERT OR IGNORE INTO activity_tutorial_visits VALUES(?,?,?)',(uid,LAST_STEP,self.destinations[LAST_STEP]))
   # Both awards, level changes and flags commit together in this Activity's DB.
   # The original bot's global Gold helper is intentionally not used here.
   gold=0;xp=0
   name=c.execute('SELECT name FROM activity_sessions WHERE user_id=? LIMIT 1',(uid,)).fetchone()
   c.execute('INSERT OR IGNORE INTO activity_tutorial_receipts(identity_key,user_id,discord_id,name) VALUES(?,?,?,?)',(key,uid,discord_id,name[0] if name else 'Aventurier'))
   receipt=c.execute('SELECT * FROM activity_tutorial_receipts WHERE identity_key=?',(key,)).fetchone()
   if not progress['reward_claimed']:
    if not receipt['gold_paid'] and not progress['gold_claimed'] and c.execute('INSERT OR IGNORE INTO activity_rewards VALUES(?)',('tutorial-welcome:'+str(uid),)).rowcount:
     gold=TUTORIAL_GOLD;c.execute('UPDATE players SET wallet_gold=wallet_gold+? WHERE user_id=?',(gold,uid))
    if not receipt['xp_paid'] and not progress['xp_claimed']:
     xp=TUTORIAL_XP;before=c.execute('SELECT xp FROM castle_profiles WHERE user_id=?',(uid,)).fetchone()[0]
     c.execute('UPDATE castle_profiles SET xp=xp+? WHERE user_id=?',(xp,uid))
     self.a.castle._queue_levelups(c,uid,before,before+xp);self.a.castle._sync_level(c,uid)
   c.execute('UPDATE activity_tutorial_receipts SET gold_paid=?,xp_paid=?,user_id=?,name=? WHERE identity_key=?',(TUTORIAL_GOLD,TUTORIAL_XP,uid,name[0] if name else 'Aventurier',key))
   c.execute('UPDATE tutorial_progress SET completed=1,reward_claimed=1,gold_claimed=1,xp_claimed=1,completed_at=COALESCE(completed_at,CURRENT_TIMESTAMP),last_completed_at=CURRENT_TIMESTAMP WHERE user_id=?',(uid,))
   c.execute('UPDATE activity_tutorial_steps SET replay=0 WHERE user_id=?',(uid,))
   c.execute('UPDATE activity_tutorial_revision SET finished=1 WHERE user_id=?',(uid,))
   return f'Bienvenue dans Legacy ! +{gold} Gold et +{xp} XP.' if gold or xp else 'Tutoriel terminé. Récompense déjà obtenue.'
