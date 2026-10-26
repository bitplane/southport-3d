"""Audit actual exported garden sections and pavilion contacts at all LoDs.

Run after both package-only builds. This is a same-facing coplanar audit, not
an accessibility, ground-following or general intersection test.
"""
import argparse,sys,json
from pathlib import Path
import numpy as np
ROOT=Path(__file__).resolve().parents[5];sys.path.insert(0,str(ROOT/'tools'))
from audit_published_coplanar import primitives
from coplanar import overlaps
p=argparse.ArgumentParser();p.add_argument('--ground',type=Path,default=ROOT/'build/southport.lord-street.corridor-public-realm/package');p.add_argument('--pavilions',type=Path,default=ROOT/'build/southport.lord-street.town-hall-gardens-pavilions/package');args=p.parse_args()
for level in ('detail','walk','district'):
 arrays=[];labels=[]
 for part in ('section-05','section-06','section-07'):
  for tri,source in primitives(args.ground/(part+'-'+level+'.glb'),{'rotationY':0,'position':[0,0,0]}):
   # Limit the wide corridor to the snag's site bounds.
   keep=(tri[:,:,0].max(axis=1)>-245)&(tri[:,:,0].min(axis=1)<-136)&(tri[:,:,2].max(axis=1)>-25)&(tri[:,:,2].min(axis=1)<25)
   t=tri[keep];arrays.append(t);labels.extend([part]*len(t))
 for part in ('north','south'):
  for tri,source in primitives(args.pavilions/(part+'-'+level+'.glb'),{'rotationY':0,'position':[0,0,0]}):arrays.append(tri);labels.extend([part]*len(tri))
 for asset in ('southport.lord-street.town-hall','southport.lord-street.christ-church-approach','southport.eastbank-street.public-realm'):
  package=ROOT/'build'/asset/'package';manifest=json.loads((package/'manifest.json').read_text())
  for f in manifest['files']:
   if f['level']!=level:continue
   for tri,source in primitives(package/f['path'],{'rotationY':0,'position':[0,0,0]}):
    keep=(tri[:,:,0].max(axis=1)>-245)&(tri[:,:,0].min(axis=1)<-136)&(tri[:,:,2].max(axis=1)>-25)&(tri[:,:,2].min(axis=1)<25)
    t=tri[keep];arrays.append(t);labels.extend([asset]*len(t))
 tris=np.concatenate(arrays);errors=[e for e in overlaps(tris,labels) if e[0]!=e[1]]
 assert not errors,(level,errors[:20])
 print(level,len(tris),'triangles, no cross-part coplanar overlaps')
