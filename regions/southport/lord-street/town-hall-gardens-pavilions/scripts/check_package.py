"""Actual GLB budgets, retained pavilion extents, and scoped overlap audit."""
import argparse,json,sys
from pathlib import Path
import numpy as np
p=argparse.ArgumentParser();p.add_argument('--package',type=Path,required=True);p.add_argument('--recipe',type=Path,required=True);a=p.parse_args()
repo=a.recipe.resolve().parents[4];sys.path[:0]=[str(repo/'tools'),str(repo/'lib')]
from audit_published_coplanar import primitives
from coplanar import overlaps
manifest=json.loads((a.package/'manifest.json').read_text());rows=[]
for part in ('north','south'):
 baseline=None
 for level in ('detail','walk','district'):
  f=next(x for x in manifest['files'] if x['part']==part and x['level']==level)
  budget=220 if level=='district' else 60000
  assert f['triangles']<=budget,(part,level,f['triangles'])
  assert f['bytes']<4000000 and f['gpuBytesEstimate']<5000000,(part,level,'resource budget',f)
  chunks=[];labels=[]
  for tri,source in primitives(a.package/f['path'],{'rotationY':0,'position':[0,0,0]}):
   chunks.append(tri);labels.extend([source['node']]*len(tri))
  tris=np.concatenate(chunks);errors=overlaps(tris,labels)
  assert not errors,(part,level,'coplanar exterior',errors[:8])
  verts=tris.reshape(-1,3);bounds=np.array([verts.min(axis=0),verts.max(axis=0)])
  if level=='detail':baseline=bounds
  else:
   assert np.max(np.abs(bounds-baseline))<.35,(part,level,'envelope silhouette bounds',bounds,baseline)
  rows.append({'part':part,'level':level,'triangles':f['triangles'],'bytes':f['bytes'],'gpu_bytes':f['gpuBytesEstimate'],'coplanar_pairs':len(errors)})
(a.package/'pavilion-check.json').write_text(json.dumps(rows,indent=2)+'\n')
print('Pavilion exported GLB checks:',rows)
