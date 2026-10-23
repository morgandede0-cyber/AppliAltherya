import sys,tempfile,unittest
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
from unittest.mock import patch
sys.path.insert(0,str(Path(__file__).parents[1]))
from activity import Activity
ADMIN='666805849011912705';PLAYER='123456789012345678';OTHER='123456789012345679'
class MailTests(unittest.TestCase):
 def setUp(self):
  self.tmp=tempfile.TemporaryDirectory();self.path=self.tmp.name+'/test.db';self.a=Activity(self.path);self.admin=self.make(ADMIN);self.player=self.make(PLAYER);self.other=self.make(OTHER)
 def tearDown(self):self.tmp.cleanup()
 def make(self,did,done=True):
  (uid,name),token=self.a.session('');self.a.snapshot(uid,name);self.a.bind_discord(uid,dict(id=did,username='Test',global_name='Test',avatar=None,discriminator='0'),token)
  if done:
   for n in range(5):self.a.action(uid,dict(action='tutorial_next',step=n))
   self.a.action(uid,dict(action='tutorial_finish',step=5))
  return uid
 def args(self,**kw):return dict(title='Un cadeau de l’intendance',text='Merci pour votre aventure.',gold=7,xp=3,pouciel=2,item='none',quantity=0,**kw)
 def send(self,args=None,cmd='mail_player',confirm=True):
  p=self.a.admin_commands.preview(self.admin,dict(command=cmd,player=PLAYER,args=args or self.args(),reason='Récompense de test'))
  if confirm:self.a.admin_commands.confirm(self.admin,p['token'])
  return p
 def mail(self,uid=None):return self.a.mailbox.listing(uid or self.player,0)['entries'][0]
 def claim(self,mid,uid=None):return self.a.action(uid or self.player,dict(action='mail_claim',key=mid))
 def test_send_requires_admin_preview_and_does_not_credit_before_claim(self):
  before=self.a.economy.get_balance(self.player).wallet;p=self.send(confirm=False);self.assertEqual(self.a.mailbox.counts(self.player)['total'],0)
  with self.assertRaises(PermissionError):self.a.admin_commands.confirm(self.player,p['token'])
  self.a.admin_commands.confirm(self.admin,p['token']);self.assertEqual(self.a.economy.get_balance(self.player).wallet,before);self.assertEqual(self.a.mailbox.counts(self.player)['unread'],1)
 def test_concurrent_claims_different_request_ids_are_paid_once(self):
  self.send();mid=self.mail()['id'];before=self.a.snapshot(self.player,'Test')
  with ThreadPoolExecutor(4) as pool:list(pool.map(lambda _:self.claim(mid),range(4)))
  after=self.a.snapshot(self.player,'Test');self.assertEqual(after['balance']['wallet'],before['balance']['wallet']+7);self.assertEqual(after['xp'],before['xp']+3);self.assertEqual(after['khaz']['pouciel'],2);self.assertEqual(after['mail']['attention'],0)
 def test_other_player_cannot_read_claim_or_archive_letter(self):
  self.send();mid=self.mail()['id'];self.assertEqual(self.a.mailbox.listing(self.other,0)['entries'],[])
  for action in ('mail_read','mail_claim','mail_archive'):
   with self.assertRaises(ValueError):self.a.action(self.other,dict(action=action,key=mid))
  self.assertEqual(self.a.mailbox.counts(self.player)['unread'],1)
 def test_collective_recipients_are_canonical_finished_accounts_at_send_time(self):
  self.make('123456789012345680',False);p=self.send(cmd='mail_all');self.assertEqual(p['affected'],3);self.assertIsNone(p['player']);self.assertEqual(self.a.admin_commands.history()['entries'][0]['target'],'*')
  for uid in (self.admin,self.player,self.other):self.assertEqual(self.a.mailbox.counts(uid)['total'],1)
  self.a.admin_commands.confirm(self.admin,p['token']);self.assertEqual(self.a.mailbox.counts(self.player)['total'],1)
  later=self.make('123456789012345681');self.assertEqual(self.a.mailbox.counts(later)['total'],0)
 def test_broadcast_preview_is_invalid_when_registry_changes(self):
  p=self.send(cmd='mail_all',confirm=False);self.make('123456789012345680')
  with self.assertRaises(ValueError):self.a.admin_commands.confirm(self.admin,p['token'])
  self.assertEqual(self.a.mailbox.counts(self.player)['total'],0)
 def test_reward_receipt_survives_read_archive_and_restart(self):
  self.send();mid=self.mail()['id'];self.a.action(self.player,dict(action='mail_read',key=mid));self.assertEqual(self.a.mailbox.counts(self.player)['unclaimed'],1)
  with self.assertRaises(ValueError):self.a.action(self.player,dict(action='mail_archive',key=mid))
  self.claim(mid);self.a=Activity(self.path);before=self.a.economy.get_balance(self.player).wallet;self.claim(mid);self.assertEqual(self.a.economy.get_balance(self.player).wallet,before)
  self.a.action(self.player,dict(action='mail_archive',key=mid));self.assertEqual(self.a.mailbox.counts(self.player)['total'],0)
  with self.assertRaises(ValueError):self.claim(mid)
  with self.a.conn() as c:self.assertIsNotNone(c.execute('SELECT claimed_at FROM activity_mail_deliveries WHERE message_id=? AND user_id=?',(mid,self.player)).fetchone()[0])
 def test_claim_failure_rolls_back_all_rewards_and_receipt(self):
  self.send();mid=self.mail()['id'];before=self.a.snapshot(self.player,'Test')
  with patch.object(self.a.castle,'_queue_levelups',side_effect=RuntimeError('write failure')):
   with self.assertRaises(RuntimeError):self.claim(mid)
  after=self.a.snapshot(self.player,'Test');self.assertEqual(after['balance'],before['balance']);self.assertEqual(after['xp'],before['xp']);self.assertEqual(after['khaz']['pouciel'],0);self.assertFalse(self.mail()['claimed']);self.claim(mid)
 def test_send_audit_failure_rolls_back_every_delivery(self):
  with patch.object(self.a.notifications,'admin_event',side_effect=RuntimeError('audit failure')):
   with self.assertRaises(RuntimeError):self.send(cmd='mail_all')
  for uid in (self.admin,self.player,self.other):self.assertEqual(self.a.mailbox.counts(uid)['total'],0)
 def test_invalid_values_cannot_create_mail(self):
  for delta in ({'gold':-1},{'gold':True},{'gold':10001},{'xp':1.5},{'title':' '},{'title':'x'*81},{'text':''},{'item':'none','quantity':1},{'item':"'; DROP TABLE players;--"}):
   args=self.args();args.update(delta)
   with self.subTest(delta=delta):
    with self.assertRaises(ValueError):self.send(args)
  self.assertEqual(self.a.mailbox.counts(self.player)['total'],0)
 def test_resource_and_story_item_gifts_are_credited_once(self):
  from story_engine import ALL_STORY_ITEMS
  item=sorted(ALL_STORY_ITEMS)[0];args=self.args();args.update(item=item,quantity=2);self.send(args);mid=self.mail()['id'];self.claim(mid);self.claim(mid)
  self.assertEqual(self.a.expeditions.get_resources(self.player)[item],2);self.assertTrue(self.a.story.has_purchased_story_item(self.player,item))
 def test_rewards_are_exact_even_during_xp_bonus_and_level_up(self):
  with self.a.conn() as c:c.execute("INSERT INTO bot_events(event_key,enabled) VALUES('xp_x2',1)")
  args=self.args();args['xp']=100;self.send(args);self.claim(self.mail()['id']);state=self.a.snapshot(self.player,'Test');self.assertEqual(self.a.castle.profile(self.player)['xp'],125);self.assertEqual(state['level'],2)
 def test_maintenance_and_active_combat_preserve_pending_reward(self):
  self.send();mid=self.mail()['id']
  with self.a.conn() as c:c.execute("INSERT INTO activity_maintenance VALUES('mail','Test',0,?,0)",(ADMIN,))
  with self.assertRaises(ValueError):self.claim(mid)
  with self.a.conn() as c:c.execute('DELETE FROM activity_maintenance')
  with patch.object(self.a.khaz,'active',return_value=True):
   with self.assertRaises(ValueError):self.claim(mid)
  self.assertFalse(self.mail()['claimed']);self.claim(mid)
 def test_pagination_has_four_letters_and_archive_reclamps_page(self):
  for n in range(5):self.send()
  self.assertEqual(len(self.a.mailbox.listing(self.player,0)['entries']),4);last=self.a.mailbox.listing(self.player,1);self.assertEqual(len(last['entries']),1)
  mid=last['entries'][0]['id'];self.claim(mid);self.a.action(self.player,dict(action='mail_archive',key=mid));self.assertEqual(self.a.mailbox.listing(self.player,1)['page'],0)
 def test_plain_message_can_be_archived_without_claim_and_caps_preserve_letter(self):
  args=self.args();args.update(gold=0,xp=0,pouciel=0);self.send(args);mid=self.mail()['id'];self.a.action(self.player,dict(action='mail_archive',key=mid));self.assertEqual(self.a.mailbox.counts(self.player)['total'],0)
  self.send();mid=self.mail()['id']
  with self.a.conn() as c:c.execute('UPDATE players SET wallet_gold=1000000000 WHERE user_id=?',(self.player,))
  with self.assertRaises(ValueError):self.claim(mid)
  self.assertFalse(self.mail()['claimed'])

 def test_bulk_mail_preview_survives_normal_play_but_freezes_recipient_list(self):
  p=self.send(cmd='mail_all',confirm=False)
  with self.a.conn() as c:c.execute('UPDATE players SET wallet_gold=wallet_gold+1 WHERE user_id=?',(self.player,))
  self.a.admin_commands.confirm(self.admin,p['token']);self.assertEqual(self.a.mailbox.counts(self.player)['total'],1)

from aiohttp import web
from aiohttp.test_utils import TestClient,TestServer
import server,activity as adapter
from request_security import api_security
class MailHttpTests(unittest.IsolatedAsyncioTestCase):
 make=MailTests.make
 args=MailTests.args
 send=MailTests.send
 mail=MailTests.mail
 async def asyncSetUp(self):
  MailTests.setUp(self);self.previous=adapter.SERVICE;adapter.SERVICE=self.a;self.tokens={}
  for did in (ADMIN,PLAYER,OTHER):
   (uid,name),token=self.a.session('');self.a.snapshot(uid,name);self.a.bind_discord(uid,dict(id=did,username='Test',global_name='Test',avatar=None,discriminator='0'),token);self.tokens[did]=token
  app=web.Application(middlewares=[api_security(lambda:self.a)]);app.router.add_get('/api/mail',server.mailbox);app.router.add_post('/api/activity',adapter.activity);app.router.add_post('/api/admin',server.admin)
  self.client=TestClient(TestServer(app));await self.client.start_server()
 async def asyncTearDown(self):await self.client.close();adapter.SERVICE=self.previous;self.tmp.cleanup()
 def headers(self,did):self.client.session.cookie_jar.clear();return {'Cookie':'altherya_test='+self.tokens[did],'X-Altherya-Request':'1'}
 async def test_inbox_authentication_does_not_allocate_anonymous_accounts(self):
  with self.a.conn() as c:before=c.execute('SELECT COUNT(*) FROM activity_sessions').fetchone()[0]
  self.assertEqual((await self.client.get('/api/mail')).status,403)
  with self.a.conn() as c:self.assertEqual(c.execute('SELECT COUNT(*) FROM activity_sessions').fetchone()[0],before)
 async def test_inbox_privacy_invalid_pages_and_no_store(self):
  self.send();r=await self.client.get('/api/mail?user_id='+str(self.player),headers=self.headers(OTHER));self.assertEqual(r.status,200);self.assertEqual((await r.json())['entries'],[]);self.assertEqual(r.headers['Cache-Control'],'no-store')
  for page in ('-1','abc','1000001'):
   self.assertEqual((await self.client.get('/api/mail?page='+page,headers=self.headers(PLAYER))).status,400)
 async def test_forged_recipient_cannot_claim_and_csrf_is_rejected(self):
  self.send();mid=self.mail()['id'];body=dict(action='mail_claim',key=mid,user_id=self.player,player=PLAYER)
  r=await self.client.post('/api/activity',headers=self.headers(OTHER),json=body);self.assertEqual(r.status,400)
  self.client.session.cookie_jar.clear();r=await self.client.post('/api/activity',headers={'Cookie':'altherya_test='+self.tokens[PLAYER]},json=body);self.assertEqual(r.status,403)
  r=await self.client.post('/api/admin',headers=self.headers(PLAYER),json=dict(action='command_preview',command='mail_all',args=self.args(),reason='Tentative'));self.assertEqual(r.status,403)
 async def test_mail_closure_blocks_read_and_claim_then_reopens(self):
  self.send();mid=self.mail()['id']
  with self.a.conn() as c:c.execute("INSERT INTO activity_maintenance VALUES('mail','Travaux',0,?,0)",(ADMIN,))
  self.assertEqual((await self.client.get('/api/mail',headers=self.headers(PLAYER))).status,400)
  self.assertEqual((await self.client.post('/api/activity',headers=self.headers(PLAYER),json=dict(action='mail_claim',key=mid))).status,400)
  with self.a.conn() as c:c.execute('DELETE FROM activity_maintenance')
  self.assertEqual((await self.client.post('/api/activity',headers=self.headers(PLAYER),json=dict(action='mail_claim',key=mid))).status,200)
