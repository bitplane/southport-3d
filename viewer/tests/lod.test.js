import test from 'node:test';
import assert from 'node:assert/strict';
import { countLevels, forcedError, tileLevel } from '../lod.js';

const proxy={proxy:'lite',rank:0}, district={level:'district',rank:1}, walk={level:'walk',rank:2}, detail={level:'detail',rank:3};
test('automatic selection leaves screen-space error alone',()=>{
  for(const extras of [proxy,district,walk,detail])assert.equal(forcedError(extras,true,'auto'),null);
});
test('forced levels refine coarser tiles and stop at the first tile reaching the level',()=>{
  assert.equal(forcedError(proxy,true,'district'),Infinity);
  assert.equal(forcedError(district,true,'district'),0);
  assert.equal(forcedError(district,true,'walk'),Infinity);
  assert.equal(forcedError(walk,true,'walk'),0);
  assert.equal(forcedError(walk,true,'detail'),Infinity);
  assert.equal(forcedError(detail,false,'detail'),0);
});
test('collapsed tiles serving several levels stop at any level they draw',()=>{
  // District and Walk content were identical, so one tile draws Walk for both.
  assert.equal(forcedError({level:'walk',rank:1},true,'district'),0);
  // A leaf cannot refine further even when coarser than requested.
  assert.equal(forcedError({level:'walk',rank:2},false,'detail'),0);
});
test('drawn tiles are summarised by level',()=>{
  assert.equal(tileLevel(proxy),'lite proxy');
  assert.deepEqual(countLevels([proxy,district,district,detail]),{'lite proxy':1,district:2,detail:1});
});
