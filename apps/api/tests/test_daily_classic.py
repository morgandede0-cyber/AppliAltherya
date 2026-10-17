import unittest,tempfile,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).parents[1]))
from activity import Activity

class ClassicDailyTests(unittest.TestCase):
 def setUp(self):
  self.tmp=tempfile.TemporaryDirectory();self.a=Activity(self.tmp.name+'/daily.db');(self.uid,self.name),_=self.a.session('');self.a.snapshot(self.uid,self.name)
 def tearDown(self):self.tmp.cleanup()
 def test_no_locked_location_or_upgrade_even_at_high_reputation(self):
  for xp in [0,100000]:
   with self.a.conn() as c:c.execute('UPDATE castle_profiles SET xp=? WHERE user_id=?',(xp,self.uid))
   qs,meta=self.a.castle.quests(self.uid)
   self.assertEqual(len(qs),3);self.assertTrue({q['key'] for q in qs}<={'arena_win','combat','daily_bonus','tavern_game','expedition'})
   self.assertTrue(all(1<=q['target']<=2 for q in qs))
   self.assertNotIn('Ashkar',' '.join(q['label'] for q in qs));self.assertEqual(meta['gold'],400)
 def test_reward_all_or_nothing_and_once_across_restart(self):
  store=self.a.castle;self.assertFalse(store.claim_quests(self.uid)[0])
  plan,_=store.quest_config(self.uid)
  for key,(_,target,event) in plan.items():
   if key=='daily_bonus':store.claim_daily(self.uid)
   else:store.record(self.uid,event,target)
  self.assertTrue(store.claim_quests(self.uid)[0]);before=self.a.economy.get_balance(self.uid).wallet
  other=Activity(self.a.path);self.assertFalse(other.castle.claim_quests(self.uid)[0]);self.assertEqual(other.economy.get_balance(self.uid).wallet,before)

 def test_previous_six_claimed_cannot_claim_new_three_again(self):
  with self.a.conn() as c:
   for key in ['tower_clear','forge_upgrade','arena_win','tavern_game','expedition','gold_earned']:
    c.execute('INSERT OR REPLACE INTO castle_daily_progress VALUES(?,?,?,?,?)',(self.uid,self.a.castle._today(),key,999,1))
  self.assertFalse(self.a.castle.claim_quests(self.uid)[0]);self.assertEqual(self.a.economy.get_balance(self.uid).wallet,0)
 def test_foraging_is_a_valid_accessible_expedition(self):
  # The standard starter gathering destination stays in the API catalog.
  s=self.a.snapshot(self.uid,self.name);self.assertIn('elarwyn_foraging',s['destinations']);self.assertLessEqual(s['destinations']['elarwyn_foraging']['level'],1)
