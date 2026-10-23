/** Pure geographic working-set and estimated memory admission policy. */
export function horizontalDistance(bounds,position){
  return Math.hypot(Math.max(bounds[0][0]-position[0],0,position[0]-bounds[1][0]),
                    Math.max(bounds[0][2]-position[2],0,position[2]-bounds[1][2]));
}
export function selectedCells(cells,position,radius){
  return cells.filter(c=>horizontalDistance(c.bounds,position)<=radius)
    .sort((a,b)=>horizontalDistance(a.bounds,position)-horizontalDistance(b.bounds,position)||a.key.localeCompare(b.key));
}
export function estimatedBytes(record){return record?.gpuBytesEstimate ?? (record?.bytes||0)*3;}
export function admit(candidates,budget){
  // Ground first, then nearest parts. Every admitted part fits individually and
  // collectively; a huge part cannot silently override the budget.
  let used=0;const result=new Map();
  const ordered=[...candidates].sort((a,b)=>Number(!!b.ground)-Number(!!a.ground)||a.distance-b.distance||a.key.localeCompare(b.key));
  const levels=e=>(e.fixed?[e.wanted]:['detail','walk','district'].slice(Math.max(0,['detail','walk','district'].indexOf(e.wanted)))).filter(l=>e.levels[l]);
  // Establish coarse coverage before spending remaining space on refinements.
  // Nearby detail must not crowd out buildings that would fit at District.
  for(const e of ordered){
    const level=levels(e).reverse().find(l=>used+estimatedBytes(e.levels[l])<=budget);
    if(level){used+=estimatedBytes(e.levels[level]);result.set(e.key,level);}
  }
  for(const e of ordered){
    const current=result.get(e.key);if(!current)continue;
    const old=estimatedBytes(e.levels[current]);
    const level=levels(e).find(l=>used-old+estimatedBytes(e.levels[l])<=budget);
    used+=estimatedBytes(e.levels[level])-old;result.set(e.key,level);
  }
  return {levels:result,bytes:used};
}
export function mergeCells(nodes,position,radius,margin,previous=[]){
  const kept=new Set(previous.map(e=>`${e.asset.id}/${e.part.id}`));const assets=new Map();
  for(const node of nodes)for(const asset of node.assets)for(const part of asset.parts){
    const key=`${asset.id}/${part.id}`;
    if(horizontalDistance(part.worldBounds,position)>radius+(kept.has(key)?margin:0))continue;
    const row=assets.get(asset.id)||{...asset,parts:[]};
    if(row.assetRevision!==asset.assetRevision)throw new Error('Mixed asset revisions in spatial snapshot');
    if(!row.parts.some(p=>p.id===part.id))row.parts.push(part);
    assets.set(asset.id,row);
  }
  return [...assets.values()].sort((a,b)=>a.id.localeCompare(b.id)).map(a=>({...a,parts:a.parts.sort((a,b)=>a.id.localeCompare(b.id))}));
}
