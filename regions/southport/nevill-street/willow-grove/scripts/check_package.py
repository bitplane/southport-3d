"""Actual exported courtyard registration, open delivery lane and envelope cost."""
import argparse,json,sys
from pathlib import Path
import numpy as np
p=argparse.ArgumentParser();p.add_argument('--package',type=Path,required=True);p.add_argument('--recipe',type=Path,required=True);a=p.parse_args();repo=a.recipe.resolve().parents[4];sys.path.insert(0,str(repo/'tools'))
from audit_published_coplanar import primitives
from publication import inspect_glb
D=json.loads((a.recipe.parent/'research/layout.json').read_text());A=json.loads((a.package/'assembly.json').read_text());rows=[]
def xyz(p):
 x,y,z=p;return np.array([D['x']+x+D['shear_x']*y,D['base_z']+z,-D['y']-y-D['shear_y']*x])
def hits(ts,names,p,q,limit):
 origin=xyz(p);direction=xyz(tuple(p[i]+q[i]for i in range(3)))-origin;direction/=np.linalg.norm(direction);e1=ts[:,1]-ts[:,0];e2=ts[:,2]-ts[:,0];h=np.cross(direction,e2);det=np.sum(e1*h,axis=1);ok=np.abs(det)>1e-10;inv=np.divide(1,det,out=np.zeros_like(det),where=ok);v=origin-ts[:,0];u=np.sum(v*h,axis=1)*inv;c=np.cross(v,e1);w=np.sum(direction*c,axis=1)*inv;t=np.sum(e2*c,axis=1)*inv;use=np.flatnonzero(ok&(u>=-1e-7)&(w>=-1e-7)&(u+w<=1+1e-7)&(t>0)&(t<limit));return sorted([(float(t[i]),names[i])for i in use])
for level in ('detail','walk','district'):
 files=[a.package/f['path']for f in A['files']if f['level']==level];parts=[(t,n)for f in files for t,n in primitives(f,{'rotationY':0,'position':[0,0,0]})];ts=np.concatenate([t for t,n in parts]);names=[n['node']for t,n in parts for _ in t]
 for name,p,q,limit in [('backing window',(14.2,36.1,5.8),(0,-1,0),2),('side vent',(16,40.5,6),(1,0,0),2),('low shed',(14.4,37,8),(0,0,-1),6)]:
  h=hits(ts,names,p,q,limit);assert h,(level,name)
  if level!='district':assert not h[0][1].startswith(('Shell','Courtyard shells')),(level,name,h[0])
 for y in (39,44,49):assert not hits(ts,names,(14.5,y,1),(0,0,1),20),(level,'delivery yard filled',y)
 info=[inspect_glb(f)for f in files];row={'level':level,'triangles':sum(i['triangles']for i in info),'bytes':sum(i['bytes']for i in info),'gpu_bytes':sum(i['gpuBytesEstimate']for i in info),'yard_probes':6}
 if level=='district':assert row['triangles']<=1550 and row['bytes']<=2200000 and row['gpu_bytes']<=5000000,row
 rows.append(row)
(a.package/'courtyard-export-check.json').write_text(json.dumps(rows,indent=2)+'\n');print(rows)
