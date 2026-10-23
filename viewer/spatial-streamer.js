import * as THREE from 'three';
import { Streamer } from './streamer.js';
import { selectedCells, mergeCells } from './spatial.js';
import { changedAssets } from './live.js';

/** Fetch a bounded cell working set; keep last good content during replacement. */
export class SpatialStreamer {
  constructor(scene,catalog,baseURL,onChange,onError,anisotropy=1){
    Object.assign(this,{scene,catalog,baseURL,onChange,onError});
    this.anisotropy=Number.isFinite(anisotropy)?Math.max(1,Math.min(16,anisotropy)):1;
    this.current=new Streamer(scene,{assets:[]},baseURL,onChange,onError,this.anisotropy);
    this.current.budget=catalog.streaming.budget;this.current.radius=catalog.streaming.radius;
    this.current.margin=catalog.streaming.margin;
    this.nodes=new Map();this.abort=null;this.generation=0;this.loading=false;
    this.snapshot={assets:[]};this.appliedCatalog=null;this.staged=null;this.requestKey=null;this.appliedKey=null;
    this.failedKey=null;this.frozen=false;this.paused=false;this.wireframe=false;this.message='';
  }
  setCatalog(next){
    if(this.paused){this.pendingCatalog=next;return;}
    this.catalog=next;this.failedKey=null;this.requestKey=null;
  }
  setPaused(value){
    if(value===this.paused)return;
    this.paused=value;this.cancel();this.requestKey=null;this.failedKey=null;
    if(value){this.pendingCatalog=this.catalog;this.catalog=this.appliedCatalog||this.catalog;}
    else if(this.pendingCatalog){this.catalog=this.pendingCatalog;this.pendingCatalog=null;}
  }
  update(camera,settings,force){
    this.current.frozen=this.frozen;
    if(this.frozen)return;
    this.current.update(camera,settings,force);
    const p=camera.position.toArray(),policy=this.catalog.streaming;
    const cells=selectedCells(this.catalog.cells,p,policy.radius+policy.margin);
    // Replan on 16 m movement, quality changes or scene revision. Keep exact
    // camera position captured for the whole fetch/stage transaction.
    const key=JSON.stringify([this.catalog.revision,Math.floor(p[0]/16),Math.floor(p[2]/16),force,settings,cells.map(c=>c.sha256)]);
    if(key!==this.requestKey){
      this.cancel();this.requestKey=key;
      if(key!==this.failedKey)this.fetchCells(cells,p,key,camera.clone(),{...settings},force);
    }
    if(this.staged){
      const stage=this.staged;
      if(!this.current.entries.length){
        this.current.adopt(stage.streamer,stage.ids);this.staged=null;
        this.snapshot=stage.snapshot;this.appliedCatalog=stage.catalog;this.appliedKey=key;
        this.current.update(camera,settings,force);return;
      }
      stage.streamer.update(stage.camera,stage.settings,stage.force);
      if(stage.streamer.entries.some(e=>e.failed.size))return this.fail('Update failed; previous models kept');
      if(stage.streamer.pending||stage.streamer.entries.some(e=>e.wanted&&e.current!==e.wanted))return;
      if(this.current.entries.length&&stage.streamer.entries.some(e=>e.deferred&&this.current.entries.some(old=>old.asset.id===e.asset.id)))return this.fail('Replacement exceeds staging budget; previous models kept');
      this.current.adopt(stage.streamer,stage.ids);this.staged=null;
      this.current.update(camera,settings,force);
      this.snapshot=stage.snapshot;this.appliedCatalog=stage.catalog;this.appliedKey=key;this.message='Models updated';this.onChange();
    }
  }
  async fetchCells(cells,position,key,camera,settings,force){
    const generation=++this.generation,controller=new AbortController();this.abort=controller;this.loading=true;
    const requested=this.catalog;const nodes=[];let index=0;
    try{
      const worker=async()=>{while(index<cells.length){
        const cell=cells[index++];let node=this.nodes.get(cell.uri);
        if(!node){
          const response=await fetch(new URL(cell.uri,this.baseURL),{signal:controller.signal});
          if(!response.ok)throw new Error(`Cell HTTP ${response.status}`);
          const bytes=await response.arrayBuffer();
          const hash=[...new Uint8Array(await crypto.subtle.digest('SHA-256',bytes))].map(n=>n.toString(16).padStart(2,'0')).join('');
          if(hash!==cell.sha256)throw new Error('Cell hash mismatch');
          node=JSON.parse(new TextDecoder().decode(bytes));
          if(generation!==this.generation)return;
          this.nodes.set(cell.uri,node);
        }
        nodes.push(node);
      }};
      await Promise.all(Array.from({length:Math.min(4,cells.length)},worker));
      if(generation!==this.generation)return;
      const keep=new Set(cells.map(c=>c.uri));for(const uri of this.nodes.keys())if(!keep.has(uri))this.nodes.delete(uri);
      const snapshot={assets:mergeCells(nodes,position,requested.streaming.radius,requested.streaming.margin,this.current.entries)};
      const ids=changedAssets(this.snapshot,snapshot);
      if(!ids.size){this.snapshot=snapshot;this.appliedCatalog=requested;this.appliedKey=key;return;}
      const next=new Streamer(new THREE.Scene(),{assets:snapshot.assets.filter(a=>ids.has(a.id))},this.baseURL,()=>{},()=>{},this.anisotropy);
      next.staging=true;next.budget=this.current.entries.length?Math.min(requested.streaming.stagingBudget,requested.streaming.budget):requested.streaming.budget;
      next.setWireframe(this.wireframe);
      // Stage coarse geometry, then let the normal budgeted selector refine it.
      this.staged={streamer:next,ids,snapshot,catalog:requested,camera,settings,force:'district'};
    }catch(error){if(generation===this.generation&&error.name!=='AbortError')this.fail(error.message+'; previous models kept');}
    finally{if(generation===this.generation){this.loading=false;this.onChange();}}
  }
  fail(message){this.failedKey=this.requestKey;this.message=message;this.cancel();this.onError(message);}
  cancel(){this.generation++;this.abort?.abort();this.abort=null;this.loading=false;this.staged?.streamer.destroy();this.staged=null;}
  destroy(){this.cancel();this.current.destroy();this.nodes.clear();}
  setWireframe(value){this.wireframe=value;this.current.setWireframe(value);this.staged?.streamer.setWireframe(value);}
  get entries(){return this.current.entries;}
  get pending(){return this.current.pending+(this.loading?1:0)+(this.staged?.streamer.pending||0);}
  get bytes(){return this.current.bytes;}
  get residentBytes(){return this.current.residentBytes;}
  get stagedBytes(){return (this.staged?.streamer.residentBytes||0)+(this.staged?.streamer.reservedBytes||0);}
  get reservedBytes(){return this.current.reservedBytes;}
  get budget(){return this.current.budget;}
  get groundRoots(){return this.current.groundRoots;}
  get activeRoots(){return this.current.activeRoots;}
}
