import json,time,unittest
import test_trading as trade
from activity import Activity
from campaign import effective_quest,QUESTS

class AdventureTests(unittest.TestCase):
 setUp=trade.TradeTests.setUp
 tearDown=trade.TradeTests.tearDown
 make=trade.TradeTests.make
 offer=trade.TradeTests.offer
 def act(self,key='',action='training',**kw):return self.a.action(self.buyer,dict(action='adventure_'+action,key=key,**kw))
 def view(self):return self.a.snapshot(self.buyer,'Test')['adventure']
 def test_training_uses_real_skills_but_never_rewards_or_attempts(self):
  before=self.a.snapshot(self.buyer,'Test');self.act('start',mode='guard');t=self.view()['training'];self.act('light',revision=t['revision']);t=self.view()['training'];self.assertTrue(t['logs']);self.assertLess(t['fighters'][1]['hp'],t['fighters'][1]['max_hp'])
  with self.assertRaises(ValueError):self.act('heavy',revision=t['revision']-1)
  self.act('stop',revision=t['revision']);after=self.a.snapshot(self.buyer,'Test')
  for k in ('balance','xp','resources'):self.assertEqual(before[k],after[k])
  self.assertEqual(before['arena']['remaining'],after['arena']['remaining']);self.assertEqual(before['stats'],after['stats'])
 def test_training_request_replay_cannot_double_turn(self):
  self.act('start');t=self.view()['training'];data=dict(action='adventure_training',key='light',revision=t['revision'],request_id='adventure-replay-00001');self.a.action(self.buyer,data);after=self.view()['training'];self.a.action(self.buyer,data);self.assertEqual(self.view()['training'],after)
 def test_training_forges_no_locked_techniques(self):
  self.act('start');self.assertTrue(all(x['id'].startswith('base_') for x in self.view()['training']['skills'].values()))
  with self.assertRaises(ValueError):self.act('c10',revision=self.view()['training']['revision'])
 def test_favorites_are_owner_scoped_and_send_zero_reward_mail_once_daily(self):
  self.act('Pierre brute',action='favorite');self.offer();self.offer();self.assertEqual(len(self.a.mailbox.listing(self.buyer,0)['entries']),1);self.assertFalse(self.a.mailbox.listing(self.seller,0)['entries']);fav=self.view()['favorites'][0];self.assertEqual(fav['available'],2);self.assertIsNone(fav['unit_median'])
  with self.assertRaises(ValueError):self.act('<script>',action='favorite')
 def test_favorite_price_is_only_completed_sale(self):
  self.act('Pierre brute',action='favorite');key=self.offer(quantity=10,price=50);self.a.action(self.other,dict(action='trade_buy',key=key,price=50));fav=self.view()['favorites'][0];self.assertEqual(fav['sales'],1);self.assertEqual(fav['unit_median'],5)
 def test_journey_choice_cannot_be_forged_early_or_repeated(self):
  self.a.action(self.buyer,dict(action='start',key='elarwyn_foraging',tool='hands'));e=self.view()['event']
  with self.assertRaises(ValueError):self.act('observe',action='event',run_id=e['run_id'])
  now=int(time.time())
  with self.a.conn() as c:c.execute('UPDATE expedition_runs SET started_at=?,ends_at=? WHERE run_id=?',(now-600,now+300,e['run_id']))
  self.act('observe',action='event',run_id=e['run_id']);self.assertEqual(self.view()['event']['choice'],'observe')
  with self.assertRaises(ValueError):self.act('hurry',action='event',run_id=e['run_id'])
  with self.assertRaises(ValueError):self.a.action(self.seller,dict(action='adventure_event',key='observe',run_id=e['run_id']))
 def test_journey_bonus_settles_once_on_restart(self):
  self.a.action(self.buyer,dict(action='start',key='elarwyn_foraging',tool='hands'));e=self.view()['event'];now=int(time.time())
  with self.a.conn() as c:c.execute('UPDATE expedition_runs SET started_at=?,ends_at=? WHERE run_id=?',(now-600,now+300,e['run_id']))
  self.act('observe',action='event',run_id=e['run_id']);run=self.a.expeditions.active_run(self.buyer);base=sum(run.loot.values())
  with self.a.conn() as c:c.execute('UPDATE expedition_runs SET ends_at=0 WHERE run_id=?',(e['run_id'],))
  after=self.a.snapshot(self.buyer,'Test');self.assertEqual(sum(after['resources'].values()),base+1)
  self.a=Activity(self.path);self.assertEqual(self.a.snapshot(self.buyer,'Test')['resources'],after['resources']);self.assertEqual(self.view()['professions'][3]['runs'],1)
 def test_specialization_requires_real_completed_runs_and_is_permanent(self):
  with self.assertRaises(ValueError):self.act('swift',action='specialize',tool='hands')
  for _ in range(5):
   self.a.action(self.buyer,dict(action='start',key='elarwyn_foraging',tool='hands'))
   with self.a.conn() as c:c.execute('UPDATE expedition_runs SET ends_at=0 WHERE user_id=?',(self.buyer,))
   self.a.snapshot(self.buyer,'Test')
  self.act('swift',action='specialize',tool='hands')
  with self.assertRaises(ValueError):self.act('steady',action='specialize',tool='hands')
  self.a.action(self.buyer,dict(action='start',key='elarwyn_foraging',tool='hands'));run=self.a.expeditions.active_run(self.buyer);from expedition_engine import EXPEDITIONS
  self.assertEqual(run.ends_at-run.started_at,round(EXPEDITIONS['elarwyn_foraging']['duration']*.95))
 def test_goal_and_titles_validate_and_persist(self):
  self.act('pickaxe',action='goal');self.assertEqual(self.view()['goal'],'pickaxe')
  with self.assertRaises(ValueError):self.act('master',action='title')
  self.a=Activity(self.path);self.assertEqual(self.view()['goal'],'pickaxe')
 def test_daily_replacement_is_once_and_never_forge_or_locked_place(self):
  before=self.a.snapshot(self.buyer,'Test');q=next(q for q in before['quests'] if not q['progress']);self.act(q['key'],action='daily');after=self.a.snapshot(self.buyer,'Test');self.assertEqual(len(after['quests']),3);self.assertEqual(before['quest_reward'],after['quest_reward']);self.assertFalse(any(q['key'] in ('forge_upgrade','tower') for q in after['quests']))
  with self.assertRaises(ValueError):self.act(after['quests'][0]['key'],action='daily')
 def test_daily_started_or_claimed_is_not_rerollable(self):
  qs=self.a.snapshot(self.buyer,'Test')['quests'];q=qs[0]
  with self.a.conn() as c:c.execute('UPDATE castle_daily_progress SET progress=1 WHERE user_id=? AND quest_key=?',(self.buyer,q['key']))
  with self.assertRaises(ValueError):self.act(q['key'],action='daily')
 def test_maintenance_covers_new_features_and_health_is_admin_only(self):
  with self.a.conn() as c:c.execute("INSERT INTO activity_maintenance VALUES('arena','test',0,'admin',?)",(time.time(),))
  with self.assertRaises(ValueError):self.act('start')
  with self.assertRaises(PermissionError):self.a.admin.handle(self.buyer,dict(action='health'))
  health=self.a.adventure.health();self.assertEqual(health['integrity'],'ok');self.assertGreaterEqual(health['total_gold'],0)
 def test_branch_keeps_accepted_previous_editions_and_catalog_immutable(self):
  idx=next(i for i,q in enumerate(QUESTS) if q['id']=='S2-Q08');original=json.dumps(QUESTS);choice={'S2-Q07':'Secourir directement les convoyeurs'};row=dict(accepted_at=time.time(),quest_index=idx)
  old=effective_quest(row,dict(edition=2,choices=choice));self.assertEqual({k:old[k] for k in QUESTS[idx] if k!='steps'},{k:v for k,v in QUESTS[idx].items() if k!='steps'});self.assertEqual([{k:step[k] for k in base} for step,base in zip(old['steps'],QUESTS[idx]['steps'])],QUESTS[idx]['steps']);new=effective_quest(row,dict(edition=3,choices=choice));self.assertEqual(len(new['steps']),len(QUESTS[idx]['steps'])+1);self.assertIn('témoignages',new['steps'][0]['label']);self.assertEqual(json.dumps(QUESTS),original)
 def test_diagnostics_store_no_sensitive_exception_text(self):
  import asyncio
  from types import SimpleNamespace
  from runtime_health import runtime_health
  async def broken(request):raise RuntimeError('secret-token-do-not-store')
  middleware=runtime_health(lambda:self.a)
  with self.assertRaises(RuntimeError):asyncio.run(middleware(SimpleNamespace(path='/api/private'),broken))
  rows=self.a.adventure.health()['errors'];self.assertEqual(rows[0]['code'],'RuntimeError');self.assertNotIn('secret-token',str(rows))
 def test_meticulous_bonus_does_not_pay_retroactively_or_twice(self):
  def trip():
   self.a.action(self.buyer,dict(action='start',key='elarwyn_foraging',tool='hands'))
   with self.a.conn() as c:c.execute('UPDATE expedition_runs SET ends_at=0 WHERE user_id=?',(self.buyer,))
   return self.a.snapshot(self.buyer,'Test')
  for _ in range(5):trip()
  before=self.a.expeditions.get_resources(self.buyer);self.act('steady',action='specialize',tool='hands');self.assertEqual(before,self.a.expeditions.get_resources(self.buyer))
  for _ in range(5):after=trip()
  self.assertEqual(sum(after['resources'].values()),61);self.assertEqual(self.a.snapshot(self.buyer,'Test')['resources'],after['resources'])
