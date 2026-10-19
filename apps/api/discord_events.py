"""Persistent Activity notifications. No browser-provided balances or identities."""
import asyncio
import hashlib
import json
import logging
import os
import time
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
from aiohttp import ClientSession, ClientTimeout, ClientError

LOG = logging.getLogger('altherya.discord_events')
CHANNELS = {'gazette': '1551927433475788880', 'hall': '1551927559925538957', 'logs': '1551928091046314117'}
LABELS = {'ashkar_start':'Tour d’Ashkar · Combat lancé','ashkar_step':'Tour d’Ashkar','daily':'Récompense quotidienne','deposit':'Dépôt bancaire','withdraw':'Retrait bancaire',
 'buy':'Achat','sell':'Vente','story_buy':'Objet de chapitre acheté','story_unlock':'Chapitre débloqué',
 'job_accept':'Contrat accepté','job_claim':'Contrat terminé','upgrade':'Forge','quests_claim':'Quêtes quotidiennes',
 'start':'Expédition lancée','drink':'Taverne','guard':'Salle clandestine','larceny':'Petit larcin',
 'npc_theft':'Vol','crime':'Méfait','heist_start':'Braquage planifié','heist_guess':'Braquage',
 'game_start':'Jeu','game_step':'Jeu','game_cancel':'Partie remboursée',
 'battle_start':'Combat lancé','battle_step':'Combat','tutorial_finish':'Tutoriel terminé'}

def safe(value):
    # Prevent player names/reasons from injecting formatting or mentions.
    return str(value).replace('@','＠').replace('`',"'").replace('*','').replace('_',' ').replace('~','').replace('|','').replace('\\','/').replace('\n',' ')[:220]

class DiscordEvents:
    def __init__(self, activity):
        self.a = activity
        with activity.conn() as c:
            c.executescript('''
            CREATE TABLE IF NOT EXISTS activity_discord_outbox(
              event_key TEXT PRIMARY KEY, channel TEXT NOT NULL, payload TEXT NOT NULL,
              created REAL NOT NULL, ready REAL NOT NULL DEFAULT 0, attempts INTEGER NOT NULL DEFAULT 0,
              sent REAL, message_id TEXT, last_error TEXT, lease_until REAL NOT NULL DEFAULT 0);
            CREATE INDEX IF NOT EXISTS activity_discord_outbox_due ON activity_discord_outbox(sent,ready);
            CREATE TABLE IF NOT EXISTS activity_discord_observed(user_id INTEGER PRIMARY KEY,payload TEXT NOT NULL,sequence INTEGER NOT NULL DEFAULT 0);
            CREATE TABLE IF NOT EXISTS activity_discord_game_results(
              event_key TEXT PRIMARY KEY,discord_id TEXT NOT NULL,name TEXT NOT NULL,net INTEGER NOT NULL,created REAL NOT NULL);
            CREATE TABLE IF NOT EXISTS activity_discord_meta(key TEXT PRIMARY KEY,value TEXT NOT NULL);
            CREATE TABLE IF NOT EXISTS activity_discord_backoff(scope TEXT PRIMARY KEY,until_at REAL NOT NULL);
            ''')
            c.execute('INSERT OR IGNORE INTO activity_discord_meta VALUES(?,?)', ('installed',str(time.time())))

    def enqueue(self, c, key, channel, title, description):
        embed = dict(title=title[:256], description=description[:3900], color=0xD6A84B,
                     timestamp=datetime.now(ZoneInfo('UTC')).isoformat(), footer={'text':'Altherya • Activity'})
        nonce = str(int(hashlib.sha256(key.encode()).hexdigest()[:15],16))
        payload = dict(embeds=[embed], allowed_mentions={'parse':[]}, nonce=nonce, enforce_nonce=True)
        c.execute('INSERT OR IGNORE INTO activity_discord_outbox(event_key,channel,payload,created) VALUES(?,?,?,?)',
                  (key,channel,json.dumps(payload,ensure_ascii=False),time.time()))

    @staticmethod
    def watched(s):
        return {k:s[k] for k in ('balance','level','gear','resources','owned','owned_story_items') } | {
          'ashkar':{k:v for k,v in s.get('ashkar',{}).items() if k in ('status','progress','floor')}, 'pouciel':s.get('khaz',{}).get('pouciel',0), 'xp':s['stats']['xp'], 'tutorial':s['tutorial']['completed'], 'play':{k:v for k,v in s['play'].items() if k in ('kind','status','session','outcome','payout','wager','revision')},
          'active':None if not s['active'] else [s['active']['name'],s['active']['ends_at']], 'expeditions':s['stats'].get('expeditions',0), 'pending':s['pending'],
          'chapters':[(r['chapter'],r.get('unlocked'),r.get('read')) for r in s['chapters']],
          'tavern':s['tavern'].get('drinks'), 'alley':s['alley']['record'], 'access':{k:v for k,v in s['alley']['access'].items() if k!='seconds_left'}, 'heist':s['alley']['heist']}

    def observe(self, uid, state, action=None, message=''):
        profile = self.a.discord_profile(uid)
        if not profile:return
        encoded=json.dumps(self.watched(state),sort_keys=True,ensure_ascii=False); current=json.loads(encoded)
        player=safe(profile['display_name']); did=profile['discord_id']; who=f'**{player}** · `{did}`'
        with self.a.conn() as c:
            c.execute('BEGIN IMMEDIATE')
            row=c.execute('SELECT payload,sequence FROM activity_discord_observed WHERE user_id=?',(uid,)).fetchone()
            old=json.loads(row[0]) if row else None
            if row and row['payload']==encoded:return
            seq=(row['sequence']+1) if row else 0
            c.execute('INSERT INTO activity_discord_observed VALUES(?,?,?) ON CONFLICT(user_id) DO UPDATE SET payload=excluded.payload,sequence=excluded.sequence',(uid,encoded,seq))
            if old is None:return  # Never announce historical balances as new earnings.
            key=f'state:{uid}:{seq}'
            delta={k:current['balance'][k]-old['balance'][k] for k in ('wallet','bank')}
            xp=current['xp']-old['xp']
            changed=any(current[k]!=old.get(k) for k in current if k!='play')
            p=state['play'];previous=old.get('play',{})
            transitioned=p.get('status')!=previous.get('status') or p.get('session')!=previous.get('session')
            if (changed or transitioned) and (action in LABELS or not action):
                title=LABELS.get(action,'Progression actualisée')
                details=f'{who}\n{safe(message) if action else "Mise à jour enregistrée par le serveur."}'
                details+=f'\nPoche : {delta["wallet"]:+d} Gold · Banque : {delta["bank"]:+d} Gold · XP : {xp:+d}'
                self.enqueue(c,key,'logs',title,details)
            if current.get('ashkar',{}).get('progress',0)>=10 and old.get('ashkar',{}).get('progress',0)<10:
                self.enqueue(c,key+':ashkar','hall','Tour d’Ashkar conquise',f'{who}\nLes dix étages et Varkhaz sont vaincus.')
            if not old['tutorial'] and current['tutorial']:
                self.enqueue(c,key+':welcome','hall','📜 Bienvenue dans Legacy',f'{who}\nTutoriel terminé — bienvenue dans le royaume !')
            if current['level']>old['level']:
                self.enqueue(c,key+':level','hall','⭐ Nouveau niveau',f'{who}\nAtteint le **niveau {current["level"]}** !')
            if current['expeditions']>old['expeditions']:
                self.enqueue(c,key+':expedition','logs','🧭 Expédition terminée',f'{who}\nRessources et XP récupérés dans le sac.')
            if p.get('status')=='finished' and p.get('revision')!=previous.get('revision'):
                # One result per immutable engine session/battle, not per HTTP retry.
                session=p.get('session') or state['play'].get('battle_id') or f'{uid}:{p["revision"]}'
                result_key='result:'+str(uid)+':'+str(session)
                if p.get('kind')=='combat':
                    if p.get('outcome')=='victory':self.enqueue(c,result_key,'hall','⚔️ Victoire dans l’arène',f'{who}\n{safe(p.get("message","Victoire"))}\nRécompense : {p.get("payout",0)} Gold.')
                else:
                    net=int(p.get('payout',0))-int(p.get('wager',0))
                    c.execute('INSERT OR IGNORE INTO activity_discord_game_results VALUES(?,?,?,?,?)',(result_key,did,profile['display_name'],net,time.time()))
                    self.enqueue(c,result_key,'logs','🎲 Résultat — '+safe(p.get('kind','jeu')),f'{who}\n{safe(p.get("message",""))}\nMise : {p.get("wager",0)} Gold · Versement : {p.get("payout",0)} Gold · **Bilan : {net:+d} Gold**')
                    if net>0:self.enqueue(c,result_key+':hall','hall','🏆 Gain aux jeux',f'{who}\n{safe(p.get("kind","Jeu"))} : **{net:+d} Gold nets**.')

    def admin_event(self,c,rid,actor,target,field,before,after,reason):
        def name(did):
            r=c.execute('SELECT d.display_name FROM activity_discord_accounts a JOIN activity_discord d ON d.user_id=a.user_id WHERE a.discord_id=?',(did,)).fetchone()
            return safe(r[0]) if r else 'Joueur'
        self.enqueue(c,'admin:'+rid,'logs','🛡️ Modification administrateur',
          f'**{name(actor)}** (`{actor}`) → **{name(target)}** (`{target}`)\n{safe(field)} : {before} → {after}\nMotif : {safe(reason)}')

    def gazette(self, now=None):
        now=now or datetime.now(ZoneInfo('Europe/Paris'))
        now=now.astimezone(ZoneInfo('Europe/Paris'))
        if now.hour<9:return
        day=now.date();start=datetime.combine(day-timedelta(days=1),datetime.min.time(),tzinfo=now.tzinfo).timestamp()
        end=datetime.combine(day,datetime.min.time(),tzinfo=now.tzinfo).timestamp()
        with self.a.conn() as c:
            installed=float(c.execute('SELECT value FROM activity_discord_meta WHERE key="installed"').fetchone()[0])
            # First edition is the next morning; no misleading empty retrospective on install.
            if installed>=end:return
            key='gazette:'+day.isoformat()
            if c.execute('SELECT 1 FROM activity_discord_outbox WHERE event_key=?',(key,)).fetchone():return
            rows=c.execute('SELECT r.discord_id,COALESCE((SELECT d.display_name FROM activity_discord_accounts a JOIN activity_discord d ON d.user_id=a.user_id WHERE a.discord_id=r.discord_id),MAX(r.name)) name,SUM(r.net) net,COUNT(*) games FROM activity_discord_game_results r WHERE r.created>=? AND r.created<? GROUP BY r.discord_id ORDER BY net DESC',(start,end)).fetchall()
            top=c.execute('SELECT d.display_name,p.wallet_gold+p.bank_gold total FROM activity_discord_accounts a JOIN activity_discord d ON d.user_id=a.user_id JOIN players p ON p.user_id=a.user_id JOIN activity_tutorial_revision t ON t.user_id=a.user_id WHERE t.finished=1 ORDER BY total DESC LIMIT 1').fetchone()
            lines=[f'**Édition du {day.strftime("%d/%m/%Y")}**',f'Bilan des jeux du {(day-timedelta(days=1)).strftime("%d/%m/%Y")} (heure de Paris).']
            if top:lines.append(f'👑 Plus grande fortune actuelle : **{safe(top["display_name"])}** — {top["total"]} Gold.')
            if rows:
                winner=rows[0];loser=rows[-1]
                if winner['net']>0:lines.append(f'🏆 Plus gros gagnant : **{safe(winner["name"])}**, {winner["net"]:+d} Gold nets.')
                if loser['net']<0:lines.append(f'🎭 **{safe(loser["name"])}** laisse {abs(loser["net"])} Gold aux tables. La chance avait manifestement pris sa journée !')
                lines.append(f'🎲 {sum(r["games"] for r in rows)} parties terminées.')
            else:lines.append('Les tables ont été calmes : aucune partie terminée sur cette période.')
            milestones=c.execute('SELECT payload FROM activity_discord_outbox WHERE channel="hall" AND created>=? AND created<? ORDER BY created DESC LIMIT 4',(start,end)).fetchall()
            for r in milestones:
                e=json.loads(r[0])['embeds'][0];lines.append(f'• {e["title"]} — {e["description"].splitlines()[0]}')
            # Discord spoiler keeps the article collapsed until clicked, without requiring a gateway bot.
            self.enqueue(c,key,'gazette','📰 La Gazette d’Altherya','Cliquez sur le texte masqué pour lire l’article.\n\n||'+'\n\n'.join(lines)[:3500]+'||')

    async def deliver_one(self, session, token, now=None):
        now=time.time() if now is None else now
        with self.a.conn() as c:
            c.execute('BEGIN IMMEDIATE')
            token_scope='token:'+hashlib.sha256(token.encode()).hexdigest()
            if c.execute('SELECT 1 FROM activity_discord_backoff WHERE scope IN (?,?) AND until_at>?',('global',token_scope,now)).fetchone():return False
            row=c.execute("SELECT o.* FROM activity_discord_outbox o WHERE sent IS NULL AND ready<=? AND lease_until<=? AND NOT EXISTS(SELECT 1 FROM activity_discord_backoff b WHERE b.scope=('channel:'||o.channel) AND b.until_at>?) ORDER BY created,o.rowid LIMIT 1",(now,now,now)).fetchone()
            if not row:return False
            c.execute('UPDATE activity_discord_outbox SET lease_until=? WHERE event_key=?',(now+60,row['event_key']))
        channel=os.getenv('ALTHERYA_'+row['channel'].upper()+'_CHANNEL_ID',CHANNELS[row['channel']]).strip()
        status=0;wait=5;error='réseau indisponible';message_id=None;pause=0.6
        if not channel.isdigit():status=400;error='ID de salon invalide'
        else:
            try:
                async with session.post(f'https://discord.com/api/v10/channels/{channel}/messages',json=json.loads(row['payload']),headers={'Authorization':'Bot '+token},allow_redirects=False) as response:
                    status=response.status
                    if status==200 or status==201:
                        data=await response.json();message_id=str(data['id'])
                        if response.headers.get('X-RateLimit-Remaining')=='0':pause=max(0.6,float(response.headers.get('X-RateLimit-Reset-After',1)))
                    elif status==429:
                        data=await response.json();wait=max(1,min(float(data.get('retry_after',5)),86400));error='limite Discord'
                    else:error=f'Discord HTTP {status}'
            except (ClientError,asyncio.TimeoutError,ValueError,KeyError):pass
        with self.a.conn() as c:
            if message_id:c.execute('UPDATE activity_discord_outbox SET sent=?,message_id=?,lease_until=0,last_error=NULL WHERE event_key=?',(time.time(),message_id,row['event_key']))
            else:
                if status!=429:wait=3600 if status in (400,401,403,404) else min(300,5*2**min(row['attempts'],6))
                c.execute('UPDATE activity_discord_outbox SET attempts=attempts+1,ready=?,lease_until=0,last_error=? WHERE event_key=?',(now+wait,error,row['event_key']))
                scope='global' if status==429 else token_scope if status==401 else 'channel:'+row['channel'] if status in (400,403,404) else None
                if scope:c.execute('INSERT INTO activity_discord_backoff VALUES(?,?) ON CONFLICT(scope) DO UPDATE SET until_at=excluded.until_at',(scope,now+wait))
                LOG.warning('Notification en attente (%s). Vérifier token/permissions si persistant.',error)
        # Respect global limits too: no other channel sent during a 429 pause.
        return min(wait,30) if status==429 else min(pause,30)

async def notification_worker(service):
    async with ClientSession(timeout=ClientTimeout(total=15)) as session:
        while True:
            try:
                # Finalize due expeditions even if the player closed the Activity.
                with service.conn() as c:due=c.execute('SELECT DISTINCT r.user_id,d.display_name FROM expedition_runs r JOIN activity_discord d ON d.user_id=r.user_id WHERE r.claimed=0 AND r.ends_at<=? LIMIT 20',(time.time(),)).fetchall()
                for row in due:
                    state=service.snapshot(row['user_id'],row['display_name']);service.notifications.observe(row['user_id'],state)
                service.notifications.gazette()
                token=os.getenv('DISCORD_BOT_TOKEN','').strip()
                if not token:
                    await asyncio.sleep(5);continue
                delay=await service.notifications.deliver_one(session,token)
                await asyncio.sleep(delay or 2)
            except asyncio.CancelledError:raise
            except Exception:
                LOG.exception('Relais Discord indisponible, nouvelle tentative dans 5 secondes')
                await asyncio.sleep(5)

async def discord_lifecycle(app):
    if os.getenv('ALTHERYA_DISCORD_NOTIFICATIONS','1')!='1':
        yield;return
    service=app['discord_service_factory']()
    task=asyncio.create_task(notification_worker(service))
    if not os.getenv('DISCORD_BOT_TOKEN','').strip():LOG.warning('DISCORD_BOT_TOKEN absent : messages conservés en attente, aucun envoi Discord.')
    yield
    task.cancel()
    try:await task
    except asyncio.CancelledError:pass
