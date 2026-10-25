"""Probe actual Detail/Walk/District yard geometry and fixed District budgets."""
import argparse,json,sys
from pathlib import Path
import numpy as np
p=argparse.ArgumentParser();p.add_argument('--package',type=Path,required=True);p.add_argument('--recipe',type=Path,required=True);a=p.parse_args()
repo=a.recipe.resolve().parents[4];sys.path[:0]=[str(repo/'tools'),str(a.recipe.parent/'scripts')]
from audit_published_coplanar import primitives
from publication import inspect_glb
from coplanar import overlaps
from plan import world
D=json.loads((a.recipe.parent/'research/layout.json').read_text());A=json.loads((a.package/'assembly.json').read_text());rows=[]
def xyz(p):
 x,y,z=world(D,p);return np.array([x,z,-y])
def hits(ts,p,q,limit):
 origin=xyz(p);direction=xyz(tuple(p[i]+q[i]for i in range(3)))-origin;direction/=np.linalg.norm(direction)
 e1=ts[:,1]-ts[:,0];e2=ts[:,2]-ts[:,0];h=np.cross(direction,e2);det=np.sum(e1*h,axis=1);ok=np.abs(det)>1e-10;inv=np.divide(1,det,out=np.zeros_like(det),where=ok);v=origin-ts[:,0];u=np.sum(v*h,axis=1)*inv;c=np.cross(v,e1);w=np.sum(direction*c,axis=1)*inv;t=np.sum(e2*c,axis=1)*inv
 use=ok&(u>=-1e-7)&(w>=-1e-7)&(u+w<=1+1e-7)&(t>0)&(t<limit);return t[use]
for level in ('detail','walk','district'):
 files=[a.package/f['path']for f in A['files']if f['level']==level];parts=[(t,n) for f in files for t,n in primitives(f,{'rotationY':0,'position':[0,0,0]})];ts=np.concatenate([t for t,n in parts]);assert np.isfinite(ts).all()
 if level!='district':
  sign=np.concatenate([t for t,n in parts if n['node']=='Architecture return lettering']);duct=np.concatenate([t for t,n in parts if n['node'].startswith('Architecture return duct') and 'bracket' not in n['node']]);gap=float(sign[:,:,1].min()-duct[:,:,1].max());assert gap>.25,(level,'duct/glyph clearance',gap)
  assert sign[:,:,1].max()-D['base_z']<4.13,(level,'lettering crosses upper course')
  labels=[n['node'] for t,n in parts for _ in t];residual=overlaps(ts,labels);assert not [r for r in residual if r[2]>5e-6],(level,residual)
 for name,p,q,limit,want in [('gate',(-1,12.1,2.08),(1,0,0),2,True),('wall',(-1,13.8,1.5),(1,0,0),2,True),('delivery lane',(-1,15.5,1.5),(1,0,0),3,False),('projection',(6,14,4),(0,-1,0),2,True),('roof',(6,12,10),(0,0,-1),5,True)]:assert bool(len(hits(ts,p,q,limit)))==want,(level,name)
 info=[inspect_glb(f)for f in files];row={'level':level,'triangles':sum(i['triangles']for i in info),'bytes':sum(i['bytes']for i in info),'gpu_bytes':sum(i['gpuBytesEstimate']for i in info),'yard_probes':5}
 if level=='district':assert row['triangles']<=1400 and row['bytes']<=2000000 and row['gpu_bytes']<=7000000,row
 rows.append(row)
(a.package/'yard-export-check.json').write_text(json.dumps(rows,indent=2)+'\n');print(rows)
