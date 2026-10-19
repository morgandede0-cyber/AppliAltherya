import unittest
from unittest.mock import patch
import test_play as fixtures
class CoinPresentationTests(unittest.TestCase):
 setUp=fixtures.GameTests.setUp
 tearDown=fixtures.GameTests.tearDown
 s=fixtures.GameTests.s
 act=fixtures.GameTests.act
 def test_all_four_choices_and_results_match_wallet(self):
  for player in ['pile','face']:
   for opponent in ['pile','face']:
    with self.subTest(player=player,opponent=opponent):
     before=self.s()['balance']['wallet']
     with patch('play.flip_coin',return_value=opponent):self.act(action='game_start',key='coin',choice=player,wager=1)
     s=self.s();p=s['play'];pay=2 if player==opponent else 0
     self.assertEqual(p['player'],player);self.assertEqual(p['opponent'],opponent);self.assertEqual(p['payout'],pay);self.assertEqual(p['status'],'finished');self.assertEqual(s['balance']['wallet'],before-1+pay)
 def test_invalid_wager_and_duplicate_request_do_not_debit(self):
  before=self.s()['balance']['wallet']
  for wager in [0,-1,501,1.5]:
   with self.assertRaises(ValueError):self.act(action='game_start',key='coin',choice='pile',wager=wager)
   self.assertEqual(self.s()['balance']['wallet'],before)
  rev=self.s()['play']['revision'];self.act(action='game_start',key='coin',choice='pile',wager=1,revision=rev);before=self.s()['balance']['wallet']
  with self.assertRaises(ValueError):self.act(action='game_start',key='coin',choice='pile',wager=1,revision=rev)
  self.assertEqual(self.s()['balance']['wallet'],before)
