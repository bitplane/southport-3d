"""Exported envelope budgets and ray-tested open courts, on every published LoD."""
import argparse,json,sys
from pathlib import Path
import numpy as np
p=argparse.ArgumentParser();p.add_argument('--package',type=Path,required=True);p.add_argument('--recipe',type=Path,required=True);args=p.parse_args()
repo=args.recipe.resolve().parents[4];sys.path[:0]=[str(repo/'tools'),str(args.recipe.parent/'scripts')]
from publication import inspect_glb
from audit_published_coplanar import primitives
from shapes import transform,bank_roof_height
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
 local_ids=[i for t,owner in exported for i in range(len(t))]
 residual=overlaps(ts,list(range(len(ts))))
 def tower_front_triangle(triangle):
  # Export coordinates are x, up, -y. Reconstruct the sheared local frame:
  # the permitted slivers must lie within the physical tower-front plane.
  X=triangle[:,0]-layout['front_origin'][0];Y=-triangle[:,2]-layout['front_origin'][1]
  y=(Y-layout['front_shear']*X)/(1-layout['front_shear']*layout['side_shear']);x=X-layout['side_shear']*y;z=triangle[:,1]-layout['floor_z']
  return (np.abs(y)<2e-4).all() and (x>=-2e-4).all() and (x<=layout['tower']['width']+2e-4).all() and (z>=8.65-2e-4).all() and (z<=layout['tower']['eaves']+2e-4).all()
 def intersection_polygon(a,b):
  def cross(u,v):return u[0]*v[1]-u[1]*v[0]
  out=[p for p in a]
  if cross(b[1]-b[0],b[2]-b[0])<0:b=b[::-1]
  for p,q in zip(b,np.roll(b,-1,axis=0)):
   old=out;out=[]
   for s,t in zip(old,old[1:]+old[:1]):
    ds=cross(q-p,s-p);dt=cross(q-p,t-p)
    if ds>=-1e-10:out.append(s)
    if (ds>0 and dt<0)or(ds<0 and dt>0):out.append(s+(t-s)*ds/(ds-dt))
  return np.asarray(out)
 # Exact clipped fan edges created when the circular aperture splits the
 # independent District front. Bounds are local x / height above floor.
 # Reordered or genuinely changed faces must be investigated, not exempted.
 known_front_fans={(52,54):((.05286,10.00000),(.89222,10.83936)),
                   (56,59):((1.56623,10.80172),(1.67697,11.50081)),
                   (60,250):((1.43925,10.00000),(1.55964,10.76001))}
 front_slivers=[]
 for ai,bi,area in residual:
  a,b=names[ai],names[bi]
  shell_trim=(a.startswith('Shell')and b.startswith('Trim'))or(b.startswith('Shell')and a.startswith('Trim'))
  slate=a.startswith('Roof')and b.startswith('Roof')and'Grey slate'in a and'Grey slate'in b
  envelope=a==b=='District roof'
  pair=tuple(sorted((local_ids[ai],local_ids[bi])));front_edge=False
  if level=='district' and a==b=='District front' and pair in known_front_fans and tower_front_triangle(ts[ai]) and tower_front_triangle(ts[bi]):
   poly=intersection_polygon(ts[ai][:,[0,1]],ts[bi][:,[0,1]])
   if len(poly)>=3:
    bounds=np.array([poly.min(axis=0),poly.max(axis=0)])-np.array([layout['front_origin'][0],layout['floor_z']]);length=max(np.linalg.norm(p-q)for p in poly for q in poly);width=2*area/length if length else float('inf')
    front_edge=area<4e-6 and width<9e-6 and np.all(np.abs(bounds-np.asarray(known_front_fans[pair]))<.002)
    if front_edge:front_slivers.append({'triangles':pair,'area_m2':area,'maximum_width_m':width,'local_x_height_bounds_m':bounds.tolist()})
  assert ((shell_trim or slate or envelope)and area<1e-5) or front_edge,(level,a,b,area,ai,bi)
 assert len(front_slivers)<=3 and sum(v['area_m2']for v in front_slivers)<7e-6,(level,'tower front fan residual',front_slivers)

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
 def probe(name,start,end,expected,tolerance=.035):
  def gl(p):
   X,Y,Z=transform(layout,p);return np.array([X,Z,-Y])
  a,b,want=[gl(p)for p in (start,end,expected)];actual=first_hit(a,b-a);assert abs(actual-np.linalg.norm(want-a))<tolerance,(level,name,actual,np.linalg.norm(want-a))
 t=layout['tower'];cx=t['width']/2
 probe('tower crown',(1.65,1.65,20),(1.65,1.65,8),(1.65,1.65,t['top']+t['crown_rise']))
 probe('wall above oriel',(cx,-2,10.20),(cx,1,10.20),(cx,0,10.20))
 probe('oculus glass',(cx+.11,-2,t['oculus_z']+.09),(cx+.11,1,t['oculus_z']+.09),(cx+.11,.205,t['oculus_z']+.09))
 probe('pediment',(cx,-2,13.0),(cx,1,13.0),(cx,-t['pediment_depth'],13.0))
 probe('return parapet',(5,2,12.6),(3,2,12.6),(t['width']+t['return_thickness'],2,12.6))
 probe('exposed party wedge',(-.4,.08,12.02),(.4,.08,12.02),(0,.08,12.02))
 def gl_local(p):
  X,Y,Z=transform(layout,p);return np.array([X,Z,-Y])
 a,b=[gl_local(p)for p in [(-.4,.5,11.95),(.4,.5,11.95)]]
 assert first_hit(a,b-a)>np.linalg.norm(b-a)-.02,(level,'bank duplicates the neighbouring party skin')
 probe('projecting return coping',(5,2,12.86),(3,2,12.86),(t['width']+t['return_thickness']+t['return_coping_projection'],2,12.86))
 z=t['top']+t['crown_rise']+.27;y=t['depth']/2
 probe('crest rail',(cx+.4,y,z),(cx-.4,y,z),(cx+.023,y,z))
 for y in (.8,2.5):probe('mansard '+str(y),(8.2,y,20),(8.2,y,8),(8.2,y,bank_roof_height(layout,y)))
 y=.8;z=(bank_roof_height(layout,y)+layout['front_eaves']+(layout['front_ridge']-layout['front_eaves'])*y/layout['ridge_y'])/2;w=layout['front_width']
 probe('end wall at pitch break',(w+.5,y,z),(w-.5,y,z),(w,y,z))
 v=layout['front_rooflights'][0];x,y=v['x'],(v['y0']+v['y1'])/2
 probe('rooflight glass',(x,y,20),(x,y,8),(x,y,bank_roof_height(layout,y)-.045))
 v=layout['front_roof_stacks'][0];x,y=v['x'],(v['y0']+v['y1'])/2
 probe('roof stack',(x,y,20),(x,y,8),(x,y,v['top']))
 # Export axes are x,up,-y. Test projected triangle containment at four court centres.
 court_hits=[]
 for x,y in layout['courts']:
  X,Y,Z=transform(layout,(x,y,4));v=ts[:,:,[0,2]];q=np.array([X,-Y]);a=v[:,0];b=v[:,1];c=v[:,2]
  def cross(a,b):return a[:,0]*b[:,1]-a[:,1]*b[:,0]
  den=cross(b-a,c-a);good=np.abs(den)>1e-9;u=np.zeros(len(ts));v0=u.copy();u[good]=cross(np.broadcast_to(q,a.shape)-a,c-a)[good]/den[good];v0[good]=cross(b-a,np.broadcast_to(q,a.shape)-a)[good]/den[good]
  height=ts[:,0,1]+u*(ts[:,1,1]-ts[:,0,1])+v0*(ts[:,2,1]-ts[:,0,1]);hit=good&(u>=0)&(v0>=0)&(u+v0<=1)&(height>Z)
  assert not hit.any(),(level,'court obstructed',x,y)
  court_hits.append(0)
 rows.append({'level':level,'triangles':triangles,'bytes':download,'gpu_bytes':gpu,'open_courts':len(court_hits),'numeric_edge_residuals':len(residual),'district_front_slivers':front_slivers})
(args.package/'building-export-check.json').write_text(json.dumps(rows,indent=2)+'\n');print(rows)
