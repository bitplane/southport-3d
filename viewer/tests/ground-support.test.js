import test from 'node:test';
import assert from 'node:assert/strict';
import {chooseSupport,supportId} from '../ground-support.js';
const hit=(height,surface)=>({face:{},point:{y:height},object:{parent:{userData:{supportSurface:surface}}}});
test('bridge stays on the current level through replacement, including missing lower mesh',()=>{
 assert.equal(chooseSupport([hit(4,'deck'),hit(0,'under')],0,'under').point.y,0);
 assert.equal(chooseSupport([hit(4,'deck')],0,'under'),null);
 assert.equal(chooseSupport([hit(4,'deck'),hit(0,'under')],4,'deck').point.y,4);
 assert.equal(chooseSupport([hit(0,'under')],4,'deck'),null);
});
test('supports connected ramps, kerbs, seams and fallback IDs across LoDs',()=>{
 let floor=0;
 for(let i=1;i<=40;i++){const next=chooseSupport([hit(i*.1,'ramp')],floor,'approach');assert.ok(next);floor=next.point.y;}
 assert.equal(chooseSupport([hit(4.12,'pavement')],4,'deck').point.y,4.12);
 assert.equal(supportId({parent:{userData:{ground:true,asset:'road',part:'west'}}}),'road/west');
 assert.equal(chooseSupport([hit(0.01,'new'),hit(0,'old')],0,'old').point.y,0);
});
test('same ID cannot pull navigator up onto a distinct surface',()=>{
 assert.equal(chooseSupport([hit(.4,'old'),hit(0,'new')],0,'old').point.y,0);
 assert.equal(chooseSupport([hit(.6,'old')],0,'old'),null);
});
