const {chromium}=require('@playwright/test'),assert=require('node:assert/strict'),fs=require('node:fs'),path=require('node:path'),os=require('node:os'),{spawn,execFileSync}=require('node:child_process');
const root=path.resolve(__dirname,'../../..'),tmp=fs.mkdtempSync(path.join(os.tmpdir(),'altherya-trade-')),db=path.join(tmp,'test.db'),url='http://127.0.0.1:20689';
const seed=JSON.parse(execFileSync('python3',['-c',`import sys,json;sys.path.insert(0,'apps/api');from activity import Activity
from trading import ITEMS
a=Activity(sys.argv[1]);out=[]
for index,(did,name) in enumerate([('123456789012345678','Vendeur du serveur'),('123456789012345679','Acheteur du serveur')]):
 (uid,n),token=a.session('');a.snapshot(uid,name);a.bind_discord(uid,dict(id=did,username='Global',global_name=name,avatar=None,discriminator='0'),token)
 for i in range(11):a.action(uid,dict(action='tutorial_visit',step=i,destination=a.tutorial.destinations[i]));a.action(uid,dict(action='tutorial_next',step=i))
 a.action(uid,dict(action='tutorial_visit',step=11,destination=a.tutorial.destinations[11]));a.action(uid,dict(action='tutorial_finish',step=11));out.append(dict(uid=uid,token=token))
 with a.conn() as c:
  c.execute('UPDATE players SET wallet_gold=10000 WHERE user_id=?',(uid,))
  for item in ITEMS:c.execute('INSERT INTO resources VALUES(?,?,?)',(uid,item,100))
for i in range(4):a.action(out[0]['uid'],dict(action='trade_create',item='Pierre brute',quantity=i+1,price=50))
with a.conn() as c:c.execute("UPDATE activity_trade_offers SET expires_at=strftime('%s','now')+175 WHERE id=(SELECT id FROM activity_trade_offers LIMIT 1)")
print(json.dumps(out))`,db],{cwd:root,encoding:'utf8'}));
(async()=>{const server=spawn('python3',['apps/api/server.py'],{cwd:root,env:{...process.env,PORT:'20689',ACTIVITY_DB:db,DISCORD_BOT_TOKEN:''},stdio:'ignore'});let browser,checks=0;const errors=[];
try{for(let i=0;i<100;i++){try{if((await fetch(url+'/api/health')).ok)break;}catch{}await new Promise(r=>setTimeout(r,100));}
browser=await chromium.launch({headless:true,dumpio:!!process.env.BROWSER_DEBUG,executablePath:process.env.CHROMIUM_EXECUTABLE,args:JSON.parse(process.env.CHROMIUM_ARGS||'[]')});
for(const [width,height] of JSON.parse(process.env.TRADE_VIEWPORTS||'[[1440,900],[1186,570],[390,844],[320,568]]')){
 execFileSync('python3',['-c',"import sqlite3,sys; c=sqlite3.connect(sys.argv[1]); c.execute(\"UPDATE activity_trade_offers SET expires_at=strftime('%s','now')+175 WHERE id=(SELECT id FROM activity_trade_offers WHERE status='active' AND seller=? ORDER BY expires_at LIMIT 1)\",(int(sys.argv[2]),)); c.commit()",db,String(seed[0].uid)]);
 console.log('Viewport',width,height);const context=await browser.newContext({viewport:{width,height}});await context.addCookies([{name:'altherya_test',value:seed[1].token,url}]);const page=await context.newPage();page.setDefaultTimeout(30000);page.on('pageerror',e=>{errors.push(String(e));console.error('Page error',String(e));});page.on('response',r=>{if(r.status()>=400)console.error('HTTP',r.status(),r.url());});await page.goto(url);await page.locator('#scene-stage[data-scene=hub][aria-busy=false]').waitFor().catch(async e=>{await page.screenshot({path:path.join(tmp,'failed-launch.png')});console.error('Launch',await page.locator('body').innerText(),tmp);throw e;});
 for(const name of ['Replier le suivi des quêtes','Replier les quêtes quotidiennes']){const b=page.getByRole('button',{name,exact:true});if(await b.isVisible())await b.click();}
 await page.getByRole('button',{name:/march/i}).first().click();await page.screenshot({path:path.join(tmp,'merchant-'+width+'.png')});console.log('Open trade');await page.getByRole('button',{name:'Comptoir des joueurs',exact:true}).click();console.log('Trade opened');const panel=page.locator('#panel[data-kind=trade]');await panel.locator('.trade-row:not(.trade-head)').first().waitFor();
 assert.ok(await panel.locator('.trade-tabs button').evaluateAll(buttons=>buttons.every(b=>b.scrollWidth<=b.clientWidth)), 'Tab labels must fit their buttons: '+JSON.stringify(await panel.locator('.trade-tabs button').evaluateAll(buttons=>buttons.map(b=>({label:b.textContent,width:b.clientWidth,scroll:b.scrollWidth,font:getComputedStyle(b).fontSize,padding:getComputedStyle(b).padding})))));
 const box=await panel.boundingBox();assert.ok(box.x>=0&&box.x+box.width<=width+1&&box.y>=0&&box.y+box.height<=height+1,JSON.stringify({box,width,height}));checks++;
 const rows=panel.locator('.trade-row:not(.trade-head)');assert.equal(await rows.count(),4);checks++;
 const times=panel.locator('.trade-time');assert.match(await times.first().innerText(),/^\d{2}:\d{2}:\d{2}$/);assert.equal(await panel.locator('.trade-time.trade-urgent').count(),1);const before=await times.first().innerText();await page.waitForFunction(value=>document.querySelector('#panel .trade-time')?.textContent!==value,before,{timeout:8000});assert.notEqual(await times.first().innerText(),before);checks+=3;
 assert.equal(await rows.first().locator('.item-asset').count(),1);assert.equal(await rows.first().locator('.trade-seller').innerText(),'Vendeur du serveur');checks+=2;
 const geometry=await rows.first().evaluate(row=>{const r=row.getBoundingClientRect();return [...row.children].map(c=>{const b=c.getBoundingClientRect();return Math.abs((b.top+b.bottom)/2-(r.top+r.bottom)/2);});});assert.ok(geometry.every(n=>n<2),JSON.stringify(geometry));checks++;
 await page.screenshot({path:path.join(tmp,'trade-list-'+width+'.png')});
 const firstId=await rows.first().getAttribute('data-offer');const response=await context.request.get(url+'/api/activity');const wallet=(await response.json()).state.balance.wallet;
 await rows.first().getByRole('button',{name:'Acheter',exact:true}).click();await rows.first().getByRole('button',{name:'Confirmer',exact:true}).click();await panel.getByRole('status').filter({hasText:'Achat effectué'}).waitFor();await panel.locator(`[data-offer="${firstId}"]`).waitFor({state:'detached'});assert.equal((await(await context.request.get(url+'/api/activity')).json()).state.balance.wallet,wallet-50);checks++;
 // Refill to keep four rows for each viewport.
 await fetch(url+'/api/activity',{method:'POST',headers:{'X-Altherya-Request':'1','Cookie':'altherya_test='+seed[0].token,'Content-Type':'application/json'},body:JSON.stringify({action:'trade_create',item:'Pierre brute',quantity:1,price:50})});
 await panel.getByRole('button',{name:'Mettre en vente',exact:true}).click();await panel.locator('.trade-stock-item').first().waitFor().catch(async e=>{console.error('Sell state',await panel.innerText());await page.screenshot({path:path.join(tmp,'failed-sell-'+width+'.png')});throw e;});assert.equal(await panel.locator('.trade-stock-item').count(),4);await panel.locator('.trade-stock-item').first().click();await panel.getByRole('spinbutton',{name:'Quantité du lot',exact:true}).fill('2');await panel.getByRole('spinbutton',{name:'Prix total du lot (Gold)',exact:true}).fill('73');await page.screenshot({path:path.join(tmp,'trade-compose-'+width+'.png')});await panel.getByRole('button',{name:'Publier le lot',exact:true}).click();await panel.getByRole('status').filter({hasText:'Lot publié'}).waitFor();await panel.locator('.trade-row:not(.trade-head)').first().waitFor();await panel.getByRole('button',{name:'Annuler',exact:true}).first().click();await panel.getByRole('status').filter({hasText:'Annonce annulée'}).waitFor();checks+=3;
 await panel.getByRole('button',{name:'Retour au marchand',exact:true}).click();await page.locator('#panel[data-kind=market]').waitFor();assert.equal(errors.length,0,errors.join('\n'));await context.close();
}
console.log(JSON.stringify({checks,errors,screenshots:tmp}));
}finally{await browser?.close();server.kill();await new Promise(r=>{if(server.exitCode!==null)r();else server.once('exit',r);});}
})().catch(e=>{console.error(e);process.exitCode=1;});
