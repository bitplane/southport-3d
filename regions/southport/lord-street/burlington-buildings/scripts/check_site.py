"""Check named threshold/post controls against actual published paving at all LoDs.

Run after publishing Burlington and the affected grounds. Independent exported
triangle interpolation deliberately does not call the ground builder's formula.
"""
import sys,json,numpy as np
from pathlib import Path
R=Path(__file__).resolve().parents[5];sys.path[:0]=[str(R/'tools'),str(R/'lib'),str(R/'regions/southport/lord-street/burlington-buildings/scripts')]
from audit_published_coplanar import primitives
from shapes import transform
from southport3d.elevation import Elevations
D=json.load(open(R/'regions/southport/lord-street/burlington-buildings/research/layout.json'));C=json.load(open(R/'dist/catalog.json'));a=next(a for a in C['assets'] if a['id']=='southport.lord-street.corridor-public-realm')
# Inverse exported site frame keeps barycentric interpolation simple.
for level in ('detail','walk','district'):
 ts=np.concatenate([t for p in a['parts'] if p.get('ground') for t,_ in primitives(R/'dist'/p['levels'][level]['uri'],{'rotationY':0,'position':[0,0,0]})]);v=ts[:,:,[0,2]];a0=v[:,0];b=v[:,1];c=v[:,2]
 def cross(a,b):return a[:,0]*b[:,1]-a[:,1]*b[:,0]
 den=cross(b-a0,c-a0);valid=np.abs(den)>1e-9
 def height(X,Y):
  q=np.array([X,-Y]);u=np.zeros(len(ts));v0=u.copy();u[valid]=cross(np.broadcast_to(q,a0.shape)-a0,c-a0)[valid]/den[valid];v0[valid]=cross(b-a0,np.broadcast_to(q,a0.shape)-a0)[valid]/den[valid];hit=valid&(u>=-1e-7)&(v0>=-1e-7)&(u+v0<=1+1e-7)
  z=ts[:,0,1]+u*(ts[:,1,1]-ts[:,0,1])+v0*(ts[:,2,1]-ts[:,0,1]);return z[hit].tolist()
 rows=[]
 for name,y,xs in [('burlington-front-approach',-.015,[.16,1.22,4.64,5.89,9.33,10.58,22.037,23.287]),('burlington-canopy-support',-3.18,D['canopy']['post_x'])]:
  surf=Elevations(R/'regions/southport/elevation/lord-burlington.json').surface(name)
  for x in xs:
   X,Y,_=transform(D,(x,y,0));hs=height(X,Y);expected=surf.height(X,Y);delta=min([abs(h-expected)for h in hs],default=99);assert delta<.001,(level,name,x,delta);rows.append({'surface':name,'x':x,'height':hs,'expected':expected,'difference':delta})
 building=next(v for v in C['assets']if v['id']=='southport.lord-street.burlington-buildings')
 canopy=next(p for p in building['parts']if p['id']=='canopy')
 vs=np.concatenate([t.reshape(-1,3)for t,_ in primitives(R/'dist'/canopy['levels'][level]['uri'],{'rotationY':0,'position':[0,0,0]})])
 for x in D['canopy']['post_x']:
  X,Y,_=transform(D,(x,-3.18,0));near=np.linalg.norm(vs[:,[0,2]]-np.array([X,-Y]),axis=1)<.16
  foot=float(vs[near,1].min());hs=height(X,Y);assert min(abs(foot-h)for h in hs)<.001,(level,'post foot',x,foot,hs)
 if level!='district':
  front=next(p for p in building['parts']if p['id']=='front')
  piers=[t for t,node in primitives(R/'dist'/front['levels'][level]['uri'],{'rotationY':0,'position':[0,0,0]})if node['node'].startswith('Shop pier ')]
  assert len(piers)==5,len(piers)
  for t in piers:assert abs(float(t[:,:,1].min())-D['foundation_z'])<1e-5,'Shop pier misses foundation'
 print(level, '13 published ground probes and 5 actual post feet passed; max discrepancy',max(r['difference']for r in rows))
