"""Scene requirements, quest-prop isolation and durable presence; never bypass auth."""
import json,sys,time,unittest
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
sys.path.insert(0,str(Path(__file__).parents[1]))
from activity import Activity
from campaign import QUESTS,effective_quest
from campaign_world import SCENES,decorate
import test_campaign as harness
class CampaignWorldTests(unittest.TestCase):
 setUp=harness.CampaignTests.setUp
 tearDown=harness.CampaignTests.tearDown
 s=harness.CampaignTests.s
 position=harness.CampaignTests.position
 fast_time=harness.CampaignTests.fast_time
 def enter(self,scene):self.a.action(self.uid,dict(action='campaign_world_enter',scene=scene));return self.s()
 def body(self,action='campaign_step',**extra):
  s=self.s();return dict(action=action,quest_id=s['quest']['id'],revision=s['revision'],world_token=s['world']['token'],**extra)
 def test_no_journal_or_remote_acceptance_or_dialogue(self):
  with self.assertRaisesRegex(ValueError,'Rejoignez'):self.a.action(self.uid,self.body('campaign_accept'))
  self.enter('bank')
  with self.assertRaisesRegex(ValueError,'Rejoignez'):self.a.action(self.uid,self.body('campaign_accept'))
  self.enter('hub');self.a.action(self.uid,self.body('campaign_accept'));self.a.action(self.uid,self.body());self.enter('market')
  with self.assertRaisesRegex(ValueError,'Rejoignez'):self.a.action(self.uid,self.body('campaign_explore',clue_id='S1-Q01-O2-I1'))
 def test_tokens_rotate_and_cannot_be_borrowed_or_unicode_crash(self):
  self.enter('hub');body=self.body('campaign_accept');self.enter('hub')
  with self.assertRaises(ValueError):self.a.action(self.uid,body)
  for token in (True,None,'ééé','forged'):
   body=self.body('campaign_accept');body['world_token']=token
   with self.assertRaises(ValueError):self.a.action(self.uid,body)
 def test_wrong_scene_and_missing_revision_cannot_complete_delivery(self):
  self.position(10,payload={'edition':6});self.a.expeditions.add_resources(self.uid,{'Bois de chêne':5});self.enter('market');before=self.a.expeditions.get_resources(self.uid)
  with self.assertRaises(ValueError):self.a.action(self.uid,self.body())
  self.assertEqual(before,self.a.expeditions.get_resources(self.uid));self.enter('khaz');body=self.body();body['revision']=True
  with self.assertRaises(ValueError):self.a.action(self.uid,body)
  self.a.action(self.uid,self.body());self.assertEqual(self.a.expeditions.get_resources(self.uid).get('Bois de chêne',0),0)
 def test_objects_are_found_once_at_search_point_then_handed_over(self):
  self.enter('hub');self.a.action(self.uid,self.body('campaign_accept'));self.a.action(self.uid,self.body());self.enter('convois');step=self.s()['quest']['steps'][1];before=self.a.snapshot(self.uid,self.name)
  body=self.body('campaign_explore',clue_id=step['clues'][0]['id'])
  def run(_):
   try:self.a.action(self.uid,body);return 1
   except ValueError:return 0
  with ThreadPoolExecutor(2) as pool:self.assertEqual(sum(pool.map(run,range(2))),1)
  for clue in step['clues'][1:]:self.a.action(self.uid,self.body('campaign_explore',clue_id=clue['id']))
  self.assertEqual(len(self.s()['world']['items']),1);self.assertIsNone(self.s()['world']['items'][0]['delivered_at']);self.assertEqual(before['resources'],self.a.expeditions.get_resources(self.uid));self.a=Activity(self.a.path);self.assertEqual(len(self.s()['world']['items']),1)
  self.a.action(self.uid,self.body());self.enter('market');self.a.action(self.uid,self.body());self.assertIsNotNone(self.s()['world']['items'][0]['delivered_at'])
 def test_new_plaque_is_found_in_forest_but_legacy_objective_stays(self):
  self.position(4,2,payload={'edition':6});s=self.s();self.assertEqual(s['world']['target'],'lisiere');self.enter('lisiere');self.a.action(self.uid,self.body());self.assertEqual(self.s()['stage'],3);self.assertIn('plaque',[i['item_id'] for i in self.s()['world']['items']]);self.position(4,2,payload={'edition':5});self.assertEqual(self.s()['world']['target'],'forge')
 def test_quest_location_is_gated_by_story_and_level(self):
  for scene in ('archives','veille','khaz','ashkar','unknown'):
   with self.assertRaises(ValueError):self.enter(scene)
  self.assertIsNone(self.s()['world']['scene'])
 def test_maintenance_of_quest_or_place_does_not_lock_other_travel(self):
  with self.a.conn() as c:c.execute('INSERT INTO activity_maintenance VALUES(?,?,?,?,?)',('campaign','Travaux',0,'test',time.time()))
  self.enter('market');self.enter('hub')
  with self.assertRaisesRegex(ValueError,'Maintenance'):self.a.action(self.uid,self.body('campaign_accept'))
  with self.a.conn() as c:c.execute('DELETE FROM activity_maintenance');c.execute('INSERT INTO activity_maintenance VALUES(?,?,?,?,?)',('market','Travaux',0,'test',time.time()))
  with self.assertRaisesRegex(ValueError,'Maintenance'):self.enter('market')
  self.enter('bank')
 def test_every_quest_step_has_a_real_destination_and_secrets_remain_private(self):
  for i,q in enumerate(QUESTS):
   self.position(i,payload={'edition':6});s=self.s();public=s['quest']
   self.assertIn(public['giver_scene'],SCENES)
   for step in public['steps']:
    self.assertIn(step['world_scene'],SCENES);self.assertNotIn('answer',step)
    for clue in step.get('clues',[]):self.assertNotIn('text',clue)
 def test_current_location_and_claim_survive_restart_with_no_remote_payment(self):
  self.position(0,3,payload={'edition':6,'reward_quote':{'gold':10,'xp':20}});self.enter('market');before=self.a.economy.get_balance(self.uid).wallet
  with self.assertRaises(ValueError):self.a.action(self.uid,self.body('campaign_claim'))
  self.enter('hub');token=self.s()['world']['token'];self.a=Activity(self.a.path);self.assertEqual(self.s()['world']['token'],token);body=self.body('campaign_claim');self.a.action(self.uid,body)
  with self.assertRaises(ValueError):self.a.action(self.uid,body)
  self.assertEqual(self.a.economy.get_balance(self.uid).wallet-before,10)
 def test_field_work_is_required_on_site_and_cannot_be_repeated(self):
  self.position(2,1,payload={'edition':6});self.enter('barman');step=self.s()['quest']['steps'][1];self.assertEqual(len(step['work_points']),2)
  with self.assertRaises(ValueError):self.a.action(self.uid,self.body())
  for point in step['work_points']:
   self.assertNotIn('text',point);self.a.action(self.uid,self.body('campaign_work',point_id=point['id']))
   with self.assertRaises(ValueError):self.a.action(self.uid,self.body('campaign_work',point_id=point['id']))
  with self.assertRaises(ValueError):self.a.action(self.uid,self.body())
  self.a=Activity(self.a.path);self.assertEqual(len(self.s()['work']),2);self.fast_time();self.enter('market')
  with self.assertRaises(ValueError):self.a.action(self.uid,self.body())
  self.enter('barman');self.a.action(self.uid,self.body());self.assertEqual(self.s()['stage'],2);self.assertEqual(self.s()['work'],[])
 def test_another_players_world_token_cannot_be_used(self):
  self.enter('hub');token=self.s()['world']['token'];(uid,name),_=self.a.session('');self.a.snapshot(uid,name)
  with self.a.conn() as c:c.execute('UPDATE tutorial_progress SET completed=1 WHERE user_id=?',(uid,));c.execute('UPDATE activity_tutorial_revision SET finished=1 WHERE user_id=?',(uid,))
  self.a.action(uid,dict(action='campaign_world_enter',scene='hub'));s=self.a.campaign.snapshot(uid)
  with self.assertRaises(ValueError):self.a.action(uid,dict(action='campaign_accept',quest_id=s['quest']['id'],revision=s['revision'],world_token=token))
 def test_all_new_field_missions_have_actions_without_exposing_results(self):
  for i,q in enumerate(QUESTS):
   self.position(i,payload={'edition':6})
   for step in self.s()['quest']['steps']:
    if step['kind']=='mission':
     self.assertGreaterEqual(len(step.get('work_points',[])),2,step['id'])
     for point in step['work_points']:self.assertNotIn('text',point)
