import * as THREE from 'three';
import { OrbitControls } from 'three/addons/controls/OrbitControls.js';
import { PointerLockControls } from 'three/addons/controls/PointerLockControls.js';
import { RoomEnvironment } from 'three/addons/environments/RoomEnvironment.js';
import { SpatialStreamer } from './spatial-streamer.js';
import { chooseLevel, formatBytes } from './lod.js';
import { installSnags } from './snags.js';
import { readView, writeView } from './view-state.js';
import { changedAssets, compatible, watchCatalog } from './live.js';

const $=id=>document.getElementById(id), viewport=$('viewport');
const showError=message=>{$('error').textContent=message;$('error').hidden=false;console.error(message);};
let renderer,streamer,mode='orbit',catalog,frames=0,lastStats=0,lastStream=0,lastSave=0,viewReady=false,lastSaved=null;
const settings={detailDistance:8,districtDistance:70};
const scene=new THREE.Scene();scene.background=new THREE.Color('#dce5df');scene.fog=new THREE.Fog('#dce5df',250,1400);
const camera=new THREE.PerspectiveCamera(50,innerWidth/innerHeight,.05,3000);
const keys=new Set(),clock=new THREE.Clock(),ray=new THREE.Raycaster();
const vector=new THREE.Vector3(),down=new THREE.Vector3(0,-1,0);
let orbit,walkControl,drag=null,walkFloor=0,reporting=false,dropPending=false,dropTimer=0;
let pendingCatalog=null;
let livePaused=false,liveConnected=true,reloadNeeded=false,liveMessage='';
let groundRevision=null;
function liveStatus(){
  $('live-status').textContent=reloadNeeded?'Viewer update available — reload when ready':
    reporting?'Updates paused while reporting':livePaused?(liveMessage||'Updates paused'):
    streamer?.staged||streamer?.loading?'Downloading nearby models…':!liveConnected?'Checking for updates — connection interrupted':liveMessage||'Live updates on';
  $('live-reload').hidden=!reloadNeeded;
}
function receiveCatalog(next){
  if(next.revision===catalog.revision && next.viewerVersion===catalog.viewerVersion)return;
  if(!compatible(catalog,next)){reloadNeeded=true;pendingCatalog=null;liveStatus();return;}
  pendingCatalog=next;liveStatus();
}
function updateLive(){
  streamer.setPaused(livePaused||reloadNeeded);
  if(reporting||livePaused||reloadNeeded||!pendingCatalog)return;
  catalog=pendingCatalog;pendingCatalog=null;streamer.setCatalog(catalog);
  liveMessage='';liveStatus();
}

function status(){
  if(!streamer)return;
  liveStatus();
  const revision=streamer.appliedCatalog?.revision;
  if(revision&&revision!==groundRevision){
    groundRevision=revision;
    if(mode==='walk'){
      scene.updateMatrixWorld(true);
      ray.set(new THREE.Vector3(camera.position.x,camera.position.y+5,camera.position.z),down);ray.far=Infinity;
      const hit=ray.intersectObjects(streamer.groundRoots,true).find(h=>h.face);
      if(hit){walkFloor=hit.point.y;camera.position.y=walkFloor+1.7;dropPending=false;}
    }
  }
  const ready=streamer.entries.filter(e=>e.current).length, failed=streamer.entries.some(e=>e.failed.size);
  const deferred=streamer.entries.filter(e=>e.deferred).length;
  $('status').textContent=streamer.pending?`Loading detail · ${ready}/${streamer.entries.length} parts ready`:failed?'Some detail could not load':`${ready} parts ready${deferred?` · ${deferred} deferred by budget`:''} · ${mode==='walk'?'Walking':'Exploring'}`;
  $('status-dot').classList.toggle('ready',!streamer.pending && ready>0 && !failed);
  $('downloaded').textContent=formatBytes(streamer.bytes);$('resident').textContent=formatBytes(streamer.residentBytes);
  if(renderer)renderer.shadowMap.needsUpdate=true;
}
function assetPoint(asset,p){return new THREE.Vector3().fromArray(p).applyAxisAngle(new THREE.Vector3(0,1,0),asset.rotationY).add(new THREE.Vector3().fromArray(asset.position));}
function overview(){
  const asset=catalog.assets.find(a=>a.id==='southport.london-square.war-memorial')||catalog.assets.find(a=>a.views?.length);
  const view=asset.views[0];setMode('orbit');
  camera.position.copy(assetPoint(asset,view.position));orbit.target.copy(assetPoint(asset,view.target));orbit.update();
}
function saveView(){
  if(!viewReady)return;
  const view={version:1,worldOrigin:catalog.worldOrigin,mode,position:camera.position.toArray(),
    quaternion:camera.quaternion.toArray(),target:orbit.target.toArray(),fov:camera.fov,walkFloor,dropPending};
  const value=JSON.stringify(view);if(value===lastSaved)return;
  try{if(writeView(localStorage,view))lastSaved=value;}catch{} // Storage can be disabled.
}
function restoreSavedView(){
  let saved;try{saved=readView(localStorage,catalog.worldOrigin);}catch{return false;}
  if(!saved)return false;
  // Restore Walk without triggering another drop or a location reset.
  mode=saved.mode;orbit.enabled=mode==='orbit';updateModeUI();
  camera.position.fromArray(saved.position);camera.quaternion.fromArray(saved.quaternion).normalize();
  camera.fov=saved.fov;camera.updateProjectionMatrix();orbit.target.fromArray(saved.target);
  walkFloor=saved.walkFloor;dropPending=saved.dropPending;dropTimer=0;
  if(mode==='orbit')orbit.update();
  return true;
}
function nearestAsset(){
  return streamer.entries.reduce((best,e)=>!best||e.box.distanceToPoint(camera.position)<best.box.distanceToPoint(camera.position)?e:best,null)?.asset||catalog.assets[0];
}
function setMode(next){
  if(next===mode)return;
  mode=next;orbit.enabled=next==='orbit';keys.clear();drag=null;dropPending=false;
  if(next==='orbit'){
    walkControl.unlock();camera.getWorldDirection(vector);orbit.target.copy(camera.position).addScaledVector(vector,12);orbit.update();
  }else{
    // Keep position and heading; ground may still be streaming beneath us.
    walkFloor=camera.position.y-1.7;dropPending=true;dropTimer=0;dropToGround();
  }
  updateModeUI();
}
function updateModeUI(){
  $('orbit').classList.toggle('active',mode==='orbit');$('walk').classList.toggle('active',mode==='walk');$('orbit').setAttribute('aria-pressed',mode==='orbit');$('walk').setAttribute('aria-pressed',mode==='walk');
  $('walk-tools').hidden=mode!=='walk';$('crosshair').hidden=mode!=='walk';
  $('controls-hint').textContent=mode==='walk'?'WASD / arrows to walk · Shift to move faster · Drag to look':'Drag to orbit · WASD / arrows to move · Shift to move faster · Scroll to zoom · Right-drag to pan';status();
}
function dropToGround(){
  scene.updateMatrixWorld(true);
  ray.set(new THREE.Vector3(camera.position.x,camera.position.y+.05,camera.position.z),down);ray.far=Infinity;
  const hit=ray.intersectObjects(streamer.groundRoots,true).find(h=>h.face);
  if(!hit)return; // Unmodelled/unloaded ground: stay here, never use a remote spawn.
  walkFloor=hit.point.y;camera.position.y=walkFloor+1.7;dropPending=false;
}
function moveOrbit(dt){
  if(mode!=='orbit'||reporting)return;
  const x=Number(keys.has('KeyD')||keys.has('ArrowRight'))-Number(keys.has('KeyA')||keys.has('ArrowLeft'));
  const z=Number(keys.has('KeyW')||keys.has('ArrowUp'))-Number(keys.has('KeyS')||keys.has('ArrowDown'));
  if(!x&&!z)return;
  camera.updateMatrixWorld();
  // Camera-right remains stable even when looking nearly straight down.
  vector.setFromMatrixColumn(camera.matrixWorld,0);vector.y=0;vector.normalize();
  const speed=THREE.MathUtils.clamp(camera.position.distanceTo(orbit.target)*.7,3,180);
  const step=speed*(keys.has('ShiftLeft')||keys.has('ShiftRight')?3:1)*Math.min(dt,.05)/Math.max(1,Math.hypot(x,z));
  const rightX=vector.x,rightZ=vector.z;
  vector.set((rightX*x+rightZ*z)*step,0,(rightZ*x-rightX*z)*step);
  camera.position.add(vector);orbit.target.add(vector);
}
function resize(){const dpr=Math.min(devicePixelRatio,2)*Number($('resolution').value);renderer.setPixelRatio(dpr);renderer.setSize(innerWidth,innerHeight);camera.aspect=innerWidth/innerHeight;camera.updateProjectionMatrix();}
function walk(dt){
  if(mode!=='walk'||reporting)return;
  if(dropPending){dropTimer-=dt;if(dropTimer<=0){dropToGround();dropTimer=.2;}}
  const speed=(keys.has('ShiftLeft')||keys.has('ShiftRight')?5:1.8)*Math.min(dt,.05);
  const x=Number(keys.has('KeyD')||keys.has('ArrowRight'))-Number(keys.has('KeyA')||keys.has('ArrowLeft'));
  const z=Number(keys.has('KeyW')||keys.has('ArrowUp'))-Number(keys.has('KeyS')||keys.has('ArrowDown'));
  if(x||z){const scale=speed/Math.max(1,Math.hypot(x,z));walkControl.moveRight(x*scale);walkControl.moveForward(z*scale);
    // Ground-following only: no collision physics in this first inspection viewer.
    if(dropPending)return;
    ray.set(new THREE.Vector3(camera.position.x,walkFloor+.6,camera.position.z),down);ray.far=5;
    const hit=ray.intersectObjects(streamer.groundRoots,true).find(h=>h.face && h.point.y<=walkFloor+.45);
    if(hit)walkFloor=hit.point.y;camera.position.y=walkFloor+1.7;
  }
}
function animate(now){
  requestAnimationFrame(animate);const dt=clock.getDelta();walk(dt);moveOrbit(dt);if(mode==='orbit'&&!reporting)orbit.update();
  if(streamer && !reporting && now-lastStream>200){updateLive();streamer.update(camera,settings,$('quality').value);lastStream=now;}
  renderer.render(scene,camera);frames++;
  if(now-lastSave>500){saveView();lastSave=now;}
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
  window.addEventListener('keydown',e=>{if(reporting||e.target.matches('input,select,button,textarea,[contenteditable]'))return;if(['KeyW','KeyA','KeyS','KeyD','ArrowUp','ArrowDown','ArrowLeft','ArrowRight','ShiftLeft','ShiftRight'].includes(e.code)){e.preventDefault();keys.add(e.code);}});
  window.addEventListener('keyup',e=>keys.delete(e.code));window.addEventListener('blur',()=>{keys.clear();drag=null;});
  $('orbit').onclick=()=>{setMode('orbit');viewport.focus();};$('walk').onclick=()=>{setMode('walk');viewport.focus();};$('home').onclick=()=>{overview();saveView();viewport.focus();};$('capture').onclick=()=>walkControl.lock();
  $('settings-toggle').onclick=()=>{const open=$('settings-panel').hidden;$('settings-panel').hidden=!open;$('settings-toggle').setAttribute('aria-expanded',open);};
  for(const [id,key] of [['detail','detailDistance'],['district','districtDistance']])$(id+'-distance').oninput=()=>{settings[key]=Number($(id+'-distance').value);$(id+'-output').textContent=settings[key]+' m';};
  $('resolution').oninput=()=>{$('resolution-output').textContent=$('resolution').value+'×';resize();};$('wireframe').onchange=()=>streamer?.setWireframe($('wireframe').checked);$('shadows').onchange=()=>{renderer.shadowMap.enabled=$('shadows').checked;renderer.shadowMap.needsUpdate=true;};$('retry').onclick=()=>location.reload();
  const manifestURL=new URL('scene.json',location.href);const response=await fetch(manifestURL,{cache:'no-store'});if(!response.ok)throw new Error('The scene package is not ready yet. Reload in a moment.');catalog=await response.json();if(!catalog.assets?.length||!Array.isArray(catalog.cells))throw new Error('No buildings are available in this package.');
  settings.detailDistance=catalog.lodPolicy.detailDistance;settings.districtDistance=catalog.lodPolicy.districtDistance;
  streamer=new SpatialStreamer(scene,catalog,manifestURL,status,showError,renderer.capabilities.getMaxAnisotropy());
  for(const option of $('quality').options)if(option.value!=='auto')option.disabled=false;
  if(!restoreSavedView())overview();viewReady=true;resize();window.addEventListener('resize',resize);
  window.addEventListener('pagehide',saveView);window.addEventListener('beforeunload',saveView);
  document.addEventListener('visibilitychange',()=>{if(document.hidden)saveView();});
  const snags=installSnags({
    setActive(active){reporting=active;streamer.frozen=active;liveStatus();keys.clear();drag=null;orbit.enabled=!active&&mode==='orbit';if(active)walkControl.unlock();},
    capture(){
      renderer.render(scene,camera);
      const canvas=document.createElement('canvas'),source=renderer.domElement;
      const scale=Math.min(1,1920/Math.max(source.width,source.height));
      canvas.width=Math.round(source.width*scale);canvas.height=Math.round(source.height*scale);
      canvas.getContext('2d').drawImage(source,0,0,canvas.width,canvas.height);
      const target=mode==='orbit'?orbit.target.clone():camera.position.clone().addScaledVector(camera.getWorldDirection(new THREE.Vector3()),12);
      return {screenshot:canvas.toDataURL('image/jpeg',.92),view:{
        catalogRevision:(streamer.appliedCatalog||catalog).catalogRevision,sceneRevision:(streamer.appliedCatalog||catalog).revision,asset:nearestAsset().id,mode,worldOrigin:catalog.worldOrigin,coordinateSystem:catalog.coordinateSystem,
        camera:{position:camera.position.toArray(),quaternion:camera.quaternion.toArray(),target:target.toArray(),fov:camera.fov,aspect:camera.aspect},
        viewport:{width:innerWidth,height:innerHeight,imageWidth:canvas.width,imageHeight:canvas.height},
        quality:$('quality').value,settings:{...settings},wireframe:$('wireframe').checked,shadows:$('shadows').checked,
        parts:streamer.entries.filter(e=>e.current).map(e=>({asset:e.asset.id,part:e.part.id,level:e.current,resource:e.part.levels[e.current]?.uri})),pending:streamer.pending
      }};
    },
    restore(view){
      setMode('orbit');camera.position.fromArray(view.camera.position);camera.quaternion.fromArray(view.camera.quaternion);
      camera.fov=view.camera.fov;camera.updateProjectionMatrix();orbit.target.fromArray(view.camera.target);orbit.update();
      $('quality').value=view.quality;
      for(const [id,key] of [['detail','detailDistance'],['district','districtDistance']])if(Number.isFinite(view.settings?.[key])){
        settings[key]=view.settings[key];$(id+'-distance').value=settings[key];$(id+'-output').textContent=settings[key]+' m';
      }
      $('wireframe').checked=!!view.wireframe;streamer.setWireframe(!!view.wireframe);
      $('shadows').checked=!!view.shadows;renderer.shadowMap.enabled=!!view.shadows;renderer.shadowMap.needsUpdate=true;
    }
  });
  $('live-pause').onchange=()=>{livePaused=$('live-pause').checked;liveMessage='';liveStatus();};
  $('live-reload').onclick=()=>{if(!reporting){saveView();location.reload();}};
  watchCatalog(receiveCatalog,connected=>{liveConnected=connected;liveStatus();});
  liveStatus();
  $('snag-new').disabled=false;$('snag-queue').disabled=false;
  const snagId=new URLSearchParams(location.search).get('snag');if(snagId)snags.openReport(snagId);
  // Read-only state gives contributors a stable way to inspect browser runs.
  window.southport={getState:()=>({revision:(streamer.appliedCatalog||catalog).revision,requestedRevision:catalog.revision,live:{paused:livePaused,reporting,staging:!!streamer.staged,queued:pendingCatalog?.revision,reloadNeeded,message:liveMessage},mode,camera:camera.position.toArray(),target:orbit.target.toArray(),quality:$('quality').value,textureAnisotropy:streamer.anisotropy,pending:streamer.pending,transferred:streamer.bytes,resident:streamer.residentBytes,budget:streamer.budget,reserved:streamer.reservedBytes,stagedBytes:streamer.stagedBytes,cells:streamer.nodes.size,streamingMessage:streamer.message,triangles:renderer.info.render.triangles,parts:streamer.entries.map(e=>({asset:e.asset.id,id:e.part.id,deferred:e.deferred,level:e.current,wanted:e.wanted,distance:e.distance,error:[...e.failed]}))})};
  requestAnimationFrame(animate);
}
init().catch(e=>{showError(e.message);$('status').textContent='Unable to open scene';});
