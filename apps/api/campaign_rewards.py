"""Modest effort-based rewards, quoted by server and frozen on acceptance.

Gold covers narrative effort and actual delivery value; XP follows objectives,
travel, combat and capped waiting time. No level/price/tutorial changes.
"""
import math
from expedition_engine import EXPEDITIONS,RESOURCE_SELL_PRICES
VERSION='20261023-campaign-effort-v1'

def quote(q):
 season=q['season'];gold={1:6,2:15,3:22,4:30}[season];xp={1:4,2:25,3:40,4:55}[season];wait=0
 for step in q['steps']:
  kind=step['kind']
  if kind=='talk':xp+=2
  elif kind=='explore':gold+=4;xp+=6+2*len(step.get('clues',[]))
  elif kind=='puzzle':gold+=2;xp+=5
  elif kind=='choice':gold+=2;xp+=4
  elif kind in ('mission','inspect'):wait+=step.get('duration',0)
  elif kind=='deliver':gold+=step['quantity']*RESOURCE_SELL_PRICES.get(step['resource'],0)+3;xp+=8
  elif kind=='expedition':
   duration=EXPEDITIONS[step['destination']]['duration'];gold+=min(12,4+math.ceil(duration/3600));xp+=min(25,10+5*math.ceil(duration/3600))
  elif kind=='battle':gold+=12 if step.get('boss') else 8;xp+=30 if step.get('boss') else 20
  elif kind=='port':gold+=14;xp+=30
 minutes=math.ceil(wait/60);gold+=min(10,math.ceil(minutes/15));xp+=min(35,math.ceil(minutes/5))
 if q['id'].endswith('-Q08'):gold+=4;xp+=10
 # Keep the first award familiar and bounded. Waiting never pays linearly forever.
 return dict(gold=min(75,gold),xp=5*math.ceil(xp/5))
