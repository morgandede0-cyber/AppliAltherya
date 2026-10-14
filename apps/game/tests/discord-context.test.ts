import {test} from 'node:test';
import assert from 'node:assert/strict';
import {isDiscordActivity,connectionError} from '../src/discord/context';
test('Discord context uses frame_id or the exact application proxy hostname',()=>{
 assert.ok(isDiscordActivity({search:'?frame_id=test',hostname:'altherya.magicgg.fr'}));
 assert.ok(isDiscordActivity({search:'',hostname:'1529936499775242250.discordsays.com'}));
 for(const hostname of ['altherya.magicgg.fr','discordsays.com','123.discordsays.com.evil.test','evil.discordsays.com'])assert.equal(isDiscordActivity({search:'',hostname}),false);
});
test('RPC errors show their message and code, not object Object or payload secrets',()=>{
 assert.equal(connectionError({message:'Invalid redirect URI',code:4000,access_token:'must-not-display'}),'Invalid redirect URI (code 4000)');
 assert.equal(connectionError(new Error('Réseau indisponible')),'Réseau indisponible');
 assert.equal(connectionError({error:'OAuth refusé'}),'OAuth refusé');
 for(const value of [null,undefined,{},42])assert.ok(!connectionError(value).includes('[object Object]'));
});
