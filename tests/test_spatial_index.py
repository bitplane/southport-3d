import copy
import math
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools'))
from spatial_index import make_index, world_bounds


def catalog():
    part={'id':'wall','bounds':[[-1,0,-1],[1,5,1]],'levels':{'detail':{'uri':'one.glb','sha256':'one','bounds':[[-1,0,-1],[1,5,1]]},'district':{'uri':'two.glb','sha256':'two','bounds':[[-2,0,-2],[2,6,2]]}}}
    asset={'id':'building','position':[0,0,0],'rotationY':0,'parts':[part]}
    return dict(assets=[asset],worldOrigin=[53,-3],coordinateSystem='East, up, south (metres)',lodPolicy={},viewerVersion='v',revision='r')


def test_straddlers_union_and_rotation():
    c=catalog();scene,resources=make_index(c)
    assert scene['cells'][0]['size']==64  # crosses both origin lines; still fine
    assert scene['cells'][0]['bounds']==[[-2,0,-2],[2,6,2]]
    assert world_bounds([[0,0,0],[2,3,4]],[10,1,20],math.pi/2)==[[10.0,1,18.0],[14.0,4,20.0]]
    import json
    nodes=[json.loads(v) for v in resources.values()]
    assert sum(len(a['parts']) for n in nodes for a in n['assets'])==1


def test_large_ground_and_deterministic_local_updates():
    c=catalog();other=copy.deepcopy(c['assets'][0]);other['id']='ground';other['position']=[2000,0,2000]
    for r in other['parts'][0]['levels'].values():r['bounds']=[[0,0,0],[200,1,200]]
    c['assets'].append(other)
    scene,files=make_index(c)
    assert sorted(x['size'] for x in scene['cells'])==[64,256]
    assert make_index(c)==(scene,files)
    c['assets'].reverse();assert make_index(c)[1]==files
    c['assets'][0]['parts'][0]['levels']['detail']['uri']='changed.glb'
    changed,resources=make_index(c)
    assert len(set(files)&set(resources))==1
    c['assets'].pop(0)
    assert len(make_index(c)[0]['cells'])==1
