import {test} from 'node:test';import assert from 'node:assert/strict';import {load,save} from '../src/save/storage';import {fresh} from '../src/data/rules';
let value:string|null=null;Object.defineProperty(globalThis,'localStorage',{value:{getItem:()=>value,setItem:(_:string,v:string)=>{value=v;}}});
test('sauvegarde et reprise incluent inventaire, équipement et quêtes',()=>{const s=fresh('Test',1);s.inventory.sword=1;s.equipped=true;s.quests.wolves.active=true;s.quests.wolves.progress=2;s.collected.push('ore1');assert.ok(save(s));assert.deepEqual(load(),s);});
test('sauvegarde corrompue ou inventaire négatif refusés',()=>{value='{';assert.equal(load(),null);const s=fresh();s.inventory.potion=-1;save(s);assert.equal(load(),null);});
