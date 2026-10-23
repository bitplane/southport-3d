// Evaluate this function in a served viewer page (Playwright page.evaluate).
async () => {
  const THREE=await import('three');
  const {Streamer}=await import('./streamer.js');
  const assert=(value,message)=>{if(!value)throw new Error(message);};
  const originalFetch=window.fetch;
  window.fetch=(url,options)=>String(url).startsWith('https://live-fixture.invalid/')
    ? Promise.resolve(new Response(new Uint8Array([1]))) : originalFetch(url,options);
  const asset=version=>({id:'test',position:[0,0,0],rotationY:0,parts:[{
    id:'wall',name:'wall',bounds:[[0,0,0],[1,1,1]],
    levels:{district:{uri:version+'.glb',bytes:1}}
  }]});
  const make=version=>new Streamer(new THREE.Scene(),{assets:[asset(version)]},
    new URL('https://live-fixture.invalid/'),()=>{},()=>{});
  const mesh=()=>{const root=new THREE.Group();root.add(new THREE.Mesh(
    new THREE.BoxGeometry(),new THREE.MeshBasicMaterial()));return root;};
  const instances=[];
  try {
    const old=make('old');instances.push(old);
    old.loader.parseAsync=async()=>({scene:mesh()});
    await old.load(old.entries[0],'district');
    const original=old.entries[0].slot.children[0];
    const next=make('next');instances.push(next);
    let finish;
    next.loader.parseAsync=()=>new Promise(resolve=>finish=resolve);
    const loading=next.load(next.entries[0],'district');
    while(!finish)await new Promise(resolve=>setTimeout(resolve,1));
    assert(old.entries[0].slot.children[0]===original,'Old geometry lost during staging');
    finish({scene:mesh()});await loading;
    assert(old.key(old.entries[0],'district')!==next.key(next.entries[0],'district'),'Revision cache collision');
    old.adopt(next,new Set(['test']));
    assert(old.entries.length===1 && old.entries[0].part.levels.district.uri==='next.glb','Batch adoption failed');
    assert(old.scene.children.length===1,'Old asset group leaked');
    const paused=make('paused');instances.push(paused);paused.frozen=true;
    paused.loader.parseAsync=async()=>({scene:mesh()});
    await paused.load(paused.entries[0],'district');
    assert(paused.entries[0].current===null,'Late activation changed frozen scene');
    paused.frozen=false;paused.activate(paused.entries[0],'district');
    assert(paused.entries[0].current==='district','Frozen load could not resume');
    const stale=make('stale');instances.push(stale);
    let done;
    stale.loader.parseAsync=()=>new Promise(resolve=>done=resolve);
    const late=stale.load(stale.entries[0],'district');
    while(!done)await new Promise(resolve=>setTimeout(resolve,1));
    const root=mesh();let disposed=false;
    root.children[0].geometry.addEventListener('dispose',()=>disposed=true);
    stale.destroy();done({scene:root});await late;
    assert(stale.cache.size===0 && disposed,'Superseded decode leaked or resurrected');
    const bounded=make('bounded');instances.push(bounded);bounded.budget=20;
    bounded.entries[0].part.levels={detail:{uri:'detail.glb',bytes:1,gpuBytesEstimate:10},district:{uri:'district.glb',bytes:1,gpuBytesEstimate:40}};
    bounded.loader.parseAsync=async()=>({scene:mesh()});
    bounded.update(new THREE.PerspectiveCamera(),{detailDistance:8,districtDistance:70},'detail');
    while(bounded.pending)await new Promise(resolve=>setTimeout(resolve,1));
    assert(bounded.entries[0].current==='detail','Expensive District bootstrap blocked cheaper Detail');
    assert(bounded.residentBytes<=bounded.budget,'Admission exceeded budget');
    return 'Streamer lifecycle checks passed';
  } finally {
    window.fetch=originalFetch;
    for(const instance of instances)instance.destroy();
  }
}
