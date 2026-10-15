"""Display the home server nickname, while keeping OAuth IDs authoritative."""
import asyncio
import logging
import os
import re
import time
from contextlib import suppress
from aiohttp import ClientSession, ClientTimeout, ClientError
from discord_profile import verified_user

LOG=logging.getLogger('altherya.guild_names')
DEFAULT_PORTAL_CHANNEL='1551927225253761044'

def snowflake(value):
    return isinstance(value,str) and bool(re.fullmatch(r'[0-9]{15,22}',value))

class NamesUnavailable(Exception):
    def __init__(self,code):self.code=code;super().__init__(code)

class GuildNames:
    def __init__(self,activity):
        self.a=activity;self.paused_until=0
        with self.a.conn() as c:
            c.executescript('''
            CREATE TABLE IF NOT EXISTS activity_guild_names(
                user_id INTEGER PRIMARY KEY,account_name TEXT NOT NULL,guild_id TEXT NOT NULL DEFAULT '',
                nickname TEXT,checked_at REAL NOT NULL DEFAULT 0,next_check REAL NOT NULL DEFAULT 0,last_error TEXT);
            CREATE TABLE IF NOT EXISTS activity_guild_name_config(
                channel_id TEXT PRIMARY KEY,guild_id TEXT NOT NULL,checked_at REAL NOT NULL);
            ''')

    def channel(self):
        channel=os.getenv('ALTHERYA_PORTAL_CHANNEL_ID',DEFAULT_PORTAL_CHANNEL).strip()
        if not snowflake(channel):raise NamesUnavailable('salon_invalide')
        return channel

    def known_guild(self):
        explicit=os.getenv('DISCORD_GUILD_ID','').strip()
        if explicit:
            if not snowflake(explicit):raise NamesUnavailable('serveur_invalide')
            return explicit
        with self.a.conn() as c:row=c.execute('SELECT guild_id FROM activity_guild_name_config WHERE channel_id=?',(self.channel(),)).fetchone()
        return row[0] if row else None

    def row(self,uid):
        with self.a.conn() as c:r=c.execute('SELECT * FROM activity_guild_names WHERE user_id=?',(uid,)).fetchone()
        return dict(r) if r else None

    @staticmethod
    def write_display(c,uid,name):
        c.execute('UPDATE activity_discord SET display_name=? WHERE user_id=?',(name,uid))
        c.execute('UPDATE activity_sessions SET name=? WHERE user_id=?',(name,uid))
        c.execute('UPDATE activity_tutorial_receipts SET name=? WHERE user_id=?',(name,uid))

    def seed(self,uid,account_name=None):
        profile=self.a.discord_profile(uid)
        if not profile:return
        with self.a.conn() as c:
            c.execute('INSERT OR IGNORE INTO activity_guild_names(user_id,account_name) VALUES(?,?)',(uid,account_name or profile['display_name']))
            if account_name:c.execute('UPDATE activity_guild_names SET account_name=? WHERE user_id=?',(account_name,uid))
            row=c.execute('SELECT * FROM activity_guild_names WHERE user_id=?',(uid,)).fetchone()
            try:guild=self.known_guild()
            except NamesUnavailable:guild=None
            self.write_display(c,uid,row['nickname'] if row['nickname'] and row['guild_id']==guild else row['account_name'])

    async def login(self,uid,user):
        # user comes from Discord /users/@me on the server, never request JSON.
        account=verified_user(user)['display_name']
        self.seed(uid,account)
        await self.refresh(uid,force=True)

    async def get_json(self,session,path,token):
        if time.time()<self.paused_until:raise NamesUnavailable('pause_discord')
        try:
            async with session.get('https://discord.com/api/v10'+path,headers={'Authorization':'Bot '+token},allow_redirects=False) as r:
                if r.status==200:
                    data=await r.json()
                    if not isinstance(data,dict):raise NamesUnavailable('reponse_invalide')
                    return data
                if r.status==429:
                    data=await r.json();delay=max(1,min(float(data.get('retry_after',5) if isinstance(data,dict) else 5),86400))
                    self.paused_until=time.time()+delay
                elif r.status in (401,403):
                    if self.paused_until<=time.time():LOG.warning('Lecture des surnoms refusée par Discord (HTTP %s). Vérifier le token du bot et son accès au serveur.',r.status)
                    self.paused_until=time.time()+300
                raise NamesUnavailable('http_'+str(r.status))
        except (ClientError,asyncio.TimeoutError,ValueError,TypeError):raise NamesUnavailable('reseau') from None

    async def resolve_guild(self,session,token):
        explicit=os.getenv('DISCORD_GUILD_ID','').strip()
        if explicit:return self.known_guild()
        channel=self.channel()
        with self.a.conn() as c:cached=c.execute('SELECT guild_id,checked_at FROM activity_guild_name_config WHERE channel_id=?',(channel,)).fetchone()
        if cached and time.time()-cached['checked_at']<86400:return cached['guild_id']
        try:
            data=await self.get_json(session,'/channels/'+channel,token)
            if str(data.get('id'))!=channel or not snowflake(data.get('guild_id')):raise NamesUnavailable('salon_sans_serveur')
            guild=data['guild_id']
            with self.a.conn() as c:c.execute('INSERT INTO activity_guild_name_config VALUES(?,?,?) ON CONFLICT(channel_id) DO UPDATE SET guild_id=excluded.guild_id,checked_at=excluded.checked_at',(channel,guild,time.time()))
            return guild
        except NamesUnavailable:
            # A channel cannot move between guilds. A previously verified mapping is safe to reuse.
            if cached:return cached['guild_id']
            raise

    def record_member(self,uid,guild,member):
        profile=self.a.discord_profile(uid)
        user=member.get('user')
        verified=verified_user(user)
        if not profile or verified['discord_id']!=profile['discord_id'] or not snowflake(guild):raise NamesUnavailable('membre_invalide')
        nick=member.get('nick')
        if nick is not None and (not isinstance(nick,str) or not nick.strip() or len(nick)>32):raise NamesUnavailable('surnom_invalide')
        account=verified['display_name'];name=nick or account;now=time.time()
        with self.a.conn() as c:
            c.execute('BEGIN IMMEDIATE')
            c.execute('INSERT INTO activity_guild_names VALUES(?,?,?,?,?,?,NULL) ON CONFLICT(user_id) DO UPDATE SET account_name=excluded.account_name,guild_id=excluded.guild_id,nickname=excluded.nickname,checked_at=excluded.checked_at,next_check=excluded.next_check,last_error=NULL',(uid,account,guild,nick,now,now+300))
            self.write_display(c,uid,name)
        return name

    async def refresh(self,uid,force=False,session=None):
        self.seed(uid)
        profile=self.a.discord_profile(uid);row=self.row(uid)
        if not profile or not row:return False
        if not force and row['next_check']>time.time():return False
        token=os.getenv('DISCORD_BOT_TOKEN','').strip()
        guild=None
        async def resolve(active):
            nonlocal guild
            guild=await self.resolve_guild(active,token)
            member=await self.get_json(active,'/guilds/'+guild+'/members/'+profile['discord_id'],token)
            self.record_member(uid,guild,member)
        try:
            if not token:raise NamesUnavailable('token_absent')
            if session is not None:await asyncio.wait_for(resolve(session),6)
            else:
                async with ClientSession(timeout=ClientTimeout(total=4)) as active:await asyncio.wait_for(resolve(active),6)
            return True
        except (NamesUnavailable,asyncio.TimeoutError,ValueError) as exc:
            code=exc.code if isinstance(exc,NamesUnavailable) else 'reponse_invalide'
            with self.a.conn() as c:
                if code=='http_404' and guild:
                    # Confirmed non-member: do not retain a nickname from an old membership.
                    c.execute('UPDATE activity_guild_names SET nickname=NULL,guild_id=? WHERE user_id=?',(guild,uid))
                    current=c.execute('SELECT account_name FROM activity_guild_names WHERE user_id=?',(uid,)).fetchone()
                    self.write_display(c,uid,current[0])
                c.execute('UPDATE activity_guild_names SET next_check=?,last_error=? WHERE user_id=?',(time.time()+300,code,uid))
            return False

    def next_player(self):
        with self.a.conn() as c:
            r=c.execute('SELECT a.user_id FROM activity_discord_accounts a LEFT JOIN activity_guild_names n ON n.user_id=a.user_id WHERE COALESCE(n.next_check,0)<=? ORDER BY COALESCE(n.next_check,0),a.user_id LIMIT 1',(time.time(),)).fetchone()
        return r[0] if r else None

async def name_worker(service):
    async with ClientSession(timeout=ClientTimeout(total=4)) as session:
        while True:
            try:
                uid=service.guild_names.next_player()
                if uid is not None:await service.guild_names.refresh(uid,session=session)
                await asyncio.sleep(1 if uid is not None else 10)
            except asyncio.CancelledError:raise
            except Exception:
                LOG.exception('Synchronisation des surnoms interrompue ; nouvelle tentative dans 10 secondes.')
                await asyncio.sleep(10)

async def names_lifecycle(app):
    if not os.getenv('DISCORD_BOT_TOKEN','').strip():
        LOG.warning('Surnoms serveur indisponibles : DISCORD_BOT_TOKEN absent, noms de compte utilisés en secours.')
        yield;return
    task=asyncio.create_task(name_worker(app['discord_service_factory']()))
    try:yield
    finally:
        task.cancel()
        with suppress(asyncio.CancelledError):await task
