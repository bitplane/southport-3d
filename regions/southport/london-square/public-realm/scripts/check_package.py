"""Check measured road planes and unchanged ground across exported LoDs."""
import argparse
import json
from pathlib import Path
import sys
import numpy as np

p=argparse.ArgumentParser()
p.add_argument('--package',type=Path,required=True)
p.add_argument('--recipe',type=Path,required=True)
args=p.parse_args()
repo=args.recipe.resolve().parents[4]
sys.path[:0]=[str(repo/'tools'),str(repo/'lib')]
from audit_published_coplanar import primitives
from southport3d.elevation import Elevations
surface=Elevations(repo/'regions/southport/elevation/london-square.json').surface('london-square-pavement')
config=json.loads(args.recipe.read_text())
ground={part['id']for part in config['parts']if part.get('ground')}
manifest=json.loads((args.package/'manifest.json').read_text())
road_materials={'Authored asphalt','Authored reddish carriageway','Authored dark service road blocks','Faded yellow road marking','Worn white road marking'}
baseline={};results=[]
for level in ['detail','walk','district']:
    count=0;worst=0.;total=0
    for item in manifest['files']:
        if item['level']!=level:continue
        total+=item['triangles']
        if item['part']not in ground:continue
        chunks=[]
        for tri,source in primitives(args.package/item['path'],{'rotationY':0,'position':[0,0,0]}):
            xyz=tri[:,:,[0,2,1]]*np.array([1,-1,1]);chunks.append(xyz)
            if source['material']not in road_materials:continue
            normal=np.cross(xyz[:,1]-xyz[:,0],xyz[:,2]-xyz[:,0])
            use=abs(normal[:,2])>.7*np.linalg.norm(normal,axis=1)
            for x,y,z in xyz[use].mean(axis=1):
                error=abs(z-(surface.height(x,y)-.12))
                assert error<1e-4,(level,source,x,y,z,error)
                count+=1;worst=max(worst,error)
        values=np.concatenate(chunks)
        if level=='detail':baseline[item['part']]=values
        else:assert np.array_equal(values,baseline[item['part']]),(level,item['part'],'ground changes at LoD transition')
    assert count>1000,(level,'road probes missing')
    results.append({'level':level,'triangles':total,'road_triangle_probes':count,'maximum_height_error_m':worst})
(args.package/'terrain-check.json').write_text(json.dumps(results,indent=2)+'\n')
print(results)
