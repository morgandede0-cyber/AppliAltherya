import unittest,tempfile,sys,os
from pathlib import Path
from unittest.mock import patch
sys.path.insert(0,str(Path(__file__).parents[1]))
from activity import Activity
from discord_profile import verified_user,avatar_cdn
import activity as adapter
import server
from aiohttp import web
from aiohttp.test_utils import TestClient,TestServer
USER={'id':'123456789012345678','username':'testeur','global_name':'Voyageur','avatar':'a_'+'b'*32,'discriminator':'0'}
class ProfileTests(unittest.TestCase):
 def setUp(self):
  self.tmp=tempfile.TemporaryDirectory();self.a=Activity(self.tmp.name+'/test.db');(self.uid,self.name),self.token=self.a.session('');self.a.snapshot(self.uid,self.name)
 def tearDown(self):self.tmp.cleanup()
 def test_verified_metadata_persists_without_changing_wallet_or_identity(self):
  before=self.a.snapshot(self.uid,self.name);self.a.bind_discord(self.uid,USER);a=Activity(self.a.path);after=a.snapshot(self.uid,self.name);self.assertEqual(after['balance'],before['balance']);self.assertEqual(after['name'],before['name']);self.assertEqual(a.session_uid(self.token),self.uid);self.assertEqual(after['discord']['display_name'],'Voyageur');self.assertTrue(after['discord']['avatar_url'].startswith('/api/avatar?v='));self.assertNotIn('discord_id',after['discord']);(other,_),_=a.session('');self.assertIsNone(a.snapshot(other,'Autre')['discord'])
 def test_rejects_client_supplied_profile_and_invalid_cdn_paths(self):
  with self.assertRaises(ValueError):self.a.action(self.uid,{'action':'profile','avatar_url':'https://example.com'})
  for field,value in [('id','../x'),('avatar','../../x'),('username',[]),('discriminator','oops')]:
   with self.assertRaises(ValueError):verified_user({**USER,field:value})
 def test_default_and_custom_avatar_urls(self):
  self.assertEqual(avatar_cdn(verified_user(USER)),f"https://cdn.discordapp.com/avatars/{USER['id']}/{USER['avatar']}.png?size=256")
  modern=verified_user({**USER,'avatar':None});self.assertIn('/embed/avatars/'+str((int(USER['id'])>>22)%6)+'.png',avatar_cdn(modern))
  legacy=verified_user({**USER,'avatar':None,'discriminator':'1234'});self.assertTrue(avatar_cdn(legacy).endswith('/4.png'))
 def test_story_inventory_stays_separate_even_after_market_moves_to_next_group(self):
  item=self.a.snapshot(self.uid,self.name)['story_items'][0]['name'];self.a.expeditions.add_resources(self.uid,{item:1,'Bois de chêne':2});s=self.a.snapshot(self.uid,self.name);self.assertIn({'name':item,'quantity':1},s['owned_story_items']);self.assertNotIn('Bois de chêne',[i['name'] for i in s['owned_story_items']])
class FakeResponse:
 def __init__(self,data,status=200,ctype='image/png',content=b'avatar-image'):self.data=data;self.status=status;self.content_type=ctype;self.content=self;self.image=content
 async def __aenter__(self):return self
 async def __aexit__(self,*args):pass
 async def json(self):return self.data
 async def iter_chunked(self,size):yield self.image
class FakeSession:
 def __init__(self,*args,**kwargs):pass
 async def __aenter__(self):return self
 async def __aexit__(self,*args):pass
 def post(self,url,**kwargs):return FakeResponse({'access_token':'fake-test-token'})
 def get(self,url,**kwargs):return FakeResponse(USER) if url.endswith('/users/@me') else FakeResponse({})
class ProfileHttpTests(unittest.IsolatedAsyncioTestCase):
 async def asyncSetUp(self):
  self.tmp=tempfile.TemporaryDirectory();self.previous=adapter.SERVICE;adapter.SERVICE=Activity(self.tmp.name+'/http.db');app=web.Application();app.router.add_get('/api/activity',adapter.activity);app.router.add_post('/api/auth/discord',server.auth);app.router.add_get('/api/avatar',server.avatar);self.client=TestClient(TestServer(app));await self.client.start_server();await self.client.get('/api/activity')
 async def asyncTearDown(self):await self.client.close();adapter.SERVICE=self.previous;self.tmp.cleanup()
 async def test_oauth_uses_verified_response_not_submitted_avatar(self):
  with patch.dict(os.environ,{'DISCORD_CLIENT_ID':'test','DISCORD_CLIENT_SECRET':'test'}),patch.object(server,'ClientSession',FakeSession):
   r=await self.client.post('/api/auth/discord',json={'code':'test-code','avatar':'bad','username':'intrus'});self.assertEqual(r.status,200);self.assertEqual(r.headers['Cache-Control'],'no-store');data=await(await self.client.get('/api/activity')).json();self.assertEqual(data['state']['discord']['display_name'],'Voyageur');self.assertEqual(data['state']['balance']['wallet'],0)
   r=await self.client.get(data['state']['discord']['avatar_url']);self.assertEqual(r.status,200);self.assertEqual(await r.read(),b'avatar-image');self.assertTrue(r.headers['Cache-Control'].startswith('private'))
 async def test_avatar_unavailable_without_oauth_and_auth_bad_code(self):
  self.assertEqual((await self.client.get('/api/avatar')).status,404)
  with patch.dict(os.environ,{'DISCORD_CLIENT_ID':'test','DISCORD_CLIENT_SECRET':'test'}):self.assertEqual((await self.client.post('/api/auth/discord',json={'code':[]})).status,400)
 async def test_oauth_network_failure_does_not_bind_profile(self):
  class DownSession(FakeSession):
   async def __aenter__(self):raise server.ClientError('offline')
  with patch.dict(os.environ,{'DISCORD_CLIENT_ID':'test','DISCORD_CLIENT_SECRET':'test'}),patch.object(server,'ClientSession',DownSession):self.assertEqual((await self.client.post('/api/auth/discord',json={'code':'test-code'})).status,502)
  self.assertIsNone((await(await self.client.get('/api/activity')).json())['state']['discord'])
