const {chromium}=require('@playwright/test'),assert=require('node:assert/strict'),fs=require('node:fs'),path=require('node:path'),os=require('node:os'),{spawn,spawnSync}=require('node:child_process');
(async()=>{
 const temp=fs.mkdtempSync(path.join(os.tmpdir(),'altherya-roulette-layout-')),root=path.resolve(__dirname,'../../..'),port=process.env.ROULETTE_PORT||'8154',url='http://127.0.0.1:'+port,db=path.join(temp,'test.db');
 const server=spawn('python3',['apps/api/server.py'],{cwd:root,env:{...process.env,PORT:port,ACTIVITY_DB:db,DISCORD_BOT_TOKEN:''},stdio:'ignore'});let browser;
 try{
  for(let i=0;i<120;i++){try{if((await fetch(url+'/api/health')).ok)break;}catch{}await new Promise(r=>setTimeout(r,100));}
  browser=await chromium.launch({headless:true,executablePath:process.env.CHROMIUM_EXECUTABLE||undefined,args:JSON.parse(process.env.CHROMIUM_ARGS||'[]')});
  const sizes=JSON.parse(process.env.ROULETTE_VIEWPORTS||'[{"width":1440,"height":900},{"width":1186,"height":570},{"width":806,"height":1110},{"width":800,"height":900},{"width":390,"height":844},{"width":320,"height":568}]');
  for(const size of sizes){
   const small=size.width<700,context=await browser.newContext({viewport:size,reducedMotion:size.width===1440?'no-preference':'reduce'}),p=await context.newPage(),errors=[];p.setDefaultTimeout(30000);
   p.on('pageerror',e=>errors.push(e.message));p.on('response',r=>{if(r.url().includes('/assets/roulette/')&&r.status()>=400)errors.push(r.url());});
   assert.ok((await context.request.get(url+'/api/activity')).ok());
   await require('./tutorial-setup.cjs').completeViaApi(context.request,url);
   const seed=spawnSync('python3',['-c','import sqlite3,sys;c=sqlite3.connect(sys.argv[1]);c.execute("UPDATE players SET wallet_gold=10000");c.commit()',db]);assert.equal(seed.status,0);
   await p.goto(url);await p.locator('#panel').waitFor({state:'hidden'});await p.locator('#launch-screen').waitFor({state:'detached'});await p.locator('#scene-stage[aria-busy="false"]').waitFor();
   for(const label of ['Replier le suivi des quêtes','Replier les quêtes quotidiennes']){const b=p.getByRole('button',{name:label,exact:true});if(await b.isVisible())await b.click();}
   for(const name of ['Ruelle sombre','Le vigile'])await p.getByRole('button',{name,exact:true}).click();await p.getByRole('button',{name:/^Payer l’entrée/}).click();await p.getByRole('button',{name:'Roulette',exact:true}).click();
   await p.locator('.rou-background').evaluate(im=>im.decode());assert.equal(await p.locator('.rou-number').count(),37);assert.ok(await p.getByRole('button',{name:'Lancer',exact:true}).isDisabled());
   const wheel=await p.locator('.rou-wheel').boundingBox();assert.ok(wheel&&Math.abs(wheel.width/wheel.height-(small?1.65:1.6))<.03,JSON.stringify({size,wheel}));
   await p.screenshot({path:path.join(temp,'roulette-'+size.width+'-idle.png'),fullPage:true});
   if(small){
    await p.getByRole('button',{name:'Tapis de mises',exact:true}).click();assert.equal(await p.locator('.rou-number:visible').count(),13);
    await p.getByRole('button',{name:'Numéros 13 à 24',exact:true}).click();assert.equal(await p.locator('.rou-number:visible').count(),13);assert.ok(await p.getByRole('button',{name:'Miser sur le numéro 15',exact:true}).isVisible());
    await p.getByRole('button',{name:'Numéros 25 à 36',exact:true}).click();assert.ok(await p.getByRole('button',{name:'Miser sur le numéro 36',exact:true}).isVisible());
    await p.getByRole('button',{name:'Numéros 1 à 12',exact:true}).click();
    for(const b of await p.locator('.rou-number:visible').evaluateAll(es=>es.map(e=>e.getBoundingClientRect().toJSON())))assert.ok(b.height>=43&&b.width>=44&&b.x>=0&&b.right<=size.width+1,JSON.stringify({size,b}));
   }else{
    const n1=await p.getByRole('button',{name:'Miser sur le numéro 1',exact:true}).boundingBox(),n3=await p.getByRole('button',{name:'Miser sur le numéro 3',exact:true}).boundingBox(),n4=await p.getByRole('button',{name:'Miser sur le numéro 4',exact:true}).boundingBox();assert.ok(n1.x<n3.x&&n4.y>n1.y);
    if(size.height>size.width){const h=await p.locator('.rou-table').evaluate(e=>e.getBoundingClientRect().height);assert.ok(h<1200,JSON.stringify({size,h}));}
   }
   const snap=()=>p.evaluate(async()=>(await(await fetch('/api/activity')).json()).state),before=(await snap()).balance.wallet;
   await p.getByRole('button',{name:'Jeton de 5 Gold',exact:true}).click();
   if(small)await p.getByRole('button',{name:'Chances simples',exact:true}).click();await p.getByRole('button',{name:'Rouge',exact:true}).click();
   if(small)await p.getByRole('button',{name:'Numéros',exact:true}).click();await p.getByRole('button',{name:'Miser sur le numéro 7',exact:true}).click();assert.equal(await p.locator('.rou-total').textContent(),'Mise totale : 10 Gold');
   await p.getByRole('button',{name:'Annuler',exact:true}).click();assert.equal(await p.locator('.rou-total').textContent(),'Mise totale : 5 Gold');await p.getByRole('button',{name:'Miser sur le numéro 7',exact:true}).click();
   await p.getByRole('button',{name:'À cheval',exact:true}).click();await p.getByRole('button',{name:'Miser sur le numéro 1',exact:true}).click();await p.getByRole('button',{name:'Miser sur le numéro 2',exact:true}).click();assert.equal(await p.locator('.rou-total').textContent(),'Mise totale : 15 Gold');assert.equal((await snap()).balance.wallet,before);
   const marker=await p.locator('.rou-combo-marker').boundingBox(),one=await p.getByRole('button',{name:'Miser sur le numéro 1',exact:true}).boundingBox(),two=await p.getByRole('button',{name:'Miser sur le numéro 2',exact:true}).boundingBox();
   assert.ok(Math.abs(marker.x+marker.width/2-(one.x+one.width))<3,JSON.stringify({size,marker,one,two}));
   await p.locator('#panel').evaluate(e=>e.scrollTop=0);await p.screenshot({path:path.join(temp,'roulette-'+size.width+'-bets.png'),fullPage:true});
   if(size.width===806){await p.setViewportSize({width:390,height:844});await p.getByRole('button',{name:'Tapis de mises',exact:true}).click();assert.equal(await p.locator('.rou-total').textContent(),'Mise totale : 15 Gold');assert.equal(await p.locator('.rou-number:visible').count(),13);await p.setViewportSize(size);await p.getByRole('button',{name:'Miser sur le numéro 36',exact:true}).waitFor();assert.equal(await p.locator('.rou-total').textContent(),'Mise totale : 15 Gold');}
   await p.getByRole('button',{name:'Lancer',exact:true}).click();
   if(size.width===1440){await p.locator('#panel[aria-busy="true"]').waitFor();assert.equal(await p.locator('#panel button:enabled').count(),0);await p.waitForFunction(()=>document.querySelector('.rou-rotor')?.hasAttribute('transform'));await p.keyboard.press('Escape');assert.equal(await p.locator('#panel.roulette-real').count(),1);const first=await p.locator('.rou-rotor').getAttribute('transform');await p.waitForFunction(previous=>document.querySelector('.rou-rotor')?.getAttribute('transform')!==previous,first,{timeout:5000});assert.equal(await p.locator('.outcome-heading').count(),0);}
   await p.locator('#panel[aria-busy="false"] .outcome-heading').waitFor({timeout:20000});
   const st=await snap(),expected=st.play.bets.reduce((sum,b)=>sum+(b.numbers.includes(st.play.number)?b.amount*b.multiplier:0),0);assert.equal(st.play.wager,15);assert.equal(st.play.payout,expected);assert.equal(st.balance.wallet,before-15+expected);assert.equal(Number(await p.locator('.rou-ball').getAttribute('cx')),500);assert.equal(Number(await p.locator('.rou-ball').getAttribute('cy')),160);assert.equal(await p.locator('.rou-number.last-number').textContent(),String(st.play.number));
   if(small){assert.ok(await p.locator('.rou-wheel').isVisible());assert.ok(await p.locator('.rou-board').isHidden());}
   await p.screenshot({path:path.join(temp,'roulette-'+size.width+'-result.png'),fullPage:true});
   await p.getByRole('button',{name:'Règles',exact:true}).click();await p.getByRole('dialog',{name:'Règles de la roulette',exact:true}).waitFor();await p.keyboard.press('Escape');await p.getByRole('button',{name:'Retour',exact:true}).click();await p.locator('#panel.casino-room').waitFor();assert.deepEqual(errors,[]);await context.close();
  }
  console.log(JSON.stringify({status:'PASS',viewports:sizes.length,screenshots:temp}));
 }finally{await browser?.close();server.kill();}
})().catch(e=>{console.error(e);process.exitCode=1;});
