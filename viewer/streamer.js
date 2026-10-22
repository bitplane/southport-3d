import * as THREE from 'three';
import { GLTFLoader } from 'three/addons/loaders/GLTFLoader.js';
import { chooseLevel, evictionCandidates } from './lod.js';

function dispose(root) {
  const geometries=new Set(), materials=new Set(), textures=new Set();
  root.traverse(o=>{if(o.geometry)geometries.add(o.geometry);for(const m of [o.material].flat().filter(Boolean)){materials.add(m);for(const v of Object.values(m))if(v?.isTexture)textures.add(v);}});
  geometries.forEach(x=>x.dispose());materials.forEach(x=>x.dispose());textures.forEach(x=>{x.dispose();x.source?.data?.close?.();});
}
export class Streamer {
  constructor(scene,catalog,baseURL,onChange,onError,maxAnisotropy=1) {
    this.scene=scene;this.baseURL=baseURL;this.onChange=onChange;this.onError=onError;
    this.entries=[];this.loader=new GLTFLoader();this.cache=new Map();this.pending=0;this.bytes=0;
    this.budget=256*1024*1024;this.wireframe=false;
    this.anisotropy=Math.max(1,Math.min(16,maxAnisotropy));
    for(const asset of catalog.assets){
      const group=new THREE.Group();group.position.fromArray(asset.position);group.rotation.y=asset.rotationY;scene.add(group);group.updateMatrixWorld(true);
      for(const part of asset.parts){
        const slot=new THREE.Group();group.add(slot);
        const box=new THREE.Box3(new THREE.Vector3().fromArray(part.bounds[0]),new THREE.Vector3().fromArray(part.bounds[1])).applyMatrix4(group.matrixWorld);
        this.entries.push({asset,part,slot,box,current:null,wanted:null,loading:null,failed:new Set(),distance:Infinity});
      }
    }
  }
  update(camera,settings,force){
    for(const entry of this.entries){
      entry.distance=entry.box.distanceToPoint(camera.position);
      const available=Object.keys(entry.part.levels);
      entry.wanted=entry.part.fixedLevel || chooseLevel(entry.distance,entry.current,force,settings,available);
      if(entry.loading && entry.loading.level!==entry.wanted && entry.current!==null) entry.loading.controller.abort();
      const key=this.key(entry,entry.wanted);
      if(this.cache.has(key))this.activate(entry,entry.wanted);
    }
    const queue=this.entries.filter(e=>e.wanted && !e.loading && e.current!==e.wanted).sort((a,b)=>(a.part.fixedLevel?-1:0)-(b.part.fixedLevel?-1:0)||a.distance-b.distance);
    for(const entry of queue){
      if(this.pending>=2)break;
      // Show an inexpensive complete part while its selected level is fetched.
      const level=entry.current===null && entry.part.levels.district && !entry.failed.has('district') && entry.wanted!=='district' ? 'district' : entry.wanted;
      if(!entry.failed.has(level)) this.load(entry,level);
    }
    this.evict();
  }
  key(entry,level){return `${entry.asset.id}/${entry.part.id}/${level}`;}
  async load(entry,level){
    const key=this.key(entry,level), record=entry.part.levels[level], controller=new AbortController();
    entry.loading={level,controller};this.pending++;this.onChange();
    try{
      const response=await fetch(new URL(record.uri,this.baseURL),{signal:controller.signal});
      if(!response.ok)throw new Error(`HTTP ${response.status}`);
      const bytes=await response.arrayBuffer();this.bytes+=bytes.byteLength;
      if(controller.signal.aborted)return;
      const gltf=await this.loader.parseAsync(bytes,'');
      if(controller.signal.aborted){dispose(gltf.scene);return;}
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
      this.cache.set(key,{key,root:gltf.scene,bytes:record.gpuBytesEstimate||record.bytes*3,used:performance.now(),entry,level});
      if(entry.current===null || entry.wanted===level)this.activate(entry,level);
    }catch(error){if(error.name!=='AbortError'){entry.failed.add(level);this.onError(`${entry.part.name}: ${error.message}`);}}
    finally{entry.loading=null;this.pending--;this.onChange();}
  }
  activate(entry,level){
    const cached=this.cache.get(this.key(entry,level));if(!cached)return;
    cached.used=performance.now();
    if(entry.current===level)return;
    entry.slot.clear();entry.slot.add(cached.root);entry.current=level;this.onChange();
  }
  evict(){
    const records=[...this.cache.values()].map(r=>({...r,active:r.entry.current===r.level}));
    for(const key of evictionCandidates(records,this.budget)){const r=this.cache.get(key);dispose(r.root);this.cache.delete(key);}
  }
  setWireframe(value){this.wireframe=value;for(const r of this.cache.values())r.root.traverse(o=>{for(const m of [o.material].flat().filter(Boolean))m.wireframe=value;});}
  get residentBytes(){return [...this.cache.values()].reduce((n,r)=>n+r.bytes,0);}
  get activeRoots(){return this.entries.filter(e=>e.current).map(e=>e.slot);}
  get groundRoots(){return this.entries.filter(e=>e.part.ground && e.current).map(e=>e.slot);}
}
