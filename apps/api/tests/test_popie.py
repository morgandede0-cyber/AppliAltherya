import json,time,unittest
from concurrent.futures import ThreadPoolExecutor
from unittest.mock import patch
import test_port as port_tests
from activity import Activity

class PopieTests(unittest.TestCase):
 setUp=port_tests.PortTests.setUp
 tearDown=port_tests.PortTests.tearDown
 make=port_tests.PortTests.make
 unlock=port_tests.PortTests.unlock
 def state(self):return self.a.snapshot(self.buyer,'Test')['port']
 def act(self,action,key='',**extra):
  return self.a.action(self.buyer,dict(action=action,key=key,revision=self.state().get('revision',0),**extra))
 def ready(self):
  self.unlock();self.act('port_enter','popie')
  with self.a.conn() as c:
   for item in ('Pierre brute','Bois de chêne','Viande de sanglier'):c.execute('INSERT OR REPLACE INTO resources VALUES(?,?,?)',(self.buyer,item,100))
 def stock(self,item):
  with self.a.conn() as c:
   r=c.execute('SELECT quantity FROM resources WHERE user_id=? AND resource_name=?',(self.buyer,item)).fetchone();return r[0] if r else 0
 def due(self):
  with self.a.conn() as c:
   p=self.a.port.popie.read(c,self.buyer);p['mission']['ready_at']=time.time()-1;c.execute('UPDATE activity_popie SET payload=? WHERE user_id=?',(json.dumps(p),self.buyer))
 def test_gate_scene_and_revision(self):
  with self.assertRaises(ValueError):self.act('port_popie_order','anything')
  self.unlock()
  with self.assertRaises(ValueError):self.act('port_popie_exchange','stone-wood')
  self.act('port_enter','popie');rev=self.state()['revision']
  self.act('port_enter','entrepots')
  with self.assertRaises(ValueError):self.a.action(self.buyer,dict(action='port_popie_exchange',key='stone-wood',revision=rev))
 def test_order_server_values_one_per_day_replay_and_restart(self):
  self.ready();o=self.state()['popie']['orders'][0];before=self.a.economy.get_balance(self.buyer).wallet;stock=self.stock(o['item']);rev=self.state()['revision']
  body=dict(action='port_popie_order',key=o['key'],revision=rev,gold=999999,xp=999999,quantity=-1,request_id='popie-order-replay-0001')
  self.a.action(self.buyer,body);self.a.action(self.buyer,body)
  self.assertEqual(self.a.economy.get_balance(self.buyer).wallet,before+o['gold']);self.assertEqual(self.stock(o['item']),stock-o['quantity'])
  self.a=Activity(self.path);self.assertTrue(self.state()['popie']['order_done'])
  with self.assertRaises(ValueError):self.act('port_popie_order',self.state()['popie']['orders'][1]['key'])
 def test_insufficient_stock_rolls_back_and_stale_day_rejected(self):
  self.ready();o=self.state()['popie']['orders'][0]
  with self.a.conn() as c:c.execute('UPDATE resources SET quantity=0 WHERE user_id=?',(self.buyer,))
  before=self.state();balance=self.a.economy.get_balance(self.buyer)
  with self.assertRaises(ValueError):self.act('port_popie_order',o['key'])
  self.assertEqual(before,self.state());self.assertEqual(balance,self.a.economy.get_balance(self.buyer))
  with self.assertRaises(ValueError):self.act('port_popie_order','2000-01-01:0')
 def test_exchanges_limited_lossy_and_no_story_items(self):
  self.ready();before=sum(self.stock(x) for x in ('Pierre brute','Bois de chêne','Viande de sanglier'))
  for key in ('stone-wood','wood-meat','meat-stone'):self.act('port_popie_exchange',key)
  self.assertEqual(sum(self.stock(x) for x in ('Pierre brute','Bois de chêne','Viande de sanglier')),before-3)
  with self.assertRaises(ValueError):self.act('port_popie_exchange','stone-wood')
  with self.assertRaises(ValueError):self.act('port_popie_exchange',"Objet d’histoire")
 def test_mission_escrow_private_roll_early_claim_once_and_restart(self):
  self.ready();before=self.stock('Bois de chêne');self.act('port_popie_start','safe');m=self.state()['popie']['mission'];self.assertNotIn('success',m);self.assertEqual(self.stock('Bois de chêne'),before-2)
  with self.assertRaises(ValueError):self.act('port_popie_claim',m['id'],ready_at=0,success=True)
  with self.assertRaises(ValueError):self.act('port_popie_start','risky')
  self.a=Activity(self.path);self.assertEqual(self.state()['popie']['mission']['id'],m['id']);self.due();before=self.a.economy.get_balance(self.buyer).wallet
  self.act('port_popie_claim',m['id']);self.assertEqual(self.a.economy.get_balance(self.buyer).wallet,before+8)
  with self.assertRaises(ValueError):self.act('port_popie_claim',m['id'])
  with self.assertRaises(ValueError):self.act('port_popie_start','safe')
 def test_risky_failure_cannot_be_forged(self):
  self.ready()
  with patch('popie.secrets.randbelow',return_value=99):self.act('port_popie_start','risky')
  self.due();m=self.state()['popie']['mission'];before=self.a.economy.get_balance(self.buyer)
  self.act('port_popie_claim',m['id'],success=True,gold=9999);self.assertEqual(before,self.a.economy.get_balance(self.buyer));self.assertIn('intercepté',self.state()['popie']['last_result'])
 def test_maintenance_applies_to_services(self):
  self.ready()
  with self.a.conn() as c:c.execute("INSERT INTO activity_maintenance VALUES('port','Fermé',0,'admin',?)",(time.time(),))
  with self.assertRaisesRegex(ValueError,'Maintenance'):self.act('port_popie_start','safe')
 def test_daily_reset_does_not_destroy_pending_mission(self):
  self.ready();self.act('port_popie_start','safe');m=self.state()['popie']['mission']
  with patch('popie.today',return_value='2099-01-01'):
   self.assertFalse(self.state()['popie']['mission_done'])
   with self.assertRaises(ValueError):self.act('port_popie_start','safe')
   self.due();self.act('port_popie_claim',m['id']);self.act('port_popie_start','safe')
 def test_concurrent_orders_pay_only_one(self):
  self.ready();s=self.state();o=s['popie']['orders'][0];before=self.stock(o['item'])
  body=dict(action='port_popie_order',key=o['key'],revision=s['revision'])
  def run(_):
   try:self.a.action(self.buyer,body);return True
   except ValueError:return False
  with ThreadPoolExecutor(max_workers=2) as pool:results=list(pool.map(run,range(2)))
  self.assertEqual(sum(results),1);self.assertEqual(self.stock(o['item']),before-o['quantity'])
 def test_reward_cap_rolls_back_materials_and_limit(self):
  self.ready();o=self.state()['popie']['orders'][0];before=self.stock(o['item'])
  with self.a.conn() as c:c.execute('UPDATE players SET wallet_gold=1000000000 WHERE user_id=?',(self.buyer,))
  with self.assertRaises(ValueError):self.act('port_popie_order',o['key'])
  self.assertEqual(self.stock(o['item']),before);self.assertFalse(self.state()['popie']['order_done'])
