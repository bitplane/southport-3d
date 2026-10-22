"""Check actual openings, gable count and footprint registration."""
import json
import math
from pathlib import Path
import bpy
from mathutils import Vector
ROOT=Path(__file__).resolve().parents[1]
bpy.ops.wm.open_mainfile(filepath=str(ROOT/'models/natwest.blend'))
D=json.loads((ROOT/'research/layout.json').read_text())
meshes=[o for o in bpy.context.scene.objects if o.type=='MESH']
assert all(o.data.polygons and o.data.uv_layers for o in meshes)
assert all(math.isfinite(c) for o in meshes for v in o.data.vertices for c in v.co)
assert all(im.packed_file for im in bpy.data.images if im.source=='FILE')
assert len([o for o in meshes if o.name.startswith('Gable ')])==3
assert len([o for o in meshes if o.name.startswith('Window oculus')])==3
assert len([o for o in meshes if o.name.startswith('Balcony rails')])==3
assert len([o for o in meshes if o.name.startswith('ATM metal')])==2
assert len([o for o in meshes if o.name.startswith('Chimney stack')])==4
bpy.context.view_layer.update();deps=bpy.context.evaluated_depsgraph_get()
for ob in meshes:
    if not ob.name.startswith(('Window cross','Window narrow','Window oculus')):continue
    probe=.30 if ob.name.startswith(('Window cross','Window narrow')) else 0
    origin=ob.matrix_world@Vector((probe,0,1))
    direction=(ob.matrix_world.to_3x3()@Vector((0,0,-1))).normalized()
    hit,point,normal,index,target,matrix=bpy.context.scene.ray_cast(deps,origin,direction,distance=2)
    assert hit and target==ob,(ob.name,'window obscured by',target.name if target else None)
points=[ob.matrix_world@v.co for ob in meshes for v in ob.data.vertices]
assert min(p.x for p in points)>D['x_min']-1.3
assert max(p.x for p in points)<D['x_max']+1
assert min(p.y for p in points)>D['rear_y']-.5
assert max(p.y for p in points)<D['front_y']+1.5
# The inner deck must stay below the pitched perimeter; no huge solid roof slab.
hit,point,normal,index,target,matrix=bpy.context.scene.ray_cast(deps,Vector((24,-40,25)),Vector((0,0,-1)),distance=25)
assert hit and point.z<12,(target.name,point)
report={'meshes':len(meshes),'checks':'finite metric meshes, packed maps, three gables/oculi and balconies, two ATMs, four stacks, unobscured main glazing and oculi, footprint limits, lower internal deck'}
(ROOT/'research/validation.json').write_text(json.dumps(report,indent=2)+'\n')
print(report)
