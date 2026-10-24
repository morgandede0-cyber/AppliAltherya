from tutorial_test_support import tutorial_action
"""Ordered campaign audit. Waits use a virtual clock, not edited quest rows.

The only progression fixture is the exact external XP needed at a level gate.
Gold and materials are earned through actual foraging/sales/expedition actions.
No quest/stage/receipt/HP/loot is injected. Supports both complementary choices.
"""
import json,sys,tempfile
from pathlib import Path
from unittest.mock import patch
sys.path.insert(0,str(Path(__file__).parents[1]))
from activity import Activity
from campaign import QUESTS,effective_quest
from progression import xp_needed_for_level

class Walkthrough:
 def __init__(self,branch):self.branch=branch;self.now=1792756800.;self.rows=[];self.external_xp=0;self.foraging=0;self.travel=0;self.actions=0;self.losses=0
 def call(self,action,**body):
  self.now+=1.1;self.actions+=1;return tutorial_action(self.a,self.uid,dict(action=action,**body))
 def snapshot(self):return self.a.snapshot(self.uid,'Auditeur')
 def state(self):return self.snapshot()['campaign']
 def quest(self):
  with self.a.conn() as c:
   r=self.a.campaign.row(c,self.uid);return effective_quest(r,json.loads(r['payload']))
 def campaign(self,action='campaign_step',**body):
  s=self.state()
  if action not in ('campaign_enter','campaign_world_enter'):
   self.call('campaign_world_enter',scene=s['world']['target']);s=self.state();body['world_token']=s['world']['token']
  return self.call(action,quest_id=s['quest']['id'],revision=s['revision'],**body)
 def port(self,action,key):return self.call('port_'+action,key=key,revision=self.snapshot()['port']['revision'])
 def voyage(self,destination,tool):
  self.call('start',key=destination,tool=tool);run=self.a.expeditions.active_run(self.uid)
  if not run or run.expedition_key!=destination:raise AssertionError('Expédition impossible '+destination)
  self.now=run.ends_at+2;self.snapshot();self.travel+=1
 def fund(self,cost):
  for _ in range(300):
   if self.snapshot()['balance']['wallet']>=cost:return
   self.voyage('elarwyn_foraging','hands');self.foraging+=1
   for name,qty in self.snapshot()['resources'].items():
    if qty:self.call('sell',key=name,amount=qty)
  raise AssertionError('Financement impossible')
 def equipment(self,tool):
  for key in ('bag',tool):
   if not self.snapshot()['owned'][key]:
    self.fund(self.snapshot()['catalog'][key]['price']);self.call('buy',key=key)
    if not self.snapshot()['owned'][key]:raise AssertionError('Achat impossible '+key)
 def combat(self,port=False):
  for attempt in range(50):
   if port:self.port('battle','start')
   else:self.campaign('campaign_battle',key='start')
   for _ in range(120):
    s=self.snapshot();b=s['port']['battle'] if port else s['campaign']['battle']
    if not b:return # Successful campaign combat advances and clears the battle.
    if b['finished']:
     if b['won']:return
     self.losses+=1;self.now+=61;break
    key='ultimate' if not b['ultimate_cd'] else 'heavy'
    if port:self.port('battle',key)
    else:self.campaign('campaign_battle',key=key)
   else:raise AssertionError('Combat sans fin')
  raise AssertionError('Combat non gagné après 50 tentatives : '+self.state()['quest']['id'])
 def investigate_port(self):
  from port import WAREHOUSE,QUAY
  self.port('enter','capitainerie');self.port('talk','captain');self.port('enter','entrepots')
  for key in sorted(WAREHOUSE):self.port('inspect',key)
  self.port('enter','passeur');self.port('talk','ferryman');self.port('enter','quai')
  for key in sorted(QUAY):self.port('inspect',key)
  self.port('choose','guards' if self.branch else 'discreet');self.combat(True);self.port('enter','capitainerie');self.port('talk','captain')
  if not self.snapshot()['port']['complete']:raise AssertionError('Dossier du port incomplet')
 def run(self):
  with tempfile.TemporaryDirectory() as folder,patch('time.time',lambda:self.now):
   self.path=Path(folder)/'journey.sqlite3';self.a=Activity(self.path);(self.uid,_),_=self.a.session('');self.snapshot()
   for n in range(11):self.call('tutorial_next',step=n)
   self.call('tutorial_finish',step=11)
   start=self.now
   for expected in QUESTS:
    state=self.state();q=state['quest'];assert q['id']==expected['id']
    level=q['min_level'];threshold=sum(xp_needed_for_level(k) for k in range(1,level));deficit=max(0,threshold-self.a.castle.profile(self.uid)['xp'])
    if deficit:
     try:self.campaign('campaign_accept')
     except ValueError:pass
     else:raise AssertionError('Palier non protégé')
     self.a.castle.add_xp(self.uid,deficit);self.external_xp+=deficit
    self.campaign('campaign_accept');q=self.quest();row=dict(id=q['id'],title=q['title'],level=self.snapshot()['level'],gold=q['gold'],xp=q['xp'],external_xp=deficit,steps=0,losses_before=self.losses,started=self.now)
    while self.state()['stage']<len(q['steps']):
     step=q['steps'][self.state()['stage']];kind=step['kind'];row['steps']+=1
     if kind in ('inspect','mission'):
      
      if step.get('work_points'):
       for point in step['work_points']:self.campaign('campaign_work',point_id=point['id'])
      else:self.campaign()
      deadline=self.state()['deadline']
      try:self.campaign()
      except ValueError:pass
      else:raise AssertionError('Délai non protégé')
      self.now=deadline+1;self.campaign()
     elif kind in ('talk','collect'):self.campaign()
     elif kind=='explore':
      self.call('campaign_enter',place_id=step['place_id'])
      for clue in step['clues']:self.campaign('campaign_explore',clue_id=clue['id'])
      self.campaign()
     elif kind=='choice':self.campaign(option=self.branch)
     elif kind=='puzzle':
      # Wrong answers must not advance, then the real answer resolves after cooldown.
      old=self.state()['stage'];self.campaign(option=(step['answer']+1)%len(step['options']));assert self.state()['stage']==old;self.now+=61;self.campaign(option=step['answer'])
     elif kind=='deliver':
      self.equipment('axe')
      while self.snapshot()['resources'].get(step['resource'],0)<step['quantity']:self.voyage('elarwyn_1','axe')
      before=self.snapshot()['resources'][step['resource']];self.campaign();assert self.snapshot()['resources'][step['resource']]==before-step['quantity']
     elif kind=='expedition':
      tool='hands' if step['destination']=='elarwyn_foraging' else 'pickaxe'
      if tool!='hands':self.equipment(tool)
      self.voyage(step['destination'],tool);assert self.state()['expedition_ready'];self.campaign()
     elif kind=='port':self.investigate_port();self.campaign()
     elif kind=='battle':self.combat()
     else:raise AssertionError('Objectif non géré '+kind)
    self.call('campaign_world_enter',scene=self.state()['world']['target']);before=self.snapshot();old=self.state();body=dict(action='campaign_claim',quest_id=q['id'],revision=old['revision'],world_token=old['world']['token'],request_id='journey-'+str(self.branch)+'-'+q['id']+'-claim')
    self.a.action(self.uid,body);after=self.snapshot();assert after['balance']['wallet']-before['balance']['wallet']==q['gold'];assert after['stats']['xp']-before['stats']['xp']==q['xp'];self.a.action(self.uid,body);assert self.snapshot()['balance']==after['balance']
    self.a=Activity(self.path);assert self.state()['completed']==len(self.rows)+1
    row['losses']=self.losses-row.pop('losses_before');row['duration_seconds']=round(self.now-row.pop('started'));self.rows.append(row)
   assert self.state()['complete'];assert len(self.rows)==32
   return dict(branch=self.branch,quests=self.rows,gold=sum(r['gold'] for r in self.rows),xp=sum(r['xp'] for r in self.rows),external_xp=self.external_xp,foraging=self.foraging,travel=self.travel,losses=self.losses,actions=self.actions,simulated_seconds=round(self.now-start),method='Virtual clock; external XP fixture only at level gates; actual earned Gold/materials; no stage, HP, receipt or loot injected.')

if __name__=='__main__':
 import argparse
 parser=argparse.ArgumentParser();parser.add_argument('--branch',type=int,choices=(0,1),default=0);parser.add_argument('--output',type=Path,required=True);args=parser.parse_args();result=Walkthrough(args.branch).run();args.output.write_text(json.dumps(result,ensure_ascii=False,indent=2));print(json.dumps({k:v for k,v in result.items() if k!='quests'},ensure_ascii=False))
