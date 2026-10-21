"""Regression tests for attack paths confirmed by the October 2026 audit."""
import json,os,tempfile,unittest,sys
from pathlib import Path
from unittest.mock import patch
sys.path.insert(0,str(Path(__file__).parents[1]))
from activity import Activity
from tutorial import ActivityTutorial
import test_play as fixtures
setUpFixture=fixtures.GameTests.setUp

class SecurityAuditTests(unittest.TestCase):
 setUp=setUpFixture
 tearDown=fixtures.GameTests.tearDown
 s=fixtures.GameTests.s
 act=fixtures.GameTests.act
 access=fixtures.GameTests.access
 blackjack_hand=fixtures.GameTests.blackjack_hand
 # Reuse fixtures, not all the base test methods.
 def test_revealed_blackjack_cannot_be_cancelled_for_a_refund(self):
  self.blackjack_hand([10,6],[10,7],[10]);before=self.s()['balance']['wallet'];revision=self.s()['play']['revision']
  with self.assertRaises(ValueError):self.act(action='game_cancel')
  self.assertEqual(self.s()['balance']['wallet'],before);self.assertEqual(self.s()['play']['revision'],revision)
  self.act(action='game_step',key='hit');self.assertEqual(self.s()['play']['payout'],0)
 def test_russian_cancellation_cannot_create_a_free_option(self):
  self.access()
  with patch('play.random.randint',return_value=6):self.act(action='game_start',key='russian',wager=100)
  self.act(action='game_step',key='try');before=self.s()['balance']['wallet']
  with self.assertRaises(ValueError):self.act(action='game_cancel')
  self.assertEqual(self.s()['balance']['wallet'],before);self.assertEqual(self.s()['play']['status'],'active')
 def test_access_expiry_does_not_refund_an_unfavourable_hand(self):
  self.blackjack_hand([10,6],[10,7],[10]);before=self.s()['balance']['wallet']
  with patch.object(self.a.play.dark,'has_clandestine_access',return_value=False):self.act(action='game_step',key='hit')
  self.assertEqual(self.s()['play']['status'],'finished');self.assertEqual(self.s()['play']['payout'],0);self.assertEqual(self.s()['balance']['wallet'],before)
 def test_campaign_battle_blocks_other_rounds_and_equipment_changes(self):
  with self.a.conn() as c:c.execute('UPDATE campaign_progress SET payload=? WHERE user_id=?',(json.dumps({'battle':{'finished':False}}),self.uid))
  before=self.a.economy.get_balance(self.uid)
  for body in [dict(action='game_start',key='dice',wager=10),dict(action='battle_start',wager=10),dict(action='arena_equip',slot='light',technique='base_light',loadout_revision=0)]:
   with self.assertRaises(ValueError):self.a.action(self.uid,dict(revision=0,**body))
  self.assertEqual(self.a.economy.get_balance(self.uid),before)
 def test_active_arena_blocks_a_campaign_battle_start(self):
  self.act(action='battle_start',wager=10)
  with self.assertRaisesRegex(ValueError,'Terminez votre partie'):self.a.action(self.uid,dict(action='campaign_battle',key='start',quest_id='forged',revision=0))
 def test_chapter_integer_is_not_coerced_from_untrusted_values(self):
  for chapter in [True,1.5,'1',None,[],100000]:
   with self.assertRaises(ValueError):self.a.action(self.uid,dict(action='story_unlock',chapter=chapter))
 def test_partial_oauth_configuration_cannot_enable_anonymous_play(self):
  for env in [dict(DISCORD_CLIENT_ID='123',DISCORD_CLIENT_SECRET=''),dict(DISCORD_CLIENT_ID='',DISCORD_CLIENT_SECRET='test')]:
   with patch.dict(os.environ,env):
    self.assertTrue(ActivityTutorial.discord_required())
    with self.assertRaisesRegex(ValueError,'Connexion Discord requise'):self.a.action(self.uid,dict(action='daily'))

from aiohttp import web
from aiohttp.test_utils import TestClient,TestServer
import activity as adapter
class RejectedRequestTests(unittest.IsolatedAsyncioTestCase):
 async def test_cross_site_post_does_not_allocate_an_anonymous_character(self):
  with tempfile.TemporaryDirectory() as folder:
   a=Activity(folder+'/test.db');old=adapter.SERVICE;adapter.SERVICE=a
   app=web.Application();app.router.add_post('/api/activity',adapter.activity)
   client=TestClient(TestServer(app));await client.start_server()
   try:
    response=await client.post('/api/activity',json={'action':'daily'})
    self.assertEqual(response.status,403)
    with a.conn() as c:self.assertEqual(c.execute('SELECT COUNT(*) FROM activity_sessions').fetchone()[0],0)
   finally:await client.close();adapter.SERVICE=old

import ast
from types import SimpleNamespace
from unittest.mock import AsyncMock,Mock
import discord
BOT=Path(__file__).parents[2]/'bot'/'tourwork'
def definition(filename,name,namespace):
 tree=ast.parse((BOT/filename).read_text());part=next(n for n in tree.body if isinstance(n,(ast.ClassDef,ast.AsyncFunctionDef)) and n.name==name)
 module=ast.Module(body=[ast.ImportFrom(module='__future__',names=[ast.alias(name='annotations')],level=0),part],type_ignores=[])
 exec(compile(ast.fix_missing_locations(module),filename,'exec'),namespace);return namespace[name]
class LegacyBotAuditTests(unittest.IsolatedAsyncioTestCase):
 async def test_admin_achievement_announcement_has_a_defined_branch_size(self):
  ach=SimpleNamespace(branch='combat',branch_emoji='X',title='Titre',description='Texte',color=1,branch_label='Combat',rarity_emoji='X',rarity='Rare')
  channel=SimpleNamespace(send=AsyncMock());store=SimpleNamespace(get_channel=lambda _:1,branch_progress=lambda *_:1)
  fn=definition('main.py','announce_achievement_for',dict(discord=discord,ACHIEVEMENTS={'one':ach,'two':ach},ACHIEVEMENT_STORE=store,bot=SimpleNamespace(get_channel=lambda _:channel)))
  await fn(SimpleNamespace(id=1),SimpleNamespace(id=2,mention='Joueur',display_avatar=SimpleNamespace(url='https://example.invalid/avatar.png')),'one')
  embed=channel.send.call_args.kwargs['embed'];self.assertEqual(embed.fields[-1].value,'**1/2**')
 async def test_identity_back_uses_the_existing_welcome_view_and_checks_its_owner(self):
  sentinel=object();welcome=Mock(return_value=sentinel)
  cls=definition('accueil.py','IdentityView',dict(discord=discord,_lang=lambda *_:'fr',WelcomePublicView=welcome,_container=lambda *items:discord.ui.Container(*items),_sep=lambda:discord.ui.Separator()))
  view=cls(1,2);button=next(n for n in view.walk_children() if isinstance(n,discord.ui.Button) and n.label=='Retour')
  response=SimpleNamespace(edit_message=AsyncMock(),send_message=AsyncMock())
  await button.callback(SimpleNamespace(user=SimpleNamespace(id=3),response=response));response.edit_message.assert_not_called()
  await button.callback(SimpleNamespace(user=SimpleNamespace(id=2),response=response));welcome.assert_called_once_with('fr');response.edit_message.assert_awaited_once_with(view=sentinel)

class LegacyWagerAuditTests(unittest.IsolatedAsyncioTestCase):
 async def test_revealed_round_timeout_settles_zero_instead_of_refunding(self):
  for name,state_key in [('BlackjackView','BLACKJACK_STATES'),('RussianRouletteView','RUSSIAN_STATES')]:
   store=SimpleNamespace(settle=Mock(),refund=Mock());states={'round':{}}
   cls=definition('main.py',name,dict(discord=discord,CASINO_STORE=store,BLACKJACK_FINISHING=set(),**{state_key:states}))
   view=cls(1,'round');await view.on_timeout();store.settle.assert_called_once_with('round',0);store.refund.assert_not_called();self.assertNotIn('round',states)
 async def test_expired_entry_still_allows_a_revealed_round_to_settle(self):
  dark=SimpleNamespace(has_clandestine_access=lambda _:False);store=SimpleNamespace(refund=Mock());eject=AsyncMock()
  fn=definition('main.py','casino_access_or_eject',dict(DARK_STORE=dark,CASINO_STORE=store,BLACKJACK_STATES={'round':{}},RUSSIAN_STATES={},eject_from_casino=eject))
  self.assertTrue(await fn(SimpleNamespace(user=SimpleNamespace(id=1)),'round'));store.refund.assert_not_called();eject.assert_not_awaited()
