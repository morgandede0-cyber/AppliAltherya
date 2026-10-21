import sys, unittest, tempfile, uuid
from pathlib import Path
from unittest.mock import patch
sys.path.insert(0,str(Path(__file__).parents[1]))
from activity import Activity
from arena_engine import Fighter,BattleState
import arena_combat

class ArenaCompleteTests(unittest.TestCase):
 def setUp(self):
  self.tmp=tempfile.TemporaryDirectory();self.a=Activity(self.tmp.name+'/arena.db');(self.uid,self.name),_=self.a.session('');self.a.snapshot(self.uid,self.name)
  with self.a.conn() as c:
   c.execute('UPDATE tutorial_progress SET completed=1');c.execute('UPDATE activity_tutorial_revision SET finished=1');c.execute('UPDATE players SET wallet_gold=100 WHERE user_id=?',(self.uid,))
 def tearDown(self):self.tmp.cleanup()
 def state(self):return self.a.snapshot(self.uid,self.name)
 def act(self,action,**kw):return self.a.action(self.uid,dict(action=action,revision=self.state()['play']['revision'],**kw))
 def test_ten_profiles_have_real_distinct_patterns_and_contextual_responses(self):
  self.assertEqual(len({arena_combat.champion(i)['role'] for i in range(1,11)}),10)
  actions=[]
  for i in range(1,11):
   b=BattleState('test','champion',0,[Fighter(1,'Moi','arena_fighter'),Fighter(None,'Ennemi','ravageur',champion_level=i)],0);p={};arena_combat.init(p,b)
   actions.append(tuple(arena_combat.choose({**p,'round':n},b) for n in range(1,5)))
  self.assertGreaterEqual(len(set(actions)),9)
  b.fighters[1].champion_level=9;p['last_action']='heavy';self.assertEqual(arena_combat.choose(p,b),'defend')
  p['last_action']='defend';self.assertEqual(arena_combat.choose(p,b),'ultimate')
 def test_locked_intent_is_resolved_and_structured_events_match_hp(self):
  self.act('battle_start',wager=0);before=self.state()['play'];intent=before['intent']['key']
  with patch('arena_engine.random.random',return_value=0):self.act('battle_step',key='defend')
  after=self.state()['play'];self.assertEqual(after['events'][-1]['action'],intent)
  self.assertEqual(after['events'][-1]['damage'],before['fighters'][0]['hp']-after['fighters'][0]['hp'])
  self.assertEqual(after['events'][0]['kind'],'guard');self.assertTrue(after['events'][-1]['guarded'])
  self.assertNotIn('battle',after);self.assertEqual(after['combat_stats'][1]['damage'],after['events'][-1]['damage'])
 def test_phase_boost_triggers_once_and_never_revives_dead_champion(self):
  b=BattleState('test','champion',0,[Fighter(1,'Moi','arena_fighter'),Fighter(None,'Roi','ravageur',champion_level=10)],0);p={};arena_combat.init(p,b)
  b.fighters[1].hp=20;arena_combat.phase(p,b);self.assertEqual(p['phase'],2);self.assertEqual(b.fighters[1].next_damage_bonus,.2)
  b.fighters[1].next_damage_bonus=0;arena_combat.phase(p,b);self.assertEqual(b.fighters[1].next_damage_bonus,0)
  p['phase']=1;b.fighters[1].hp=0;arena_combat.phase(p,b);self.assertEqual(p['phase'],1)
 def finish_win(self):
  self.act('battle_start',wager=10);_,p=self.a.play.read(self.uid);p['battle']['fighters'][1]['hp']=1;self.a.play.save(self.uid,p)
  with patch('arena_engine.random.random',return_value=0):self.act('battle_step',key='light')
  return self.state()['play']
 def test_complete_result_net_xp_rating_and_history_persist_and_cannot_repay(self):
  p=self.finish_win();r=p['result'];self.assertEqual((r['wager'],r['payout'],r['net_gold']),(10,20,10));self.assertEqual(r['xp'],40);self.assertEqual(r['rating_delta'],30);self.assertEqual(len(r['fighters']),2);self.assertTrue(r['events']);self.assertTrue(r['logs']);self.assertIn('heavy',r['skills'])
  self.assertEqual(r['next_champion']['level'],2);self.assertEqual(r['wins_after'],1);self.assertTrue(r['won'])
  self.assertEqual(self.state()['balance']['wallet'],110)
  with self.assertRaises(ValueError):self.act('battle_step',key='light')
  self.a=Activity(self.a.path);s=self.state();self.assertEqual(s['arena']['recent'][0],r);self.assertEqual(s['balance']['wallet'],110)
  with self.a.conn() as c:self.assertEqual(c.execute('SELECT COUNT(*) FROM activity_arena_results').fetchone()[0],1)
 def test_defeat_shows_lost_wager_real_clamped_rating_and_actual_xp(self):
  self.act('battle_start',wager=10);self.act('battle_step',key='abandon');r=self.state()['play']['result']
  self.assertEqual((r['net_gold'],r['xp'],r['rating_delta']),(-10,10,0));self.assertTrue(r['abandoned']);self.assertFalse(r['won']);self.assertEqual(r['wins_after'],0)
 def test_tenth_victory_caps_circuit_without_champion_eleven(self):
  with self.a.conn() as c:c.execute('INSERT INTO arena_progress(user_id,rating,champion_wins) VALUES(?,300,9)',(self.uid,))
  p=self.finish_win();self.assertTrue(p['result']['circuit_complete']);self.assertEqual(p['result']['next_champion']['level'],10);self.assertEqual(p['result']['wins_after'],10)
 def test_ultimate_cooldown_and_client_tampering_are_checked_on_server(self):
  self.act('battle_start',wager=0)
  self.act('battle_step',key='ultimate',net_gold=99999,xp=99999,champion_level=10)
  self.assertEqual(self.state()['play']['champion']['level'],1)
  with self.assertRaises(ValueError):self.act('battle_step',key='ultimate')
  self.assertEqual(self.state()['balance']['wallet'],100)
 def test_receipt_replay_of_finishing_turn_does_not_append_history_or_awards(self):
  self.act('battle_start',wager=10);_,p=self.a.play.read(self.uid);p['battle']['fighters'][1]['hp']=1;self.a.play.save(self.uid,p)
  body=dict(action='battle_step',key='light',revision=self.state()['play']['revision'],request_id=str(uuid.uuid4()))
  with patch('arena_engine.random.random',return_value=0):self.a.action(self.uid,body)
  self.a.action(self.uid,body);s=self.state();self.assertEqual(s['balance']['wallet'],110);self.assertEqual(s['stats']['wins'],1);self.assertEqual(len(s['arena']['recent']),1)
 def test_fatal_bleed_is_reported_without_counting_a_guard_not_executed(self):
  self.act('battle_start',wager=0);_,p=self.a.play.read(self.uid);p['battle']['fighters'][0]['hp']=2;p['battle']['fighters'][0]['bleed_pending']=4;self.a.play.save(self.uid,p)
  self.act('battle_step',key='defend');p=self.state()['play'];self.assertEqual(p['result']['hp'],0);self.assertEqual(p['events'][-1]['kind'],'bleed');self.assertEqual(p['result']['stats'][0]['guards'],0);self.assertEqual(p['result']['stats'][1]['damage'],2)
 def test_failure_writing_report_rolls_back_awards_and_game(self):
  self.act('battle_start',wager=10)
  with patch.object(self.a.play,'battle_public',side_effect=RuntimeError('write interrupted')):
   with self.assertRaises(RuntimeError):self.act('battle_step',key='abandon')
  s=self.state();self.assertEqual(s['play']['status'],'active');self.assertEqual(s['balance']['wallet'],90);self.assertEqual(s['arena']['recent'],[]);self.assertEqual(s['stats']['losses'],0)

if __name__=='__main__':unittest.main()
