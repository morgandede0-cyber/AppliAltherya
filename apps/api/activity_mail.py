"""Private durable letters; delivery and rewards have separate once-only receipts."""
import hashlib,json,re,time,uuid

class Mailbox:
 def __init__(self,a):
  self.a=a
  with a.conn() as c:
   c.execute('CREATE TABLE IF NOT EXISTS activity_mail_messages(id TEXT PRIMARY KEY,command_ref TEXT NOT NULL UNIQUE,sender TEXT NOT NULL,title TEXT NOT NULL,body TEXT NOT NULL,rewards TEXT NOT NULL,has_reward INTEGER NOT NULL,created_at REAL NOT NULL)')
   c.execute('CREATE TABLE IF NOT EXISTS activity_mail_deliveries(message_id TEXT NOT NULL,user_id INTEGER NOT NULL,read_at REAL,claimed_at REAL,archived_at REAL,PRIMARY KEY(message_id,user_id))')
   c.execute('CREATE INDEX IF NOT EXISTS activity_mail_inbox ON activity_mail_deliveries(user_id,archived_at,message_id)')
 def counts(self,uid):
  with self.a.conn() as c:r=c.execute('SELECT COUNT(*) total,COALESCE(SUM(d.read_at IS NULL),0) unread,COALESCE(SUM(m.has_reward=1 AND d.claimed_at IS NULL),0) unclaimed,COALESCE(SUM(d.read_at IS NULL OR (m.has_reward=1 AND d.claimed_at IS NULL)),0) attention FROM activity_mail_deliveries d JOIN activity_mail_messages m ON m.id=d.message_id WHERE d.user_id=? AND d.archived_at IS NULL',(uid,)).fetchone()
  return dict(r)
 def listing(self,uid,page):
  if type(page) is not int or not 0<=page<=1000000:raise ValueError('Page invalide.')
  with self.a.conn() as c:
   total=c.execute('SELECT COUNT(*) FROM activity_mail_deliveries WHERE user_id=? AND archived_at IS NULL',(uid,)).fetchone()[0];pages=max(1,(total+3)//4);page=min(page,pages-1)
   rows=c.execute('SELECT m.id,m.sender,m.title,m.body,m.rewards,m.created_at,m.has_reward,d.read_at,d.claimed_at FROM activity_mail_deliveries d JOIN activity_mail_messages m ON m.id=d.message_id WHERE d.user_id=? AND d.archived_at IS NULL ORDER BY m.created_at DESC,m.id DESC LIMIT 4 OFFSET ?',(uid,page*4)).fetchall()
  entries=[dict(id=r['id'],title=r['title'],body=r['body'],sender='Comptoir des joueurs' if r['sender']=='Comptoir des joueurs' else 'Intendance d’Altherya',rewards=json.loads(r['rewards']),created_at=r['created_at'],has_reward=bool(r['has_reward']),read=r['read_at'] is not None,claimed=r['claimed_at'] is not None) for r in rows]
  return dict(entries=entries,page=page,pages=pages,total=total,save_owner=hashlib.sha256(f'activity:{uid}'.encode()).hexdigest()[:24])
 def send(self,c,targets,args,actor,reference):
  if not reference:raise ValueError('Référence de commande requise.')
  if c.execute('SELECT 1 FROM activity_mail_messages WHERE command_ref=?',(reference,)).fetchone():return
  targets=list(dict.fromkeys(targets))
  if not targets:raise ValueError('Aucun joueur admissible dans le registre.')
  rewards={k:args[k] for k in ('gold','xp','pouciel','item','quantity')};has_reward=any(rewards[k] for k in ('gold','xp','pouciel','quantity'));mid=uuid.uuid4().hex
  c.execute('INSERT INTO activity_mail_messages VALUES(?,?,?,?,?,?,?,?)',(mid,reference,actor,args['title'].strip(),args['text'].strip(),json.dumps(rewards,ensure_ascii=False),int(has_reward),time.time()))
  c.executemany('INSERT INTO activity_mail_deliveries(message_id,user_id) VALUES(?,?)',[(mid,u) for u in targets])
 def action(self,uid,body):
  action=body['action'];mid=body.get('key')
  if not isinstance(mid,str) or not re.fullmatch('[0-9a-f]{32}',mid):raise ValueError('Courrier introuvable.')
  with self.a.conn() as c:
   r=c.execute('SELECT m.rewards,m.has_reward,d.read_at,d.claimed_at FROM activity_mail_deliveries d JOIN activity_mail_messages m ON m.id=d.message_id WHERE d.user_id=? AND d.message_id=? AND d.archived_at IS NULL',(uid,mid)).fetchone()
   if not r:raise ValueError('Courrier introuvable.')
   now=time.time()
   if action=='mail_read':c.execute('UPDATE activity_mail_deliveries SET read_at=COALESCE(read_at,?) WHERE user_id=? AND message_id=?',(now,uid,mid));return 'Courrier ouvert.'
   if action=='mail_archive':
    if r['has_reward'] and r['claimed_at'] is None:raise ValueError('Récupérez les récompenses avant d’archiver ce courrier.')
    c.execute('UPDATE activity_mail_deliveries SET archived_at=?,read_at=COALESCE(read_at,?) WHERE user_id=? AND message_id=?',(now,now,uid,mid));return 'Courrier archivé.'
   if action!='mail_claim':raise ValueError('Action de courrier inconnue.')
   if r['claimed_at'] is not None:return 'Récompenses déjà récupérées.'
   if not r['has_reward']:raise ValueError('Ce courrier ne contient pas de récompense.')
   if self.a.khaz.active(c,uid):raise ValueError('Terminez votre combat ou votre partie avant de récupérer les récompenses.')
   reward=json.loads(r['rewards']);gold,xp,pouciel=(reward[k] for k in ('gold','xp','pouciel'))
   old_xp=c.execute('SELECT xp FROM castle_profiles WHERE user_id=?',(uid,)).fetchone()[0]
   wallet=c.execute('SELECT wallet_gold FROM players WHERE user_id=?',(uid,)).fetchone()[0]
   self.a.khaz.ensure(c,uid);old_p=c.execute('SELECT pouciel FROM legacy_wallet WHERE user_id=?',(uid,)).fetchone()[0]
   if any(old+delta>1000000000 for old,delta in ((wallet,gold),(old_xp,xp),(old_p,pouciel))):raise ValueError('Un solde dépasserait sa limite. Contactez un administrateur ; le courrier est conservé.')
   c.execute('UPDATE players SET wallet_gold=wallet_gold+? WHERE user_id=?',(gold,uid));c.execute('UPDATE legacy_wallet SET pouciel=pouciel+? WHERE user_id=?',(pouciel,uid));c.execute('UPDATE castle_profiles SET xp=xp+? WHERE user_id=?',(xp,uid))
   if xp:self.a.castle._queue_levelups(c,uid,old_xp,old_xp+xp);self.a.castle._sync_level(c,uid)
   if reward['quantity']:
    key=reward['item'];quantity=reward['quantity'];old=c.execute('SELECT quantity FROM resources WHERE user_id=? AND resource_name=?',(uid,key)).fetchone()
    if old and old[0]+quantity>1000000000:raise ValueError('Quantité d’objets hors limite. Le courrier est conservé.')
    c.execute('INSERT INTO resources VALUES(?,?,?) ON CONFLICT(user_id,resource_name) DO UPDATE SET quantity=quantity+excluded.quantity',(uid,key,quantity))
    from story_engine import ALL_STORY_ITEMS
    if key in ALL_STORY_ITEMS:c.execute('INSERT OR IGNORE INTO story_item_purchases(user_id,item_name,purchased_at) VALUES(?,?,?)',(uid,key,int(now)))
   c.execute('UPDATE activity_mail_deliveries SET claimed_at=?,read_at=COALESCE(read_at,?) WHERE user_id=? AND message_id=?',(now,now,uid,mid))
   return 'Récompenses du courrier récupérées.'
