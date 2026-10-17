import unittest,json,uuid
from unittest.mock import patch
from concurrent.futures import ThreadPoolExecutor
import test_arena_complete as harness
from activity import Activity
from job_board_engine import RARITIES
from economy_balance import JOB_GOLD
from progression import JOB_RARITY_XP

class ActivityJobsTests(unittest.TestCase):
 setUp=harness.ArenaCompleteTests.setUp
 tearDown=harness.ArenaCompleteTests.tearDown
 state=harness.ArenaCompleteTests.state
 act=harness.ArenaCompleteTests.act
 def test_eight_unique_neutral_offers_no_roll_or_api_leak_and_stable_on_reload(self):
  with patch.object(self.a.jobs,'_rarity_roll',side_effect=AssertionError('early roll')):
   batch,jobs=self.a.jobs._generate_batch();self.assertEqual(len(jobs),8);self.assertEqual(len({j.title for j in jobs}),8);self.assertTrue(all(j.rarity=='unrevealed' and j.reward==0 for j in jobs))
   board=self.state()['board'];self.assertEqual(len(board['jobs']),8);self.assertTrue(all(set(j)=={'job_id','title'} for j in board['jobs']));self.assertEqual(self.state()['board'],board)
  self.a=Activity(self.a.path);self.assertEqual(self.state()['board'],board)
 def test_rank_drawn_only_after_valid_acceptance_and_client_cannot_select_rank(self):
  b=self.state()['board'];j=b['jobs'][0]
  with patch.object(self.a.jobs,'_rarity_roll',return_value='legendary') as roll:
   self.act('job_accept',batch='stale',key=j['job_id']);self.act('job_accept',batch=b['batch_id'],key='missing');roll.assert_not_called()
   self.act('job_accept',batch=b['batch_id'],key=j['job_id'],rarity='common',reward=9999);self.assertEqual(roll.call_count,1)
  p=self.state()['pending'];self.assertEqual(p['job']['rarity'],'legendary');self.assertTrue(JOB_GOLD['legendary'][0]<=p['job']['reward']<=JOB_GOLD['legendary'][1]);self.assertEqual(self.state()['balance']['wallet'],100);self.assertEqual(self.state()['board']['jobs'],[])
 def test_all_five_ranks_use_original_weights_and_ranges_at_acceptance(self):
  self.assertEqual([r['weight'] for r in RARITIES.values()],[55,25,12,6,2])
  for i,rank in enumerate(RARITIES):
   uid=10000+i;b=self.a.jobs.get_board(uid)
   with patch.object(self.a.jobs,'_rarity_roll',return_value=rank):ok,_,j,_=self.a.jobs.accept_job(uid,b.batch_id,b.jobs[0].job_id)
   self.assertTrue(ok);self.assertEqual(j.rarity,rank);self.assertTrue(JOB_GOLD[rank][0]<=j.reward<=JOB_GOLD[rank][1])
 def test_double_click_other_tab_and_expired_unclaimed_contract_cannot_reroll(self):
  b=self.state()['board'];bodies=[dict(action='job_accept',batch=b['batch_id'],key=j['job_id'],request_id=str(uuid.uuid4())) for j in b['jobs'][:2]]
  with patch.object(self.a.jobs,'_rarity_roll',return_value='rare') as roll:
   with ThreadPoolExecutor(max_workers=2) as pool:list(pool.map(lambda body:self.a.action(self.uid,body),bodies))
   self.assertEqual(roll.call_count,1)
   with self.a.conn() as c:c.execute('UPDATE job_board_state SET next_board_at=0,reward_ready_at=0 WHERE user_id=?',(self.uid,))
   self.act('job_accept',batch=b['batch_id'],key=b['jobs'][1]['job_id']);self.assertEqual(roll.call_count,1)
  with self.a.conn() as c:self.assertEqual(c.execute('SELECT accepted_total FROM job_board_state WHERE user_id=?',(self.uid,)).fetchone()[0],1)
 def test_replay_and_restart_preserve_one_draw_and_identical_contract(self):
  b=self.state()['board'];body=dict(action='job_accept',batch=b['batch_id'],key=b['jobs'][0]['job_id'],request_id=str(uuid.uuid4()))
  self.a.action(self.uid,body);p=self.a.jobs.pending_reward(self.uid)
  with patch.object(self.a.jobs,'_rarity_roll',side_effect=AssertionError('reroll')):self.a.action(self.uid,body);self.state()
  self.a=Activity(self.a.path);after=self.a.jobs.pending_reward(self.uid);self.assertEqual(after['job'],p['job']);self.assertEqual(after['ready_at'],p['ready_at'])
 def test_migrate_old_unsiged_offers_but_keep_signed_old_contract(self):
  b=self.state()['board']
  with self.a.conn() as c:c.execute('UPDATE job_board_state SET jobs_json=? WHERE user_id=?',(json.dumps([dict(job_id='old',title='Ancienne offre',rarity='legendary',reward=500)]),self.uid))
  self.a=Activity(self.a.path);fresh=self.state()['board'];self.assertNotEqual(fresh['batch_id'],b['batch_id']);self.assertEqual(len(fresh['jobs']),8)
  old=dict(job_id='signed',title='Ancien contrat',rarity='legendary',reward=500)
  with self.a.conn() as c:c.execute("UPDATE job_board_state SET pending_job_json=?,reward_ready_at=9999999999 WHERE user_id=?",(json.dumps(old),self.uid))
  self.a=Activity(self.a.path);self.assertEqual(self.state()['pending']['job'],old)
 def test_claim_uses_rolled_gold_xp_once_and_next_batch_has_eight_offers(self):
  b=self.state()['board'];before=self.a.castle.profile(self.uid)['xp']
  with patch.object(self.a.jobs,'_rarity_roll',return_value='epic'):self.act('job_accept',batch=b['batch_id'],key=b['jobs'][0]['job_id'])
  reward=self.state()['pending']['job']['reward'];self.act('job_claim');self.assertEqual(self.state()['balance']['wallet'],100)
  with self.a.conn() as c:c.execute('UPDATE job_board_state SET reward_ready_at=0 WHERE user_id=?',(self.uid,))
  self.act('job_claim');self.assertEqual(self.state()['balance']['wallet'],100+reward);self.assertEqual(self.a.castle.profile(self.uid)['xp']-before,JOB_RARITY_XP['epic']);self.assertEqual(len(self.state()['board']['jobs']),8)
  self.act('job_claim');self.assertEqual(self.state()['balance']['wallet'],100+reward)
 def test_write_failure_rolls_back_acceptance_and_keeps_board(self):
  b=self.state()['board']
  with self.a.conn() as c:c.execute("CREATE TRIGGER reject_contract BEFORE UPDATE ON job_board_state WHEN NEW.pending_job_json!='' BEGIN SELECT RAISE(ABORT,'test'); END")
  with self.assertRaises(Exception):self.act('job_accept',batch=b['batch_id'],key=b['jobs'][0]['job_id'])
  self.assertEqual(self.state()['board'],b);self.assertIsNone(self.state()['pending']);self.assertEqual(self.state()['balance']['wallet'],100)
