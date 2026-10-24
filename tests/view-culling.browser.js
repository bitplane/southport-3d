// Run in the served viewer with page.evaluate. Synthetic network/geometry only.
async () => {
  const THREE=await import('three');
  const {SpatialStreamer}=await import('./spatial-streamer.js');
  const {viewVolume}=await import('./view-volume.js');
  const assert=(value,message)=>{if(!value)throw new Error(message);};
  const camera=new THREE.PerspectiveCamera(50,2.064646,0.05,3000);
  camera.position.set(-200,778,135);camera.lookAt(-200,0,135);
  const volume=viewVolume(camera,250,0),visibleBounds=[[200,0,130],[210,20,140]];
  assert(volume.includes(visibleBounds),'High orbit excluded visible ground beyond horizontal radius');
  assert(!volume.includes([[4000,0,0],[4010,10,10]]),'Frustum admitted distant offscreen ground');
  camera.position.set(0,5,0);camera.lookAt(1000,5,0);
  assert(viewVolume(camera,100).includes([[995,0,-2],[1005,10,2]]),'Look direction ignored');
  camera.lookAt(-1000,5,0);
  assert(!viewVolume(camera,100).includes([[995,0,-2],[1005,10,2]]),'Rotation did not change visible selection');
  const originalFetch=window.fetch,requests=[],data=new Map();let release;
  const part=(id,x)=>({id,name:id,bounds:[[x,0,0],[x+2,5,2]],worldBounds:[[x,0,0],[x+2,5,2]],levels:{district:{uri:id+'.glb',bytes:1,gpuBytesEstimate:20}}});
  async function cell(id,parts,bounds){
    const bytes=new TextEncoder().encode(JSON.stringify({assets:[{id:'block',assetRevision:'one',position:[0,0,0],rotationY:0,parts}]}));
    const sha256=[...new Uint8Array(await crypto.subtle.digest('SHA-256',bytes))].map(x=>x.toString(16).padStart(2,'0')).join('');
    data.set(id+'.json',bytes);return {key:id,uri:id+'.json',sha256,bounds};
  }
  const a=await cell('a',[part('a',0)],[[0,0,0],[2,5,2]]);
  const b=await cell('b',[part('b',150)],[[150,0,0],[152,5,2]]);
  window.fetch=async(url,opts)=>{
    if(!String(url).startsWith('https://culling-fixture.invalid/'))return originalFetch(url,opts);
    const id=new URL(url).pathname.slice(1);requests.push(id);
    if(id==='b.json')await new Promise(resolve=>release=resolve);
    if(opts?.signal?.aborted)throw new DOMException('Aborted','AbortError');
    return new Response(data.get(id)||new Uint8Array([1]));
  };
  const manager=new SpatialStreamer(new THREE.Scene(),{revision:'one',cells:[a,b],streaming:{radius:100,margin:0,retentionMs:500,budget:100,stagingBudget:100}},new URL('https://culling-fixture.invalid/'),()=>{},()=>{});
  manager.current.loader.parseAsync=async()=>({scene:new THREE.Mesh(new THREE.BoxGeometry(),new THREE.MeshBasicMaterial())});
  camera.position.set(0,2,0);camera.lookAt(0,2,-1000);
  const tick=async()=>{manager.update(camera,{detailDistance:8,districtDistance:70},'district');assert(manager.residentBytes+manager.reservedBytes<=manager.budget,'Travel exceeded memory budget');await new Promise(r=>setTimeout(r,3));};
  const until=async fn=>{for(let i=0;i<200;i++){await tick();if(fn())return;}throw new Error('Culling fixture timed out');};
  try{
    await until(()=>manager.entries.some(e=>e.current));
    const entry=manager.entries[0],root=entry.slot.children[0];
    camera.position.x=65;await until(()=>!!release);
    for(let i=0;i<4;i++){camera.position.x+=17;await tick();}
    assert(requests.filter(x=>x==='b.json').length===1,'Movement restarted pending cell fetch');
    manager.frozen=true;release();
    await until(()=>!!manager.prepared);
    assert(manager.entries.length===1&&entry.slot.children[0]===root,'Late cell fetch changed frozen snag');
    manager.frozen=false;
    await until(()=>manager.entries.some(e=>e.part.id==='b'&&e.current));
    assert(manager.entries.find(e=>e.part.id==='a')===entry&&entry.slot.children[0]===root,'Adding a part replaced unchanged model');
    assert(requests.filter(x=>x==='a.glb').length===1,'Travel downloaded unchanged part again');
    camera.position.x=1000;await tick();
    assert(entry.current,'Model immediately unloaded outside view');
    await until(()=>manager.entries.length===0);
    assert(manager.residentBytes===0&&manager.scene.children.length===0,'Expired retained models leaked');
    return 'View, delayed movement, incremental parts and retention checks passed';
  }finally{release?.();manager.destroy();window.fetch=originalFetch;}
}
