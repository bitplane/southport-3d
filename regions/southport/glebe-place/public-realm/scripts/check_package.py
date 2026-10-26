"""Check measured ground and LoD equality in the actual exported files."""
import argparse,json,os,sys
from pathlib import Path
import numpy as np
REPO=Path(sys.argv[sys.argv.index('--recipe')+1]).resolve().parents[4]
sys.path[:0]=[str(REPO/'tools'),str(REPO/'lib')]
from audit_published_coplanar import primitives
from southport3d.elevation import Elevations
p=argparse.ArgumentParser();p.add_argument('--package',type=Path,required=True);p.add_argument('--recipe');args=p.parse_args()
e=Elevations(REPO/'regions/southport/elevation/glebe.json');road=e.surface('glebe-road');mouth=e.surface('glebe-mouth')
manifest=json.loads((args.package/'manifest.json').read_text());baseline={};results=[]
for level in ['detail','walk','district']:
 count=0;worst=0.
 for item in manifest['files']:
  if item['level']!=level or item['part']not in ['lane-ground','court-ground']:continue
  chunks=[]
  for tri,source in primitives(args.package/item['path'],{'rotationY':0,'position':[0,0,0]}):
   xyz=tri[:,:,[0,2,1]]*np.array([1,-1,1]);chunks.append(xyz)
   normal=np.cross(xyz[:,1]-xyz[:,0],xyz[:,2]-xyz[:,0]);use=abs(normal[:,2])>.7*np.linalg.norm(normal,axis=1)
   material=source['material']
   for x,y,z in xyz[use].mean(axis=1):
    if material in ['Pale London Street approach','Weathered kerb','Buff tactile pads']:expected=road.height(x,y)+.12
    elif material in ['Faded yellow edge paint','Dark raised mouth setts'] or (material in ['Asphalt repairs','Iron drainage covers']and x>-10.6):expected=mouth.height(x,y)
    else:expected=road.height(x,y)
    error=abs(z-expected);assert error<1e-4,(level,source,x,y,z,expected)
    count+=1;worst=max(worst,error)
  values=np.concatenate(chunks)
  if level=='detail':baseline[item['part']]=values
  else:assert np.array_equal(values,baseline[item['part']]),(level,item['part'],'ground changes at LoD transition')
 results.append({'level':level,'ground_triangle_probes':count,'maximum_height_error_m':worst})
(args.package/'terrain-check.json').write_text(json.dumps(results,indent=2)+'\n');print(results)
