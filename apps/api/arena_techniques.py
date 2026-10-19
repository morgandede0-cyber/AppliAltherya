"""Server-owned champion collection and four-slot loadout, Activity only."""
from arena_engine import Fighter, arena_player_skills, CHAMPION_PROFILES
from tower_techniques import TOWER_CATALOG,FLOORS
SLOTS=('light','heavy','ultimate','defend')
# Power scales with the corresponding level-learned base technique.
CATALOG={
 1:dict(id='c1',slot='heavy',name='Lacération',power=24,accuracy=.78,effect='bleed',description='Un impact réussi pose 4 dégâts de saignement.',limit='Moins puissante et moins précise que certaines attaques lourdes ; aucun effet si elle manque.'),
 2:dict(id='c2',slot='defend',name='Forteresse',effect='fortress',description='Réduit de 55 % le prochain impact reçu.',limit='Votre prochaine attaque perd 10 % de puissance.'),
 3:dict(id='c3',slot='light',name='Croc éclair',power=11,accuracy=1.,effect='evade',description='Après l’impact, gagnez 10 points d’esquive temporaire (plafond total 15 %).',limit='Faibles dégâts. L’esquive ne protège pas des attaques rapides, qui touchent toujours.'),
 4:dict(id='c4',slot='light',name='Griffes enchaînées',power=11,accuracy=1.,effect='charge',description='Après l’impact, prépare votre prochaine attaque avec +20 % de puissance.',limit='Faibles dégâts immédiats ; le bonus ne se cumule pas.'),
 5:dict(id='c5',slot='defend',name='Riposte du rempart',effect='counter',description='Garde de 35 %. Un impact bloqué prépare une riposte à +15 %.',limit='Protège moins que la garde normale. Aucun bonus si le champion ne vous touche pas.'),
 6:dict(id='c6',slot='ultimate',name='Chasse Fantôme',power=28,accuracy=.94,effect='pierce',description='Ignore la moitié de la réduction de garde adverse.',limit='Dégâts inférieurs à l’ultime de base contre un adversaire sans garde. Recharge : 2 actions.'),
 7:dict(id='c7',slot='ultimate',name='Exécution rouge',power=28,accuracy=.85,effect='execute',description='+40 % de puissance si la cible a au plus 35 % de ses PV.',limit='Moins précise et moins puissante tant que la cible est en bonne santé. Recharge : 2 actions.'),
 8:dict(id='c8',slot='heavy',name='Fracas du Bastion',power=22,accuracy=.80,effect='shake',description='Un impact ébranle la cible : sa prochaine attaque perd 10 % de puissance.',limit='Dégâts immédiats plus faibles ; aucun affaiblissement en cas de raté.'),
 9:dict(id='c9',slot='defend',name='Pas de l’Ombre',effect='shadow',description='Garde de 25 % et 10 points d’esquive temporaire (plafond total 15 %).',limit='Protection réduite contre les attaques rapides, impossibles à esquiver.'),
 10:dict(id='c10',slot='ultimate',name='Défi du Roi',power=30,accuracy=.88,effect='king',description='+30 % de puissance si vos PV sont au plus à la moitié.',limit='Vous inflige 3 dégâts de saignement au prochain tour, même en cas de raté. Recharge : 2 actions.'),
}
class ArenaFighter(Fighter):
 @property
 def cfg(self):
  cfg=super().cfg
  return {**cfg,'skills':getattr(self,'loadout',cfg['skills'])} if self.class_key=='arena_fighter' else cfg

def setup(c):
 c.execute('CREATE TABLE IF NOT EXISTS activity_ashkar_techniques(user_id INTEGER NOT NULL,floor INTEGER NOT NULL,PRIMARY KEY(user_id,floor))')
 c.execute('CREATE TABLE IF NOT EXISTS activity_arena_migrations(key TEXT PRIMARY KEY)')
 c.execute('CREATE TABLE IF NOT EXISTS activity_arena_techniques(user_id INTEGER NOT NULL,champion INTEGER NOT NULL,PRIMARY KEY(user_id,champion))')
 c.execute('CREATE TABLE IF NOT EXISTS activity_arena_loadout(user_id INTEGER NOT NULL,slot TEXT NOT NULL,technique TEXT NOT NULL,PRIMARY KEY(user_id,slot))')
 c.execute('CREATE TABLE IF NOT EXISTS activity_arena_loadout_version(user_id INTEGER PRIMARY KEY,revision INTEGER NOT NULL DEFAULT 0)')

RESET_KEY='champion_techniques_fresh_start_20261017'

def reset_once(activity):
 """One atomic migration; a restart must never erase newly earned progress."""
 with activity.conn() as c:
  if c.execute('SELECT 1 FROM activity_arena_migrations WHERE key=?',(RESET_KEY,)).fetchone():return False
 from save_safety import backup
 backup(activity.path,force=True)
 with activity.conn() as c:
  c.execute('BEGIN IMMEDIATE')
  if not c.execute('INSERT OR IGNORE INTO activity_arena_migrations VALUES(?)',(RESET_KEY,)).rowcount:return False
  c.execute('UPDATE arena_progress SET champion_wins=0')
  c.execute('UPDATE arena_champion SET last_started_utc=NULL')
  c.execute('DELETE FROM activity_arena_techniques')
  c.execute('DELETE FROM activity_arena_loadout')
  c.execute('UPDATE activity_arena_loadout_version SET revision=revision+1')
 return True

def grant(c,uid,champion):
 if c.execute('INSERT OR IGNORE INTO activity_arena_techniques VALUES(?,?)',(uid,champion)).rowcount:
  return {**CATALOG[champion],'champion':champion,'source':CHAMPION_PROFILES[champion]['name']}
 return None

def grant_tower(c,uid,floor):
 if c.execute('INSERT OR IGNORE INTO activity_ashkar_techniques VALUES(?,?)',(uid,floor)).rowcount:
  return {**TOWER_CATALOG[floor],'floor':floor,'source_kind':'tower','source':FLOORS[floor]['name']}
 return None

def book(c,uid,level,wins):
 c.execute('INSERT OR IGNORE INTO activity_arena_loadout_version(user_id) VALUES(?)',(uid,))
 owned={r[0] for r in c.execute('SELECT champion FROM activity_arena_techniques WHERE user_id=?',(uid,))}
 tower_owned={r[0] for r in c.execute('SELECT floor FROM activity_ashkar_techniques WHERE user_id=?',(uid,))}
 selected=dict(c.execute('SELECT slot,technique FROM activity_arena_loadout WHERE user_id=?',(uid,)))
 base=arena_player_skills(level);skills={k:{**v,'id':'base_'+k} for k,v in base.items()};cards=[]
 entries=[(t,dict(champion=n,source_kind='arena',source=CHAMPION_PROFILES[n]['name'],unlocked=n in owned)) for n,t in CATALOG.items()]
 entries += [(t,dict(floor=n,source_kind='tower',source=FLOORS[n]['name'],unlocked=n in tower_owned)) for n,t in TOWER_CATALOG.items()]
 for t,origin in entries:
  card={**t,**origin,'emoji':base[t['slot']]['emoji']}
  if 'power' in t:card['power']=round(t['power']*base[t['slot']]['power']/arena_player_skills(1)[t['slot']]['power'])
  cards.append(card)
  if card['unlocked'] and selected.get(t['slot'])==t['id']:skills[t['slot']]=card
 return dict(skills=skills,base_skills=base,techniques=cards,loadout_revision=c.execute('SELECT revision FROM activity_arena_loadout_version WHERE user_id=?',(uid,)).fetchone()[0])

def equip(c,uid,level,wins,slot,technique,revision):
 if slot not in SLOTS or not isinstance(technique,str):raise ValueError('Emplacement ou technique invalide.')
 b=book(c,uid,level,wins)
 if type(revision) is not int or revision!=b['loadout_revision']:raise ValueError('Votre équipement a changé. Actualisez le grimoire.')
 if technique!='base_'+slot:
  card=next((t for t in b['techniques'] if t['id']==technique),None)
  if not card or not card['unlocked'] or card['slot']!=slot:raise ValueError('Technique verrouillée ou incompatible avec cet emplacement.')
 if b['skills'][slot]['id']==technique:return 'Cette technique est déjà équipée.'
 c.execute('INSERT INTO activity_arena_loadout VALUES(?,?,?) ON CONFLICT(user_id,slot) DO UPDATE SET technique=excluded.technique',(uid,slot,technique))
 c.execute('UPDATE activity_arena_loadout_version SET revision=revision+1 WHERE user_id=?',(uid,))
 return 'Technique équipée. Votre ancienne technique reste disponible dans le grimoire.'

def resolve(b,action,engine):
 actor,target=b.actor(),b.target();skill=actor.cfg['skills'][action];effect=skill.get('effect');guarded=target.defending;before=target.hp
 # Modifiers are local to this attack; restore the catalog power even on failure.
 old=getattr(actor,'loadout',None);reduction=target.defend_reduction
 if effect in ('execute','king'):
  boost=1.4 if effect=='execute' and target.hp/target.max_hp<=.35 else 1.3 if effect=='king' and actor.hp/actor.max_hp<=.5 else 1.
  actor.loadout={**actor.cfg['skills'],action:{**skill,'power':round(skill['power']*boost)}}
 if effect=='pierce' and guarded:target.defend_reduction*=.5
 try:lines=engine(b,action)
 finally:
  if old is not None:actor.loadout=old
  if target.defending:target.defend_reduction=reduction
 if not actor.alive:return lines
 hit=target.hp<before
 if effect=='fortress':actor.defend_reduction=.55;actor.shaken=True;lines=lines[:-1]+[f"{actor.name} utilise {skill['name']} : garde 55 %, prochaine attaque −10 %."]
 elif effect=='counter':actor.defend_reduction=.35;lines=lines[:-1]+[f"{actor.name} prépare {skill['name']} : garde 35 %, riposte après un impact bloqué."]
 elif effect=='shadow':actor.defend_reduction=.25;actor.temp_evade=.10;lines=lines[:-1]+[f"{actor.name} utilise {skill['name']} : garde 25 %, esquive renforcée."]
 elif hit and effect=='bleed':target.bleed_pending=max(target.bleed_pending,4);lines.append(f"{skill['name']} : saignement de 4 préparé.")
 elif hit and effect=='evade':actor.temp_evade=max(actor.temp_evade,.10);lines.append(f"{skill['name']} : esquive renforcée jusqu’à la prochaine action.")
 elif hit and effect=='charge':actor.next_damage_bonus=max(actor.next_damage_bonus,.20);lines.append(f"{skill['name']} : prochaine attaque +20 %.")
 elif hit and effect=='shake':target.shaken=True;lines.append(f"{skill['name']} : cible ébranlée, prochaine attaque −10 %.")
 if effect=='king':actor.bleed_pending=max(actor.bleed_pending,3);lines.append(f"{skill['name']} : contrecoup de 3 au prochain tour.")
 if guarded and hit and target.cfg['skills']['defend'].get('effect')=='counter':target.counter_ready=True;lines.append('Riposte du rempart : prochaine attaque +15 %.')
 return lines
