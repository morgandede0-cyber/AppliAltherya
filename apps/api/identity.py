"""Bind opaque browser sessions to a canonical profile using verified OAuth only."""
import hashlib,secrets
from discord_profile import verified_user

class DiscordIdentity:
 def __init__(self, activity):
  self.a=activity
  with self.a.conn() as c:
   c.execute('BEGIN IMMEDIATE')
   # Older builds allowed only one session per profile. Preserve every old token.
   unique_uid=False
   for index in c.execute('PRAGMA index_list(activity_sessions)').fetchall():
    if index['unique'] and [r['name'] for r in c.execute('PRAGMA index_info("'+index['name'].replace('"','""')+'")')]==['user_id']:unique_uid=True
   if unique_uid:
    c.execute('ALTER TABLE activity_sessions RENAME TO activity_sessions_single_profile')
    c.execute('CREATE TABLE activity_sessions(token TEXT PRIMARY KEY,user_id INTEGER NOT NULL,name TEXT NOT NULL)')
    c.execute('INSERT INTO activity_sessions SELECT token,user_id,name FROM activity_sessions_single_profile')
    c.execute('DROP TABLE activity_sessions_single_profile')
   c.execute('CREATE INDEX IF NOT EXISTS activity_sessions_user ON activity_sessions(user_id)')
   c.execute('CREATE TABLE IF NOT EXISTS activity_discord_accounts(discord_id TEXT PRIMARY KEY,user_id INTEGER NOT NULL UNIQUE)')
   # Keep the existing rewarded profile when historical devices created duplicates.
   rows=c.execute('SELECT d.user_id,d.discord_id FROM activity_discord d LEFT JOIN tutorial_progress t ON t.user_id=d.user_id ORDER BY COALESCE(t.reward_claimed,0) DESC,COALESCE(t.completed,0) DESC,d.user_id').fetchall()
   for row in rows:c.execute('INSERT OR IGNORE INTO activity_discord_accounts VALUES(?,?)',(row['discord_id'],row['user_id']))
 def bind(self, uid, user, token=None):
  p=verified_user(user)
  with self.a.conn() as c:
   c.execute('BEGIN IMMEDIATE')
   current=c.execute('SELECT discord_id FROM activity_discord WHERE user_id=?',(uid,)).fetchone()
   account=c.execute('SELECT user_id FROM activity_discord_accounts WHERE discord_id=?',(p['discord_id'],)).fetchone()
   if account:target=account['user_id']
   elif current and current['discord_id']!=p['discord_id']:
    if not token:raise ValueError('Session requise pour changer de compte Discord.')
    target=secrets.randbelow(2**52)+1
    while c.execute('SELECT 1 FROM players WHERE user_id=? UNION SELECT 1 FROM activity_sessions WHERE user_id=?',(target,target)).fetchone():target=secrets.randbelow(2**52)+1
   else:target=uid
   c.execute('INSERT OR IGNORE INTO activity_discord_accounts VALUES(?,?)',(p['discord_id'],target))
   previous=c.execute('SELECT name FROM activity_sessions WHERE user_id=? LIMIT 1',(target,)).fetchone()
   name=previous['name'] if previous else p['display_name']
   if token:
    digest=hashlib.sha256(token.encode()).hexdigest()
    if not c.execute('SELECT 1 FROM activity_sessions WHERE token=? AND user_id=?',(digest,uid)).fetchone():raise ValueError('Session Discord invalide.')
    c.execute('UPDATE activity_sessions SET user_id=?,name=? WHERE token=?',(target,name,digest))
   elif target!=uid:
    c.execute('UPDATE activity_sessions SET user_id=?,name=? WHERE user_id=?',(target,name,uid))
   c.execute('INSERT INTO activity_discord VALUES(?,?,?,?,?,?) ON CONFLICT(user_id) DO UPDATE SET discord_id=excluded.discord_id,avatar=excluded.avatar,username=excluded.username,display_name=excluded.display_name,discriminator=excluded.discriminator',(target,p['discord_id'],p['avatar'],p['username'],p['display_name'],p['discriminator']))
  return target
