import * as THREE from 'three';
import { OrbitControls } from 'three/addons/controls/OrbitControls.js';
import { PointerLockControls } from 'three/addons/controls/PointerLockControls.js';
import { RoomEnvironment } from 'three/addons/environments/RoomEnvironment.js';
import { Streamer } from './streamer.js';
import { formatBytes } from './lod.js';

const $=id=>document.getElementById(id), viewport=$('viewport');
const showError=message=>{$('error').textContent=message;$('error').hidden=false;console.error(message);};
let renderer,streamer,mode='orbit',catalog,selectedAsset,frames=0,lastStats=0,lastStream=0;
const settings={detailDistance:8,districtDistance:70};
const scene=new THREE.Scene();scene.background=new THREE.Color('#dce5df');scene.fog=new THREE.Fog('#dce5df',250,1400);
const camera=new THREE.PerspectiveCamera(50,innerWidth/innerHeight,.05,3000);
const keys=new Set(),clock=new THREE.Clock(),ray=new THREE.Raycaster();
const vector=new THREE.Vector3(),down=new THREE.Vector3(0,-1,0);
let orbit,walkControl,drag=null,walkFloor=0;
function status(){
  if(!streamer)return;
  const ready=streamer.entries.filter(e=>e.current).length, failed=streamer.entries.some(e=>e.failed.size);
  $('status').textContent=streamer.pending?`Loading detail · ${ready}/${streamer.entries.length} parts ready`:failed?'Some detail could not load':`${ready} parts ready · ${mode==='walk'?'Walking':'Exploring'}`;
  $('status-dot').classList.toggle('ready',!streamer.pending && ready>0 && !failed);
  $('downloaded').textContent=formatBytes(streamer.bytes);$('resident').textContent=formatBytes(streamer.residentBytes);
  $('part-status').replaceChildren(...streamer.entries.filter(e=>e.asset===selectedAsset).map(e=>{
    const line=document.createElement('div'),name=document.createElement('span'),level=document.createElement('span');name.textContent=e.part.name;level.textContent=e.loading?`${e.loading.level}…`:e.current||'waiting';line.append(name,level);return line;
  }));
  if(renderer)renderer.shadowMap.needsUpdate=true;
}
function assetPoint(asset,p){return new THREE.Vector3().fromArray(p).applyAxisAngle(new THREE.Vector3(0,1,0),asset.rotationY).add(new THREE.Vector3().fromArray(asset.position));}
function viewpoint(view){
  setMode('orbit');camera.position.copy(assetPoint(selectedAsset,view.position));orbit.target.copy(assetPoint(selectedAsset,view.target));orbit.update();
}
function selectAsset(asset){
  selectedAsset=asset;$('place-name').textContent=asset.areaName||asset.name;$('place-subtitle').textContent=asset.name+' · Southport, UK';
  $('coverage').textContent=asset.status;
  $('bookmarks').replaceChildren(...asset.views.map(view=>{const button=document.createElement('button');button.textContent=view.name;button.onclick=()=>viewpoint(view);return button;}));
  viewpoint(asset.views[0]);status();
}
function setMode(next){
  mode=next;orbit.enabled=next==='orbit';keys.clear();
  if(next==='orbit'){
    walkControl.unlock();camera.getWorldDirection(vector);orbit.target.copy(camera.position).addScaledVector(vector,12);orbit.update();
  }else if(selectedAsset){
    const spawn=selectedAsset.walkSpawn;camera.position.copy(assetPoint(selectedAsset,spawn.position));camera.lookAt(assetPoint(selectedAsset,spawn.target));walkFloor=camera.position.y-1.7;
  }
  $('orbit').classList.toggle('active',mode==='orbit');$('walk').classList.toggle('active',mode==='walk');$('orbit').setAttribute('aria-pressed',mode==='orbit');$('walk').setAttribute('aria-pressed',mode==='walk');
  $('walk-tools').hidden=mode!=='walk';$('crosshair').hidden=mode!=='walk';
  $('controls-hint').textContent=mode==='walk'?'WASD / arrows to walk · Shift to move faster · Drag to look':'Drag to orbit · Scroll to move closer · Right-drag to pan';status();
}
function resize(){const dpr=Math.min(devicePixelRatio,2)*Number($('resolution').value);renderer.setPixelRatio(dpr);renderer.setSize(innerWidth,innerHeight);camera.aspect=innerWidth/innerHeight;camera.updateProjectionMatrix();}
function walk(dt){
  if(mode!=='walk')return;
  const speed=(keys.has('ShiftLeft')||keys.has('ShiftRight')?5:1.8)*Math.min(dt,.05);
  const x=Number(keys.has('KeyD')||keys.has('ArrowRight'))-Number(keys.has('KeyA')||keys.has('ArrowLeft'));
  const z=Number(keys.has('KeyW')||keys.has('ArrowUp'))-Number(keys.has('KeyS')||keys.has('ArrowDown'));
  if(x||z){const scale=speed/Math.max(1,Math.hypot(x,z));walkControl.moveRight(x*scale);walkControl.moveForward(z*scale);
    // Ground-following only: no collision physics in this first inspection viewer.
    ray.set(new THREE.Vector3(camera.position.x,walkFloor+.6,camera.position.z),down);ray.far=5;
    const hit=ray.intersectObjects(streamer.groundRoots,true).find(h=>h.face && h.point.y<=walkFloor+.45);
    if(hit)walkFloor=hit.point.y;camera.position.y=walkFloor+1.7;
  }
}
function animate(now){
  requestAnimationFrame(animate);const dt=clock.getDelta();walk(dt);if(mode==='orbit')orbit.update();
  if(streamer && now-lastStream>200){streamer.update(camera,settings,$('quality').value);lastStream=now;}
  renderer.render(scene,camera);frames++;
  if(now-lastStats>1000){$('fps').textContent=`${Math.round(frames*1000/(now-lastStats))} fps`;$('triangles').textContent=renderer.info.render.triangles.toLocaleString();frames=0;lastStats=now;status();}
}
async function init(){
  try{renderer=new THREE.WebGLRenderer({antialias:true,powerPreference:'high-performance',logarithmicDepthBuffer:true});}catch(e){throw new Error('This browser could not start WebGL 2. Try enabling hardware acceleration.');}
  viewport.append(renderer.domElement);renderer.outputColorSpace=THREE.SRGBColorSpace;renderer.toneMapping=THREE.ACESFilmicToneMapping;renderer.toneMappingExposure=.95;
  renderer.shadowMap.type=THREE.PCFSoftShadowMap;renderer.shadowMap.autoUpdate=false;
  const pmrem=new THREE.PMREMGenerator(renderer),room=new RoomEnvironment();scene.environment=pmrem.fromScene(room,.04).texture;scene.environmentIntensity=.45;room.dispose();pmrem.dispose();
  scene.add(new THREE.HemisphereLight(0xf3f7f7,0x7b8069,.65));const sun=new THREE.DirectionalLight(0xfff2d8,2);sun.position.set(-40,70,35);sun.castShadow=true;sun.shadow.mapSize.set(2048,2048);Object.assign(sun.shadow.camera,{left:-90,right:90,top:90,bottom:-90,near:1,far:250});sun.shadow.bias=-.0002;scene.add(sun);
  orbit=new OrbitControls(camera,renderer.domElement);orbit.enableDamping=true;orbit.dampingFactor=.08;orbit.minDistance=.3;orbit.maxDistance=1800;orbit.maxPolarAngle=Math.PI*.495;
  walkControl=new PointerLockControls(camera,renderer.domElement);walkControl.addEventListener('lock',()=>{$('capture').textContent='Mouse captured';});walkControl.addEventListener('unlock',()=>{$('capture').textContent='Capture mouse';keys.clear();});
  renderer.domElement.addEventListener('pointerdown',e=>{if(mode==='walk'&&!walkControl.isLocked){drag={x:e.clientX,y:e.clientY};renderer.domElement.setPointerCapture(e.pointerId);}});
  renderer.domElement.addEventListener('pointermove',e=>{if(!drag||mode!=='walk'||walkControl.isLocked)return;const rotation=new THREE.Euler().setFromQuaternion(camera.quaternion,'YXZ');rotation.y-=(e.clientX-drag.x)*.003;rotation.x=THREE.MathUtils.clamp(rotation.x-(e.clientY-drag.y)*.003,-1.45,1.45);camera.quaternion.setFromEuler(rotation);drag={x:e.clientX,y:e.clientY};});
  renderer.domElement.addEventListener('pointerup',()=>{drag=null;});
  window.addEventListener('keydown',e=>{if(e.target.matches('input,select,button'))return;if(mode==='walk'&&['KeyW','KeyA','KeyS','KeyD','ArrowUp','ArrowDown','ArrowLeft','ArrowRight','ShiftLeft','ShiftRight'].includes(e.code)){e.preventDefault();keys.add(e.code);}});
  window.addEventListener('keyup',e=>keys.delete(e.code));window.addEventListener('blur',()=>{keys.clear();drag=null;});
  $('orbit').onclick=()=>setMode('orbit');$('walk').onclick=()=>{setMode('walk');viewport.focus();};$('home').onclick=()=>viewpoint(selectedAsset.views[0]);$('capture').onclick=()=>walkControl.lock();
  $('settings-toggle').onclick=()=>{const open=$('settings-panel').hidden;$('settings-panel').hidden=!open;$('settings-toggle').setAttribute('aria-expanded',open);};
  for(const [id,key] of [['detail','detailDistance'],['district','districtDistance']])$(id+'-distance').oninput=()=>{settings[key]=Number($(id+'-distance').value);$(id+'-output').textContent=settings[key]+' m';};
  $('resolution').oninput=()=>{$('resolution-output').textContent=$('resolution').value+'×';resize();};$('wireframe').onchange=()=>streamer?.setWireframe($('wireframe').checked);$('shadows').onchange=()=>{renderer.shadowMap.enabled=$('shadows').checked;renderer.shadowMap.needsUpdate=true;};$('retry').onclick=()=>location.reload();
  const manifestURL=new URL('catalog.json',location.href);const response=await fetch(manifestURL,{cache:'no-store'});if(!response.ok)throw new Error('The scene package is not ready yet. Reload in a moment.');catalog=await response.json();if(!catalog.assets?.length)throw new Error('No buildings are available in this package.');
  settings.detailDistance=catalog.lodPolicy.detailDistance;settings.districtDistance=catalog.lodPolicy.districtDistance;
  streamer=new Streamer(scene,catalog,manifestURL,status,showError);
  for(const asset of catalog.assets){const option=document.createElement('option');option.value=asset.id;option.textContent=asset.name;$('asset-select').append(option);}
  $('asset-select').onchange=()=>selectAsset(catalog.assets.find(a=>a.id===$('asset-select').value));
  for(const option of $('quality').options)if(option.value!=='auto')option.disabled=!catalog.assets.some(a=>a.parts.some(p=>p.levels[option.value]));
  selectAsset(catalog.assets[0]);resize();window.addEventListener('resize',resize);
  // Read-only state gives contributors a stable way to inspect browser runs.
  window.southport={getState:()=>({mode,camera:camera.position.toArray(),target:orbit.target.toArray(),quality:$('quality').value,pending:streamer.pending,transferred:streamer.bytes,resident:streamer.residentBytes,triangles:renderer.info.render.triangles,parts:streamer.entries.map(e=>({id:e.part.id,level:e.current,wanted:e.wanted,distance:e.distance,error:[...e.failed]}))})};
  requestAnimationFrame(animate);
}
init().catch(e=>{showError(e.message);$('status').textContent='Unable to open scene';});
