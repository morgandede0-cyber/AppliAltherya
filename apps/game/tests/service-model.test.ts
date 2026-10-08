import test from 'node:test';
import assert from 'node:assert/strict';
import {withdrawalQuote,validAmount,pageSlice} from '../src/ui/service-model';
test('Premier retrait gratuit puis frais arrondis selon le moteur bancaire',()=>{assert.deepEqual(withdrawalQuote(100,true),{fee:0,received:100});assert.deepEqual(withdrawalQuote(101,false),{fee:5,received:96});assert.deepEqual(withdrawalQuote(1,false),{fee:1,received:0});});
test('Refuse les montants fractionnaires, vides ou supérieurs au solde',()=>{for(const value of [0,-1,1.5,NaN,Infinity,101])assert.equal(validAmount(value,100),false);assert.equal(validAmount(100,100),true);});
test('Les pages comportent quatre objets au maximum sans perte',()=>{const items=Array.from({length:11},(_,i)=>i);assert.deepEqual(pageSlice(items,0),[0,1,2,3]);assert.deepEqual(pageSlice(items,1),[4,5,6,7]);assert.deepEqual(pageSlice(items,2),[8,9,10]);});
