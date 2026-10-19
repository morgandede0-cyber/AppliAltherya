import unittest
from unittest.mock import patch
import test_play as fixtures
class HorseRacingTests(unittest.TestCase):
 setUp=fixtures.GameTests.setUp
 tearDown=fixtures.GameTests.tearDown
 s=fixtures.GameTests.s
 act=fixtures.GameTests.act
 access=fixtures.GameTests.access
 def test_full_order_agrees_with_winner_and_settlement(self):
  self.access();odds=self.s()['casino']['odds'];before=self.s()['balance']['wallet']
  with patch('play.random.choices',return_value=[2]):self.act(action='game_start',key='horses',choice=2,wager=10,odds=odds)
  p=self.s()['play'];self.assertEqual(p['order'][0],2);self.assertEqual(sorted(p['order']),[0,1,2,3]);self.assertEqual(sorted(range(4),key=lambda i:p['finish_times'][i]),p['order']);self.assertEqual(p['odds'],odds);self.assertEqual(p['payout'],round(10*odds[2]));self.assertEqual(self.s()['balance']['wallet'],before-10+p['payout'])
 def test_changed_odds_are_rejected_before_debit(self):
  self.access();before=self.s()['balance']['wallet']
  with self.assertRaises(ValueError):self.act(action='game_start',key='horses',choice=0,wager=10,odds=[999]*4)
  self.assertEqual(self.s()['balance']['wallet'],before)
 def test_finish_result_cannot_be_paid_twice(self):
  self.access();rev=self.s()['play']['revision'];self.act(action='game_start',key='horses',choice=0,wager=10,revision=rev);before=self.s()['balance']['wallet']
  with self.assertRaises(ValueError):self.act(action='game_start',key='horses',choice=0,wager=10,revision=rev)
  self.assertEqual(self.s()['balance']['wallet'],before)
