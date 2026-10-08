import unittest,tempfile,sys,time,json
from pathlib import Path
from unittest.mock import patch
sys.path.insert(0,str(Path(__file__).parents[1]))
from activity import Activity
from play import total
class GameTests(unittest.TestCase):
 def setUp(self):
  self.tmp=tempfile.TemporaryDirectory();self.a=Activity(self.tmp.name+'/games.sqlite3');(self.uid,self.name),_=self.a.session('');self.s()
  with self.a.conn() as c:c.execute('UPDATE players SET wallet_gold=10000 WHERE user_id=?',(self.uid,))
 def tearDown(self):self.tmp.cleanup()
 def s(self):return self.a.snapshot(self.uid,self.name)
 def act(self,**b):return self.a.action(self.uid,{'revision':self.s()['play']['revision'],**b})
 def access(self):self.act(action='guard',key='pay')
 def test_access_atomic_and_no_second_charge(self):
  self.access();self.access();self.assertEqual(self.s()['balance']['wallet'],9850);self.assertTrue(self.s()['alley']['access']['valid'])
 def test_no_bets_without_access_or_invalid_wager(self):
  with self.assertRaises(ValueError):self.act(action='game_start',key='slots',wager=10)
  self.access();before=self.s()['balance']['wallet']
  for v in [0,-1,True,1.3,'10',501]:
   with self.assertRaises(ValueError):self.act(action='game_start',key='slots',wager=v)
  self.assertEqual(before,self.s()['balance']['wallet'])
 def test_replayed_bet_does_not_debit_or_pay_twice(self):
  self.access();rev=self.s()['play']['revision']
  with patch('play.draw_slot',return_value=['7️⃣']*3):self.act(action='game_start',key='slots',wager=10,revision=rev)
  self.assertEqual(self.s()['play']['payout'],120);before=self.s()['balance']['wallet']
  with self.assertRaises(ValueError):self.act(action='game_start',key='slots',wager=10,revision=rev)
  self.assertEqual(before,self.s()['balance']['wallet']);self.assertEqual(self.s()['stats']['casino_games'],1);self.assertEqual(self.s()['xp'],3)
 def test_roulette_zero_not_even(self):
  self.access()
  with patch('play.roulette_spin',return_value=(0,'green')):self.act(action='game_start',key='roulette',wager=10,choice='even')
  self.assertEqual(self.s()['play']['payout'],0)
  with patch('play.roulette_spin',return_value=(0,'green')):self.act(action='game_start',key='roulette',wager=10,choice='number',number=0)
  self.assertEqual(self.s()['play']['payout'],360)
 def test_horse_odds_visible_before_wager_are_used(self):
  self.access();odds=self.s()['casino']['odds'];self.assertEqual(odds,self.s()['casino']['odds'])
  with patch('play.random.choices',return_value=[2]):self.act(action='game_start',key='horses',wager=10,choice=2)
  self.assertEqual(self.s()['play']['odds'],odds);self.assertEqual(self.s()['play']['payout'],round(10*odds[2]))
 def test_hidden_cards_and_barrel_are_never_exposed(self):
  self.access()
  with patch('play.random.shuffle',side_effect=lambda d:d.sort(key=lambda c:c['rank']=='A',reverse=True)):self.act(action='game_start',key='blackjack',wager=10)
  p=self.s()['play'];self.assertEqual(p['status'],'active');self.assertNotIn('deck',p);self.assertEqual(p['dealer'][1],{'hidden':True})
  self.act(action='game_cancel');self.act(action='game_start',key='russian',wager=10);self.assertNotIn('danger',self.s()['play'])
 def test_restart_refunds_only_once(self):
  self.access();self.act(action='game_start',key='russian',wager=100);self.assertEqual(self.s()['balance']['wallet'],9750)
  self.a=Activity(self.a.path);self.assertEqual(self.s()['balance']['wallet'],9850);self.assertEqual(self.s()['play']['status'],'refunded');self.a=Activity(self.a.path);self.assertEqual(self.s()['balance']['wallet'],9850)
 def test_tavern_rps_uses_original_french_symbols(self):
  with patch('play.rps_bot',return_value='ciseaux'):self.act(action='game_start',key='rps',wager=10,choice='rock')
  self.assertEqual(self.s()['play']['payout'],20);self.assertEqual(self.s()['xp'],5)
 def test_drink_reputation_limits_are_authoritative(self):
  with self.assertRaises(ValueError):self.act(action='drink',key='whisky')
  self.act(action='drink',key='beer');self.assertEqual(self.s()['tavern']['remaining_today'],1)
  with self.assertRaises(ValueError):self.act(action='drink',key='beer')
 def test_arena_actual_logs_riposte_and_single_xp(self):
  self.act(action='battle_start',wager=0);p=self.s()['play'];self.assertEqual(p['status'],'active');self.assertNotIn('battle',p)
  self.act(action='battle_step',key='defend');p=self.s()['play'];self.assertTrue(len(p['logs'])>=2);self.assertEqual(p['turn'],3)
  self.act(action='battle_step',key='abandon');s=self.s();self.assertEqual(s['play']['outcome'],'defeat');self.assertEqual(s['stats']['combats'],1);self.assertEqual(s['stats']['losses'],1);self.assertEqual(s['xp'],10)
  with self.assertRaises(ValueError):self.act(action='battle_step',key='abandon')
  self.assertEqual(self.s()['xp'],10)
 def test_victory_outcome_is_authoritative_and_not_repaid(self):
  self.act(action='battle_start',wager=10)
  _,p=self.a.play.read(self.uid)
  p['battle']['fighters'][1]['hp']=1
  self.a.play.save(self.uid,p)
  with patch('arena_engine.random.random',return_value=0):
   self.act(action='battle_step',key='light')
  s=self.s();self.assertEqual(s['play']['outcome'],'victory');self.assertGreater(s['play']['payout'],0)
  gold=s['balance']['wallet']
  with self.assertRaises(ValueError):self.act(action='battle_step',key='light')
  self.assertEqual(self.s()['balance']['wallet'],gold)
 def test_cancel_cannot_refund_a_combat(self):
  self.act(action='battle_start',wager=10)
  with self.assertRaises(ValueError):self.act(action='game_cancel')
  self.assertEqual(self.s()['play']['status'],'active')
 def test_accessories_unavailable_and_future_loot_hidden(self):
  with self.assertRaises(ValueError):self.act(action='start',key='elarwyn_foraging',tool='hands',object1='torch')
  self.act(action='start',key='elarwyn_foraging',tool='hands');active=self.s()['active'];self.assertNotIn('loot',active);self.assertEqual(active['revealed_loot'],{});self.assertEqual(active['log'],[])
 def test_blackjack_multiple_aces(self):
  self.assertEqual(total([{'rank':'A'},{'rank':'A'},{'rank':'9'}]),21);self.assertEqual(total([{'rank':'A'},{'rank':'K'},{'rank':'5'}]),16)
if __name__=='__main__':unittest.main()
