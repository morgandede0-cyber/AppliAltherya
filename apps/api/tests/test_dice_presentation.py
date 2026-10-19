import unittest
from unittest.mock import patch
import test_play as fixtures
class DicePresentationTests(unittest.TestCase):
 setUp=fixtures.GameTests.setUp
 tearDown=fixtures.GameTests.tearDown
 s=fixtures.GameTests.s
 act=fixtures.GameTests.act
 def test_all_36_pairs_match_wager_and_payout(self):
  for player in range(1,7):
   for opponent in range(1,7):
    with self.subTest(player=player,opponent=opponent):
     before=self.s()['balance']['wallet']
     with patch('play.roll_die',side_effect=[player,opponent]):self.act(action='game_start',key='dice',wager=1)
     s=self.s();p=s['play'];pay=2 if player>opponent else 1 if player==opponent else 0
     self.assertEqual(p['player'],player);self.assertEqual(p['opponent'],opponent);self.assertEqual(p['payout'],pay);self.assertEqual(p['status'],'finished');self.assertEqual(s['balance']['wallet'],before-1+pay)
 def test_invalid_wager_and_duplicate_request_do_not_debit(self):
  before=self.s()['balance']['wallet']
  for wager in [0,-1,501,1.5]:
   with self.assertRaises(ValueError):self.act(action='game_start',key='dice',wager=wager)
   self.assertEqual(self.s()['balance']['wallet'],before)
  rev=self.s()['play']['revision'];self.act(action='game_start',key='dice',wager=1,revision=rev);before=self.s()['balance']['wallet']
  with self.assertRaises(ValueError):self.act(action='game_start',key='dice',wager=1,revision=rev)
  self.assertEqual(self.s()['balance']['wallet'],before)
