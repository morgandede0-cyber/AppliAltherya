const {chromium}=require('@playwright/test'),assert=require('node:assert/strict'),fs=require('node:fs'),path=require('node:path'),os=require('node:os'),{spawn,execFileSync}=require('node:child_process');
const root=path.resolve(__dirname,'../../..'),tmp=fs.mkdtempSync(path.join(os.tmpdir(),'altherya-models-')),db=path.join(tmp,'state.db'),url='http://127.0.0.1:20683';
const users=JSON.parse(execFileSync('python3',['-c',`import sys,json;sys.path.insert(0,'apps/api');from activity import Activity
a=Activity(sys.argv[1]);out=[]
for i in range(4):
 (uid,name),token=a.session('');a.snapshot(uid,name);u=dict(id=str(123456789012345670+i),username='Compte',global_name='Global',avatar='a'*32,discriminator='0');uid=a.bind_discord(uid,u,token);a.guild_names.record_member(uid,'123456789012345679',dict(user=u,nick='Gardien du serveur '+str(i)))
 with a.conn() as c:
  c.execute('UPDATE tutorial_progress SET completed=1 WHERE user_id=?',(uid,));c.execute('UPDATE activity_tutorial_revision SET finished=1 WHERE user_id=?',(uid,));c.execute('UPDATE players SET wallet_gold=5000 WHERE user_id=?',(uid,))
 out.append(dict(uid=uid,token=token))
print(json.dumps(out))`,db],{cwd:root,encoding:'utf8'}));
(async()=>{const server=spawn('python3',['apps/api/server.py'],{cwd:root,env:{...process.env,PORT:'20683',ACTIVITY_DB:db,DISCORD_BOT_TOKEN:''},stdio:'ignore'});let browser,checks=0;const errors=[];
try{for(let i=0;i<100;i++){try{if((await fetch(url+'/api/health')).ok)break;}catch{}await new Promise(r=>setTimeout(r,100));}browser=await chromium.launch({headless:true,executablePath:process.env.CHROMIUM_EXECUTABLE,args:JSON.parse(process.env.CHROMIUM_ARGS||'[]')});
for(const [i,[width,height]] of [[1440,900],[1186,570],[390,844],[320,568]].entries()){
 const ctx=await browser.newContext({viewport:{width,height}});await ctx.addCookies([{name:'altherya_test',value:users[i].token,url}]);const p=await ctx.newPage();p.setDefaultTimeout(45000);p.on('pageerror',e=>errors.push(String(e)));await p.route('**/api/avatar*',r=>r.fulfill({contentType:'image/svg+xml',body:'<svg xmlns="http://www.w3.org/2000/svg" width="100" height="100"><rect width="100" height="100" fill="#426269"/><circle cx="50" cy="40" r="25" fill="#e1c490"/></svg>'}));
 const panel=p.locator('#panel'),b=name=>panel.getByRole('button',{name,exact:true}),state=async()=>(await(await p.request.get(url+'/api/activity')).json()).state;
 async function home(){await p.goto(url);await p.locator('#launch-screen').waitFor({state:'detached'});await p.locator('#scene-stage[aria-busy="false"]').waitFor();for(const label of ['Replier le suivi des quêtes','Replier les quêtes quotidiennes']){const n=p.getByRole('button',{name:label,exact:true});if(await n.count())await n.click();}}
 async function enter(name){await home();await p.getByRole('button',{name,exact:true}).click();await panel.locator('.realm-inner,.arena-inner').waitFor();}
 async function shot(name){assert.ok(await panel.evaluate(n=>n.scrollWidth<=n.clientWidth+2),name+' width');const r=await panel.boundingBox();assert.ok(r.x>=-1&&r.y>=-1&&r.x+r.width<=width+1&&r.y+r.height<=height+1,name+' bounds');await p.screenshot({path:path.join(tmp,`${name}-${width}.png`),animations:'disabled'});checks++;}
 for(const [label,name] of [['Marché','merchant'],['Forge','forge'],['Taverne','tavern'],['Petites annonces','jobs'],['Arène','arena']]){await enter(label);await shot(name);if(label==='Marché')assert.equal(await panel.locator('.realm-product').count(),4);if(label==='Taverne')assert.equal(await panel.locator('.approved-tavern-card').count(),3);assert.ok(await panel.locator('.approved-button-fill').count()>0);assert.equal(await p.locator('#hud').isVisible(),false);}
 const s=await state();assert.equal(s.catalog.axe.price,400);assert.equal(s.tutorial.gold,100);assert.equal(s.tutorial.xp,25);checks++;await ctx.close();
}assert.deepEqual(errors,[]);console.log(JSON.stringify({checks,errors,screenshots:tmp}));}finally{await browser?.close();server.kill();}})().catch(e=>{console.error(e);process.exitCode=1;});
