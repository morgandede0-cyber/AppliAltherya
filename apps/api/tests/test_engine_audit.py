"""Cross-engine races and bounded reconciliation regression checks."""
import sys,tempfile,threading,unittest
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
from unittest.mock import patch
sys.path.insert(0,str(Path(__file__).parents[1]))
from activity import Activity
from sqlite_store import atomic
class EngineAuditTests(unittest.TestCase):
 def setUp(self):
  self.tmp=tempfile.TemporaryDirectory();self.a=Activity(self.tmp.name+'/test.db');(self.uid,_),_=self.a.session('');self.a.snapshot(self.uid,'Auditeur')
 def tearDown(self):self.tmp.cleanup()
 def test_simultaneous_engine_starts_create_only_one_expedition(self):
  engine=self.a.expeditions;original=engine.active_run;barrier=threading.Barrier(2)
  def lookup(uid):
   result=original(uid);barrier.wait(timeout=10);return result
  with patch.object(engine,'active_run',side_effect=lookup),ThreadPoolExecutor(max_workers=2) as pool:
   results=list(pool.map(lambda _:engine.start(self.uid,'elarwyn_foraging','hands'),range(2)))
  self.assertEqual(sum(r[0] for r in results),1)
  with self.a.conn() as c:self.assertEqual(c.execute('SELECT COUNT(*) FROM expedition_runs WHERE user_id=? AND claimed=0',(self.uid,)).fetchone()[0],1)
 def test_reward_reconciliation_remains_once_only_after_many_reads(self):
  ok,_,run=self.a.expeditions.start(self.uid,'elarwyn_foraging','hands');self.assertTrue(ok)
  before=self.a.castle.profile(self.uid)['xp']
  with patch('time.time',return_value=run.ends_at+2):
   self.a.snapshot(self.uid,'Auditeur');after=self.a.castle.profile(self.uid)['xp'];self.assertEqual(after-before,15)
   for _ in range(10):self.a.snapshot(self.uid,'Auditeur')
  self.assertEqual(self.a.castle.profile(self.uid)['xp'],after)
  self.a=Activity(self.a.path);self.a.snapshot(self.uid,'Auditeur');self.assertEqual(self.a.castle.profile(self.uid)['xp'],after)

 def test_thousand_already_paid_voyages_do_not_repeat_thousand_writes(self):
  _,_,run=self.a.expeditions.start(self.uid,'elarwyn_foraging','hands')
  with patch('time.time',return_value=run.ends_at+2):self.a.snapshot(self.uid,'Auditeur')
  with self.a.conn() as c:
   template=dict(c.execute('SELECT * FROM expedition_runs WHERE run_id=?',(run.run_id,)).fetchone());keys=list(template)
   for n in range(1000):
    template['run_id']='past-'+str(n);c.execute('INSERT INTO expedition_runs('+','.join(keys)+') VALUES('+','.join('?' for _ in keys)+')',list(template.values()));c.execute('INSERT INTO activity_rewards VALUES(?)',('expedition:'+template['run_id'],))
  before=self.a.castle.profile(self.uid)['xp'];statements=[]
  with atomic(self.a.path) as c:
   c.set_trace_callback(statements.append);self.a.reconcile(self.uid);c.set_trace_callback(None)
  self.assertLess(len(statements),20);self.assertEqual(self.a.castle.profile(self.uid)['xp'],before)

 def test_retained_legacy_combat_randomness_has_no_replayable_state(self):
  import tower_engine,legacy_world_forge
  for engine in (tower_engine,legacy_world_forge):
   with self.subTest(engine=engine.__name__),self.assertRaises(NotImplementedError):engine.random.getstate()

if __name__=='__main__':unittest.main()
