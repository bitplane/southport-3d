import * as THREE from 'three';
import { GLTFLoader } from 'three/addons/loaders/GLTFLoader.js';
import { viewVolume } from './view-volume.js';
import { chooseLevel } from './lod.js';
import { admit, estimatedBytes, horizontalDistance } from './spatial.js';

function dispose(root) {
  const geometries=new Set(), materials=new Set(), textures=new Set();
  root.traverse(o=>{if(o.geometry)geometries.add(o.geometry);for(const m of [o.material].flat().filter(Boolean)){materials.add(m);for(const v of Object.values(m))if(v?.isTexture)textures.add(v);}});
  geometries.forEach(x=>x.dispose());materials.forEach(x=>x.dispose());textures.forEach(x=>{x.dispose();x.source?.data?.close?.();});
}
export class Streamer {
  constructor(scene,catalog,baseURL,onChange,onError,maxAnisotropy=1) {
    this.scene=scene;this.baseURL=baseURL;this.onChange=onChange;this.onError=onError;
    this.entries=[];this.loader=new GLTFLoader();this.cache=new Map();this.pending=0;this.bytes=0;
    this.budget=256*1024*1024;this.radius=Infinity;this.margin=64;this.wireframe=false;this.frozen=false;this.staging=false;
    this.anisotropy=Math.max(1,Math.min(16,maxAnisotropy));
    this.addAssets(catalog.assets);
  }
  addAssets(assets){
    for(const asset of assets){
      const group=new THREE.Group();group.position.fromArray(asset.position);group.rotation.y=asset.rotationY;this.scene.add(group);group.updateMatrixWorld(true);
      for(const part of asset.parts){
        const slot=new THREE.Group();group.add(slot);
        const box=new THREE.Box3(new THREE.Vector3().fromArray(part.bounds[0]),new THREE.Vector3().fromArray(part.bounds[1])).applyMatrix4(group.matrixWorld);
        this.entries.push({asset,part,slot,box,current:null,wanted:null,loading:null,failed:new Set(),distance:Infinity});
      }
    }
  }
  update(camera,settings,force){
    if(this.frozen)return;
    const candidates=[],now=performance.now();
    const view=this.viewAware?viewVolume(camera,this.radius,this.margin):null;
    for(const entry of this.entries){
      entry.distance=entry.box.distanceToPoint(camera.position);
      const bounds=[entry.box.min.toArray(),entry.box.max.toArray()];
      const nearby=view?view.includes(bounds):horizontalDistance(bounds,camera.position.toArray())<=this.radius+(entry.current?this.margin:0);
      if(nearby)entry.lastSeen=now;
      const retained=entry.lastSeen!==undefined&&now-entry.lastSeen<(this.retentionMs??0);
      entry.priority=nearby?(view?.visible(bounds)?0:1):2;
      const desired=entry.part.fixedLevel || chooseLevel(entry.distance,entry.current,force,settings,Object.keys(entry.part.levels));
      entry.desired=nearby?desired:retained?(entry.part.fixedLevel||(entry.part.levels.district?'district':desired)):null;
      if(entry.desired)candidates.push({key:this.entryKey(entry),priority:entry.priority,ground:entry.part.ground,distance:entry.distance,
        wanted:entry.desired,fixed:!!entry.part.fixedLevel,levels:entry.part.levels});
    }
    const selection=admit(candidates,this.budget).levels;
    for(const entry of this.entries){
      entry.wanted=selection.get(this.entryKey(entry))||null;
      entry.deferred=!!entry.desired&&!entry.wanted;
      if(entry.loading && (!entry.wanted || (entry.current!==null&&entry.loading.level!==entry.wanted)))entry.loading.controller.abort();
      if(!entry.wanted){entry.slot.clear();entry.current=null;entry.replacing=false;}
      const key=this.key(entry,entry.wanted);
      if(entry.wanted&&this.cache.has(key))this.activate(entry,entry.wanted);
    }
    this.evict();
    const queue=this.entries.filter(e=>e.wanted && !e.loading && e.current!==e.wanted).sort((a,b)=>a.priority-b.priority||(a.part.fixedLevel?-1:0)-(b.part.fixedLevel?-1:0)||a.distance-b.distance);
    for(const entry of queue){
      if(this.pending>=2)break;
      // Show an inexpensive complete part while its selected level is fetched.
      // If eviction made room for an upgrade, fetch that upgrade directly.
      // Bootstrapping District again would repeat the same eviction forever.
      const fallback=!this.staging && !entry.replacing && entry.current===null && entry.part.levels.district && !entry.failed.has('district') && entry.wanted!=='district' ? 'district' : entry.wanted;
      const available=this.budget-this.residentBytes-this.reservedBytes;
      // A baked District GLB can cost more memory than its detailed geometry.
      // Do not let an unaffordable bootstrap block an affordable wanted level.
      const level=estimatedBytes(entry.part.levels[fallback])<=available?fallback:entry.wanted;
      if(!entry.failed.has(level) && estimatedBytes(entry.part.levels[level])<=available) this.load(entry,level);
    }
    this.evict();
  }
  entryKey(entry){return `${entry.asset.id}/${entry.part.id}`;}
  get reservedBytes(){return this.entries.reduce((n,e)=>n+(e.loading?estimatedBytes(e.part.levels[e.loading.level]):0),0);}
  key(entry,level){return `${entry.asset.id}/${entry.part.id}/${level}/${entry.part.levels[level]?.uri}`;}
  async load(entry,level){
    const key=this.key(entry,level), record=entry.part.levels[level], controller=new AbortController();
    entry.loading={level,controller};this.pending++;this.onChange();
    try{
      const response=await fetch(new URL(record.uri,this.baseURL),{signal:controller.signal});
      if(!response.ok)throw new Error(`HTTP ${response.status}`);
      const bytes=await response.arrayBuffer();this.bytes+=bytes.byteLength;
      if(controller.signal.aborted)return;
      const gltf=await this.loader.parseAsync(bytes,'');
      if(controller.signal.aborted || entry.retired || (entry.desired===null)){dispose(gltf.scene);return;}
      // Long sign panels and oblique paving otherwise lose their long-axis detail
      // to isotropic mip filtering, even when the underlying bake is sharp.
      const textures=new Set();
      gltf.scene.traverse(o=>{if(o.isMesh){
        o.castShadow=true;o.receiveShadow=true;
        for(const m of [o.material].flat().filter(Boolean)){
          m.wireframe=this.wireframe;
          for(const texture of Object.values(m))if(texture?.isTexture)textures.add(texture);
        }
      }});
      for(const texture of textures)texture.anisotropy=this.anisotropy;
      this.cache.set(key,{key,root:gltf.scene,bytes:estimatedBytes(record),used:performance.now(),entry,level});
      if(entry.current===null || entry.wanted===level)this.activate(entry,level);
    }catch(error){if(error.name!=='AbortError'){entry.failed.add(level);this.onError(`${entry.part.name}: ${error.message}`);}}
    finally{entry.loading=null;this.pending--;this.onChange();}
  }
  activate(entry,level){
    if(this.frozen || entry.retired)return;
    const cached=this.cache.get(this.key(entry,level));if(!cached)return;
    cached.used=performance.now();entry.replacing=false;
    if(entry.current===level)return;
    entry.slot.clear();entry.slot.add(cached.root);entry.current=level;this.onChange();
  }
  evict(){
    // Keep only the active or selected replacement version. Inactive cached
    // LoDs must not prevent admission of a selected, closer part.
    for(const [key,r] of this.cache){
      if(r.entry.current!==r.level && r.entry.wanted!==r.level){dispose(r.root);this.cache.delete(key);}
    }
    // Release an active level only if both it and the selected replacement
    // cannot coexist. An in-flight replacement is already in reservedBytes.
    for(const entry of this.entries){
      if(entry.current&&entry.wanted&&entry.current!==entry.wanted){
        const target=entry.loading?.level===entry.wanted || this.cache.has(this.key(entry,entry.wanted)) ? 0 : estimatedBytes(entry.part.levels[entry.wanted]);
        if(this.residentBytes+this.reservedBytes+target>this.budget){
          const key=this.key(entry,entry.current),r=this.cache.get(key);
          entry.slot.clear();entry.current=null;entry.replacing=true;if(r){dispose(r.root);this.cache.delete(key);}
        }
      }
    }
  }
  removeEntries(removed){
    const retired=new Set(removed);
    const groups=new Set(removed.map(e=>e.slot.parent));
    for(const entry of removed){entry.retired=true;entry.loading?.controller.abort();entry.slot.removeFromParent();}
    for(const group of groups)if(group&&!group.children.length)group.removeFromParent();
    for(const [key,record] of this.cache){
      if(retired.has(record.entry)){dispose(record.root);this.cache.delete(key);}
    }
    this.entries=this.entries.filter(e=>!retired.has(e));
  }
  removeAssets(ids){this.removeEntries(this.entries.filter(e=>ids.has(e.asset.id)));}
  reconcile(assets){
    const wanted=new Set(assets.flatMap(a=>a.parts.map(p=>`${a.id}/${p.id}`)));
    this.removeEntries(this.entries.filter(e=>!wanted.has(this.entryKey(e))));
    const existing=new Set(this.entries.map(e=>this.entryKey(e)));
    this.addAssets(assets.map(a=>({...a,parts:a.parts.filter(p=>!existing.has(`${a.id}/${p.id}`))})).filter(a=>a.parts.length));
  }
  destroy(){this.removeAssets(new Set(this.entries.map(e=>e.asset.id)));}
  adopt(staged,ids){
    this.removeAssets(ids);
    for(const group of [...staged.scene.children])this.scene.add(group);
    this.entries.push(...staged.entries);
    for(const [key,record] of staged.cache)this.cache.set(key,record);
    this.bytes+=staged.bytes;
    staged.entries=[];staged.cache.clear();
    this.scene.updateMatrixWorld(true);this.onChange();
  }
  setWireframe(value){this.wireframe=value;for(const r of this.cache.values())r.root.traverse(o=>{for(const m of [o.material].flat().filter(Boolean))m.wireframe=value;});}
  get residentBytes(){return [...this.cache.values()].reduce((n,r)=>n+r.bytes,0);}
  get activeRoots(){return this.entries.filter(e=>e.current).map(e=>e.slot);}
  get groundRoots(){return this.entries.filter(e=>e.part.ground && e.current).map(e=>e.slot);}
}
