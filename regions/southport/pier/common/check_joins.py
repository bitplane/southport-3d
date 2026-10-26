"""Check exported section boundaries in the publisher's world frame."""
import json,math,sys
from pathlib import Path
import numpy as np
REPO=Path(__file__).resolve().parents[4]
sys.path.insert(0,str(REPO/'tools'))
from publication import east_north_offset
from audit_published_coplanar import primitives
world=json.loads((REPO/'viewer/world.json').read_text())['origin_wgs84_lat_lon']
rows=[]
for i in range(1,13):
 d=REPO/f'regions/southport/pier/section-{i:02}'
 a=json.loads((d/'asset.json').read_text());cfg=json.loads((d/'research/section.json').read_text())
 e,n=east_north_offset(world,a['origin_wgs84_lat_lon']);yaw=math.radians(a['site_rotation_from_east_degrees'])
 levels={}
 for level in ['detail','walk','district']:
  f=REPO/f'build/southport.pier.section-{i:02}/package/deck-{level}.glb'
  v=np.concatenate([t.reshape(-1,3) for t,_ in primitives(f,{'rotationY':0,'position':[0,0,0]})])
  # The main deck spans the section length; extensions retain their own ownership.
  ends=[]
  for x in [0,cfg['stations'][1]-cfg['stations'][0]]:
   p=v[(np.abs(v[:,0]-x)<.0001)&(np.abs(v[:,1]-3.208)<.0001)]
   assert len(p), (i,level,x,'missing deck edge')
   station=cfg['stations'][0]+x
   centre=float(np.interp(station,[0,75,500,710,1044],[1,1,.6,2.5,2.5]))
   p=p[np.abs(p[:,2]+centre)<4.0]
   zs=[p[:,2].min(),p[:,2].max()]
   ends.append(np.array([[e+math.cos(yaw)*x+math.sin(yaw)*z,3.208,-n-math.sin(yaw)*x+math.cos(yaw)*z]for z in zs]))
  levels[level]=ends
 rows.append(levels)
report=[]
for i,(a,b) in enumerate(zip(rows,rows[1:]),1):
 for left in a:
  for right in b:
   error=float(np.linalg.norm(a[left][1]-b[right][0],axis=1).max())
   assert error<.001,(i,left,right,error)
   report.append({'join':i,'left':left,'right':right,'maximum_edge_gap_m':error})
out=REPO/'build/pier-joins.json';out.write_text(json.dumps(report,indent=2)+'\n');print(f'{len(report)} same/mixed LoD joins checked; maximum {max(r["maximum_edge_gap_m"]for r in report):.8f} m')
