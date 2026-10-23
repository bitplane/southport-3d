import test from 'node:test';
import assert from 'node:assert/strict';
import {readView,writeView,VIEW_KEY} from '../view-state.js';
const origin=[53.6486555,-3.0043401];
const view={version:1,worldOrigin:origin,mode:'orbit',position:[15,30,45],quaternion:[0,0,0,1],target:[1,2,3],fov:50,walkFloor:.7,dropPending:false};
function storage(){const items=new Map();return {getItem:k=>items.get(k)??null,setItem:(k,v)=>items.set(k,v)};}
test('both navigation modes survive a reload independently of model versions',()=>{
  for(const mode of ['orbit','walk']){const s=storage(),v={...view,mode};assert.equal(writeView(s,v),true);assert.deepEqual(readView(s,origin),v);}
});
test('absent, malformed, incompatible or unusable camera state is ignored',()=>{
  const s=storage();assert.equal(readView(s,origin),null);
  for(const value of ['{', 'null', JSON.stringify({...view,version:2}),JSON.stringify({...view,position:[1,2]}),JSON.stringify({...view,quaternion:[0,0,0,0]}),JSON.stringify({...view,target:view.position}),JSON.stringify({...view,worldOrigin:[0,0]})]){
    s.setItem(VIEW_KEY,value);assert.equal(readView(s,origin),null);
  }
});
test('storage access and quota failures do not prevent viewing',()=>{
  const denied={getItem(){throw Error('denied');},setItem(){throw Error('quota');}};
  assert.equal(readView(denied,origin),null);assert.equal(writeView(denied,view),false);
});
