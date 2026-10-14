import unittest,tempfile,sys
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
sys.path.insert(0,str(Path(__file__).parents[1]))
from activity import Activity
class TutorialTests(unittest.TestCase):
 def setUp(self):
  self.tmp=tempfile.TemporaryDirectory();self.a=Activity(self.tmp.name+'/test.db');(self.uid,self.name),self.token=self.a.session('');self.a.snapshot(self.uid,self.name)
 def tearDown(self):self.tmp.cleanup()
 def state(self):return self.a.snapshot(self.uid,self.name)
 def act(self,action,step=None,**other):return self.a.action(self.uid,dict(action=action,step=step,**other))
 def complete(self):
  for i in range(5):self.act('tutorial_next',i)
  self.act('tutorial_finish',5)
 def test_new_profile_and_step_resume_after_restart(self):
  self.assertFalse(self.state()['tutorial']['completed']);self.act('tutorial_next',0);self.act('tutorial_next',1)
  self.a=Activity(self.a.path);self.assertEqual(self.a.session(self.token)[0][0],self.uid);self.assertEqual(self.state()['tutorial']['step'],2)
 def test_reward_exactly_once_after_replay_and_restart(self):
  self.complete();s=self.state();self.assertEqual(s['balance']['wallet'],100);self.assertEqual(s['xp'],25);self.assertTrue(s['tutorial']['reward_claimed'])
  self.act('tutorial_finish',5);self.a=Activity(self.a.path);self.act('tutorial_replay');self.complete();again=self.state();self.assertEqual(again['balance'],s['balance']);self.assertEqual(again['xp'],s['xp'])
 def test_no_skipping_or_client_chosen_reward(self):
  self.act('tutorial_next',4);self.assertEqual(self.state()['tutorial']['step'],0)
  with self.assertRaises(ValueError):self.act('tutorial_finish',0)
  for step in [True,-1,6,1.5,'1',None]:
   with self.assertRaises(ValueError):self.act('tutorial_next',step)
  for i in range(5):self.act('tutorial_next',i)
  self.act('tutorial_finish',5,gold=99999,xp=99999);self.assertEqual(self.state()['balance']['wallet'],100);self.assertEqual(self.state()['xp'],25)
 def test_concurrent_duplicate_steps_and_finishes(self):
  with ThreadPoolExecutor(4) as pool:list(pool.map(lambda _:self.act('tutorial_next',0),range(4)))
  self.assertEqual(self.state()['tutorial']['step'],1)
  for i in range(1,5):self.act('tutorial_next',i)
  with ThreadPoolExecutor(4) as pool:list(pool.map(lambda _:self.act('tutorial_finish',5),range(4)))
  self.assertEqual(self.state()['balance']['wallet'],100);self.assertEqual(self.state()['xp'],25)
 def test_cannot_cancel_or_replay_before_completion(self):
  for action in ['tutorial_cancel','tutorial_replay']:
   with self.assertRaises(ValueError):self.act(action)
  self.complete();self.act('tutorial_replay');self.act('tutorial_next',0);self.act('tutorial_cancel');self.assertFalse(self.state()['tutorial']['replay']);self.assertTrue(self.state()['tutorial']['completed'])
 def test_other_profile_is_independent_and_legacy_completion_is_kept(self):
  self.complete();(uid,name),_=self.a.session('');other=self.a.snapshot(uid,name);self.assertFalse(other['tutorial']['completed']);self.assertEqual(other['balance']['wallet'],0)
  with self.a.conn() as c:c.execute('UPDATE tutorial_progress SET completed=1,reward_claimed=1 WHERE user_id=?',(uid,))
  self.a.action(uid,dict(action='tutorial_replay'))
  for i in range(5):self.a.action(uid,dict(action='tutorial_next',step=i))
  self.a.action(uid,dict(action='tutorial_finish',step=5));self.assertEqual(self.a.snapshot(uid,name)['balance']['wallet'],0)
 def test_reward_transaction_rolls_back_on_error(self):
  for i in range(5):self.act('tutorial_next',i)
  original=self.a.castle._sync_level
  def fail(*args):raise RuntimeError('simulated error')
  self.a.castle._sync_level=fail
  with self.assertRaises(RuntimeError):self.act('tutorial_finish',5)
  self.a.castle._sync_level=original;s=self.state();self.assertEqual(s['balance']['wallet'],0);self.assertEqual(s['xp'],0);self.assertFalse(s['tutorial']['completed']);self.act('tutorial_finish',5);self.assertEqual(self.state()['balance']['wallet'],100)
