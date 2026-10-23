"""Regression checks for the ordered October 23 campaign audit."""
import json,sys,time,unittest
from pathlib import Path
from unittest.mock import patch
sys.path.insert(0,str(Path(__file__).parents[1]))
import test_campaign as harness
from activity import Activity
from campaign import QUESTS
from campaign_rewards import quote
from expedition_engine import RESOURCE_SELL_PRICES

class CampaignAuditTests(unittest.TestCase):
 setUp=harness.CampaignTests.setUp
 tearDown=harness.CampaignTests.tearDown
 s=harness.CampaignTests.s
 act=harness.CampaignTests.act
 position=harness.CampaignTests.position
 fast_time=harness.CampaignTests.fast_time

 def test_quote_is_frozen_on_accept_and_survives_steps_restart_and_claim(self):
  self.act('campaign_accept',gold=999999,xp=999999);q=self.s()['quest'];self.assertEqual((q['gold'],q['xp']),(10,20))
  with patch('campaign.reward_quote',return_value=dict(gold=999,xp=999)):
   self.act('campaign_step');self.a=Activity(self.a.path);self.assertEqual(self.s()['quest']['gold'],10)
   self.act('campaign_enter',place_id='convois')
   for clue in self.s()['quest']['steps'][1]['clues']:self.act('campaign_explore',clue_id=clue['id'])
   self.act('campaign_step');self.act('campaign_step');self.fast_time();before=self.a.snapshot(self.uid,self.name);self.act('campaign_claim');after=self.a.snapshot(self.uid,self.name)
   self.assertEqual(after['balance']['wallet']-before['balance']['wallet'],10);self.assertEqual(after['stats']['xp']-before['stats']['xp'],20)

 def test_accepted_previous_editions_keep_original_rewards(self):
  for edition in (2,3,4):
   self.position(8,payload={'edition':edition})
   q=self.s()['quest'];self.assertEqual((q['gold'],q['xp']),(QUESTS[8]['gold'],QUESTS[8]['xp']))
   self.a=Activity(self.a.path);self.assertEqual(self.s()['quest']['gold'],QUESTS[8]['gold'])

 def test_reward_effort_and_delivery_value(self):
  base=dict(id='S1-Q03',season=1,steps=[dict(kind='talk')])
  simple=quote(base)
  for step in [dict(kind='battle',boss=True),dict(kind='port'),dict(kind='expedition',destination='vorak_3')]:
   advanced=quote({**base,'steps':base['steps']+[step]});self.assertGreater(advanced['gold'],simple['gold']);self.assertGreater(advanced['xp'],simple['xp'])
  delivery=dict(kind='deliver',resource='Bois de chêne',quantity=5);r=quote({**base,'steps':[delivery]});self.assertGreaterEqual(r['gold'],5*RESOURCE_SELL_PRICES['Bois de chêne'])
  for original in QUESTS:
   r=quote(original);self.assertTrue(0<r['gold']<=75);self.assertTrue(0<r['xp']<=150)

 def test_dialogue_returns_the_active_step_text(self):
  self.act('campaign_accept');s=self.s();step=s['quest']['steps'][0]
  self.assertEqual(self.act('campaign_step'),step.get('text') or s['quest']['dialogue'])

 def prepare_expedition(self,old_first=False):
  self.position(6,0,payload={'edition':5});now=int(time.time())+.6
  with patch('time.time',return_value=now):
   if old_first:self.a.action(self.uid,dict(action='start',key='elarwyn_foraging',tool='hands'))
   self.act('campaign_step')
   if not old_first:self.a.action(self.uid,dict(action='start',key='elarwyn_foraging',tool='hands'))
  run=self.a.expeditions.active_run(self.uid)
  with patch('time.time',return_value=run.ends_at+2):self.a.reconcile(self.uid)
  return run

 def test_same_second_prior_voyage_cannot_complete_new_objective(self):
  self.prepare_expedition(old_first=True);self.assertFalse(self.s()['expedition_ready'])
  with self.assertRaises(ValueError):self.act('campaign_step')

 def test_same_second_new_voyage_can_complete_objective(self):
  self.prepare_expedition();self.assertTrue(self.s()['expedition_ready']);self.act('campaign_step');self.assertEqual(self.s()['stage'],2)

 def test_empty_legacy_loot_cannot_validate_quest(self):
  run=self.prepare_expedition()
  with self.a.conn() as c:c.execute('UPDATE expedition_runs SET loot_json=? WHERE run_id=?',('{}',run.run_id))
  self.assertFalse(self.s()['expedition_ready'])

 def test_ineligible_tool_is_rejected_without_creating_run(self):
  self.position(27)
  with self.a.conn() as c:c.execute('UPDATE players SET wallet_gold=2000 WHERE user_id=?',(self.uid,))
  for equipment in ('bag','spear','pickaxe'):self.assertTrue(self.a.expeditions.buy_starter(self.uid,equipment)[0])
  ok,message,run=self.a.expeditions.start(self.uid,'vorak_3','spear',bag_level=1,tool_level=1)
  self.assertFalse(ok);self.assertIn('trop faible',message);self.assertIsNone(run);self.assertIsNone(self.a.expeditions.active_run(self.uid))
  ok,_,run=self.a.expeditions.start(self.uid,'vorak_3','pickaxe',bag_level=1,tool_level=1)
  self.assertTrue(ok);self.assertTrue(run.loot)

 def equip(self):
  with self.a.conn() as c:
   c.execute('INSERT INTO activity_arena_techniques VALUES(?,1)',(self.uid,));c.execute('INSERT INTO activity_arena_loadout VALUES(?,?,?)',(self.uid,'heavy','c1'))

 def test_main_combat_uses_and_preserves_equipped_technique(self):
  self.position(7,2,payload={'edition':5});self.equip()
  # Edition 4+ inserts the port objective before this battle.
  self.act('campaign_battle',key='start');self.assertEqual(self.s()['battle']['skills']['heavy']['id'],'c1')
  self.a=Activity(self.a.path)
  with patch('arena_engine.random.random',return_value=.4):self.act('campaign_battle',key='heavy')
  self.assertIn('Lacération',' '.join(self.s()['battle']['log']));self.assertIn('saignement',' '.join(self.s()['battle']['log']))
  with self.assertRaises(ValueError):self.a.action(self.uid,dict(action='arena_equip',slot='heavy',technique='base_heavy',loadout_revision=0))
  with self.assertRaises(ValueError):self.a.action(self.uid,dict(action='game_start',key='coin',wager=1))

 def test_old_active_base_combat_remains_playable(self):
  self.position(7,1,payload={'edition':2});self.act('campaign_battle',key='start')
  with self.a.conn() as c:
   row=self.a.campaign.row(c,self.uid);p=json.loads(row['payload']);p.pop('skills');c.execute('UPDATE campaign_progress SET payload=? WHERE user_id=?',(json.dumps(p),self.uid))
  self.a=Activity(self.a.path);self.act('campaign_battle',key='light');self.assertIsNone(self.s()['battle']['skills'])

 def test_interception_respects_all_four_prior_choice_combinations(self):
  from campaign_story import playable_branch
  q=QUESTS[28]
  for rescue in (False,True):
   for blockade in (False,True):
    choices={'S2-Q07':'Secourir directement les convoyeurs' if rescue else 'Prévenir les renforts','S4-Q03':'Préparer un barrage autorisé' if blockade else 'Installer un leurre'}
    branch=playable_branch(q,choices);stage=next(i for i,s in enumerate(branch['steps']) if s['kind']=='battle');self.position(28,stage,payload={'edition':5,'choices':choices});self.act('campaign_battle',key='start')
    with self.a.conn() as c:enemy=json.loads(self.a.campaign.row(c,self.uid)['payload'])['battle']['fighters'][1]
    self.assertEqual(enemy['class_key'],'gardien' if blockade else 'ravageur')
    step=branch['steps'][stage];expected=round((100+10*(q['min_level']-1))*(1.3 if step.get('boss') else 1.05)*(.9 if rescue else 1));self.assertEqual(enemy['max_hp'],expected)

if __name__=='__main__':unittest.main()
