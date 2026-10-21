"""Reproducible synthetic draws; no network, player wallet or production DB."""
import sys,json,random,itertools,math
from pathlib import Path
from fractions import Fraction
root=Path(__file__).resolve().parents[1];sys.path[:0]=[str(root/'apps/api'),str(root/'apps/bot/tourwork')]
from casino_engine import SLOT_SYMBOLS,SLOT_WEIGHTS,slot_multiplier
from roulette_rules import OUTSIDE,covered
N=200000;rng=random.Random(20261021);results={}
# Exact distributions, avoiding misleading conclusions from a short lucky run.
slots=sum(Fraction(SLOT_WEIGHTS[a]*SLOT_WEIGHTS[b]*SLOT_WEIGHTS[c],sum(SLOT_WEIGHTS)**3)*slot_multiplier([SLOT_SYMBOLS[a],SLOT_SYMBOLS[b],SLOT_SYMBOLS[c]]) for a,b,c in itertools.product(range(5),repeat=3))
results['slots_exact_return_per_gold']=float(slots)
results['roulette_standard_exact_return_per_gold']=36/37
results['coin_exact_return_per_gold']=1
results['dice_with_tie_refund_exact_return_per_gold']=1
results['rps_with_tie_refund_exact_return_per_gold']=1
coin_net=0;dice_net=0;rps_net=0;slots_net=0;roulette_net=0
for _ in range(N):
 coin_net+=2*(rng.randrange(2)==0)-1
 a,b=rng.randrange(1,7),rng.randrange(1,7);dice_net+=(2 if a>b else 1 if a==b else 0)-1
 rps_net+=rng.choice([0,1,2])-1
 slots_net+=slot_multiplier(rng.choices(SLOT_SYMBOLS,weights=SLOT_WEIGHTS,k=3))-1
 roulette_net+=2*(rng.randrange(37) in OUTSIDE['red'])-1
results['synthetic_draws_per_game']=N
results['simulated_net_gold_at_one_gold_per_round']={'coin':coin_net,'dice':dice_net,'rps':rps_net,'slots':slots_net,'roulette_red':roulette_net}
# All listed odds combinations, every integer wager up to the ordinary 500 cap.
best=(-1,None)
for odds in itertools.product([1.5+i/10 for i in range(6)],[2.1+i/10 for i in range(5)],[2.1+i/10 for i in range(5)],[2.6+i/10 for i in range(5)]):
 total=sum(1/o for o in odds)
 for wager in range(1,501):
  for o in odds:
   value=round(wager*o)/(wager*o*total)
   if value>best[0]:best=(value,dict(odds=list(odds),chosen=o,wager=wager))
results['horse_max_expected_return_in_enumerated_standard_odds']={'return':best[0],**best[1]}
results['gold_x2_event_coin_exact_return_per_gold']=1.5
results['xp_loop_theoretical_without_a_server_cadence']='Every valid tavern round awards XP, even when animation is skipped; this is not a duplicate payment.'
(root/'SIMULATION_ANTITRICHE.json').write_text(json.dumps(results,indent=2));print(json.dumps(results))
