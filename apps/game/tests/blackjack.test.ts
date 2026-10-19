import test from 'node:test';
import assert from 'node:assert/strict';
import {buildSync} from 'esbuild';
const code=buildSync({entryPoints:['src/ui/blackjack.ts'],bundle:true,format:'cjs',platform:'node',write:false,loader:{'.css':'empty'}}).outputFiles[0].text;
const m={exports:{} as any};new Function('module','exports',code)(m,m.exports);
test('blackjack ace totals stay consistent with server rules',()=>{const t=(...r:string[])=>m.exports.cardTotal(r.map(rank=>({rank})));assert.equal(t('A','A','9'),21);assert.equal(t('A','K'),21);assert.equal(t('A','6'),17);assert.equal(t('10','6','10'),26);});
test('every card face is deterministic and hidden card exposes no value',()=>{for(const suit of ['♠','♥','♦','♣'])for(const rank of ['2','3','4','5','6','7','8','9','10','J','Q','K','A']){const svg=m.exports.cardSVG({rank,suit});assert.match(svg,/<svg/);assert.ok(svg.includes(suit));assert.ok(!svg.includes('undefined'));}const hidden=m.exports.cardSVG({hidden:true});assert.ok(!hidden.includes('♥'));});
