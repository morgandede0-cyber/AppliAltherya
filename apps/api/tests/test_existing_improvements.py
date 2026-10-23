import json,os,subprocess,sys,unittest
from pathlib import Path
from unittest.mock import patch
import test_trading as trade
import test_ashkar as tower
from activity import Activity
from khaz import bonuses_for

class CommerceJournalTests(unittest.TestCase):
 setUp=trade.TradeTests.setUp
 tearDown=trade.TradeTests.tearDown
 make=trade.TradeTests.make
 offer=trade.TradeTests.offer
 buy=trade.TradeTests.buy
 stock=trade.TradeTests.stock
 balance=trade.TradeTests.balance
 def letters(self,uid):return self.a.mailbox.listing(uid,0)['entries']
 def count(self,table,where='1=1',params=()):
  with self.a.conn() as c:return c.execute('SELECT COUNT(*) FROM '+table+' WHERE '+where,params).fetchone()[0]
 def test_sale_history_and_informative_mail_never_pay_twice(self):
  key=self.offer();body=dict(action='trade_buy',key=key,price=50,request_id='sale-safe-unique-0001');self.a.action(self.buyer,body);wallet=self.balance(self.seller)
  self.assertEqual(self.a.trading.history(self.seller)['entries'][0]['status'],'sold');self.assertEqual(self.a.trading.history(self.buyer)['entries'][0]['buyer_name'],'Acheteur');self.assertEqual(self.a.trading.history(self.other)['total'],0)
  letter=self.letters(self.seller)[0];self.assertFalse(letter['has_reward']);self.assertIn('50 Gold',letter['body']);self.assertEqual(letter['sender'],'Comptoir des joueurs')
  self.a.action(self.buyer,body);self.a=Activity(self.path);self.assertEqual(len(self.letters(self.seller)),1);self.assertEqual(self.balance(self.seller),wallet)
  with self.assertRaises(ValueError):self.a.action(self.seller,dict(action='mail_claim',key=letter['id']))
 def test_expiration_mail_and_return_are_atomic_and_unique(self):
  key=self.offer()
  with self.a.conn() as c:c.execute('UPDATE activity_trade_offers SET expires_at=0 WHERE id=?',(key,))
  self.a.trading.expire();self.a.trading.expire();self.assertEqual(self.stock(self.seller),100);self.assertEqual(len(self.letters(self.seller)),1);self.assertIn('rendus',self.letters(self.seller)[0]['body']);self.assertEqual(self.count('activity_transaction_journal',"action='trade_expired'"),1)
 def test_failed_mail_rolls_back_entire_sale_then_retry_succeeds(self):
  key=self.offer();before=(self.stock(self.buyer),self.balance(self.buyer),self.balance(self.seller))
  with patch.object(self.a.mailbox,'send',side_effect=RuntimeError('disk fault')):
   with self.assertRaises(RuntimeError):self.buy(key)
  self.assertEqual((self.stock(self.buyer),self.balance(self.buyer),self.balance(self.seller)),before);self.assertEqual(self.a.trading.listing(self.seller,'mine')['total'],1);self.assertEqual(self.letters(self.seller),[])
  self.buy(key);self.assertEqual(len(self.letters(self.seller)),1)
 def test_failed_expiry_keeps_escrow_until_safe_retry(self):
  key=self.offer()
  with self.a.conn() as c:c.execute('UPDATE activity_trade_offers SET expires_at=0 WHERE id=?',(key,))
  with patch.object(self.a.mailbox,'send',side_effect=RuntimeError('disk fault')):
   with self.assertRaises(RuntimeError):self.a.trading.expire()
  self.assertEqual(self.stock(self.seller),90)
  with self.a.conn() as c:self.assertEqual(c.execute('SELECT status FROM activity_trade_offers WHERE id=?',(key,)).fetchone()[0],'active')
  self.a.trading.expire();self.assertEqual(self.stock(self.seller),100)
 def test_journal_tracks_both_parties_and_reference_once(self):
  key=self.offer();rid='traceable-purchase-0001';self.buy(key,request_id=rid);self.buy(key,request_id=rid)
  rows=self.a.transaction_journal.listing(dict(query=rid))['entries'];self.assertEqual(len(rows),2);self.assertEqual(sorted(r['gold_delta'] for r in rows),[-50,50]);self.assertEqual(sum(r['gold_delta'] for r in rows),0)
  self.assertEqual({r['name'] for r in rows},{'Panda du serveur','Acheteur'})
 def test_bank_transfer_is_not_reported_as_creation_of_gold(self):
  self.a.action(self.seller,dict(action='deposit',amount=100,request_id='bank-transfer-audit-0001'))
  r=self.a.transaction_journal.listing(dict(query='bank-transfer-audit-0001'))['entries'][0];self.assertEqual(r['gold_delta'],0);self.assertEqual(r['after']['bank']-r['before']['bank'],100)
 def test_admin_search_requires_server_permission_and_validates_filters(self):
  with self.assertRaises(PermissionError):self.a.admin.handle(self.buyer,dict(action='transactions'))
  with patch.dict(os.environ,{'ACTIVITY_ADMIN_IDS':'123456789012345678'}):
   self.assertIn('entries',self.a.admin.handle(self.seller,dict(action='transactions',player='123456789012345679')))
   with self.assertRaises(ValueError):self.a.admin.handle(self.seller,dict(action='transactions',min_gain=-1))
   with self.assertRaises(ValueError):self.a.admin.handle(self.seller,dict(action='transactions',player="1 OR 1=1"))
  self.assertEqual(self.a.transaction_journal.listing(dict(query="' OR 1=1 --"))['total'],0)
 def test_large_gains_are_review_flags_not_automatic_sanctions(self):
  key=self.offer(price=600);self.buy(key,price=600);data=self.a.transaction_journal.listing(dict(min_gain=500));self.assertEqual(data['total'],1);self.assertTrue(data['entries'][0]['review']);self.assertEqual(self.balance(self.seller),1600)
 def child(self,body,phase):
  script='''import json,os,sys
sys.path.insert(0,sys.argv[1]);from activity import Activity
a=Activity(sys.argv[2]);uid=int(sys.argv[3]);body=json.loads(sys.argv[4]);original=a.transaction_journal.record
def record(c,actor,target,action,reference,before):
 if action=='trade_buy' and sys.argv[5]=='before':os._exit(77)
 return original(c,actor,target,action,reference,before)
a.transaction_journal.record=record
a.action(uid,body)
os._exit(78)
'''
  return subprocess.run([sys.executable,'-c',script,str(Path(__file__).parents[1]),str(self.path),str(self.buyer),json.dumps(body),phase],capture_output=True,timeout=30)
 def test_process_killed_before_commit_loses_no_gold_objects_or_receipts(self):
  key=self.offer();rid='process-crash-before-0001';body=dict(action='trade_buy',key=key,price=50,request_id=rid);self.assertEqual(self.child(body,'before').returncode,77)
  self.a=Activity(self.path);self.assertEqual(self.stock(self.seller),90);self.assertEqual(self.stock(self.buyer),0);self.assertEqual(self.balance(self.buyer),1000);self.assertEqual(self.balance(self.seller),1000);self.assertEqual(self.letters(self.seller),[]);self.assertEqual(self.count('activity_operations','request_id=?',(rid,)),0)
  self.a.action(self.buyer,body);self.assertEqual(self.stock(self.buyer),10)
 def test_process_killed_after_commit_can_retry_lost_response_exactly_once(self):
  key=self.offer();rid='process-crash-after-00001';body=dict(action='trade_buy',key=key,price=50,request_id=rid);self.assertEqual(self.child(body,'after').returncode,78)
  self.a=Activity(self.path);wallet=self.balance(self.buyer);self.a.action(self.buyer,body);self.assertEqual(self.balance(self.buyer),wallet);self.assertEqual(self.stock(self.buyer),10);self.assertEqual(len(self.letters(self.seller)),1);self.assertEqual(self.count('activity_operations','request_id=?',(rid,)),1)
 def test_finalized_expedition_has_one_origin_and_survives_reconnect(self):
  self.a.action(self.buyer,dict(action='start',key='elarwyn_foraging',tool='hands'))
  with self.a.conn() as c:c.execute('UPDATE expedition_runs SET ends_at=0 WHERE user_id=?',(self.buyer,))
  self.a.snapshot(self.buyer,'Acheteur');self.a=Activity(self.path);self.a.snapshot(self.buyer,'Acheteur')
  rows=self.a.transaction_journal.listing(dict(query='expedition_finalize'))['entries'];self.assertEqual(len(rows),1);self.assertGreater(rows[0]['after']['xp'],rows[0]['before']['xp'])

class CombatReviewTests(unittest.TestCase):
 setUp=tower.AshkarTests.setUp
 tearDown=tower.AshkarTests.tearDown
 s=tower.AshkarTests.s
 act=tower.AshkarTests.act
 weaken=tower.AshkarTests.weaken
 def test_tower_archive_keeps_victory_and_later_defeat_without_rewards(self):
  self.act();self.weaken();self.act('ashkar_step',key='light');first=self.a.combat_archive.listing(self.uid)['entries'][0];self.assertTrue(first['report']['won']);self.assertTrue(first['report']['events']);self.assertEqual(first['source'],'tower')
  self.act();self.act('ashkar_step',key='abandon');data=self.a.combat_archive.listing(self.uid);self.assertEqual(data['total'],2);self.assertFalse(data['entries'][0]['report']['won']);self.assertEqual(self.a.combat_archive.listing(self.uid+1)['total'],0)
  wallet=self.a.economy.get_balance(self.uid).wallet;self.a.combat_archive.listing(self.uid);self.assertEqual(self.a.economy.get_balance(self.uid).wallet,wallet)
 def test_archive_filter_rejects_injection_and_negative_page(self):
  with self.assertRaises(ValueError):self.a.combat_archive.listing(self.uid,-1)
  with self.assertRaises(ValueError):self.a.combat_archive.listing(self.uid,0,"' UNION SELECT")
 def test_armor_preview_matches_exact_equipment_bonus_calculation(self):
  k=self.a.khaz.snapshot(self.uid);item=next(i for i in k['items'] if i['slot']=='weapon' and i['branch']=='atk');self.assertEqual(item['buy_bonuses'],bonuses_for({'weapon':dict(branch='atk',tier='commun')}));self.assertEqual(item['price'],1000)

class DailyLevelTests(unittest.TestCase):
 def setUp(self):
  import test_daily_random
  test_daily_random.RandomDailyTests.setUp(self)
 def tearDown(self):self.tmp.cleanup()
 def test_level_scales_allowed_objectives_without_forge_or_locked_zones(self):
  with self.a.conn() as c:c.execute('UPDATE castle_profiles SET xp=10000 WHERE user_id=?',(self.uid,))
  found=False
  from datetime import date,timedelta
  for n in range(8):
   with patch.object(self.a.castle,'_today',return_value=(date(2027,1,1)+timedelta(days=n)).isoformat()):
    plan,reward=self.a.castle.quest_config(self.uid)
    if 'combat' in plan:found=True;self.assertEqual(plan['combat'][1],2)
    if 'tavern_game' in plan:self.assertEqual(plan['tavern_game'][1],2)
    if 'expedition' in plan:self.assertEqual(plan['expedition'][1],1)
    self.assertEqual(reward['gold'],30);self.assertEqual(reward['xp'],75)
  self.assertTrue(found)
 def test_plan_does_not_change_when_level_changes_during_day(self):
  with patch.object(self.a.castle,'_today',return_value='2027-02-01'):
   before=self.a.castle.quest_config(self.uid)
   with self.a.conn() as c:c.execute('UPDATE castle_profiles SET xp=100000 WHERE user_id=?',(self.uid,))
   self.assertEqual(self.a.castle.quest_config(self.uid),before)
