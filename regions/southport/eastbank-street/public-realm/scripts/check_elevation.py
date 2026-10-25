"""Check actual exported levels, profile interiors and bridge support layers."""
import argparse,json,sys
from pathlib import Path
import numpy as np
REPO=next(p for p in Path(__file__).resolve().parents if (p/'tools/check_lods.py').is_file());sys.path[:0]=[str(REPO/'tools'),str(REPO/'lib')]
from audit_published_coplanar import primitives
from southport3d.elevation import Elevations
p=argparse.ArgumentParser();p.add_argument('--package',type=Path,required=True);p.add_argument('--recipe',type=Path,required=True);args=p.parse_args()
e=Elevations(REPO/'regions/southport/elevation/eastbank.json');surface=e.surface('eastbank-pavement');manifest=json.loads((args.package/'manifest.json').read_text());reference=None;counts={}
for level in ['detail','walk','district']:
 triangles=[];total_bytes=0
 for row in manifest['files']:
  if row['level']!=level:continue
  total_bytes+=row['bytes']
  if not row['part'].endswith('ground'):continue
  for tris,src in primitives(args.package/row['path'],{'rotationY':0,'position':[0,0,0]}):
   # Convert glTF local Y-up into authored XY/Z-up.
   t=tris[:,:,[0,2,1]]*[1,-1,1]
   if src['node'].endswith('kerb'):continue
   centre=t.mean(axis=1)
   expected=np.array([0 if row['part']=='rail-ground' else surface.height(x,y)-(.12 if any(src['node'].endswith(' '+m)for m in ['asphalt','white','yellow'])else 0)for x,y,z in centre])
   assert np.max(abs(centre[:,2]-expected))<8e-5,(row['path'],src['node'],'lost slope break')
   triangles.append(t)
 t=np.concatenate(triangles);counts[level]={'ground_triangles':len(t),'bytes':total_bytes}
 assert total_bytes<3000000,(level,total_bytes,'download budget')
 # All levels share EXACT topology/positions here, not merely endpoints.
 if reference is None:reference=t
 else:assert t.shape==reference.shape and np.max(abs(t-reference))<1e-6,level
 a=t[:,0,:2];u=t[:,1,:2]-a;v=t[:,2,:2]-a;det=u[:,0]*v[:,1]-u[:,1]*v[:,0]
 q=np.array([-334.3,-602])-a
 with np.errstate(divide='ignore',invalid='ignore'):
  b=(q[:,0]*v[:,1]-q[:,1]*v[:,0])/det;c=(u[:,0]*q[:,1]-u[:,1]*q[:,0])/det
 mask=(abs(det)>1e-10)&(b>=-1e-8)&(c>=-1e-8)&(b+c<=1+1e-8)
 z=t[:,0,2]+b*(t[:,1,2]-t[:,0,2])+c*(t[:,2,2]-t[:,0,2]);heights=z[mask]
 assert any(abs(heights)<1e-5) and any(abs(heights-(surface.height(-334.3,-602)-.12))<8e-5),(level,heights)
print('Published elevation profiles/LoD identity/bridge levels:',counts)
