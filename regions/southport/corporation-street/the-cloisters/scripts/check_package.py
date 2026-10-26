"""All exported LoDs: coplanar ownership, budget and school/retail access clearance."""
import argparse,json,sys
from pathlib import Path
import numpy as np
p=argparse.ArgumentParser();p.add_argument('--package',type=Path,required=True);p.add_argument('--recipe',type=Path,required=True);a=p.parse_args()
repo=a.recipe.resolve().parents[4];sys.path.insert(0,str(repo/'tools'))
from audit_published_coplanar import primitives
from coplanar import overlaps
assembly=json.loads((a.package/'assembly.json').read_text());report=[]
for level in ('detail','walk','district'):
 ts=[];names=[]
 for f in assembly['files']:
  if f['level']!=level:continue
  for tri,owner in primitives(a.package/f['path'],{'rotationY':0,'position':[0,0,0]}):
   ts.extend(tri);names.extend([f['part']+':'+owner['node']]*len(tri))
 ts=np.asarray(ts);hits=overlaps(ts,names)
 assert not [h for h in hits if h[2]>5e-6],(level,hits[:20])
 assert len(ts)<=({'detail':50000,'walk':35000,'district':500}[level]),(level,len(ts))
 # No school roof/facade occupies the observed separation from Boots and rear services.
 for x,y in [(-114,-91),(-104.7,-80)]:
  v=ts[:,:,[0,2]];q=np.array([x,-y]);b=v[:,1]-v[:,0];c=v[:,2]-v[:,0];d=q-v[:,0]
  cross=lambda f,g:f[:,0]*g[:,1]-f[:,1]*g[:,0]
  den=cross(b,c);good=np.abs(den)>1e-8;u=np.zeros(len(ts));vv=u.copy();u[good]=cross(d,c)[good]/den[good];vv[good]=cross(b,d)[good]/den[good]
  assert not np.any(good&(u>=0)&(vv>=0)&(u+vv<=1)),(level,'access gap occupied',x,y)
 report.append({'level':level,'triangles':len(ts),'coplanar_candidates':hits,'access_samples_clear':2})
(a.package/'cloisters-export-check.json').write_text(json.dumps(report,indent=2)+'\n');print(report)
