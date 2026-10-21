import unittest

import test_arena_complete as harness
from activity import Activity
import arena_techniques as tech
class ArenaResetTests(unittest.TestCase):
 setUp=harness.ArenaCompleteTests.setUp
 tearDown=harness.ArenaCompleteTests.tearDown
 state=harness.ArenaCompleteTests.state
 act=harness.ArenaCompleteTests.act
 finish_win=harness.ArenaCompleteTests.finish_win
 def old_database(self):
  with self.a.conn() as c:
   c.execute('DELETE FROM activity_arena_migrations WHERE key=?',(tech.RESET_KEY,))
   c.execute('INSERT INTO arena_progress VALUES(?,300,9)',(self.uid,))
   for n in range(1,11):tech.grant(c,self.uid,n)
   c.execute("INSERT INTO activity_arena_loadout VALUES(?,'heavy','c1')",(self.uid,))
   c.execute('UPDATE castle_profiles SET xp=250 WHERE user_id=?',(self.uid,))
 def test_reset_once_all_players_only_champions_and_techniques(self):
  self.old_database()
  with self.a.conn() as c:c.execute('INSERT INTO arena_progress VALUES(123,900,8)')
  self.a=Activity(self.a.path);s=self.state()
  self.assertEqual(s['arena']['champion_level'],1);self.assertEqual(s['arena']['champion_wins'],0);self.assertEqual(s['arena']['rating'],300);self.assertEqual(s['balance']['wallet'],100);self.assertEqual(s['xp'],150);self.assertEqual(s['arena']['skills']['heavy']['id'],'base_heavy');self.assertFalse(any(t['unlocked'] for t in s['arena']['techniques']))
  with self.a.conn() as c:self.assertEqual(c.execute('SELECT xp FROM castle_profiles WHERE user_id=?',(self.uid,)).fetchone()[0],250);self.assertEqual(tuple(c.execute('SELECT rating,champion_wins FROM arena_progress WHERE user_id=123').fetchone()),(900,0))
  p=self.finish_win();self.assertEqual(p['result']['technique_unlocked']['id'],'c1')
  self.a.action(self.uid,dict(action='arena_equip',slot='heavy',technique='c1',loadout_revision=self.state()['arena']['loadout_revision']))
  self.a=Activity(self.a.path);s=self.state();self.assertEqual(s['arena']['champion_wins'],1);self.assertEqual(s['arena']['skills']['heavy']['id'],'c1');self.assertFalse(s['arena']['techniques'][1]['unlocked'])
 def test_no_backfill_even_if_victory_counter_is_high(self):
  with self.a.conn() as c:c.execute('INSERT INTO arena_progress VALUES(?,0,10)',(self.uid,))
  self.assertFalse(any(t['unlocked'] for t in self.state()['arena']['techniques']))
 def test_interrupted_wager_refunded_once_before_reset(self):
  self.act('battle_start',wager=10)
  with self.a.conn() as c:c.execute('DELETE FROM activity_arena_migrations WHERE key=?',(tech.RESET_KEY,))
  self.a=Activity(self.a.path);self.assertEqual(self.state()['balance']['wallet'],100);self.assertEqual(self.state()['play']['status'],'refunded');self.assertEqual(self.state()['arena']['remaining'],0)
  self.a=Activity(self.a.path);self.assertEqual(self.state()['balance']['wallet'],100)
 def test_failed_reset_rolls_back_and_can_retry(self):
  self.old_database()
  with self.a.conn() as c:c.execute("CREATE TRIGGER block_reset BEFORE DELETE ON activity_arena_loadout BEGIN SELECT RAISE(ABORT,'test failure'); END")
  with self.assertRaises(Exception):tech.reset_once(self.a)
  with self.a.conn() as c:
   self.assertIsNone(c.execute('SELECT 1 FROM activity_arena_migrations WHERE key=?',(tech.RESET_KEY,)).fetchone());self.assertEqual(c.execute('SELECT champion_wins FROM arena_progress WHERE user_id=?',(self.uid,)).fetchone()[0],9);self.assertEqual(c.execute('SELECT COUNT(*) FROM activity_arena_techniques').fetchone()[0],10);c.execute('DROP TRIGGER block_reset')
  self.assertTrue(tech.reset_once(self.a));self.assertFalse(tech.reset_once(self.a))
