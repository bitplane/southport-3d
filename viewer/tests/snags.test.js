import test from 'node:test';
import assert from 'node:assert/strict';
import {selectionBox} from '../snags.js';
test('selection works for reverse dragging and clamps outside the image',()=>{
  assert.deepEqual(selectionBox([.8,.9],[.2,.3]),[.2,.3,.6000000000000001,.6000000000000001]);
  assert.deepEqual(selectionBox([.5,.5],[-1,2]),[0,.5,.5,.5]);
});
test('clicks have no selectable area',()=>{
  assert.deepEqual(selectionBox([.4,.6],[.4,.6]),[.4,.6,0,0]);
});
