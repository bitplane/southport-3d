"""Check ground ownership, traversable seam and furnishing classification."""
from pathlib import Path
import json
import math
import sys
import bpy
from mathutils import Vector
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
from datum import ROAD,MOUTH
bpy.ops.wm.open_mainfile(filepath=str(ROOT/'models/glebe-place.blend'))
meshes=[obj for obj in bpy.context.scene.objects if obj.type=='MESH']
assert all(obj.data.polygons and obj.data.uv_layers for obj in meshes)
assert all(math.isfinite(x) for obj in meshes for v in obj.data.vertices for x in v.co)
assert all(im.packed_file for im in bpy.data.images if im.source=='FILE')
ground=[obj for name in ['lane-ground','court-ground'] for obj in bpy.data.collections[name].objects]
assert max(v.co.x for obj in ground for v in obj.data.vertices)<=-4.3+1e-5
assert all(obj.name.startswith('Surface ') for obj in ground)
bpy.context.view_layer.update()
deps=bpy.context.evaluated_depsgraph_get()
# Near the seam the road must meet London Street's .6645m datum without a hole.
for y in [-68.5,-67,-65,-64.3]:
    hit,p,n,index,obj,matrix=bpy.context.scene.ray_cast(deps,Vector((-4.301,y,30)),Vector((0,0,-1)),distance=60)
    assert hit and obj in ground,(y,obj)
    assert abs(p.z-MOUTH.height(-4.301,y))<.0001,(y,p.z)
for x,y in [(-18,-66.5),(-28,-66.5),(-40,-53),(-38,-70),(-28,-69.7),(-49.5,-57),(-49.5,-51),(-48,-68),(-30.35,-52),(-30.35,-62.5)]:
    hit,p,n,index,obj,matrix=bpy.context.scene.ray_cast(deps,Vector((x,y,30)),Vector((0,0,-1)),distance=60)
    assert hit and obj in ground,(x,y,obj)
report={'objects':len(meshes),'ground_objects':len(ground),'checks':'Ground owns x<=-4.3; seam road height matches; lane, parking aisle and rear passage connected; furniture separate'}


# Actual triangle interiors must retain grid and mouth-ramp breaks.
for obj in ground:
    obj.data.calc_loop_triangles()
    for tri in obj.data.loop_triangles:
        points=[obj.data.vertices[i].co for i in tri.vertices]
        a,b,c=points;normal=(b-a).cross(c-a)
        assert normal.length>1e-10,(obj.name,tri.index,'degenerate float32 face')
        if abs(normal.z)<.7*normal.length:continue
        x,y,z=[sum(float(v[k])for v in points)/3 for k in range(3)]
        if obj.name.endswith((' paving','kerb','tactile')):expected=ROAD.height(x,y)+.12
        elif obj.name.endswith((' blocks','yellow')) or (obj.name.endswith((' iron','patch'))and x>-10.6):expected=MOUTH.height(x,y)
        else:expected=ROAD.height(x,y)
        assert abs(z-expected)<.0001,(obj.name,tri.index,z,expected)
for i,(x,y)in enumerate([(-9.4,-63.55),(-9.4,-69.25)]):
    ob=bpy.data.objects['Furniture bollard '+str(i)]
    assert abs(ob.location.z-ROAD.height(x,y)-.12)<1e-6

import os
sys.path.insert(0,str(Path(os.environ['SOUTHPORT_REPO_ROOT'])/'tools'))
from coplanar import check_blender
check_blender(ground)
report['checks']='Single ground ownership; measured ground and explicit throat offsets; triangle interiors; float32 geometry; bollard support; no coplanar ground overlaps.'
(ROOT/'research/validation.json').write_text(json.dumps(report,indent=2)+'\n')
print(report)
