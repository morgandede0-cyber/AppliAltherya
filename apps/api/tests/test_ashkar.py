import unittest,tempfile,sys,json
from pathlib import Path
from unittest.mock import patch
from concurrent.futures import ThreadPoolExecutor
sys.path.insert(0,str(Path(__file__).parents[1]))
from activity import Activity
from ashkar_combat import FLOORS
from progression import ASHKAR_FLOOR_XP
class AshkarTests(unittest.TestCase):
 def setUp(self):
  self.t=tempfile.TemporaryDirectory();self.a=Activity(self.t.name+'/test.db');(self.uid,self.name),_=self.a.session('');self.a.snapshot(self.uid,self.name)
  with self.a.conn() as c:
   c.execute('UPDATE tutorial_progress SET completed=1');c.execute('UPDATE activity_tutorial_revision SET finished=1');c.execute('UPDATE castle_profiles SET xp=10000 WHERE user_id=?',(self.uid,));c.execute('UPDATE players SET wallet_gold=1000 WHERE user_id=?',(self.uid,))
 def tearDown(self):self.t.cleanup()
 def s(self):return self.a.snapshot(self.uid,self.name)['ashkar']
 def act(self,action='ashkar_start',**body):
  s=self.s();b=dict(action=action,revision=s['revision'],floor=s['progress']+1);b.update(body);return self.a.action(self.uid,b)
 def weaken(self):
  with self.a.conn() as c:
   p=json.loads(c.execute('SELECT payload FROM activity_ashkar WHERE user_id=?',(self.uid,)).fetchone()[0]);p['arena_battle']['fighters'][1]['hp']=1;c.execute('UPDATE activity_ashkar SET payload=? WHERE user_id=?',(json.dumps(p),self.uid))
 def win(self):self.act();self.weaken();self.act('ashkar_step',key='light')
 def test_level_tutorial_and_floor_guards(self):
  with self.a.conn() as c:c.execute('UPDATE castle_profiles SET xp=0')
  self.assertFalse(self.s()['available'])
  with self.assertRaises(ValueError):self.act()
  with self.a.conn() as c:c.execute('UPDATE castle_profiles SET xp=10000');c.execute('UPDATE tutorial_progress SET completed=0')
  with self.assertRaises(ValueError):self.act()
  with self.a.conn() as c:c.execute('UPDATE tutorial_progress SET completed=1')
  for body in [dict(floor=2),dict(revision=True),dict(revision=-1),dict(floor=True)]:
   with self.assertRaises(ValueError):self.act(**body)
 def test_real_riposte_cooldown_and_restart(self):
  self.act();s=self.s();hp=s['battle']['player_hp'];ehp=s['battle']['enemy_hp']
  with patch('ashkar_combat.random.random',return_value=.99),patch('ashkar_combat.random.uniform',return_value=1):self.act('ashkar_step',key='light')
  s=self.s();self.assertLess(s['battle']['player_hp'],hp);self.assertLess(s['battle']['enemy_hp'],ehp)
  self.act('ashkar_step',key='ultimate');self.assertEqual(self.s()['battle']['ultimate_cd'],2)
  with self.assertRaises(ValueError):self.act('ashkar_step',key='ultimate')
  self.act('ashkar_step',key='defend');self.assertEqual(self.s()['battle']['ultimate_cd'],1);self.a=Activity(self.a.path);self.assertEqual(self.s()['battle']['ultimate_cd'],1)
  self.act('ashkar_step',key='light');self.assertEqual(self.s()['battle']['ultimate_cd'],0)
 def test_reward_once_and_equipment_currency_at_five(self):
  with self.a.conn() as c:c.execute('UPDATE ashkar_progress SET max_floor=4 WHERE user_id=?',(self.uid,))
  before=self.a.snapshot(self.uid,self.name);self.win();after=self.a.snapshot(self.uid,self.name)
  self.assertEqual(after['balance']['wallet']-before['balance']['wallet'],30);self.assertEqual(after['stats']['xp']-before['stats']['xp'],28);self.assertEqual(after['khaz']['pouciel']-before['khaz']['pouciel'],1);self.assertEqual(after['ashkar']['progress'],5)
  with self.assertRaises(ValueError):self.act('ashkar_step',key='light')
  self.a=Activity(self.a.path);self.assertEqual(self.s()['progress'],5);self.assertEqual(self.a.snapshot(self.uid,self.name)['khaz']['pouciel'],1)
 def test_three_clears_daily_and_midnight(self):
  with patch('ashkar.today',return_value='2026-10-19'):
   for _ in range(3):self.win()
   self.assertEqual(self.s()['remaining'],0)
   with self.assertRaises(ValueError):self.act()
  with patch('ashkar.today',return_value='2026-10-20'):
   self.assertEqual(self.s()['remaining'],3);self.act();self.assertEqual(self.s()['floor'],4)
 def test_loss_and_abandon_preserve_progress_and_rewards(self):
  self.win();before=self.a.snapshot(self.uid,self.name);self.act();self.act('ashkar_step',key='abandon');s=self.a.snapshot(self.uid,self.name)
  self.assertEqual(s['ashkar']['progress'],1);self.assertEqual(s['ashkar']['daily_cleared'],1);self.assertEqual(s['balance'],before['balance']);self.assertEqual(s['stats']['xp'],before['stats']['xp']);self.act();self.assertEqual(self.s()['floor'],2)
 def test_concurrent_victory_one_receipt(self):
  self.act();self.weaken();body=dict(action='ashkar_step',key='light',revision=self.s()['revision'])
  def invoke(_):
   try:self.a.action(self.uid,body);return True
   except ValueError:return False
  with ThreadPoolExecutor(max_workers=2) as p:self.assertEqual(sum(p.map(invoke,range(2))),1)
  with self.a.conn() as c:self.assertEqual(c.execute('SELECT COUNT(*) FROM activity_ashkar_receipts').fetchone()[0],1)
 def test_cross_activity_lock_and_forge_lock(self):
  self.act()
  for body in [dict(action='battle_start',revision=0,wager=0),dict(action='game_start',revision=0,key='coin',wager=1),dict(action='campaign_battle',key='start'),dict(action='khaz_buy',slot='weapon',branch='atk',revision=0)]:
   with self.assertRaises(ValueError):self.a.action(self.uid,body)
  self.act('ashkar_step',key='abandon');self.a.action(self.uid,dict(action='battle_start',revision=self.a.snapshot(self.uid,self.name)['play']['revision'],wager=0))
  with self.assertRaises(ValueError):self.act()
 def test_atomic_rollback_if_reward_write_fails(self):
  self.act();self.weaken();before=self.s()
  with patch.object(self.a.castle,'add_xp',side_effect=RuntimeError('test rollback')):
   with self.assertRaises(RuntimeError):self.act('ashkar_step',key='light')
  s=self.s();self.assertEqual(s['revision'],before['revision']);self.assertEqual(s['progress'],0);self.assertEqual(s['status'],'active')
  with self.a.conn() as c:self.assertEqual(c.execute('SELECT COUNT(*) FROM activity_ashkar_receipts').fetchone()[0],0);self.assertEqual(c.execute('SELECT wallet_gold FROM players WHERE user_id=?',(self.uid,)).fetchone()[0],1000)
 def test_boss_and_legacy_progress_preserved(self):
  with self.a.conn() as c:c.execute('UPDATE ashkar_progress SET max_floor=9 WHERE user_id=?',(self.uid,))
  self.a=Activity(self.a.path);self.win();s=self.a.snapshot(self.uid,self.name);self.assertTrue(s['ashkar']['complete']);self.assertEqual(s['khaz']['pouciel'],3);self.assertEqual(s['ashkar']['result']['xp'],75)
  with self.assertRaises(ValueError):self.act()
 def test_equipment_and_catalog_exact(self):
  with self.a.conn() as c:c.execute("INSERT INTO legacy_equipment VALUES(?,'weapon','atk','legendaire')",(self.uid,))
  self.act()
  with self.a.conn() as c:p=json.loads(c.execute('SELECT payload FROM activity_ashkar WHERE user_id=?',(self.uid,)).fetchone()[0])
  self.assertEqual(p['arena_battle']['fighters'][0]['class_key'],'arena_fighter');self.assertGreater(p['arena_battle']['fighters'][0]['equipment_atk_pct'],0)
  self.assertEqual([(f['gold'],f['pouciel'],f['xp']) for f in self.s()['floors']],[(FLOORS[i]['gold'],FLOORS[i]['pouciel'],ASHKAR_FLOOR_XP[i]) for i in range(1,11)])
if __name__=='__main__':unittest.main()
