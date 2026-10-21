import sys, unittest, tempfile, uuid, json, subprocess
from pathlib import Path
from unittest.mock import patch
from concurrent.futures import ThreadPoolExecutor
sys.path.insert(0,str(Path(__file__).parents[1]))
from activity import Activity
from save_safety import backup


class EconomySaveTests(unittest.TestCase):
 def setUp(self):
  self.tmp=tempfile.TemporaryDirectory();self.path=Path(self.tmp.name)/'game.db';self.a=Activity(self.path)
  (self.uid,self.name),self.token=self.a.session('');self.a.snapshot(self.uid,self.name)
  with self.a.conn() as c:
   c.execute('UPDATE tutorial_progress SET completed=1 WHERE user_id=?',(self.uid,))
   c.execute('UPDATE activity_tutorial_revision SET finished=1 WHERE user_id=?',(self.uid,))
   c.execute('UPDATE players SET wallet_gold=100 WHERE user_id=?',(self.uid,))
 def tearDown(self):self.tmp.cleanup()
 def snap(self):return self.a.snapshot(self.uid,self.name)
 def act(self,**kw):return self.a.action(self.uid,kw)
 def test_original_starter_prices_and_no_duplicate_purchase(self):
  with self.a.conn() as c:c.execute('UPDATE players SET wallet_gold=800 WHERE user_id=?',(self.uid,))
  self.act(action='buy',key='axe');self.act(action='buy',key='bag');self.act(action='buy',key='axe')
  s=self.snap();self.assertEqual(s['balance']['wallet'],0);self.assertTrue(s['owned']['axe']);self.assertTrue(s['owned']['bag'])
 def test_daily_passive_income_less_than_active_objectives(self):
  s=self.snap();self.assertLess(s['daily_reward']['gold'],s['quest_reward']['gold'])
  self.act(action='daily');self.assertEqual(self.snap()['balance']['wallet'],110)
 def test_job_generation_in_new_ranges_and_signed_old_contract_preserved(self):
  for _ in range(50):
   _,jobs=self.a.jobs._generate_batch()
   self.assertEqual(len(jobs),8)
   for j in jobs:self.assertEqual((j.rarity,j.reward),('unrevealed',0))
  board=self.snap()['board'];j=board['jobs'][0];self.act(action='job_accept',batch=board['batch_id'],key=j['job_id'])
  with self.a.conn() as c:
   row=c.execute('SELECT pending_job_json FROM job_board_state WHERE user_id=?',(self.uid,)).fetchone();data=json.loads(row[0]);data['reward']=500
   c.execute('UPDATE job_board_state SET pending_job_json=?,reward_ready_at=0 WHERE user_id=?',(json.dumps(data),self.uid))
  self.a=Activity(self.path);self.act(action='job_claim');self.assertEqual(self.snap()['balance']['wallet'],600)
 def test_unsigned_old_offer_is_repriced_and_stale_batch_rejected(self):
  board=self.snap()['board']
  with self.a.conn() as c:
   jobs=[{**j,'rarity':'common','reward':500} for j in board['jobs']]
   c.execute('UPDATE job_board_state SET jobs_json=? WHERE user_id=?',(json.dumps(jobs),self.uid))
  self.a=Activity(self.path);fresh=self.snap()['board']
  self.assertNotEqual(fresh['batch_id'],board['batch_id']);self.assertNotIn('reward',fresh['jobs'][0]);self.assertEqual(len(fresh['jobs']),8)
  self.act(action='job_accept',batch=board['batch_id'],key=jobs[0]['job_id']);self.assertIsNone(self.snap()['pending'])
 def test_duplicate_bank_operation_concurrent_and_after_restart(self):
  body=dict(action='deposit',amount=30,request_id=str(uuid.uuid4()))
  with ThreadPoolExecutor(max_workers=2) as pool:results=list(pool.map(lambda _:self.a.action(self.uid,body),range(2)))
  self.assertEqual(results[0],results[1]);self.assertEqual(self.snap()['balance']['bank'],30)
  self.a=Activity(self.path);self.a.action(self.uid,body);self.assertEqual(self.snap()['balance']['wallet'],70)
  with self.assertRaises(ValueError):self.a.action(self.uid,{**body,'amount':10})
 def test_two_distinct_bank_operations_both_preserved(self):
  with ThreadPoolExecutor(max_workers=2) as pool:list(pool.map(lambda _:self.act(action='deposit',amount=25,request_id=str(uuid.uuid4())),range(2)))
  s=self.snap();self.assertEqual((s['balance']['wallet'],s['balance']['bank']),(50,50))
 def test_failure_between_purchase_and_response_rolls_back_inventory_gold_and_receipt(self):
  with self.a.conn() as c:c.execute('UPDATE players SET wallet_gold=1000 WHERE user_id=?',(self.uid,))
  original=self.a._action
  def fail(uid,body):original(uid,body);raise RuntimeError('simulated interruption')
  key=str(uuid.uuid4())
  with patch.object(self.a,'_action',side_effect=fail):
   with self.assertRaises(RuntimeError):self.act(action='buy',key='axe',request_id=key)
  self.assertEqual(self.snap()['balance']['wallet'],1000);self.assertFalse(self.snap()['owned']['axe'])
  self.act(action='buy',key='axe',request_id=key);self.assertEqual(self.snap()['balance']['wallet'],600)
 def test_game_debit_and_saved_state_atomic_on_crash(self):
  with patch.object(self.a.play,'save',side_effect=RuntimeError('disk failure')):
   with self.assertRaises(RuntimeError):self.act(action='game_start',key='dice',wager=10,revision=self.snap()['play']['revision'],request_id=str(uuid.uuid4()))
  self.assertEqual(self.snap()['balance']['wallet'],100)
  with self.a.conn() as c:self.assertEqual(c.execute('SELECT COUNT(*) FROM activity_operations').fetchone()[0],0)
 def test_verified_backup_restores_session_inventory_and_idempotency_receipt(self):
  with self.a.conn() as c:c.execute('UPDATE players SET wallet_gold=1000 WHERE user_id=?',(self.uid,))
  body=dict(action='buy',key='axe',request_id=str(uuid.uuid4()));self.a.action(self.uid,body)
  copy=backup(self.path,True);self.assertTrue(copy.is_file())
  restored=Activity(copy);self.assertEqual(restored.session(self.token)[0][0],self.uid)
  restored.action(self.uid,body);s=restored.snapshot(self.uid,self.name)
  self.assertEqual(s['balance']['wallet'],600);self.assertTrue(s['owned']['axe'])
 def test_objectives_follow_server_level_resources_and_current_step(self):
  with self.a.conn() as c:c.execute('UPDATE players SET wallet_gold=1000 WHERE user_id=?',(self.uid,))
  s=self.snap();equipment=next(g for g in s['objectives'] if g['key']=='equipment');self.assertTrue(equipment['ready'])
  self.act(action='buy',key='axe');self.act(action='buy',key='bag')
  goals=self.snap()['objectives'];forge=next(g for g in goals if g['key']=='forge')
  self.assertFalse(forge['ready']);self.assertIn('Niveau 5',forge['detail']);self.assertIn('Pierre brute',forge['detail'])
  self.assertEqual(next(g for g in goals if g['key']=='destination')['target'],5)
 def test_real_process_crash_does_not_commit_half_purchase(self):
  with self.a.conn() as c:c.execute('UPDATE players SET wallet_gold=1000 WHERE user_id=?',(self.uid,))
  script="""import sys,os;sys.path.insert(0,sys.argv[3]);from activity import Activity
+a=Activity(sys.argv[1]);uid=int(sys.argv[2]);original=a._action
+def crash(uid,body):
+ original(uid,body);os._exit(23)
+a._action=crash;a.action(uid,dict(action='buy',key='axe',request_id='crash-test-operation-001'))
+""".replace('\n+','\n')
  result=subprocess.run([sys.executable,'-c',script,str(self.path),str(self.uid),str(Path(__file__).parents[1])],capture_output=True,text=True)
  self.assertEqual(result.returncode,23,result.stderr)
  self.a=Activity(self.path);s=self.snap();self.assertEqual(s['balance']['wallet'],1000);self.assertFalse(s['owned']['axe'])
 def test_pending_request_cannot_move_to_a_different_discord_character(self):
  with self.assertRaises(ValueError):self.act(action='deposit',amount=10,save_owner='other-character',request_id=str(uuid.uuid4()))
  self.assertEqual(self.snap()['balance']['wallet'],100)
 def test_existing_wallet_and_inventory_survive_balance_change(self):
  self.a.expeditions.add_resources(self.uid,{'Pierre brute':17});self.a=Activity(self.path)
  s=self.snap();self.assertEqual(s['balance']['wallet'],100);self.assertEqual(s['resources']['Pierre brute'],17)

if __name__=='__main__':unittest.main()
