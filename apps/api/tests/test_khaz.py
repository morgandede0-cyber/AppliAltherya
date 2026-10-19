import unittest,tempfile,sys,json
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
sys.path.insert(0,str(Path(__file__).parents[1]))
from activity import Activity
from khaz import CFG,bonuses_for
class KhazTests(unittest.TestCase):
 def setUp(self):
  self.t=tempfile.TemporaryDirectory();self.a=Activity(self.t.name+'/test.db');(self.uid,self.name),_=self.a.session('');self.a.snapshot(self.uid,self.name)
  with self.a.conn() as c:
   c.execute('UPDATE tutorial_progress SET completed=1 WHERE user_id=?',(self.uid,));c.execute('UPDATE activity_tutorial_revision SET finished=1 WHERE user_id=?',(self.uid,));c.execute('UPDATE castle_profiles SET xp=10000 WHERE user_id=?',(self.uid,));c.execute('UPDATE players SET wallet_gold=10000 WHERE user_id=?',(self.uid,));c.execute('UPDATE legacy_wallet SET pouciel=1000 WHERE user_id=?',(self.uid,))
 def tearDown(self):self.t.cleanup()
 def s(self):return self.a.snapshot(self.uid,self.name)['khaz']
 def act(self,action='khaz_buy',slot='weapon',branch='atk',**extra):
  s=self.s();body=dict(action=action,slot=slot,branch=branch,revision=s['revision'],expected_tier=s['equipment'].get(slot,{}).get('tier'));body.update(extra);return self.a.action(self.uid,body)
 def test_uniform_price_for_all_common_slots_and_server_catalog(self):
  import ast
  original=Path(__file__).resolve().parents[3]/'apps/bot/tourwork/legacy_world_forge.py'
  tree=ast.parse(original.read_text());prices=next(ast.literal_eval(n.value) for n in tree.body if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='COMMON_GOLD_PRICES' for t in n.targets))
  self.assertEqual(prices,CFG['COMMON_GOLD_PRICES']);self.assertTrue(all(v==1000 for v in prices.values()))
  for item in self.s()['items']:
   if item['slot'] in CFG['BASE_SLOTS']:self.assertEqual(item['price'],1000)
  for slot in CFG['BASE_SLOTS']:self.act(slot=slot,price=1)
  with self.a.conn() as c:self.assertEqual(c.execute('SELECT wallet_gold FROM players WHERE user_id=?',(self.uid,)).fetchone()[0],10000-1000*len(CFG['BASE_SLOTS']))
 def test_buy_server_price_auto_equips_and_persists(self):
  self.act(price=1);s=self.s();self.assertEqual(s['equipment']['weapon'],dict(branch='atk',tier='commun'))
  with self.a.conn() as c:self.assertEqual(c.execute('SELECT wallet_gold FROM players WHERE user_id=?',(self.uid,)).fetchone()[0],9000)
  self.a=Activity(self.a.path);self.assertEqual(self.s()['equipment'],s['equipment'])
  with self.assertRaises(ValueError):self.act(branch='def')
 def test_upgrade_costs_and_advanced_unlock(self):
  with self.assertRaises(ValueError):self.act('khaz_upgrade','helmet')
  self.act()
  for tier,cost in [('rare',20),('epique',45),('mythique',90),('legendaire',160)]:
   before=self.s()['pouciel'];self.act('khaz_upgrade');self.assertEqual(self.s()['equipment']['weapon']['tier'],tier);self.assertEqual(before-self.s()['pouciel'],cost)
  with self.assertRaises(ValueError):self.act('khaz_upgrade')
  before=self.s()['pouciel'];self.act('khaz_upgrade','helmet');self.assertEqual(before-self.s()['pouciel'],70);self.assertEqual(self.s()['equipment']['helmet']['tier'],'mythique')
 def test_level_tutorial_material_and_branch_guards(self):
  with self.a.conn() as c:c.execute('UPDATE castle_profiles SET xp=0 WHERE user_id=?',(self.uid,))
  self.assertFalse(self.s()['available'])
  with self.assertRaises(ValueError):self.act()
  with self.a.conn() as c:c.execute('UPDATE castle_profiles SET xp=10000 WHERE user_id=?',(self.uid,))
  self.act()
  with self.assertRaises(ValueError):self.act('khaz_upgrade',branch='def')
  with self.assertRaises(ValueError):self.act('khaz_upgrade',expected_tier='mythique')
  with self.a.conn() as c:c.execute('UPDATE legacy_wallet SET pouciel=0 WHERE user_id=?',(self.uid,))
  with self.assertRaises(ValueError):self.act('khaz_upgrade')
  self.assertEqual(self.s()['equipment']['weapon']['tier'],'commun')
  with self.a.conn() as c:c.execute('UPDATE tutorial_progress SET completed=0 WHERE user_id=?',(self.uid,))
  with self.assertRaises(ValueError):self.act(slot='ring')
 def test_concurrent_duplicate_charges_once(self):
  body=dict(action='khaz_buy',slot='weapon',branch='atk',revision=self.s()['revision'])
  def invoke(_):
   try:self.a.action(self.uid,body);return True
   except ValueError:return False
  with ThreadPoolExecutor(max_workers=2) as p:self.assertEqual(sum(p.map(invoke,range(2))),1)
  with self.a.conn() as c:
   self.assertEqual(c.execute('SELECT wallet_gold FROM players WHERE user_id=?',(self.uid,)).fetchone()[0],9000);self.assertEqual(c.execute('SELECT COUNT(*) FROM activity_khaz_receipts').fetchone()[0],1)
 def test_insufficient_gold_atomic_and_invalid_inputs(self):
  with self.a.conn() as c:c.execute('UPDATE players SET wallet_gold=1 WHERE user_id=?',(self.uid,))
  with self.assertRaises(ValueError):self.act()
  self.assertEqual(self.s()['equipment'],{});self.assertEqual(self.s()['revision'],0)
  for body in [dict(branch='bad'),dict(slot='bad'),dict(revision=True),dict(revision=-1)]:
   with self.assertRaises(ValueError):self.act(**body)
 def test_combat_and_game_lock(self):
  with self.a.conn() as c:c.execute('INSERT OR REPLACE INTO activity_play(user_id,payload) VALUES(?,?)',(self.uid,json.dumps(dict(status='active'))))
  self.assertTrue(self.s()['busy'])
  with self.assertRaises(ValueError):self.act()
  with self.a.conn() as c:
   c.execute('DELETE FROM activity_play WHERE user_id=?',(self.uid,));c.execute('UPDATE campaign_progress SET payload=? WHERE user_id=?',(json.dumps(dict(battle=dict(finished=False))),self.uid))
  with self.assertRaises(ValueError):self.a.khaz.action(self.uid,dict(action='khaz_buy',slot='weapon',branch='atk',revision=0))
 def test_arena_and_campaign_use_equipment_on_start(self):
  self.act();s=self.a.snapshot(self.uid,self.name)
  self.a.action(self.uid,dict(action='battle_start',wager=0,revision=s['play']['revision']))
  with self.a.conn() as c:
   payload=json.loads(c.execute('SELECT payload FROM activity_play WHERE user_id=?',(self.uid,)).fetchone()[0]);fighter=payload['battle']['fighters'][0]
  self.assertAlmostEqual(fighter['equipment_atk_pct'],2/6,places=7)
  with self.a.conn() as c:
   c.execute('DELETE FROM activity_play WHERE user_id=?',(self.uid,));c.execute('UPDATE campaign_progress SET quest_index=7,stage=1,accepted_at=0,payload=? WHERE user_id=?',('{}',self.uid))
  q=self.a.snapshot(self.uid,self.name)['campaign'];self.a.action(self.uid,dict(action='campaign_battle',key='start',quest_id=q['quest']['id'],revision=q['revision']))
  with self.a.conn() as c:fighter=json.loads(c.execute('SELECT payload FROM campaign_progress WHERE user_id=?',(self.uid,)).fetchone()[0])['battle']['fighters'][0]
  self.assertAlmostEqual(fighter['equipment_atk_pct'],2/6,places=7)
 def test_exact_set_bonuses_without_hp(self):
  for branch in ('atk','def','speed'):
   for tier,target in [('commun',2),('rare',4),('epique',6),('mythique',8),('legendaire',10)]:
    slots=CFG['SLOTS'] if tier in ('mythique','legendaire') else CFG['BASE_SLOTS'];b=bonuses_for({s:dict(branch=branch,tier=tier) for s in slots});self.assertAlmostEqual(b['equipment_'+branch+'_pct'],target);self.assertNotIn('equipment_hp_pct',b)
if __name__=='__main__':unittest.main()
