"""Scan all pier sections together, including their cross-asset seams."""
import json,math,subprocess,sys
from pathlib import Path
import numpy as np
REPO=Path(__file__).resolve().parents[4];sys.path.insert(0,str(REPO/'tools'))
from publication import east_north_offset
from audit_published_coplanar import primitives
world=json.loads((REPO/'viewer/world.json').read_text())['origin_wgs84_lat_lon']
out=REPO/'build/pier-assembly-audit';out.mkdir(exist_ok=True);report=[]
for level in ['detail','walk','district']:
 tris=[]
 for i in range(1,13):
  a=json.loads((REPO/f'regions/southport/pier/section-{i:02}/asset.json').read_text())
  e,n=east_north_offset(world,a['origin_wgs84_lat_lon'])
  transform={'rotationY':math.radians(a['site_rotation_from_east_degrees']),'position':[e,0,-n]}
  p=REPO/f'build/southport.pier.section-{i:02}/package'
  for row in json.loads((p/'assembly.json').read_text())['files']:
   if row['level']==level:tris.extend(t for t,_ in primitives(p/row['path'],transform))
 t=np.concatenate(tris);t.astype('<f8').tofile(out/f'{level}.bin')
 subprocess.run([str(REPO/'build/southport.pier.section-01/package/pier-coplanar-scan'),str(out/f'{level}.bin'),str(out/f'{level}-hits.bin')],check=True)
 hits=np.fromfile(out/f'{level}-hits.bin',dtype=[('a','<u4'),('b','<u4'),('area','<f8')])
 row={'level':level,'triangles':len(t),'coplanar_pairs':len(hits)};print(row,flush=True);report.append(row)
 assert not len(hits),hits[:5]
(out/'report.json').write_text(json.dumps(report,indent=2)+'\n')
