import os,unittest,sys
from pathlib import Path
from unittest.mock import patch
from aiohttp import web
from aiohttp.test_utils import make_mocked_request,TestClient,TestServer
sys.path.insert(0,str(Path(__file__).parents[1]))
from activity_cookie import set_activity_cookie
class CookieTests(unittest.TestCase):
 def cookie(self,url,headers=None,configured=True):
  with patch.dict(os.environ,{'DISCORD_CLIENT_ID':'1529936499775242250' if configured else '', 'DISCORD_CLIENT_SECRET':'unit-test' if configured else ''}):
   response=web.Response();request=make_mocked_request('GET',url,headers=headers or {});set_activity_cookie(response,request,'opaque-session-value')
   return response
 def test_production_cookie_is_iframe_compatible_even_behind_http_proxy(self):
  r=self.cookie('/api/activity',{'Host':'altherya.magicgg.fr','X-Forwarded-Proto':'https'})
  cookie=r.headers['Set-Cookie'];self.assertIn('SameSite=None',cookie);self.assertIn('Secure',cookie);self.assertIn('HttpOnly',cookie);self.assertIn('Partitioned',cookie);self.assertIn('Path=/',cookie);self.assertNotIn('Domain=',cookie)
 def test_proxy_hostname_remains_host_only(self):
  r=self.cookie('/api/activity',{'Host':'1529936499775242250.discordsays.com'})
  self.assertIn('Partitioned',r.headers['Set-Cookie']);self.assertNotIn('Domain=',r.headers['Set-Cookie'])
 def test_direct_local_http_mode_preserves_development(self):
  r=self.cookie('/api/activity',{'Host':'localhost:8080'})
  self.assertEqual(r.cookies['altherya_test']['samesite'],'Strict');self.assertFalse(r.cookies['altherya_test']['secure']);self.assertNotIn('Partitioned',r.headers.get('Set-Cookie',''))
 def test_localhost_behind_https_proxy_uses_secure_partitioned_cookie(self):
  r=self.cookie('/api/activity',{'Host':'localhost:8080','X-Forwarded-Proto':'https'})
  self.assertIn('Secure',r.headers['Set-Cookie']);self.assertIn('Partitioned',r.headers['Set-Cookie'])
 def test_no_oauth_configuration_preserves_local_profile(self):
  r=self.cookie('/api/activity',{'Host':'127.0.0.1:8080'},False);self.assertEqual(r.cookies['altherya_test']['samesite'],'Strict')
 def test_no_empty_token_cookie(self):
  response=web.Response();set_activity_cookie(response,make_mocked_request('GET','/'),None);self.assertFalse(response.cookies);self.assertNotIn('Set-Cookie',response.headers)
import server
from test_discord_profile import FakeSession
class AuthCsrfTests(unittest.IsolatedAsyncioTestCase):
 async def test_auth_rejects_cross_origin_simple_post(self):
  app=web.Application();app.router.add_post('/api/auth/discord',server.auth);client=TestClient(TestServer(app));await client.start_server()
  try:
   with patch.dict(os.environ,{'DISCORD_CLIENT_ID':'test','DISCORD_CLIENT_SECRET':'test'}),patch.object(server,'ClientSession',FakeSession):
    r=await client.post('/api/auth/discord',json={'code':'attacker-code'});self.assertEqual(r.status,403)
  finally:await client.close()
