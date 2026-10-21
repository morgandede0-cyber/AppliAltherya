import unittest,json,sys
from pathlib import Path
from unittest.mock import patch
sys.path.insert(0,str(Path(__file__).parents[1]));sys.path.insert(0,str(Path(__file__).parent))
import test_ashkar as harness
import arena_combat

class SharedTowerTests(unittest.TestCase):
 def boss_win(self):
  with self.a.conn() as c:c.execute('UPDATE ashkar_progress SET max_floor=9 WHERE user_id=?',(self.uid,))
  self.win()
 setUp=harness.AshkarTests.setUp
 tearDown=harness.AshkarTests.tearDown
 s=harness.AshkarTests.s
 act=harness.AshkarTests.act
 weaken=harness.AshkarTests.weaken
 win=harness.AshkarTests.win
 def test_win_grants_shared_skill_and_replay_never_pays_twice(self):
  self.boss_win();s=self.a.snapshot(self.uid,self.name);card=next(t for t in s['arena']['techniques'] if t['id']=='ashkar_10');self.assertTrue(card['unlocked']);self.assertEqual(s['ashkar']['result']['technique_unlocked']['id'],'ashkar_10')
  before=(s['balance'],s['stats']['xp'],s['khaz']['pouciel'],s['ashkar']['daily_cleared'])
  self.act(floor=10);self.weaken();self.act('ashkar_step',key='light');s=self.a.snapshot(self.uid,self.name);self.assertEqual(before,(s['balance'],s['stats']['xp'],s['khaz']['pouciel'],s['ashkar']['daily_cleared']));self.assertTrue(s['ashkar']['result']['replay']);self.assertIsNone(s['ashkar']['result']['technique_unlocked'])
  with self.a.conn() as c:self.assertEqual(c.execute('SELECT COUNT(*) FROM activity_ashkar_techniques').fetchone()[0],1)
 def test_old_progress_can_earn_missing_skill_without_reset(self):
  with self.a.conn() as c:c.execute('UPDATE ashkar_progress SET max_floor=10');c.execute('UPDATE ashkar_daily SET cleared=3')
  self.act(floor=10);self.weaken();self.act('ashkar_step',key='light');s=self.a.snapshot(self.uid,self.name);self.assertEqual(s['ashkar']['progress'],10);self.assertEqual(s['ashkar']['daily_cleared'],3);self.assertEqual(s['ashkar']['result']['gold'],0);self.assertEqual(s['khaz']['pouciel'],0);self.assertEqual(s['ashkar']['result']['technique_unlocked']['id'],'ashkar_10')
 def test_shared_equipment_and_effect_in_both_modes(self):
  self.boss_win();s=self.a.snapshot(self.uid,self.name);self.a.action(self.uid,dict(action='arena_equip',slot='ultimate',technique='ashkar_10',loadout_revision=s['arena']['loadout_revision']))
  self.act(floor=10);s=self.s();self.assertEqual(s['combat']['skills']['ultimate']['id'],'ashkar_10')
  with patch('arena_engine.random.random',return_value=.5),patch('arena_engine.random.uniform',return_value=1):self.act('ashkar_step',key='ultimate')
  self.assertTrue(any('Serment de Varkhaz' in e['text'] for e in self.s()['combat']['events']));self.act('ashkar_step',key='abandon')
  s=self.a.snapshot(self.uid,self.name);self.a.action(self.uid,dict(action='battle_start',revision=s['play']['revision'],wager=0));s=self.a.snapshot(self.uid,self.name);self.assertEqual(s['play']['skills']['ultimate']['id'],'ashkar_10')
  with patch('arena_engine.random.random',return_value=.5),patch('arena_engine.random.uniform',return_value=1):self.a.action(self.uid,dict(action='battle_step',revision=s['play']['revision'],key='ultimate'))
  self.assertTrue(any('Serment de Varkhaz' in e['text'] for e in self.a.snapshot(self.uid,self.name)['play']['events']))
 def test_loadout_frozen_and_defeat_never_grants(self):
  self.act();s=self.a.snapshot(self.uid,self.name)
  with self.assertRaises(ValueError):self.a.action(self.uid,dict(action='arena_equip',slot='ultimate',technique='base_ultimate',loadout_revision=s['arena']['loadout_revision']))
  self.act('ashkar_step',key='abandon');self.assertFalse(any(t['unlocked'] for t in self.a.snapshot(self.uid,self.name)['arena']['techniques'] if t.get('source_kind')=='tower'))
 def test_original_arena_effects_and_tactics_are_called(self):
  self.act()
  with patch('arena_combat.resolve',wraps=arena_combat.resolve) as resolve:self.act('ashkar_step',key='defend');self.assertEqual(resolve.call_count,2)
  s=self.s();self.assertEqual(len(s['combat']['events']),2);self.assertEqual(len(s['combat']['combat_stats']),2);self.assertTrue(s['combat']['intent']['name'])
 def test_legacy_active_fight_keeps_hp_fraction_and_cooldown(self):
  with self.a.conn() as c:
   from ashkar_combat import BattleState
   from dataclasses import asdict
   b=BattleState(self.uid,1,'arena_fighter','Ancien',10,95,190,120,87,111,0,325,650,70,35,94,ultimate_cd=2)
   c.execute('UPDATE activity_ashkar SET payload=? WHERE user_id=?',(json.dumps(dict(status='active',floor=1,battle=asdict(b),logs=['Ancien journal'],turn=2)),self.uid))
  self.act('ashkar_step',key='defend');s=self.s();self.assertLessEqual(s['battle']['player_hp'],95);self.assertEqual(s['battle']['enemy_hp'],54);self.assertEqual(s['battle']['ultimate_cd'],1);self.assertTrue(s['combat']);self.assertIn('Ancien journal',s['logs'])
 def test_shared_collection_and_replacement_survive_restart(self):
  self.boss_win();s=self.a.snapshot(self.uid,self.name);self.a.action(self.uid,dict(action='arena_equip',slot='ultimate',technique='ashkar_10',loadout_revision=s['arena']['loadout_revision']))
  from activity import Activity
  self.a=Activity(self.a.path);s=self.a.snapshot(self.uid,self.name);self.assertEqual(s['arena']['skills']['ultimate']['id'],'ashkar_10')
  with self.assertRaises(ValueError):self.a.action(self.uid,dict(action='arena_equip',slot='light',technique='ashkar_10',loadout_revision=s['arena']['loadout_revision']))
  self.a.action(self.uid,dict(action='arena_equip',slot='ultimate',technique='base_ultimate',loadout_revision=s['arena']['loadout_revision']));self.assertTrue(next(t for t in self.a.snapshot(self.uid,self.name)['arena']['techniques'] if t['id']=='ashkar_10')['unlocked'])
if __name__=='__main__':unittest.main()
