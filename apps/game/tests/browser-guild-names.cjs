const {chromium}=require('@playwright/test'),assert=require('node:assert/strict'),fs=require('node:fs'),path=require('node:path'),os=require('node:os'),{spawn,execFileSync}=require('node:child_process');
const root=path.resolve(__dirname,'../../..'),tmp=fs.mkdtempSync(path.join(os.tmpdir(),'altherya-guild-names-')),db=path.join(tmp,'test.db'),url='http://127.0.0.1:20607';
const names=['❖ [IV] Gardien du Royaume','★ Panda [Explorateur]'];
const tokens=JSON.parse(execFileSync('python3',['-c',`import sys,json;sys.path.insert(0,'apps/api')
from activity import Activity
a=Activity(sys.argv[1]);tokens=[]
for i,nick in enumerate(['❖ [IV] Gardien du Royaume','★ Panda [Explorateur]']):
 (uid,_),token=a.session('');a.snapshot(uid,'Test');user=dict(id='666805849011912705' if i==0 else '342359563791761411',username='admin' if i==0 else 'joueur1',global_name='Compte global '+str(i),avatar=None,discriminator='0');a.bind_discord(uid,user,token)
 for step in range(5):a.action(uid,dict(action='tutorial_next',step=step))
 a.action(uid,dict(action='tutorial_finish',step=5));a.guild_names.record_member(uid,'123456789012345679',dict(user=user,nick=nick));tokens.append(token)
print(json.dumps(tokens))`,db],{cwd:root,encoding:'utf8'}));
(async()=>{const server=spawn('python3',['apps/api/server.py'],{cwd:root,env:{...process.env,PORT:'20607',ACTIVITY_DB:db,DISCORD_BOT_TOKEN:''},stdio:'ignore'});let browser,checks=0;const errors=[];
try{for(let i=0;i<100;i++){try{if((await fetch(url+'/api/health')).ok)break;}catch{}await new Promise(r=>setTimeout(r,100));}browser=await chromium.launch({headless:true,executablePath:process.env.CHROMIUM_EXECUTABLE,args:JSON.parse(process.env.CHROMIUM_ARGS||'[]')});
for(const [width,height] of [[1440,900],[1186,570],[390,844]]){const ctx=await browser.newContext({viewport:{width,height}});await ctx.addCookies([{name:'altherya_test',value:tokens[0],url}]);const p=await ctx.newPage();p.on('pageerror',e=>errors.push(String(e)));await p.route('**/api/avatar*',r=>r.fulfill({status:404}));await p.goto(url);await p.locator('#scene-stage[aria-busy="false"]').waitFor();assert.match(await p.locator('#hud').textContent(),/Gardien du Royaume/);checks++;
await p.getByRole('button',{name:'Mon profil',exact:true}).click();const panel=p.locator('#panel');await panel.locator('.pp-name').waitFor();assert.equal(await panel.locator('.pp-name').innerText(),names[0]);checks++;await p.screenshot({path:path.join(tmp,'profile-'+width+'.png')});const box=await panel.boundingBox();assert.ok(box.x>=-1&&box.x+box.width<=width+1);assert.ok(await panel.evaluate(n=>n.scrollWidth<=n.clientWidth+2));checks++;
await p.keyboard.press('Escape');await panel.waitFor({state:'hidden'});await p.getByRole('button',{name:'Admin',exact:true}).click();const admin=p.locator('#panel[data-kind="admin"]');await admin.getByRole('searchbox',{name:'Rechercher un joueur'}).fill('joueur1');await admin.getByRole('button',{name:names[1],exact:true}).click();assert.equal(await admin.locator('.admin-identity h3').innerText(),names[1]);checks++;await p.screenshot({path:path.join(tmp,'admin-'+width+'.png')});assert.ok(await admin.evaluate(n=>n.scrollWidth<=n.clientWidth+2));checks++;await ctx.close();}
assert.deepEqual(errors,[]);console.log(JSON.stringify({checks,errors,screenshots:tmp}));}finally{await browser?.close();server.kill();}})().catch(e=>{console.error(e);process.exitCode=1});
