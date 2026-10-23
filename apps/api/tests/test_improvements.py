import itertools,json,sys,unittest
from pathlib import Path
from unittest.mock import patch
sys.path.insert(0,str(Path(__file__).parents[1]))
from expedition_guide import preparation,catalog
from expedition_engine import EXPEDITIONS,LOOT_TABLES,generate_loot
from campaign_story import enrich,consequences
from campaign import QUESTS
from game_fairness import rules
from casino_engine import SLOT_SYMBOLS,SLOT_WEIGHTS,slot_multiplier
from arena_engine import Fighter,BattleState
import arena_combat,ashkar_arena
import test_trading as fixtures

class PublicGuideTests(unittest.TestCase):
 def test_preview_matches_the_real_draw_pool_for_every_profession_and_tier(self):
  for destination,tools in LOOT_TABLES.items():
   for tool in tools:
    for tier in range(6):
     captured=[]
     def pick(names,weights,k):captured.extend(names);return [names[0]]
     with patch('expedition_engine.random.choices',side_effect=pick):generate_loot(destination,tool,tier,1)
     guide=preparation(destination,tool,tier,1)
     self.assertEqual([r['name'] for r in guide['resources']],captured)
     if captured:self.assertAlmostEqual(sum(r['chance'] for r in guide['resources']),1)
 def test_wrong_profession_is_rejected_and_capacity_is_actual(self):
  with self.assertRaises(ValueError):preparation('elarwyn_1','pickaxe',1,1)
  self.assertEqual(preparation('elarwyn_1','axe',1,2)['capacity'],14)
  self.assertEqual(preparation('elarwyn_foraging','hands',0,1)['capacity'],6)
 def test_catalog_contains_no_generated_trip_or_reward(self):
  public=catalog();self.assertEqual(set(public),set(LOOT_TABLES));self.assertNotIn('run_id',json.dumps(public))
  for key in public:self.assertIn(key,EXPEDITIONS)
 def test_slots_exact_return_over_all_125_results_is_balanced_and_public(self):
  total=sum(SLOT_WEIGHTS);expected=0
  for indices in itertools.product(range(5),repeat=3):
   probability=1
   for i in indices:probability*=SLOT_WEIGHTS[i]/total
   expected+=probability*slot_multiplier([SLOT_SYMBOLS[i] for i in indices])
  self.assertAlmostEqual(expected,rules()['slots_return']);self.assertGreater(expected,.94);self.assertLess(expected,.97)
 def test_all_eight_games_have_probabilities_and_no_guaranteed_wins(self):
  self.assertEqual(set(rules()['notes']),set(('blackjack','roulette','slots','horses','russian','dice','coin','rps')))
 def test_every_recorded_choice_has_a_distinct_valid_narrative_consequence(self):
  for q in QUESTS:
   for step in q['steps']:
    if step['kind']!='choice':continue
    a=consequences({q['id']:step['options'][0]},QUESTS);b=consequences({q['id']:step['options'][1]},QUESTS)
    self.assertEqual(len(a),1);self.assertEqual(len(b),1);self.assertNotEqual(a[0]['reaction'],b[0]['reaction'])
 def test_future_choices_and_invalid_choices_do_not_spoil_current_dialogue(self):
  q=QUESTS[0];self.assertFalse(enrich(q,{'S4-Q07':'Récupérer les relevés : le Faussaire disparaît'},QUESTS)['context'])
  self.assertEqual(consequences({'S1-Q04':'Forged choice'},QUESTS),[])
 def test_earlier_choices_are_visible_without_changing_rewards_or_steps(self):
  original=QUESTS[5];before=json.dumps(original,sort_keys=True)
  choice=next(q for q in QUESTS if q['id']=='S1-Q04')['steps'];step=next(s for s in choice if s['kind']=='choice')
  result=enrich(original,{'S1-Q04':step['options'][0]},QUESTS)
  self.assertTrue(result['context']);self.assertEqual(json.dumps(original,sort_keys=True),before)
  for key in ('gold','xp','steps','min_duration','min_level'):self.assertEqual(result[key],original[key])

class TacticsTests(unittest.TestCase):
 def battle(self,champion=2):
  player=Fighter(1,'Vous','arena_fighter',player_level=5);enemy=Fighter(None,'Gardien','gardien',champion_level=champion)
  return BattleState('guide','champion',0,[player,enemy],0)
 def test_readout_uses_committed_intent_and_never_rolls_a_result(self):
  b=self.battle();b.fighters[0].counter_ready=True;b.fighters[1].defending=True
  with patch('arena_engine.random.random',side_effect=AssertionError('No RNG in previews')):
   read=arena_combat.tactical_readout({'enemy_action':'ultimate'},b)
  self.assertEqual(read['key'],'ultimate');self.assertEqual(read['name'],b.fighters[1].cfg['skills']['ultimate']['name'])
  self.assertTrue(any('riposte' in s for s in read['notes']));self.assertTrue(any('garde adverse' in s for s in read['notes']))
 def test_low_health_rempart_adapts_without_repeating_a_permanent_guard(self):
  b=self.battle();b.fighters[1].hp=1
  self.assertEqual(arena_combat.choose({'round':4},b),'defend')
  self.assertNotEqual(arena_combat.choose({'round':5},b),'defend')
 def test_tower_guardians_have_distinct_readable_roles(self):
  self.assertEqual(len({ashkar_arena.opponent(i)['role'] for i in range(1,11)}),10)
 def test_debrief_is_derived_from_actual_misses_and_guards(self):
  events=[dict(actor=0,action='heavy',kind='miss',guarded=False,damage=0)]*2
  report=arena_combat.debrief({'events':events});self.assertTrue(any('2 attaques ont manqué' in x for x in report))

class MarketFilterTests(unittest.TestCase):
 setUp=fixtures.TradeTests.setUp
 tearDown=fixtures.TradeTests.tearDown
 make=fixtures.TradeTests.make
 offer=fixtures.TradeTests.offer
 def test_price_and_unit_sort_are_applied_before_pagination(self):
  a=self.offer(10,80);b=self.offer(1,20);c=self.offer(20,100)
  self.assertEqual([r['id'] for r in self.a.trading.listing(self.buyer,sort='unit_asc')['offers']],[c,a,b])
  self.assertEqual([r['id'] for r in self.a.trading.listing(self.buyer,sort='price_asc')['offers']],[b,a,c])
  self.assertEqual([r['id'] for r in self.a.trading.listing(self.buyer,sort='price_desc')['offers']],[c,a,b])
 def test_profession_and_accent_insensitive_search(self):
  with self.a.conn() as c:c.execute('INSERT INTO resources VALUES(?,?,?)',(self.seller,'Défense de sanglier',3))
  self.a.action(self.seller,dict(action='trade_create',item='Défense de sanglier',quantity=1,price=10))
  self.offer();data=self.a.trading.listing(self.buyer,search='DEFENSE',category='Chasseur')
  self.assertEqual(data['total'],1);self.assertEqual(data['offers'][0]['item'],'Défense de sanglier')
  self.assertEqual(self.a.trading.listing(self.buyer,category='Cueillette')['total'],0)
 def test_unknown_sort_or_sql_like_filter_is_rejected(self):
  for args in ({'sort':'price; DROP TABLE players'},{'category':'Other'}):
   with self.assertRaises(ValueError):self.a.trading.listing(self.buyer,**args)
