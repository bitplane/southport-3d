import test from 'node:test';
import assert from 'node:assert/strict';
import { chooseLevel, evictionCandidates } from '../lod.js';
const settings={detailDistance:8,districtDistance:70},available=['detail','walk','district'];
test('distance bands and manual override',()=>{assert.equal(chooseLevel(2,null,'auto',settings,available),'detail');assert.equal(chooseLevel(30,null,'auto',settings,available),'walk');assert.equal(chooseLevel(200,null,'auto',settings,available),'district');assert.equal(chooseLevel(2,'detail','district',settings,available),'district');});
test('hysteresis prevents repeated switching at a boundary',()=>{assert.equal(chooseLevel(8.5,'detail','auto',settings,available),'detail');assert.equal(chooseLevel(7,'walk','auto',settings,available),'walk');assert.equal(chooseLevel(72,'walk','auto',settings,available),'walk');assert.equal(chooseLevel(65,'district','auto',settings,available),'district');});
test('partial levels remain viewable without inventing resources',()=>{assert.equal(chooseLevel(300,null,'auto',settings,['detail']),'detail');assert.equal(chooseLevel(10,null,'auto',settings,[]),null);});
test('cache eviction preserves active models and removes least recently used first',()=>{const records=[{key:'active',bytes:50,active:true,used:0},{key:'old',bytes:30,active:false,used:1},{key:'new',bytes:30,active:false,used:2}];assert.deepEqual(evictionCandidates(records,80),['old']);assert.deepEqual(evictionCandidates(records,20),['old','new']);});
