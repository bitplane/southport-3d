"""Check authored coverage, open entrances and semantic ground ownership."""
import json
import math
import os
import sys
from pathlib import Path
import bpy
ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(Path(os.environ['SOUTHPORT_REPO_ROOT'])/'lib'),str(ROOT/'scripts')]
from components import hedge,lantern
from southport3d.landscape import tree
bpy.ops.wm.open_mainfile(filepath=str(ROOT/'models/public-realm.blend'))
report=json.loads((ROOT/'research/geometry-report.json').read_text())
for place in ['christ','george']:
    ground=bpy.data.collections[place+'-ground']
    assert ground.objects
    assert all(o.name.startswith('Surface ') for o in ground.objects),'Furniture leaked into walking surface'
    for o in ground.objects:
        assert o.data.uv_layers and o.data.polygons
        assert all(math.isfinite(c) for v in o.data.vertices for c in v.co)
for factory in [hedge,lantern,tree]:
    counts=[sum(len(f)-2 for f in factory(level).faces) for level in ['detail','walk','district']]
    assert counts[0]>counts[1]>counts[2],(factory.__name__,counts)
# No wall blocks the mapped Christ Church cross-garden path.
for w in report['walls']:
    if w['place']=='christ':
        for a,b in zip(w['xy'],w['xy'][1:]):
            assert not (min(a[0],b[0])<-100.8<max(a[0],b[0]) and min(a[1],b[1])>10),'Wall blocks entrance'
positions=[(r['place'],r['kind'],*r['xy']) for r in report['placements']]
assert len(positions)==len(set(positions)), 'Duplicate furnishings'
assert all(image.packed_file for image in bpy.data.images if image.source=='FILE')
# Declared ownership station occurs in exported ground on both sides of the road.
for place,x in [('christ',-73),('george',154)]:
    verts=[v.co for o in bpy.data.collections[place+'-ground'].objects for v in o.data.vertices]
    for y in [21,31]:
        assert any(abs(v.x-x)<.001 and abs(v.y-y)<.001 for v in verts),(place,'missing seam vertex',y)
(ROOT/'research/validation.json').write_text(json.dumps({'checks':'Finite surfaces, ground separation, distinct placements, open cross-garden entrance, all LOD generators reduce, seam vertices, packed maps','placements':len(positions)},indent=2))
print('Church gardens geometry, entrances and LoDs validated')

# Backrest is local +Y: the northern garden rows must face +Y, not the lawn.
D=json.loads((ROOT/'research/layout.json').read_text())
for rows in D['benches'].values():
 for x,y,yaw in rows:
  assert yaw in ((180,90) if y>0 else (0,)),(x,y,yaw,'reversed garden bench')

# Road-facing retaining wall and low path edging must not be interchanged.
assert any(w['place']=='christ' and w['height']==.55 and w['xy'][0]==[-75.3,-13] and len(w['xy'])>10 for w in report['walls'])
assert not any(w['place']=='christ' and w['height']>.1 and len(w['xy'])>2 and all(y<0 for x,y in w['xy']) for w in report['walls'])
from mathutils import Vector
def ground_height(x,y):
    hits=[]
    for ob in bpy.data.collections['christ-ground'].objects:
        hit,p,n,i=ob.ray_cast(Vector((x,y,4)),Vector((0,0,-1)))
        if hit:hits.append((p.z,ob.name))
    assert len(hits)==1,(x,y,hits)
    return hits[0]
for x,y in [(-85,0),(-115,0)]:
    z,name=ground_height(x,y);assert 'grass' in name and abs(z-(-.0075-.022*y+.45))<.002
for x,y in [(-82,-24.5),(-91,-28.5),(-80,-20.4)]:
    z,name=ground_height(x,y);assert 'grass' not in name and abs(z-(-.0075-.022*y))<.002

# Raised grass must remain behind the west retaining wall, not protrude through
# its exposed outside face. Check exported surfaces at several wall stations.
for y in (-14,-8,0,8,15):
 z,name=ground_height(-127.92,y)
 assert 'grass' not in name,('Turf outside retaining wall',y,name)
 z,name=ground_height(-127.48,y)
 assert 'grass' in name,('Missing lawn behind retaining wall',y,name)
print('West retaining wall contains the raised lawn')
