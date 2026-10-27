"""Probe exported approach paving and the measured facade-ground perimeter."""
import math,os,sys
from pathlib import Path
import numpy as np
R=Path(__file__).resolve().parents[1];repo=Path(os.environ['SOUTHPORT_REPO_ROOT']);sys.path.insert(0,str(repo/'tools'))
from audit_published_coplanar import primitives
p=R/'models/public-realm.glb';fake={'rotationY':0,'position':[0,0,0]};records=[]
for triangles,meta in primitives(p,fake):
 if meta['node'].startswith('Ground ') and meta['material'] in ('Southlake paving','Southlake courts','Southlake green','Southlake sand','Southlake asphalt'):
  t=triangles[:,:,[0,2,1]]*np.array([1,-1,1]);lo=t[:,:,:2].min(axis=1);hi=t[:,:,:2].max(axis=1)
  near=(hi[:,0]>-325)&(lo[:,0]<-290)&(hi[:,1]>510)&(lo[:,1]<550)
  if near.any():records.append((t[near],meta))
ox,oy=-306.95,529.7;u=(.989273,.146078);v=(.146078,-.989273)
def probe(x,y):
 pt=np.array([ox+u[0]*x+v[0]*y,oy+u[1]*x+v[1]*y]);owners=[]
 for tris,meta in records:
  a=tris[:,0,:2];ab=tris[:,1,:2]-a;ac=tris[:,2,:2]-a;d=pt-a;det=ab[:,0]*ac[:,1]-ab[:,1]*ac[:,0];valid=abs(det)>1e-10
  U=np.divide(d[:,0]*ac[:,1]-d[:,1]*ac[:,0],det,out=np.zeros_like(det),where=valid);V=np.divide(ab[:,0]*d[:,1]-ab[:,1]*d[:,0],det,out=np.zeros_like(det),where=valid)
  hit=valid&(U>1e-7)&(V>1e-7)&(U+V<1-1e-7)
  for t0,aa,bb in zip(tris[hit],U[hit],V[hit]):owners.append((meta['node'],meta['material'],float(t0[0,2]+aa*(t0[1,2]-t0[0,2])+bb*(t0[2,2]-t0[0,2]))))
 assert len(owners)==1,(x,y,owners)
 return owners[0]
heights=[]
for x in [-2.53,-1.57,1.57,2.53]:
 for y in [6.38,6.83,8.19,10.27,12.73]:
  owner=probe(x,y);assert owner[1]=='Southlake paving',(x,y,owner);heights.append(owner[2])
assert max(heights)-min(heights)<.15,heights
# Sample just outside the real wall and drum, not the old roof projection. A
# missing hit here was a visible background strip at the eastern facade.
perimeter=[(x,6.57) for x in [-10.13,-8.11,-5.17,5.13,8.07,11.13]]
perimeter += [(x,y) for x in [-10.94,11.60] for y in [-5.71,-2.31,2.21,5.71]]
perimeter += [(4.15*math.cos(a),-9.5+4.15*math.sin(a)) for a in np.linspace(3.25,6.10,8)]
for x,y in perimeter:probe(x,y)
print('Heritage Centre: 20 sole-paving approach probes and',len(perimeter),'sole-owner perimeter probes; approach height spread',max(heights)-min(heights),'m')
