import test from 'node:test';
import assert from 'node:assert/strict';
import {sceneViewport} from '../src/ui/responsive';
for(const [width,height] of [[1440,900],[1186,570],[844,390],[390,844],[809,1110],[320,568]])test(`Activity layout ${width}×${height}`,()=>{const v=sceneViewport(width,height,16/9);assert.equal(v.portrait,width/height<1.15);assert.ok(v.width<=width&&v.height<=height);if(v.portrait){assert.equal(v.height,height);assert.equal(v.width,width);}else assert.ok(Math.abs(v.width/v.height-16/9)<.001);});
