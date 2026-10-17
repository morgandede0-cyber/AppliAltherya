import unittest,sys
from pathlib import Path
from unittest.mock import patch
sys.path.insert(0,str(Path(__file__).parents[1]))
import test_arena_complete as harness
from activity import Activity
import arena_techniques as tech,arena_combat
from arena_engine import Fighter,BattleState,resolve_action,arena_player_skills

class ArenaTechniqueTests(unittest.TestCase):
 setUp=harness.ArenaCompleteTests.setUp
 tearDown=harness.ArenaCompleteTests.tearDown
 state=harness.ArenaCompleteTests.state
 act=harness.ArenaCompleteTests.act
 finish_win=harness.ArenaCompleteTests.finish_win
 def unlock(self,n):
  with self.a.conn() as c:c.execute('INSERT INTO arena_progress(user_id,rating,champion_wins) VALUES(?,0,?) ON CONFLICT(user_id) DO UPDATE SET champion_wins=excluded.champion_wins',(self.uid,n));[tech.grant(c,self.uid,i) for i in range(1,n+1)]
 def equip(self,slot,id,**kw):return self.act('arena_equip',slot=slot,technique=id,loadout_revision=self.state()['arena']['loadout_revision'],**kw)
 def test_victory_grants_once_and_defeat_grants_nothing(self):
  p=self.finish_win();self.assertEqual(p['result']['technique_unlocked']['id'],'c1');self.assertEqual(self.state()['arena']['techniques'][0]['unlocked'],True)
  with self.a.conn() as c:self.assertEqual(c.execute('SELECT COUNT(*) FROM activity_arena_techniques').fetchone()[0],1);c.execute('UPDATE arena_champion SET last_started_utc=NULL')
  self.act('battle_start',wager=0);self.act('battle_step',key='abandon');self.assertIsNone(self.state()['play']['result'].get('technique_unlocked'));self.assertFalse(self.state()['arena']['techniques'][1]['unlocked'])
 def test_earned_collection_preserves_money_and_loadout_after_restart(self):
  self.unlock(6);self.assertEqual(sum(t['unlocked'] for t in self.state()['arena']['techniques']),6)
  self.equip('heavy','c1');self.a=Activity(self.a.path);s=self.state();self.assertEqual(s['arena']['skills']['heavy']['id'],'c1');self.assertEqual(s['balance']['wallet'],100)
  self.equip('heavy','base_heavy');self.assertEqual(self.state()['arena']['skills']['heavy']['name'],'Coup puissant');self.assertTrue(self.state()['arena']['techniques'][0]['unlocked'])
 def test_validation_unowned_wrong_slot_stale_version_and_other_player(self):
  with self.assertRaises(ValueError):self.equip('heavy','c1')
  self.unlock(1)
  with self.assertRaises(ValueError):self.equip('ultimate','c1')
  with self.assertRaises(ValueError):self.equip('bad','c1')
  self.equip('heavy','c1')
  with self.assertRaises(ValueError):self.act('arena_equip',slot='heavy',technique='base_heavy',loadout_revision=0)
  (other,name),_=self.a.session('');self.a.snapshot(other,name)
  self.assertFalse(self.a.play.technique_book(other)['techniques'][0]['unlocked'])
 def test_combat_freezes_actual_equipped_skill_and_rejects_replacement(self):
  self.unlock(1);self.equip('heavy','c1');self.act('battle_start',wager=0)
  self.assertEqual(self.state()['play']['skills']['heavy']['name'],'Lacération')
  with self.assertRaises(ValueError):self.equip('heavy','base_heavy')
  with patch('arena_engine.random.random',return_value=.4):self.act('battle_step',key='heavy')
  p=self.state()['play'];self.assertEqual(p['events'][0]['skill'],'Lacération');self.assertIn('saignement',p['events'][0]['text'])
 def battle(self,n):
  p=tech.ArenaFighter(1,'Joueur','arena_fighter');p.loadout=arena_player_skills(1);t=tech.CATALOG[n];p.loadout[t['slot']]={**p.loadout[t['slot']],**t}
  b=BattleState('test','champion',0,[p,Fighter(None,'Cible','arena_fighter')],0)
  return b,p,b.fighters[1],t['slot']
 def resolve(self,b,slot):
  with patch('arena_engine.random.random',return_value=.4),patch('arena_engine.random.uniform',return_value=1.):return tech.resolve(b,slot,resolve_action)
 def test_bleed_evade_charge_and_shake_have_real_effects(self):
  for n,field,value in [(1,'bleed_pending',4),(3,'temp_evade',.1),(4,'next_damage_bonus',.2),(8,'shaken',True)]:
   b,p,t,slot=self.battle(n);self.resolve(b,slot);self.assertEqual(getattr(t if n in (1,8) else p,field),value)
 def test_three_guards_and_counter_tradeoff(self):
  for n,reduction in [(2,.55),(5,.35),(9,.25)]:
   b,p,t,slot=self.battle(n);self.resolve(b,slot);self.assertEqual(p.defend_reduction,reduction)
   if n==2:self.assertTrue(p.shaken)
   if n==9:self.assertEqual(p.temp_evade,.1)
   if n==5:b.switch();self.resolve(b,'light');self.assertTrue(p.counter_ready)
 def test_pierce_only_benefits_guarded_targets_and_preserves_guard_on_miss(self):
  b,p,t,slot=self.battle(6);t.defending=True;t.defend_reduction=.6;self.resolve(b,slot);pierced=100-t.hp
  b,p,t,slot=self.battle(6);t.defending=True;t.defend_reduction=.6;p.loadout[slot]={**p.loadout[slot],'effect':None};self.resolve(b,slot);self.assertGreater(pierced,100-t.hp)
  b,p,t,slot=self.battle(6);t.defending=True;t.defend_reduction=.6
  with patch('arena_engine.random.random',return_value=.999):tech.resolve(b,slot,resolve_action)
  self.assertTrue(t.defending);self.assertEqual(t.defend_reduction,.6)
 def test_execute_threshold_king_cost_and_catalog_unchanged(self):
  b,p,t,slot=self.battle(7);t.max_hp=300;t.hp=300;self.resolve(b,slot);normal=300-t.hp
  b,p,t,slot=self.battle(7);t.max_hp=300;t.hp=105;self.resolve(b,slot);self.assertGreater(105-t.hp,normal);self.assertEqual(p.cfg['skills'][slot]['power'],28)
  b,p,t,slot=self.battle(10);p.hp=50;self.resolve(b,slot);self.assertEqual(p.bleed_pending,3);self.assertEqual(p.cfg['skills'][slot]['power'],30)
 def test_dead_actor_does_not_receive_technique_effect_and_base_engine_unchanged(self):
  b,p,t,slot=self.battle(2);p.hp=2;p.bleed_pending=4;self.resolve(b,slot);self.assertFalse(p.defending);self.assertFalse(p.shaken)
  self.assertEqual(arena_player_skills(1)['heavy']['name'],'Coup puissant')
 def test_unlock_failure_rolls_back_win_award_and_report(self):
  self.act('battle_start',wager=10);_,p=self.a.play.read(self.uid);p['battle']['fighters'][1]['hp']=1;self.a.play.save(self.uid,p)
  with patch('arena_techniques.grant',side_effect=RuntimeError('disk')),self.assertRaises(RuntimeError):self.act('battle_step',key='light')
  s=self.state();self.assertEqual(s['play']['status'],'active');self.assertEqual(s['balance']['wallet'],90);self.assertEqual(s['arena']['champion_wins'],0);self.assertFalse(s['arena']['techniques'][0]['unlocked'])
 def test_scaling_tracks_base_level_and_keeps_slot_identity(self):
  with self.a.conn() as c:b=tech.book(c,self.uid,15,10)
  self.assertEqual(next(t for t in b['techniques'] if t['id']=='c1')['power'],round(24*39/26));self.assertEqual(b['skills']['heavy']['name'],'Impact dévastateur')

 def test_custom_guard_preserves_nonfatal_bleed_in_journal(self):
  b,p,t,slot=self.battle(2);p.bleed_pending=4;lines=self.resolve(b,slot);self.assertEqual(p.hp,96);self.assertIn('saignement',' '.join(lines));self.assertIn('Forteresse',' '.join(lines))
