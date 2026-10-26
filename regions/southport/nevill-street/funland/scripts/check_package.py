"""Actual exports audit; no blanket exemptions for trim or roofs."""
import argparse,json,sys
from pathlib import Path
p=argparse.ArgumentParser();p.add_argument('--package',type=Path,required=True);p.add_argument('--recipe',type=Path,required=True);a=p.parse_args();sys.path.insert(0,str(a.recipe.resolve().parents[4]/'tools'))
from audit_published_coplanar import primitives
from coplanar import overlaps
results={}
for level in ['detail','walk','district']:
 tri=[];names=[]
 for part in ['architecture','carousel']:
  for t,m in primitives(a.package/f'{part}-{level}.glb',{'rotationY':0,'position':[0,0,0]}):
   for i,q in enumerate(t):tri.append(q);names.append(m['node']+':'+str(i))
 rows=overlaps(tri,names)
 assert not rows,rows
 results[level]={'triangles':len(tri),'coplanar_findings':rows}
(a.package/'surface-check.json').write_text(json.dumps(results,indent=2));print('Funland exported surfaces',json.dumps(results))
