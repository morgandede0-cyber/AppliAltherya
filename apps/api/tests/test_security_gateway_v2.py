"""Session expiry and HTTP flood/forgery regression tests."""
import hashlib,os,sys,tempfile,time,unittest
from pathlib import Path
from unittest.mock import patch
from aiohttp import web
from aiohttp.test_utils import TestClient,TestServer
sys.path.insert(0,str(Path(__file__).parents[1]))
from activity import Activity,SESSION_SECONDS
import activity as adapter
import server
from request_security import RequestBudget,api_security
USER=dict(id='666805849011912705',username='Admin',global_name='Admin',avatar=None,discriminator='0')
class SessionLifetimeTests(unittest.TestCase):
 def setUp(self):
  self.tmp=tempfile.TemporaryDirectory();self.a=Activity(self.tmp.name+'/test.db');(self.uid,_),self.token=self.a.session('');self.digest=hashlib.sha256(self.token.encode()).hexdigest()
 def tearDown(self):self.tmp.cleanup()
 def expire(self):
  with self.a.conn() as c:c.execute('UPDATE activity_session_expiry SET expires_at=?',(time.time()-1,))
 def test_expired_admin_session_is_rejected(self):
  uid,token=self.a.identities.login(self.uid,USER,self.token);self.expire();self.assertIsNone(self.a.session_uid(token))
  with self.assertRaises(PermissionError):self.a.admin.require(self.a.session_uid(token))
  self.assertEqual(uid,self.uid)
 def test_restart_cannot_renew_expired_tokens(self):
  self.expire();a=Activity(self.a.path);self.assertIsNone(a.session_uid(self.token));self.assertNotEqual(a.session(self.token)[0][0],self.uid)
 def test_expired_token_cannot_bind_identity(self):
  self.expire()
  with self.assertRaises(ValueError):self.a.identities.login(self.uid,USER,self.token)
 def test_rotation_revokes_old_token_and_sets_finite_lifetime(self):
  uid,token=self.a.identities.login(self.uid,USER,self.token);self.assertIsNone(self.a.session_uid(self.token));self.assertEqual(self.a.session_uid(token),uid)
  with self.a.conn() as c:expiry=c.execute('SELECT expires_at FROM activity_session_expiry WHERE token=?',(hashlib.sha256(token.encode()).hexdigest(),)).fetchone()[0]
  self.assertAlmostEqual(expiry-time.time(),SESSION_SECONDS,delta=5)
 def test_existing_tokens_migrate_without_reset(self):
  with self.a.conn() as c:c.execute('DROP TABLE activity_session_expiry')
  self.assertEqual(Activity(self.a.path).session_uid(self.token),self.uid)
 def test_reconnection_restores_the_same_save(self):
  uid,token=self.a.identities.login(self.uid,USER,self.token);self.a.snapshot(uid,'Admin')
  with self.a.conn() as c:c.execute('UPDATE players SET wallet_gold=123 WHERE user_id=?',(uid,))
  self.expire();(anonymous,_),fresh=self.a.session(token);target,replacement=self.a.identities.login(anonymous,USER,fresh)
  self.assertEqual(target,uid);self.assertEqual(self.a.economy.get_balance(target).wallet,123);self.assertEqual(self.a.session_uid(replacement),uid)
class BudgetTests(unittest.TestCase):
 def test_refill_and_separate_players(self):
  now=[0.];b=RequestBudget(clock=lambda:now[0]);self.assertEqual(b.take(('p',1),1,1),0);self.assertEqual(b.take(('p',1),1,1),1);self.assertEqual(b.take(('p',2),1,1),0);now[0]=1;self.assertEqual(b.take(('p',1),1,1),0)
 def test_bounded_memory(self):
  b=RequestBudget(maximum=3)
  for i in range(20):b.take(i,1,1)
  self.assertEqual(len(b.entries),3)
class HttpAdmissionTests(unittest.IsolatedAsyncioTestCase):
 async def asyncSetUp(self):
  self.tmp=tempfile.TemporaryDirectory();self.a=Activity(self.tmp.name+'/test.db');self.old=adapter.SERVICE;adapter.SERVICE=self.a
  app=web.Application(client_max_size=4096,middlewares=[api_security(lambda:self.a,RequestBudget(clock=lambda:0),anonymous_capacity=40,oauth_capacity=20)]);app.router.add_get('/api/activity',adapter.activity);app.router.add_post('/api/activity',adapter.activity);app.router.add_post('/api/auth/discord',server.auth)
  self.client=TestClient(TestServer(app));await self.client.start_server()
 async def asyncTearDown(self):
  await self.client.close();adapter.SERVICE=self.old;self.tmp.cleanup()
 def count(self):
  with self.a.conn() as c:return c.execute('SELECT COUNT(*) FROM activity_sessions').fetchone()[0]
 async def test_post_without_session_does_not_create_player(self):
  r=await self.client.post('/api/activity',json={'action':'daily'},headers={'X-Altherya-Request':'1'});self.assertEqual(r.status,401);self.assertEqual(self.count(),0)
 async def test_malformed_post_does_not_create_session(self):
  for body in [[],None,{'action':True},{'action':'buy','key':[]}]:
   r=await self.client.post('/api/activity',json=body,headers={'X-Altherya-Request':'1'});self.assertEqual(r.status,400)
  self.assertEqual(self.count(),0)
 async def test_cross_site_post_rejected_with_custom_header(self):
  r=await self.client.post('/api/activity',json={'action':'daily'},headers={'X-Altherya-Request':'1','Sec-Fetch-Site':'cross-site'});self.assertEqual(r.status,403);self.assertEqual(self.count(),0)
 async def test_forged_cookies_and_forwarded_headers_do_not_bypass_quota(self):
  for i in range(41):
   self.client.session.cookie_jar.clear();r=await self.client.get('/api/activity',headers={'Cookie':'altherya_test=forged'+str(i),'X-Forwarded-For':'10.0.0.'+str(i)});self.assertEqual(r.status,200 if i<40 else 429)
  self.assertEqual(self.count(),40);self.assertEqual(r.headers['Retry-After'],'1')
 async def test_oauth_flood_throttled(self):
  with patch.dict(os.environ,{'DISCORD_CLIENT_ID':'','DISCORD_CLIENT_SECRET':''}):
   for i in range(21):
    r=await self.client.post('/api/auth/discord',json={'code':'x'},headers={'X-Altherya-Request':'1'});self.assertEqual(r.status,503 if i<20 else 429)
  self.assertEqual(self.count(),0)
 async def test_oauth_non_object_returns_400(self):
  with patch.dict(os.environ,{'DISCORD_CLIENT_ID':'test','DISCORD_CLIENT_SECRET':'test'}):r=await self.client.post('/api/auth/discord',json=[],headers={'X-Altherya-Request':'1'})
  self.assertEqual(r.status,400)
 async def test_oversized_body_cannot_allocate_session(self):
  r=await self.client.post('/api/activity',json={'action':'name','name':'x'*5000},headers={'X-Altherya-Request':'1'});self.assertEqual(r.status,413);self.assertEqual(self.count(),0)
 async def test_private_response_headers(self):
  r=await self.client.get('/api/activity');self.assertEqual(r.status,200);self.assertEqual(r.headers['Cache-Control'],'no-store');self.assertEqual(r.headers['X-Content-Type-Options'],'nosniff')
