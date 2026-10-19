import unittest
from unittest.mock import patch
import test_play as fixtures
from casino_engine import SLOT_SYMBOLS,SLOT_WEIGHTS,SLOT_TRIPLE_MULTIPLIERS
class SlotsTests(unittest.TestCase):
 setUp=fixtures.GameTests.setUp
 tearDown=fixtures.GameTests.tearDown
 s=fixtures.GameTests.s
 act=fixtures.GameTests.act
 access=fixtures.GameTests.access
 def test_public_rules_match_the_actual_engine(self):
  rules=self.s()['casino']['slots']
  self.assertEqual([x['key'] for x in rules['symbols']],SLOT_SYMBOLS)
  self.assertEqual([x['weight'] for x in rules['symbols']],SLOT_WEIGHTS)
  self.assertEqual([x['multiplier'] for x in rules['symbols']],[SLOT_TRIPLE_MULTIPLIERS[s] for s in SLOT_SYMBOLS])
 def test_all_triples_and_two_sevens_settle_once(self):
  self.access()
  for symbol in SLOT_SYMBOLS:
   before=self.s()['balance']['wallet'];rev=self.s()['play']['revision']
   with patch('play.draw_slot',return_value=[symbol]*3):self.act(action='game_start',key='slots',wager=10,revision=rev)
   p=self.s()['play'];self.assertEqual(p['reels'],[symbol]*3);self.assertEqual(p['payout'],10*SLOT_TRIPLE_MULTIPLIERS[symbol]);self.assertEqual(self.s()['balance']['wallet'],before-10+p['payout'])
   with self.assertRaises(ValueError):self.act(action='game_start',key='slots',wager=10,revision=rev)
  with patch('play.draw_slot',return_value=['7️⃣','🍒','7️⃣']):self.act(action='game_start',key='slots',wager=10)
  self.assertEqual(self.s()['play']['payout'],10)
 def test_mixed_symbols_pay_zero(self):
  self.access();before=self.s()['balance']['wallet']
  with patch('play.draw_slot',return_value=['🍒','🔔','💎']):self.act(action='game_start',key='slots',wager=10)
  self.assertEqual(self.s()['play']['payout'],0);self.assertEqual(self.s()['balance']['wallet'],before-10)
