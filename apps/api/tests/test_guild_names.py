import asyncio,os,sys,tempfile,time,unittest
from pathlib import Path
from unittest.mock import patch,AsyncMock
sys.path.insert(0,str(Path(__file__).parents[1]))
from activity import Activity
from guild_names import NamesUnavailable,names_lifecycle
from test_discord_profile import USER
GUILD='123456789012345679'
CHANNEL='1551927225253761044'
MEMBER={'user':USER,'nick':'[IV] Voyageur du serveur'}

class Response:
 def __init__(self,data,status=200):self.data=data;self.status=status
 async def __aenter__(self):return self
 async def __aexit__(self,*args):pass
 async def json(self):return self.data
class Session:
 def __init__(self,responses):self.responses=list(responses);self.calls=[]
 def get(self,url,**kwargs):
  self.calls.append((url,kwargs));return self.responses.pop(0)

class GuildNameTests(unittest.IsolatedAsyncioTestCase):
 async def asyncSetUp(self):
  self.tmp=tempfile.TemporaryDirectory();self.a=Activity(self.tmp.name+'/db')
  (self.uid,self.name),self.token=self.a.session('');self.a.snapshot(self.uid,self.name);self.a.bind_discord(self.uid,USER,self.token)
  self.n=self.a.guild_names
  self.env=patch.dict(os.environ,{'DISCORD_BOT_TOKEN':'test-only','DISCORD_GUILD_ID':GUILD});self.env.start()
 async def asyncTearDown(self):self.env.stop();self.tmp.cleanup()
 def display(self):return self.a.snapshot(self.uid,self.name)['name']
 async def refresh(self,member=MEMBER,status=200):
  return await self.n.refresh(self.uid,force=True,session=Session([Response(member,status)]))
 async def test_nickname_preferred_and_wallet_untouched(self):
  before=self.a.snapshot(self.uid,self.name);self.assertTrue(await self.refresh())
  after=self.a.snapshot(self.uid,self.name);self.assertEqual(after['name'],MEMBER['nick']);self.assertEqual(after['balance'],before['balance']);self.assertEqual(after['xp'],before['xp'])
  self.assertEqual(self.a.session_uid(self.token),self.uid);self.assertEqual(self.a.discord_profile(self.uid)['discord_id'],USER['id'])
 async def test_missing_nickname_global_then_username(self):
  await self.refresh({'user':USER,'nick':None});self.assertEqual(self.display(),'Voyageur')
  await self.refresh({'user':{**USER,'global_name':None},'nick':None});self.assertEqual(self.display(),'testeur')
 async def test_nickname_removal_clears_old_value(self):
  await self.refresh();await self.refresh({'user':{**USER,'global_name':'Nouveau global'},'nick':None});self.assertEqual(self.display(),'Nouveau global');self.assertIsNone(self.n.row(self.uid)['nickname'])
 async def test_network_error_keeps_verified_cached_nick(self):
  await self.refresh()
  with patch.object(self.n,'get_json',side_effect=NamesUnavailable('reseau')):self.assertFalse(await self.refresh())
  self.assertEqual(self.display(),MEMBER['nick'])
 async def test_http_403_keeps_nick(self):
  await self.refresh();self.assertFalse(await self.refresh({},403));self.assertEqual(self.display(),MEMBER['nick'])
 async def test_non_member_falls_back_without_reset(self):
  await self.refresh();self.assertFalse(await self.refresh({},404));self.assertEqual(self.display(),'Voyageur')
 async def test_identity_mismatch_rejected(self):
  await self.refresh();self.assertFalse(await self.refresh({'user':{**USER,'id':'999999999999999999'},'nick':'Intrus'}));self.assertEqual(self.display(),MEMBER['nick'])
 async def test_bad_nick_rejected(self):
  for nick in ([],{},'x'*33,''):
   self.assertFalse(await self.refresh({'user':USER,'nick':nick}));self.assertEqual(self.display(),'Voyageur')
 async def test_source_is_configured_portal_not_player_input(self):
  with patch.dict(os.environ,{'DISCORD_GUILD_ID':''}):
   fake=Session([Response({'id':CHANNEL,'guild_id':GUILD}),Response(MEMBER)])
   self.assertTrue(await self.n.refresh(self.uid,force=True,session=fake))
   self.assertTrue(fake.calls[0][0].endswith('/channels/'+CHANNEL));self.assertTrue(fake.calls[1][0].endswith('/guilds/'+GUILD+'/members/'+USER['id']))
   self.assertEqual(fake.calls[1][1]['headers']['Authorization'],'Bot test-only');self.assertFalse(fake.calls[1][1]['allow_redirects'])
 async def test_unverified_channel_mapping_rejected(self):
  with patch.dict(os.environ,{'DISCORD_GUILD_ID':''}):
   fake=Session([Response({'id':'999999999999999999','guild_id':GUILD})]);self.assertFalse(await self.n.refresh(self.uid,force=True,session=fake));self.assertEqual(self.display(),'Voyageur')
 async def test_mapping_cached_on_next_member_request(self):
  with patch.dict(os.environ,{'DISCORD_GUILD_ID':''}):
   fake=Session([Response({'id':CHANNEL,'guild_id':GUILD}),Response(MEMBER),Response(MEMBER)])
   await self.n.refresh(self.uid,force=True,session=fake);await self.n.refresh(self.uid,force=True,session=fake);self.assertEqual(len(fake.calls),3)
 async def test_poll_throttled_before_next_check(self):
  await self.refresh();fake=Session([]);self.assertFalse(await self.n.refresh(self.uid,session=fake));self.assertEqual(fake.calls,[])
 async def test_rate_limit_sets_pause(self):
  fake=Session([Response({'retry_after':60},429)]);self.assertFalse(await self.n.refresh(self.uid,force=True,session=fake));self.assertGreater(self.n.paused_until,time.time()+50)
  second=Session([]);self.assertFalse(await self.n.refresh(self.uid,force=True,session=second));self.assertEqual(second.calls,[])
 async def test_relogin_failure_restores_cached_nick_after_bind(self):
  await self.refresh();self.a.bind_discord(self.uid,USER,self.token);self.assertEqual(self.a.discord_profile(self.uid)['display_name'],'Voyageur')
  with patch.dict(os.environ,{'DISCORD_BOT_TOKEN':''}):await self.n.login(self.uid,USER)
  self.assertEqual(self.display(),MEMBER['nick'])
 async def test_restart_preserves_nick_and_account_fallback(self):
  await self.refresh();a=Activity(self.a.path);self.assertEqual(a.snapshot(self.uid,self.name)['name'],MEMBER['nick']);self.assertEqual(a.guild_names.row(self.uid)['account_name'],'Voyageur')
 async def test_all_sessions_and_receipt_names_update(self):
  for i in range(5):self.a.action(self.uid,{'action':'tutorial_next','step':i})
  self.a.action(self.uid,{'action':'tutorial_finish','step':5})
  (other,_),token=self.a.session('');self.a.snapshot(other,'Other');self.a.bind_discord(other,USER,token)
  await self.refresh()
  with self.a.conn() as c:
   names=[r[0] for r in c.execute('SELECT name FROM activity_sessions WHERE user_id=?',(self.uid,))];receipt=c.execute('SELECT name FROM activity_tutorial_receipts WHERE user_id=?',(self.uid,)).fetchone()[0]
  self.assertEqual(set(names),{MEMBER['nick']});self.assertEqual(receipt,MEMBER['nick'])
 async def test_old_nick_not_used_for_different_guild(self):
  await self.refresh()
  with patch.dict(os.environ,{'DISCORD_GUILD_ID':'999999999999999999','DISCORD_BOT_TOKEN':''}):await self.n.login(self.uid,USER)
  self.assertEqual(self.display(),'Voyageur')
 async def test_backfill_only_known_accounts(self):
  self.assertEqual(self.n.next_player(),self.uid);await self.refresh();self.assertIsNone(self.n.next_player())
 async def test_admin_rights_still_use_id(self):
  await self.refresh({'user':USER,'nick':'666805849011912705'});self.assertFalse(self.a.admin.allowed(self.uid))
 async def test_no_token_still_plays_with_account_name(self):
  with patch.dict(os.environ,{'DISCORD_BOT_TOKEN':''}):await self.n.login(self.uid,USER)
  self.assertEqual(self.display(),'Voyageur');self.assertEqual(self.n.row(self.uid)['last_error'],'token_absent')
 async def test_active_battle_uses_current_server_nickname(self):
  await self.refresh();self.a.play.save(self.uid,{'kind':'combat','status':'active','fighters':[{'name':'Ancien'},{'name':'Champion'}]})
  self.assertEqual(self.a.play.public(self.uid)['fighters'][0]['name'],MEMBER['nick'])
 async def test_gazette_uses_current_nickname_for_old_results(self):
  from datetime import datetime,timedelta
  from zoneinfo import ZoneInfo
  await self.refresh()
  with self.a.conn() as c:
   c.execute("INSERT INTO activity_discord SELECT -1,discord_id,avatar,username,'Ancien doublon',discriminator FROM activity_discord WHERE user_id=?",(self.uid,))
   c.execute('INSERT INTO activity_discord_game_results VALUES(?,?,?,?,?)',('fixture',USER['id'],'Ancien',10,time.time()))
  self.a.notifications.gazette((datetime.now(ZoneInfo('Europe/Paris'))+timedelta(days=1)).replace(hour=9))
  with self.a.conn() as c:r=c.execute('SELECT payload FROM activity_discord_outbox WHERE channel="gazette"').fetchone()
  self.assertIn(MEMBER['nick'],r[0]);self.assertNotIn('Ancien',r[0])
 async def test_admin_log_name_uses_canonical_account(self):
  await self.refresh()
  with self.a.conn() as c:
   c.execute("INSERT INTO activity_discord SELECT -1,discord_id,avatar,username,'Ancien doublon',discriminator FROM activity_discord WHERE user_id=?",(self.uid,))
   self.a.notifications.admin_event(c,'fixture-name',USER['id'],USER['id'],'wallet',1,2,'Test')
   text=c.execute('SELECT payload FROM activity_discord_outbox WHERE event_key="admin:fixture-name"').fetchone()[0]
  self.assertIn(MEMBER['nick'],text);self.assertNotIn('Ancien doublon',text)
 async def test_no_token_no_worker(self):
  with patch.dict(os.environ,{'DISCORD_BOT_TOKEN':''}),patch('guild_names.name_worker',new_callable=AsyncMock) as worker:
   ctx=names_lifecycle({});await anext(ctx);await ctx.aclose();worker.assert_not_called()

class GuildNameHttpTests(unittest.IsolatedAsyncioTestCase):
 async def asyncSetUp(self):
  import activity as adapter
  import server
  from aiohttp import web
  from aiohttp.test_utils import TestClient,TestServer
  self.tmp=tempfile.TemporaryDirectory();self.old=adapter.SERVICE;adapter.SERVICE=Activity(self.tmp.name+'/http.db')
  app=web.Application();app.router.add_get('/api/activity',adapter.activity);app.router.add_post('/api/auth/discord',server.auth)
  self.client=TestClient(TestServer(app),headers={'X-Altherya-Request':'1'});await self.client.start_server();await self.client.get('/api/activity')
 async def asyncTearDown(self):
  import activity as adapter
  await self.client.close();adapter.SERVICE=self.old;self.tmp.cleanup()
 async def connect(self,status):
  import server
  from test_discord_profile import FakeSession
  class BotSession(Session):
   def __init__(self,*args,**kwargs):super().__init__([Response(MEMBER,status)])
   async def __aenter__(self):return self
   async def __aexit__(self,*args):pass
  with patch.dict(os.environ,{'DISCORD_CLIENT_ID':'test','DISCORD_CLIENT_SECRET':'test','DISCORD_BOT_TOKEN':'test-only','DISCORD_GUILD_ID':GUILD}),patch.object(server,'ClientSession',FakeSession),patch('guild_names.ClientSession',BotSession):
   return await self.client.post('/api/auth/discord',json={'code':'test','nick':'Intrus','guild_id':'999999999999999999'})
 async def test_oauth_uses_member_from_bot_not_client_nick(self):
  self.assertEqual((await self.connect(200)).status,200)
  state=(await(await self.client.get('/api/activity')).json())['state'];self.assertEqual(state['name'],MEMBER['nick']);self.assertEqual(state['discord']['display_name'],MEMBER['nick'])
 async def test_bot_failure_does_not_block_oauth(self):
  self.assertEqual((await self.connect(403)).status,200)
  state=(await(await self.client.get('/api/activity')).json())['state'];self.assertEqual(state['name'],'Voyageur')

if __name__=='__main__':unittest.main()
