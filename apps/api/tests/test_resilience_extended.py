"""Extra adversarial coverage: restart, process death, malformed actions and buffs."""
import copy, itertools, json, subprocess, sys, tempfile, unittest, uuid
from dataclasses import asdict
from pathlib import Path
from unittest.mock import patch
sys.path.insert(0,str(Path(__file__).parents[1]))
import test_play as fixtures
from activity import Activity
from arena_engine import Fighter,BattleState,resolve_action,arena_player_skills
import arena_techniques as tech
from ashkar_arena import TowerFighter
from khaz import bonuses_for,CFG
from sqlite_store import atomic

class ResilienceTests(unittest.TestCase):
 setUp=fixtures.GameTests.setUp
 tearDown=fixtures.GameTests.tearDown
 s=fixtures.GameTests.s
 act=fixtures.GameTests.act
 access=fixtures.GameTests.access
 blackjack_hand=fixtures.GameTests.blackjack_hand
 def restart(self):self.a=Activity(self.a.path)
 def test_unfavourable_blackjack_survives_restarts_and_expired_entry(self):
  self.blackjack_hand([10,6],[10,7],[10]);before=self.a.play.read(self.uid);wallet=self.s()['balance']['wallet']
  for _ in range(3):self.restart();self.assertEqual(self.a.play.read(self.uid),before);self.assertEqual(self.s()['balance']['wallet'],wallet)
  with patch.object(self.a.play.dark,'has_clandestine_access',return_value=False):self.act(action='game_step',key='hit')
  self.assertEqual(self.s()['play']['payout'],0);self.restart();self.assertEqual(self.s()['balance']['wallet'],wallet)
 def test_russian_same_barrel_after_each_turn_and_restart(self):
  self.access()
  with patch('play.random.randint',return_value=6):self.act(action='game_start',key='russian',wager=100)
  wallet=self.s()['balance']['wallet']
  for i in range(3):
   before=self.a.play.read(self.uid);self.restart();self.assertEqual(self.a.play.read(self.uid),before);self.assertEqual(self.s()['balance']['wallet'],wallet)
   self.act(action='game_step',key='try')
  self.assertEqual(self.s()['play']['payout'],200);self.assertEqual(self.s()['balance']['wallet'],wallet+200)
  self.restart();self.assertEqual(self.s()['balance']['wallet'],wallet+200)
 def test_arena_hp_effects_and_stake_survive_restart(self):
  self.act(action='battle_start',wager=100);self.act(action='battle_step',key='defend');before=self.a.play.read(self.uid);wallet=self.s()['balance']['wallet']
  for _ in range(3):self.restart();self.assertEqual(self.a.play.read(self.uid),before);self.assertEqual(self.s()['balance']['wallet'],wallet)
  self.act(action='battle_step',key='abandon');self.assertEqual(self.s()['balance']['wallet'],wallet);self.assertEqual(self.s()['play']['outcome'],'defeat')
 def test_orphaned_engine_wagers_refund_once_without_a_saved_round(self):
  self.access();r=self.a.play.casino.start(self.uid,'russian',100);self.assertTrue(r['ok']);self.restart();self.assertEqual(self.s()['balance']['wallet'],9970)
  self.restart();self.assertEqual(self.s()['balance']['wallet'],9970)
 def test_incomplete_saved_round_refunds_its_engine_once(self):
  self.access();self.act(action='game_start',key='russian',wager=100);_,p=self.a.play.read(self.uid);p.pop('danger');self.a.play.save(self.uid,p)
  self.restart();self.assertEqual(self.s()['play']['status'],'refunded');self.assertEqual(self.s()['balance']['wallet'],9970);self.restart();self.assertEqual(self.s()['balance']['wallet'],9970)
 def test_recovery_failure_is_atomic(self):
  self.access();self.a.play.casino.start(self.uid,'russian',100)
  with patch('arena_engine.ArenaStore.recover_unfinished',side_effect=RuntimeError('recovery interrupted')):
   with self.assertRaises(RuntimeError):self.restart()
  self.assertEqual(self.a.economy.get_balance(self.uid).wallet,9870)
  self.restart();self.assertEqual(self.s()['balance']['wallet'],9970)
 def child_crash(self,body,hook):
  script='''import sys,os,json
sys.path.insert(0,sys.argv[1]);from activity import Activity
a=Activity(sys.argv[2]);uid=int(sys.argv[3]);body=json.loads(sys.argv[4]);hook=sys.argv[5]
if hook=='save':
 def crash(*args):os._exit(37)
 a.play.save=crash
else:
 original=a._action
 def crash(*args):original(*args);os._exit(37)
 a._action=crash
a.action(uid,body)
'''
  result=subprocess.run([sys.executable,'-c',script,str(Path(__file__).parents[1]),str(self.a.path),str(self.uid),json.dumps(body),hook],capture_output=True,text=True,timeout=30)
  self.assertEqual(result.returncode,37,result.stderr)
 def test_process_death_after_bet_debit_before_state_save_rolls_back(self):
  self.access();rev=self.a.play.read(self.uid)[0];self.child_crash(dict(action='game_start',key='russian',wager=100,revision=rev,request_id='crash-start-request-0001'),'save')
  self.restart();self.assertEqual(self.s()['balance']['wallet'],9970);self.assertNotEqual(self.s()['play'].get('status'),'active')
  with self.a.conn() as c:self.assertEqual(c.execute("SELECT COUNT(*) FROM casino_sessions WHERE status='active'").fetchone()[0],0)
 def test_process_death_after_payout_before_receipt_keeps_paid_hand_unsettled(self):
  self.blackjack_hand([10,10],[10,7],[2]);before=self.a.play.read(self.uid);wallet=self.s()['balance']['wallet'];body=dict(action='game_step',key='stand',revision=before[0],request_id='crash-finish-request-001')
  self.child_crash(body,'action');self.restart();self.assertEqual(self.a.play.read(self.uid),before);self.assertEqual(self.s()['balance']['wallet'],wallet)
  self.a.action(self.uid,body);self.a.action(self.uid,body);self.assertEqual(self.s()['balance']['wallet'],wallet+20)
 def test_actual_new_process_reads_identical_round_and_private_secrets_stay_private(self):
  self.access()
  with patch('play.random.randint',return_value=6):self.act(action='game_start',key='russian',wager=100)
  before=self.a.play.read(self.uid)
  script="import sys,json;sys.path.insert(0,sys.argv[1]);from activity import Activity;a=Activity(sys.argv[2]);print(json.dumps(a.play.read(int(sys.argv[3]))))"
  result=subprocess.run([sys.executable,'-c',script,str(Path(__file__).parents[1]),str(self.a.path),str(self.uid)],capture_output=True,text=True,timeout=30)
  self.assertEqual(result.returncode,0,result.stderr);self.assertEqual(json.loads(result.stdout),list(before));self.assertNotIn('danger',self.s()['play'])
 def test_malformed_action_matrix_never_changes_balances(self):
  actions=['deposit','withdraw','sell','buy','upgrade','story_read','story_unlock','job_accept','start','game_start','game_step','battle_start','battle_step','arena_equip','khaz_buy','khaz_upgrade','ashkar_start','ashkar_step','campaign_accept','campaign_claim']
  bad=[None,True,False,-1,1.25,10**40,[],{},'unknown']
  before=self.a.economy.get_balance(self.uid);count=0
  for action,value in itertools.product(actions,bad):
   body=dict(action=action,key=value,amount=value,chapter=value,batch=value,tool=value,revision=value,slot=value,branch=value,floor=value,technique=value,loadout_revision=value,quest_id=value,wager=value,request_id=str(uuid.uuid4()))
   try:self.a.action(self.uid,body)
   except (ValueError,TypeError):pass
   count+=1;self.assertEqual(self.a.economy.get_balance(self.uid),before,repr(body))
  self.assertEqual(count,180)

 def test_552_individual_field_type_mutations_have_no_uncaught_internal_error(self):
  bases=[dict(action='start',key='elarwyn_foraging',tool='hands'),dict(action='game_start',key='coin',choice='pile',wager=1,revision=0),dict(action='arena_equip',slot='light',technique='base_light',loadout_revision=0),dict(action='job_accept',batch='unknown',key='unknown'),dict(action='campaign_accept',quest_id='unknown',revision=0),dict(action='khaz_buy',slot='weapon',branch='atk',revision=0)]
  count=0
  for base in bases:
   for field in sorted(set(base)|{'tool_level','bag_level','amount','request_id','save_owner','bets','choice','name'}):
    for value in [None,False,True,[],{},1.1,10**50,'x'*5000]:
     body={**base,field:value};body['revision']=body.get('revision',0)
     try:self.a.action(self.uid,body)
     except (ValueError,TypeError):pass
     count+=1
  self.assertEqual(count,552)

class CombatCombinationTests(unittest.TestCase):
 def test_all_180_equippable_combinations_keep_catalog_and_bounds_after_serialization(self):
  # All four-slot combinations at three levels, against ten champion classes,
  # with and without real legendary equipment: 10,800 scenarios, four rounds each.
  from tower_techniques import TOWER_CATALOG
  from arena_engine import CHAMPION_PROFILES
  catalog=copy.deepcopy(tech.CATALOG);tower=copy.deepcopy(TOWER_CATALOG);n=0
  for level in (1,10,30):
   base={k:{**v,'id':'base_'+k} for k,v in arena_player_skills(level).items()}
   choices={k:[base[k]] for k in tech.SLOTS}
   for t in list(tech.CATALOG.values())+list(TOWER_CATALOG.values()):
    t={**t,'emoji':base[t['slot']]['emoji']}
    if 'power' in t:t['power']=round(t['power']*base[t['slot']]['power']/arena_player_skills(1)[t['slot']]['power'])
    choices[t['slot']].append(t)
   for moves in itertools.product(*(choices[k] for k in tech.SLOTS)):
    for champion,equipped in itertools.product(range(1,11),(False,True)):
     gear=bonuses_for({k:dict(branch='atk',tier='legendaire') for k in CFG['SLOTS']}) if equipped else {}
     p=tech.ArenaFighter(1,'Joueur','arena_fighter',player_level=level,max_hp=100+10*(level-1),**gear);p.loadout=dict(zip(tech.SLOTS,copy.deepcopy(moves)))
     enemy=Fighter(None,'Champion',CHAMPION_PROFILES[champion]['class_key'],champion_level=champion)
     b=BattleState('probe','champion',0,[p,enemy],0)
     with patch('arena_engine.random.random',return_value=.4),patch('arena_engine.random.uniform',return_value=1.):
      for action in ('light','heavy','defend','ultimate'):
       if b.finished:break
       tech.resolve(b,action,resolve_action)
       for f in b.fighters:self.assertGreaterEqual(f.hp,0);self.assertLessEqual(f.hp,f.max_hp);self.assertLessEqual(f.next_damage_bonus,.2);self.assertLessEqual(f.bleed_pending,4)
       raw=asdict(b);restored=[]
       for i,row in enumerate(raw['fighters']):
        f=tech.ArenaFighter(**row);f.hp=row['hp'];f.max_hp=row['max_hp']
        if i==0:f.loadout=p.loadout
        restored.append(f)
       reloaded=BattleState(**{**raw,'fighters':restored});self.assertEqual(asdict(reloaded),asdict(b));b=reloaded;p=b.fighters[0]
       if not b.finished:b.switch();tech.resolve(b,'light',resolve_action)
       if not b.finished:b.switch()
     n+=1
  self.assertEqual(n,10800);self.assertEqual(tech.CATALOG,catalog);self.assertEqual(TOWER_CATALOG,tower)
 def test_repeated_charge_does_not_accumulate_and_bonus_consumes_on_attack(self):
  p=tech.ArenaFighter(1,'Joueur','arena_fighter');p.loadout=arena_player_skills(1);p.loadout['light']={**p.loadout['light'],**tech.CATALOG[4]}
  t=Fighter(None,'Cible','arena_fighter',max_hp=10000);b=BattleState('charge','champion',0,[p,t],0)
  with patch('arena_engine.random.random',return_value=.4),patch('arena_engine.random.uniform',return_value=1.):
   for _ in range(100):tech.resolve(b,'light',resolve_action);self.assertEqual(p.next_damage_bonus,.2)
   tech.resolve(b,'heavy',resolve_action);self.assertEqual(p.next_damage_bonus,0)
 def test_legendary_bonuses_sum_one_piece_per_slot_and_reload_does_not_multiply_hp(self):
  for branch in CFG['BRANCH_LABELS']:
   eq={slot:dict(branch=branch,tier='legendaire') for slot in CFG['SLOTS']};bonuses=bonuses_for(eq)
   expected=sum(CFG['SPEC_PIECE']['legendaire']['advanced' if s in CFG['ADVANCED_SLOTS'] else 'base'] for s in eq)
   self.assertEqual(bonuses['equipment_'+branch+'_pct'],expected)
   p=TowerFighter(1,'Joueur','arena_fighter',max_hp=300,**bonuses);hp=p.max_hp
   for _ in range(100):
    raw=asdict(p);p=TowerFighter(**raw);p.hp=raw['hp'];p.max_hp=raw['max_hp'];self.assertEqual(p.max_hp,hp)

class EventAndStorageTests(unittest.TestCase):
 setUp=fixtures.GameTests.setUp
 tearDown=fixtures.GameTests.tearDown
 s=fixtures.GameTests.s
 act=fixtures.GameTests.act
 access=fixtures.GameTests.access
 blackjack_hand=fixtures.GameTests.blackjack_hand
 def events(self,on):
  from admin_engine import AdminStore
  AdminStore(self.a.path)
  with self.a.conn() as c:
   for key in ('gold_x2','xp_x2'):c.execute('INSERT INTO bot_events(event_key,enabled) VALUES(?,?) ON CONFLICT(event_key) DO UPDATE SET enabled=excluded.enabled',(key,int(on)))
 def test_gold_event_doubles_profit_once_not_returned_stake_and_replay_is_stable(self):
  self.events(True);self.access();wallet=self.s()['balance']['wallet'];body=dict(action='game_start',key='slots',wager=10,revision=self.a.play.read(self.uid)[0],request_id='event-slots-test-00001')
  with patch('play.draw_slot',return_value=['7️⃣']*3):self.a.action(self.uid,body)
  self.assertEqual(self.s()['play']['payout'],230);self.assertEqual(self.s()['balance']['wallet'],wallet+220);self.assertEqual(self.s()['xp'],6)
  self.events(False);self.a.action(self.uid,body);self.assertEqual(self.s()['balance']['wallet'],wallet+220);self.assertEqual(self.s()['xp'],6)
 def test_event_blackjack_double_uses_updated_stake_for_profit(self):
  self.blackjack_hand([5,6],[10,7],[10]);self.events(True);wallet=self.s()['balance']['wallet'];self.act(action='game_step',key='double');p=self.s()['play']
  self.assertEqual(p['wager'],20);self.assertEqual(p['payout'],60);self.assertEqual(self.s()['balance']['wallet'],wallet-10+60)
 def test_event_losses_and_ties_never_create_profit(self):
  self.events(True);wallet=self.s()['balance']['wallet']
  with patch('play.flip_coin',return_value='face'):self.act(action='game_start',key='coin',wager=10,choice='pile')
  self.assertEqual(self.s()['balance']['wallet'],wallet-10);self.assertEqual(self.s()['xp'],10)
  with patch('play.roll_die',return_value=4):self.act(action='game_start',key='dice',wager=10)
  self.assertEqual(self.s()['balance']['wallet'],wallet-10);self.assertEqual(self.s()['play']['payout'],10);self.assertEqual(self.s()['xp'],20)
 def test_30_days_replayed_in_reverse_cannot_repay_any_daily(self):
  from datetime import date,timedelta
  days=[(date(2026,10,1)+timedelta(days=i)).isoformat() for i in range(30)]
  for day in days+list(reversed(days)):
   with patch.object(self.a.castle,'_today',return_value=day):self.a.action(self.uid,dict(action='daily'))
  self.assertEqual(self.s()['balance']['wallet'],10300);self.assertEqual(self.s()['stats']['xp'],600)
  with self.a.conn() as c:self.assertEqual(c.execute('SELECT COUNT(*) FROM castle_daily_receipts WHERE user_id=?',(self.uid,)).fetchone()[0],30)
 def test_four_processes_replay_one_deposit_with_an_active_game(self):
  self.access()
  with patch('play.random.randint',return_value=6):self.act(action='game_start',key='russian',wager=100)
  before=self.a.play.read(self.uid);wallet=self.s()['balance']['wallet']
  code="import sys;sys.path.insert(0,sys.argv[1]);from activity import Activity;a=Activity(sys.argv[2]);a.action(int(sys.argv[3]),dict(action='deposit',amount=100,request_id='multiprocess-replay-0001'))"
  children=[subprocess.Popen([sys.executable,'-c',code,str(Path(__file__).parents[1]),str(self.a.path),str(self.uid)],stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True) for _ in range(4)]
  for child in children:
   out,err=child.communicate(timeout=60);self.assertEqual(child.returncode,0,err)
  self.assertEqual(self.s()['balance']['wallet'],wallet-100);self.assertEqual(self.s()['balance']['bank'],100);self.assertEqual(self.a.play.read(self.uid),before)
 def test_corrupted_database_refuses_start_and_is_not_overwritten(self):
  path=Path(self.tmp.name)/'corrupt.db';data=b'Not a SQLite database: preserve evidence';path.write_bytes(data)
  import sqlite3
  with self.assertRaises(sqlite3.DatabaseError):Activity(path)
  self.assertEqual(path.read_bytes(),data)
 def test_failed_backup_does_not_replace_previous_verified_copy(self):
  from save_safety import backup
  first=backup(self.a.path,force=True);before=first.read_bytes()
  with patch('save_safety.os.fsync',side_effect=OSError('simulated full disk')):
   with self.assertRaises(OSError):backup(self.a.path,force=True)
  self.assertEqual(first.read_bytes(),before);self.assertEqual(list(first.parent.glob('*.tmp')),[])

from aiohttp import web
from aiohttp.test_utils import TestClient,TestServer
import activity as adapter
import server
class InputBoundaryHttpTests(unittest.IsolatedAsyncioTestCase):
 async def asyncSetUp(self):
  self.tmp=tempfile.TemporaryDirectory();self.old=adapter.SERVICE;self.a=Activity(self.tmp.name+'/http.db');adapter.SERVICE=self.a
  app=web.Application(client_max_size=4096);app.router.add_get('/api/activity',adapter.activity);app.router.add_post('/api/activity',adapter.activity);app.router.add_post('/api/admin',server.admin)
  self.client=TestClient(TestServer(app),headers={'X-Altherya-Request':'1'});await self.client.start_server();r=await self.client.get('/api/activity');self.uid=self.a.session_uid(r.cookies['altherya_test'].value)
 async def asyncTearDown(self):await self.client.close();adapter.SERVICE=self.old;self.tmp.cleanup()
 async def test_nested_json_rejected_cleanly_without_a_server_error(self):
  r=await self.client.post('/api/activity',data='{"action":"daily","extra":'+'['*1300+'0'+']'*1300+'}',headers={'Content-Type':'application/json'})
  self.assertEqual(r.status,400)
 async def test_oversize_and_malformed_json_and_forged_admin_are_rejected(self):
  for body,expected in [('x'*5000,413),('{broken',400),('[]',400),('null',400),('true',400)]:
   with self.subTest(expected=expected,body=body[:10]):
    r=await self.client.post('/api/activity',data=body,headers={'Content-Type':'application/json'});self.assertEqual(r.status,expected)
  for value in ['666805849011912705',{},None,True]:
   r=await self.client.post('/api/admin',json=dict(action='list',discord_id=value,admin=True));self.assertEqual(r.status,403)
 async def test_client_values_and_injection_strings_cannot_authorize_play_before_tutorial(self):
  for val in ["' OR 1=1 --",'<img src=x onerror=alert(1)>',{'$gt':0},10**50,True,None,[],{}]:
   r=await self.client.post('/api/activity',json=dict(action='daily',completed=True,reward_claimed=True,user_id=val,admin=True,gold=10**9))
   self.assertEqual(r.status,400)
  self.assertEqual(self.a.economy.get_balance(self.uid).wallet,0)

class SnapshotConsistencyTests(unittest.TestCase):
 setUp=fixtures.GameTests.setUp
 tearDown=fixtures.GameTests.tearDown
 s=fixtures.GameTests.s
 act=fixtures.GameTests.act
 def test_failed_snapshot_rolls_back_reconciliation_and_later_pays_once(self):
  self.act(action='start',key='elarwyn_foraging',tool='hands');run=self.a.expeditions.active_run(self.uid)
  with self.a.conn() as c:c.execute('UPDATE expedition_runs SET ends_at=0 WHERE run_id=?',(run.run_id,))
  before=self.a.castle.profile(self.uid)['xp']
  with patch('objectives.objectives',side_effect=RuntimeError('failed snapshot rendering')):
   with self.assertRaises(RuntimeError):self.s()
  with self.a.conn() as c:
   self.assertEqual(c.execute('SELECT claimed FROM expedition_runs WHERE run_id=?',(run.run_id,)).fetchone()[0],0)
   self.assertEqual(c.execute('SELECT COUNT(*) FROM activity_rewards WHERE reference=?',('expedition:'+run.run_id,)).fetchone()[0],0)
  self.assertEqual(self.a.castle.profile(self.uid)['xp'],before)
  self.s();paid=self.a.castle.profile(self.uid)['xp'];self.assertGreater(paid,before);self.s();self.assertEqual(self.a.castle.profile(self.uid)['xp'],paid)
 def test_concurrent_xp_awards_never_mix_level_and_total_xp_from_different_states(self):
  from concurrent.futures import ThreadPoolExecutor
  from progression import level_from_xp
  def award():
   for _ in range(60):
    with atomic(self.a.path):self.a.castle.add_xp(self.uid,10)
  with ThreadPoolExecutor(max_workers=2) as pool:
   future=pool.submit(award)
   for _ in range(30):
    s=self.s();level,xp,needed=level_from_xp(s['stats']['xp']);self.assertEqual((s['level'],s['xp'],s['xp_needed']),(level,xp,needed))
   future.result()
  self.assertEqual(self.s()['stats']['xp'],600)
