import unittest,json,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).parents[1]));sys.path.insert(0,str(Path(__file__).parent))
import test_ashkar as harness
from activity import Activity
import arena_techniques
class BossGrimoireTests(unittest.TestCase):
 setUp=harness.AshkarTests.setUp
 tearDown=harness.AshkarTests.tearDown
 s=harness.AshkarTests.s
 act=harness.AshkarTests.act
 weaken=harness.AshkarTests.weaken
 win=harness.AshkarTests.win
 def test_intermediate_guardian_never_grants_a_technique(self):
  self.win();s=self.a.snapshot(self.uid,self.name);self.assertIsNone(s['ashkar']['result']['technique_unlocked']);self.assertIsNone(s['ashkar']['floors'][0]['technique']);self.assertTrue(all(t.get('floor',10)%10==0 for t in s['arena']['techniques']))
  with self.a.conn() as c:
   self.assertIsNone(arena_techniques.grant_tower(c,self.uid,1));self.assertEqual(c.execute('SELECT COUNT(*) FROM activity_ashkar_techniques').fetchone()[0],0)
 def test_retirement_preserves_boss_champions_economy_and_floors(self):
  with self.a.conn() as c:
   for floor in range(1,11):c.execute('INSERT INTO activity_ashkar_techniques VALUES(?,?)',(self.uid,floor))
   arena_techniques.grant(c,self.uid,3)
   for slot,skill in [('heavy','ashkar_1'),('ultimate','ashkar_10'),('light','c3')]:c.execute('INSERT INTO activity_arena_loadout VALUES(?,?,?)',(self.uid,slot,skill))
   c.execute('UPDATE ashkar_progress SET max_floor=7 WHERE user_id=?',(self.uid,))
  before=self.a.snapshot(self.uid,self.name);self.a=Activity(self.a.path);after=self.a.snapshot(self.uid,self.name)
  self.assertEqual(after['balance'],before['balance']);self.assertEqual(after['stats']['xp'],before['stats']['xp']);self.assertEqual(after['ashkar']['progress'],7);self.assertEqual(after['ashkar']['daily_cleared'],before['ashkar']['daily_cleared']);self.assertEqual(after['arena']['skills']['heavy']['id'],'base_heavy');self.assertEqual(after['arena']['skills']['ultimate']['id'],'ashkar_10');self.assertEqual(after['arena']['skills']['light']['id'],'c3')
  version=after['arena']['loadout_revision'];self.a=Activity(self.a.path);self.assertEqual(self.a.snapshot(self.uid,self.name)['arena']['loadout_revision'],version)
  with self.a.conn() as c:self.assertEqual([r[0] for r in c.execute('SELECT floor FROM activity_ashkar_techniques WHERE user_id=?',(self.uid,))],[10])
 def test_saved_combat_retirement_keeps_health_cooldown_and_gear(self):
  self.act()
  with self.a.conn() as c:
   p=json.loads(c.execute('SELECT payload FROM activity_ashkar WHERE user_id=?',(self.uid,)).fetchone()[0]);p['skills']['heavy']=dict(id='ashkar_1',name='Morsure infectée',power=20,accuracy=.82,effect='bleed');p['arena_battle']['fighters'][0]['hp']=70;p['arena_battle']['fighters'][0]['ultimate_cd']=2;p['battle']['player_hp']=70;p['battle']['ultimate_cd']=2;c.execute('UPDATE activity_ashkar SET payload=? WHERE user_id=?',(json.dumps(p),self.uid))
  self.a=Activity(self.a.path);s=self.s();self.assertEqual(s['battle']['player_hp'],70);self.assertEqual(s['battle']['ultimate_cd'],2);self.assertEqual(s['status'],'active');self.assertEqual(s['combat']['skills']['heavy']['id'],'base_heavy');self.assertNotIn('ashkar_1',[x['id'] for x in self.a.snapshot(self.uid,self.name)['arena']['techniques']])
 def test_retired_skill_cannot_be_equipped_even_with_a_stale_client(self):
  s=self.a.snapshot(self.uid,self.name)
  with self.assertRaises(ValueError):self.a.action(self.uid,dict(action='arena_equip',slot='heavy',technique='ashkar_1',loadout_revision=s['arena']['loadout_revision']))
  self.assertEqual(set(arena_techniques.TOWER_CATALOG),{10})
if __name__=='__main__':unittest.main()
