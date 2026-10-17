import unittest,tempfile,sys
from pathlib import Path
from datetime import date,timedelta
from concurrent.futures import ThreadPoolExecutor
from unittest.mock import patch
sys.path.insert(0,str(Path(__file__).parents[1]))
from activity import Activity

class RandomDailyTests(unittest.TestCase):
 def setUp(self):
  self.tmp=tempfile.TemporaryDirectory();self.a=Activity(self.tmp.name+'/random.db');(self.uid,self.name),_=self.a.session('');self.a.snapshot(self.uid,self.name)
 def tearDown(self):self.tmp.cleanup()
 def test_stable_after_restart_and_concurrent_reads(self):
  first=self.a.castle.quest_config(self.uid)[0];other=Activity(self.a.path);self.assertEqual(first,other.castle.quest_config(self.uid)[0])
  with ThreadPoolExecutor(max_workers=4) as pool:
   self.assertTrue(all(p==first for p in pool.map(lambda _:other.castle.quest_config(self.uid)[0],range(8))))
 def test_variety_and_no_advanced_location_or_two_arena_targets(self):
  previous=None;seen=set()
  for day in range(24):
   with patch.object(self.a.castle,'_today',return_value=(date(2026,10,17)+timedelta(days=day)).isoformat()):
    plan,_=self.a.castle.quest_config(self.uid);keys=frozenset(plan)
    self.assertEqual(len(keys),3);self.assertFalse({'combat','arena_win'}<=keys)
    self.assertTrue(keys<={'combat','arena_win','daily_bonus','tavern_game','expedition'})
    self.assertNotEqual(keys,previous);previous=keys;seen.add(keys)
  self.assertGreaterEqual(len(seen),4)
 def test_profiles_get_different_draws(self):
  plans={tuple(self.a.castle.quest_config(uid)[0]) for uid in range(1,21)};self.assertGreater(len(plans),1)
 def test_already_collected_daily_bonus_and_no_double_quest_reward(self):
  self.a.castle.claim_daily(self.uid)
  with patch.object(self.a.castle,'_today',return_value='2026-11-01'):
   self.a.castle.claim_daily(self.uid);plan,_=self.a.castle.quest_config(self.uid)
   for key,(_,target,event) in plan.items():
    if key!='daily_bonus':self.a.castle.record(self.uid,event,target)
   qs,_=self.a.castle.quests(self.uid)
   for q in qs:
    if q['key']=='daily_bonus':self.assertEqual(q['progress'],1)
   self.assertTrue(self.a.castle.claim_quests(self.uid)[0]);self.assertFalse(self.a.castle.claim_quests(self.uid)[0])
 def test_legacy_claim_marks_new_objectives_claimed(self):
  with self.a.conn() as c:c.execute('INSERT OR REPLACE INTO castle_daily_progress VALUES(?,?,?,?,?)',(self.uid,self.a.castle._today(),'forge_upgrade',1,1))
  qs,_=self.a.castle.quests(self.uid);self.assertTrue(all(q['claimed'] for q in qs));self.assertFalse(self.a.castle.claim_quests(self.uid)[0])
