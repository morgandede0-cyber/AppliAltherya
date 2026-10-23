import json,time,unittest
import test_trading as trade
from activity import Activity
from campaign import QUESTS,effective_quest
from port import port_quest,WAREHOUSE,QUAY

class PortTests(unittest.TestCase):
 setUp=trade.TradeTests.setUp
 tearDown=trade.TradeTests.tearDown
 make=trade.TradeTests.make
 def view(self,uid=None):return self.a.snapshot(uid or self.buyer,'Test')['port']
 def act(self,action,key,**kw):return self.a.action(self.buyer,dict(action='port_'+action,key=key,revision=self.view()['revision'],**kw))
 def unlock(self,edition=4,stage=1):
  idx=next(i for i,q in enumerate(QUESTS) if q['id']=='S1-Q08')
  with self.a.conn() as c:
   c.execute('UPDATE castle_profiles SET xp=10000 WHERE user_id=?',(self.buyer,));c.execute('UPDATE campaign_progress SET quest_index=?,stage=?,accepted_at=?,payload=? WHERE user_id=?',(idx,stage,time.time()-10000,json.dumps(dict(edition=edition)),self.buyer))
  return idx
 def gather(self):
  self.act('enter','capitainerie');self.act('talk','captain');self.act('enter','entrepots')
  for key in sorted(WAREHOUSE):self.act('inspect',key)
  self.act('enter','passeur');self.act('talk','ferryman');self.act('enter','quai')
  for key in sorted(QUAY):self.act('inspect',key)
 def finish(self,choice='guards'):
  self.gather();self.act('choose',choice);self.act('battle','start')
  with self.a.conn() as c:
   p=json.loads(c.execute('SELECT payload FROM activity_port WHERE user_id=?',(self.buyer,)).fetchone()[0]);p['battle']['fighters'][1]['hp']=1;c.execute('UPDATE activity_port SET payload=? WHERE user_id=?',(json.dumps(p),self.buyer))
  self.act('battle','light');self.act('enter','capitainerie');self.act('talk','captain')
 def test_gate_is_quest_progress_not_level_or_client_payload(self):
  with self.a.conn() as c:c.execute('UPDATE castle_profiles SET xp=100000 WHERE user_id=?',(self.buyer,))
  self.assertFalse(self.view()['unlocked'])
  with self.assertRaises(ValueError):self.a.action(self.buyer,dict(action='port_enter',key='port',revision=0,unlocked=True,phase=7))
  self.unlock(stage=0);self.assertFalse(self.view()['unlocked'])
  self.unlock(stage=1);self.assertTrue(self.view()['unlocked'])
 def test_unlock_persists_after_restart_and_main_quest_moves_back(self):
  self.unlock();self.assertTrue(self.view()['unlocked'])
  with self.a.conn() as c:c.execute('UPDATE campaign_progress SET quest_index=0,stage=0 WHERE user_id=?',(self.buyer,))
  self.a=Activity(self.path);self.assertTrue(self.view()['unlocked'])
 def test_older_accepted_quests_keep_their_original_steps(self):
  idx=self.unlock(edition=3);row=dict(quest_index=idx,accepted_at=time.time());self.assertEqual([s['id'] for s in effective_quest(row,dict(edition=3))['steps']],[s['id'] for s in QUESTS[idx]['steps']]);self.assertEqual(len(effective_quest(row,dict(edition=4))['steps']),4);self.assertTrue(self.view()['unlocked'])
 def test_players_past_quest_gain_access_without_receipts_or_extra_reward(self):
  idx=self.unlock()
  with self.a.conn() as c:c.execute('UPDATE campaign_progress SET quest_index=?,accepted_at=NULL WHERE user_id=?',(idx+1,self.buyer))
  before=self.a.economy.get_balance(self.buyer);self.assertTrue(self.view()['unlocked']);self.assertEqual(before,self.a.economy.get_balance(self.buyer))
 def test_unaccepted_quest_does_not_open_port(self):
  self.unlock()
  with self.a.conn() as c:c.execute('UPDATE campaign_progress SET accepted_at=NULL WHERE user_id=?',(self.buyer,))
  self.assertFalse(self.view()['unlocked'])
 def test_locked_quay_and_out_of_order_clues_rejected(self):
  self.unlock()
  with self.assertRaises(ValueError):self.act('enter','quai')
  with self.assertRaises(ValueError):self.act('inspect','register')
  self.act('enter','passeur');self.act('talk','ferryman');self.assertEqual(self.view()['phase'],0)
  self.act('enter','capitainerie');self.act('talk','captain');self.assertEqual(self.view()['phase'],1)
  with self.assertRaises(ValueError):self.act('choose','guards')
 def test_clues_are_owner_scoped_and_not_given_before_inspection(self):
  self.unlock();self.assertEqual(self.view()['clues'],[]);self.act('enter','capitainerie');self.act('talk','captain');self.act('enter','entrepots');self.act('inspect','crate');self.assertEqual(len(self.view()['clues']),1);self.assertFalse(self.view(self.other)['unlocked'])
  with self.assertRaises(ValueError):self.act('inspect','crate')
 def test_revision_and_request_replay_resolve_only_once(self):
  self.unlock();p=self.view();body=dict(action='port_enter',key='capitainerie',revision=p['revision'],request_id='port-replay-once-0001');self.a.action(self.buyer,body);after=self.view();self.a.action(self.buyer,body);self.assertEqual(after,self.view())
  with self.assertRaises(ValueError):self.a.action(self.buyer,dict(action='port_enter',key='port',revision=p['revision']))
  with self.assertRaises(ValueError):self.a.action(self.buyer,dict(action='port_enter',key='port',revision=True))
 def test_main_objective_cannot_be_skipped_and_port_has_no_independent_gold(self):
  self.unlock();self.a.action(self.buyer,dict(action='campaign_world_enter',scene='port'));s=self.a.snapshot(self.buyer,'Test');q=s['campaign'];body=dict(action='campaign_step',quest_id=q['quest']['id'],revision=q['revision'],world_token=q['world']['token'])
  with self.assertRaises(ValueError):self.a.action(self.buyer,body)
  before=self.a.snapshot(self.buyer,'Test');self.finish();after=self.a.snapshot(self.buyer,'Test');self.assertTrue(after['port']['complete']);self.assertEqual(after['balance'],before['balance']);self.assertEqual(after['xp'],before['xp']);self.assertEqual(after['resources'],before['resources']);self.a.action(self.buyer,body);self.assertEqual(self.a.snapshot(self.buyer,'Test')['campaign']['stage'],2)
  self.act('talk','captain');self.assertEqual(after['balance'],self.a.snapshot(self.buyer,'Test')['balance'])
 def test_choice_changes_location_and_guard_support_only_once(self):
  self.unlock();self.gather();self.act('choose','guards');self.assertEqual(self.view()['scene'],'entrepots')
  with self.assertRaises(ValueError):self.act('choose','discreet')
  self.act('battle','start');b=self.view()['battle'];self.assertEqual(b['fighters'][1]['hp'],round(b['fighters'][1]['max_hp']*.9))
 def test_discreet_branch_stays_on_quay_with_full_enemy_hp(self):
  self.unlock();self.gather();self.act('choose','discreet');self.assertEqual(self.view()['scene'],'quai');self.act('battle','start');b=self.view()['battle'];self.assertEqual(b['fighters'][1]['hp'],b['fighters'][1]['max_hp'])
 def test_combat_mutual_exclusion_and_technique_changes(self):
  self.unlock();self.gather();self.act('choose','guards');self.act('battle','start')
  for body in [dict(action='battle_start',wager=1),dict(action='game_start',key='dice',wager=1),dict(action='ashkar_start',floor=1),dict(action='arena_equip',key='x')]:
   with self.assertRaises(ValueError):self.a.action(self.buyer,body)
  with self.assertRaises(ValueError):self.act('talk','foreman')
 def test_other_active_game_prevents_starting_port_combat(self):
  self.unlock();self.gather();self.act('choose','guards')
  with self.a.conn() as c:c.execute('UPDATE activity_play SET payload=? WHERE user_id=?',(json.dumps(dict(status='active')),self.buyer))
  with self.assertRaises(ValueError):self.act('battle','start')
 def test_abandon_keeps_evidence_and_has_server_retry_time(self):
  self.unlock();self.gather();self.act('choose','guards');self.act('battle','start');before=self.view()['clues'];self.act('battle','abandon');after=self.view();self.assertEqual(before,after['clues']);self.assertGreater(after['retry_at'],time.time());self.assertFalse(self.a.port.active(self.buyer))
  with self.assertRaises(ValueError):self.act('battle','start')
 def test_reconnect_keeps_scene_and_combat_hp_without_reward(self):
  self.unlock();self.gather();self.act('choose','guards');self.act('battle','start');self.act('battle','light');before=self.view();self.a=Activity(self.path);after=self.view();self.assertEqual(before,after)
 def test_port_maintenance_is_enforced_even_with_forged_client(self):
  self.unlock()
  with self.a.conn() as c:c.execute("INSERT INTO activity_maintenance VALUES('port','Intervention',0,'admin',?)",(time.time(),))
  with self.assertRaises(ValueError):self.act('enter','port')
  state=self.a.snapshot(self.buyer,'Test')['campaign']
  with self.assertRaisesRegex(ValueError,'Maintenance'):self.a.action(self.buyer,dict(action='campaign_step',quest_id=state['quest']['id'],revision=state['revision']))
 def test_catalog_remains_immutable_and_rewards_unchanged(self):
  q=next(q for q in QUESTS if q['id']=='S1-Q08');before=json.dumps(QUESTS);new=port_quest(q);self.assertEqual(new['gold'],q['gold']);self.assertEqual(new['xp'],q['xp']);self.assertEqual(json.dumps(QUESTS),before)
