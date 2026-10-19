"""Activity game orchestration: source engines, server-owned outcomes, isolated SQLite."""
import json,random,time
from roulette_rules import normalise_bets, winnings
import arena_combat,arena_techniques
from dataclasses import asdict
from casino_engine import CasinoStore,draw_slot,slot_multiplier,roulette_spin,MAX_BET,VIP_MAX_BET,SLOT_SYMBOLS,SLOT_WEIGHTS,SLOT_TRIPLE_MULTIPLIERS
from tavern_engine import TavernGameStore,roll_die,flip_coin,rps_bot,rps_result
from dark_alley import DarkAlleyStore,NPC_THEFT_TARGETS,GUARD_ENTRY_FEE,HEIST_CODE_LENGTH,HEIST_ATTEMPTS
from arena_engine import ArenaStore,Fighter,BattleState,CHAMPION_PROFILES,arena_player_skills
from progression import XP_REWARDS
DRINKS=[('beer','Bière',0),('cider','Cidre',1),('mead','Hydromel',2),('red_wine','Vin rouge',3),('spiced_rum','Rhum épicé',4),('whisky','Whisky des Trois Terres',5)]
HORSES=['Éclair','Cendre','Furie','Minuit']
def total(cards):
 n=sum(11 if c['rank']=='A' else 10 if c['rank'] in ('J','Q','K') else int(c['rank']) for c in cards);aces=sum(c['rank']=='A' for c in cards)
 while n>21 and aces:n-=10;aces-=1
 return n
class Play:
 def __init__(self,activity):
  self.a=activity;path=activity.path
  self.casino=CasinoStore(path);self.tavern=TavernGameStore(path);self.dark=DarkAlleyStore(path);self.arena=ArenaStore(path)
  with self.a.conn() as c:
   arena_techniques.setup(c)
   c.execute('CREATE TABLE IF NOT EXISTS activity_play(user_id INTEGER PRIMARY KEY,revision INTEGER NOT NULL DEFAULT 0,payload TEXT NOT NULL DEFAULT "{}")')
   c.execute('CREATE TABLE IF NOT EXISTS activity_arena_results(battle_id TEXT PRIMARY KEY,user_id INTEGER NOT NULL,payload TEXT NOT NULL,created_at REAL NOT NULL)')
   c.execute('CREATE INDEX IF NOT EXISTS idx_activity_arena_results_user ON activity_arena_results(user_id,created_at DESC)')
   c.execute('CREATE TABLE IF NOT EXISTS activity_horse_odds(user_id INTEGER PRIMARY KEY,payload TEXT NOT NULL)')
  # Interrupted wagers are refunded by the original engines when this worker restarts.
  self.casino.recover_unfinished();self.tavern.recover_unfinished();self.arena.recover_unfinished()
  with self.a.conn() as c:
   rows=c.execute('SELECT user_id,payload FROM activity_play').fetchall()
   for uid,payload in rows:
    p=json.loads(payload)
    if p.get('status')=='active':c.execute('UPDATE activity_play SET revision=revision+1,payload=? WHERE user_id=?',(json.dumps({'status':'refunded','message':'Partie interrompue : mise remboursée au redémarrage.'}),uid))
  arena_techniques.reset_once(self.a)
 def read(self,uid):
  with self.a.conn() as c:
   c.execute('INSERT OR IGNORE INTO activity_play(user_id) VALUES(?)',(uid,));r=c.execute('SELECT revision,payload FROM activity_play WHERE user_id=?',(uid,)).fetchone()
  return r[0],json.loads(r[1])
 def save(self,uid,p):
  with self.a.conn() as c:c.execute('UPDATE activity_play SET revision=revision+1,payload=? WHERE user_id=?',(json.dumps(p),uid))
 def public(self,uid):
  rev,p=self.read(uid);p=dict(p)
  profile=self.a.discord_profile(uid)
  if profile and isinstance(p.get('fighters'),list) and p['fighters']:
   p['fighters']=[{**p['fighters'][0],'name':profile['display_name']},*p['fighters'][1:]]
  p.pop('deck',None);p.pop('danger',None);p.pop('battle',None)
  if p.get('kind')=='russian':p.update(chambers_remaining=max(0,6-p.get('step',0)),cartridges_remaining=1 if p.get('status')=='active' else 0)
  if p.get('kind')=='blackjack' and p.get('status')=='active':p['dealer']=[p['dealer'][0],{'hidden':True}];p['dealer_total']=total([p['dealer'][0]])
  return {**p,'revision':rev}
 def horse_odds(self,uid,renew=False):
  with self.a.conn() as c:
   row=c.execute('SELECT payload FROM activity_horse_odds WHERE user_id=?',(uid,)).fetchone()
   if row and not renew:return json.loads(row[0])
   odds=[round(random.uniform(1.5,2),1),round(random.uniform(2.1,2.5),1),round(random.uniform(2.1,2.5),1),round(random.uniform(2.6,3),1)];random.shuffle(odds)
   c.execute('INSERT INTO activity_horse_odds VALUES(?,?) ON CONFLICT(user_id) DO UPDATE SET payload=excluded.payload',(uid,json.dumps(odds)))
   return odds
 def technique_book(self,uid):
  with self.a.conn() as c:return arena_techniques.book(c,uid,self.a.castle.current_level(uid),self.arena.progress(uid)["champion_wins"])
 def snapshot(self,uid):
  rep=self.tavern.tavern_reputation(uid);dr=self.tavern.drink_status(uid);heist=self.dark.active_heist(uid)
  return dict(play=self.public(uid),tavern={**rep,**dr,'drinks_catalog':[dict(key=k,name=n,required=t,available=rep['tier']>=t) for k,n,t in DRINKS]},alley=dict(reputation=self.dark.criminal_reputation(uid),access=self.dark.clandestine_access_info(uid),vip=self.casino.loyalty(uid)['vip'],fee=GUARD_ENTRY_FEE,invitations=self.dark.invitation_count(uid),larceny_remaining=self.dark.cooldown_remaining(uid,'larceny'),ban_remaining=self.dark.ban_remaining(uid),npc_targets=[dict(key=k,name=v[0]) for k,v in NPC_THEFT_TARGETS.items()],record=self.dark.criminal_record(uid),heist=None if not heist else dict(attempts_left=heist.attempts_left,code_length=HEIST_CODE_LENGTH)),arena={**self.arena.progress(uid),'remaining':self.arena.champion_remaining_seconds(uid),**self.technique_book(uid),'champion':arena_combat.champion(self.arena.progress(uid)['champion_level']),'recent':self.recent(uid)},casino=dict(slots=dict(symbols=[dict(key=k,weight=w,multiplier=SLOT_TRIPLE_MULTIPLIERS[k]) for k,w in zip(SLOT_SYMBOLS,SLOT_WEIGHTS)],two_sevens_multiplier=1),max_bet=VIP_MAX_BET if self.casino.loyalty(uid)['vip'] else MAX_BET,horses=HORSES,odds=self.horse_odds(uid)))
 def finish_casino(self,uid,p,payout,message):
  result=self.casino.settle(p['session'],payout);p.update(status='finished',payout=result.get('payout',payout),message=message)
  if result.get('ok'):
   self.a.castle.record(uid,'casino')
   if p['payout']:self.a.castle.record(uid,'gold_earned',p['payout'])
 def blackjack_finish(self,uid,p):
  player=total(p['player']);dealer=total(p['dealer']);natural=len(p['player'])==2 and player==21;dn=len(p['dealer'])==2 and dealer==21
  if not natural and not dn:
   while player<=21 and dealer<17:p['dealer'].append(p['deck'].pop());dealer=total(p['dealer'])
  if natural and dn:pay=p['wager'];msg='Deux Black Jacks : égalité.'
  elif dn or player>21:pay=0;msg='La maison gagne.'
  elif natural:pay=round(p['wager']*2.5);msg='Black Jack !'
  elif dealer>21 or player>dealer:pay=p['wager']*2;msg='Vous gagnez !'
  elif player==dealer:pay=p['wager'];msg='Égalité : mise rendue.'
  else:pay=0;msg='Le croupier gagne.'
  p.update(player_total=player,dealer_total=dealer);self.finish_casino(uid,p,pay,msg)
 def recent(self,uid):
  with self.a.conn() as c:rows=c.execute('SELECT payload FROM activity_arena_results WHERE user_id=? ORDER BY created_at DESC LIMIT 5',(uid,)).fetchall()
  return [json.loads(r[0]) for r in rows]
 def battle_finish(self,uid,p,b):
  before=self.arena.progress(uid);xp_before=self.a.castle.profile(uid)['xp']
  won=b.winner_index==0;ok,payout=self.arena.finish(b.battle_id,uid if won else None)
  if ok:self.a.castle.record(uid,'combat');self.a.castle.record(uid,'arena_win' if won else 'arena_loss')
  p.update(status='finished',outcome='victory' if won else 'defeat',payout=payout,message='Victoire !' if won else 'Défaite.')
  if ok:
   after=self.arena.progress(uid)
   result=dict(battle_id=b.battle_id,won=won,abandoned=p.get('abandoned',False),champion=p.get('champion') or arena_combat.champion(b.fighters[1].champion_level),
    wager=b.wager,payout=payout,net_gold=payout-b.wager,xp=self.a.castle.profile(uid)['xp']-xp_before,
    rating_before=before['rating'],rating_after=after['rating'],rating_delta=after['rating']-before['rating'],
    wins_before=before['champion_wins'],wins_after=after['champion_wins'],next_champion=arena_combat.champion(after['champion_level']),
    circuit_complete=after['champion_wins']>=10,rounds=p.get('round',max(1,(b.turn_no+1)//2)),
    duration=max(0,int(time.time()-p.get('started_at',time.time()))),stats=p.get('combat_stats',[]),fighters=arena_combat.public_fighters(b),events=p.get('events',[]),logs=b.log[-60:],skills=b.fighters[0].cfg["skills"],hp=b.fighters[0].hp,max_hp=b.fighters[0].max_hp)
   if won:
    with self.a.conn() as c:result['technique_unlocked']=arena_techniques.grant(c,uid,b.fighters[1].champion_level)
   p['result']=result
   with self.a.conn() as c:c.execute('INSERT OR IGNORE INTO activity_arena_results VALUES(?,?,?,?)',(b.battle_id,uid,json.dumps(result),time.time()))
 def battle_public(self,p,b):
  p['skills']=b.fighters[0].cfg['skills'];p['battle']=asdict(b);p['fighters']=arena_combat.public_fighters(b);p['turn']=b.turn_no;p['logs']=b.log[-16:]
  if not b.finished:
   key=p.get('enemy_action','light');p['intent']=dict(key=key,name=b.fighters[1].cfg['skills'][key]['name'])
  else:p.pop('intent',None)
 def action(self,uid,body):
  action=body['action'];key=body.get('key','');rev,p=self.read(uid)
  if action.startswith(('game_','battle_')) and (type(body.get('revision')) is not int or body.get('revision')!=rev):raise ValueError('La partie a changé. Actualisez le menu avant de réessayer.')
  if action=='arena_equip':
   if p.get('kind')=='combat' and p.get('status')=='active':raise ValueError('Terminez votre combat avant de remplacer une technique.')
   with self.a.conn() as c:return arena_techniques.equip(c,uid,self.a.castle.current_level(uid),self.arena.progress(uid)['champion_wins'],body.get('slot'),body.get('technique'),body.get('loadout_revision'))
  if action=='drink':
   drink=next((d for d in DRINKS if d[0]==key),None)
   if not drink or self.tavern.tavern_reputation(uid)['tier']<drink[2]:raise ValueError('Boisson verrouillée.')
   r=self.tavern.drink(uid,key)
   if not r.get('ok'):raise ValueError(r.get('message') or f"Boisson indisponible : {r.get('reason')}, délai {r.get('cooldown_seconds',0)} s.")
   return f"{drink[1]} servi. Réputation : {r['label']} · {r['drunk_state']}."+(' '+r['event']['text'] if r.get('event') else '')
  if action=='guard':
   r=self.dark.enter_clandestine_room(uid,key=='invite')
   if not r.get('ok'):raise ValueError(r['message'])
   return 'Accès à la salle clandestine accordé jusqu’à minuit.'
  if action=='larceny':
   r=self.dark.petty_larceny(uid)
   if not r.get('ok'):raise ValueError(f"Disponible dans {r.get('cooldown',0)} secondes.")
   xp=XP_REWARDS['larceny_success'];self.a.castle.add_xp(uid,xp);return f"Petit larcin réussi : +{r['amount']} Gold et +{xp} XP."
  if action in ('npc_theft','crime'):
   r=self.dark.steal_npc(uid,key) if action=='npc_theft' else self.dark.commit_crime(uid)
   if not r.get('ok'):raise ValueError(r.get('message') or f"Disponible dans {r.get('cooldown',0)} secondes.")
   if r['outcome']=='success':self.a.castle.add_xp(uid,XP_REWARDS['npc_theft_success' if action=='npc_theft' else 'crime_success'])
   return f"Résultat : { {'success':'réussite','fail':'échec','caught':'pris sur le fait'}.get(r['outcome'],r['outcome'])} · {r.get('amount',0)} Gold."
  if action=='heist_start':
   ok,status,h=self.dark.start_heist(uid)
   if not ok:raise ValueError('Rang Criminel requis ou accès temporairement interdit.')
   return f'Combinaison de {HEIST_CODE_LENGTH} chiffres distincts · {h.attempts_left} essais.'
  if action=='heist_guess':
   guess=body.get('guess','')
   if not isinstance(guess,str) or len(guess)!=HEIST_CODE_LENGTH or not guess.isascii() or not guess.isdigit() or len(set(guess))!=len(guess):raise ValueError('Entrez quatre chiffres distincts.')
   r=self.dark.guess_heist(uid,guess)
   if r.get('won'):self.a.castle.add_xp(uid,XP_REWARDS['heist_win']);return f"Braquage réussi : {r['reward']} Gold !"
   return r.get('message') or f"{r['well']} bien placé(s), {r['misplaced']} mal placé(s) · {r['attempts_left']} essais restants."
  if action=='game_cancel':
   if p.get('status')=='active' and p.get('kind')=='combat':raise ValueError('Utilisez Abandonner pour terminer le combat.')
   if p.get('status')=='active':
    (self.tavern if p.get('kind') in ('dice','coin','rps') else self.casino).refund(p['session']);p.update(status='refunded',message='Mise remboursée.');self.save(uid,p)
   return 'Retour aux jeux.'
  if action=='game_start':
   if p.get('status')=='active':raise ValueError('Terminez votre partie en cours.')
   wager=body.get('wager')
   if type(wager) is not int or wager<1:raise ValueError('La mise doit être un entier positif.')
   if key not in ('blackjack','roulette','slots','russian','horses','dice','coin','rps'):raise ValueError('Jeu inconnu.')
   tavern=key in ('dice','coin','rps')
   if not tavern and not self.dark.has_clandestine_access(uid):raise ValueError('Accès à la salle clandestine requis.')
   choice=body.get('choice','')
   if key=='roulette' and 'bets' not in body and choice not in ('red','black','even','odd','low','high','number'):raise ValueError('Pari invalide.')
   if key=='roulette' and 'bets' not in body and choice=='number' and (type(body.get('number')) is not int or not 0<=body['number']<=36):raise ValueError('Numéro entre 0 et 36 requis.')
   if key=='horses' and (type(choice) is not int or not 0<=choice<4):raise ValueError('Choisissez un cheval.')
   if key=='rps' and choice not in ('rock','paper','scissors'):raise ValueError('Choisissez pierre, feuille ou ciseaux.')
   if key=='coin' and choice not in ('pile','face'):raise ValueError('Choisissez pile ou face.')
   roulette_bets=normalise_bets(body['bets'] if 'bets' in body else [dict(type=choice,amount=wager,numbers=[body.get('number')])],wager) if key=='roulette' else None
   if key=='horses' and 'odds' in body and body['odds']!=self.horse_odds(uid):raise ValueError('Les cotes ont changé. Vérifiez les nouvelles cotes avant de miser.')
   r=(self.tavern if tavern else self.casino).start(uid,key,wager)
   if not r.get('ok'):raise ValueError(r['message'])
   p=dict(kind=key,status='active',session=r['session_id'],wager=wager,message='À votre tour.')
   if key=='blackjack':
    deck=[dict(rank=str(rank),suit=suit) for suit in ('♠','♥','♦','♣') for rank in list(range(2,11))+['J','Q','K','A']];random.shuffle(deck);p.update(deck=deck,player=[deck.pop(),deck.pop()],dealer=[deck.pop(),deck.pop()]);p['player_total']=total(p['player'])
    if total(p['player'])==21 or total(p['dealer'])==21:self.blackjack_finish(uid,p)
   elif key=='russian':p.update(danger=random.randint(1,6),step=0,events=[])
   elif key=='slots':
    reels=draw_slot();p['reels']=reels;self.finish_casino(uid,p,wager*slot_multiplier(reels),'Résultat des rouleaux.')
   elif key=='roulette':
    number,color=roulette_spin();p.update(number=number,color=color,choice=choice,bets=roulette_bets);self.finish_casino(uid,p,winnings(roulette_bets,number),f'Numéro {number} · {dict(red="rouge",black="noir",green="vert")[color]}.')
   elif key=='horses':
    # Cotes générées côté serveur, mêmes fourchettes et pondérations que le bot.
    odds=self.horse_odds(uid);winner=random.choices(range(4),weights=[1/max(1.01,o) for o in odds])[0];rng=random.Random(p['session']);order=[winner];remaining=[i for i in range(4) if i!=winner]
    while remaining:
     runner=rng.choices(remaining,weights=[1/max(1.01,odds[i]) for i in remaining])[0];order.append(runner);remaining.remove(runner)
    clock=11.0;finish_times=[0.0]*4
    for runner in order:finish_times[runner]=round(clock,3);clock+=rng.uniform(.28,.58)
    p.update(winner=winner,choice=choice,odds=odds,order=order,finish_times=finish_times);self.finish_casino(uid,p,round(wager*odds[winner]) if winner==choice else 0,f'{HORSES[winner]} remporte la course.');self.horse_odds(uid,renew=True)
   else:
    if key=='dice':player,bot=roll_die(),roll_die();won=player>bot;tie=player==bot
    elif key=='coin':player,bot=choice,flip_coin();won=player==bot;tie=False
    else:player,bot={'rock':'pierre','paper':'feuille','scissors':'ciseaux'}[choice],rps_bot();out=rps_result(player,bot);won=out==1;tie=out==0
    payout=wager if tie else wager*2 if won else 0;r=self.tavern.settle(p['session'],payout);p.update(status='finished',player=player,opponent=bot,payout=r.get('payout',payout),message='Égalité.' if tie else 'Victoire !' if won else 'Défaite.');self.a.castle.record(uid,'tavern_game');self.a.castle.add_xp(uid,XP_REWARDS['tavern_game'])
   self.save(uid,p);return p['message']
  if action=='game_step':
   if p.get('status')!='active' or p.get('kind') not in ('blackjack','russian'):raise ValueError('Aucune manche en cours.')
   if not self.dark.has_clandestine_access(uid):self.casino.refund(p['session']);p.update(status='refunded',message='Accès expiré : mise remboursée.');self.save(uid,p);return p['message']
   if p['kind']=='blackjack':
    if key=='hit':p['player'].append(p['deck'].pop());p['player_total']=total(p['player'])
    elif key=='double':
     if len(p['player'])!=2:raise ValueError('Doubler est disponible uniquement avec deux cartes.')
     self.casino.double_blackjack(p['session'],uid,p['wager']);p['wager']*=2;p['doubled']=True
     p['player'].append(p['deck'].pop());p['player_total']=total(p['player'])
    elif key!='stand':raise ValueError('Action invalide.')
    if key in ('stand','double') or total(p['player'])>=21:self.blackjack_finish(uid,p)
   else:
    if key!='try':raise ValueError('Action invalide.')
    p['step']+=1
    p.setdefault('events',[]).append(dict(chamber=p['step'],actor='player',spent=p['step']==p['danger']))
    if p['step']==p['danger']:self.finish_casino(uid,p,0,'BANG : vous perdez la manche.')
    else:
     p['step']+=1
     p.setdefault('events',[]).append(dict(chamber=p['step'],actor='opponent',spent=p['step']==p['danger']))
     if p['step']==p['danger']:self.finish_casino(uid,p,p['wager']*2,'La hyène perd la manche : vous gagnez !')
     else:p['message']='CLIC. La hyène s’en sort aussi. À votre tour.'
   self.save(uid,p);return p['message']
  if action=='battle_start':
   if p.get('status')=='active':raise ValueError('Terminez votre partie en cours.')
   wager=body.get('wager',0)
   if type(wager) is not int or not 0<=wager<=500:raise ValueError('Mise entre 0 et 500 Gold requise.')
   ok,msg,bid=self.arena.start_champion(uid,wager)
   if not ok:raise ValueError(msg)
   level=self.a.castle.current_level(uid);champ=self.arena.progress(uid)['champion_level'];cfg=CHAMPION_PROFILES[champ]
   with self.a.conn() as c:name=c.execute('SELECT name FROM activity_sessions WHERE user_id=?',(uid,)).fetchone()[0]
   b=BattleState(bid,'champion',wager,[arena_techniques.ArenaFighter(uid,name,'arena_fighter',max_hp=100+10*(level-1),player_level=level),Fighter(None,cfg['name'],cfg['class_key'],champion_level=champ)],0)
   b.fighters[0].loadout=self.technique_book(uid)['skills']
   p=dict(kind='combat',status='active',wager=wager,message='À votre tour.');arena_combat.init(p,b);self.battle_public(p,b);self.save(uid,p);return p['message']
  if action=='battle_step':
   if p.get('kind')!='combat' or p.get('status')!='active':raise ValueError('Aucun combat en cours.')
   if key not in ('light','heavy','ultimate','defend','abandon'):raise ValueError('Technique invalide.')
   raw=p['battle'];fighters=[]
   for f in raw['fighters']:
    fighter=arena_techniques.ArenaFighter(**f);fighter.max_hp=f['max_hp'];fighter.hp=f['hp'];fighters.append(fighter)
   fighters[0].loadout=p.get('skills') or arena_player_skills(fighters[0].player_level)
   raw['fighters']=fighters;b=BattleState(**raw)
   if key=='ultimate' and b.fighters[0].ultimate_cd>0:raise ValueError('Technique en recharge.')
   if 'combat_stats' not in p:
    arena_combat.init(p,b);p['round']=max(1,(b.turn_no+1)//2)
   if key=='abandon':b.finished=True;b.winner_index=1;p['abandoned']=True;b.log.append('Le joueur abandonne.')
   else:
    arena_combat.resolve(p,b,key);arena_combat.phase(p,b)
    if not b.finished:
     b.switch();arena_combat.resolve(p,b,p.get('enemy_action','light'))
    if not b.finished:
     b.switch();p['last_action']=key;p['round']+=1;p['enemy_action']=arena_combat.choose(p,b)
   if b.finished:self.battle_finish(uid,p,b)
   self.battle_public(p,b);self.save(uid,p);return p.get('message','Tour résolu.')
  raise ValueError('Action inconnue.')
