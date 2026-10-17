"""Activity-only champion tactics and a durable, structured combat report.

The campaign, historical bot, wagers and award rules keep their existing engine.
"""
import time
import arena_techniques
from arena_engine import CHAMPION_PROFILES, resolve_action

TACTICS = {
 1: ('Assaut frontal','🐾','#d78c54',['light','heavy','light','ultimate'],'Alternez garde et attaques sûres face à ses coups puissants.'),
 2: ('Rempart patient','🛡','#72a7c0',['defend','light','heavy','light','ultimate','light'],'Sa garde absorbe le prochain impact ; évitez d’y gaspiller votre frappe décisive.'),
 3: ('Danse de la Louve','☾','#b2a8df',['light','defend','light','heavy'],'Sa garde favorise l’esquive. Préparez vos grosses attaques après son mouvement.'),
 4: ('Enchaînement du Fauve','✦','#da9c5c',['light','light','heavy','ultimate'],'Ses deux coups rapides préparent une attaque renforcée.'),
 5: ('Mur et riposte','♜','#9aafc6',['defend','heavy','defend','ultimate'],'Sous 50 % PV, sa première riposte gagne 10 % de puissance.'),
 6: ('Chasse opportuniste','◈','#c6a2cf',['light','heavy','defend','ultimate'],'Elle cherche sa frappe décisive quand vos PV passent sous la moitié.'),
 7: ('Exécution rouge','⚔','#de7b72',['heavy','light','ultimate','heavy'],'Il privilégie les attaques lourdes lorsque vous êtes affaibli.'),
 8: ('Bastion du contre','⬖','#82b5af',['defend','light','defend','heavy'],'Il utilise sa riposte préparée après avoir reçu un coup dans sa garde.'),
 9: ('Rythme de l’Ombre','✧','#a29bcf',['light','heavy','defend','ultimate'],'Elle répond à votre dernière technique : gardes répétées et coups lourds sont surveillés.'),
 10: ('Roi de l’Arène','♛','#e2bb62',['light','defend','heavy','ultimate'],'Sous 50 % PV, le Roi change de rythme et prépare une attaque renforcée de 20 %.'),
}

def champion(level):
 level=max(1,min(10,int(level)));role,emblem,color,pattern,hint=TACTICS[level]
 return dict(level=level,name=CHAMPION_PROFILES[level]['name'],role=role,emblem=emblem,color=color,
             style=CHAMPION_PROFILES[level]['style'],hint=hint,phases=2 if level in (5,10) else 1)

def choose(p,b):
 enemy,player=b.fighters[1],b.fighters[0];level=enemy.champion_level or 1
 pattern=TACTICS[level][3];turn=p.get('round',1)-1
 if level==10 and p.get('phase',1)==2:pattern=['heavy','ultimate','defend','heavy']
 action=pattern[turn%len(pattern)]
 if level==6 and player.hp/player.max_hp<.5 and not enemy.ultimate_cd:action='ultimate'
 if level==7 and player.hp/player.max_hp<.5:action='ultimate' if not enemy.ultimate_cd else 'heavy'
 if level==8 and enemy.counter_ready:action='heavy'
 if level==9:
  if p.get('last_action')=='heavy':action='defend'
  elif p.get('last_action')=='defend':action='ultimate' if not enemy.ultimate_cd else 'light'
 if action=='ultimate' and enemy.ultimate_cd:action='heavy' if level in (4,7,10) else 'light'
 return action

def init(p,b,now=None):
 p.update(champion=champion(b.fighters[1].champion_level),round=1,phase=1,started_at=now or time.time(),
          events=[],sequence=0,combat_stats=[dict(damage=0,hits=0,misses=0,critical=0,guards=0) for _ in range(2)])
 p['enemy_action']=choose(p,b)

def resolve(p,b,action):
 """Resolve one engine action and record actual HP losses, not client estimates."""
 actor=b.current;target=1-actor;before=[f.hp for f in b.fighters];guarded=b.fighters[target].defending
 lines=arena_techniques.resolve(b,action,resolve_action);b.log.extend(lines)
 damage=before[target]-b.fighters[target].hp;bleed=before[actor]-b.fighters[actor].hp
 stat=p['combat_stats'][actor]
 if action=='defend' and b.fighters[actor].alive:stat['guards']+=1
 elif damage:stat['hits']+=1;stat['damage']+=damage
 elif b.fighters[actor].alive:stat['misses']+=1
 critical=any('CRITIQUE' in l for l in lines)
 if critical:stat['critical']+=1
 if bleed:p['combat_stats'][target]['damage']+=bleed
 p['sequence']+=1
 event=dict(id=p['sequence'],round=p['round'],actor=actor,target=target,action=action,
            skill=b.fighters[actor].cfg['skills'][action]['name'],damage=damage,bleed=bleed,
            critical=critical,guarded=guarded,kind='guard' if action=='defend' else 'critical' if critical else 'hit' if damage else 'miss',
            text=' '.join(lines).replace('*',''))
 if bleed and not b.fighters[actor].alive:event.update(kind='bleed',skill='Saignement',action='bleed')
 p['events']=(p['events']+[event])[-60:]

def phase(p,b):
 enemy=b.fighters[1]
 if enemy.champion_level in (5,10) and enemy.alive and enemy.hp/enemy.max_hp<=.5 and p.get('phase',1)==1:
  p['phase']=2;enemy.next_damage_bonus=max(enemy.next_damage_bonus,.2 if enemy.champion_level==10 else .1)
  b.log.append(f"⚑ {enemy.name} entre en seconde phase : sa prochaine attaque est renforcée.")

def public_fighters(b):
 result=[]
 for f in b.fighters:
  statuses=[]
  if f.defending:statuses.append(dict(key='guard',label=f'Garde {round(f.defend_reduction*100)} %'))
  if f.bleed_pending:statuses.append(dict(key='bleed',label=f'Saignement {f.bleed_pending}'))
  if f.shaken:statuses.append(dict(key='shaken',label='Ébranlé'))
  if f.counter_ready:statuses.append(dict(key='counter',label='Riposte prête'))
  if f.next_damage_bonus:statuses.append(dict(key='charge',label=f'Attaque +{round(f.next_damage_bonus*100)} %'))
  if f.temp_evade:statuses.append(dict(key='evade',label='Esquive renforcée'))
  if not f.alive:statuses=[dict(key='defeated',label='Hors combat')]
  result.append(dict(name=f.name,hp=f.hp,max_hp=f.max_hp,ultimate_cd=f.ultimate_cd,statuses=statuses))
 return result
