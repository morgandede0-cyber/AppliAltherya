"""Private read-only combat archives; no replay of rewards or live battle state."""
import json,time,hashlib
class CombatArchive:
 def __init__(self,a):
  self.a=a
  with a.conn() as c:
   c.execute('CREATE TABLE IF NOT EXISTS activity_tower_results(id TEXT PRIMARY KEY,user_id INTEGER NOT NULL,created_at REAL NOT NULL,payload TEXT NOT NULL)')
   c.execute('CREATE INDEX IF NOT EXISTS tower_result_player ON activity_tower_results(user_id,created_at DESC)')
 def tower(self,c,uid,result):
  c.execute('INSERT OR IGNORE INTO activity_tower_results VALUES(?,?,?,?)',(result['battle_id'],uid,time.time(),json.dumps(result,ensure_ascii=False)))
 def listing(self,uid,page=0,source='all'):
  if type(page) is not int or not 0<=page<=100000 or source not in ('all','arena','tower'):raise ValueError('Historique de combats invalide.')
  parts=[];params=[]
  if source!='tower':parts.append("SELECT battle_id id,created_at,payload,'arena' source FROM activity_arena_results WHERE user_id=?");params.append(uid)
  if source!='arena':parts.append("SELECT id,created_at,payload,'tower' source FROM activity_tower_results WHERE user_id=?");params.append(uid)
  union=' UNION ALL '.join(parts)
  with self.a.conn() as c:
   total=c.execute('SELECT COUNT(*) FROM ('+union+')',params).fetchone()[0];pages=max(1,(total+3)//4);page=min(page,pages-1)
   rows=c.execute('SELECT * FROM ('+union+') ORDER BY created_at DESC,id DESC LIMIT 4 OFFSET ?',(*params,page*4)).fetchall()
  return dict(entries=[dict(id=r['id'],source=r['source'],created_at=r['created_at'],report=json.loads(r['payload'])) for r in rows],page=page,pages=pages,total=total,save_owner=hashlib.sha256(f'activity:{uid}'.encode()).hexdigest()[:24])
