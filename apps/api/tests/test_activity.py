import unittest,tempfile,sys,time,os
from pathlib import Path
from unittest.mock import patch
sys.path.insert(0,str(Path(__file__).parents[1]))
from activity import Activity
class ActivityTests(unittest.TestCase):
 def setUp(self):
  self.tmp=tempfile.TemporaryDirectory();self.a=Activity(self.tmp.name+'/test.sqlite3');(self.uid,self.name),self.token=self.a.session('');self.a.snapshot(self.uid,self.name)
 def tearDown(self):self.tmp.cleanup()
 def snapshot(self):return self.a.snapshot(self.uid,self.name)
 def act(self,**body):return self.a.action(self.uid,body)
 def test_daily_only_once_and_session_survives_restart(self):
  self.act(action='daily');self.act(action='daily');s=self.snapshot();self.assertEqual(s['balance']['wallet'],200);self.assertEqual(s['xp'],20)
  restored=Activity(self.a.path);self.assertEqual(restored.session(self.token)[0][0],self.uid)
  (other,_),_=restored.session('');self.assertNotEqual(other,self.uid)
 def test_bank_conserves_fortune_and_rejects_invalid(self):
  self.act(action='daily');self.act(action='deposit',amount=150);self.assertEqual(self.snapshot()['balance']['bank'],150)
  self.act(action='withdraw',amount=50);s=self.snapshot();self.assertEqual(s['balance']['wallet']+s['balance']['bank'],200)
  for amount in [-1,0,1.5,True,'10']:
   with self.assertRaises(ValueError):self.act(action='deposit',amount=amount)
 def test_purchase_once_upgrade_checks_level(self):
  with self.a.conn() as c:c.execute('UPDATE players SET wallet_gold=1200 WHERE user_id=?',(self.uid,))
  self.act(action='buy',key='axe');self.act(action='buy',key='axe');self.assertEqual(self.snapshot()['balance']['wallet'],800)
  self.act(action='upgrade',key='axe');self.assertEqual(self.snapshot()['gear']['axe_level'],1)
 def test_expediton_restart_and_exactly_once_loot_and_xp(self):
  self.act(action='start',key='elarwyn_foraging',tool='hands');run=self.a.expeditions.active_run(self.uid)
  self.assertIsNotNone(run);self.assertNotIn('loot',self.snapshot()['active'])
  self.act(action='start',key='elarwyn_foraging',tool='hands');self.assertEqual(self.a.expeditions.active_run(self.uid).run_id,run.run_id)
  with self.a.conn() as c:c.execute('UPDATE expedition_runs SET ends_at=? WHERE run_id=?',(int(time.time())-1,run.run_id))
  self.a=Activity(self.a.path);one=self.snapshot();two=self.snapshot();self.assertIsNone(one['active']);self.assertEqual(one['resources'],run.loot);self.assertEqual(two['resources'],one['resources']);self.assertEqual(two['xp'],15)
 def test_contract_no_early_or_duplicate_reward(self):
  board=self.snapshot()['board'];job=board['jobs'][0]
  self.act(action='job_accept',batch=board['batch_id'],key=job['job_id']);self.act(action='job_claim');self.assertEqual(self.snapshot()['balance']['wallet'],0)
  with self.a.conn() as c:c.execute('UPDATE job_board_state SET reward_ready_at=0 WHERE user_id=?',(self.uid,))
  self.act(action='job_claim');first=self.snapshot();self.act(action='job_claim');second=self.snapshot();self.assertEqual(first['balance']['wallet'],job['reward']);self.assertEqual(first['xp'],second['xp']);self.assertEqual(first['balance'],second['balance'])
 def test_sell_exact_quantity_and_reject_overdraw(self):
  self.a.expeditions.add_resources(self.uid,{'Bois de chêne':7})
  self.act(action='sell',key='Bois de chêne',amount=3)
  s=self.snapshot();self.assertEqual(s['resources']['Bois de chêne'],4);self.assertEqual(s['balance']['wallet'],6)
  self.act(action='sell',key='Bois de chêne',amount=5)
  s=self.snapshot();self.assertEqual(s['resources']['Bois de chêne'],4);self.assertEqual(s['balance']['wallet'],6)
  self.act(action='sell',key='Bois de chêne',amount=4)
  self.assertNotIn('Bois de chêne',self.snapshot()['resources']);self.assertEqual(self.snapshot()['balance']['wallet'],14)
 def test_locked_chapter_cannot_be_read(self):
  with self.assertRaises(ValueError):self.act(action='story_read',chapter=2)
  self.assertIn('Voyageur',self.act(action='story_read',chapter=1))
 def test_shared_wallet_refused_in_test_mode(self):
  with patch.dict(os.environ,{'ECONOMY_DATABASE_URL':'postgresql://example'}):
   with self.assertRaises(RuntimeError):Activity(self.a.path)

 def test_story_market_chapter_advances_with_collection(self):
  s=self.snapshot();self.assertEqual({i['chapter'] for i in s['story_items']},{2})
  with self.a.conn() as c:c.execute('UPDATE players SET wallet_gold=10000 WHERE user_id=?',(self.uid,))
  for item in s['story_items']:self.act(action='story_buy',key=item['name'])
  following=self.snapshot()['story_items'];self.assertEqual(len(following),4);self.assertEqual({i['chapter'] for i in following},{3})

if __name__=='__main__':unittest.main()

from aiohttp.test_utils import TestClient,TestServer
from aiohttp import web
import activity as adapter
class ActivityHttpTests(unittest.IsolatedAsyncioTestCase):
 async def asyncSetUp(self):
  self.tmp=tempfile.TemporaryDirectory();self.previous=adapter.SERVICE;adapter.SERVICE=Activity(self.tmp.name+'/http.sqlite3')
  app=web.Application();app.router.add_get('/api/activity',adapter.activity);app.router.add_post('/api/activity',adapter.activity)
  self.client=TestClient(TestServer(app));await self.client.start_server()
 async def asyncTearDown(self):
  await self.client.close();adapter.SERVICE=self.previous;self.tmp.cleanup()
 async def test_cookie_state_reward_and_csrf(self):
  r=await self.client.get('/api/activity');self.assertEqual(r.status,200);self.assertIn('altherya_test',r.cookies)
  r=await self.client.post('/api/activity',json={'action':'daily'});self.assertEqual(r.status,403)
  for _ in range(2):
   r=await self.client.post('/api/activity',json={'action':'daily'},headers={'X-Altherya-Request':'1'});self.assertEqual(r.status,200);self.assertEqual((await r.json())['state']['balance']['wallet'],200)
 async def test_malformed_action_has_clear_error(self):
  r=await self.client.post('/api/activity',json={'action':'buy','key':[]},headers={'X-Altherya-Request':'1'});self.assertEqual(r.status,400);self.assertIn('error',await r.json())
