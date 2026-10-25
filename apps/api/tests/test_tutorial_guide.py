"""Explanatory tutorial: sequential pages, no visits or gameplay actions."""
import json,tempfile,unittest,sys
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
sys.path.insert(0,str(Path(__file__).parents[1]))
from activity import Activity
from tutorial import GUIDE,LAST_STEP
class ExplanationTests(unittest.TestCase):
 def setUp(self):
  self.tmp=tempfile.TemporaryDirectory();self.a=Activity(self.tmp.name+'/db');(self.uid,self.name),self.token=self.a.session('');self.a.snapshot(self.uid,self.name)
 def tearDown(self):self.tmp.cleanup()
 def state(self):return self.a.snapshot(self.uid,self.name)
 def act(self,action,step=None,**body):return self.a.action(self.uid,dict(action=action,step=step,**body))
 def finish(self):
  for step in range(LAST_STEP):self.act('tutorial_next',step)
  self.act('tutorial_finish',LAST_STEP)
 def test_twelve_matching_pages_and_no_visit_requirement(self):
  self.assertEqual(len(GUIDE),12);self.assertEqual(GUIDE,json.loads((Path(__file__).parents[2]/'game/src/ui/tutorial-guide.json').read_text()));self.finish();self.assertTrue(self.state()['tutorial']['completed']);self.assertEqual(self.state()['tutorial']['visited'],[])
 def test_cannot_skip_pages_or_supply_own_reward(self):
  self.act('tutorial_finish',LAST_STEP,gold=99999,xp=99999);self.assertEqual(self.state()['tutorial']['step'],0);self.assertEqual(self.state()['balance']['wallet'],0)
  self.act('tutorial_next',5);self.assertEqual(self.state()['tutorial']['step'],0)
  for value in [True,-1,12,'1',None]:
   with self.assertRaises(ValueError):self.act('tutorial_next',value)
 def test_no_gameplay_before_explanations_finish(self):
  for action in ['buy','daily','deposit','battle_start','campaign_accept']:
   with self.assertRaises(ValueError):self.a.action(self.uid,dict(action=action))
 def test_progress_resumes_without_visits_after_restart(self):
  self.act('tutorial_next',0);self.act('tutorial_next',1);self.a=Activity(self.a.path);self.assertEqual(self.state()['tutorial']['step'],2);self.assertEqual(self.state()['tutorial']['visited'],[])
 def test_old_visit_requests_are_harmless_and_do_not_advance(self):
  self.act('tutorial_visit',0,destination='bank');self.assertEqual(self.state()['tutorial']['step'],0);self.assertEqual(self.state()['tutorial']['visited'],[])
 def test_reward_once_including_replay(self):
  self.finish();first=self.state();self.assertEqual((first['balance']['wallet'],first['xp']),(100,25));self.act('tutorial_replay');self.finish();last=self.state();self.assertEqual(last['balance'],first['balance']);self.assertEqual(last['xp'],first['xp'])
 def test_two_sessions_cannot_double_advance_or_pay(self):
  with ThreadPoolExecutor(4) as p:list(p.map(lambda _:self.act('tutorial_next',0),range(4)))
  self.assertEqual(self.state()['tutorial']['step'],1)
  for step in range(1,LAST_STEP):self.act('tutorial_next',step)
  with ThreadPoolExecutor(4) as p:list(p.map(lambda _:self.act('tutorial_finish',LAST_STEP),range(4)))
  self.assertEqual((self.state()['balance']['wallet'],self.state()['xp']),(100,25))
 def test_existing_current_revision_completion_is_not_reset(self):
  self.finish();self.a=Activity(self.a.path);self.assertTrue(self.state()['tutorial']['completed'])
 def test_other_player_keeps_independent_progress(self):
  self.act('tutorial_next',0);(uid,name),_=self.a.session('');self.assertEqual(self.a.snapshot(uid,name)['tutorial']['step'],0)
