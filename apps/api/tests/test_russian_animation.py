import unittest
from unittest.mock import patch
import test_play as fixtures
class RussianAnimationTests(unittest.TestCase):
 setUp=fixtures.GameTests.setUp
 tearDown=fixtures.GameTests.tearDown
 s=fixtures.GameTests.s
 act=fixtures.GameTests.act
 access=fixtures.GameTests.access
 def test_all_six_positions_preserve_payout_and_private_outcome(self):
  self.access()
  for danger in range(1,7):
   with self.subTest(danger=danger):
    before=self.s()['balance']['wallet']
    with patch('play.random.randint',return_value=danger):self.act(action='game_start',key='russian',wager=1)
    p=self.s()['play'];self.assertNotIn('danger',p);self.assertEqual(p['chambers_remaining'],6);self.assertEqual(p['cartridges_remaining'],1)
    while p['status']=='active':
     previous=p['step'];self.act(action='game_step',key='try');p=self.s()['play'];self.assertNotIn('danger',p);self.assertEqual(p['chambers_remaining'],6-p['step']);self.assertLessEqual(p['step']-previous,2);self.assertEqual(len(p['events']),p['step']);self.assertEqual(p['cartridges_remaining'],int(p['status']=='active'))
     self.assertEqual([e['chamber'] for e in p['events']],list(range(1,p['step']+1)));self.assertTrue(all(not e['spent'] for e in p['events'][:-1]))
    self.assertEqual(p['step'],danger);self.assertTrue(p['events'][-1]['spent']);self.assertEqual(p['payout'],2 if danger%2==0 else 0);self.assertEqual(self.s()['balance']['wallet'],before-1+p['payout'])
 def test_stale_step_does_not_repeat_or_repay(self):
  self.access()
  with patch('play.random.randint',return_value=6):self.act(action='game_start',key='russian',wager=1)
  rev=self.s()['play']['revision'];self.act(action='game_step',key='try',revision=rev);before=self.s()
  with self.assertRaises(ValueError):self.act(action='game_step',key='try',revision=rev)
  self.assertEqual(self.s()['play']['step'],before['play']['step']);self.assertEqual(self.s()['balance']['wallet'],before['balance']['wallet'])
