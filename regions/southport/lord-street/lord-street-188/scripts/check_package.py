"""Enforce size, finite float32 triangles, surface ownership and open gaps."""
import argparse,json,sys
from pathlib import Path
import numpy as np
p=argparse.ArgumentParser();p.add_argument('--package',type=Path,required=True);p.add_argument('--recipe',type=Path,required=True);args=p.parse_args()
repo=args.recipe.resolve().parents[4];sys.path.insert(0,str(repo/'tools'))
from publication import inspect_glb
from audit_published_coplanar import primitives
from coplanar import overlaps
assembly=json.loads((args.package/'assembly.json').read_text());rows=[]
for level in ('detail','walk','district'):
 files=[args.package/f['path'] for f in assembly['files'] if f['level']==level];assert files
 infos=[inspect_glb(f)for f in files];count=sum(i['triangles']for i in infos);size=sum(i['bytes']for i in infos);gpu=sum(i['gpuBytesEstimate']for i in infos)
 assert count<=({'detail':70000,'walk':70000,'district':1800}[level]),(level,count)
 if level=='district':assert size<=3000000 and gpu<=13107200,(size,gpu)
 primitives_all=[(ts,o)for f in files for ts,o in primitives(f,{'rotationY':0,'position':[0,0,0]})]
 ts=np.concatenate([v for v,_ in primitives_all]);assert np.isfinite(ts).all()
 cross=np.cross(ts[:,1]-ts[:,0],ts[:,2]-ts[:,0]);assert np.all(np.linalg.norm(cross,axis=1)>1e-9),(level,'degenerate float32 triangles')
 labels=[o['node']for t,o in primitives_all for _ in t];issues=overlaps(ts,labels);assert not issues,(level,issues[:10])
 for x,y in ((455,-33.5),(455,-65)):
  q=np.array([x,-y]);v=ts[:,:,[0,2]];a,b,c=v[:,0],v[:,1],v[:,2]
  def cross2(a,b):return a[:,0]*b[:,1]-a[:,1]*b[:,0]
  den=cross2(b-a,c-a);good=np.abs(den)>1e-9;u=np.zeros(len(ts));w=u.copy();u[good]=cross2(np.broadcast_to(q,a.shape)-a,c-a)[good]/den[good];w[good]=cross2(b-a,np.broadcast_to(q,a.shape)-a)[good]/den[good]
  h=ts[:,0,1]+u*(ts[:,1,1]-ts[:,0,1])+w*(ts[:,2,1]-ts[:,0,1]);assert not (good&(u>=0)&(w>=0)&(u+w<=1)&(h>1)).any(),(level,'obstructed gap',x,y)
 rows.append({'level':level,'triangles':count,'bytes':size,'gpu_bytes':gpu,'gaps':2,'coplanar':len(issues)})
(args.package/'building-export-check.json').write_text(json.dumps(rows,indent=2)+'\n');print(rows)
