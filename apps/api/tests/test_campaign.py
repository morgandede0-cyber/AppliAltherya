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
  self.act('campaign_accept');self.act('campaign_step');self.act('campaign_step')
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
