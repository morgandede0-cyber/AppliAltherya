const {chromium}=require('@playwright/test'),assert=require('node:assert/strict'),fs=require('node:fs'),path=require('node:path'),os=require('node:os'),{spawn,execFileSync}=require('node:child_process');
const root=path.resolve(__dirname,'../../..'),tmp=fs.mkdtempSync(path.join(os.tmpdir(),'altherya-castle-')),db=path.join(tmp,'state.db'),url='http://127.0.0.1:20686';
const users=JSON.parse(execFileSync('python3',['-c',`import sys,json;sys.path.insert(0,'apps/api');from activity import Activity
a=Activity(sys.argv[1]);out=[]
for i in range(4):
 (uid,name),token=a.session('');a.snapshot(uid,name);u=dict(id=str(123456789012345670+i),username='Compte',global_name='Global',avatar='a'*32,discriminator='0');uid=a.bind_discord(uid,u,token);a.guild_names.record_member(uid,'123456789012345679',dict(user=u,nick='Gardien du serveur '+str(i)))
 with a.conn() as c:
  c.execute('UPDATE tutorial_progress SET completed=1 WHERE user_id=?',(uid,));c.execute('UPDATE activity_tutorial_revision SET finished=1 WHERE user_id=?',(uid,));c.execute('UPDATE players SET wallet_gold=5000 WHERE user_id=?',(uid,))
 out.append(dict(uid=uid,token=token))
print(json.dumps(out))`,db],{cwd:root,encoding:'utf8'}));
(async()=>{const server=spawn('python3',['apps/api/server.py'],{cwd:root,env:{...process.env,PORT:'20686',ACTIVITY_DB:db,DISCORD_BOT_TOKEN:''},stdio:'ignore'});let browser,checks=0;const errors=[];
try{for(let i=0;i<100;i++){try{if((await fetch(url+'/api/health')).ok)break;}catch{}await new Promise(r=>setTimeout(r,100));}browser=await chromium.launch({headless:true,executablePath:process.env.CHROMIUM_EXECUTABLE,args:JSON.parse(process.env.CHROMIUM_ARGS||'[]')});
for(const [i,[width,height]] of [[1440,900],[1186,570],[390,844],[320,568]].entries()){
 const ctx=await browser.newContext({viewport:{width,height}});await ctx.addCookies([{name:'altherya_test',value:users[i].token,url}]);const p=await ctx.newPage();p.setDefaultTimeout(45000);p.on('pageerror',e=>errors.push(String(e)));await p.route('**/api/avatar*',r=>r.fulfill({contentType:'image/svg+xml',body:'<svg xmlns="http://www.w3.org/2000/svg" width="100" height="100"><rect width="100" height="100" fill="#426269"/><circle cx="50" cy="40" r="25" fill="#e1c490"/></svg>'}));
 const panel=p.locator('#panel'),b=name=>panel.getByRole('button',{name,exact:true}),state=async()=>(await(await p.request.get(url+'/api/activity')).json()).state;
 async function home(){await p.goto(url);await p.locator('#launch-screen').waitFor({state:'detached'});await p.locator('#scene-stage[aria-busy="false"]').waitFor();for(const label of ['Replier le suivi des quêtes','Replier les quêtes quotidiennes']){const n=p.getByRole('button',{name:label,exact:true});if(await n.count())await n.click();}}
 async function enter(name){await home();await p.getByRole('button',{name,exact:true}).click();await panel.locator('.realm-inner').waitFor();}
 async function shot(name){assert.ok(await panel.evaluate(n=>n.scrollWidth<=n.clientWidth+2),name+' width');const r=await panel.boundingBox();assert.ok(r.x>=-1&&r.y>=-1&&r.x+r.width<=width+1&&r.y+r.height<=height+1,name+' bounds');await p.screenshot({path:path.join(tmp,`${name}-${width}.png`),animations:'disabled'});checks++;}
 await enter('Château');await shot('castle');
 const before=await state();assert.equal(await panel.locator('.castle-path').count(),3);checks++;
 await b('Récupérer').click();await b('Déjà récupérée').waitFor();assert.equal(await b('Déjà récupérée').isDisabled(),true);const after=await state();assert.equal(after.balance.wallet,before.balance.wallet+before.daily_reward.gold);checks+=2;
 await b('Voir mon parcours').click();await panel.locator('.castle-identity img').waitFor();assert.match(await panel.locator('.castle-identity').innerText(),/Gardien du serveur/);await shot('dashboard');
 const first=await panel.locator('progress').getAttribute('value');await b('Actualiser').click();await p.waitForFunction(()=>document.querySelector('#panel')?.getAttribute('aria-busy')==='false');assert.equal(await panel.locator('progress').getAttribute('value'),first);checks++;
 await b('Retour au château').click();await b('Voir le classement').click();await panel.locator('.castle-podium').waitFor();await shot('podium');assert.equal(await panel.locator('.castle-pedestal').count(),3);assert.equal(await panel.locator('.castle-podium img').count(),3);assert.doesNotMatch(await panel.innerText(),/Global/);checks++;
 for(const button of await panel.locator('button:visible').all()){await button.scrollIntoViewIfNeeded();const r=await button.boundingBox();assert.ok(r.x>=0&&r.x+r.width<=width+1,'button inside viewport');checks++;}
 assert.ok(await panel.locator('.realm-body').evaluate(n=>n.scrollWidth<=n.clientWidth+2),'body no horizontal overflow');checks++;
 await b('Retour au château').click();await b('Retour au hub').click();await panel.waitFor({state:'hidden'});checks++;
 await ctx.close();
}assert.deepEqual(errors,[]);console.log(JSON.stringify({checks,errors,screenshots:tmp}));}finally{await browser?.close();server.kill();}})().catch(e=>{console.error(e);process.exitCode=1;});
