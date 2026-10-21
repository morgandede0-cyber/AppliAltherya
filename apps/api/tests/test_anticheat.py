"""Adversarial tests: concurrent devices, replay, forged data and time boundaries."""
import json,random as test_random,tempfile,time,unittest,uuid,sys,os
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
from unittest.mock import patch
sys.path.insert(0,str(Path(__file__).parents[1]))
from activity import Activity
from campaign import QUESTS
from secure_random import random as outcomes
USER=dict(id='123456789012345678',username='audit',global_name='Audit',avatar=None,discriminator='0')
class AntiCheatTests(unittest.TestCase):
 def setUp(self):
  self.tmp=tempfile.TemporaryDirectory();self.a=Activity(self.tmp.name+'/test.db');(self.uid,self.name),self.token=self.a.session('');self.a.snapshot(self.uid,self.name)
  with self.a.conn() as c:
   c.execute('UPDATE tutorial_progress SET completed=1 WHERE user_id=?',(self.uid,));c.execute('UPDATE activity_tutorial_revision SET finished=1 WHERE user_id=?',(self.uid,));c.execute('UPDATE players SET wallet_gold=1000 WHERE user_id=?',(self.uid,))
 def tearDown(self):self.tmp.cleanup()
 def wallet(self):return self.a.economy.get_balance(self.uid)
 def concurrent(self,body,n=24):
  def invoke(i):
   try:return self.a.action(self.uid,{**body,'request_id':str(uuid.uuid4())})
   except ValueError:return None
  with ThreadPoolExecutor(max_workers=8) as pool:return list(pool.map(invoke,range(n)))
 def test_concurrent_deposits_cannot_spend_one_wallet_twice(self):
  self.concurrent(dict(action='deposit',amount=70));b=self.wallet();self.assertEqual((b.wallet,b.bank),(20,980))
 def test_concurrent_withdrawals_have_one_free_withdrawal(self):
  with self.a.conn() as c:c.execute('UPDATE players SET wallet_gold=0,bank_gold=1000 WHERE user_id=?',(self.uid,))
  self.concurrent(dict(action='withdraw',amount=100));b=self.wallet();self.assertEqual((b.wallet,b.bank),(955,0))
 def test_same_request_replayed_by_24_threads_pays_once(self):
  body=dict(action='deposit',amount=30,request_id=str(uuid.uuid4()))
  with ThreadPoolExecutor(max_workers=8) as pool:list(pool.map(lambda _:self.a.action(self.uid,dict(body)),range(24)))
  self.assertEqual(self.wallet().bank,30)
  for _ in range(25):self.a.action(self.uid,dict(body))
  self.assertEqual(self.wallet().bank,30)
  with self.assertRaises(ValueError):self.a.action(self.uid,{**body,'amount':300})
 def test_model_2000_transactions_including_replays_and_invalid_amounts(self):
  rng=test_random.Random(4217);wallet,bank,free=1000,0,True;past=[]
  for i in range(2000):
   if past and i%7==0:
    self.a.action(self.uid,dict(rng.choice(past)))
   else:
    action=rng.choice(['deposit','withdraw']);n=rng.choice([1,2,7,20,70,500,1001,0,-1,True,1.25,'10',10**30]);body=dict(action=action,amount=n,request_id=str(uuid.uuid4()))
    if type(n) is int and 1<=n<=10**9:
     self.a.action(self.uid,body);past.append(body)
     if action=='deposit' and wallet>=n:wallet-=n;bank+=n
     elif action=='withdraw' and bank>=n:
      fee=0 if free else max(1,n*5//100);wallet+=n-fee;bank-=n;free=False
    else:
     with self.assertRaises(ValueError):self.a.action(self.uid,body)
   b=self.wallet();self.assertEqual((b.wallet,b.bank),(wallet,bank),f'operation {i}')
 def test_repeated_daily_reward_from_different_devices_pays_once(self):
  self.concurrent(dict(action='daily'));self.assertEqual(self.wallet().wallet,1010);self.assertEqual(self.a.castle.profile(self.uid)['xp'],20)
 def test_client_day_and_reward_fields_do_not_choose_a_daily_reward(self):
  for day in ['2099-12-31','1900-01-01','2026-01-01']:
   self.a.action(self.uid,dict(action='daily',day=day,server_now=10**15,gold=10**9,xp=10**9,completed=True))
  self.assertEqual(self.wallet().wallet,1010);self.assertEqual(self.a.castle.profile(self.uid)['xp'],20)
 def test_midnight_and_server_clock_rollback_cannot_repay_the_same_day(self):
  for day in ['2026-10-21','2026-10-22','2026-10-21','2026-10-22']:
   with patch.object(self.a.castle,'_today',return_value=day):self.a.action(self.uid,dict(action='daily'))
  self.assertEqual(self.wallet().wallet,1020);self.assertEqual(self.a.castle.profile(self.uid)['xp'],40)
 def test_concurrent_purchase_delivers_one_item_at_the_server_price(self):
  self.concurrent(dict(action='buy',key='axe',price=0,cost=-999,quantity=999,gold=999999))
  self.assertEqual(self.wallet().wallet,600);self.assertTrue(self.a.expeditions.owned_equipment(self.uid)['axe'])
 def test_concurrent_sales_cannot_sell_one_inventory_twice(self):
  self.a.expeditions.add_resources(self.uid,{'Bois de chêne':7})
  self.concurrent(dict(action='sell',key='Bois de chêne',amount=7,price=10**9));self.assertEqual(self.wallet().wallet,1014);self.assertEqual(self.a.expeditions.get_resources(self.uid).get('Bois de chêne',0),0)
 def test_concurrent_bets_on_one_revision_debit_and_resolve_once(self):
  rev=self.a.play.read(self.uid)[0]
  with patch('play.flip_coin',return_value='pile'):
   results=self.concurrent(dict(action='game_start',key='coin',choice='pile',wager=10,revision=rev,payout=10**9,winner=True,xp=10**9))
  self.assertEqual(sum(r is not None for r in results),1);self.assertEqual(self.wallet().wallet,1010);self.assertEqual(self.a.castle.profile(self.uid)['xp'],5)
 def test_forged_winning_outcome_does_not_replace_a_losing_server_result(self):
  with patch('play.flip_coin',return_value='face'):
   self.a.action(self.uid,dict(action='game_start',key='coin',choice='pile',wager=10,revision=0,payout=10**9,winner=True,outcome='victory'))
  p=self.a.play.public(self.uid);self.assertEqual(p['payout'],0);self.assertEqual(self.wallet().wallet,990)
 def test_pending_contract_cannot_be_rerolled_by_accepting_all_eight_offers(self):
  board=self.a.snapshot(self.uid,self.name)['board']
  for offer in board['jobs']:self.a.action(self.uid,dict(action='job_accept',key=offer['job_id'],batch=board['batch_id']))
  with self.a.conn() as c:
   row=c.execute('SELECT accepted_total,pending_job_json FROM job_board_state WHERE user_id=?',(self.uid,)).fetchone()
  self.assertEqual(row[0],1);self.assertEqual(json.loads(row[1])['job_id'],board['jobs'][0]['job_id'])
 def test_contract_server_clock_and_concurrent_claim(self):
  board=self.a.snapshot(self.uid,self.name)['board'];self.a.action(self.uid,dict(action='job_accept',key=board['jobs'][0]['job_id'],batch=board['batch_id']))
  self.concurrent(dict(action='job_claim',ready=True,remaining=0,reward=10**9,server_now=10**15));self.assertEqual(self.wallet().wallet,1000)
  with self.a.conn() as c:
   row=c.execute('SELECT pending_job_json FROM job_board_state WHERE user_id=?',(self.uid,)).fetchone();reward=json.loads(row[0])['reward'];c.execute('UPDATE job_board_state SET reward_ready_at=0 WHERE user_id=?',(self.uid,))
  self.concurrent(dict(action='job_claim',reward=10**9));self.assertEqual(self.wallet().wallet,1000+reward)
 def test_expedition_start_race_and_forged_finish_time(self):
  self.concurrent(dict(action='start',key='elarwyn_foraging',tool='hands',ends_at=0,remaining=0,loot={'Diamant':10000}))
  with self.a.conn() as c:self.assertEqual(c.execute('SELECT COUNT(*) FROM expedition_runs WHERE user_id=?',(self.uid,)).fetchone()[0],1)
  run=self.a.expeditions.active_run(self.uid);self.assertGreater(run.ends_at,time.time());self.a.reconcile(self.uid);self.assertEqual(self.a.expeditions.get_resources(self.uid),{})
 def test_campaign_reward_cannot_be_claimed_twice_or_overridden(self):
  q=QUESTS[0]
  with self.a.conn() as c:c.execute('UPDATE campaign_progress SET stage=?,accepted_at=?,payload=? WHERE user_id=?',(len(q['steps']),time.time()-10000,json.dumps({'edition':2}),self.uid))
  self.concurrent(dict(action='campaign_claim',quest_id=q['id'],revision=0,gold=10**9,xp=10**9))
  self.assertEqual(self.wallet().wallet,1000+q['gold']);self.assertEqual(self.a.castle.profile(self.uid)['xp'],q['xp'])
 def test_other_player_ids_and_admin_fields_do_not_change_the_actor(self):
  (other,name),_=self.a.session('');self.a.snapshot(other,name)
  self.a.action(self.uid,dict(action='deposit',amount=10,user_id=other,discord_id='666805849011912705',admin=True,player=other))
  self.assertEqual(self.wallet().bank,10);self.assertEqual(self.a.economy.get_balance(other).bank,0);self.assertFalse(self.a.admin.allowed(self.uid))
 def test_unowned_or_retired_techniques_cannot_be_forged(self):
  before=self.a.play.technique_book(self.uid)['skills']
  for key in ['c10','ashkar_1','ashkar_9','ashkar_10','not-a-technique']:
   with self.assertRaises(ValueError):self.a.action(self.uid,dict(action='arena_equip',slot='ultimate',technique=key,loadout_revision=0,unlocked=True))
  self.assertEqual(self.a.play.technique_book(self.uid)['skills'],before)
 def test_raw_blackjack_and_russian_secrets_never_leave_the_server(self):
  self.a.action(self.uid,dict(action='guard',key='pay'))
  with patch('play.random.shuffle',side_effect=lambda cards:cards.sort(key=lambda c:c['rank']=='A',reverse=True)):
   self.a.action(self.uid,dict(action='game_start',key='blackjack',wager=1,revision=0))
  p=self.a.play.public(self.uid);self.assertNotIn('deck',p);self.assertEqual(p['dealer'][1],{'hidden':True})
  self.a.action(self.uid,dict(action='game_step',key='stand',revision=p['revision']))
  with patch.object(self.a.play,'round_clock',return_value=time.time()+4):self.a.action(self.uid,dict(action='game_start',key='russian',wager=1,revision=self.a.play.read(self.uid)[0]))
  p=self.a.play.public(self.uid);self.assertNotIn('danger',p);self.assertNotIn('code',p)
 def test_outcomes_use_an_os_generator_not_a_cloneable_seeded_state(self):
  import random
  self.assertIsInstance(outcomes,random.SystemRandom)
  with self.assertRaises(NotImplementedError):outcomes.getstate()
  for name in ['play','activity_jobs','arena_engine','casino_engine','tavern_engine','dark_alley','expedition_engine','job_board_engine']:
   module=__import__(name);self.assertIs(module.random,outcomes,name)
 def test_login_rotates_a_fixed_token_and_preserves_other_devices(self):
  self.a.bind_discord(self.uid,USER,self.token)
  (other,_),other_token=self.a.session('');self.a.bind_discord(other,USER,other_token)
  uid,new=self.a.identities.login(self.uid,USER,self.token)
  self.assertEqual(uid,self.uid);self.assertNotEqual(new,self.token);self.assertIsNone(self.a.session_uid(self.token));self.assertEqual(self.a.session_uid(new),self.uid);self.assertEqual(self.a.session_uid(other_token),self.uid);self.assertEqual(self.wallet().wallet,1000)
 def test_login_failure_rolls_back_identity_and_session_together(self):
  with patch('identity.secrets.token_urlsafe',side_effect=RuntimeError('simulated failure')):
   with self.assertRaises(RuntimeError):self.a.identities.login(self.uid,USER,self.token)
  self.assertEqual(self.a.session_uid(self.token),self.uid);self.assertIsNone(self.a.discord_profile(self.uid))
 def test_cleared_legacy_daily_flag_does_not_erase_the_payment_receipt(self):
  self.a.action(self.uid,dict(action='daily'))
  with self.a.conn() as c:c.execute('UPDATE castle_profiles SET last_daily=NULL WHERE user_id=?',(self.uid,))
  self.assertFalse(self.a.castle.daily_available(self.uid));self.a.action(self.uid,dict(action='daily'));self.assertEqual(self.wallet().wallet,1010)
 def test_existing_last_daily_is_migrated_without_repaying(self):
  day=self.a.castle._today()
  with self.a.conn() as c:c.execute('UPDATE castle_profiles SET last_daily=? WHERE user_id=?',(day,self.uid))
  self.a=Activity(self.a.path);self.assertFalse(self.a.castle.daily_available(self.uid));self.a.action(self.uid,dict(action='daily'));self.assertEqual(self.wallet().wallet,1000)

from aiohttp import web
from aiohttp.test_utils import TestClient,TestServer
import activity as adapter
import server
from test_discord_profile import FakeSession
class LoginHttpAntiCheatTests(unittest.IsolatedAsyncioTestCase):
 async def asyncSetUp(self):
  self.tmp=tempfile.TemporaryDirectory();self.old=adapter.SERVICE;self.a=Activity(self.tmp.name+'/http.db');adapter.SERVICE=self.a
  app=web.Application();app.router.add_get('/api/activity',adapter.activity);app.router.add_post('/api/activity',adapter.activity);app.router.add_post('/api/auth/discord',server.auth)
  self.client=TestClient(TestServer(app),headers={'X-Altherya-Request':'1'});await self.client.start_server()
  r=await self.client.get('/api/activity');self.before=r.cookies['altherya_test'].value
 async def asyncTearDown(self):await self.client.close();adapter.SERVICE=self.old;self.tmp.cleanup()
 async def test_http_login_replaces_cookie_and_a_fixed_old_cookie_cannot_read_the_profile(self):
  with patch.dict(os.environ,{'DISCORD_CLIENT_ID':'test','DISCORD_CLIENT_SECRET':'test'}),patch.object(server,'ClientSession',FakeSession):
   r=await self.client.post('/api/auth/discord',json={'code':'verified-code','id':'666805849011912705'});self.assertEqual(r.status,200)
   new=r.cookies['altherya_test'].value;self.assertNotEqual(new,self.before);self.assertIsNone(self.a.session_uid(self.before));self.assertIsNotNone(self.a.session_uid(new))
   state=(await(await self.client.get('/api/activity')).json())['state'];self.assertIsNotNone(state['discord']);self.assertFalse(state['admin'])
   self.client.session.cookie_jar.clear();r=await self.client.get('/api/activity',headers={'Cookie':'altherya_test='+self.before});self.assertIsNone((await r.json())['state']['discord'])
 async def test_network_failure_does_not_rotate_or_bind_the_existing_session(self):
  class Offline(FakeSession):
   async def __aenter__(self):raise server.ClientError('simulated network loss')
  uid=self.a.session_uid(self.before)
  with patch.dict(os.environ,{'DISCORD_CLIENT_ID':'test','DISCORD_CLIENT_SECRET':'test'}),patch.object(server,'ClientSession',Offline):
   r=await self.client.post('/api/auth/discord',json={'code':'test'});self.assertEqual(r.status,502)
  self.assertEqual(self.a.session_uid(self.before),uid);self.assertIsNone(self.a.discord_profile(uid))

class CadenceAntiCheatTests(unittest.TestCase):
 setUp=AntiCheatTests.setUp
 tearDown=AntiCheatTests.tearDown
 wallet=AntiCheatTests.wallet
 def test_reconnect_and_alternating_games_do_not_bypass_the_three_second_server_cadence(self):
  now=time.time()
  with patch.object(self.a.play,'round_clock',return_value=now):self.a.action(self.uid,dict(action='game_start',key='coin',choice='pile',wager=1,revision=0))
  before=self.wallet();xp=self.a.castle.profile(self.uid)['xp'];rev=self.a.play.read(self.uid)[0]
  for key in ['dice','coin','rps']:
   with patch.object(self.a.play,'round_clock',return_value=now+.1):
    with self.assertRaisesRegex(ValueError,'Attendez'):self.a.action(self.uid,dict(action='game_start',key=key,choice='pile' if key=='coin' else 'rock',wager=1,revision=rev,next_round_at=0,server_now=10**15))
  self.a=Activity(self.a.path)
  with patch.object(self.a.play,'round_clock',return_value=now+.1):
   with self.assertRaises(ValueError):self.a.action(self.uid,dict(action='game_start',key='dice',wager=1,revision=rev))
  self.assertEqual(self.wallet(),before);self.assertEqual(self.a.castle.profile(self.uid)['xp'],xp)
  with patch.object(self.a.play,'round_clock',return_value=now+3):self.a.action(self.uid,dict(action='game_start',key='dice',wager=1,revision=rev))
  self.assertEqual(self.a.castle.profile(self.uid)['xp'],xp+5)
 def test_a_thousand_fresh_requests_cannot_farm_xp_at_one_timestamp(self):
  now=time.time()
  with patch.object(self.a.play,'round_clock',return_value=now):
   self.a.action(self.uid,dict(action='game_start',key='coin',choice='pile',wager=1,revision=0));before=self.wallet()
   for _ in range(1000):
    with self.assertRaises(ValueError):self.a.action(self.uid,dict(action='game_start',key='dice',wager=1,revision=1,request_id=str(uuid.uuid4())))
  self.assertEqual(self.a.castle.profile(self.uid)['xp'],5);self.assertEqual(self.wallet(),before)
