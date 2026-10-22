"""Check identity, registration and exposed windows rather than mesh counts alone."""
from pathlib import Path
import json
import math
import bpy
from mathutils import Vector

ROOT=Path(__file__).resolve().parents[1]
bpy.ops.wm.open_mainfile(filepath=str(ROOT/'models/london-street-6-12.blend'))
D=json.loads((ROOT/'research/layout.json').read_text())
meshes=[obj for obj in bpy.context.scene.objects if obj.type=='MESH']
assert all(obj.data.polygons and obj.data.uv_layers for obj in meshes)
assert all(math.isfinite(x) for obj in meshes for v in obj.data.vertices for x in v.co)
assert all(im.packed_file for im in bpy.data.images if im.source=='FILE')
windows=[obj for obj in meshes if obj.name.startswith('Window front ')]
assert len(windows)==24, len(windows)
points=[obj.matrix_world@v.co for obj in meshes for v in obj.data.vertices]
assert -31<min(v.x for v in points)<-29
assert -9.5<max(v.x for v in points)<-8.8
assert min(v.y for v in points)>-64 and max(v.y for v in points)<-41
assert 12<max(v.z for v in points)<14
bpy.context.view_layer.update()
deps=bpy.context.evaluated_depsgraph_get()
for obj in windows:
    origin=obj.matrix_world@Vector((.23,.23,1))
    direction=(obj.matrix_world.to_3x3()@Vector((0,0,-1))).normalized()
    hit,point,normal,index,found,matrix=bpy.context.scene.ray_cast(deps,origin,direction,distance=2)
    assert hit and found==obj,(obj.name,found.name if found else None)
# Ground entrance remains set back from the display panes, not a wall filling it.
doors=[obj for obj in meshes if obj.name.startswith('Shop recessed door leaf')]
assert len(doors)==2
assert all(max((obj.matrix_world@v.co).x for v in obj.data.vertices)<D['front_x']-.5 for obj in doors)
# No coincident exterior faces on the Glebe wall or its corner cap. These
# samples exposed overlapping return boxes as black patches in the render.
for origin,direction in [(Vector((-28,D['south_y']-1,D['base_z']+2)),Vector((0,1,0))),
                         (Vector((D['front_x']+1,D['south_y']+.16,D['base_z']+6.6)),Vector((-1,0,0)))]:
    distances=[]
    for obj in meshes:
        inverse=obj.matrix_world.inverted()
        hit,p,n,index=obj.ray_cast(inverse@origin,(inverse.to_3x3()@direction).normalized())
        if hit:
            distances.append(((obj.matrix_world@p-origin).length,obj.name))
    distances.sort()
    assert distances and sum(abs(distance-distances[0][0])<1e-5 for distance,name in distances)==1,distances[:3]
report={'objects':len(meshes),'front_windows':len(windows),'checks':'Finite UV meshes, packed maps, registered extent, 24 unobscured front windows, recessed double entrance'}
(ROOT/'research/validation.json').write_text(json.dumps(report,indent=2)+'\n')
print(report)
