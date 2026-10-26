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

 # Physical regression: the tower crown and box bays must survive all LoDs.
 def first_hit(origin, direction):
  direction=np.asarray(direction,dtype=float);direction/=np.linalg.norm(direction)
  e1=ts[:,1]-ts[:,0];e2=ts[:,2]-ts[:,0];h=np.cross(np.broadcast_to(direction,e2.shape),e2)
  det=np.einsum('ij,ij->i',e1,h);ok=np.abs(det)>1e-9;inv=np.zeros_like(det);inv[ok]=1/det[ok]
  delta=np.asarray(origin)-ts[:,0];u=inv*np.einsum('ij,ij->i',delta,h);q=np.cross(delta,e1)
  v=inv*np.einsum('j,ij->i',direction,q);t=inv*np.einsum('ij,ij->i',e2,q)
  hits=t[ok&(u>=-1e-6)&(v>=-1e-6)&(u+v<=1+1e-6)&(t>1e-6)]
  assert len(hits),'missing architectural surface'
  return float(hits.min())
 for cx in layout['bay_centres'][1:3]:
  X,Y,Z=transform(layout,(cx,-2,6.1))
  distance=first_hit((X,Z,-Y),(layout['side_shear'],0,-1))
  assert 1.1<distance<1.5,(level,'box bay lost projection',distance)
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
