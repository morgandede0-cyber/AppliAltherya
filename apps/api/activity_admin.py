"""Private Activity registry. Discord identities come exclusively from OAuth."""
import os,re
from tutorial import TUTORIAL_REVISION
DEFAULT_ADMIN_IDS={'666805849011912705','342359563791761410','587578557027450900'}

class ActivityAdmin:
 def __init__(self,a):
  self.a=a
  with a.conn() as c:c.execute('CREATE TABLE IF NOT EXISTS activity_admin_log(request_id TEXT PRIMARY KEY,actor TEXT NOT NULL,target TEXT NOT NULL,field TEXT NOT NULL,before_value INTEGER NOT NULL,after_value INTEGER NOT NULL,reason TEXT NOT NULL,created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP)')
 def allowed(self,uid):
  profile=self.a.discord_profile(uid)
  ids={s.strip() for s in os.environ['ACTIVITY_ADMIN_IDS'].split(',')} if 'ACTIVITY_ADMIN_IDS' in os.environ else DEFAULT_ADMIN_IDS
  return bool(profile and profile['discord_id'] in ids)
 def require(self,uid):
  if not self.allowed(uid):raise PermissionError('Accès administrateur refusé.')
 def target(self,discord_id):
  if not isinstance(discord_id,str) or not re.fullmatch(r'[0-9]{15,22}',discord_id):raise ValueError('Joueur invalide.')
  with self.a.conn() as c:r=c.execute('SELECT a.user_id FROM activity_discord_accounts a JOIN tutorial_progress t ON t.user_id=a.user_id JOIN activity_tutorial_revision v ON v.user_id=a.user_id AND v.revision=? AND v.finished=1 JOIN activity_tutorial_receipts r ON r.identity_key=? WHERE a.discord_id=? AND t.completed=1 AND t.reward_claimed=1 AND r.gold_paid>=100 AND r.xp_paid>=25',(TUTORIAL_REVISION,'discord:'+discord_id,discord_id)).fetchone()
  if not r:raise ValueError('Ce joueur n’a pas terminé le tutoriel.')
  return r['user_id']
 def handle(self,actor,body):
  self.require(actor)
  action=body.get('action')
  if action=='list':
   q=body.get('query','');page=body.get('page',0)
   if not isinstance(q,str) or len(q)>80 or type(page) is not int or page<0 or page>100000:raise ValueError('Recherche invalide.')
   # Canonical accounts, not guild members or one row per browser session.
   with self.a.conn() as c:
    rows=c.execute('SELECT a.discord_id,a.user_id,d.username,d.display_name,COALESCE((SELECT name FROM activity_sessions s WHERE s.user_id=a.user_id LIMIT 1),d.display_name) AS name FROM activity_discord_accounts a JOIN activity_discord d ON d.user_id=a.user_id JOIN tutorial_progress t ON t.user_id=a.user_id JOIN activity_tutorial_revision v ON v.user_id=a.user_id AND v.revision=? AND v.finished=1 JOIN activity_tutorial_receipts r ON r.identity_key=(\'discord:\'||a.discord_id) WHERE t.completed=1 AND t.reward_claimed=1 AND r.gold_paid>=100 AND r.xp_paid>=25',(TUTORIAL_REVISION,)).fetchall()
   matches=[dict(r) for r in rows if q.strip().casefold() in ' '.join(str(r[k]) for k in ('discord_id','username','display_name','name')).casefold()]
   matches.sort(key=lambda r:(r['name'].casefold(),r['discord_id']));pages=max(1,(len(matches)+3)//4);page=min(page,pages-1)
   return dict(players=[{k:v for k,v in r.items() if k!='user_id'} for r in matches[page*4:page*4+4]],page=page,pages=pages,total=len(matches))
  target=body.get('player');uid=self.target(target)
  if action=='detail':
   with self.a.conn() as c:
    name=c.execute('SELECT name FROM activity_sessions WHERE user_id=? LIMIT 1',(uid,)).fetchone()
    receipt=c.execute('SELECT claimed_at FROM activity_tutorial_receipts WHERE identity_key=?',('discord:'+target,)).fetchone()
   s=self.a.snapshot(uid,name[0] if name else 'Aventurier');p=self.a.discord_profile(uid)
   return dict(player=target,name=s['name'],username=p['username'],level=s['level'],xp=s['xp'],xp_needed=s['xp_needed'],balance=s['balance'],resources=s['resources'],gear=s['gear'],owned=s['owned'],story=s['owned_story_items'],reputations=dict(tavern=s['tavern']['label'],alley=s['alley']['reputation']['label']),delays=dict(larceny=s['alley']['larceny_remaining'],ban=s['alley']['ban_remaining'],daily_available=s['daily_available']),tutorial_at=receipt['claimed_at'])
  if action=='history':
   with self.a.conn() as c:rows=c.execute('SELECT actor,field,before_value,after_value,reason,created_at FROM activity_admin_log WHERE target=? ORDER BY created_at DESC,rowid DESC LIMIT 30',(target,)).fetchall()
   return dict(entries=[dict(r) for r in rows])
  if action!='adjust':raise ValueError('Action administrateur invalide.')
  field=body.get('field');amount=body.get('amount');expected=body.get('expected');reason=body.get('reason');rid=body.get('request_id')
  if field not in ('wallet','bank','xp') or type(amount) is not int or amount==0 or abs(amount)>1000000 or (field=='xp' and amount<0) or type(expected) is not int or not isinstance(reason,str) or not 3<=len(reason.strip())<=200 or not isinstance(rid,str) or not re.fullmatch(r'[a-zA-Z0-9-]{16,80}',rid):raise ValueError('Modification invalide : montant entier et motif requis.')
  identity=self.a.discord_profile(actor)['discord_id'];table,column=('castle_profiles','xp') if field=='xp' else ('players','wallet_gold' if field=='wallet' else 'bank_gold')
  with self.a.conn() as c:
   c.execute('BEGIN IMMEDIATE')
   old=c.execute('SELECT * FROM activity_admin_log WHERE request_id=?',(rid,)).fetchone()
   if old:
    if (old['actor'],old['target'],old['field'],old['after_value']-old['before_value'],old['reason'])!=(identity,target,field,amount,reason.strip()):raise ValueError('Référence de modification déjà utilisée.')
    return dict(message='Modification déjà enregistrée.')
   before=c.execute(f'SELECT {column} FROM {table} WHERE user_id=?',(uid,)).fetchone()[0]
   if before!=expected:raise ValueError('Les données ont changé. Actualisez la fiche avant de confirmer.')
   after=before+amount
   if not 0<=after<=1000000000:raise ValueError('Le résultat doit être compris entre 0 et 1 milliard.')
   c.execute(f'UPDATE {table} SET {column}=? WHERE user_id=?',(after,uid))
   if field=='xp':
    if after>before:self.a.castle._queue_levelups(c,uid,before,after)
    self.a.castle._sync_level(c,uid)
   c.execute('INSERT INTO activity_admin_log(request_id,actor,target,field,before_value,after_value,reason) VALUES(?,?,?,?,?,?,?)',(rid,identity,target,field,before,after,reason.strip()))
   self.a.notifications.admin_event(c,rid,identity,target,field,before,after,reason.strip())
  return dict(message='Modification enregistrée.')
