"""Local HTTP smoke load, isolated DB; not a production capacity benchmark."""
import asyncio,json,statistics,sys,tempfile,time
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'apps'/'api'))
from aiohttp import ClientSession,CookieJar,web
from aiohttp.test_utils import TestServer
import activity as adapter
from activity import Activity
async def main():
 with tempfile.TemporaryDirectory() as temp:
  a=Activity(temp+'/load.db');old=adapter.SERVICE;adapter.SERVICE=a
  app=web.Application(client_max_size=4096);app.router.add_get('/api/activity',adapter.activity);app.router.add_post('/api/activity',adapter.activity);server=TestServer(app);await server.start_server();url=str(server.make_url('/api/activity'));sessions=[];uids=[];latencies=[];statuses=[]
  try:
   for i in range(16):
    (uid,name),token=a.session('');a.snapshot(uid,name);uids.append(uid)
    with a.conn() as c:c.execute('UPDATE tutorial_progress SET completed=1 WHERE user_id=?',(uid,));c.execute('UPDATE activity_tutorial_revision SET finished=1 WHERE user_id=?',(uid,));c.execute('UPDATE players SET wallet_gold=1000 WHERE user_id=?',(uid,))
    sessions.append(ClientSession(cookie_jar=CookieJar(unsafe=True),cookies={'altherya_test':token},headers={'X-Altherya-Request':'1'}))
   async def worker(n,session):
    for i in range(20):
     body=dict(action='deposit' if i%2==0 else 'withdraw',amount=1,request_id=f'http-load-user-{n:02}-{i:03}')
     start=time.perf_counter()
     async with session.post(url,json=body) as r:
      statuses.append(r.status);result=await r.json();assert r.status==200,result
     latencies.append((time.perf_counter()-start)*1000)
     async with session.get(url) as r:statuses.append(r.status);assert r.status==200;await r.read()
   start=time.perf_counter();await asyncio.gather(*(worker(i,s) for i,s in enumerate(sessions)));elapsed=time.perf_counter()-start
   for uid in uids:
    b=a.economy.get_balance(uid);assert (b.wallet,b.bank)==(991,0),(b.wallet,b.bank)
   with a.conn() as c:assert c.execute('PRAGMA integrity_check').fetchone()[0]=='ok'
   print(json.dumps(dict(users=16,posts=320,gets=320,success_responses=len(statuses),elapsed_seconds=round(elapsed,3),post_latency_median_ms=round(statistics.median(latencies),2),post_latency_p95_ms=round(sorted(latencies)[int(.95*len(latencies))-1],2),wallet_per_user=991,bank_per_user=0,sqlite_integrity='ok',scope='local HTTP only; concurrent browser suites share host; no production capacity claim')))
  finally:
   for session in sessions:await session.close()
   await server.close();adapter.SERVICE=old
asyncio.run(main())
