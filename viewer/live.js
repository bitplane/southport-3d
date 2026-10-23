// Compare complete asset records: transforms, boundaries and removals matter too.
export function changedAssets(before,after){
  const old=new Map(before.assets.map(a=>[a.id,JSON.stringify(a)]));
  const next=new Map(after.assets.map(a=>[a.id,JSON.stringify(a)]));
  return new Set([...old.keys(),...next.keys()].filter(id=>old.get(id)!==next.get(id)));
}
export function compatible(before,after){
  return before.schema_version===after.schema_version &&
    before.viewerVersion===after.viewerVersion &&
    JSON.stringify(before.worldOrigin)===JSON.stringify(after.worldOrigin) &&
    before.coordinateSystem===after.coordinateSystem;
}
// Notifications are hints. Always fetch the latest catalog, including on reconnect.
export function watchCatalog(onCatalog,onStatus){
  let busy=false,again=false,closed=false;
  async function check(){
    if(closed)return;
    if(busy){again=true;return;}
    busy=true;
    try{
      const response=await fetch(new URL('scene.json',location.href),{cache:'no-store'});
      if(!response.ok)throw new Error('Catalog unavailable');
      const catalog=await response.json();
      if(!Array.isArray(catalog.assets)||!catalog.assets.length)throw new Error('Invalid catalog');
      onCatalog(catalog);onStatus(true);
    }catch{onStatus(false);}
    finally{busy=false;if(again){again=false;check();}}
  }
  const events=new EventSource('/api/events');
  events.addEventListener('catalog',check);events.onopen=check;
  events.onerror=()=>onStatus(false);
  // Also supports static hosting, an older server and sleeping/disconnected tabs.
  const timer=setInterval(check,15000);
  const visible=()=>{if(!document.hidden)check();};
  document.addEventListener('visibilitychange',visible);
  check();
  return ()=>{closed=true;events.close();clearInterval(timer);document.removeEventListener('visibilitychange',visible);};
}
