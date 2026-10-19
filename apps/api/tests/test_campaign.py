import unittest,tempfile,sys,json,time,random
from pathlib import Path
from unittest.mock import patch
from concurrent.futures import ThreadPoolExecutor
sys.path.insert(0,str(Path(__file__).parents[1]))
from activity import Activity
from campaign import QUESTS

class CampaignTests(unittest.TestCase):
 def setUp(self):
  self.tmp=tempfile.TemporaryDirectory();self.a=Activity(self.tmp.name+'/campaign.db');(self.uid,self.name),_=self.a.session('');self.a.snapshot(self.uid,self.name)
  with self.a.conn() as c:
   c.execute('UPDATE tutorial_progress SET completed=1 WHERE user_id=?',(self.uid,));c.execute('UPDATE activity_tutorial_revision SET finished=1 WHERE user_id=?',(self.uid,))
 def tearDown(self):self.tmp.cleanup()
 def s(self):return self.a.snapshot(self.uid,self.name)['campaign']
 def act(self,action,**body):
  s=self.s();return self.a.action(self.uid,dict(action=action,quest_id=s['quest']['id'],revision=s['revision'],**body))
 def position(self,idx,stage=0,payload=None):
  self.s()
  with self.a.conn() as c:
   c.execute('UPDATE castle_profiles SET xp=100000 WHERE user_id=?',(self.uid,))
   c.execute('UPDATE campaign_progress SET quest_index=?,stage=?,accepted_at=?,entered_at=?,payload=? WHERE user_id=?',(idx,stage,time.time()-10000,time.time()-1,json.dumps(payload or {}),self.uid))
 def fast_time(self):
  with self.a.conn() as c:
   r=c.execute('SELECT payload FROM campaign_progress WHERE user_id=?',(self.uid,)).fetchone();p=json.loads(r[0]);p['deadline']=time.time()-1;p['retry_at']=0
   c.execute('UPDATE campaign_progress SET accepted_at=?,payload=? WHERE user_id=?',(time.time()-10000,json.dumps(p),self.uid))
 def test_tutorial_level_and_replay_gates(self):
  with self.a.conn() as c:c.execute('UPDATE tutorial_progress SET completed=0 WHERE user_id=?',(self.uid,))
  with self.assertRaises(ValueError):self.act('campaign_accept')
  with self.a.conn() as c:c.execute('UPDATE tutorial_progress SET completed=1 WHERE user_id=?',(self.uid,))
  self.act('campaign_accept');s=self.s();body=dict(action='campaign_step',quest_id=s['quest']['id'],revision=s['revision']);self.a.action(self.uid,body)
  with self.assertRaises(ValueError):self.a.action(self.uid,body)
  with self.assertRaises(ValueError):self.act('campaign_claim')
  self.position(8)
  with self.a.conn() as c:c.execute('UPDATE castle_profiles SET xp=0 WHERE user_id=?',(self.uid,));c.execute('UPDATE campaign_progress SET accepted_at=NULL WHERE user_id=?',(self.uid,))
  with self.assertRaises(ValueError):self.act('campaign_accept')
 def test_clock_and_hidden_answers(self):
  self.position(0);self.act('campaign_step');self.act('campaign_step')
  with self.assertRaises(ValueError):self.act('campaign_step')
  self.fast_time();self.act('campaign_step');self.act('campaign_step');self.act('campaign_claim')
  self.position(1,1);s=self.s();self.assertNotIn('answer',s['quest']['steps'][1]);self.act('campaign_step',option=1)
  self.assertEqual(self.s()['stage'],1)
  with self.assertRaises(ValueError):self.act('campaign_step',option=0)
  self.fast_time();self.act('campaign_step',option=0);self.assertEqual(self.s()['stage'],2)
 def test_delivery_and_reward_atomic(self):
  self.position(10)
  with self.assertRaises(ValueError):self.act('campaign_step')
  self.a.expeditions.add_resources(self.uid,{'Bois de chêne':5});s=self.s();body=dict(action='campaign_step',quest_id=s['quest']['id'],revision=s['revision'])
  def invoke(_):
   try:self.a.action(self.uid,body);return True
   except ValueError:return False
  with ThreadPoolExecutor(max_workers=2) as pool:self.assertEqual(sum(pool.map(invoke,range(2))),1)
  self.assertEqual(self.a.expeditions.get_resources(self.uid).get('Bois de chêne',0),0)
 def test_old_or_wrong_expeditions_do_not_complete(self):
  self.position(6,1)
  # Start a genuine voyage through the normal API and finalize through reconcile.
  self.a.action(self.uid,dict(action='start',key='elarwyn_foraging',tool='hands'))
  run=self.a.expeditions.active_run(self.uid)
  with self.a.conn() as c:c.execute('UPDATE expedition_runs SET ends_at=? WHERE run_id=?',(int(time.time())-1,run.run_id))
  self.a.reconcile(self.uid);self.assertTrue(self.s()['expedition_ready']);self.act('campaign_step');self.assertEqual(self.s()['stage'],2)
  self.position(11,1)
  with self.assertRaises(ValueError):self.act('campaign_step')
 def test_battle_persists_and_does_not_pay_per_turn(self):
  self.position(7,1);self.act('campaign_battle',key='start');before=self.a.economy.get_balance(self.uid).wallet
  self.act('campaign_battle',key='light');hp=self.s()['battle']['fighters'][1]['hp'];self.a=Activity(self.a.path);self.assertEqual(self.s()['battle']['fighters'][1]['hp'],hp)
  self.act('campaign_battle',key='abandon');self.assertEqual(self.a.economy.get_balance(self.uid).wallet,before);self.assertEqual(self.s()['stage'],1)
  with self.assertRaises(ValueError):self.act('campaign_battle',key='start')
 def test_full_campaign_has_once_only_receipts_and_keeps_chronicles(self):
  random.seed(145)
  with self.a.conn() as c:c.execute('UPDATE castle_profiles SET xp=100000 WHERE user_id=?',(self.uid,))
  original_chapters=self.a.snapshot(self.uid,self.name)['chapters'];total=0
  for idx,q in enumerate(QUESTS):
   self.assertEqual(self.s()['quest']['id'],q['id']);self.act('campaign_accept')
   for step in q['steps']:
    kind=step['kind']
    if kind in ('inspect','mission'):self.act('campaign_step');self.fast_time();self.act('campaign_step')
    elif kind in ('puzzle','choice'):self.act('campaign_step',option=step.get('answer',0))
    elif kind=='explore':
     self.act('campaign_enter',place_id=step['place_id'])
     for clue in step['clues']:self.act('campaign_explore',clue_id=clue['id'])
     self.act('campaign_step')
    elif kind=='deliver':self.a.expeditions.add_resources(self.uid,{step['resource']:step['quantity']});self.act('campaign_step')
    elif kind=='expedition':
     # A completed real run is checked separately; here seed a matching run from its schema.
     self.a.action(self.uid,dict(action='start',key='elarwyn_foraging',tool='hands'));run=self.a.expeditions.active_run(self.uid)
     if not run:
      with self.a.conn() as c:c.execute('UPDATE expedition_profiles SET last_expedition_date=NULL WHERE user_id=?',(self.uid,))
      self.a.action(self.uid,dict(action='start',key='elarwyn_foraging',tool='hands'));run=self.a.expeditions.active_run(self.uid)
     with self.a.conn() as c:c.execute('UPDATE expedition_runs SET expedition_key=?,started_at=?,ends_at=? WHERE run_id=?',(step['destination'],int(time.time()),int(time.time())-1,run.run_id))
     self.a.reconcile(self.uid);self.act('campaign_step')
    elif kind=='battle':
     self.act('campaign_battle',key='start')
     for turn in range(150):
      if self.s()['stage']>=q['steps'].index(step)+1:break
      b=self.s()['battle']
      if b['finished']:self.fast_time();self.act('campaign_battle',key='start');continue
      self.act('campaign_battle',key='ultimate' if not b['ultimate_cd'] else 'heavy')
     else:self.fail('combat not resolved')
    else:self.act('campaign_step')
   self.fast_time();old=self.s();self.act('campaign_claim');total+=q['gold']
   with self.assertRaises(ValueError):self.a.action(self.uid,dict(action='campaign_claim',quest_id=q['id'],revision=old['revision']))
  self.assertTrue(self.s()['complete']);self.assertEqual(self.s()['completed'],32)
  with self.a.conn() as c:self.assertEqual(c.execute('SELECT SUM(gold) FROM campaign_receipts WHERE user_id=?',(self.uid,)).fetchone()[0],total)
  self.assertEqual([(c['chapter'],c['title'],c['unlocked']) for c in self.a.snapshot(self.uid,self.name)['chapters']],[(c['chapter'],c['title'],c['unlocked']) for c in original_chapters])

 def test_claim_race_and_minimum_duration(self):
  self.position(0,3)
  with self.a.conn() as c:c.execute('UPDATE campaign_progress SET accepted_at=? WHERE user_id=?',(time.time(),self.uid))
  with self.assertRaises(ValueError):self.act('campaign_claim')
  self.fast_time();s=self.s();body=dict(action='campaign_claim',quest_id=s['quest']['id'],revision=s['revision']);before=self.a.economy.get_balance(self.uid).wallet
  def invoke(_):
   try:self.a.action(self.uid,body);return True
   except ValueError:return False
  with ThreadPoolExecutor(max_workers=2) as pool:self.assertEqual(sum(pool.map(invoke,range(2))),1)
  self.assertEqual(self.s()['quest']['gold'],10);self.assertEqual(self.a.economy.get_balance(self.uid).wallet-before,10);self.assertEqual(self.a.castle.profile(self.uid)['quests_completed'],1)

 def test_old_paid_reward_survives_restart_without_second_payment(self):
  self.position(0,3)
  with self.a.conn() as c:
   c.execute('INSERT INTO campaign_receipts VALUES(?,?,?,?,?)',(self.uid,'S1-Q01',115,20,time.time()))
   c.execute('UPDATE players SET wallet_gold=115 WHERE user_id=?',(self.uid,))
   c.execute('UPDATE campaign_progress SET quest_index=1,stage=0,accepted_at=NULL WHERE user_id=?',(self.uid,))
  self.a=Activity(self.a.path)
  self.assertEqual(self.a.economy.get_balance(self.uid).wallet,115)
  self.assertEqual(self.s()['quest']['gold'],10)
  with self.a.conn() as c:
   self.assertEqual(tuple(c.execute('SELECT gold,xp FROM campaign_receipts WHERE user_id=?',(self.uid,)).fetchone()),(115,20))
  self.position(0,3)
  with self.assertRaises(ValueError):self.act('campaign_claim')
  self.assertEqual(self.a.economy.get_balance(self.uid).wallet,115)

 def explore_first(self):
  self.act('campaign_accept');self.act('campaign_step');self.act('campaign_enter',place_id='convois');return self.s()['quest']['steps'][1]
 def test_exploration_requires_each_real_clue_and_preserves_journal(self):
  step=self.explore_first();self.assertEqual(step['kind'],'explore');self.assertNotIn('text',step['clues'][0])
  before=self.a.economy.get_balance(self.uid).wallet
  with self.assertRaises(ValueError):self.act('campaign_step')
  with self.assertRaises(ValueError):self.act('campaign_explore',clue_id='S4-Q02-O1-I1')
  for clue in step['clues']:self.act('campaign_explore',clue_id=clue['id'])
  self.assertEqual(len(self.s()['evidence']),3);self.assertEqual(self.s()['stage'],1)
  with self.assertRaises(ValueError):self.act('campaign_explore',clue_id=step['clues'][0]['id'])
  self.a=Activity(self.a.path);self.assertEqual(len(self.s()['evidence']),3);self.act('campaign_step');self.act('campaign_step')
  with self.assertRaises(ValueError):self.act('campaign_claim')
  self.fast_time()
  xp=self.a.castle.profile(self.uid)['xp'];self.act('campaign_claim');self.assertEqual(self.a.castle.profile(self.uid)['xp']-xp,20)
  self.assertEqual(self.a.economy.get_balance(self.uid).wallet-before,10);self.assertEqual(len(self.s()['evidence']),3)
  other,_=self.a.session('');self.a.snapshot(*other);self.assertEqual(self.a.campaign.snapshot(other[0])['evidence'],[])
 def test_clue_double_click_and_concurrent_claim_are_idempotent(self):
  step=self.explore_first();state=self.s();body=dict(action='campaign_explore',quest_id=state['quest']['id'],revision=state['revision'],clue_id=step['clues'][0]['id'])
  def run(_):
   try:self.a.action(self.uid,body);return True
   except ValueError:return False
  with ThreadPoolExecutor(2) as pool:self.assertEqual(sum(pool.map(run,range(2))),1)
  self.assertEqual(len(self.s()['evidence']),1)
 def test_new_level_gate_is_server_owned_and_old_accepted_mission_is_preserved(self):
  self.position(4,1);old=self.s();self.assertEqual(old['edition'],1);self.assertEqual(old['quest']['min_level'],1);self.assertEqual(old['quest']['steps'][0]['kind'],'mission')
  self.a=Activity(self.a.path);self.assertEqual(self.s()['stage'],1);self.assertEqual(self.s()['quest']['min_level'],1)
  with self.a.conn() as c:c.execute('UPDATE campaign_progress SET accepted_at=NULL,payload="{}" WHERE user_id=?',(self.uid,));c.execute('UPDATE castle_profiles SET xp=0 WHERE user_id=?',(self.uid,))
  self.assertEqual(self.s()['quest']['min_level'],3);self.assertFalse(self.s()['level_allowed'])
  with self.assertRaises(ValueError):self.act('campaign_accept')
 def test_campaign_rewards_and_step_ids_are_stable_and_every_quest_has_xp(self):
  from campaign import LEGACY_QUESTS,CATALOG
  levels=[q['min_level'] for q in QUESTS];self.assertEqual(levels,sorted(levels));self.assertEqual(levels[-1],15)
  for old,new in zip(LEGACY_QUESTS,QUESTS):
   self.assertEqual((old['id'],old['gold'],old['xp']),(new['id'],new['gold'],new['xp']));self.assertGreater(new['xp'],0)
   self.assertEqual([s['id'] for s in old['steps']],[s['id'] for s in new['steps']])
   for ns,os in zip(new['steps'],old['steps']):
    if ns['kind']=='explore':self.assertGreaterEqual(new['min_duration'],os.get('duration',0))
  self.assertEqual(len(CATALOG['locations']),6);self.assertEqual(sum(s['kind']=='explore' for q in QUESTS for s in q['steps']),12)

 def test_new_places_have_assets_and_are_not_above_their_quest_level(self):
  from campaign import CATALOG
  locations={p['id']:p for p in CATALOG['locations']}
  self.assertEqual(len({p['scene_image'] for p in locations.values()}),6)
  assets=Path(__file__).parents[2]/'game/public/assets/scenes'
  for loc in locations.values():self.assertTrue((assets/loc['scene_image']).is_file(),loc['name'])
  for q in QUESTS:
   for step in q['steps']:
    if step['kind']=='explore':
     self.assertGreaterEqual(q['min_level'],locations[step['place_id']]['min_level']);self.assertEqual(len({c['id'] for c in step['clues']}),3)

 def test_place_entry_needs_story_and_level_and_cannot_be_guessed(self):
  before=self.a.castle.profile(self.uid)['xp'];wallet=self.a.economy.get_balance(self.uid).wallet
  for place in ('convois','archives','inconnu'):
   with self.assertRaises(ValueError):self.a.action(self.uid,dict(action='campaign_enter',place_id=place))
  self.act('campaign_accept');self.act('campaign_step');state=self.s();place=next(p for p in state['locations'] if p['id']=='convois');self.assertTrue(place['can_enter']);self.assertFalse(place['visited'])
  with self.assertRaises(ValueError):self.act('campaign_explore',clue_id=state['quest']['steps'][1]['clues'][0]['id'])
  self.act('campaign_enter',place_id='convois');self.act('campaign_enter',place_id='convois');self.assertEqual(self.a.castle.profile(self.uid)['xp'],before);self.assertEqual(self.a.economy.get_balance(self.uid).wallet,wallet)
  with self.a.conn() as c:self.assertEqual(c.execute('SELECT COUNT(*) FROM campaign_visits WHERE user_id=?',(self.uid,)).fetchone()[0],1)
  self.a=Activity(self.a.path);self.assertTrue(next(p for p in self.s()['locations'] if p['id']=='convois')['visited'])
 def test_level_alone_does_not_unlock_places_but_completed_story_does(self):
  self.position(1)
  with self.assertRaises(ValueError):self.act('campaign_enter',place_id='sceaux')
  with self.a.conn() as c:c.execute('INSERT INTO campaign_receipts VALUES(?,?,?,?,?)',(self.uid,'S1-Q01',10,20,time.time()))
  self.act('campaign_enter',place_id='convois');self.assertTrue(next(p for p in self.s()['locations'] if p['id']=='convois')['can_enter'])
  with self.a.conn() as c:c.execute('INSERT INTO campaign_receipts VALUES(?,?,?,?,?)',(self.uid,'S2-Q01',18,35,time.time()));c.execute('UPDATE castle_profiles SET xp=0 WHERE user_id=?',(self.uid,))
  with self.assertRaises(ValueError):self.act('campaign_enter',place_id='sceaux')
 def test_completed_campaign_can_revisit_unlocked_places_without_reopening_rewards(self):
  self.position(len(QUESTS));before=self.a.economy.get_balance(self.uid).wallet
  with self.a.conn() as c:c.execute('INSERT INTO campaign_receipts VALUES(?,?,?,?,?)',(self.uid,'S1-Q01',10,20,time.time()))
  self.a.action(self.uid,dict(action='campaign_enter',place_id='convois'));self.assertTrue(self.s()['complete']);self.assertEqual(self.a.economy.get_balance(self.uid).wallet,before)
