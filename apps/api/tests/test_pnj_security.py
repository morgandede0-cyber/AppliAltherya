"""Adversarial regressions for Popie, Panda and Smogo (temporary SQLite)."""
import json,time,unittest
from concurrent.futures import ThreadPoolExecutor
from unittest.mock import patch
import test_popie as popie
from smogo import Smogo

class PNJSecurityTests(unittest.TestCase):
 tearDown=popie.PopieTests.tearDown
 make=popie.PopieTests.make
 unlock=popie.PopieTests.unlock
 ready=popie.PopieTests.ready
 state=popie.PopieTests.state
 act=popie.PopieTests.act
 stock=popie.PopieTests.stock
 due=popie.PopieTests.due
 def setUp(self):
  p=patch.object(Smogo,'presence',return_value=dict(available=True,available_until=None));p.start();self.addCleanup(p.stop)
  popie.PopieTests.setUp(self)
 def funds(self):return self.a.economy.get_balance(self.buyer).wallet
 def saved(self):
  with self.a.conn() as c:
   return tuple((table,[tuple(r) for r in c.execute('SELECT * FROM '+table+' WHERE user_id=?',(self.buyer,))]) for table in ('activity_port','activity_popie','activity_smogo','players','resources','castle_profiles'))
 def smogo(self,action,**kw):
  p=self.a.smogo.snapshot(self.buyer);return self.a.action(self.buyer,dict(action='smogo_'+action,revision=p['revision'],**kw))
 def mission(self):self.ready();self.act('port_popie_start','safe');self.due();return self.state()['popie']['mission']
 def test_concurrent_claims_without_receipt_pay_and_finalize_once(self):
  m=self.mission();rev=self.state()['revision'];wallet=self.funds();body=dict(action='port_popie_claim',key=m['id'],revision=rev)
  def run(_):
   try:self.a.action(self.buyer,body);return True
   except ValueError:return False
  with ThreadPoolExecutor(max_workers=4) as pool:results=list(pool.map(run,range(4)))
  self.assertEqual(sum(results),1);self.assertEqual(self.funds(),wallet+8);self.assertIsNone(self.state()['popie']['mission'])
 def test_claim_idempotency_and_foreign_owner(self):
  m=self.mission();wallet=self.funds();rev=self.state()['revision']
  self.unlock();body=dict(action='port_popie_claim',key=m['id'],revision=rev,request_id='audit-popie-claim-0001')
  self.a.action(self.buyer,body);self.a.action(self.buyer,body);self.assertEqual(self.funds(),wallet+8)
  with self.assertRaises(ValueError):self.a.action(self.other,body)
 def test_post_reward_failure_rolls_back_resources_xp_limit_and_receipt(self):
  self.ready();o=self.state()['popie']['orders'][0];before=self.saved();body=dict(action='port_popie_order',key=o['key'],revision=self.state()['revision'],request_id='audit-popie-rollback-0001')
  with patch.object(self.a.transaction_journal,'record',side_effect=RuntimeError('simulated write failure')):
   with self.assertRaises(RuntimeError):self.a.action(self.buyer,body)
  self.assertEqual(before,self.saved())
  self.a.action(self.buyer,body);self.assertTrue(self.state()['popie']['order_done'])
 def test_wallet_cap_does_not_consume_pending_delivery_and_retry_pays_once(self):
  m=self.mission()
  with self.a.conn() as c:c.execute('UPDATE players SET wallet_gold=1000000000 WHERE user_id=?',(self.buyer,))
  before=self.saved()
  with self.assertRaises(ValueError):self.act('port_popie_claim',m['id'])
  self.assertEqual(before,self.saved())
  with self.a.conn() as c:c.execute('UPDATE players SET wallet_gold=10 WHERE user_id=?',(self.buyer,))
  self.act('port_popie_claim',m['id']);self.assertEqual(self.funds(),18)
  with self.assertRaises(ValueError):self.act('port_popie_claim',m['id'])
 def test_exchange_cannot_inject_item_amount_reward_or_negative_quantities(self):
  self.ready();stone=self.stock('Pierre brute');wood=self.stock('Bois de chêne');wallet=self.funds()
  self.act('port_popie_exchange','stone-wood',quantity=-999,give_qty=0,receive_qty=99999,item='Objet d’histoire',gold=99999,xp=99999)
  self.assertEqual(self.stock('Pierre brute'),stone-3);self.assertEqual(self.stock('Bois de chêne'),wood+2);self.assertEqual(self.funds(),wallet)
 def test_invalid_keys_types_and_revisions_never_mutate_private_state(self):
  self.ready()
  for action in ('port_popie_order','port_popie_exchange','port_popie_start','port_popie_claim','port_talk','port_inspect','port_choose','port_battle','port_enter','smogo_answer','smogo_giveup'):
   for key in (None,[],{},True,123,"'; DROP TABLE players;--"):
    before=self.saved()
    with self.assertRaises(ValueError):self.a.action(self.buyer,dict(action=action,key=key,revision=self.state()['revision']))
    self.assertEqual(before,self.saved())
  for revision in (True,False,1.5,'0',None,-1,999999):
   before=self.saved()
   with self.assertRaises(ValueError):self.a.action(self.buyer,dict(action='port_popie_start',key='safe',revision=revision))
   self.assertEqual(before,self.saved())
 def test_account_owner_and_reused_receipt_cannot_change_action(self):
  self.ready();before=self.saved()
  for action,key in [('port_popie_start','safe'),('port_talk','captain'),('smogo_start','')]:
   with self.assertRaises(ValueError):self.a.action(self.buyer,dict(action=action,key=key,wager=10,revision=0,save_owner='another-account'))
  self.assertEqual(before,self.saved())
  body=dict(action='port_popie_exchange',key='stone-wood',revision=self.state()['revision'],request_id='audit-reuse-receipt-0001');self.a.action(self.buyer,body);after=self.saved()
  with self.assertRaises(ValueError):self.a.action(self.buyer,{**body,'key':'wood-meat','revision':self.state()['revision']})
  self.assertEqual(after,self.saved())
 def test_panda_cannot_authenticate_a_forged_completed_investigation(self):
  self.unlock();self.act('port_enter','capitainerie');self.act('port_talk','captain',phase=6,complete=True,won=True,clues=['crate','register','seal','boat','pouch','quay_crate'])
  self.assertEqual(self.state()['phase'],1);self.assertFalse(self.state()['complete']);self.assertEqual(self.state()['clues'],[])
  self.act('port_talk','captain',phase=6,won=True);self.assertEqual(self.state()['phase'],1)
 def test_smogo_cannot_start_when_absent_by_forging_client_clock_or_availability(self):
  before=self.funds()
  with patch.object(self.a.smogo,'presence',return_value=dict(available=False,available_until=None)):
   with self.assertRaisesRegex(ValueError,'introuvable'):self.smogo('start',wager=10,available=True,server_now=0,expires_at=9999999999)
  self.assertEqual(self.funds(),before);self.assertIsNone(self.a.smogo.snapshot(self.buyer)['round'])
 def test_smogo_payout_write_failure_rolls_back_and_can_be_retried_once(self):
  self.smogo('start',wager=10);s=self.a.smogo.snapshot(self.buyer)
  with self.a.conn() as c:r=json.loads(c.execute('SELECT payload FROM activity_smogo WHERE user_id=?',(self.buyer,)).fetchone()[0])['round']
  body=dict(action='smogo_answer',revision=s['revision'],key=r['id'],answer=r['answers'][0],request_id='audit-smogo-rollback-0001');before=self.saved()
  with patch.object(self.a.transaction_journal,'record',side_effect=RuntimeError('simulated write failure')):
   with self.assertRaises(RuntimeError):self.a.action(self.buyer,body)
  self.assertEqual(before,self.saved());wallet=self.funds();self.a.action(self.buyer,body);self.a.action(self.buyer,body);self.assertEqual(self.funds(),wallet+20)
 def test_player_lock_blocks_all_three_npcs(self):
  self.ready()
  with self.a.conn() as c:c.execute('INSERT INTO activity_player_locks(user_id,message,until_at) VALUES(?,?,?)',(self.buyer,'Audit',time.time()+3600))
  before=self.saved()
  for action,key in [('port_popie_start','safe'),('port_talk','captain'),('smogo_start','')]:
   with self.assertRaisesRegex(ValueError,'verrouillé'):self.a.action(self.buyer,dict(action=action,key=key,revision=self.state()['revision'],wager=10))
  self.assertEqual(before,self.saved())
