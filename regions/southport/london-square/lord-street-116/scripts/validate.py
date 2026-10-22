"""Check facade visibility, neighbour bounds, entrance recess and sign receivers."""
import bpy,json,math
from pathlib import Path
from mathutils import Vector
ROOT=Path(__file__).resolve().parents[1];bpy.ops.wm.open_mainfile(filepath=str(ROOT/'models/bhf.blend'))
D=json.loads((ROOT/'research/layout.json').read_text());meshes=[o for o in bpy.context.scene.objects if o.type=='MESH']
assert all(o.data.polygons and o.data.uv_layers for o in meshes)
assert all(math.isfinite(c) for o in meshes for v in o.data.vertices for c in v.co)
assert all(i.packed_file for i in bpy.data.images if i.source=='FILE')
points=[o.matrix_world@v.co for o in meshes for v in o.data.vertices]
assert min(v.x for v in points)>=D['x_far']-.07 and max(v.x for v in points)<=D['x_near']+.07
assert 13.7<max(v.z for v in points)<14
windows=[o for o in meshes if o.name.startswith('Window ')];assert len(windows)==D['upper_bays']
bpy.context.view_layer.update();deps=bpy.context.evaluated_depsgraph_get()
for o in windows+[o for o in meshes if o.name.startswith('Sign ')]:
 origin=o.matrix_world@Vector((0,0,.8));direction=(o.matrix_world.to_3x3()@Vector((0,0,-1))).normalized()
 hit,point,normal,index,obj,matrix=bpy.context.scene.ray_cast(deps,origin,direction,distance=1.5)
 assert hit and obj==o,(o.name,obj.name if obj else None)
doors=next(o for o in meshes if o.name=='Shop recessed doors')
assert max((doors.matrix_world@v.co).y for v in doors.data.vertices)<D['front_y']-1.1
assert len([o for o in meshes if o.name.startswith('Shop entrance step')])==3
report={'objects':len(meshes),'window_modules':len(windows),'checks':'metric finite meshes, packed maps, neighbour bounds, visible windows/signs, deep entrance and three steps'}
(ROOT/'research/validation.json').write_text(json.dumps(report,indent=2));print(report)
