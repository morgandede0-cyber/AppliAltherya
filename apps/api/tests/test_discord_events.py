import asyncio,json,os,sys,tempfile,time,unittest
from datetime import datetime
from pathlib import Path
from unittest.mock import patch
from zoneinfo import ZoneInfo
sys.path.insert(0,str(Path(__file__).parents[1]))
from activity import Activity
from discord_events import CHANNELS, notification_worker

class EventsTests(unittest.TestCase):
 def setUp(self):
  self.tmp=tempfile.TemporaryDirectory();self.a=Activity(self.tmp.name+'/db.sqlite3')
  (self.uid,self.name),token=self.a.session('')
  self.a.bind_discord(self.uid,dict(id='666805849011912705',username='test',global_name='Test @everyone',avatar=None,discriminator='0'),token)
  self.s=self.a.snapshot(self.uid,self.name);self.a.notifications.observe(self.uid,self.s)
  with self.a.conn() as c:
   c.execute('UPDATE tutorial_progress SET completed=1 WHERE user_id=?',(self.uid,));c.execute('UPDATE activity_tutorial_revision SET finished=1 WHERE user_id=?',(self.uid,))
  self.a.notifications.observe(self.uid,self.a.snapshot(self.uid,self.name))
  with self.a.conn() as c:c.execute('DELETE FROM activity_discord_outbox')
 def tearDown(self):self.tmp.cleanup()
 def rows(self):
  with self.a.conn() as c:return c.execute('SELECT * FROM activity_discord_outbox ORDER BY rowid').fetchall()
 def test_channel_routes(self):self.assertEqual(CHANNELS,dict(gazette='1551927433475788880',hall='1551927559925538957',logs='1551928091046314117'))
 def test_daily_once_poll_no_spam_and_restart(self):
  self.a.action(self.uid,dict(action='daily'));self.a.action(self.uid,dict(action='daily'))
  for _ in range(3):self.a.notifications.observe(self.uid,self.a.snapshot(self.uid,self.name))
  self.assertEqual(len(self.rows()),1)
  restored=Activity(self.a.path);restored.notifications.observe(self.uid,restored.snapshot(self.uid,self.name));self.assertEqual(len(self.rows()),1)
  p=json.loads(self.rows()[0]['payload']);self.assertEqual(p['allowed_mentions'],{'parse':[]});self.assertNotIn('@everyone',p['embeds'][0]['description'])
 def test_repeated_same_bank_transitions_are_distinct(self):
  self.a.action(self.uid,dict(action='daily'))
  for action in ('deposit','withdraw','deposit','withdraw'):self.a.action(self.uid,dict(action=action,amount=10))
  self.assertEqual(len(self.rows()),5)
 def test_rejected_action_no_event(self):
  with self.assertRaises(ValueError):self.a.action(self.uid,dict(action='deposit',amount=-1))
  self.assertEqual(len(self.rows()),0)
 def test_timer_poll_no_spam(self):
  self.a.play.dark.enter_clandestine_room(self.uid,False)
  s=self.a.snapshot(self.uid,self.name);self.a.notifications.observe(self.uid,s)
  with self.a.conn() as c:c.execute('DELETE FROM activity_discord_outbox')
  s['alley']['access']['seconds_left']=123;self.a.notifications.observe(self.uid,s)
  self.assertEqual(len(self.rows()),0)
 def test_game_result_unique_and_net_not_payout(self):
  s=self.a.snapshot(self.uid,self.name);s['play']=dict(kind='coin',status='finished',session='fixture-session',revision=1,wager=10,payout=20,message='Victoire')
  self.a.notifications.observe(self.uid,s,'game_start','Victoire');self.a.notifications.observe(self.uid,s)
  with self.a.conn() as c:r=c.execute('SELECT * FROM activity_discord_game_results').fetchall()
  self.assertEqual(len(r),1);self.assertEqual(r[0]['net'],10)
  self.assertEqual(sum(r['channel']=='hall' for r in self.rows()),1)
 def test_gazette_day_boundary_and_dedup(self):
  now=datetime(2026,10,27,9,tzinfo=ZoneInfo('Europe/Paris'))
  with self.a.conn() as c:
   c.execute('UPDATE activity_discord_meta SET value=? WHERE key="installed"',(str(now.timestamp()-172800),))
   c.execute('INSERT INTO activity_discord_game_results VALUES(?,?,?,?,?)',('x','1','Gagnant',50,now.timestamp()-36000))
   c.execute('INSERT INTO activity_discord_game_results VALUES(?,?,?,?,?)',('y','2','Perdant',-30,now.timestamp()-35000))
  self.a.notifications.gazette(now.replace(hour=8));self.assertEqual(len(self.rows()),0)
  self.a.notifications.gazette(now);self.a.notifications.gazette(now)
  self.assertEqual(len(self.rows()),1);r=self.rows()[0];self.assertEqual(r['channel'],'gazette');self.assertIn('Gagnant',r['payload']);self.assertIn('Perdant',r['payload'])
 def test_admin_same_transaction_rollback(self):
  try:
   with self.a.conn() as c:
    self.a.notifications.admin_event(c,'id','admin','target','wallet',1,2,'motif');raise ValueError()
  except ValueError:pass
  self.assertEqual(len(self.rows()),0)
 def test_level_xp_delta_uses_total_not_progress_bar(self):
  s=self.a.snapshot(self.uid,self.name);s['stats']['xp']=125;s['xp']=25;s['level']=2
  self.a.notifications.observe(self.uid,s,'daily','Récompense')
  logs=[json.loads(r['payload']) for r in self.rows() if r['channel']=='logs']
  self.assertIn('XP : +125',logs[0]['embeds'][0]['description'])
 def test_offline_expedition_finalized_and_announced(self):
  self.a.action(self.uid,dict(action='start',key='elarwyn_foraging',tool='hands'))
  with self.a.conn() as c:c.execute('UPDATE expedition_runs SET ends_at=0 WHERE user_id=?',(self.uid,))
  with patch.dict(os.environ,{'DISCORD_BOT_TOKEN':''}),patch('discord_events.asyncio.sleep',side_effect=asyncio.CancelledError):
   with self.assertRaises(asyncio.CancelledError):asyncio.run(notification_worker(self.a))
  self.assertTrue(any('Expédition terminée' in r['payload'] for r in self.rows()))
  self.assertIsNone(self.a.snapshot(self.uid,self.name)['active'])
 def test_guest_no_public_events(self):
  (uid,name),_=self.a.session('');s=self.a.snapshot(uid,name);self.a.notifications.observe(uid,s)
  self.assertEqual(len(self.rows()),0)

class FakeResponse:
 def __init__(self,status,data):self.status=status;self.data=data;self.headers={}
 async def __aenter__(self):return self
 async def __aexit__(self,*args):pass
 async def json(self):return self.data
class FakeSession:
 def __init__(self,status=200,data=None):self.status=status;self.data=data or {'id':'123'};self.calls=[]
 def post(self,*args,**kwargs):self.calls.append((args,kwargs));return FakeResponse(self.status,self.data)

class DeliveryTests(unittest.IsolatedAsyncioTestCase):
 async def asyncSetUp(self):
  self.tmp=tempfile.TemporaryDirectory();self.a=Activity(self.tmp.name+'/db')
  with self.a.conn() as c:self.a.notifications.enqueue(c,'key','logs','Titre','Texte')
 async def asyncTearDown(self):self.tmp.cleanup()
 def row(self):
  with self.a.conn() as c:return c.execute('SELECT * FROM activity_discord_outbox').fetchone()
 async def test_send_ack_restart_no_resend(self):
  fake=FakeSession();await self.a.notifications.deliver_one(fake,'FAKE')
  self.assertIsNotNone(self.row()['sent']);self.assertEqual(len(fake.calls),1)
  await self.a.notifications.deliver_one(fake,'FAKE');self.assertEqual(len(fake.calls),1)
  self.assertTrue(fake.calls[0][1]['json']['enforce_nonce']);self.assertIn(CHANNELS['logs'],fake.calls[0][0][0])
 async def test_429_retained_and_retry_after(self):
  fake=FakeSession(429,{'retry_after':20});now=time.time();delay=await self.a.notifications.deliver_one(fake,'FAKE',now)
  self.assertEqual(delay,20);self.assertEqual(self.row()['ready'],now+20);self.assertIsNone(self.row()['sent'])
 async def test_forbidden_retained_no_tight_loop(self):
  fake=FakeSession(403);now=time.time();await self.a.notifications.deliver_one(fake,'FAKE',now)
  self.assertEqual(self.row()['ready'],now+3600);self.assertEqual(self.row()['last_error'],'Discord HTTP 403')
 async def test_forbidden_blocks_channel_backlog(self):
  with self.a.conn() as c:self.a.notifications.enqueue(c,'key2','logs','Deux','Texte')
  fake=FakeSession(403);now=time.time();await self.a.notifications.deliver_one(fake,'FAKE',now)
  await self.a.notifications.deliver_one(fake,'FAKE',now+1);self.assertEqual(len(fake.calls),1)
 async def test_unauthorized_pauses_all_channels(self):
  with self.a.conn() as c:self.a.notifications.enqueue(c,'key2','hall','Deux','Texte')
  fake=FakeSession(401);now=time.time();await self.a.notifications.deliver_one(fake,'FAKE',now)
  await self.a.notifications.deliver_one(fake,'FAKE',now+1);self.assertEqual(len(fake.calls),1)
 async def test_timeout_retries_same_nonce(self):
  fake=FakeSession(500);await self.a.notifications.deliver_one(fake,'FAKE',time.time()-10)
  success=FakeSession();await self.a.notifications.deliver_one(success,'FAKE')
  self.assertEqual(fake.calls[0][1]['json']['nonce'],success.calls[0][1]['json']['nonce'])
 async def test_multi_worker_claim(self):
  one,two=FakeSession(),FakeSession()
  await asyncio.gather(self.a.notifications.deliver_one(one,'FAKE'),self.a.notifications.deliver_one(two,'FAKE'))
  self.assertEqual(len(one.calls)+len(two.calls),1)

if __name__=='__main__':unittest.main()
