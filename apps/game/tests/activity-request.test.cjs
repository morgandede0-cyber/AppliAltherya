const test=require('node:test'),assert=require('node:assert/strict'),{buildSync}=require('esbuild'),vm=require('node:vm'),{randomUUID}=require('node:crypto');
const code=buildSync({entryPoints:['src/activity.ts'],bundle:true,format:'cjs',write:false}).outputFiles[0].text;
function setup(fetch,storage=new Map()){
 const module={exports:{}};const localStorage={getItem:k=>storage.get(k)??null,setItem:(k,v)=>storage.set(k,v),removeItem:k=>storage.delete(k)};
 vm.runInNewContext(code,{module,exports:module.exports,fetch,localStorage,AbortSignal,crypto:{randomUUID}});
 return{request:module.exports.request,storage};
}
const ok=message=>({ok:true,status:200,json:async()=>({message,state:{save_owner:'verified-owner'}})});
test('lost response retries the same operation id rather than creating a second payment',async()=>{
 const calls=[];const f=setup(async(_,options)=>{calls.push(JSON.parse(options.body));if(calls.length===1)throw Error('connection lost after commit');return ok('stored');});
 assert.equal((await f.request({action:'deposit',amount:10})).message,'stored');
 assert.equal(calls.length,2);assert.equal(calls[0].request_id,calls[1].request_id);assert.equal(f.storage.size,0);
});
test('uncertain operation survives reload and is verified before a fresh action',async()=>{
 const storage=new Map(),calls=[];const before=setup(async(_,options)=>{calls.push(JSON.parse(options.body));throw Error('offline');},storage);
 await assert.rejects(before.request({action:'buy',key:'axe'}),/vérifiée/);assert.equal(storage.size,1);
 const after=setup(async(_,options)=>{calls.push(JSON.parse(options.body));return ok('already committed');},storage);
 assert.equal((await after.request()).message,'already committed');assert.equal(calls[0].request_id,calls[2].request_id);assert.equal(storage.size,0);
});
test('validation refusal is not retried and clears pending operation',async()=>{
 let calls=0;const f=setup(async()=>{calls++;return{ok:false,status:400,json:async()=>({error:'Solde insuffisant'})};});
 await assert.rejects(f.request({action:'deposit',amount:10}),/Solde insuffisant/);assert.equal(calls,1);assert.equal(f.storage.size,0);
});
test('server outages retain the operation and prevent simultaneous mutations',async()=>{
 let release;const f=setup(async()=>{await new Promise(r=>release=r);return ok('saved');});
 const one=f.request({action:'deposit',amount:10});await assert.rejects(f.request({action:'deposit',amount:20}),/Patientez/);release();await one;
});
test('a new wager waits for the server cadence while retaining one operation id',async()=>{
 let now=1000,scheduled,posts=0;const module={exports:{}};const storage=new Map();
 const fetch=async(_,options)=>{if(options?.method==='POST')posts++;return{ok:true,status:200,json:async()=>({message:'ok',state:{save_owner:'owner',server_now:100,play:{next_round_at:103}}})};};
 vm.runInNewContext(code,{module,exports:module.exports,fetch,localStorage:{getItem:k=>storage.get(k)??null,setItem:(k,v)=>storage.set(k,v),removeItem:k=>storage.delete(k)},AbortSignal,crypto:{randomUUID},Date:{now:()=>now},setTimeout:(fn,delay)=>{scheduled={fn,delay};}});
 await module.exports.request();const pending=module.exports.request({action:'game_start',key:'coin',wager:1,revision:0});assert.equal(posts,0);assert.ok(scheduled.delay>=3000&&scheduled.delay<=3030);now+=scheduled.delay;scheduled.fn();await pending;assert.equal(posts,1);assert.equal(storage.size,0);
});
