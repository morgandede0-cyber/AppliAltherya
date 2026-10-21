const {chromium}=require('@playwright/test'),assert=require('node:assert/strict'),fs=require('node:fs'),path=require('node:path'),os=require('node:os'),{spawn,execFileSync}=require('node:child_process');
const root=path.resolve(__dirname,'../../..'),tmp=fs.mkdtempSync(path.join(os.tmpdir(),'altherya-arena-complete-')),db=path.join(tmp,'state.db'),url='http://127.0.0.1:20672';
const users=JSON.parse(execFileSync('python3',['-c',`import sys,json;sys.path.insert(0,'apps/api');from activity import Activity
a=Activity(sys.argv[1]);result=[]
for i in range(4):
 (uid,name),token=a.session('');a.snapshot(uid,name)
 user=dict(id=str(123456789012345670+i),username='compte_global',global_name='Nom global',avatar='aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa',discriminator='0');uid=a.bind_discord(uid,user,token);a.guild_names.record_member(uid,'123456789012345678',dict(user=user,nick='Gardien du serveur '+str(i)))
 with a.conn() as c:
  c.execute('UPDATE tutorial_progress SET completed=1 WHERE user_id=?',(uid,));c.execute('UPDATE activity_tutorial_revision SET finished=1 WHERE user_id=?',(uid,));c.execute('UPDATE players SET wallet_gold=1000 WHERE user_id=?',(uid,))
 result.append(dict(uid=uid,token=token))
print(json.dumps(result))`,db],{cwd:root,encoding:'utf8'}));
function sql(code,uid){execFileSync('python3',['-c',`import sqlite3,json,sys;c=sqlite3.connect(sys.argv[1]);uid=int(sys.argv[2]);${code};c.commit()`,db,String(uid)],{cwd:root});}
(async()=>{const server=spawn('python3',['apps/api/server.py'],{cwd:root,env:{...process.env,PORT:'20672',ACTIVITY_DB:db,DISCORD_BOT_TOKEN:''},stdio:'ignore'});let browser;const errors=[];let checks=0;
try{
 for(let i=0;i<100;i++){try{if((await fetch(url+'/api/health')).ok)break;}catch{}await new Promise(r=>setTimeout(r,100));}
 browser=await chromium.launch({headless:true,executablePath:process.env.CHROMIUM_EXECUTABLE,args:JSON.parse(process.env.CHROMIUM_ARGS||'[]')});
 for(const [index,[width,height]] of [[1440,900],[1186,570],[390,844],[320,568]].slice(0,Number(process.env.ARENA_TEST_VIEWPORTS||4)).entries()){
  const user=users[index],ctx=await browser.newContext({viewport:{width,height},reducedMotion:width===320?'reduce':'no-preference'});await ctx.addCookies([{name:'altherya_test',value:user.token,url}]);const p=await ctx.newPage();p.setDefaultTimeout(60000);p.on('pageerror',e=>errors.push(String(e)));
  await p.route('**/api/avatar*',r=>width===320?r.fulfill({status:404,body:''}):r.fulfill({contentType:'image/svg+xml',body:'<svg xmlns="http://www.w3.org/2000/svg" width="120" height="120"><rect width="120" height="120" fill="#638577"/><circle cx="60" cy="45" r="22" fill="#eed4a4"/><path d="M20 120Q20 65 60 70Q100 65 100 120" fill="#253e4b"/></svg>'}));const panel=p.locator('#panel'),button=name=>panel.getByRole('button',{name,exact:true}),state=async()=>(await(await p.request.get(url+'/api/activity')).json()).state;
  async function home(){await p.goto(url);await p.locator('#launch-screen').waitFor({state:'detached'});await p.locator('#scene-stage[aria-busy="false"]').waitFor();for(const label of ['Replier le suivi des quêtes','Replier les quêtes quotidiennes']){const b=p.getByRole('button',{name:label,exact:true});if(await b.count())await b.click();}}
  async function lobby(){await home();await p.getByRole('button',{name:'Arène',exact:true}).click();await panel.locator('.arena-summary').waitFor();}
  async function shot(name){assert.ok(await panel.evaluate(n=>n.scrollWidth<=n.clientWidth+2),name+' horizontal bounds');const r=await panel.boundingBox();assert.ok(r.x>=-1&&r.y>=-1&&r.x+r.width<=width+1&&r.y+r.height<=height+1,name+' viewport');await p.screenshot({timeout:60000,animations:'disabled',path:path.join(tmp,`${name}-${width}.png`)});checks++;}
  await lobby();await shot('wager-lobby');
  const input=panel.getByRole('textbox',{name:'Mise du combat'});
  await input.fill('');assert.ok(await button('Affronter le champion').isDisabled());
  await input.fill('1.5');assert.ok(await button('Affronter le champion').isDisabled());
  await button('Mise maximale').click();assert.equal(await input.inputValue(),'500');assert.ok(await button('Augmenter la mise').isDisabled());
  await button('Sans mise').click();assert.equal(await input.inputValue(),'0');assert.ok(await button('Diminuer la mise').isDisabled());
  await button('50 Gold').click();await button('Affronter le champion').click();await shot('wager-confirmation');
  const requests=[];p.on('request',r=>{if(r.method()==='POST'&&r.url().includes('/api/')){try{const b=r.postDataJSON();if(b.action==='battle_start')requests.push(b);}catch{}}});
  await button('Commencer le combat').click();await p.locator('#panel[data-kind="combat"][aria-busy="false"]').waitFor();
  const actual=await state();assert.equal(actual.balance.wallet,950);assert.equal(actual.play.wager,50);assert.equal(requests.length,1);assert.equal(requests[0].wager,50);checks+=8;
  await ctx.close();
 }
 assert.deepEqual(errors,[]);console.log(JSON.stringify({checks,errors,screenshots:tmp}));
}finally{await browser?.close();server.kill();}})().catch(e=>{console.error(e);process.exitCode=1;});
