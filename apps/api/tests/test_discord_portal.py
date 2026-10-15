import asyncio
import json
import os
import sys
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace as NS
from unittest.mock import AsyncMock,Mock,MagicMock,patch

import discord
from discord.webhook.async_ import async_context
sys.path.insert(0,str(Path(__file__).parents[1]))
from activity import Activity
from discord_portal import (CUSTOM_ID,DEFAULT_APP,DEFAULT_CHANNEL,PortalClient,PortalStore,PortalView,PortalError,is_portal,portal_lifecycle,portal_supervisor,portal_art_url)


def http_error(cls,status):
 return cls(NS(status=status,reason='test'),'Erreur de test')

def message(mid='100',bot=42,pinned=True,ours=True):
 return NS(id=int(mid),author=NS(id=bot),components=[NS(children=[NS(custom_id=CUSTOM_ID if ours else 'other')])],pinned=pinned,edit=AsyncMock(),pin=AsyncMock())

class FakeChannel:
 def __init__(self):
  self.messages={};self.recent=[];self.pinned=[];self.failure=None
 async def fetch_message(self,mid):
  if self.failure:raise self.failure
  if mid not in self.messages:raise http_error(discord.NotFound,404)
  return self.messages[mid]
 def pins(self,**kwargs):
  async def gen():
   for m in self.pinned:yield m
  return gen()
 def history(self,**kwargs):
  async def gen():
   for m in self.recent:yield m
  return gen()

class PortalTests(unittest.IsolatedAsyncioTestCase):
 async def asyncSetUp(self):
  self.tmp=tempfile.TemporaryDirectory();self.a=Activity(self.tmp.name+'/db');self.store=PortalStore(self.a)
  self.client=PortalClient(self.store,DEFAULT_CHANNEL,DEFAULT_APP)
  self.client._connection.user=NS(id=42)
  self.client.validated=True;self.client.portal_view=PortalView(self.client)
  self.channel=FakeChannel();self.channel.id=int(DEFAULT_CHANNEL);self.client.fetch_channel=AsyncMock(return_value=self.channel)
  self.type_patch=patch('discord_portal.discord.TextChannel',FakeChannel);self.type_patch.start()
  async def request(route,**kwargs):
   m=message('100',pinned=False);self.channel.messages[100]=m;self.channel.recent=[m]
   return {'id':'100'}
  self.client.http.request=AsyncMock(side_effect=request)
 async def asyncTearDown(self):
  self.type_patch.stop();await self.client.close();self.tmp.cleanup()
 async def test_create_once_then_restart_and_no_edit_churn(self):
  m=await self.client.ensure_portal();await self.client.ensure_portal()
  self.assertEqual(self.client.http.request.await_count,1);m.edit.assert_not_awaited()
  store=PortalStore(Activity(self.a.path));self.assertEqual(store.state(DEFAULT_CHANNEL)['message_id'],'100')
  self.assertEqual(self.client.portal_view.timeout,None);self.assertTrue(self.client.portal_view.is_persistent())
 async def test_concurrent_ready_creates_one_message(self):
  await asyncio.gather(self.client.ensure_portal(),self.client.ensure_portal())
  self.assertEqual(self.client.http.request.await_count,1)
 async def test_button_native_not_external_link(self):
  button=self.client.portal_view.play_button
  self.assertEqual(button.label,'Jouer à Altherya');self.assertEqual(button.custom_id,CUSTOM_ID);self.assertIsNone(button.url)
 async def test_send_uses_nonce_and_no_mentions(self):
  await self.client.ensure_portal();p=self.client.http.request.call_args.kwargs['json']
  self.assertTrue(p['enforce_nonce']);self.assertLessEqual(len(p['nonce']),25);self.assertEqual(p['allowed_mentions'],{'parse':[]})
 async def test_v2_whole_image_then_functional_button(self):
  await self.client.ensure_portal();p=self.client.http.request.call_args.kwargs['json']
  self.assertEqual(p['flags'],32768);self.assertNotIn('content',p);self.assertNotIn('embeds',p)
  container=p['components'][0];self.assertEqual(container['type'],17)
  gallery,row=container['components'];self.assertEqual(gallery['type'],12);self.assertEqual(len(gallery['items']),1)
  self.assertIn('/assets/discord/portal-altherya.png?v=',gallery['items'][0]['media']['url'])
  self.assertEqual(row['type'],1);self.assertEqual(row['components'][0]['custom_id'],CUSTOM_ID)
 async def test_v1_message_migrates_without_duplicate(self):
  m=message();self.channel.messages[100]=m;self.store.state(DEFAULT_CHANNEL);self.store.save(DEFAULT_CHANNEL,'100','v1-hash')
  await self.client.ensure_portal();self.client.http.request.assert_not_awaited()
  p=m.edit.call_args.kwargs;self.assertIsNone(p['content']);self.assertEqual(p['embeds'],[]);self.assertEqual(p['attachments'],[])
  self.assertIsInstance(p['view'],discord.ui.LayoutView)
 async def test_real_sdk_edit_sets_v2_and_clears_v1_fields(self):
  data={'id':'100','channel_id':DEFAULT_CHANNEL,'author':{'id':'42','username':'test','discriminator':'0','avatar':None},'content':'old','embeds':[],'attachments':[],'type':0,'pinned':True,'flags':0,'mentions':[],'mention_roles':[],'components':[]}
  self.client.http.edit_message=AsyncMock(return_value=data)
  m=discord.Message(state=self.client._connection,channel=self.channel,data=data)
  await m.edit(content=None,embeds=[],attachments=[],view=self.client.portal_view,allowed_mentions=discord.AllowedMentions.none())
  payload=self.client.http.edit_message.call_args.kwargs['params'].payload
  self.assertEqual(payload['flags']&32768,32768);self.assertIsNone(payload['content']);self.assertEqual(payload['embeds'],[])
  self.assertEqual(payload['components'][0]['type'],17)
 async def test_nested_v2_portal_recognized(self):
  m=message();m.components=[NS(children=[NS(children=[NS(custom_id=CUSTOM_ID)])])]
  self.assertTrue(is_portal(m,42));self.assertFalse(is_portal(m,123))
 async def test_art_public_url_validation(self):
  with patch.dict(os.environ,{'ALTHERYA_PUBLIC_URL':'http://insecure.test'}):
   with self.assertRaises(PortalError):portal_art_url()
  with patch.dict(os.environ,{'ALTHERYA_PUBLIC_URL':'https://user:secret@example.test'}):
   with self.assertRaises(PortalError):portal_art_url()
 async def test_button_callback_reaches_launch(self):
  self.client.launch=AsyncMock();i=self.interaction()
  await self.client.portal_view.play_button.callback(i);self.client.launch.assert_awaited_once_with(i)
 async def test_recover_pinned_after_database_loss(self):
  m=message();self.channel.pinned=[m];await self.client.ensure_portal()
  self.client.http.request.assert_not_awaited();self.assertEqual(self.store.state(DEFAULT_CHANNEL)['message_id'],'100')
 async def test_recover_recent_send_before_id_commit(self):
  self.channel.recent=[message()];await self.client.ensure_portal();self.client.http.request.assert_not_awaited()
 async def test_forbidden_fetch_never_creates_duplicate(self):
  self.store.state(DEFAULT_CHANNEL);self.store.save(DEFAULT_CHANNEL,'100','old');self.channel.failure=http_error(discord.Forbidden,403)
  with self.assertRaises(discord.Forbidden):await self.client.ensure_portal()
  self.client.http.request.assert_not_awaited()
 async def test_deleted_portal_new_generation(self):
  self.store.state(DEFAULT_CHANNEL);self.store.save(DEFAULT_CHANNEL,'99','old')
  await self.client.ensure_portal();self.assertEqual(self.store.state(DEFAULT_CHANNEL)['generation'],1)
 async def test_other_message_not_overwritten(self):
  m=message(ours=False);self.channel.messages[100]=m;self.store.state(DEFAULT_CHANNEL);self.store.save(DEFAULT_CHANNEL,'100','x')
  with self.assertRaises(PortalError):await self.client.ensure_portal()
  m.edit.assert_not_awaited();self.client.http.request.assert_not_awaited()
 async def test_pin_forbidden_keeps_existing_portal(self):
  m=message(pinned=False);m.pin.side_effect=http_error(discord.Forbidden,403)
  self.channel.recent=[m];self.channel.messages[100]=m
  await self.client.ensure_portal();await self.client.ensure_portal();self.client.http.request.assert_not_awaited()
  self.assertEqual(self.store.state(DEFAULT_CHANNEL)['message_id'],'100')
 async def test_wrong_bot_token_application_rejected(self):
  self.client.application_info=AsyncMock(return_value=NS(id=123,interactions_endpoint_url=None))
  with self.assertRaises(PortalError):await self.client.setup_hook()
 async def test_http_interactions_endpoint_not_overwritten(self):
  self.client.application_info=AsyncMock(return_value=NS(id=int(DEFAULT_APP),interactions_endpoint_url='https://example.test/existing'))
  with self.assertRaises(PortalError):await self.client.setup_hook()
  self.client.http.request.assert_not_awaited()
 async def test_entry_point_patch_only_handler(self):
  self.client.http.request=AsyncMock(side_effect=[[{'id':'123','type':4,'handler':2},{'id':'456','type':1}],{}])
  await self.client.configure_entry_point()
  calls=self.client.http.request.call_args_list;self.assertEqual(len(calls),2);self.assertEqual(calls[1].kwargs['json'],{'handler':1});self.assertEqual(calls[1].args[0].method,'PATCH')
 async def test_custom_entry_point_not_patched_again(self):
  self.client.http.request=AsyncMock(return_value=[{'id':'123','type':4,'handler':1}])
  await self.client.configure_entry_point();self.assertEqual(self.client.http.request.await_count,1)
 async def test_missing_entry_point_created_without_bulk_sync(self):
  self.client.http.request=AsyncMock(side_effect=[[],{'id':'123'}]);await self.client.configure_entry_point()
  p=self.client.http.request.call_args.kwargs['json'];self.assertEqual((p['type'],p['handler']),(4,1));self.assertEqual(self.client.http.request.call_args.args[0].method,'POST')
 def interaction(self,channel=DEFAULT_CHANNEL,uid=7):
  return NS(application_id=int(DEFAULT_APP),guild_id=123,channel_id=int(channel),user=NS(id=uid),response=NS(launch_activity=AsyncMock(),send_message=AsyncMock(),is_done=Mock(return_value=False)),type=discord.InteractionType.application_command,data={'id':'123'})
 async def test_launch_only_no_public_message_or_followup(self):
  i=self.interaction();await self.client.launch(i);i.response.launch_activity.assert_awaited_once();i.response.send_message.assert_not_awaited();self.client.http.request.assert_not_awaited()
 async def test_duplicate_click_ephemeral_only(self):
  i=self.interaction();await self.client.launch(i);await self.client.launch(i)
  i.response.launch_activity.assert_awaited_once();self.assertTrue(i.response.send_message.call_args.kwargs['ephemeral'])
 async def test_wrong_channel_no_launch(self):
  i=self.interaction(channel='1551927433475788880');await self.client.launch(i)
  i.response.launch_activity.assert_not_awaited();self.assertTrue(i.response.send_message.call_args.kwargs['ephemeral'])
 async def test_launch_failure_can_be_retried(self):
  i=self.interaction();i.response.launch_activity.side_effect=http_error(discord.HTTPException,400)
  await self.client.launch(i);self.assertNotIn(7,self.client.launches)
  i.response.launch_activity.side_effect=None;await self.client.launch(i);self.assertEqual(i.response.launch_activity.await_count,2)
 async def test_entry_point_launches_same_path(self):
  i=self.interaction();self.client.entry_point_id='123';await self.client.on_interaction(i);i.response.launch_activity.assert_awaited_once()
 async def test_unknown_command_ignored(self):
  i=self.interaction();self.client.entry_point_id='999';await self.client.on_interaction(i);i.response.launch_activity.assert_not_awaited()
 async def test_leader_lease(self):
  self.assertTrue(self.store.lease(DEFAULT_CHANNEL,'one',100));self.assertFalse(self.store.lease(DEFAULT_CHANNEL,'two',110));self.assertTrue(self.store.lease(DEFAULT_CHANNEL,'one',120))
  self.assertTrue(self.store.lease(DEFAULT_CHANNEL,'two',211));self.store.release(DEFAULT_CHANNEL,'one');self.assertFalse(self.store.lease(DEFAULT_CHANNEL,'three',212))
 async def test_no_token_no_gateway(self):
  with patch.dict(os.environ,{'DISCORD_BOT_TOKEN':''}),patch('discord_portal.portal_supervisor',new_callable=AsyncMock) as start:
   ctx=portal_lifecycle({});await anext(ctx);await ctx.aclose();start.assert_not_called()
 async def test_disabled_no_gateway(self):
  with patch.dict(os.environ,{'ALTHERYA_PORTAL_ENABLED':'0'}):
   ctx=portal_lifecycle({});await anext(ctx);await ctx.aclose()
 async def test_wrong_author_not_adopted(self):
  self.assertFalse(is_portal(message(bot=999),42))
 async def test_library_wire_response_type_12(self):
  # Exercise discord.py's real response method, replacing only its HTTP transport.
  parent=NS(id=123,token='test-only',_session=object(),_state=NS(http=NS(proxy=None,proxy_auth=None)))
  transport=NS(create_interaction_response=AsyncMock(return_value={'interaction':{'id':'123','activity_instance_id':'fixture'},'resource':{'type':12,'activity_instance':{'id':'fixture'}}}))
  marker=async_context.set(transport)
  try:
   response=discord.InteractionResponse(parent);result=await response.launch_activity()
   params=transport.create_interaction_response.call_args.kwargs['params']
   self.assertEqual(params.payload,{'type':12});self.assertEqual(result.activity_id,'fixture')
  finally:async_context.reset(marker)

class RestoreTests(unittest.IsolatedAsyncioTestCase):
 async def test_restore_missing_token(self):
  from portal_restore_entry import restore
  with patch.dict(os.environ,{'DISCORD_BOT_TOKEN':''}):
   with self.assertRaises(SystemExit):await restore()
 def fake_client(self,app=int(DEFAULT_APP),commands=None):
  client=MagicMock();client.__aenter__=AsyncMock(return_value=client);client.__aexit__=AsyncMock(return_value=False)
  client.login=AsyncMock();client.application_info=AsyncMock(return_value=NS(id=app));client.http.request=AsyncMock(side_effect=[commands or [],{}]);return client
 async def test_restore_wrong_application_refused(self):
  from portal_restore_entry import restore
  client=self.fake_client(app=123)
  with patch.dict(os.environ,{'DISCORD_BOT_TOKEN':'test-only','DISCORD_CLIENT_ID':DEFAULT_APP}),patch('portal_restore_entry.discord.Client',return_value=client):
   with self.assertRaises(SystemExit):await restore()
  client.http.request.assert_not_awaited()
 async def test_restore_no_entry_no_write(self):
  from portal_restore_entry import restore
  client=self.fake_client()
  with patch.dict(os.environ,{'DISCORD_BOT_TOKEN':'test-only','DISCORD_CLIENT_ID':DEFAULT_APP}),patch('portal_restore_entry.discord.Client',return_value=client):
   with self.assertRaises(SystemExit):await restore()
  self.assertEqual(client.http.request.await_count,1)
 async def test_restore_only_handler_two(self):
  from portal_restore_entry import restore
  client=self.fake_client(commands=[{'id':'123','type':4},{'id':'456','type':1}])
  with patch.dict(os.environ,{'DISCORD_BOT_TOKEN':'test-only','DISCORD_CLIENT_ID':DEFAULT_APP}),patch('portal_restore_entry.discord.Client',return_value=client),patch('builtins.print'):
   await restore()
  self.assertEqual(client.http.request.call_args.kwargs['json'],{'handler':2})
  self.assertEqual(client.http.request.call_args.args[0].method,'PATCH')

if __name__=='__main__':unittest.main()
