import unittest,tempfile,sys,os
from pathlib import Path
from unittest.mock import patch
from concurrent.futures import ThreadPoolExecutor
sys.path.insert(0,str(Path(__file__).parents[1]))
from activity import Activity
from activity_admin import DEFAULT_ADMIN_IDS
USER={'id':'666805849011912705','username':'admin','global_name':'Admin','avatar':None,'discriminator':'0'}
class AdminTests(unittest.TestCase):
 def setUp(self):
  self.tmp=tempfile.TemporaryDirectory();self.a=Activity(self.tmp.name+'/test.db');self.admin,self.token=self.make(USER['id'],'Moi');self.player,_=self.make('123456789012345678','Aventurier');self.did='123456789012345678'
 def tearDown(self):self.tmp.cleanup()
 def make(self,did,name,complete=True):
  (uid,_),token=self.a.session('');self.a.snapshot(uid,name);self.a.action(uid,{'action':'name','name':name});uid=self.a.bind_discord(uid,{**USER,'id':did,'username':name},token)
  if complete:
   for i in range(5):self.a.action(uid,{'action':'tutorial_next','step':i})
   self.a.action(uid,{'action':'tutorial_finish','step':5})
  return uid,token
 def call(self,**body):return self.a.admin.handle(self.admin,body)
 def change(self,**extra):return self.call(action='adjust',player=self.did,field='wallet',amount=20,expected=100,reason='Correction test',request_id='test-request-12345678',**extra)
 def test_allowlist_exact_verified_ids_only(self):
  self.assertEqual(DEFAULT_ADMIN_IDS,{'666805849011912705','342359563791761410','587578557027450900'})
  for did in DEFAULT_ADMIN_IDS:
   uid,_=self.make(did,'Test');self.assertTrue(self.a.admin.allowed(uid))
  self.assertFalse(self.a.admin.allowed(self.player));self.assertFalse(self.a.admin.allowed(None))
  with self.assertRaises(PermissionError):self.a.admin.handle(self.player,dict(action='list',discord_id=USER['id']))
 def test_env_override_and_revocation(self):
  with patch.dict(os.environ,{'ACTIVITY_ADMIN_IDS':''}):
   self.assertFalse(self.a.admin.allowed(self.admin))
   with self.assertRaises(PermissionError):self.call(action='detail',player=self.did)
 def test_only_completed_verified_unique_profiles_four_per_page(self):
  self.make('223456789012345678','Incomplet',False)
  for i in range(5):self.make(str(323456789012345670+i),'Joueur '+str(i))
  (other,_),token=self.a.session('');self.a.snapshot(other,'Autre');self.a.bind_discord(other,{**USER,'id':self.did,'username':'Aventurier'},token)
  r=self.call(action='list');self.assertEqual(r['total'],7);self.assertEqual(len(r['players']),4);self.assertEqual(len(self.call(action='list',page=1)['players']),3)
  for query in ['aventu',self.did]:self.assertEqual(self.call(action='list',query=query)['total'],1)
  self.assertEqual(self.call(action='list',query="' OR 1=1 --")['total'],0)
 def test_gold_adjustment_atomic_audited_and_idempotent(self):
  with ThreadPoolExecutor(3) as pool:list(pool.map(lambda _:self.change(),range(3)))
  d=self.call(action='detail',player=self.did);self.assertEqual(d['balance']['wallet'],120)
  history=self.call(action='history',player=self.did)['entries'];self.assertEqual(len(history),1);self.assertEqual(history[0]['actor'],USER['id']);self.assertEqual(history[0]['reason'],'Correction test')
 def test_stale_balance_and_invalid_values_rejected(self):
  self.change()
  with self.assertRaises(ValueError):self.call(action='adjust',player=self.did,field='wallet',amount=10,expected=100,reason='Correction',request_id='different-request-123')
  for amount in [True,1.5,-10000000,0,'10']:
   with self.assertRaises(ValueError):self.call(action='adjust',player=self.did,field='wallet',amount=amount,expected=120,reason='Test',request_id='invalid-request-123')
 def test_xp_award_and_restart(self):
  self.call(action='adjust',player=self.did,field='xp',amount=25,expected=25,reason='Bonus événement',request_id='xp-request-123456789')
  self.a=Activity(self.a.path);self.assertEqual(self.call(action='detail',player=self.did)['xp'],50)
 def test_bank_adjustment_and_negative_balance_rejected(self):
  self.call(action='adjust',player=self.did,field='bank',amount=50,expected=0,reason='Correction banque',request_id='bank-request-1234567')
  with self.assertRaises(ValueError):self.call(action='adjust',player=self.did,field='bank',amount=-51,expected=50,reason='Retrait incorrect',request_id='bank-negative-123456')
  self.assertEqual(self.call(action='detail',player=self.did)['balance']['bank'],50)
 def test_failed_xp_transaction_rolls_back_money_and_history(self):
  before=self.call(action='detail',player=self.did)['xp']
  with patch.object(self.a.castle,'_sync_level',side_effect=RuntimeError('test')):
   with self.assertRaises(RuntimeError):self.call(action='adjust',player=self.did,field='xp',amount=20,expected=before,reason='Bonus test',request_id='rollback-request-123')
  self.assertEqual(self.call(action='detail',player=self.did)['xp'],before);self.assertEqual(self.call(action='history',player=self.did)['entries'],[])
 def test_incomplete_target_and_anonymous_are_rejected(self):
  self.make('223456789012345678','Incomplet',False)
  with self.assertRaises(ValueError):self.call(action='detail',player='223456789012345678')
  (uid,_),_=self.a.session('');self.a.snapshot(uid,'Anonyme')
  with self.assertRaises(PermissionError):self.a.admin.handle(uid,{'action':'list','admin':True})
from aiohttp import web
from aiohttp.test_utils import TestClient,TestServer
import server,activity as adapter
class AdminHttpTests(unittest.IsolatedAsyncioTestCase):
 async def asyncSetUp(self):
  self.tmp=tempfile.TemporaryDirectory();self.previous=adapter.SERVICE;adapter.SERVICE=Activity(self.tmp.name+'/http.db');self.a=adapter.SERVICE
  (uid,_),token=self.a.session('');self.a.snapshot(uid,'Test');self.a.bind_discord(uid,USER,token);self.token=token
  app=web.Application();app.router.add_post('/api/admin',server.admin);app.router.add_get('/api/avatar',server.avatar);self.client=TestClient(TestServer(app));await self.client.start_server()
 async def asyncTearDown(self):await self.client.close();adapter.SERVICE=self.previous;self.tmp.cleanup()
 async def test_anonymous_and_forged_id_denied(self):
  r=await self.client.post('/api/admin',json={'action':'list','discord_id':USER['id']},headers={'X-Altherya-Request':'1'});self.assertEqual(r.status,403)
  self.assertEqual((await self.client.get('/api/avatar?player=123456789012345678')).status,403)
 async def test_authorized_cookie_and_csrf(self):
  self.client.session.cookie_jar.update_cookies({'altherya_test':self.token})
  self.assertEqual((await self.client.post('/api/admin',json={'action':'list'})).status,403)
  r=await self.client.post('/api/admin',json={'action':'list'},headers={'X-Altherya-Request':'1'});self.assertEqual(r.status,200);self.assertEqual(r.headers['Cache-Control'],'no-store')
