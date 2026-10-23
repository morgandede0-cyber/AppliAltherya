"""Adversarial JSON boundaries and route-wide request quotas."""
import os,sys,tempfile,unittest
from pathlib import Path
from unittest.mock import patch
from aiohttp import web
from aiohttp.test_utils import TestClient,TestServer
sys.path.insert(0,str(Path(__file__).parents[1]))
import activity as adapter
from activity import Activity
import server
from request_security import api_security,RequestBudget
ADMIN=dict(id='666805849011912705',username='Admin',global_name='Admin',avatar=None,discriminator='0')

class HttpAuditTests(unittest.IsolatedAsyncioTestCase):
 async def asyncSetUp(self):
  self.tmp=tempfile.TemporaryDirectory();self.a=Activity(self.tmp.name+'/test.db');self.old=adapter.SERVICE;adapter.SERVICE=self.a
  (self.uid,_),token=self.a.session('');self.uid,token=self.a.identities.login(self.uid,ADMIN,token);self.a.snapshot(self.uid,'Admin')
  with self.a.conn() as c:
   c.execute('UPDATE tutorial_progress SET completed=1 WHERE user_id=?',(self.uid,));c.execute('UPDATE activity_tutorial_revision SET finished=1 WHERE user_id=?',(self.uid,))
  app=web.Application(client_max_size=4096,middlewares=[api_security(lambda:self.a,RequestBudget(clock=lambda:0))]);app.router.add_post('/api/activity',adapter.activity);app.router.add_post('/api/admin',server.admin);app.router.add_post('/api/auth/discord',server.auth);app.router.add_get('/api/combat-history',server.combat_history)
  self.client=TestClient(TestServer(app));await self.client.start_server();self.client.session.cookie_jar.update_cookies({'altherya_test':token})
 async def asyncTearDown(self):await self.client.close();adapter.SERVICE=self.old;self.tmp.cleanup()
 async def post(self,route,body):return await self.client.post('/api/'+route,data=body,headers={'X-Altherya-Request':'1','Content-Type':'application/json'})
 async def test_deep_json_is_refused_on_game_and_admin(self):
  for depth in (33,1100):
   for route in ('activity','admin'):
    body='{"action":"'+('daily' if route=='activity' else 'health')+'","extra":'+'['*depth+'0'+']'*depth+'}'
    with self.subTest(depth=depth,route=route):self.assertEqual((await self.post(route,body)).status,400)
 async def test_nonfinite_json_numbers_are_rejected_on_all_post_routes(self):
  for value in ('NaN','Infinity','-Infinity'):
   for route in ('activity','admin','auth/discord'):
    with self.subTest(value=value,route=route),patch.dict(os.environ,{'DISCORD_CLIENT_ID':'test','DISCORD_CLIENT_SECRET':'test'}):
     self.assertEqual((await self.post(route,'{"action":"'+('daily' if route=='activity' else 'health')+'","code":null,"extra":'+value+'}')).status,400)
 async def test_combat_history_uses_the_same_authenticated_budget(self):
  for i in range(61):
   r=await self.client.get('/api/combat-history')
   self.assertEqual(r.status,200 if i<60 else 429)
 async def test_invalid_input_does_not_change_economy(self):
  before=self.a.economy.get_balance(self.uid)
  for body in ('null','[]','{"action":3}','{"action":"deposit","amount":true}','{"action":"buy","key":[]}'):
   self.assertEqual((await self.post('activity',body)).status,400)
  self.assertEqual(self.a.economy.get_balance(self.uid),before)

 async def test_normal_json_and_oversized_json_keep_their_contract(self):
  self.assertEqual((await self.post('admin','{"action":"health","extra":'+('['*20)+'0'+(']'*20)+'}')).status,200)
  self.assertEqual((await self.post('activity','{"action":"daily","extra":"'+'x'*5000+'"}')).status,413)

if __name__=='__main__':unittest.main()
