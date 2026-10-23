"""Durable closures, checked in the same transaction as gameplay actions."""
import json,time
VENUES={'global':'Tout le jeu','bank':'Banque','market':'Marché','forge':'Forge de Legacy','khaz':'KHAZ’GORAM','tavern':'Taverne','tavern_games':'Jeux de taverne','story':'Troubadour','castle':'Château','jobs':'Petites annonces','arena':'Arène','techniques':'Grimoire','alley':'Ruelle sombre','guard':'Vigile','thief':'Voleur','robber':'Braqueur','casino':'Salle clandestine','expeditions':'Expéditions','elarwyn':'Forêt d’Elarwyn','vorak':'Mont Vorak','tower':'Tour d’Ashkar','campaign':'Quêtes principales','daily':'Quêtes quotidiennes','world':'Monde','profile':'Profil'}
VENUES['mail']='Boîte aux lettres'
VENUES['trade']='Comptoir des joueurs'
VENUES['port']='Port des Brumes'
VENUES['smogo']='Smogo'
VENUES.update({'blackjack':'Blackjack','roulette':'Roulette','russian':'Roulette russe','slots':'Machines à sous','horses':'Courses de chevaux','dice':'Dés','coin':'Pile ou face','rps':'Pierre feuille ciseaux'})
PARENTS={'tavern_games':'tavern','story':'tavern','guard':'alley','thief':'alley','robber':'alley','casino':'alley','elarwyn':'expeditions','vorak':'expeditions','daily':'castle'}
PARENTS['trade']='market'
PARENTS['port']='campaign'
PARENTS['smogo']='alley'
PARENTS.update({**{k:'casino' for k in ('blackjack','roulette','russian','slots','horses')},**{k:'tavern_games' for k in ('dice','coin','rps')},'khaz':'world','tower':'world','expeditions':'world'})
class Maintenance:
 def __init__(self,a):
  self.a=a
  from campaign import CATALOG
  for p in CATALOG.get('locations',[]):
   if isinstance(p,dict):VENUES.setdefault(p['id'],p.get('name',p['id']));PARENTS[p['id']]='campaign'
  with a.conn() as c:c.execute('CREATE TABLE IF NOT EXISTS activity_maintenance(scope TEXT PRIMARY KEY,message TEXT NOT NULL,until_at REAL NOT NULL DEFAULT 0,actor TEXT NOT NULL,updated_at REAL NOT NULL)')
 def public(self,uid=None):
  with self.a.conn() as c:rows=c.execute('SELECT scope,message,until_at FROM activity_maintenance WHERE until_at=0 OR until_at>?',(time.time(),)).fetchall()
  with self.a.conn() as c:
   lock=c.execute('SELECT message,until_at FROM activity_player_locks WHERE user_id=? AND until_at>?',(uid,time.time())).fetchone() if uid is not None else None
   bulletin=c.execute("SELECT value FROM activity_admin_settings WHERE key='announcement'").fetchone()
  return {'player_lock':dict(lock) if lock else None,'announcement':bulletin[0] if bulletin else '', 'closures':[dict(r) for r in rows],'places':VENUES,'parents':PARENTS}
 def scopes(self,uid,body):
  action=body['action'];key=body.get('key','');scopes=[]
  direct={'deposit':'bank','withdraw':'bank','buy':'market','sell':'market','story_buy':'market','upgrade':'forge','story_unlock':'story','story_read':'story','job_accept':'jobs','job_claim':'jobs','daily':'castle','quests_claim':'daily','drink':'tavern','guard':'guard','larceny':'thief','npc_theft':'thief','crime':'thief','heist_start':'robber','heist_guess':'robber','battle_start':'arena','arena_equip':'techniques'}
  if action.startswith('adventure_'):
   scopes.append({'adventure_daily':'daily','adventure_training':'arena','adventure_favorite':'trade','adventure_goal':'forge','adventure_specialize':'expeditions','adventure_event':'expeditions','adventure_title':'profile'}.get(action,'profile'))
  if action.startswith('smogo_'):scopes.append('smogo')
  if action.startswith('port_'):scopes.append('port')
  if action.startswith('trade_'):scopes.append('trade')
  if action.startswith('mail_'):scopes.append('mail')
  if action in direct:scopes.append(direct[action])
  if action.startswith('tutorial_'):scopes.append('global')
  if action.startswith('khaz_'):scopes.append('khaz')
  if action.startswith('ashkar_'):scopes.append('tower')
  if action.startswith('campaign_'):
   scopes.append('campaign')
   from campaign import effective_quest,QUESTS
   with self.a.conn() as c:
    row=c.execute('SELECT * FROM campaign_progress WHERE user_id=?',(uid,)).fetchone()
    if row and row['quest_index']<len(QUESTS):
     quest=effective_quest(row,json.loads(row['payload']))
     if row['stage']<len(quest['steps']):scopes.append(quest['steps'][row['stage']].get('place_id',''))
     if row['stage']<len(quest['steps']) and quest['steps'][row['stage']]['kind']=='port':scopes.append('port')
   if action=='campaign_enter':scopes.append(body.get('place_id',''))
  if action=='start':
   scopes.append('expeditions');scopes.append('vorak' if key.startswith('vorak') else 'elarwyn')
  if action in ('game_start','game_step','game_cancel','battle_step'):
   if action!='game_start':_,p=self.a.play.read(uid);key=p.get('kind','')
   scopes.append(key)
   scopes.append('arena' if action=='battle_step' or key=='arena' else 'tavern_games' if key in ('dice','coin','rps') else 'casino')
  return scopes
 def check(self,uid,body):
  if self.a.admin.allowed(uid):return
  status=self.public(uid)
  if status['player_lock']:raise ValueError('Compte verrouillé : '+status['player_lock']['message'])
  closures={r['scope']:r for r in status['closures']}
  for scope in ['global',*self.scopes(uid,body)]:
   while scope:
    if scope in closures:raise ValueError('Maintenance · '+VENUES.get(scope,scope)+' : '+closures[scope]['message'])
    scope=PARENTS.get(scope)
