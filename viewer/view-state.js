// Local camera state is independent of model package versions.
export const VIEW_KEY='southport3d.view.v1';
export function readView(storage, worldOrigin){
  try {
    const v=JSON.parse(storage.getItem(VIEW_KEY));
    const tuple=(a,n)=>Array.isArray(a)&&a.length===n&&a.every(Number.isFinite);
    if(v?.version!==1||!['orbit','walk'].includes(v.mode)||
       !tuple(v.position,3)||!tuple(v.quaternion,4)||!tuple(v.target,3)||
       !tuple(v.worldOrigin,2)||v.worldOrigin.some((x,i)=>x!==worldOrigin[i])||
       !Number.isFinite(v.fov)||v.fov<10||v.fov>120||
       !Number.isFinite(v.walkFloor)||typeof v.dropPending!=='boolean')return null;
    const norm=Math.hypot(...v.quaternion);
    if(norm<.99||norm>1.01)return null;
    if(v.mode==='orbit'&&Math.hypot(...v.position.map((x,i)=>x-v.target[i]))<.001)return null;
    return v;
  }catch{return null;}
}
export function writeView(storage, view){
  try{storage.setItem(VIEW_KEY,JSON.stringify(view));return true;}catch{return false;}
}
