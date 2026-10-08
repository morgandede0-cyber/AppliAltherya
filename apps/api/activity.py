"""Isolated Activity test adapter. Original bot engines remain unchanged."""
import os, sys, secrets, sqlite3, hashlib, time, json
from pathlib import Path
from dataclasses import asdict
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'bot' / 'tourwork'))
from economy import Economy
from castle_engine import CastleStore
from expedition_engine import ExpeditionStore, STARTER_GEAR, EXPEDITIONS, RESOURCE_SELL_PRICES, TOOL_LEVELS, BAG_LEVELS, UPGRADE_RECIPES, BAG_UPGRADE_RECIPES, EXPEDITION_OBJECTS
from progression import level_from_xp, FORGE_LEVEL_REQUIREMENTS, FORGE_GOLD_COSTS, EXPEDITION_TIER_XP
from story_engine import StoryStore, SEASON_1_TITLES, SEASON_1_TEXTS, STORY_ITEM_PRICES, STORY_REQUIREMENTS
from job_board_engine import JobBoardStore, BoardJob
from progression import JOB_RARITY_XP
from aiohttp import web
from play import Play
from discord_profile import verified_user,avatar_revision

class Activity:
    def __init__(self, path):
        if os.getenv('ECONOMY_DATABASE_URL','').strip():
            raise RuntimeError('Le mode de test Activity exige une économie locale séparée. Retirez ECONOMY_DATABASE_URL de ce service.')
        self.path=Path(path)
        self.economy=Economy(path); self.expeditions=ExpeditionStore(path); self.castle=CastleStore(path)
        self.story=StoryStore(path);self.jobs=JobBoardStore(path)
        with self.conn() as c:
            c.execute('CREATE TABLE IF NOT EXISTS activity_sessions(token TEXT PRIMARY KEY,user_id INTEGER UNIQUE,name TEXT NOT NULL)')
            c.execute('CREATE TABLE IF NOT EXISTS activity_discord(user_id INTEGER PRIMARY KEY,discord_id TEXT NOT NULL,avatar TEXT NOT NULL,username TEXT NOT NULL,display_name TEXT NOT NULL,discriminator TEXT NOT NULL)')
            c.execute('CREATE TABLE IF NOT EXISTS activity_rewards(reference TEXT PRIMARY KEY)')
        self.play=Play(self)
    def conn(self):
        c=sqlite3.connect(self.path);c.row_factory=sqlite3.Row;return c
    def session(self, token):
        digest=hashlib.sha256(token.encode()).hexdigest() if token else ''
        with self.conn() as c: row=c.execute('SELECT user_id,name FROM activity_sessions WHERE token=?',(digest,)).fetchone()
        if row:return row, None
        token=secrets.token_urlsafe(32); uid=secrets.randbelow(2**52)+1
        with self.conn() as c:c.execute('INSERT INTO activity_sessions VALUES(?,?,?)',(hashlib.sha256(token.encode()).hexdigest(),uid,'Aventurier'))
        return (uid,'Aventurier'),token
    def bind_discord(self, uid, user):
        profile=verified_user(user)
        with self.conn() as c:
            c.execute('INSERT INTO activity_discord VALUES(?,?,?,?,?,?) ON CONFLICT(user_id) DO UPDATE SET discord_id=excluded.discord_id,avatar=excluded.avatar,username=excluded.username,display_name=excluded.display_name,discriminator=excluded.discriminator',(uid,profile['discord_id'],profile['avatar'],profile['username'],profile['display_name'],profile['discriminator']))
    def discord_profile(self, uid):
        with self.conn() as c:row=c.execute('SELECT * FROM activity_discord WHERE user_id=?',(uid,)).fetchone()
        return dict(row) if row else None
    def session_uid(self, token):
        if not token:return None
        with self.conn() as c:row=c.execute('SELECT user_id FROM activity_sessions WHERE token=?',(hashlib.sha256(token.encode()).hexdigest(),)).fetchone()
        return row[0] if row else None
    def reconcile(self, uid):
        run=self.expeditions.active_run(uid)
        if run and run.finished:self.expeditions.finalize_run(run.run_id)
        # Completed runs survive restarts; unique reward marker and XP commit together.
        with self.conn() as c:
            c.execute('BEGIN IMMEDIATE')
            rows=c.execute('SELECT run_id,expedition_key FROM expedition_runs WHERE user_id=? AND claimed=1',(uid,)).fetchall()
            for rid,key in rows:
                if c.execute('INSERT OR IGNORE INTO activity_rewards VALUES(?)',('expedition:'+rid,)).rowcount:
                    cfg=EXPEDITIONS[key]; xp=cfg.get('xp_reward',EXPEDITION_TIER_XP.get(cfg['destination_index'],0))
                    before=c.execute('SELECT xp FROM castle_profiles WHERE user_id=?',(uid,)).fetchone()[0]
                    c.execute('UPDATE castle_profiles SET xp=xp+?,expeditions=expeditions+1 WHERE user_id=?',(xp,uid))
                    self.castle._queue_levelups(c,uid,before,before+xp); self.castle._sync_level(c,uid)
                    c.execute('INSERT INTO castle_daily_progress(user_id,day,quest_key,progress) VALUES(?,?,?,1) ON CONFLICT(user_id,day,quest_key) DO UPDATE SET progress=progress+1',(uid,self.castle._today(),'expedition'))
    def snapshot(self, uid, name):
        self.economy.get_balance(uid); self.expeditions.ensure_profile(uid); self.castle.ensure(uid);self.reconcile(uid)
        level,xp,needed=level_from_xp(self.castle.profile(uid)['xp'])
        run=self.expeditions.active_run(uid)
        if run:self.expeditions.reveal_due_events(run.run_id)
        # Never expose precomputed future loot to the client.
        active=None if not run else {'name':EXPEDITIONS[run.expedition_key]['name'],'ends_at':run.ends_at,'remaining':run.remaining_seconds,'capacity':run.capacity,'ends_at':run.ends_at,'started_at':run.started_at,'revealed_loot':self.expeditions.revealed_loot(run.run_id),'log':self.expeditions.drop_log(run.run_id)}
        self.story.unlock_chapter(uid,1,1)
        chapters=[dict(chapter=n,title=title,**self.story.chapter_state(uid,1,n)) for n,title in SEASON_1_TITLES.items()]
        board=asdict(self.jobs.get_board(uid));pending=self.jobs.pending_reward(uid)
        if pending:pending={**pending,'job':asdict(pending['job'])}
        quests,quest_reward=self.castle.quests(uid)
        with self.conn() as c:names={r['user_id']:r['name'] for r in c.execute('SELECT user_id,name FROM activity_sessions')}
        podium=[dict(name=names.get(r['user_id'],'Aventurier'),total=r['total']) for r in self.castle.leaderboard(10)]
        discord=self.discord_profile(uid)
        public_discord=None if not discord else dict(username=discord['username'],display_name=discord['display_name'],avatar_url='/api/avatar?v='+avatar_revision(discord))
        history_inventory=self.story.inventory(uid)
        owned_story_items=[dict(name=n,quantity=q) for n,q in history_inventory.items() if n in STORY_ITEM_PRICES]
        return dict(owned_story_items=owned_story_items,discord=public_discord,**self.play.snapshot(uid),server_now=time.time(),stats={k:v for k,v in self.castle.profile(uid).items() if k!='user_id'},quests=quests,quest_reward=quest_reward,podium=podium,chapters=chapters,story_items=[dict(name=item,chapter=next(group+1 for group,items in STORY_REQUIREMENTS.items() if item in items),price=STORY_ITEM_PRICES[item],owned=self.story.has_purchased_story_item(uid,item)) for item in self.story.current_market_items(uid)],board=board,pending=pending,name=name,level=level,xp=xp,xp_needed=needed,balance=asdict(self.economy.get_balance(uid)),owned=self.expeditions.owned_equipment(uid),gear=asdict(self.expeditions.get_gear(uid)),resources=self.expeditions.get_resources(uid),daily_available=self.castle.daily_available(uid),active=active,catalog=STARTER_GEAR,destinations=EXPEDITIONS,prices=RESOURCE_SELL_PRICES,tools=TOOL_LEVELS,bags=BAG_LEVELS,recipes=UPGRADE_RECIPES,bag_recipes=BAG_UPGRADE_RECIPES,forge_levels=FORGE_LEVEL_REQUIREMENTS,forge_gold=FORGE_GOLD_COSTS,objects=EXPEDITION_OBJECTS,mode='test séparé du bot')
    def action(self,uid,body):
        action=body.get('action'); key=body.get('key','')
        if not isinstance(action,str) or not isinstance(key,str):raise ValueError('Action invalide.')
        if action=='name':
            name=body.get('name')
            if not isinstance(name,str) or not 1<=len(name.strip())<=24:raise ValueError('Nom invalide.')
            with self.conn() as c:c.execute('UPDATE activity_sessions SET name=? WHERE user_id=?',(name.strip(),uid))
            return 'Nom enregistré.'
        if action in ('deposit','withdraw','sell'):
            amount=body.get('amount')
            if type(amount) is not int or not 1<=amount<=1000000000:raise ValueError('Indiquez une quantité entière positive.')
        if action in ('deposit','withdraw'):return getattr(self.economy,action)(uid,amount).message
        if action=='story_buy':return self.story.buy_story_item(uid,key)[1]
        if action=='story_unlock':return self.story.unlock_chapter(uid,1,int(body.get('chapter',0)))[1]
        if action=='story_read':
            n=body.get('chapter')
            if type(n) is not int or n not in SEASON_1_TEXTS or not self.story.is_unlocked(uid,1,n):raise ValueError('Chapitre verrouillé.')
            self.story.remember_read_chapter(uid,1,n);return SEASON_1_TEXTS[n]
        if action=='job_accept':return self.jobs.accept_job(uid,body.get('batch',''),key)[1]
        if action=='job_claim':
            # Original readiness/Gold rules plus XP in the same transaction.
            with self.conn() as c:
                c.execute('BEGIN IMMEDIATE')
                row=c.execute('SELECT pending_job_json,reward_ready_at FROM job_board_state WHERE user_id=?',(uid,)).fetchone()
                if not row or not row[0]:return 'Aucune récompense en attente.'
                if time.time()<row[1]:return 'La mission n’est pas encore terminée.'
                job=BoardJob.from_dict(json.loads(row[0]));xp=JOB_RARITY_XP[job.rarity]
                c.execute('UPDATE players SET wallet_gold=wallet_gold+? WHERE user_id=?',(job.reward,uid))
                before=c.execute('SELECT xp FROM castle_profiles WHERE user_id=?',(uid,)).fetchone()[0]
                c.execute('UPDATE castle_profiles SET xp=xp+? WHERE user_id=?',(xp,uid))
                self.castle._queue_levelups(c,uid,before,before+xp);self.castle._sync_level(c,uid)
                c.execute("UPDATE job_board_state SET pending_job_json='',reward_ready_at=0,next_board_at=0 WHERE user_id=?",(uid,))
            return f'{job.reward} Gold et {xp} XP récupérés.'
        if action=='buy':return self.expeditions.buy_starter(uid,key)[1]
        if action=='sell':return self.expeditions.sell_resource(uid,key,amount)[1]
        if action=='upgrade':
            ok,msg=self.expeditions.upgrade(uid,key)
            if ok:
                self.castle.record(uid,'forge_upgrade');tier=self.expeditions.get_gear(uid).bag_level if key=='bag' else self.expeditions.get_gear(uid).tool_level(key);self.castle.add_xp(uid,20 if tier==2 else 35 if tier==3 else 60 if tier==4 else 100)
            return msg
        if action=='daily':
            ok,gold=self.castle.claim_daily(uid);return f'{gold} Gold et 20 XP récupérés.' if ok else 'Déjà récupéré aujourd’hui.'
        if action=='quests_claim':
            ok,gold,xp,_=self.castle.claim_quests(uid);return f'{gold} Gold et {xp} XP récupérés.' if ok else 'Terminez les six quêtes avant de réclamer la récompense.'
        if action=='start':
            if body.get('object1','none')!='none' or body.get('object2','none')!='none':raise ValueError('Les accessoires ne sont pas encore disponibles.')
            for field in ('tool_level','bag_level'):
                if field in body and type(body[field]) is not int:raise ValueError('Palier invalide.')
            return self.expeditions.start(uid,key,body.get('tool','hands'),tool_level=body.get('tool_level'),bag_level=body.get('bag_level'))[1]
        if action in ('drink','guard','larceny','npc_theft','crime','heist_start','heist_guess','game_cancel','game_start','game_step','battle_start','battle_step'):return self.play.action(uid,body)
        raise ValueError('Action inconnue.')

SERVICE=None
async def activity(request):
    global SERVICE
    if SERVICE is None:SERVICE=Activity(os.getenv('ACTIVITY_DB',str(Path(__file__).resolve().parents[2]/'data'/'activity.sqlite3')))
    (uid,name),token=SERVICE.session(request.cookies.get('altherya_test',''))
    message=''
    if request.method=='POST':
        # Same-origin form submissions only; no balances or rewards from client.
        if request.headers.get('X-Altherya-Request')!='1':raise web.HTTPForbidden()
        try:
            body=await request.json()
            if not isinstance(body,dict):raise ValueError('Requête invalide.')
            SERVICE.snapshot(uid,name)
            message=SERVICE.action(uid,body)
            with SERVICE.conn() as c:name=c.execute('SELECT name FROM activity_sessions WHERE user_id=?',(uid,)).fetchone()[0]
        except (ValueError,TypeError) as e:return web.json_response({'error':str(e)},status=400)
    response=web.json_response({'state':SERVICE.snapshot(uid,name),'message':message},headers={'Cache-Control':'no-store'})
    if token:response.set_cookie('altherya_test',token,httponly=True,samesite='Strict',secure=request.secure,max_age=31536000)
    return response
