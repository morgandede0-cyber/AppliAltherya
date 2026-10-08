import {test} from 'node:test';import assert from 'node:assert/strict';
import {WHEEL,RED,wheelRotation,raceProgress} from '../src/ui/game-model';
test('la roulette contient 37 secteurs uniques et termine sur le numéro serveur',()=>{assert.equal(new Set(WHEEL).size,37);assert.equal(RED.size,18);let prior=0;for(const n of WHEEL){const angle=wheelRotation(n,prior);assert.ok(angle>prior+1000);assert.ok(Math.abs((angle+WHEEL.indexOf(n)*360/37)%360)<1e-8||Math.abs((angle+WHEEL.indexOf(n)*360/37)%360-360)<1e-8);prior=angle;}});
test('le cheval désigné par le serveur arrive en premier sans débordement',()=>{for(let winner=0;winner<4;winner++){const values=raceProgress(1,winner);assert.equal(values[winner],1);assert.ok(values.every((v,i)=>v>=0&&v<=1&&(i===winner||v<1)));assert.deepEqual(raceProgress(-1,winner),[0,0,0,0]);}});

import {slotKey} from '../src/ui/game-model';
test('les cinq symboles réels du serveur correspondent aux cinq dessins des rouleaux',()=>{assert.deepEqual(['🍒','🔔','💎','👑','7️⃣'].map(slotKey),['cherry','bell','diamond','crown','seven']);});

import {gestureKey} from '../src/ui/game-model';
test('les gestes français renvoyés par le serveur sélectionnent les bons assets',()=>{assert.deepEqual(['pierre','feuille','ciseaux','rock','paper','scissors'].map(gestureKey),['rock','paper','scissors','rock','paper','scissors']);});

import {outcomeTone,coinRotation} from '../src/ui/game-model';
test('le retour réel décide du résultat, y compris les mises restituées',()=>{assert.equal(outcomeTone(0,10),'loss');assert.equal(outcomeTone(10,10),'tie');assert.equal(outcomeTone(15,10),'win');});
test('la pièce termine sur la bonne face après plusieurs tours',()=>{assert.equal(coinRotation('pile')%360,0);assert.equal(coinRotation('face')%360,180);});
test('les chevaux changent de rythme sans reculer ni dépasser la ligne',()=>{for(let winner=0;winner<4;winner++){let previous=[0,0,0,0];for(let step=0;step<=100;step++){const now=raceProgress(step/100,winner);now.forEach((value,i)=>{assert.ok(value>=previous[i]-1e-9);assert.ok(value>=0&&value<=1);});previous=now;}assert.equal(previous.indexOf(Math.max(...previous)),winner);}});
