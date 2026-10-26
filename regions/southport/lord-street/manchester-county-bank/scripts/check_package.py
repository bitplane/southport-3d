"""Exported envelope budgets and ray-tested open courts, on every published LoD."""
import argparse,json,sys
from pathlib import Path
import numpy as np
p=argparse.ArgumentParser();p.add_argument('--package',type=Path,required=True);p.add_argument('--recipe',type=Path,required=True);args=p.parse_args()
repo=args.recipe.resolve().parents[4];sys.path[:0]=[str(repo/'tools'),str(args.recipe.parent/'scripts')]
from publication import inspect_glb
from audit_published_coplanar import primitives
from shapes import transform
from coplanar import overlaps
layout=json.loads((args.recipe.parent/'research/layout.json').read_text());assembly=json.loads((args.package/'assembly.json').read_text());rows=[]
for level in ['detail','walk','district']:
 files=[args.package/f['path']for f in assembly['files']if f['level']==level]
 infos=[inspect_glb(f)for f in files];triangles=sum(r['triangles']for r in infos);download=sum(r['bytes']for r in infos);gpu=sum(r['gpuBytesEstimate']for r in infos)
 assert triangles<=({'detail':80000,'walk':70000,'district':2000}[level]),(level,triangles)
 if level=='district':assert download<=2400000 and gpu<=5800000,(download,gpu)
 exported=[(t,owner) for f in files for t,owner in primitives(f,{'rotationY':0,'position':[0,0,0]})]
 ts=np.concatenate([t for t,_ in exported]);assert np.isfinite(ts).all()
 names=[owner['node']for t,owner in exported for _ in t]
 residual=overlaps(ts,names)
 for a,b,area in residual:
  shell_trim=(a.startswith('Shell')and b.startswith('Trim'))or(b.startswith('Shell')and a.startswith('Trim'))
  slate=a.startswith('Roof')and b.startswith('Roof')and'Grey slate'in a and'Grey slate'in b
  envelope=a==b=='District roof'
  assert (shell_trim or slate or envelope)and area<1e-5,(level,a,b,area)

 # Export axes are x,up,-y. Test projected triangle containment at four court centres.
 court_hits=[]
 for x,y in layout['courts']:
  X,Y,Z=transform(layout,(x,y,4));v=ts[:,:,[0,2]];q=np.array([X,-Y]);a=v[:,0];b=v[:,1];c=v[:,2]
  def cross(a,b):return a[:,0]*b[:,1]-a[:,1]*b[:,0]
  den=cross(b-a,c-a);good=np.abs(den)>1e-9;u=np.zeros(len(ts));v0=u.copy();u[good]=cross(np.broadcast_to(q,a.shape)-a,c-a)[good]/den[good];v0[good]=cross(b-a,np.broadcast_to(q,a.shape)-a)[good]/den[good]
  height=ts[:,0,1]+u*(ts[:,1,1]-ts[:,0,1])+v0*(ts[:,2,1]-ts[:,0,1]);hit=good&(u>=0)&(v0>=0)&(u+v0<=1)&(height>Z)
  assert not hit.any(),(level,'court obstructed',x,y)
  court_hits.append(0)
 rows.append({'level':level,'triangles':triangles,'bytes':download,'gpu_bytes':gpu,'open_courts':len(court_hits),'numeric_edge_residuals':len(residual)})
(args.package/'building-export-check.json').write_text(json.dumps(rows,indent=2)+'\n');print(rows)
