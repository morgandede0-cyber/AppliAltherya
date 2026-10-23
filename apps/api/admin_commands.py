"""Whitelisted operational commands, preview/confirm, atomic receipts and audit."""
import hashlib,json,re,secrets,time
from sqlite_store import atomic
from progression import xp_needed_for_level
from maintenance import VENUES
from campaign import QUESTS
from khaz import CFG
import arena_techniques as techniques

FIELDS={
 'wallet':('Portefeuille','players','wallet_gold',1000000000),'bank':('Banque','players','bank_gold',1000000000),'xp':('Expérience totale','castle_profiles','xp',1000000000),'pouciel':('Pouciels','legacy_wallet','pouciel',1000000000),
 'tavern_rep':('Réputation taverne','tavern_reputation','drinks',1000000),'criminal_rep':('Réputation ruelle','criminal_reputation','successes',1000000),'rating':('Classement arène','arena_progress','rating',1000000),'champions':('Champions vaincus','arena_progress','champion_wins',10),'tower_floor':('Étages validés','ashkar_progress','max_floor',10),
 **{'stat_'+k:(label,'castle_profiles',k,1000000000) for k,label in [('combats','Combats'),('wins','Victoires'),('losses','Défaites'),('expeditions','Expéditions terminées'),('casino_games','Parties casino'),('quests_completed','Quêtes terminées')]},
 **{'crime_'+k:(label,'criminal_record',k,1000000000) for k,label in [('theft_success','Vols réussis'),('theft_fail','Vols ratés'),('crimes_success','Crimes réussis'),('heists_success','Braquages réussis'),('gold_stolen','Gold volé'),('biggest_loot','Plus gros butin'),('caught','Arrestations')]}}

def arg(name,label,kind='integer',**kw):return dict(name=name,label=label,type=kind,**kw)
def options(values):return [{'value':str(k),'label':str(v)} for k,v in values]
def digest(value):return hashlib.sha256(json.dumps(value,sort_keys=True,ensure_ascii=False,separators=(',',':')).encode()).hexdigest()

class AdminCommands:
 def __init__(self,a):
  self.a=a
  with a.conn() as c:
   c.execute('CREATE TABLE IF NOT EXISTS activity_admin_commands(id TEXT PRIMARY KEY,actor TEXT NOT NULL,target TEXT NOT NULL,command TEXT NOT NULL,args TEXT NOT NULL,reason TEXT NOT NULL,before_json TEXT NOT NULL,after_json TEXT NOT NULL,created_at REAL NOT NULL)')
   c.execute('CREATE TABLE IF NOT EXISTS activity_admin_previews(token TEXT PRIMARY KEY,actor TEXT NOT NULL,body TEXT NOT NULL,fingerprint TEXT NOT NULL,expires REAL NOT NULL,result TEXT)')
   c.execute('CREATE TABLE IF NOT EXISTS activity_admin_settings(key TEXT PRIMARY KEY,value TEXT NOT NULL)')
   c.execute('CREATE TABLE IF NOT EXISTS bot_events(event_key TEXT PRIMARY KEY,enabled INTEGER NOT NULL DEFAULT 0,updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,updated_by INTEGER)')
   c.execute('CREATE TABLE IF NOT EXISTS activity_admin_cancelled_expeditions(run_id TEXT PRIMARY KEY)')
   c.execute('CREATE TABLE IF NOT EXISTS activity_player_locks(user_id INTEGER PRIMARY KEY,message TEXT NOT NULL,until_at REAL NOT NULL)')
 def target(self,discord_id):
  if not isinstance(discord_id,str) or not re.fullmatch(r'[0-9]{15,22}',discord_id):raise ValueError('Identifiant Discord invalide.')
  with self.a.conn() as c:r=c.execute('SELECT a.user_id FROM activity_discord_accounts a JOIN activity_tutorial_receipts r ON r.identity_key=(\'discord:\'||a.discord_id) WHERE a.discord_id=? AND r.gold_paid>=100 AND r.xp_paid>=25',(discord_id,)).fetchone()
  if not r:raise ValueError('Joueur absent du registre des tutoriels terminés.')
  return r[0]
 def catalogue(self):
  from expedition_engine import RESOURCE_SELL_PRICES,TOOL_LEVELS,BAG_LEVELS
  from story_engine import ALL_STORY_ITEMS,SEASON_1_TEXTS
  from ashkar import today
  resources=sorted(set(RESOURCE_SELL_PRICES)|set(ALL_STORY_ITEMS))
  commands=[dict(id=k,label=label,group='Économie' if k in ('wallet','bank','xp','pouciel') else 'Progression',scope='player',args=[arg('value','Nouvelle valeur',min=0,max=limit)]) for k,(label,_,_,limit) in FIELDS.items()]
  def add(id,label,group,args,scope='player'):commands.append(dict(id=id,label=label,group=group,scope=scope,args=args))
  add('level','Définir le niveau','Progression',[arg('value','Niveau',min=1,max=100)])
  add('resource','Définir un objet / une ressource','Inventaire',[arg('key','Objet','choice',options=options((n,n) for n in resources)),arg('value','Quantité',min=0,max=1000000)])
  for tool in ('pickaxe','axe','spear','bag'):
   tiers=BAG_LEVELS if tool=='bag' else TOOL_LEVELS
   add('tool_'+tool,'Équiper / retirer '+{'pickaxe':'la pioche','axe':'la hache','spear':'la lance','bag':'le sac'}[tool],'Équipement',[arg('value','Palier (0 = retirer)',min=0,max=max(tiers))])
  add('armor','Définir une armure','Équipement',[arg('key','Emplacement','choice',options=options(CFG['SLOT_LABELS'].items())),arg('branch','Voie','choice',options=options(CFG['BRANCH_LABELS'].items())),arg('tier','Qualité','choice',options=[{'value':'none','label':'Retirer'},*options(CFG['TIER_LABELS'].items())])])
  all_skills=[(x['id'],x['name']) for x in techniques.CATALOG.values()]+[(x['id'],x['name']) for x in techniques.TOWER_CATALOG.values()]
  add('technique','Accorder / retirer une technique','Techniques',[arg('key','Technique','choice',options=options(all_skills)),arg('value','Possession',min=0,max=1)])
  add('loadout_clear','Rétablir les quatre techniques de base','Techniques',[])
  add('story_chapter','Ouvrir / fermer un chapitre du livre','Histoire',[arg('value','Chapitre',min=1,max=max(SEASON_1_TEXTS)),arg('enabled','Débloqué','boolean')])
  add('campaign_position','Repositionner la campagne (sans récompense)','Histoire',[arg('value','Quêtes considérées passées',min=0,max=len(QUESTS))])
  add('campaign_stage','Repositionner l’objectif de la quête','Histoire',[arg('value','Étapes considérées terminées',min=0,max=100)])
  for key,label in [('larceny','Petit larcin'),('ban','Interdiction de ruelle'),('champion','Champion'),('drink','Boissons'),('expedition','Terminer l’expédition et verser son butin'),('job','Mission en cours'),('tower','Quota de tour'),('game','Nouvelle mise')]:
   add('delay_'+key,'Libérer le délai · '+label,'Délais',[])
  add('job_refresh','Renouveler les huit annonces disponibles','Annonces',[])
  add('job_cancel','Annuler le contrat sans paiement','Annonces',[])
  add('expedition_cancel','Annuler l’expédition sans butin ni XP','Expéditions',[])
  add('round_close','Clôturer les combats / parties sans remboursement','Combats',[])
  add('daily_restart','Recommencer les objectifs quotidiens (reçus conservés)','Quêtes quotidiennes',[])
  add('daily_reopen','Autoriser un nouveau bonus quotidien','Quêtes quotidiennes',[])
  add('tutorial_restart','Repasser le tutoriel (sans seconde récompense)','Comptes',[])
  add('sessions_revoke','Déconnecter tous les appareils','Comptes',[])
  add('player_lock','Verrouiller / déverrouiller ce joueur','Comptes',[arg('value','Durée en minutes (0 = déverrouiller)',min=0,max=525600)])
  add('maintenance','Maintenance globale / par lieu','Royaume',[arg('key','Lieu','choice',options=options(VENUES.items())),arg('enabled','Verrouiller','boolean'),arg('value','Durée en minutes (0 = sans limite)',min=0,max=525600)],'game')
  add('event','Activer / arrêter un bonus des moteurs compatibles','Royaume',[arg('key','Bonus','choice',options=options([('gold_x2','Gold x2'),('xp_x2','XP x2')])),arg('enabled','Actif','boolean')],'game')
  add('announcement','Message de service (vide = retirer)','Royaume',[arg('text','Message','text',max=500)],'game')
  add('gift_gold','Distribuer du Gold aux joueurs du registre','Royaume',[arg('value','Gold par joueur',min=1,max=10000)],'game')
  mail_args=[arg('title','Titre du courrier','text',max=80),arg('text','Message au joueur','text',max=500),arg('gold','Gold',min=0,max=10000,default=0),arg('xp','XP',min=0,max=10000,default=0),arg('pouciel','Pouciels',min=0,max=1000,default=0),arg('item','Objet / ressource','choice',options=[{'value':'none','label':'Aucun objet'},*options((n,n) for n in resources)],default='none'),arg('quantity','Quantité d’objets',min=0,max=1000,default=0)]
  add('mail_player','Récompenser un joueur par courrier','Courrier',mail_args)
  add('mail_all','Récompenser tout le registre par courrier','Courrier',mail_args,'game')
  return dict(commands=commands,maintenance=self.a.maintenance.public(),today=today())
 def validate(self,body):
  command=next((x for x in self.catalogue()['commands'] if x['id']==body.get('command')),None)
  if not command:raise ValueError('Commande inconnue.')
  args=body.get('args')
  if not isinstance(args,dict) or set(args)!={a['name'] for a in command['args']}:raise ValueError('Paramètres incomplets ou inattendus.')
  for spec in command['args']:
   value=args[spec['name']];kind=spec['type']
   if kind=='integer' and (type(value) is not int or not spec['min']<=value<=spec['max']):raise ValueError('Valeur hors limites : '+spec['label'])
   if kind=='boolean' and type(value) is not bool:raise ValueError('Choix oui/non requis.')
   if kind=='choice' and (not isinstance(value,str) or value not in {o['value'] for o in spec['options']}):raise ValueError('Choix invalide : '+spec['label'])
   if kind=='text' and (not isinstance(value,str) or len(value)>spec['max']):raise ValueError('Texte invalide.')
  if command['id']=='armor' and args['key'] in CFG['ADVANCED_SLOTS'] and args['tier'] not in ('none','mythique','legendaire'):raise ValueError('Les emplacements avancés commencent au Mythique.')
  if command['id'] in ('mail_player','mail_all'):
   if not args['title'].strip() or not args['text'].strip():raise ValueError('Titre et message obligatoires.')
   if (args['item']=='none') != (args['quantity']==0):raise ValueError('Choisissez un objet et une quantité positive, ou Aucun objet et zéro.')
  reason=body.get('reason')
  if not isinstance(reason,str) or not 3<=len(reason.strip())<=200:raise ValueError('Motif de 3 à 200 caractères requis.')
  uid=self.target(body.get('player')) if command['scope']=='player' else None
  return command,uid
 def state(self,c,uid):
  if uid is None:
   return dict(maintenance=[dict(r) for r in c.execute('SELECT * FROM activity_maintenance ORDER BY scope')],settings=[dict(r) for r in c.execute('SELECT * FROM activity_admin_settings ORDER BY key')],events=[dict(r) for r in c.execute('SELECT * FROM bot_events ORDER BY event_key')],players=[dict(r) for r in c.execute("SELECT a.discord_id,a.user_id,p.wallet_gold FROM activity_discord_accounts a JOIN activity_tutorial_receipts t ON t.identity_key=('discord:'||a.discord_id) JOIN players p ON p.user_id=a.user_id WHERE t.gold_paid>=100 AND t.xp_paid>=25 ORDER BY a.discord_id")])
  # Do not reveal decks, heist codes or session secrets in previews or the audit log.
  tables=['players','castle_profiles','resources','equipment_ownership','expedition_profiles','legacy_wallet','legacy_equipment','tavern_reputation','criminal_reputation','criminal_record','arena_progress','ashkar_progress','activity_arena_techniques','activity_ashkar_techniques','activity_arena_loadout','dark_actions','alley_bans','job_board_state','campaign_progress','tutorial_progress','activity_tutorial_revision','activity_tutorial_steps','activity_player_locks','arena_champion','tavern_drink_limits','clandestine_access','activity_khaz','activity_arena_loadout_version','ashkar_daily','castle_daily_progress','castle_daily_plans','castle_daily_receipts','activity_game_cadence','story_unlocks','story_item_purchases','story_read_progress']
  data={table:[dict(r) for r in c.execute('SELECT * FROM '+table+' WHERE user_id=?',(uid,))] for table in tables}
  for row in data['campaign_progress']:row['payload_hash']=digest(row.pop('payload'))
  for table in ['activity_play','activity_ashkar']:
   data[table]=[{'revision':r['revision'],'state_hash':digest(r['payload'])} for r in c.execute('SELECT revision,payload FROM '+table+' WHERE user_id=?',(uid,))]
  data['pending_expeditions']=[dict(r) for r in c.execute('SELECT run_id,claimed,ends_at FROM expedition_runs WHERE user_id=? AND claimed=0',(uid,))]
  data['session_count']=c.execute('SELECT COUNT(*) FROM activity_sessions WHERE user_id=?',(uid,)).fetchone()[0]
  return data
 def fingerprint(self,c,uid,command=None,state=None):
  value=state if state is not None else self.state(c,uid)
  if command=='mail_player':return digest({'recipient':uid})
  if command=='mail_all':return digest({'recipients':[(r['discord_id'],r['user_id']) for r in value['players']]})
  return digest(value)
 def preview(self,actor,body):
  self.a.admin.require(actor);command,uid=self.validate(body);identity=self.a.discord_profile(actor)['discord_id']
  with atomic(self.a.path) as c:
   c.execute('DELETE FROM activity_admin_previews WHERE expires<?',(time.time()-86400,))
   token=secrets.token_urlsafe(32);before=self.state(c,uid)
   c.execute('INSERT INTO activity_admin_previews VALUES(?,?,?,?,?,NULL)',(token,identity,json.dumps(body,ensure_ascii=False),self.fingerprint(c,uid,command['id'],before),time.time()+300))
  current=(before.get(FIELDS[command['id']][1]) or [{}])[0].get(FIELDS[command['id']][2],0) if command['id'] in FIELDS else None
  return dict(current=current,token=token,label=command['label'],player=body.get('player') if command['scope']=='player' else None,args=body['args'],reason=body['reason'],expires_in=300,affected=len(before.get('players',[])) if uid is None and command['id'] in ('gift_gold','mail_all') else 1,before=before)
 def confirm(self,actor,token):
  self.a.admin.require(actor);identity=self.a.discord_profile(actor)['discord_id']
  if not isinstance(token,str) or len(token)>100:raise ValueError('Confirmation invalide.')
  with atomic(self.a.path) as c:
   row=c.execute('SELECT * FROM activity_admin_previews WHERE token=?',(token,)).fetchone()
   if not row or row['actor']!=identity:raise ValueError('Cette confirmation appartient à un autre administrateur.')
   if row['result']:return json.loads(row['result'])
   if row['expires']<time.time():raise ValueError('Confirmation expirée. Recommencez l’aperçu.')
   body=json.loads(row['body']);command,uid=self.validate(body)
   if self.fingerprint(c,uid,command['id'])!=row['fingerprint']:raise ValueError('Les données ont changé. Recommencez l’aperçu.')
   economy_before=self.a.transaction_journal.capture(c,uid) if uid is not None else None
   before=self.state(c,uid);self.apply(c,uid,command['id'],body['args'],identity,body['reason'],token);after=self.state(c,uid)
   if economy_before is not None:self.a.transaction_journal.record(c,actor,uid,'admin:'+command['id'],'admin:'+token,economy_before)
   target=body.get('player') if command['scope']=='player' else '*'
   c.execute('INSERT INTO activity_admin_commands VALUES(?,?,?,?,?,?,?,?,?)',(token,identity,target,command['id'],json.dumps(body['args'],ensure_ascii=False),body['reason'],json.dumps(before,ensure_ascii=False),json.dumps(after,ensure_ascii=False),time.time()))
   self.a.notifications.admin_event(c,token,identity,target,command['label'],0,1,body['reason'])
   result=dict(message='Commande appliquée et journalisée.',command=command['id']);c.execute('UPDATE activity_admin_previews SET result=? WHERE token=?',(json.dumps(result),token));return result
 def busy(self,c,uid):return self.a.khaz.active(c,uid)
 def apply(self,c,uid,cmd,args,actor,reason,reference=None):
  from ashkar import today
  now=time.time();v=args.get('value');key=args.get('key')
  if cmd in ('mail_player','mail_all'):
   targets=[uid] if uid is not None else [r['user_id'] for r in self.state(c,None)['players']]
   self.a.mailbox.send(c,targets,args,actor,reference);return
  if uid is not None and cmd not in ('round_close','sessions_revoke','player_lock') and self.busy(c,uid):raise ValueError('Clôturez le combat ou la partie avant de modifier ce joueur.')
  if cmd in FIELDS or cmd=='level':
   if cmd=='level':v=sum(xp_needed_for_level(n) for n in range(1,v));cmd='xp'
   _,table,column,_=FIELDS[cmd];c.execute('INSERT OR IGNORE INTO '+table+'(user_id) VALUES(?)',(uid,));old=c.execute('SELECT '+column+' FROM '+table+' WHERE user_id=?',(uid,)).fetchone()[0];c.execute('UPDATE '+table+' SET '+column+'=? WHERE user_id=?',(v,uid))
   if cmd=='xp':
    if v>old:self.a.castle._queue_levelups(c,uid,old,v)
    self.a.castle._sync_level(c,uid)
   return
  if cmd=='resource':
   c.execute('INSERT INTO resources VALUES(?,?,?) ON CONFLICT(user_id,resource_name) DO UPDATE SET quantity=excluded.quantity',(uid,key,v));return
  if cmd.startswith('tool_'):
   tool=cmd[5:];c.execute('UPDATE equipment_ownership SET '+tool+'_owned=? WHERE user_id=?',(int(v>0),uid));c.execute('UPDATE expedition_profiles SET '+tool+'_level=? WHERE user_id=?',(max(1,v),uid));return
  if cmd=='armor':
   if args['tier']=='none':c.execute('DELETE FROM legacy_equipment WHERE user_id=? AND slot=?',(uid,key))
   else:c.execute('INSERT INTO legacy_equipment VALUES(?,?,?,?) ON CONFLICT(user_id,slot) DO UPDATE SET branch=excluded.branch,tier=excluded.tier',(uid,key,args['branch'],args['tier']))
   c.execute('UPDATE activity_khaz SET revision=revision+1 WHERE user_id=?',(uid,));return
  if cmd in ('technique','loadout_clear'):
   if cmd=='loadout_clear':c.execute('DELETE FROM activity_arena_loadout WHERE user_id=?',(uid,))
   else:
    tower=key.startswith('ashkar_');table,column=('activity_ashkar_techniques','floor') if tower else ('activity_arena_techniques','champion');number=next(n for n,x in (techniques.TOWER_CATALOG if tower else techniques.CATALOG).items() if x['id']==key)
    if v:c.execute('INSERT OR IGNORE INTO '+table+' VALUES(?,?)',(uid,number))
    else:c.execute('DELETE FROM '+table+' WHERE user_id=? AND '+column+'=?',(uid,number));c.execute('DELETE FROM activity_arena_loadout WHERE user_id=? AND technique=?',(uid,key))
   c.execute('INSERT INTO activity_arena_loadout_version VALUES(?,1) ON CONFLICT(user_id) DO UPDATE SET revision=revision+1',(uid,));return
  if cmd=='story_chapter':
   if args['enabled']:c.execute('INSERT OR IGNORE INTO story_unlocks VALUES(?,1,?,?)',(uid,v,int(now)))
   else:c.execute('DELETE FROM story_unlocks WHERE user_id=? AND season=1 AND chapter=?',(uid,v))
   return
  if cmd=='campaign_position':c.execute('UPDATE campaign_progress SET quest_index=?,stage=0,accepted_at=NULL,entered_at=0,payload=\'{"admin_replay":true}\',revision=revision+1 WHERE user_id=?',(v,uid));return
  if cmd=='campaign_stage':
   r=c.execute('SELECT * FROM campaign_progress WHERE user_id=?',(uid,)).fetchone()
   if r['quest_index']>=len(QUESTS) or r['accepted_at'] is None:raise ValueError('Une quête doit être acceptée.')
   from campaign import effective_quest
   if v>len(effective_quest(r,json.loads(r['payload']))['steps']):raise ValueError('Étape hors de cette quête.')
   c.execute('UPDATE campaign_progress SET stage=?,payload=?,entered_at=?,revision=revision+1 WHERE user_id=?',(v,json.dumps({k:v for k,v in json.loads(r['payload']).items() if k in ('edition','admin_replay','choices')}),now,uid));return
  if cmd.startswith('delay_'):
   kind=cmd[6:]
   if kind=='larceny':c.execute("DELETE FROM dark_actions WHERE user_id=? AND action_type='larceny'",(uid,))
   elif kind=='ban':c.execute('DELETE FROM alley_bans WHERE user_id=?',(uid,))
   elif kind=='champion':c.execute('UPDATE arena_champion SET last_started_utc=NULL WHERE user_id=?',(uid,))
   elif kind=='drink':c.execute('DELETE FROM tavern_drink_limits WHERE user_id=?',(uid,))
   elif kind=='expedition':
    runs=c.execute('SELECT run_id FROM expedition_runs WHERE user_id=? AND claimed=0',(uid,)).fetchall()
    c.execute('UPDATE expedition_runs SET ends_at=? WHERE user_id=? AND claimed=0',(int(now),uid))
    for run in runs:self.a.expeditions.finalize_run(run[0])
    self.a.reconcile(uid)
   elif kind=='job':c.execute('UPDATE job_board_state SET reward_ready_at=?,next_board_at=0 WHERE user_id=?',(int(now),uid))
   elif kind=='tower':c.execute('UPDATE ashkar_daily SET cleared=0 WHERE user_id=? AND day=?',(uid,today()))
   elif kind=='game':c.execute('DELETE FROM activity_game_cadence WHERE user_id=?',(uid,))
   return
  if cmd=='job_refresh':
   row=c.execute('SELECT pending_job_json FROM job_board_state WHERE user_id=?',(uid,)).fetchone()
   if row and row[0]:raise ValueError('Un contrat est déjà en cours.')
   c.execute("UPDATE job_board_state SET batch_id='',jobs_json='[]',next_board_at=0 WHERE user_id=?",(uid,));return
  if cmd=='job_cancel':c.execute("UPDATE job_board_state SET batch_id='',jobs_json='[]',pending_job_json='',reward_ready_at=0,next_board_at=0 WHERE user_id=?",(uid,));return
  if cmd=='expedition_cancel':
   for r in c.execute('SELECT run_id FROM expedition_runs WHERE user_id=? AND claimed=0',(uid,)).fetchall():
    c.execute('INSERT OR IGNORE INTO activity_admin_cancelled_expeditions VALUES(?)',(r[0],));c.execute('INSERT OR IGNORE INTO activity_rewards VALUES(?)',('expedition:'+r[0],));c.execute('UPDATE expedition_runs SET claimed=1,loot_json=\'{}\' WHERE run_id=?',(r[0],))
   return
  if cmd=='round_close':
   rev,p=self.a.play.read(uid)
   if p.get('status')=='active':
    if p.get('kind')=='combat':self.a.play.action(uid,dict(action='battle_step',key='abandon',revision=rev))
    else:self.a.play.finish_casino(uid,p,0,'Partie clôturée par un administrateur.');self.a.play.save(uid,p)
   if self.a.tower.active_in(c,uid):
    row=c.execute('SELECT revision FROM activity_ashkar WHERE user_id=?',(uid,)).fetchone();self.a.tower.action(uid,dict(action='ashkar_step',key='abandon',revision=row[0]))
   row=c.execute('SELECT * FROM campaign_progress WHERE user_id=?',(uid,)).fetchone();p=json.loads(row['payload'])
   if p.get('battle') and not p['battle']['finished']:
    p['battle']['finished']=True;p['battle']['winner_index']=1;p['retry_at']=now+60;c.execute('UPDATE campaign_progress SET payload=?,revision=revision+1 WHERE user_id=?',(json.dumps(p),uid))
   return
  if cmd=='daily_restart':
   day=self.a.castle._today()
   if c.execute('SELECT 1 FROM castle_daily_progress WHERE user_id=? AND day=? AND claimed=1',(uid,day)).fetchone():raise ValueError('Les quotidiennes ont déjà été payées : reçus conservés.')
   c.execute('DELETE FROM castle_daily_progress WHERE user_id=? AND day=?',(uid,day));c.execute('DELETE FROM castle_daily_plans WHERE user_id=? AND day=?',(uid,day));return
  if cmd=='daily_reopen':c.execute('UPDATE castle_profiles SET last_daily=NULL WHERE user_id=?',(uid,));c.execute('DELETE FROM castle_daily_receipts WHERE user_id=? AND day=?',(uid,self.a.castle._today()));return
  if cmd=='tutorial_restart':c.execute('UPDATE activity_tutorial_revision SET finished=0 WHERE user_id=?',(uid,));c.execute('UPDATE activity_tutorial_steps SET step=0,replay=0 WHERE user_id=?',(uid,));return
  if cmd=='sessions_revoke':
   c.execute('DELETE FROM activity_session_expiry WHERE token IN (SELECT token FROM activity_sessions WHERE user_id=?)',(uid,));c.execute('DELETE FROM activity_sessions WHERE user_id=?',(uid,));return
  if cmd=='player_lock':
   if not v:c.execute('DELETE FROM activity_player_locks WHERE user_id=?',(uid,))
   else:c.execute('INSERT INTO activity_player_locks VALUES(?,?,?) ON CONFLICT(user_id) DO UPDATE SET message=excluded.message,until_at=excluded.until_at',(uid,reason,now+v*60))
   return
  if cmd=='maintenance':
   if args['enabled']:c.execute('INSERT INTO activity_maintenance VALUES(?,?,?,?,?) ON CONFLICT(scope) DO UPDATE SET message=excluded.message,until_at=excluded.until_at,actor=excluded.actor,updated_at=excluded.updated_at',(key,reason,now+v*60 if v else 0,actor,now))
   else:c.execute('DELETE FROM activity_maintenance WHERE scope=?',(key,))
   return
  if cmd=='event':c.execute('INSERT INTO bot_events(event_key,enabled,updated_by) VALUES(?,?,?) ON CONFLICT(event_key) DO UPDATE SET enabled=excluded.enabled,updated_at=CURRENT_TIMESTAMP,updated_by=excluded.updated_by',(key,int(args['enabled']),int(actor)));return
  if cmd=='announcement':c.execute("INSERT INTO activity_admin_settings VALUES('announcement',?) ON CONFLICT(key) DO UPDATE SET value=excluded.value",(args['text'],));return
  if cmd=='gift_gold':
   for r in self.state(c,None)['players']:
    if r['wallet_gold']+v>1000000000:raise ValueError('Un solde dépasserait le plafond.')
    c.execute('UPDATE players SET wallet_gold=wallet_gold+? WHERE user_id=?',(v,r['user_id']))
   return
  raise ValueError('Commande non implémentée.')
 def cancel(self,actor,token):
  self.a.admin.require(actor);identity=self.a.discord_profile(actor)['discord_id']
  if not isinstance(token,str):raise ValueError('Confirmation invalide.')
  with self.a.conn() as c:c.execute('DELETE FROM activity_admin_previews WHERE token=? AND actor=? AND result IS NULL',(token,identity))
  return dict(message='Commande annulée.')
 def history(self):
  with self.a.conn() as c:rows=c.execute('SELECT id,actor,target,command,args,reason,created_at FROM activity_admin_commands ORDER BY created_at DESC LIMIT 100').fetchall()
  return {'entries':[dict(r) for r in rows]}
