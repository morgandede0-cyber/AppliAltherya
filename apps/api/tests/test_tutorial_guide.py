"""Direct protocol/security tests: do not use onboarding fixture shortcuts here."""
import json,tempfile,unittest,sys
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
sys.path.insert(0,str(Path(__file__).parents[1]))
from activity import Activity
from tutorial import GUIDE,LAST_STEP
class GuidedTutorialTests(unittest.TestCase):
 def setUp(self):
  self.tmp=tempfile.TemporaryDirectory();self.a=Activity(self.tmp.name+'/db');(self.uid,self.name),self.token=self.a.session('');self.a.snapshot(self.uid,self.name)
 def tearDown(self):self.tmp.cleanup()
 def state(self):return self.a.snapshot(self.uid,self.name)
 def act(self,action,step=None,**body):return self.a.action(self.uid,dict(action=action,step=step,**body))
 def visit(self,step):return self.act('tutorial_visit',step,destination=GUIDE[step]['destination'])
 def finish(self):
  for step in range(len(GUIDE)):
   self.visit(step);self.act('tutorial_next' if step<LAST_STEP else 'tutorial_finish',step)
 def test_twelve_steps_and_client_catalog_match(self):
  self.assertEqual(len(GUIDE),12);self.assertEqual(self.state()['tutorial']['visited'],[])
  client=json.loads((Path(__file__).parents[2]/'game/src/ui/tutorial-guide.json').read_text());self.assertEqual(GUIDE,client)
 def test_no_skipping_visits_or_client_chosen_destination(self):
  before=self.state()
  with self.assertRaisesRegex(ValueError,'Ouvrez'):self.act('tutorial_next',0)
  for destination in ['bank',None,True,[],{'name':'castle'}]:
   with self.assertRaises(ValueError):self.act('tutorial_visit',0,destination=destination)
  self.act('tutorial_visit',4,destination='bank');self.assertEqual(self.state()['tutorial']['visited'],[])
  for action in ['buy','daily','deposit','battle_start','campaign_accept']:
   with self.assertRaises(ValueError):self.a.action(self.uid,dict(action=action))
  self.assertEqual(self.state()['balance'],before['balance']);self.assertEqual(self.state()['xp'],before['xp'])
 def test_read_only_visit_persists_after_restart_and_other_player_cannot_supply_it(self):
  before=self.state();self.visit(0);self.a=Activity(self.a.path)
  self.assertEqual(self.state()['tutorial']['visited'],[0]);self.assertEqual(self.state()['balance'],before['balance'])
  (other,name),_=self.a.session('');self.a.snapshot(other,name)
  self.assertEqual(self.a.snapshot(other,name)['tutorial']['visited'],[])
  with self.assertRaises(ValueError):self.a.action(other,dict(action='tutorial_next',step=0))
 def test_reward_is_unchanged_single_and_replay_requires_visits_again(self):
  self.finish();first=self.state();self.assertEqual((first['balance']['wallet'],first['xp']),(100,25))
  self.act('tutorial_replay');self.assertEqual(self.state()['tutorial']['visited'],[])
  with self.assertRaises(ValueError):self.act('tutorial_next',0)
  self.finish();last=self.state();self.assertEqual(last['balance'],first['balance']);self.assertEqual(last['xp'],first['xp'])
 def test_two_sessions_cannot_double_advance_or_pay(self):
  for step in range(LAST_STEP):self.visit(step);self.act('tutorial_next',step)
  self.visit(LAST_STEP)
  with ThreadPoolExecutor(4) as p:list(p.map(lambda _:self.act('tutorial_finish',LAST_STEP,gold=99999),range(4)))
  self.assertEqual((self.state()['balance']['wallet'],self.state()['xp']),(100,25))
 def test_completed_legacy_players_are_not_reset(self):
  with self.a.conn() as c:
   c.execute('UPDATE tutorial_progress SET completed=1,reward_claimed=1,gold_claimed=1,xp_claimed=1 WHERE user_id=?',(self.uid,));c.execute('UPDATE activity_tutorial_revision SET finished=1 WHERE user_id=?',(self.uid,));c.execute('UPDATE activity_tutorial_steps SET step=5 WHERE user_id=?',(self.uid,))
  state=self.state()['tutorial'];self.assertTrue(state['completed']);self.assertTrue(state['reward_claimed']);self.assertEqual(state['step'],5)
 def test_incomplete_old_six_page_tutorial_restarts_guide_without_paying(self):
  with self.a.conn() as c:c.execute('UPDATE activity_tutorial_steps SET step=4 WHERE user_id=?',(self.uid,))
  state=self.state();self.assertEqual(state['tutorial']['step'],0);self.assertEqual(state['balance']['wallet'],0)

 def test_eight_page_discoveries_migrate_without_losing_receipts(self):
  with self.a.conn() as c:
   c.execute('DELETE FROM activity_tutorial_catalog WHERE user_id=?',(self.uid,))
   c.execute('UPDATE activity_tutorial_steps SET step=5 WHERE user_id=?',(self.uid,))
   for step,destination in enumerate(['castle','profile','expedition','market:buy','bank']):c.execute('INSERT INTO activity_tutorial_visits VALUES(?,?,?)',(self.uid,step,destination))
  t=self.state()['tutorial'];self.assertEqual(t['visited'],[0,1,3,4,6]);self.assertEqual(t['step'],2);self.assertFalse(t['completed']);self.assertEqual(self.state()['balance']['wallet'],0)
  self.assertEqual(self.state()['tutorial'],t)
 def test_final_recap_claim_needs_all_eleven_discoveries_but_no_extra_visit(self):
  for step in range(LAST_STEP):self.visit(step);self.act('tutorial_next',step)
  self.act('tutorial_finish',LAST_STEP);self.assertTrue(self.state()['tutorial']['completed']);self.assertEqual(self.state()['balance']['wallet'],100)
 def test_tampered_final_index_without_prior_visits_cannot_pay(self):
  with self.a.conn() as c:
   c.execute('INSERT INTO activity_tutorial_visits VALUES(?,?,?)',(self.uid,0,GUIDE[0]['destination']))
   c.execute('UPDATE activity_tutorial_steps SET step=? WHERE user_id=?',(LAST_STEP,self.uid))
  self.visit(LAST_STEP)
  with self.assertRaises(ValueError):self.act('tutorial_finish',LAST_STEP)
  self.assertEqual(self.state()['balance']['wallet'],0)
