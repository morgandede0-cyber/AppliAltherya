"""Explicit rollback utility; never executed by the Activity service."""
import asyncio
import os
import discord
from discord.http import Route
from discord_portal import DEFAULT_APP

async def restore():
    token=os.getenv('DISCORD_BOT_TOKEN','').strip()
    application=os.getenv('DISCORD_CLIENT_ID',DEFAULT_APP).strip()
    if not token:raise SystemExit('DISCORD_BOT_TOKEN absent.')
    async with discord.Client(intents=discord.Intents.none()) as client:
        await client.login(token)
        info=await client.application_info()
        if str(info.id)!=application:raise SystemExit('Le token ne correspond pas à l’application Altherya.')
        commands=await client.http.request(Route('GET','/applications/{application_id}/commands',application_id=info.id))
        entry=next((c for c in commands if c.get('type')==4),None)
        if not entry:raise SystemExit('Aucun point d’entrée trouvé ; aucune modification.')
        await client.http.request(Route('PATCH','/applications/{application_id}/commands/{command_id}',application_id=info.id,command_id=entry['id']),json={'handler':2})
        print('Point d’entrée rendu à Discord. Désactiver ALTHERYA_PORTAL_ENABLED pour arrêter le portail.')

if __name__=='__main__':
    try:asyncio.run(restore())
    except discord.HTTPException as exc:raise SystemExit(f'Discord a refusé la restauration (HTTP {exc.status}).') from None
