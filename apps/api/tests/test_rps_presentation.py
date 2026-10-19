import unittest
from unittest.mock import patch
import test_play as fixtures
class RpsPresentationTests(unittest.TestCase):
 setUp=fixtures.GameTests.setUp
 tearDown=fixtures.GameTests.tearDown
 s=fixtures.GameTests.s
 act=fixtures.GameTests.act
 def test_all_nine_pairs_and_payouts(self):
  beats={'pierre':'ciseaux','feuille':'pierre','ciseaux':'feuille'}
  for choice,player in [('rock','pierre'),('paper','feuille'),('scissors','ciseaux')]:
   for opponent in beats:
    with self.subTest(player=player,opponent=opponent):
     before=self.s()['balance']['wallet']
     with patch('play.rps_bot',return_value=opponent):self.act(action='game_start',key='rps',choice=choice,wager=1)
     s=self.s();p=s['play'];pay=1 if player==opponent else 2 if beats[player]==opponent else 0
     self.assertEqual(p['player'],player);self.assertEqual(p['opponent'],opponent);self.assertEqual(p['payout'],pay);self.assertEqual(p['status'],'finished');self.assertEqual(s['balance']['wallet'],before-1+pay)
 def test_invalid_wager_choice_and_duplicate_do_not_debit(self):
  before=self.s()['balance']['wallet']
  for wager in [0,-1,501,1.5]:
   with self.assertRaises(ValueError):self.act(action='game_start',key='rps',choice='rock',wager=wager)
   self.assertEqual(self.s()['balance']['wallet'],before)
  with self.assertRaises(ValueError):self.act(action='game_start',key='rps',choice='invalid',wager=1)
  self.assertEqual(self.s()['balance']['wallet'],before)
  rev=self.s()['play']['revision'];self.act(action='game_start',key='rps',choice='rock',wager=1,revision=rev);before=self.s()['balance']['wallet']
  with self.assertRaises(ValueError):self.act(action='game_start',key='rps',choice='rock',wager=1,revision=rev)
  self.assertEqual(self.s()['balance']['wallet'],before)
