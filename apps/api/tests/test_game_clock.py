"""Civil boundaries and DST, exercised independently of the host TZ setting."""
import sys,tempfile,unittest
from pathlib import Path
from datetime import datetime
from unittest.mock import patch
sys.path.insert(0,str(Path(__file__).parents[1]))
from activity import Activity
import game_clock

def stamp(value):return datetime.fromisoformat(value).timestamp()
class GameClockTests(unittest.TestCase):
 def setUp(self):
  self.tmp=tempfile.TemporaryDirectory();self.a=Activity(self.tmp.name+'/test.db');(self.uid,_),_=self.a.session('');self.a.snapshot(self.uid,'Horloge')
 def tearDown(self):self.tmp.cleanup()
 def test_reset_timer_counts_real_seconds_through_both_dst_changes(self):
  for instant,expected in [('2026-03-28T23:00:00+00:00',23*3600),('2026-10-24T22:00:00+00:00',25*3600)]:
   with self.subTest(instant=instant),patch('time.time',return_value=stamp(instant)):
    self.assertEqual(game_clock.seconds_until_midnight(),expected);self.assertEqual(self.a.play.dark.seconds_until_server_midnight(),expected)
    self.assertEqual(self.a.tower.snapshot(self.uid)['reset_at']-stamp(instant),expected)
 def test_all_daily_engines_agree_with_paris_before_utc_midnight(self):
  with patch('time.time',return_value=stamp('2026-10-23T22:30:00+00:00')):
   self.assertEqual(self.a.economy._today(),'2026-10-24');self.assertEqual(self.a.castle._today(),'2026-10-24');self.assertEqual(self.a.tower.snapshot(self.uid)['day'],'2026-10-24')
 def test_daily_reward_is_not_reopened_at_utc_midnight_or_dst_repeat(self):
  with patch('time.time',return_value=stamp('2026-10-24T22:30:00+00:00')):self.assertTrue(self.a.castle.claim_daily(self.uid)[0])
  for instant in ('2026-10-25T00:30:00+00:00','2026-10-25T01:30:00+00:00','2026-10-25T22:59:59+00:00'):
   with patch('time.time',return_value=stamp(instant)):self.assertFalse(self.a.castle.claim_daily(self.uid)[0])
  with patch('time.time',return_value=stamp('2026-10-25T23:00:01+00:00')):self.assertTrue(self.a.castle.claim_daily(self.uid)[0])
 def test_casino_pass_expires_at_paris_midnight_and_not_utc_midnight(self):
  with self.a.conn() as c:c.execute('UPDATE players SET wallet_gold=1000 WHERE user_id=?',(self.uid,))
  with patch('time.time',return_value=stamp('2026-10-23T22:30:00+00:00')):self.assertTrue(self.a.play.dark.enter_clandestine_room(self.uid,False)['ok'])
  with patch('time.time',return_value=stamp('2026-10-24T00:30:00+00:00')):self.assertTrue(self.a.play.dark.clandestine_access_info(self.uid)['valid'])
  with patch('time.time',return_value=stamp('2026-10-24T22:00:01+00:00')):self.assertFalse(self.a.play.dark.clandestine_access_info(self.uid)['valid'])
 def test_drink_limit_uses_the_same_civil_day(self):
  with self.a.conn() as c:c.execute('UPDATE players SET wallet_gold=1000 WHERE user_id=?',(self.uid,))
  with patch('time.time',return_value=stamp('2026-10-23T22:30:00+00:00')):
   self.assertTrue(self.a.play.tavern.drink(self.uid,'beer')['ok']);before=self.a.play.tavern.drink_status(self.uid)['remaining_today']
  with patch('time.time',return_value=stamp('2026-10-24T00:30:00+00:00')):self.assertEqual(self.a.play.tavern.drink_status(self.uid)['remaining_today'],before)

if __name__=='__main__':unittest.main()
