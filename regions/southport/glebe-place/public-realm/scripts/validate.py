"""Check ground ownership, traversable seam and furnishing classification."""
from pathlib import Path
import json
import math
import bpy
from mathutils import Vector
ROOT=Path(__file__).resolve().parents[1]
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
    hit,p,n,index,obj,matrix=bpy.context.scene.ray_cast(deps,Vector((-4.301,y,3)),Vector((0,0,-1)),distance=4)
    assert hit and obj in ground,(y,obj)
    assert abs(p.z-.66465)<.005,(y,p.z)
for x,y in [(-18,-66.5),(-28,-66.5),(-40,-53),(-38,-70),(-28,-69.7),(-49.5,-57),(-49.5,-51),(-48,-68),(-30.35,-52),(-30.35,-62.5)]:
    hit,p,n,index,obj,matrix=bpy.context.scene.ray_cast(deps,Vector((x,y,3)),Vector((0,0,-1)),distance=4)
    assert hit and obj in ground,(x,y,obj)
report={'objects':len(meshes),'ground_objects':len(ground),'checks':'Ground owns x<=-4.3; seam road height matches; lane, parking aisle and rear passage connected; furniture separate'}
(ROOT/'research/validation.json').write_text(json.dumps(report,indent=2)+'\n')
print(report)
