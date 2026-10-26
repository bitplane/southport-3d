"""Audit actual three-level exports, retaining named numerical seam residues."""
import argparse,json,sys,os
from pathlib import Path
p=argparse.ArgumentParser();p.add_argument('--package',type=Path,required=True);p.add_argument('--recipe',type=Path,required=True);a=p.parse_args()
repo=a.recipe.resolve().parents[4]
sys.path.insert(0,str(repo/'tools'))
from audit_published_coplanar import primitives
from coplanar import overlaps
results={}
for level in ('detail','walk','district'):
 triangles=[];names=[]
 for t,m in primitives(a.package/f'architecture-{level}.glb',{'rotationY':0,'position':[0,0,0]}):
  for i,q in enumerate(t):triangles.append(q);names.append(m['node']+':'+str(i))
 rows=overlaps(triangles,names)
 # Float32 rotation leaves micron-scale area on touching roof/cap edges only.
 # No large/unspecified overlaps may hide under this numerical allowance.
 assert all(q[2]<5e-6 for q in rows),rows
 assert sum(q[2] for q in rows)<1e-5,rows
 if level!='district':assert all(q[0].startswith('Shell pier caps:') and q[1].startswith('Shell flat roof:') for q in rows),rows
 results[level]={'triangles':len(triangles),'numerical_edge_residues':rows,'maximum_permitted_total_m2':1e-5}
(a.package/'surface-check.json').write_text(json.dumps(results,indent=2))
print('Maritime three-level surface checks passed',json.dumps(results))
