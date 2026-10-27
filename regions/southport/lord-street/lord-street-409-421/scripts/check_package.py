"""Exported envelope budgets and ray-tested open courts, on every published LoD."""
import argparse,json,sys
from pathlib import Path
import numpy as np
p=argparse.ArgumentParser();p.add_argument('--package',type=Path,required=True);p.add_argument('--recipe',type=Path,required=True);args=p.parse_args()
repo=args.recipe.resolve().parents[4];sys.path[:0]=[str(repo/'tools'),str(args.recipe.parent/'scripts')]
from publication import inspect_glb
from audit_published_coplanar import primitives
from shapes import transform,facade_x,roof_probes
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
  X,Y,Z=transform(layout,(facade_x(layout,cx),-2,6.1))
  distance=first_hit((X,Z,-Y),(layout['side_shear'],0,-1))
  assert 1.1<distance<1.5,(level,'box bay lost projection',distance)
 X,Y,Z=transform(layout,(layout['cafe']['width']/2,-2,6.1))
 assert 1.2<first_hit((X,Z,-Y),(layout['side_shear'],0,-1))<1.6,(level,'missing cafe bay')
 hip=layout['rear_ranges']['hip'];op=hip['opening'];X,Y,Z=transform(layout,(hip['x1']+2,op['y0']+.4,(op['z0']+op['z1'])/2))
 assert 2.15<first_hit((X,Z,-Y),(-1,0,layout['front_shear']))<2.25,(level,'hip band lost recess')
 # Export axes are x,up,-y. Test projected triangle containment at four court centres.
 court_hits=[]
 for x,y in layout['courts']:
  X,Y,Z=transform(layout,(x,y,4));v=ts[:,:,[0,2]];q=np.array([X,-Y]);a=v[:,0];b=v[:,1];c=v[:,2]
  def cross(a,b):return a[:,0]*b[:,1]-a[:,1]*b[:,0]
  den=cross(b-a,c-a);good=np.abs(den)>1e-9;u=np.zeros(len(ts));v0=u.copy();u[good]=cross(np.broadcast_to(q,a.shape)-a,c-a)[good]/den[good];v0[good]=cross(b-a,np.broadcast_to(q,a.shape)-a)[good]/den[good]
  height=ts[:,0,1]+u*(ts[:,1,1]-ts[:,0,1])+v0*(ts[:,2,1]-ts[:,0,1]);hit=good&(u>=0)&(v0>=0)&(u+v0<=1)&(height>Z)
  assert not hit.any(),(level,'court obstructed',x,y)
  court_hits.append(0)
 # Test exported roof receivers and both valleys at every level. Bars and
 # chimney furniture are excluded from these vertical silhouette probes.
 roof_file=next(args.package/f['path']for f in assembly['files']if f['level']==level and f['part']=='roof')
 roof_prim=primitives(roof_file,{'rotationY':0,'position':[0,0,0]})
 roof_ts=np.concatenate([t for t,o in roof_prim if level=='district' or o['node'] in ('Roof roof Grey slate','Roof roof Muted rooflight glazing')])
 for name,x,y,bounds in roof_probes():
  X,Y,_=transform(layout,(x,y,0));q=np.array([X,-Y]);v=roof_ts[:,:,[0,2]];a,b,c=v[:,0],v[:,1],v[:,2]
  def cross2(u,v):return u[:,0]*v[:,1]-u[:,1]*v[:,0]
  den=cross2(b-a,c-a);good=np.abs(den)>1e-9;u=np.zeros(len(a));v0=u.copy()
  u[good]=cross2(np.broadcast_to(q,a.shape)-a,c-a)[good]/den[good];v0[good]=cross2(b-a,np.broadcast_to(q,a.shape)-a)[good]/den[good]
  mask=good&(u>=-1e-7)&(v0>=-1e-7)&(u+v0<=1+1e-7)
  height=roof_ts[:,0,1]+u*(roof_ts[:,1,1]-roof_ts[:,0,1])+v0*(roof_ts[:,2,1]-roof_ts[:,0,1])-layout['floor_z']
  unique=[]
  for z in height[mask]:
   if not any(abs(z-v)<1e-4 for v in unique):unique.append(z)
  if bounds is None:assert not unique,(level,name,unique)
  else:assert len(unique)==1 and bounds[0]<unique[0]<bounds[1],(level,name,unique)
 rows.append({'level':level,'triangles':triangles,'bytes':download,'gpu_bytes':gpu,'open_courts':len(court_hits),'roof_probes':len(roof_probes()),'numeric_edge_residuals':len(residual)})
(args.package/'building-export-check.json').write_text(json.dumps(rows,indent=2)+'\n');print(rows)
