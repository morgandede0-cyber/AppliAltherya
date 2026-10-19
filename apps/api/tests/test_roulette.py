import unittest,sys
from pathlib import Path
from unittest.mock import patch
sys.path.insert(0,str(Path(__file__).parents[1]))
from roulette_rules import normalise_bets,covered,winnings,RED
import test_play as fixtures
class RouletteRulesTests(unittest.TestCase):
 def test_payouts_all_numbers(self):
  for n in range(37):
   bets=normalise_bets([dict(type='number',numbers=[n],amount=2),dict(type='red',amount=3)],5)
   self.assertEqual(winnings(bets,n),72+(6 if n in RED else 0))
 def test_adjacent_and_zero(self):
  for kind,ns,m in [('split',[0,2],18),('street',[0,1,2],12),('corner',[0,1,2,3],9),('six_line',[1,2,3,4,5,6],6),('dozen2',None,3),('column3',None,3)]:
   bets=normalise_bets([dict(type=kind,numbers=ns,amount=2)],2);self.assertEqual(bets[0]['multiplier'],m)
  for k in ['red','black','even','odd','low','high','dozen1','column1']:self.assertNotIn(0,covered(k))
 def test_invalid_bets(self):
  bad=[[],[dict(type='split',numbers=[3,4],amount=1)],[dict(type='number',numbers=[37],amount=1)],[dict(type='red',amount=True)],[dict(type='red',amount=0)],[dict(type='corner',numbers=[3,4,6,7],amount=1)]]
  for b in bad:
   with self.assertRaises(ValueError):normalise_bets(b,1)
  with self.assertRaises(ValueError):normalise_bets([dict(type='red',amount=2)],1)
class RouletteIntegrationTests(unittest.TestCase):
 setUp=fixtures.GameTests.setUp
 tearDown=fixtures.GameTests.tearDown
 s=fixtures.GameTests.s
 act=fixtures.GameTests.act
 access=fixtures.GameTests.access
 def test_combined_bets_debit_once_and_settle_sum_once(self):
  self.access();before=self.s()['balance']['wallet'];rev=self.s()['play']['revision'];bets=[dict(type='number',numbers=[7],amount=2),dict(type='red',amount=3),dict(type='dozen1',amount=5)]
  with patch('play.roulette_spin',return_value=(7,'red')):self.act(action='game_start',key='roulette',wager=10,bets=bets,revision=rev)
  p=self.s()['play'];self.assertEqual(p['payout'],72+6+15);self.assertEqual(self.s()['balance']['wallet'],before-10+93)
  with self.assertRaises(ValueError):self.act(action='game_start',key='roulette',wager=10,bets=bets,revision=rev)
  self.assertEqual(self.s()['balance']['wallet'],before-10+93)
 def test_invalid_selection_never_spends(self):
  self.access();before=self.s()['balance']['wallet']
  with self.assertRaises(ValueError):self.act(action='game_start',key='roulette',wager=10,bets=[dict(type='split',numbers=[3,4],amount=10)])
  self.assertEqual(self.s()['balance']['wallet'],before)
