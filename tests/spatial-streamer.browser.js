// Execute in the served viewer. Requests and loaders are isolated to this fixture.
async () => {
 const THREE=await import('three');
 const {SpatialStreamer}=await import('./spatial-streamer.js');
 const assert=(v,m)=>{if(!v)throw new Error(m);};
 const oldFetch=window.fetch,requests=[];const nodes=new Map();
 const encoder=new TextEncoder();
 async function cell(id,x,version='one'){
   const asset={id,assetRevision:version,position:[x,0,0],rotationY:0,parts:[{
     id:'wall',name:id,bounds:[[0,0,0],[2,5,2]],worldBounds:[[x,0,0],[x+2,5,2]],
     levels:{district:{uri:`${id}-${version}.glb`,bytes:1,gpuBytesEstimate:20}}}]};
   const bytes=encoder.encode(JSON.stringify({assets:[asset]}));
   const digest=[...new Uint8Array(await crypto.subtle.digest('SHA-256',bytes))].map(n=>n.toString(16).padStart(2,'0')).join('');
   const uri=`${id}-${version}.json`;nodes.set(uri,bytes);
   return {key:id,uri,sha256:digest,bounds:[[x,0,0],[x+2,5,2]]};
 }
 const near=await cell('near',0),far=await cell('far',1000);
 const root={revision:'one',cells:[near,far],streaming:{radius:100,margin:16,retentionMs:0,budget:100,stagingBudget:100}};
 window.fetch=(url,opts)=>{
   if(!String(url).startsWith('https://spatial-fixture.invalid/'))return oldFetch(url,opts);
   const name=new URL(url).pathname.slice(1);requests.push(name);
   return Promise.resolve(new Response(nodes.get(name)||new Uint8Array([1])));
 };
 const scene=new THREE.Scene(),manager=new SpatialStreamer(scene,root,new URL('https://spatial-fixture.invalid/'),()=>{},()=>{});
 const camera=new THREE.PerspectiveCamera();camera.position.set(0,2,0);
 const settings={detailDistance:8,districtDistance:70};
 const mesh=()=>{const r=new THREE.Group();r.add(new THREE.Mesh(new THREE.BoxGeometry(),new THREE.MeshBasicMaterial()));return r;};
 manager.current.loader.parseAsync=async()=>({scene:mesh()});
 const prepare=manager.prepareSnapshot.bind(manager);
 manager.prepareSnapshot=(...args)=>{prepare(...args);if(manager.staged)manager.staged.streamer.loader.parseAsync=async()=>({scene:mesh()});};
 async function tick(){if(manager.staged)manager.staged.streamer.loader.parseAsync=async()=>({scene:mesh()});manager.update(camera,settings,'district');await new Promise(r=>setTimeout(r,2));}
 async function until(check){for(let i=0;i<200;i++){await tick();if(check())return;}throw new Error('Spatial fixture timed out: '+manager.message);}
 try{
   await until(()=>manager.entries.some(e=>e.current));
   assert(manager.entries.length===1&&manager.entries[0].asset.id==='near','Loaded distant asset');
   assert(!requests.some(x=>x.startsWith('far')),'Fetched distant cell or mesh');
   const old=manager.entries[0].slot.children[0];let disposed=false;old.children[0].geometry.addEventListener('dispose',()=>disposed=true);
   camera.position.x=1000;
   await until(()=>manager.entries.length===1&&manager.entries[0].asset.id==='far'&&manager.entries[0].current);
   assert(disposed,'Travel did not release prior active mesh');
   assert(manager.nodes.size===1,'Distant manifest retained');
   assert(manager.residentBytes+manager.current.reservedBytes<=manager.budget,'Budget exceeded');
   const before=manager.entries[0].slot.children[0];
   const updated=await cell('far',1000,'two');manager.setPaused(true);manager.setCatalog({...root,revision:'two',cells:[near,updated]});
   for(let i=0;i<5;i++)await tick();
   assert(manager.entries[0].slot.children[0]===before,'Paused live update applied');
   manager.setPaused(false);await tick();manager.frozen=true;
   for(let i=0;i<5;i++)await tick();
   assert(manager.entries[0].slot.children[0]===before,'Snag freeze changed the scene');
   manager.frozen=false;
   await until(()=>manager.entries[0].asset.assetRevision==='two'&&!manager.staged);
   assert(camera.position.x===1000,'Live update moved camera');
   const good=manager.entries[0].slot.children[0];
   manager.setCatalog({...root,revision:'bad',cells:[{...updated,uri:'corrupt.json'}]});
   await until(()=>manager.message.includes('hash mismatch'));
   assert(manager.entries[0].slot.children[0]===good,'Failed replacement removed last good model');
   manager.setCatalog({...root,revision:'empty',cells:[]});
   await until(()=>manager.entries.length===0);
   assert(manager.residentBytes===0,'Deleted scene retained resources');
   // Same transform convention as Python world_bounds: [0,0,0]..[2,3,4],
   // translation[10,1,20], rotation pi/2 => [10,1,18]..[14,4,20].
   const matrix=new THREE.Matrix4().makeRotationY(Math.PI/2);matrix.setPosition(10,1,20);
   const box=new THREE.Box3(new THREE.Vector3(),new THREE.Vector3(2,3,4)).applyMatrix4(matrix);
   assert(box.min.distanceTo(new THREE.Vector3(10,1,18))<1e-10&&box.max.distanceTo(new THREE.Vector3(14,4,20))<1e-10,'Python/three bounds mismatch');
   return {result:'Spatial lifecycle checks passed',requests};
 }finally{manager.destroy();window.fetch=oldFetch;}
}
