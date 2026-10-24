import test from 'node:test';
import assert from 'node:assert/strict';
import {selectedCells,admit,mergeCells} from '../spatial.js';

test('50k sparse cells select only a bounded neighbourhood',()=>{
 const cells=Array.from({length:50000},(_,i)=>({key:String(i),bounds:[[i*64,0,0],[i*64+64,20,64]]}));
 assert.ok(selectedCells(cells,[10000,2,0],250).length<12);
 assert.equal(selectedCells(cells,[0,2,0],250).length,4);
 assert.equal(selectedCells(cells,[-1000,2,0],250).length,0);
});
test('admission prioritizes ground and downgrades without exceeding estimates',()=>{
 const levels={detail:{gpuBytesEstimate:100},walk:{gpuBytesEstimate:30},district:{gpuBytesEstimate:10}};
 const candidates=[{key:'near',distance:1,wanted:'detail',levels},{key:'ground',distance:2,wanted:'detail',levels,ground:true},
 {key:'far',distance:30,wanted:'detail',levels}];
 const plan=admit(candidates,135);
 assert.deepEqual([...plan.levels],[['ground','detail'],['near','district'],['far','district']]);
 assert.equal(plan.bytes,120);
 assert.deepEqual(admit(candidates,135),plan); // stable deferral, not alternating churn
 assert.equal(admit([{key:'huge',wanted:'district',levels:{district:{gpuBytesEstimate:200}}}],100).levels.size,0);
});
test('part filtering, hysteresis and revision consistency',()=>{
 const asset={id:'a',assetRevision:'one',parts:[{id:'p',worldBounds:[[0,0,0],[2,10,2]]}]};
 assert.equal(mergeCells([{assets:[asset]}],[270,1,0],250,64).length,0);
 assert.equal(mergeCells([{assets:[asset]}],[270,1,0],250,64,[{asset,part:asset.parts[0]}]).length,1);
 assert.equal(mergeCells([{assets:[asset]}],[400,1,0],250,64,[{asset,part:asset.parts[0]}]).length,0);
 assert.throws(()=>mergeCells([{assets:[asset,{...asset,assetRevision:'two'}]}],[0,0,0],250,64),/Mixed asset/);
});

test('visible coverage wins over nearby and retained content under pressure',()=>{
 const levels={district:{gpuBytesEstimate:20}};
 const candidates=[{key:'retained',priority:2,ground:true,distance:1,wanted:'district',levels},
  {key:'nearby',priority:1,ground:true,distance:2,wanted:'district',levels},
  {key:'visible',priority:0,distance:1000,wanted:'district',levels}];
 assert.deepEqual([...admit(candidates,20).levels.keys()],['visible']);
});
