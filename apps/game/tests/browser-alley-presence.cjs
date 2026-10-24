/* Actual built game + API; presence windows and accounts exist only in a temp DB. */
const {chromium}=require('@playwright/test'),assert=require('node:assert/strict'),fs=require('node:fs'),path=require('node:path'),os=require('node:os'),{spawn,execFileSync}=require('node:child_process');
const root=path.resolve(__dirname,'../../..'),tmp=fs.mkdtempSync(path.join(os.tmpdir(),'alley-presence-')),db=path.join(tmp,'test.db'),url='http://127.0.0.1:20942';
const python=(code,...args)=>execFileSync('python3',['-c',code,db,...args],{cwd:root,encoding:'utf8'});
const tokens=JSON.parse(python(`import sys,json;sys.path.insert(0,'apps/api');from activity import Activity
a=Activity(sys.argv[1]);out=[]
with a.conn() as c:a.smogo.presence(c);c.execute("UPDATE activity_smogo_visits SET windows='[]'")
for i in range(3):
 (uid,name),token=a.session('');a.snapshot(uid,name)
 for step in range(11):a.action(uid,dict(action='tutorial_visit',step=step,destination=a.tutorial.destinations[step]));a.action(uid,dict(action='tutorial_next',step=step))
 a.action(uid,dict(action='tutorial_visit',step=11,destination=a.tutorial.destinations[11]));a.action(uid,dict(action='tutorial_finish',step=11));out.append(token)
print(json.dumps(out))`));
const visit=seconds=>python(`import sqlite3,sys,time,json;c=sqlite3.connect(sys.argv[1]);n=time.time();c.execute('UPDATE activity_smogo_visits SET windows=?',(json.dumps([[n-10,n+int(sys.argv[2])]]) if int(sys.argv[2]) else '[]',));c.commit()`,String(seconds));
(async()=>{let browser;const errors=[];let checks=0;const server=spawn('python3',['apps/api/server.py'],{cwd:root,env:{...process.env,PORT:'20942',ACTIVITY_DB:db,DISCORD_CLIENT_ID:'',DISCORD_CLIENT_SECRET:'',DISCORD_BOT_TOKEN:''},stdio:'ignore'});try{
 for(let i=0;i<100;i++){try{if((await fetch(url+'/api/health')).ok)break;}catch{}await new Promise(r=>setTimeout(r,100));}
 browser=await chromium.launch({headless:true,executablePath:process.env.CHROMIUM_EXECUTABLE,args:JSON.parse(process.env.CHROMIUM_ARGS||'[]')});
 for(const [i,[width,height]] of [[1440,900],[390,844],[320,568]].entries()){
 visit(0);const ctx=await browser.newContext({viewport:{width,height}});await ctx.addCookies([{name:'altherya_test',value:tokens[i],url}]);const p=await ctx.newPage();p.setDefaultTimeout(30000);p.on('pageerror',e=>errors.push(String(e)));const stage=p.locator('#scene-stage'),panel=p.locator('#panel'),b=name=>p.getByRole('button',{name,exact:true}),snapshot=async()=>(await(await ctx.request.get(url+'/api/activity')).json()).state;
 await p.goto(url,{waitUntil:'domcontentloaded'});await p.locator('#scene-stage[data-scene=hub][aria-busy=false]').waitFor();for(const id of ['#daily-quest-tracker','#quest-tracker']){const t=p.locator(id+' .quest-toggle');if(await t.getAttribute('aria-expanded')==='true')await t.click();}
 async function alley(){await b('Ruelle sombre').click();await p.locator('#scene-stage[data-scene=alley][aria-busy=false]').waitFor();}
 async function artwork(present){await p.locator('#scene-stage[data-smogo-presence='+(present?'present':'absent')+']').waitFor();assert.ok((await stage.locator(':scope > img').getAttribute('src')).endsWith(present?'alley-smogo-present-v2.png':'alley-smogo-absent-v2.png'));assert.equal(await stage.locator('[data-smogo-character]').isVisible(),present);assert.equal(await stage.locator('[data-smogo-character]').isDisabled(),!present);for(const label of ['Le voleur','Le braqueur','Le vigile','Retour au hub'])assert.ok(await b(label).isVisible());const box=await stage.boundingBox();for(const el of await stage.locator('.city-panel-button').all()){const a=await el.boundingBox();assert.ok(a.x>=box.x-1&&a.y>=box.y-1&&a.x+a.width<=box.x+box.width+1&&a.y+a.height<=box.y+box.height+1);}checks++;}
 await alley();await artwork(false);assert.equal(await b('Reprendre l’énigme').isVisible(),false);await p.screenshot({path:path.join(tmp,'absent-'+width+'.png')});checks++;
 visit(90);await b('Retour au hub').click();await p.locator('#scene-stage[data-scene=hub][aria-busy=false]').waitFor();await alley();await artwork(true);assert.equal(await b('Reprendre l’énigme').isVisible(),false);const area=await stage.locator('[data-smogo-character]').boundingBox(),scene=await stage.boundingBox();assert.ok(area.x>=scene.x&&area.x+area.width<=scene.x+scene.width);await p.screenshot({path:path.join(tmp,'present-'+width+'.png')});checks++;
 await b('Smogo').click();await panel.locator('#smogo-wager').waitFor();const before=await snapshot();await panel.locator('#smogo-wager').fill('10');await b('Miser et découvrir l’énigme').click();await b('Confirmer').click();await panel.locator('#smogo-answer').waitFor();const paid=await snapshot();assert.equal(paid.balance.wallet,before.balance.wallet-10);checks++;
 visit(0);await b('Retour à la ruelle').click();await p.locator('#scene-stage[data-scene=alley][aria-busy=false]').waitFor();await artwork(false);assert.ok(await b('Reprendre l’énigme').isVisible());await b('Reprendre l’énigme').click();await panel.locator('#smogo-answer').waitFor();const resumed=await snapshot();assert.deepEqual(resumed.smogo.round,paid.smogo.round);assert.equal(resumed.balance.wallet,paid.balance.wallet);checks++;
 await b('Retour à la ruelle').click();await p.locator('#scene-stage[data-scene=alley][aria-busy=false]').waitFor();visit(10);await b('Retour au hub').click();await p.locator('#scene-stage[data-scene=hub][aria-busy=false]').waitFor();await alley();await artwork(true);await artwork(false);assert.ok(await b('Reprendre l’énigme').isVisible());checks++;
 await ctx.close();console.log('Viewport passed',width,height);
 }
 assert.deepEqual(errors,[]);console.log(JSON.stringify({checks,errors,artifacts:tmp}));
 }finally{await browser?.close();server.kill();}})().catch(e=>{console.error(e);process.exitCode=1;});
