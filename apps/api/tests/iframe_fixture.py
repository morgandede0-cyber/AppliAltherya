"""Local browser test fixture only; never imported by the production gateway."""
if __name__=='__main__':
 import sys,ssl,os
 from pathlib import Path
 sys.path.insert(0,str(Path(__file__).parents[1]))
 from aiohttp import web
 import server,activity as adapter
 from test_discord_profile import FakeSession
 adapter.SERVICE=adapter.Activity(sys.argv[1]);server.ClientSession=FakeSession
 os.environ['DISCORD_CLIENT_ID']='123456789012345678';os.environ['DISCORD_CLIENT_SECRET']='fake-local-test'
 async def parent(request):return web.Response(text='<iframe src="https://localhost:20599/probe"></iframe>',content_type='text/html')
 async def probe(request):return web.Response(text='<p>Cookie test</p>',content_type='text/html')
 async def legacy(request):
  r=web.json_response(dict(present=bool(request.cookies.get('legacy_probe'))));r.set_cookie('legacy_probe','test',secure=True,httponly=True,samesite='Strict');return r
 from request_security import api_security
 app=web.Application(middlewares=[api_security(server.get_service)]);app.router.add_get('/parent',parent);app.router.add_get('/probe',probe);app.router.add_get('/legacy',legacy)
 app.router.add_get('/api/activity',adapter.activity);app.router.add_post('/api/activity',adapter.activity);app.router.add_post('/api/auth/discord',server.auth);app.router.add_post('/api/admin',server.admin)
 context=ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER);context.load_cert_chain(sys.argv[2],sys.argv[3]);web.run_app(app,host='0.0.0.0',port=20599,ssl_context=context,print=None)
