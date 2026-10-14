import os,sqlite3,unittest,tempfile,sys
from pathlib import Path
from unittest.mock import patch
from concurrent.futures import ThreadPoolExecutor
sys.path.insert(0,str(Path(__file__).parents[1]))
from activity import Activity
USER={'id':'123456789012345678','username':'testeur','global_name':'Voyageur','avatar':None,'discriminator':'0'}
class TutorialIdentityTests(unittest.TestCase):
 def setUp(self):
  self.tmp=tempfile.TemporaryDirectory();self.path=self.tmp.name+'/test.db';self.a=Activity(self.path);self.uid,self.token=self.new()
 def tearDown(self):self.tmp.cleanup()
 def new(self):
  (uid,name),token=self.a.session('');self.a.snapshot(uid,name);return uid,token
 def finish(self,uid):
  for i in range(5):self.a.action(uid,{'action':'tutorial_next','step':i})
  self.a.action(uid,{'action':'tutorial_finish','step':5})
 def test_gameplay_blocked_until_tutorial_complete(self):
  for action in ['daily','buy','deposit','game','battle','start']:
   with self.assertRaisesRegex(ValueError,'tutoriel'):self.a.action(self.uid,{'action':action})
  self.assertEqual(self.a.snapshot(self.uid,'Test')['balance']['wallet'],0)
 def test_production_requires_verified_discord(self):
  with patch.dict(os.environ,{'DISCORD_CLIENT_ID':'test','DISCORD_CLIENT_SECRET':'test'}):
   with self.assertRaisesRegex(ValueError,'Discord'):self.finish(self.uid)
   self.a.bind_discord(self.uid,USER,self.token);self.finish(self.uid)
  with self.a.conn() as c:r=c.execute('SELECT * FROM activity_tutorial_receipts').fetchone()
  self.assertEqual(r['identity_key'],'discord:'+USER['id']);self.assertEqual(r['discord_id'],USER['id']);self.assertEqual((r['gold_paid'],r['xp_paid']),(100,25));self.assertTrue(r['claimed_at'])
 def test_new_device_and_restart_keep_same_profile_and_reward(self):
  self.a.bind_discord(self.uid,USER,self.token);self.finish(self.uid)
  other,token=self.new();target=self.a.bind_discord(other,USER,token);self.assertEqual(target,self.uid)
  self.a=Activity(self.path);self.assertEqual(self.a.session_uid(token),self.uid);self.assertEqual(self.a.session_uid(self.token),self.uid)
  self.finish(target);s=self.a.snapshot(target,'Test');self.assertTrue(s['tutorial']['completed']);self.assertEqual((s['balance']['wallet'],s['xp']),(100,25))
 def test_simultaneous_devices_share_identity_and_single_reward(self):
  devices=[(self.uid,self.token),self.new(),self.new()]
  with ThreadPoolExecutor(3) as p:uids=list(p.map(lambda x:self.a.bind_discord(x[0],USER,x[1]),devices))
  self.assertEqual(len(set(uids)),1);uid=uids[0]
  for i in range(5):self.a.action(uid,{'action':'tutorial_next','step':i})
  with ThreadPoolExecutor(3) as p:list(p.map(lambda _:self.a.action(uid,{'action':'tutorial_finish','step':5}),range(3)))
  s=self.a.snapshot(uid,'Test');self.assertEqual((s['balance']['wallet'],s['xp']),(100,25))
 def test_switching_account_does_not_switch_other_device(self):
  self.a.bind_discord(self.uid,USER,self.token);self.finish(self.uid);other,token=self.new();self.a.bind_discord(other,USER,token)
  second=self.a.bind_discord(self.uid,{**USER,'id':'223456789012345678'},token)
  self.assertNotEqual(second,self.uid);self.assertEqual(self.a.session_uid(self.token),self.uid);self.assertEqual(self.a.session_uid(token),second)
  s=self.a.snapshot(second,'Test');self.assertFalse(s['tutorial']['completed']);self.assertEqual(s['balance']['wallet'],0)
 def test_receipt_prevents_repayment_if_progress_flags_reset(self):
  self.a.bind_discord(self.uid,USER,self.token);self.finish(self.uid)
  with self.a.conn() as c:c.execute('UPDATE tutorial_progress SET completed=0,reward_claimed=0,gold_claimed=0,xp_claimed=0 WHERE user_id=?',(self.uid,))
  self.assertTrue(self.a.snapshot(self.uid,'Test')['tutorial']['completed']);self.finish(self.uid)
  self.assertEqual(self.a.snapshot(self.uid,'Test')['balance']['wallet'],100)
 def test_old_unique_session_schema_migrates_without_losing_token(self):
  with self.a.conn() as c:
   c.execute('DROP INDEX activity_sessions_user');c.execute('ALTER TABLE activity_sessions RENAME TO sessions_old');c.execute('CREATE TABLE activity_sessions(token TEXT PRIMARY KEY,user_id INTEGER UNIQUE,name TEXT NOT NULL)');c.execute('INSERT INTO activity_sessions SELECT * FROM sessions_old');c.execute('DROP TABLE sessions_old')
  self.a=Activity(self.path);self.assertEqual(self.a.session_uid(self.token),self.uid)
  self.a.bind_discord(self.uid,USER,self.token);other,token=self.new();self.a.bind_discord(other,USER,token);self.assertEqual(self.a.session_uid(token),self.uid)
