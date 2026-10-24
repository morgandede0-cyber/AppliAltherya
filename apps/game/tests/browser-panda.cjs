const {chromium}=require('@playwright/test'),assert=require('node:assert/strict'),fs=require('node:fs'),path=require('node:path'),os=require('node:os'),{spawn,execFileSync}=require('node:child_process');
const root=path.resolve(__dirname,'../../..'),tmp=fs.mkdtempSync(path.join(os.tmpdir(),'altherya-panda-')),db=path.join(tmp,'test.db'),url='http://127.0.0.1:20922';
const users=JSON.parse(execFileSync('python3',['-c',`import sys,json,time;sys.path.insert(0,'apps/api');from activity import Activity
from campaign import QUESTS
a=Activity(sys.argv[1]);out=[];idx=next(i for i,q in enumerate(QUESTS) if q['id']=='S1-Q08')
for i in range(5):
 (uid,n),token=a.session('');a.snapshot(uid,n);a.bind_discord(uid,dict(id=str(123456789012345670+i),username='Test',global_name='Enquêteur '+str(i),avatar=None,discriminator='0'),token)
 for step in range(11):a.action(uid,dict(action='tutorial_visit',step=step,destination=a.tutorial.destinations[step]));a.action(uid,dict(action='tutorial_next',step=step))
 a.action(uid,dict(action='tutorial_visit',step=11,destination=a.tutorial.destinations[11]));a.action(uid,dict(action='tutorial_finish',step=11))
 if i<4:
  with a.conn() as c:c.execute('UPDATE castle_profiles SET xp=10000 WHERE user_id=?',(uid,));c.execute('UPDATE campaign_progress SET quest_index=?,stage=1,accepted_at=?,payload=? WHERE user_id=?',(idx,time.time()-10000,json.dumps(dict(edition=4)),uid))
 out.append(dict(token=token,uid=uid))
print(json.dumps(out))`,db],{cwd:root,encoding:'utf8'}));
(async()=>{const server=spawn('python3',['apps/api/server.py'],{cwd:root,env:{...process.env,PORT:'20922',ACTIVITY_DB:db,DISCORD_BOT_TOKEN:''},stdio:'ignore'});let browser;let checks=0;const errors=[];try{
for(let i=0;i<100;i++){try{if((await fetch(url+'/api/health')).ok)break;}catch{}await new Promise(r=>setTimeout(r,100));}
browser=await chromium.launch({headless:true,executablePath:process.env.CHROMIUM_EXECUTABLE,args:JSON.parse(process.env.CHROMIUM_ARGS||'[]')});let index=0;
for(const [width,height] of [[1440,900],[1186,570],[390,844],[320,568]]){
 const user=users[index++],context=await browser.newContext({viewport:{width,height}});await context.addCookies([{name:'altherya_test',value:user.token,url}]);const p=await context.newPage();p.on('pageerror',e=>errors.push(String(e)));p.setDefaultTimeout(30000);await p.route('**/api/avatar*',r=>r.fulfill({contentType:'image/svg+xml',body:'<svg xmlns="http://www.w3.org/2000/svg" width="80" height="80"/>'}));await p.goto(url,{waitUntil:'domcontentloaded',timeout:60000});await p.locator('#launch-screen').waitFor({state:'detached'});await p.locator('#scene-stage[data-scene=hub][aria-busy=false]').waitFor();console.log('Viewport',width,height);
 for(const label of ['Replier le suivi des quêtes','Replier les quêtes quotidiennes']){const n=p.getByRole('button',{name:label,exact:true});if(await n.isVisible())await n.click();}
 const panel=p.locator('#panel'),b=name=>panel.getByRole('button',{name,exact:true});await p.getByRole('button',{name:'Monde',exact:true}).click();await b('Voyager vers Port des Brumes').click();await b('La capitainerie').click();await panel.locator('.port-stage[data-scene=capitainerie]').waitFor();const art=panel.locator('.port-stage>img');await art.evaluate(im=>im.decode());assert.match(await art.getAttribute('src'),/capitainerie\.png\?v=panda-bambou-/);checks++;
 const before=(await(await context.request.get(url+'/api/activity')).json()).state;await b('Parler à Panda').click();await panel.locator('.port-paper').filter({hasText:'Panda :'}).waitFor();const after=(await(await context.request.get(url+'/api/activity')).json()).state;assert.equal(after.port.phase,1);assert.deepEqual(after.balance,before.balance);assert.equal(after.xp,before.xp);checks++;
 const box=await panel.boundingBox();assert.ok(box.x>=-1&&box.y>=-1&&box.x+box.width<=width+1&&box.y+box.height<=height+1);assert.ok(await panel.evaluate(n=>n.scrollWidth<=n.clientWidth+2));for(const r of await panel.locator('.port-footer button').evaluateAll(es=>es.map(e=>e.getBoundingClientRect().toJSON())))assert.ok(r.x>=0&&r.right<=width+1&&r.y>=0&&r.bottom<=height+1,JSON.stringify(r));checks++;
 if(process.env.PNJ_CAPTURE==='1')await p.screenshot({animations:'disabled',timeout:60000,path:path.join(tmp,'panda-'+width+'.png')});await context.close();
}
assert.deepEqual(errors,[]);console.log(JSON.stringify({checks,errors,screenshots:tmp}));}finally{await browser?.close();server.kill();}})().catch(e=>{console.error(e);process.exitCode=1;});
