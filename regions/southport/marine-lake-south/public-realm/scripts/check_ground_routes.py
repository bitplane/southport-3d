"""Exported route continuity regression for estimated road and access grades."""
import sys,json,math
from pathlib import Path
import numpy as np
import os
ROOT=Path(__file__).resolve().parents[1];R=Path(os.environ['SOUTHPORT_REPO_ROOT']);sys.path.insert(0,str(R/'tools'));from audit_published_coplanar import primitives
path=ROOT/'models/public-realm.glb';fake={'rotationY':0,'position':[0,0,0]};vals=[]
for tris,meta in primitives(path,fake):
 if meta['node'].startswith('Ground '):vals.append(tris[:,:,[0,2,1]]*np.array([1,-1,1]))
t=np.concatenate(vals);u=t[:,1,:2]-t[:,0,:2];v=t[:,2,:2]-t[:,0,:2];det=u[:,0]*v[:,1]-u[:,1]*v[:,0];valid=abs(det)>1e-8;t=t[valid];u=u[valid];v=v[valid];det=det[valid]
index={}
for i,tri in enumerate(t):
 lo=np.floor(tri[:,:2].min(0)/16).astype(int);hi=np.floor(tri[:,:2].max(0)/16).astype(int)
 for x in range(lo[0],hi[0]+1):
  for y in range(lo[1],hi[1]+1):index.setdefault((x,y),[]).append(i)
index={k:np.array(v)for k,v in index.items()}
def height(p):
 ids=index.get(tuple(math.floor(v/16)for v in p))
 if ids is None:return None
 q=np.array(p)-t[ids,0,:2];U=(q[:,0]*v[ids,1]-q[:,1]*v[ids,0])/det[ids];V=(u[ids,0]*q[:,1]-u[ids,1]*q[:,0])/det[ids];hit=(U>=-1e-7)&(V>=-1e-7)&(U+V<=1+1e-7)
 if not hit.any():return None
 return float(np.max(t[ids[hit],0,2]+U[hit]*(t[ids[hit],1,2]-t[ids[hit],0,2])+V[hit]*(t[ids[hit],2,2]-t[ids[hit],0,2])))
D=json.load(open(ROOT/'research/layout.json'));errors=[];samples=0
for road in D['roads']:
 previous=None
 for a,b in zip(road['points'],road['points'][1:]):
  n=max(1,math.ceil(math.dist(a,b)))
  for i in range(n):
   p=[a[k]+(b[k]-a[k])*i/n for k in [0,1]];h=height(p)
   if h is not None:samples+=1
   if h is not None and previous is not None:
    xy,zh=previous
    if abs(h-zh)>.45:errors.append({'road':road['id'],'name':road['name'],'xy':[xy,p],'heights':[zh,h],'step_m':abs(h-zh)})
   previous=(p,h)if h is not None else None
assert samples>8000,(samples,'too few supported road samples')
assert not errors,errors[:8]
(ROOT/'research/route-validation.json').write_text(json.dumps({'supported_samples':samples,'steps_over_045m':errors,'scope':'Exported master road centrelines at <=1m intervals; only consecutive supported samples are compared. Neighbour handovers and actual three-level publication are checked separately.'},indent=2)+'\n');print('Road continuity:',samples,'supported samples; no step above 0.45m')
