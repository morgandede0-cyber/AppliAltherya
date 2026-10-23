"""Tower fights use the same fighters, tactics, effects and reports as the arena."""
import time,uuid,math
from dataclasses import asdict
from arena_engine import BattleState,arena_player_skills
from arena_techniques import ArenaFighter
from tower_techniques import FLOORS,TOWER_CATALOG
import arena_combat
class TowerFighter(ArenaFighter):
 @property
 def cfg(self):
  cfg=super().cfg
  return {**cfg,'skills':self.loadout} if hasattr(self,'loadout') else cfg
CLASSES={1:'traqueur',2:'ravageur',3:'traqueur',4:'gardien',5:'gardien',6:'ravageur',7:'gardien',8:'gardien',9:'traqueur',10:'ravageur'}
def opponent(floor):
 data=arena_combat.champion(floor)
 return {**data,'name':FLOORS[floor]['name'],'role':('Gardien final · ' if floor==10 else 'Gardien · ')+data['role'],'style':TOWER_CATALOG.get(floor,{}).get('description',data['style'])}
def create(uid,name,level,gear,floor,skills,legacy=None):
 player=TowerFighter(uid,name,'arena_fighter',max_hp=100+10*(level-1),player_level=level,**gear);player.loadout=skills
 # Fixed tower HP are expressed in the arena's damage scale (six times smaller).
 hp=round(FLOORS[floor]['hp']/6);enemy=TowerFighter(None,FLOORS[floor]['name'],CLASSES[floor],max_hp=hp,champion_level=floor);enemy.max_hp=enemy.hp=hp
 t=TOWER_CATALOG.get(floor);enemy.loadout=dict(enemy.cfg['skills'])
 if t:
  skill={**t,'emoji':enemy.cfg['skills'][t['slot']]['emoji']}
  if 'power' in t:skill['power']=round(t['power']*enemy.cfg['skills'][t['slot']]['power']/arena_player_skills(1)[t['slot']]['power'])
  enemy.loadout={**enemy.cfg['skills'],t['slot']:skill}
 battle=BattleState(uuid.uuid4().hex,'tower',0,[player,enemy],0);battle.log.append('Le combat commence.');p=dict(engine=2,status='active',floor=floor,turn=0,logs=['Le combat commence.'],skills=skills,enemy_skills=enemy.loadout)
 arena_combat.init(p,battle);p['champion']=opponent(floor)
 if legacy:
  player.hp=max(1,math.ceil(legacy['player_hp']/legacy['player_max_hp']*player.max_hp));enemy.hp=max(1,math.ceil(legacy['enemy_hp']/legacy['enemy_max_hp']*enemy.max_hp));player.ultimate_cd=legacy.get('ultimate_cd',0)
 sync(p,battle);return p

def restore(p):
 raw=p['arena_battle'];fighters=[]
 for row in raw['fighters']:
  fighter=TowerFighter(**row);fighter.hp=row['hp'];fighter.max_hp=row['max_hp'];fighters.append(fighter)
 fighters[0].loadout=p['skills'];fighters[1].loadout=p['enemy_skills'];return BattleState(**{**raw,'fighters':fighters})

def sync(p,b):
 p['arena_battle']=asdict(b);p['fighters']=arena_combat.public_fighters(b);p['logs']=b.log[-24:];p['turn']=max(0,(b.turn_no-1)//2)
 p['intent']=arena_combat.tactical_readout(p,b)
 player,enemy=b.fighters
 p['battle']=dict(floor=p['floor'],player_name=player.name,player_level=player.player_level,player_hp=player.hp,player_max_hp=player.max_hp,enemy_hp=enemy.hp,enemy_max_hp=enemy.max_hp,ultimate_cd=player.ultimate_cd,enemy_enraged=p.get('phase')==2)

def step(p,key):
 b=restore(p)
 if key=='ultimate' and b.fighters[0].ultimate_cd:raise ValueError('Technique encore en recharge.')
 if key=='abandon':b.finished=True;b.winner_index=1;p['abandoned']=True;b.log.append('Vous vous repliez. Vos étages validés restent acquis.')
 else:
  arena_combat.resolve(p,b,key);arena_combat.phase(p,b)
  if not b.finished:b.switch();arena_combat.resolve(p,b,p.get('enemy_action','light'))
  if not b.finished:b.switch();p['last_action']=key;p['round']+=1;p['enemy_action']=arena_combat.choose(p,b)
 sync(p,b);return b.finished,b.winner_index==0

def report(p,reward,progress):
 b=restore(p);player=b.fighters[0];next_floor=min(10,progress+1)
 p['combat_result']=dict(analysis=arena_combat.debrief(p),battle_id=b.battle_id,won=reward['won'],abandoned=p.get('abandoned',False),champion=p['champion'],next_champion=opponent(next_floor),wager=0,payout=reward['gold'],net_gold=reward['gold'],xp=reward['xp'],pouciel=reward['pouciel'],rating_delta=0,rating_before=0,rating_after=0,wins_before=progress if p.get('replay') or not reward['won'] else progress-1,wins_after=progress,circuit_complete=progress>=10,rounds=p['round'],duration=max(0,int(time.time()-p['started_at'])),hp=player.hp,max_hp=player.max_hp,stats=p['combat_stats'],events=p['events'],logs=p['logs'],skills=p['skills'],fighters=p['fighters'],technique_unlocked=reward.get('technique_unlocked'))

def public(p,revision):
 if p.get('engine')!=2:return None
 return dict(kind='combat',status='active' if p['status']=='active' else 'finished',revision=revision,champion=p['champion'],round=p['round'],phase=p['phase'],events=p['events'],combat_stats=p['combat_stats'],intent=p['intent'],fighters=p['fighters'],logs=p['logs'],skills=p['skills'],wager=0,result=p.get('combat_result'),message='Victoire !' if p['status']=='won' else 'Défaite' if p['status']=='lost' else 'À votre tour.')
