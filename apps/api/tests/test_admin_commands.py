from tutorial_test_support import tutorial_action
"""Operational admin commands and maintenance adversarial regressions."""
import json,os,sys,tempfile,time,unittest
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from unittest.mock import patch
sys.path.insert(0,str(Path(__file__).parents[1]))
from activity import Activity
ADMIN='666805849011912705';PLAYER='123456789012345678';OTHER='342359563791761410'
class AdminCommandTests(unittest.TestCase):
 def setUp(self):
  self.tmp=tempfile.TemporaryDirectory();self.a=Activity(self.tmp.name+'/test.db');self.admin=self.make(ADMIN);self.player=self.make(PLAYER);self.other=self.make(OTHER)
 def tearDown(self):self.tmp.cleanup()
 def make(self,did):
  (u,n),t=self.a.session('');self.a.snapshot(u,n);self.a.bind_discord(u,dict(id=did,username='Test',global_name='Test',avatar=None,discriminator='0'),t)
  for i in range(11):tutorial_action(self.a,u,dict(action='tutorial_next',step=i))
  tutorial_action(self.a,u,dict(action='tutorial_finish',step=11));return u
 def preview(self,cmd,args=None,who=None):return self.a.admin_commands.preview(who or self.admin,dict(command=cmd,player=PLAYER,args=args or {},reason='Correction de test'))
 def apply(self,cmd,args=None):
  p=self.preview(cmd,args);return self.a.admin_commands.confirm(self.admin,p['token'])
 def balance(self):return self.a.economy.get_balance(self.player).wallet
 def test_preview_cannot_mutate_and_confirm_is_idempotent_under_concurrency(self):
  p=self.preview('gift_gold',{'value':7});before=self.balance()
  self.assertEqual(self.balance(),before)
  with ThreadPoolExecutor(3) as pool:list(pool.map(lambda _:self.a.admin_commands.confirm(self.admin,p['token']),range(3)))
  self.assertEqual(self.balance(),before+7);self.assertEqual(len(self.a.admin_commands.history()['entries']),1)
 def test_permission_and_confirmation_owner(self):
  with self.assertRaises(PermissionError):self.preview('wallet',{'value':3},self.player)
  p=self.preview('wallet',{'value':3})
  with self.assertRaises(ValueError):self.a.admin_commands.confirm(self.other,p['token'])
  with patch.dict(os.environ,{'ACTIVITY_ADMIN_IDS':''}):
   with self.assertRaises(PermissionError):self.a.admin_commands.confirm(self.admin,p['token'])
 def test_expired_preview_and_stale_data_rejected(self):
  p=self.preview('wallet',{'value':123})
  with self.a.conn() as c:c.execute('UPDATE activity_admin_previews SET expires=0 WHERE token=?',(p['token'],))
  with self.assertRaises(ValueError):self.a.admin_commands.confirm(self.admin,p['token'])
  p=self.preview('wallet',{'value':123})
  with self.a.conn() as c:c.execute('UPDATE players SET wallet_gold=111 WHERE user_id=?',(self.player,))
  with self.assertRaises(ValueError):self.a.admin_commands.confirm(self.admin,p['token'])
  self.assertEqual(self.balance(),111)
 def test_audit_failure_rolls_back_change_and_receipt(self):
  p=self.preview('wallet',{'value':123});before=self.balance()
  with patch.object(self.a.notifications,'admin_event',side_effect=RuntimeError('disk failure')):
   with self.assertRaises(RuntimeError):self.a.admin_commands.confirm(self.admin,p['token'])
  self.assertEqual(self.balance(),before);self.assertEqual(self.a.admin_commands.history()['entries'],[])
  self.a.admin_commands.confirm(self.admin,p['token']);self.assertEqual(self.balance(),123)
 def test_invalid_parameters_are_rejected(self):
  for cmd,args in [('wallet',{'value':True}),('wallet',{'value':-1}),('resource',{'key':"x'; DROP TABLE players;--",'value':1}),('armor',{'key':'head','branch':'fake','tier':'fake'}),('technique',{'key':'ashkar_1','value':1}),('maintenance',{'key':'unknown','enabled':True,'value':0})]:
   with self.subTest(cmd=cmd,args=args):
    with self.assertRaises(ValueError):self.preview(cmd,args)
 def test_every_catalogue_command_has_an_executable_validated_handler(self):
  # Each command is attempted; state-dependent refusals must be explicit ValueError,
  # never an absent SQL table, invalid enum or unimplemented handler.
  for spec in self.a.admin_commands.catalogue()['commands']:
   args={a['name']:(a['options'][0]['value'] if a['type']=='choice' else False if a['type']=='boolean' else 'Message test' if a['type']=='text' else a['min']) for a in spec['args']}
   with self.subTest(command=spec['id']):
    try:self.apply(spec['id'],args)
    except ValueError as e:self.assertIn(spec['id'],('campaign_stage','daily_restart','round_close'),str(e))
  self.a.snapshot(self.player,'Test')
 def test_tower_only_boss_skills_and_revoke_clears_loadout(self):
  self.apply('technique',{'key':'ashkar_10','value':1})
  with self.a.conn() as c:
   self.assertEqual(c.execute('SELECT floor FROM activity_ashkar_techniques WHERE user_id=?',(self.player,)).fetchone()[0],10)
   c.execute('INSERT INTO activity_arena_loadout VALUES(?,?,?)',(self.player,'ultimate','ashkar_10'))
  self.apply('technique',{'key':'ashkar_10','value':0})
  with self.a.conn() as c:self.assertEqual(c.execute('SELECT COUNT(*) FROM activity_arena_loadout WHERE user_id=?',(self.player,)).fetchone()[0],0)
 def test_tutorial_restart_does_not_repay_reward(self):
  before=self.balance();self.apply('tutorial_restart')
  for i in range(11):tutorial_action(self.a,self.player,dict(action='tutorial_next',step=i))
  tutorial_action(self.a,self.player,dict(action='tutorial_finish',step=11));self.assertEqual(self.balance(),before)
 def test_paid_daily_objectives_cannot_be_reset_for_another_payment(self):
  with self.a.conn() as c:c.execute('INSERT OR REPLACE INTO castle_daily_progress VALUES(?,?,?,?,?)',(self.player,self.a.castle._today(),'combat',1,1))
  p=self.preview('daily_restart')
  with self.assertRaises(ValueError):self.a.admin_commands.confirm(self.admin,p['token'])
 def test_cancelled_expedition_cannot_give_loot_or_xp_later(self):
  self.a.action(self.player,dict(action='start',key='elarwyn_foraging',tool='hands'));xp=self.a.castle.profile(self.player)['xp'];before=self.a.expeditions.get_resources(self.player)
  self.apply('expedition_cancel');self.a=Activity(self.a.path);self.a.snapshot(self.player,'Test')
  self.assertEqual(self.a.expeditions.get_resources(self.player),before);self.assertEqual(self.a.castle.profile(self.player)['xp'],xp)
 def test_restart_persists_maintenance_and_expiry_reopens(self):
  self.apply('maintenance',{'key':'global','enabled':True,'value':0});self.a=Activity(self.a.path)
  with self.assertRaisesRegex(ValueError,'Maintenance'):self.a.action(self.player,dict(action='daily'))
  self.a.action(self.admin,dict(action='daily'))
  with self.a.conn() as c:c.execute('UPDATE activity_maintenance SET until_at=?',(time.time()-1,))
  self.a.action(self.player,dict(action='daily'))
 def test_scoped_maintenance_blocks_direct_api_but_not_unrelated_actions(self):
  self.apply('maintenance',{'key':'bank','enabled':True,'value':0});before=self.balance()
  with self.assertRaisesRegex(ValueError,'Banque'):self.a.action(self.player,dict(action='deposit',amount=1))
  self.assertEqual(self.balance(),before);self.a.action(self.player,dict(action='daily'))
 def test_parents_and_individual_games_resolve_server_side(self):
  self.apply('maintenance',{'key':'tavern','enabled':True,'value':0})
  with self.assertRaisesRegex(ValueError,'Maintenance'):self.a.action(self.player,dict(action='game_start',key='dice',wager=1,revision=0))
  self.apply('maintenance',{'key':'tavern','enabled':False,'value':0});self.apply('maintenance',{'key':'dice','enabled':True,'value':0})
  with self.assertRaisesRegex(ValueError,'Maintenance'):self.a.action(self.player,dict(action='game_start',key='dice',wager=1,revision=0))
  self.a.action(self.player,dict(action='game_start',key='coin',choice='pile',wager=1,revision=0))
 def test_player_lock_and_session_revocation(self):
  (u,n),token=self.a.session('');self.a.snapshot(u,n);self.a.bind_discord(u,dict(id=PLAYER,username='Test',global_name='Test',avatar=None,discriminator='0'),token)
  self.apply('player_lock',{'value':10})
  with self.assertRaises(ValueError):self.a.action(self.player,dict(action='daily'))
  self.apply('player_lock',{'value':0});self.apply('sessions_revoke');self.assertIsNone(self.a.session_uid(token))
 def test_global_lock_covers_all_action_families_and_preserves_data(self):
  self.apply('maintenance',{'key':'global','enabled':True,'value':0});before=self.balance()
  for action in ['buy','upgrade','campaign_accept','ashkar_start','khaz_buy','tutorial_next','job_accept','larceny','battle_start','arena_equip']:
   with self.subTest(action=action):
    with self.assertRaisesRegex(ValueError,'Maintenance'):self.a.action(self.player,dict(action=action,key='axe'))
  self.assertEqual(self.balance(),before)
 def test_campaign_reposition_keeps_reward_receipts(self):
  with self.a.conn() as c:c.execute('INSERT INTO campaign_receipts VALUES(?,?,?,?,?)',(self.player,'S1-Q01',10,5,time.time()))
  self.apply('campaign_position',{'value':0})
  with self.a.conn() as c:self.assertEqual(c.execute('SELECT COUNT(*) FROM campaign_receipts WHERE user_id=?',(self.player,)).fetchone()[0],1)
 def test_cancelled_preview_cannot_be_confirmed(self):
  p=self.preview('wallet',{'value':123});self.a.admin_commands.cancel(self.admin,p['token'])
  with self.assertRaises(ValueError):self.a.admin_commands.confirm(self.admin,p['token'])
 def test_closed_arena_round_is_a_loss_without_refunding_stake(self):
  self.a.action(self.player,dict(action='battle_start',wager=1,revision=0));before=self.balance();self.apply('round_close')
  self.assertEqual(self.balance(),before);self.assertEqual(self.a.play.public(self.player)['status'],'finished');self.assertEqual(self.a.play.public(self.player)['outcome'],'defeat')
 def test_return_to_paid_campaign_quest_can_advance_without_repayment(self):
  from campaign import QUESTS
  q=QUESTS[0]
  with self.a.conn() as c:c.execute('INSERT INTO campaign_receipts VALUES(?,?,?,?,?)',(self.player,q['id'],10,20,time.time()))
  self.apply('campaign_position',{'value':0})
  with self.a.conn() as c:c.execute('UPDATE campaign_progress SET stage=?,accepted_at=?,payload=? WHERE user_id=?',(len(q['steps']),time.time()-100000,json.dumps({'admin_replay':True,'edition':2}),self.player))
  self.a.action(self.player,dict(action='campaign_world_enter',scene=self.a.campaign.snapshot(self.player)['world']['target']));state=self.a.campaign.snapshot(self.player);before=self.balance();xp=self.a.castle.profile(self.player)['xp'];self.a.action(self.player,dict(action='campaign_claim',quest_id=q['id'],revision=state['revision'],world_token=state['world']['token']))
  self.assertEqual(self.balance(),before);self.assertEqual(self.a.castle.profile(self.player)['xp'],xp)
  with self.a.conn() as c:self.assertEqual(c.execute('SELECT quest_index FROM campaign_progress WHERE user_id=?',(self.player,)).fetchone()[0],1)
 def test_paid_tower_floor_can_restore_progress_without_gold_xp_or_quota(self):
  self.apply('level',{'value':5})
  with self.a.conn() as c:c.execute('INSERT INTO activity_ashkar_receipts VALUES(?,?,?,?,?,?)',(self.player,1,10,20,0,time.time()));c.execute('UPDATE ashkar_progress SET max_floor=1 WHERE user_id=?',(self.player,))
  self.apply('tower_floor',{'value':0});state=self.a.tower.snapshot(self.player);self.a.action(self.player,dict(action='ashkar_start',floor=1,revision=state['revision']));before=self.balance();xp=self.a.castle.profile(self.player)['xp'];revision=self.a.tower.snapshot(self.player)['revision']
  with patch('ashkar_arena.step',return_value=(True,True)):self.a.action(self.player,dict(action='ashkar_step',key='light',revision=revision))
  state=self.a.tower.snapshot(self.player);self.assertEqual(state['progress'],1);self.assertEqual(state['daily_cleared'],0);self.assertEqual(self.balance(),before);self.assertEqual(self.a.castle.profile(self.player)['xp'],xp)
 def test_cancelled_expedition_is_not_an_achievement_for_a_story_objective(self):
  self.a.action(self.player,dict(action='start',key='elarwyn_foraging',tool='hands'));self.apply('expedition_cancel')
  with self.a.conn() as c:self.assertFalse(self.a.campaign._expedition_done(c,self.player,{'destination':'elarwyn_foraging'},0))

from types import SimpleNamespace as NS
from unittest.mock import AsyncMock,Mock
import discord_admin_commands as slash
class SlashCommandTests(unittest.IsolatedAsyncioTestCase):
 setUp=AdminCommandTests.setUp
 tearDown=AdminCommandTests.tearDown
 make=AdminCommandTests.make
 def interaction(self,uid,kind='maintenance',app='1529936499775242250'):
  response=NS(defer=AsyncMock(),send_message=AsyncMock(),edit_message=AsyncMock(),is_done=Mock(return_value=False))
  return NS(user=NS(id=int(uid)),application_id=int(app),guild_id=123456789012345679,response=response,followup=NS(send=AsyncMock()),edit_original_response=AsyncMock(),data={'name':slash.NAME,'options':[{'name':kind,'options':[{'name':'lieu','value':'bank'},{'name':'active','value':True},{'name':'motif','value':'Test Discord'}]}]})
 def client(self):return NS(store=NS(service=self.a),validated=True,portal_application='1529936499775242250',http=NS(request=AsyncMock()))
 async def test_unlisted_discord_id_and_wrong_application_rejected(self):
  for uid,app in [(PLAYER,'1529936499775242250'),(ADMIN,'123456789012345679')]:
   i=self.interaction(uid,app=app);await slash.handle(self.client(),i);i.response.send_message.assert_awaited_once();self.assertEqual(self.a.maintenance.public()['closures'],[])
 async def test_preview_then_owner_confirmation_without_public_message(self):
  i=self.interaction(ADMIN);await slash.handle(self.client(),i);i.response.defer.assert_awaited_once_with(ephemeral=True)
  self.assertEqual(self.a.maintenance.public()['closures'],[]);view=i.followup.send.call_args.kwargs['view'];self.assertTrue(i.followup.send.call_args.kwargs['ephemeral'])
  confirm=next(b for b in view.children if b.label=='Confirmer');intruder=self.interaction(PLAYER);await confirm.callback(intruder);self.assertEqual(self.a.maintenance.public()['closures'],[])
  owner=self.interaction(ADMIN);await confirm.callback(owner);self.assertEqual(self.a.maintenance.public()['closures'][0]['scope'],'bank');owner.edit_original_response.assert_awaited_once()
 async def test_registration_upserts_one_command_without_bulk_deletion(self):
  c=self.client();await slash.register(c);c.http.request.assert_awaited_once();self.assertEqual(c.http.request.call_args.args[0].method,'POST');self.assertEqual(c.http.request.call_args.kwargs['json']['name'],'altherya-admin')

from aiohttp import web
from aiohttp.test_utils import TestClient,TestServer
import server,activity as adapter
class AdminCommandHttpTests(unittest.IsolatedAsyncioTestCase):
 make=AdminCommandTests.make
 async def asyncSetUp(self):
  AdminCommandTests.setUp(self);self.previous=adapter.SERVICE;adapter.SERVICE=self.a
  self.tokens={}
  for did in (ADMIN,PLAYER,OTHER):
   (u,n),token=self.a.session('');self.a.snapshot(u,n);self.a.bind_discord(u,dict(id=did,username='Test',global_name='Test',avatar=None,discriminator='0'),token);self.tokens[did]=token
  app=web.Application();app.router.add_post('/api/admin',server.admin);app.router.add_get('/api/activity',adapter.activity);app.router.add_post('/api/activity',adapter.activity)
  self.client=TestClient(TestServer(app));await self.client.start_server()
 async def asyncTearDown(self):
  await self.client.close();adapter.SERVICE=self.previous;self.tmp.cleanup()
 async def post(self,did,body,url='/api/admin'):
  self.client.session.cookie_jar.clear();return await self.client.post(url,json=body,headers={'X-Altherya-Request':'1','Cookie':'altherya_test='+self.tokens[did]})
 async def test_non_admin_cannot_list_or_preview_commands(self):
  for action in ('catalogue','command_preview','command_history'):
   r=await self.post(PLAYER,dict(action=action,command='wallet',player=PLAYER,args={'value':100000},reason='Tentative'));self.assertEqual(r.status,403)
 async def test_confirmation_is_tied_to_authenticated_admin_not_submitted_actor(self):
  p=await(await self.post(ADMIN,dict(action='command_preview',command='wallet',player=PLAYER,args={'value':123},reason='Correction HTTP'))).json()
  r=await self.post(OTHER,dict(action='command_confirm',token=p['token'],actor=ADMIN));self.assertEqual(r.status,400)
  r=await self.post(ADMIN,dict(action='command_confirm',token=p['token']));self.assertEqual(r.status,200);self.assertEqual(self.a.economy.get_balance(self.player).wallet,123)
 async def test_maintenance_rejects_direct_player_api_and_admin_can_reopen(self):
  p=await(await self.post(ADMIN,dict(action='command_preview',command='maintenance',args={'key':'global','enabled':True,'value':0},reason='Travaux HTTP'))).json()
  self.assertEqual((await self.post(ADMIN,dict(action='command_confirm',token=p['token']))).status,200)
  before=self.a.economy.get_balance(self.player).wallet;r=await self.post(PLAYER,dict(action='daily'),'/api/activity');self.assertEqual(r.status,400);self.assertIn('Maintenance',(await r.json())['error']);self.assertEqual(self.a.economy.get_balance(self.player).wallet,before)
  p=await(await self.post(ADMIN,dict(action='command_preview',command='maintenance',args={'key':'global','enabled':False,'value':0},reason='Réouverture HTTP'))).json();self.assertEqual((await self.post(ADMIN,dict(action='command_confirm',token=p['token']))).status,200)
  self.assertEqual((await self.post(PLAYER,dict(action='daily'),'/api/activity')).status,200)
