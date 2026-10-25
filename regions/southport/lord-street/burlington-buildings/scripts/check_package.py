"""Exported envelope budgets and ray-tested open courts, on every published LoD."""
import argparse,json,sys
from pathlib import Path
import numpy as np
p=argparse.ArgumentParser();p.add_argument('--package',type=Path,required=True);p.add_argument('--recipe',type=Path,required=True);args=p.parse_args()
repo=args.recipe.resolve().parents[4];sys.path[:0]=[str(repo/'tools'),str(args.recipe.parent/'scripts')]
from publication import inspect_glb
from audit_published_coplanar import primitives
from shapes import transform
layout=json.loads((args.recipe.parent/'research/layout.json').read_text());assembly=json.loads((args.package/'assembly.json').read_text());rows=[]
for level in ['detail','walk','district']:
 files=[args.package/f['path']for f in assembly['files']if f['level']==level]
 infos=[inspect_glb(f)for f in files];triangles=sum(r['triangles']for r in infos);download=sum(r['bytes']for r in infos);gpu=sum(r['gpuBytesEstimate']for r in infos)
 assert triangles<=({'detail':40000,'walk':35000,'district':1750}[level]),(level,triangles)
 if level=='district':assert download<=2400000 and gpu<=5800000,(download,gpu)
 exported=[(t,owner) for f in files for t,owner in primitives(f,{'rotationY':0,'position':[0,0,0]})]
 if level in ('detail','walk'):
  lettering=[t for t,owner in exported if owner['node']=='Architecture Burlington inscription']
  assert len(lettering)==1 and len(lettering[0])>100,(level,'missing Burlington inscription')
 ts=np.concatenate([t for t,_ in exported]);assert np.isfinite(ts).all()
 # Export axes are x,up,-y. Test projected triangle containment at four court centres.
 court_hits=[]
 for x,y in [(10,18),(16.5,18),(16.5,25),(10,26)]:
  X,Y,Z=transform(layout,(x,y,.5));v=ts[:,:,[0,2]];q=np.array([X,-Y]);a=v[:,0];b=v[:,1];c=v[:,2]
  def cross(a,b):return a[:,0]*b[:,1]-a[:,1]*b[:,0]
  den=cross(b-a,c-a);good=np.abs(den)>1e-9;u=np.zeros(len(ts));v0=u.copy();u[good]=cross(np.broadcast_to(q,a.shape)-a,c-a)[good]/den[good];v0[good]=cross(b-a,np.broadcast_to(q,a.shape)-a)[good]/den[good]
  height=ts[:,0,1]+u*(ts[:,1,1]-ts[:,0,1])+v0*(ts[:,2,1]-ts[:,0,1]);hit=good&(u>=0)&(v0>=0)&(u+v0<=1)&(height>Z)
  assert not hit.any(),(level,'court obstructed',x,y)
  court_hits.append(0)
 rows.append({'level':level,'triangles':triangles,'bytes':download,'gpu_bytes':gpu,'open_courts':len(court_hits)})
(args.package/'burlington-export-check.json').write_text(json.dumps(rows,indent=2)+'\n');print(rows)
