import json,time,unittest
from concurrent.futures import ThreadPoolExecutor
from unittest.mock import patch
import test_trading as trade
from activity import Activity
from smogo import normalise,RIDDLES,Smogo
PRESENCE=Smogo.presence

class SmogoTests(unittest.TestCase):
 def setUp(self):
  self.presence_patch=patch.object(Smogo,'presence',return_value=dict(available=True,available_until=None))
  self.presence_patch.start();self.addCleanup(self.presence_patch.stop)
  trade.TradeTests.setUp(self)
 tearDown=trade.TradeTests.tearDown
 make=trade.TradeTests.make
 def state(self,uid=None):return self.a.snapshot(uid or self.buyer,'Test')['smogo']
 def act(self,action,uid=None,**extra):
  uid=uid or self.buyer;s=self.state(uid)
  return self.a.action(uid,dict(action='smogo_'+action,revision=s['revision'],**extra))
 def start(self,uid=None,wager=10):self.act('start',uid,wager=wager);return self.state(uid)['round']
 def private(self,uid=None):
  with self.a.conn() as c:return json.loads(c.execute('SELECT payload FROM activity_smogo WHERE user_id=?',(uid or self.buyer,)).fetchone()[0])['round']
 def wallet(self,uid=None):return self.a.economy.get_balance(uid or self.buyer).wallet
 def answer(self,text=None,**extra):
  r=self.private();return self.act('answer',key=r['id'],answer=text if text is not None else r['answers'][0],**extra)
 def expire(self):
  with self.a.conn() as c:
   p=json.loads(c.execute('SELECT payload FROM activity_smogo WHERE user_id=?',(self.buyer,)).fetchone()[0]);p['round']['expires_at']=time.time()-1;c.execute('UPDATE activity_smogo SET payload=? WHERE user_id=?',(json.dumps(p),self.buyer))
 def test_correct_pays_double_stake_once_and_logs_both_moves(self):
  before=self.wallet();xp=self.a.castle.profile(self.buyer)['xp'];r=self.start();self.assertEqual(self.wallet(),before-10)
  self.answer();s=self.state()['round'];self.assertTrue(s['won']);self.assertEqual(s['payout'],20);self.assertEqual(s['net_gold'],10);self.assertEqual(self.wallet(),before+10);self.assertEqual(self.a.castle.profile(self.buyer)['xp'],xp)
  with self.assertRaises(ValueError):self.act('answer',key=r['id'],answer=self.private()['answers'][0])
  with self.a.conn() as c:self.assertEqual([x[0] for x in c.execute("SELECT gold_delta FROM activity_transaction_journal WHERE user_id=? AND action LIKE 'smogo_%' ORDER BY created_at",(self.buyer,))],[-10,20])
 def test_wrong_loses_only_escrow_and_reveals_solution_afterwards(self):
  before=self.wallet();self.start();self.answer('ceci est faux',won=True,payout=99999);r=self.state()['round'];self.assertFalse(r['won']);self.assertEqual(r['payout'],0);self.assertEqual(self.wallet(),before-10);self.assertIn('solution',r)
 def test_private_answers_never_sent_while_active(self):
  self.start();r=self.state()['round'];self.assertEqual(r['status'],'active')
  for k in ('answers','solution','explanation','won','payout'):self.assertNotIn(k,r)
 def test_reopen_restart_same_question_stake_id_deadline_and_count(self):
  self.start();before=self.state();wallet=self.wallet();self.a=Activity(self.path)
  self.assertEqual(self.state(),before);self.assertEqual(self.wallet(),wallet)
  with self.assertRaises(ValueError):self.act('start',wager=25)
  self.assertEqual(self.state(),before);self.assertEqual(self.wallet(),wallet)
 def test_different_players_have_different_questions_even_on_collision(self):
  with patch('smogo.secrets.choice',side_effect=lambda choices:choices[0]):
   one=self.start();two=self.start(self.other)
  self.assertNotEqual(one['question'],two['question']);self.assertNotEqual(one['id'],two['id'])
 def test_global_registry_preserves_uniqueness_beyond_static_bank(self):
  with self.a.conn() as c:
   seen=[];questions=[]
   for _ in range(100):
    q=self.a.smogo.question(c,seen);questions.append(q[1]);seen=(seen+[q[0]])[-20:]
   self.assertEqual(len(set(questions)),100)
 def test_other_player_cannot_answer_my_round(self):
  r=self.start();other=self.wallet(self.other)
  with self.assertRaises(ValueError):self.act('answer',self.other,key=r['id'],answer=self.private()['answers'][0])
  self.assertEqual(self.wallet(self.other),other);self.assertEqual(self.state()['round']['status'],'active')
 def test_invalid_stakes_and_no_overdraft(self):
  for n in (0,-1,501,1.5,True,'10',None):
   with self.assertRaises(ValueError):self.act('start',wager=n)
  with self.a.conn() as c:c.execute('UPDATE players SET wallet_gold=2 WHERE user_id=?',(self.buyer,))
  with self.assertRaises(ValueError):self.act('start',wager=10)
  self.assertEqual(self.wallet(),2);self.assertIsNone(self.state()['round']);self.assertEqual(self.state()['remaining'],1)
 def test_empty_answer_does_not_consume_single_try(self):
  self.start()
  for bad in ('','  ',123,['echo']):
   with self.assertRaises(ValueError):self.answer(bad)
  self.assertEqual(self.state()['round']['status'],'active');self.answer();self.assertTrue(self.state()['round']['won'])
 def test_timeout_is_a_loss_after_reconnect_even_if_answer_is_correct(self):
  before=self.wallet();self.start();self.expire();r=self.state()['round'];self.assertEqual(r['reason'],'timeout');self.a=Activity(self.path);self.answer();self.assertFalse(self.state()['round']['won']);self.assertEqual(self.wallet(),before-10)
 def test_no_early_timeout_or_client_timer_override(self):
  r=self.start()
  with self.assertRaises(ValueError):self.act('timeout',key=r['id'],expires_at=0,server_now=999999999999)
  self.assertEqual(self.state()['round']['status'],'active')
 def test_abandon_never_refunds_and_lifetime_limit_persists(self):
  before=self.wallet()
  r=self.start();self.act('giveup',key=r['id'])
  self.assertEqual(self.wallet(),before-10);self.a=Activity(self.path);self.assertEqual(self.state()['remaining'],0)
  with self.assertRaises(ValueError):self.act('start',wager=10)
 def test_midnight_does_not_reroll_running_question(self):
  self.start();round=self.state()['round']
  with patch('smogo.today',return_value='2099-01-01'):
   self.assertEqual(self.state()['round'],round)
   with self.assertRaises(ValueError):self.act('start',wager=10)
   self.answer();self.assertEqual(self.state()['remaining'],0)
   self.assertFalse(self.state()['available'])
   with self.assertRaises(ValueError):self.start()
 def test_replay_request_and_simultaneous_answers_do_not_double_credit(self):
  before=self.wallet();r=self.start();body=dict(action='smogo_answer',revision=self.state()['revision'],key=r['id'],answer=self.private()['answers'][0],request_id='smogo-replay-answer-0001')
  def run(_):return self.a.action(self.buyer,body)
  with ThreadPoolExecutor(max_workers=2) as pool:list(pool.map(run,range(2)))
  self.assertEqual(self.wallet(),before+10)
 def test_simultaneous_start_only_debits_once(self):
  before=self.wallet();body=dict(action='smogo_start',revision=self.state()['revision'],wager=10)
  def run(_):
   try:self.a.action(self.buyer,body);return True
   except ValueError:return False
  with ThreadPoolExecutor(max_workers=2) as pool:result=list(pool.map(run,range(2)))
  self.assertEqual(sum(result),1);self.assertEqual(self.wallet(),before-10);self.assertEqual(self.state()['remaining'],0)
 def test_failure_to_reserve_unique_question_rolls_back_debit(self):
  before=self.wallet()
  with patch.object(self.a.smogo,'question',side_effect=ValueError('Réessayez')):
   with self.assertRaises(ValueError):self.act('start',wager=10)
  self.assertEqual(self.wallet(),before);self.assertEqual(self.state()['remaining'],1)
 def test_maintenance_and_tutorial_gate(self):
  with self.a.conn() as c:c.execute("INSERT INTO activity_maintenance VALUES('alley','Fermé',0,'admin',?)",(time.time(),))
  with self.assertRaisesRegex(ValueError,'Maintenance'):self.act('start',wager=10)
  with self.a.conn() as c:c.execute('DELETE FROM activity_maintenance');c.execute('UPDATE activity_tutorial_revision SET finished=0 WHERE user_id=?',(self.buyer,))
  with self.assertRaises(ValueError):self.act('start',wager=10)
 def test_normalisation_accepts_accents_articles_case_and_ligatures(self):
  self.assertEqual(normalise('Un ÉCHO !'),normalise('écho'));self.assertEqual(normalise('Le nœud'),normalise('noeud'));self.assertEqual(normalise("L’éponge"),normalise('éponge'))

 def test_second_discord_session_resumes_canonical_players_round(self):
  self.start();before=self.state();wallet=self.wallet()
  (guest,_),token=self.a.session('');self.a.snapshot(guest,'Nouveau navigateur')
  self.a.bind_discord(guest,dict(id='123456789012345679',username='Autre appareil',global_name='Acheteur',avatar=None,discriminator='0'),token)
  restored=self.a.session(token)[0][0]
  self.assertEqual(restored,self.buyer);self.assertEqual(self.state(restored),before);self.assertEqual(self.wallet(restored),wallet)

 def test_negative_number_is_not_accepted_as_its_positive_value(self):
  with patch.object(self.a.smogo,'question',return_value=('number','Combien font deux plus trois ? Répondez en chiffres.',('5',),'2 + 3 = 5.')):
   self.start();self.answer('-5');self.assertFalse(self.state()['round']['won'])
   r=self.start(self.other);self.act('answer',self.other,key=r['id'],answer='005');self.assertTrue(self.state(self.other)['round']['won'])

 def test_library_has_one_hundred_unique_valid_questions(self):
  self.assertEqual(len(RIDDLES),100)
  self.assertEqual(len({q[0] for q in RIDDLES}),100)
  self.assertEqual(len({normalise(q[1]) for q in RIDDLES}),100)
  for key,question,answers,explanation in RIDDLES:
   self.assertTrue(key and question and explanation and answers)
   for answer in answers:self.assertTrue(normalise(answer))
 def test_absence_blocks_start_without_debit_or_question_change(self):
  before=self.wallet()
  with patch.object(self.a.smogo,'presence',return_value=dict(available=False,available_until=None)):
   self.assertFalse(self.state()['available'])
   with self.assertRaisesRegex(ValueError,'introuvable'):self.start()
  self.assertEqual(self.wallet(),before);self.assertIsNone(self.state()['round'])
 def test_paid_round_survives_disappearance_and_can_be_answered(self):
  before=self.wallet();r=self.start()
  with patch.object(self.a.smogo,'presence',return_value=dict(available=False,available_until=None)):
   self.assertEqual(self.state()['round'],r)
   self.answer();self.assertTrue(self.state()['round']['won'])
   with self.assertRaisesRegex(ValueError,'déjà participé'):self.start()
  self.assertEqual(self.wallet(),before+10)
 def test_visits_are_shared_persisted_and_enforced_at_boundaries(self):
  with self.a.conn() as c:
   PRESENCE(self.a.smogo,c)
   day,raw=c.execute('SELECT day,windows FROM activity_smogo_visits').fetchone();windows=json.loads(raw)
   self.assertEqual(len(windows),3)
   for i,(start,end) in enumerate(windows):
    self.assertEqual(end-start,3600)
    if i:self.assertGreaterEqual(start,windows[i-1][1])
    with patch('smogo.time.time',return_value=start):self.assertTrue(PRESENCE(self.a.smogo,c)['available'])
    with patch('smogo.time.time',return_value=end):self.assertFalse(PRESENCE(self.a.smogo,c)['available'])
  self.a=Activity(self.path)
  with self.a.conn() as c:
   PRESENCE(self.a.smogo,c)
   self.assertEqual(c.execute('SELECT windows FROM activity_smogo_visits WHERE day=?',(day,)).fetchone()[0],raw)

 def test_500_gold_accepted_and_lifetime_completion_survives_restart_and_midnight(self):
  before=self.wallet();self.start(wager=500);self.answer()
  self.assertEqual(self.wallet(),before+500)
  self.a=Activity(self.path)
  with patch('smogo.today',return_value='2099-01-01'):
   s=self.state();self.assertTrue(s['completed']);self.assertFalse(s['available']);self.assertEqual(s['remaining'],0)
   self.assertEqual(s['max_wager'],500);self.assertIsNone(s['reset_at'])
   with self.assertRaisesRegex(ValueError,'déjà participé'):self.start()
  self.assertEqual(self.state(self.other)['remaining'],1)
 def test_expired_round_disappears_and_cannot_be_replaced(self):
  self.start();self.expire();s=self.state()
  self.assertTrue(s['completed']);self.assertFalse(s['available'])
  with self.assertRaisesRegex(ValueError,'déjà participé'):self.start()
 def test_legacy_participation_counts_even_when_daily_counter_is_old(self):
  self.start();self.answer()
  with self.a.conn() as c:c.execute("UPDATE activity_smogo SET day='2000-01-01',attempts=0 WHERE user_id=?",(self.buyer,))
  self.assertTrue(self.state()['completed'])
  with self.assertRaises(ValueError):self.start()
