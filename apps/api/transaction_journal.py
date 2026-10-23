"""Atomic, private economy trail. Read access is reserved to the existing admins."""
import json,time,uuid

class TransactionJournal:
 def __init__(self,a):
  self.a=a
  with a.conn() as c:
   c.execute('''CREATE TABLE IF NOT EXISTS activity_transaction_journal(
    id TEXT PRIMARY KEY,reference TEXT NOT NULL,actor INTEGER NOT NULL,user_id INTEGER NOT NULL,
    action TEXT NOT NULL,created_at REAL NOT NULL,before_json TEXT NOT NULL,after_json TEXT NOT NULL,
    gold_delta INTEGER NOT NULL,UNIQUE(reference,user_id))''')
   c.execute('CREATE INDEX IF NOT EXISTS transaction_player_time ON activity_transaction_journal(user_id,created_at DESC)')
   c.execute('CREATE INDEX IF NOT EXISTS transaction_reference ON activity_transaction_journal(reference)')
 def capture(self,c,uid):
  wallet=c.execute('SELECT wallet_gold,bank_gold FROM players WHERE user_id=?',(uid,)).fetchone()
  xp=c.execute('SELECT xp FROM castle_profiles WHERE user_id=?',(uid,)).fetchone()
  p=c.execute('SELECT pouciel FROM legacy_wallet WHERE user_id=?',(uid,)).fetchone()
  return dict(wallet=wallet[0] if wallet else 0,bank=wallet[1] if wallet else 0,xp=xp[0] if xp else 0,pouciel=p[0] if p else 0,
   resources=dict(c.execute('SELECT resource_name,quantity FROM resources WHERE user_id=? AND quantity<>0',(uid,))))
 def record(self,c,actor,uid,action,reference,before):
  after=self.capture(c,uid)
  if before==after:return
  delta=after['wallet']+after['bank']-before['wallet']-before['bank']
  c.execute('INSERT OR IGNORE INTO activity_transaction_journal VALUES(?,?,?,?,?,?,?,?,?)',
   (uuid.uuid4().hex,reference,actor,uid,action,time.time(),json.dumps(before,ensure_ascii=False),json.dumps(after,ensure_ascii=False),delta))
 def listing(self,body):
  page=body.get('page',0);q=body.get('query','');minimum=body.get('min_gain',0);player=body.get('player','')
  if type(page) is not int or not 0<=page<=100000 or not isinstance(q,str) or len(q)>80 or type(minimum) is not int or not 0<=minimum<=1000000000:raise ValueError('Recherche de transactions invalide.')
  where=['1=1'];params=[]
  if player:where.append('j.user_id=?');params.append(self.a.admin.target(player))
  if q:where.append('(j.id=? OR j.reference=? OR j.action LIKE ?)');params.extend((q,q,'%'+q+'%'))
  if minimum:where.append('j.gold_delta>=?');params.append(minimum)
  sql=' FROM activity_transaction_journal j LEFT JOIN activity_discord d ON d.user_id=j.user_id LEFT JOIN activity_discord actor ON actor.user_id=j.actor WHERE '+' AND '.join(where)
  with self.a.conn() as c:
   total=c.execute('SELECT COUNT(*)'+sql,params).fetchone()[0];pages=max(1,(total+9)//10);page=min(page,pages-1)
   rows=c.execute('SELECT j.*,d.discord_id,d.display_name,actor.display_name actor_name,actor.discord_id actor_discord_id'+sql+' ORDER BY j.created_at DESC,j.id DESC LIMIT 10 OFFSET ?',(*params,page*10)).fetchall()
  return dict(page=page,pages=pages,total=total,entries=[dict(id=r['id'],reference=r['reference'],action=r['action'],actor_name=r['actor_name'] or 'Aventurier',actor_discord_id=r['actor_discord_id'],name=r['display_name'] or 'Aventurier',discord_id=r['discord_id'],created_at=r['created_at'],gold_delta=r['gold_delta'],review=r['gold_delta']>=500,before=json.loads(r['before_json']),after=json.loads(r['after_json'])) for r in rows])
