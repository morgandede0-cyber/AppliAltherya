"""One persistent Discord portal, served by the Activity's own application bot."""
import asyncio
import hashlib
import json
import logging
import os
import secrets
import time
from pathlib import Path
from urllib.parse import urlsplit
from contextlib import suppress

import discord
from discord.http import Route

LOG = logging.getLogger('altherya.portal')
DEFAULT_CHANNEL = '1551927225253761044'
DEFAULT_APP = '1529936499775242250'
CUSTOM_ID = 'altherya:portal:play:v1'

class PortalError(Exception):
    pass

class PortalStore:
    def __init__(self, service):
        self.service = service
        with service.conn() as c:
            c.executescript('''
            CREATE TABLE IF NOT EXISTS activity_portal_messages(
                channel_id TEXT PRIMARY KEY,message_id TEXT,payload_hash TEXT,
                generation INTEGER NOT NULL DEFAULT 0);
            CREATE TABLE IF NOT EXISTS activity_portal_leases(
                channel_id TEXT PRIMARY KEY,owner TEXT NOT NULL,expires REAL NOT NULL);
            ''')

    def lease(self, channel, owner, now=None):
        now = time.time() if now is None else now
        with self.service.conn() as c:
            c.execute('BEGIN IMMEDIATE')
            row = c.execute('SELECT owner,expires FROM activity_portal_leases WHERE channel_id=?',(channel,)).fetchone()
            if row and row['owner'] != owner and row['expires'] > now:
                return False
            c.execute('INSERT INTO activity_portal_leases VALUES(?,?,?) ON CONFLICT(channel_id) DO UPDATE SET owner=excluded.owner,expires=excluded.expires',(channel,owner,now+90))
            return True

    def release(self, channel, owner):
        with self.service.conn() as c:
            c.execute('DELETE FROM activity_portal_leases WHERE channel_id=? AND owner=?',(channel,owner))

    def state(self, channel):
        with self.service.conn() as c:
            c.execute('INSERT OR IGNORE INTO activity_portal_messages(channel_id) VALUES(?)',(channel,))
            return dict(c.execute('SELECT * FROM activity_portal_messages WHERE channel_id=?',(channel,)).fetchone())

    def save(self, channel, message, payload_hash):
        with self.service.conn() as c:
            c.execute('UPDATE activity_portal_messages SET message_id=?,payload_hash=? WHERE channel_id=?',(str(message),payload_hash,channel))

    def missing(self, channel, message):
        with self.service.conn() as c:
            c.execute('UPDATE activity_portal_messages SET message_id=NULL,payload_hash=NULL,generation=generation+1 WHERE channel_id=? AND message_id=?',(channel,str(message)))


def portal_art_url():
    base=os.getenv('ALTHERYA_PUBLIC_URL','https://altherya.magicgg.fr').strip().rstrip('/')
    parsed=urlsplit(base)
    if parsed.scheme!='https' or not parsed.hostname or parsed.username or parsed.password or parsed.query or parsed.fragment:
        raise PortalError('ALTHERYA_PUBLIC_URL doit être une URL publique HTTPS, sans identifiants ni paramètres.')
    game=Path(__file__).resolve().parents[1]/'game'
    relative=Path('assets/discord/portal-altherya.png')
    artwork=next((root/relative for root in (game/'dist',game/'public') if (root/relative).is_file()),None)
    if artwork is None:raise PortalError('Image du portail absente : reconstruire le frontend avec les assets fournis.')
    revision=hashlib.sha256(artwork.read_bytes()).hexdigest()[:12]
    return base+'/'+relative.as_posix()+'?v='+revision


def is_portal(message, bot_id):
    if message.author.id != bot_id:
        return False
    def contains(items):
        return any(getattr(item,'custom_id',None)==CUSTOM_ID or contains(getattr(item,'children',())) for item in items)
    return contains(message.components)


class PortalView(discord.ui.LayoutView):
    def __init__(self, client):
        super().__init__(timeout=None)
        self.client = client
        self.play_button=discord.ui.Button(label='Jouer à Altherya',emoji='🎮',style=discord.ButtonStyle.primary,custom_id=CUSTOM_ID)
        self.play_button.callback=self.play
        gallery=discord.ui.MediaGallery(discord.MediaGalleryItem(media=portal_art_url(),description='Althérya — votre aventure commence à Legacy. Utilisez le bouton Jouer à Altherya sous cette image pour entrer.'))
        self.add_item(discord.ui.Container(gallery,discord.ui.ActionRow(self.play_button),accent_colour=0xD6A84B))

    async def play(self, interaction):
        await self.client.launch(interaction)

    async def on_error(self, interaction, error, item):
        LOG.error('Bouton portail indisponible (%s)',type(error).__name__)
        if not interaction.response.is_done():
            with suppress(discord.HTTPException):
                await interaction.response.send_message('Le portail est momentanément indisponible. Réessayez dans quelques instants.',ephemeral=True,allowed_mentions=discord.AllowedMentions.none())


class PortalClient(discord.Client):
    def __init__(self, store, channel, application):
        super().__init__(intents=discord.Intents.none(),allowed_mentions=discord.AllowedMentions.none())
        self.store=store
        self.portal_channel=str(channel)
        self.portal_application=str(application)
        self.portal_view=None
        self.portal_lock=asyncio.Lock()
        self.launches={}
        self.entry_point_id=None
        self.validated=False
        self.last_check=0.0
        self.pin_warned=False

    async def setup_hook(self):
        info=await self.application_info()
        if str(info.id)!=self.portal_application:
            raise PortalError('DISCORD_BOT_TOKEN doit appartenir à l’application Altherya '+self.portal_application+'.')
        if info.interactions_endpoint_url:
            raise PortalError('Une Interactions Endpoint URL est configurée : ce portail utilise le Gateway. Ne pas effacer cet endpoint sans vérifier son usage ; intégrer le bouton à son gestionnaire HTTP ou choisir le Gateway pour cette application.')
        self.portal_view=PortalView(self)
        self.add_view(self.portal_view)
        self.validated=True
        if os.getenv('ALTHERYA_PORTAL_ENTRY_POINT','1')=='1':
            await self.configure_entry_point()

    async def configure_entry_point(self):
        app=int(self.portal_application)
        commands=await self.http.request(Route('GET','/applications/{application_id}/commands',application_id=app))
        entry=next((c for c in commands if c.get('type')==4),None)
        if entry:
            if entry.get('handler')!=1:
                await self.http.request(Route('PATCH','/applications/{application_id}/commands/{command_id}',application_id=app,command_id=entry['id']),json={'handler':1})
            self.entry_point_id=str(entry['id'])
        else:
            entry=await self.http.request(Route('POST','/applications/{application_id}/commands',application_id=app),json={'name':'jouer','description':'Ouvrir Altherya depuis son portail','type':4,'handler':1,'contexts':[0],'integration_types':[0]})
            self.entry_point_id=str(entry['id'])

    async def on_ready(self):
        await self.check_portal()

    async def check_portal(self):
        if not self.validated:return
        try:
            await self.ensure_portal()
            LOG.info('Portail Altherya prêt dans le salon %s',self.portal_channel)
        except (discord.HTTPException,PortalError,OSError,asyncio.TimeoutError) as exc:
            LOG.warning('Portail non installé (%s). Vérifier le salon et les permissions du bot.',type(exc).__name__)
        self.last_check=time.monotonic()

    async def ensure_portal(self):
        async with self.portal_lock:
            channel=await self.fetch_channel(int(self.portal_channel))
            if not isinstance(channel,discord.TextChannel):
                raise PortalError('Le portail exige un salon textuel de serveur.')
            state=self.store.state(self.portal_channel)
            message=None
            if state['message_id']:
                try:message=await channel.fetch_message(int(state['message_id']))
                except discord.NotFound:self.store.missing(self.portal_channel,state['message_id'])
                # Forbidden and network errors must never cause another message to be created.
                if message and not is_portal(message,self.user.id):
                    raise PortalError('Le message enregistré ne correspond pas au portail ; aucune modification.')
            if message is None:
                # Recover a send accepted just before a process/DB interruption.
                async for candidate in channel.pins(limit=None):
                    if is_portal(candidate,self.user.id):message=candidate;break
                if message is None:
                    async for candidate in channel.history(limit=100):
                        if is_portal(candidate,self.user.id):message=candidate;break
            payload={'flags':32768,'components':self.portal_view.to_components(),'allowed_mentions':{'parse':[]}}
            fingerprint=hashlib.sha256(json.dumps(payload,sort_keys=True).encode()).hexdigest()
            if message is None:
                generation=self.store.state(self.portal_channel)['generation']
                nonce=str(int(hashlib.sha256(f'portal:{self.portal_application}:{self.portal_channel}:{generation}'.encode()).hexdigest()[:15],16))
                data=await self.http.request(Route('POST','/channels/{channel_id}/messages',channel_id=int(self.portal_channel)),json={**payload,'nonce':nonce,'enforce_nonce':True})
                # Persist the id before fetching/pinning, so a pin failure cannot duplicate the portal.
                self.store.save(self.portal_channel,data['id'],fingerprint)
                message=await channel.fetch_message(int(data['id']))
            elif state['payload_hash']!=fingerprint:
                # LayoutView sets IS_COMPONENTS_V2. Explicitly clear old V1 fields when migrating.
                await message.edit(content=None,embeds=[],attachments=[],view=self.portal_view,allowed_mentions=discord.AllowedMentions.none())
            self.store.save(self.portal_channel,message.id,fingerprint)
            if not message.pinned:
                try:await message.pin(reason='Portail permanent Altherya')
                except discord.Forbidden:
                    if not self.pin_warned:LOG.warning('Portail publié : épinglez-le manuellement ou accordez la permission d’épingler au bot.')
                    self.pin_warned=True
            return message

    async def launch(self, interaction):
        if not self.validated or str(interaction.application_id)!=self.portal_application:
            return
        if not interaction.guild_id or str(interaction.channel_id)!=self.portal_channel:
            await interaction.response.send_message(f'Ouvrez Altherya depuis le portail dans <#{self.portal_channel}>.',ephemeral=True,allowed_mentions=discord.AllowedMentions.none())
            return
        now=time.monotonic()
        # Only cache a tiny recent window; persistent player progress never lives here.
        self.launches={uid:at for uid,at in self.launches.items() if now-at<5}
        if interaction.user.id in self.launches:
            await interaction.response.send_message('Le lancement est déjà demandé. Patientez un instant.',ephemeral=True,allowed_mentions=discord.AllowedMentions.none())
            return
        self.launches[interaction.user.id]=now
        try:
            # Must be the initial response, not deferred, to stay within Discord's deadline.
            await interaction.response.launch_activity()
        except discord.HTTPException:
            self.launches.pop(interaction.user.id,None)
            LOG.warning('Lancement Activity refusé par Discord ; vérifier Activities et le token de l’application.')
            if not interaction.response.is_done():
                with suppress(discord.HTTPException):
                    await interaction.response.send_message('Discord n’a pas pu ouvrir Altherya. Réessayez dans quelques instants.',ephemeral=True,allowed_mentions=discord.AllowedMentions.none())

    async def on_interaction(self, interaction):
        if interaction.type==discord.InteractionType.application_command and str(interaction.data.get('id'))==self.entry_point_id:
            await self.launch(interaction)


async def portal_supervisor(service, token, channel, application):
    store=PortalStore(service)
    owner=secrets.token_hex(16)
    client=None;task=None;check_task=None
    try:
        while True:
            if not store.lease(channel,owner):
                await asyncio.sleep(15);continue
            client=PortalClient(store,channel,application)
            task=asyncio.create_task(client.start(token,reconnect=True))
            try:
                while not task.done():
                    await asyncio.sleep(15)
                    if not store.lease(channel,owner):break
                    if client.is_ready() and time.monotonic()-client.last_check>900 and (check_task is None or check_task.done()):
                        check_task=asyncio.create_task(client.check_portal())
                if task.done():await task
            except (discord.LoginFailure,PortalError) as exc:
                LOG.error('Portail arrêté : %s',str(exc) if isinstance(exc,PortalError) else 'DISCORD_BOT_TOKEN invalide.')
                return
            except (discord.HTTPException,discord.ConnectionClosed,OSError,asyncio.TimeoutError):
                LOG.warning('Connexion portail interrompue ; nouvelle tentative dans 30 secondes.')
            finally:
                if check_task:
                    check_task.cancel()
                    with suppress(asyncio.CancelledError,Exception):await check_task
                    check_task=None
                await client.close()
                task.cancel()
                with suppress(asyncio.CancelledError,Exception):await task
                task=None;client=None
            await asyncio.sleep(30)
    finally:
        if client:await client.close()
        if task:
            task.cancel()
            with suppress(asyncio.CancelledError,Exception):await task
        store.release(channel,owner)


async def portal_lifecycle(app):
    if os.getenv('ALTHERYA_PORTAL_ENABLED','1')!='1':yield;return
    token=os.getenv('DISCORD_BOT_TOKEN','').strip()
    if not token:
        LOG.warning('Portail inactif : ajouter DISCORD_BOT_TOKEN dans le service Activity.')
        yield;return
    channel=os.getenv('ALTHERYA_PORTAL_CHANNEL_ID',DEFAULT_CHANNEL).strip()
    application=os.getenv('DISCORD_CLIENT_ID',DEFAULT_APP).strip()
    if not channel.isdigit() or not application.isdigit():
        LOG.error('Portail inactif : identifiant du salon ou de l’application invalide.')
        yield;return
    task=asyncio.create_task(portal_supervisor(app['discord_service_factory'](),token,channel,application))
    try:yield
    finally:
        task.cancel()
        with suppress(asyncio.CancelledError,Exception):await task
