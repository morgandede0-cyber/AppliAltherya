"""OAuth gateway only. No client-submitted Gold or rewards accepted."""
from activity_cookie import set_activity_cookie
import os
import asyncio
from pathlib import Path
from aiohttp import web, ClientSession, ClientTimeout, ClientError
PUBLIC=Path(__file__).resolve().parents[1]/'game'/'public'
DIST=Path(__file__).resolve().parents[1]/'game'/'dist'
async def health(request): return web.json_response({'status':'ok','economy':'isolated-server-test'})
async def auth(request):
    client_id=os.getenv('DISCORD_CLIENT_ID');secret=os.getenv('DISCORD_CLIENT_SECRET')
    if not client_id or not secret: return web.json_response({'error':'Discord OAuth non configuré'},status=503)
    if request.headers.get('X-Altherya-Request')!='1':return web.json_response({'error':'Requête de connexion refusée'},status=403,headers={'Cache-Control':'no-store'})
    try:
        body=await request.json();code=body.get('code')
        if not isinstance(code,str) or not 1<=len(code)<=2048: raise ValueError()
    except Exception: return web.json_response({'error':'code invalide'},status=400)
    try:
        async with ClientSession(timeout=ClientTimeout(total=15)) as session:
            async with session.post('https://discord.com/api/oauth2/token',data={'client_id':client_id,'client_secret':secret,'grant_type':'authorization_code','code':code}) as response:
                data=await response.json()
                if response.status!=200: return web.json_response({'error':'OAuth refusé'},status=401)
            async with session.get('https://discord.com/api/v10/users/@me',headers={'Authorization':'Bearer '+data['access_token']}) as response:
                if response.status!=200:return web.json_response({'error':'Profil Discord inaccessible'},status=502)
                user=await response.json()
    except (ClientError,asyncio.TimeoutError,ValueError,KeyError,TypeError):
        return web.json_response({'error':'Connexion Discord indisponible'},status=502)
    service=get_service()
    (uid,_),token=service.session(request.cookies.get('altherya_test',''))
    try:target,session_token=service.identities.login(uid,user,token or request.cookies.get('altherya_test',''))
    except ValueError:return web.json_response({'error':'Profil Discord invalide'},status=502)
    await service.guild_names.login(target,user)
    response=web.json_response({'access_token':data['access_token']},headers={'Cache-Control':'no-store'})
    set_activity_cookie(response,request,session_token)
    return response

def get_service():
    if adapter.SERVICE is None:adapter.SERVICE=adapter.Activity(os.getenv('ACTIVITY_DB',str(Path(__file__).resolve().parents[2]/'data'/'activity.sqlite3')))
    return adapter.SERVICE

async def admin(request):
    service=get_service();uid=service.session_uid(request.cookies.get('altherya_test',''))
    try:
        service.admin.require(uid)
        if request.headers.get('X-Altherya-Request')!='1':raise web.HTTPForbidden()
        body=await request.json()
        if not isinstance(body,dict):raise ValueError('Requête invalide.')
        data=service.admin.handle(uid,body)
        return web.json_response(data,headers={'Cache-Control':'no-store'})
    except PermissionError:return web.json_response({'error':'Accès administrateur refusé.'},status=403,headers={'Cache-Control':'no-store'})
    except (ValueError,TypeError):return web.json_response({'error':'Requête invalide ou données modifiées. Actualisez la fiche.'},status=400,headers={'Cache-Control':'no-store'})

async def avatar(request):
    service=get_service();uid=service.session_uid(request.cookies.get('altherya_test',''))
    if 'player' in request.query:
        try:service.admin.require(uid);uid=service.admin.target(request.query['player'])
        except (PermissionError,ValueError):raise web.HTTPForbidden()
    profile=service.discord_profile(uid) if uid else None
    if 'podium' in request.query:
        if not uid:raise web.HTTPForbidden()
        profile=None
        for entry in service.castle.leaderboard(10):
            candidate=service.discord_profile(entry['user_id'])
            if candidate and avatar_revision(candidate)==request.query['podium']:
                profile=candidate;break
    if not profile:raise web.HTTPNotFound()
    try:
        async with ClientSession(timeout=ClientTimeout(total=10)) as session:
            async with session.get(avatar_cdn(profile),allow_redirects=False) as response:
                if response.status!=200 or response.content_type not in ('image/png','image/jpeg','image/webp','image/gif'):raise web.HTTPBadGateway()
                data=bytearray()
                async for chunk in response.content.iter_chunked(65536):
                    data.extend(chunk)
                    if len(data)>2*1024*1024:raise web.HTTPBadGateway()
                return web.Response(body=bytes(data),content_type=response.content_type,headers={'Cache-Control':'private,max-age=3600'})
    except (ClientError,asyncio.TimeoutError):raise web.HTTPBadGateway()

async def static(request):
    relative=request.match_info['path'] or 'index.html'
    for root in (DIST,PUBLIC):
        path=(root/relative).resolve()
        if path.is_relative_to(root.resolve()) and path.is_file():
            response=web.FileResponse(path)
            if path.name=='index.html':response.headers['Cache-Control']='no-store'
            return response
    raise web.HTTPNotFound()
app=web.Application(client_max_size=4096)
import sys
sys.path.insert(0,str(Path(__file__).resolve().parent))
import activity as adapter
from activity import activity
from discord_profile import avatar_cdn,avatar_revision
from discord_events import discord_lifecycle
from discord_portal import portal_lifecycle
from guild_names import names_lifecycle
app['discord_service_factory']=get_service
from save_safety import save_lifecycle
app.cleanup_ctx.append(save_lifecycle)
app.cleanup_ctx.append(discord_lifecycle)
app.cleanup_ctx.append(portal_lifecycle)
app.cleanup_ctx.append(names_lifecycle)
app.router.add_get('/api/activity',activity);app.router.add_post('/api/activity',activity)
app.router.add_post('/api/admin',admin);app.router.add_get('/api/avatar',avatar);app.router.add_get('/api/health',health);app.router.add_post('/api/auth/discord',auth);app.router.add_get('/{path:.*}',static)
if __name__=='__main__':web.run_app(app,host='0.0.0.0',port=int(os.getenv('PORT','8080')))
