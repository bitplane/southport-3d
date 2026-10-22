import bpy,json,math
from pathlib import Path
from mathutils import Vector
ROOT=Path(__file__).resolve().parents[1];bpy.ops.wm.open_mainfile(filepath=str(ROOT/'models/terrace.blend'))
D=json.loads((ROOT/'research/layout.json').read_text());meshes=[o for o in bpy.context.scene.objects if o.type=='MESH']
assert all(o.data.polygons and o.data.uv_layers for o in meshes)
assert all(math.isfinite(c) for o in meshes for v in o.data.vertices for c in v.co)
assert all(i.packed_file for i in bpy.data.images if i.source=='FILE')
points=[o.matrix_world@v.co for o in meshes for v in o.data.vertices]
assert min(v.x for v in points)>D['x_far']-.2 and max(v.x for v in points)<D['x_near']+.2
assert 12<max(v.z for v in points)<13
windows=[o for o in meshes if o.name.startswith('Window ')];assert len(windows)==6
bpy.context.view_layer.update();deps=bpy.context.evaluated_depsgraph_get()
for o in windows:
 origin=o.matrix_world@Vector((.2,.2,1));direction=(o.matrix_world.to_3x3()@Vector((0,0,-1))).normalized()
 hit,point,normal,index,obj,matrix=bpy.context.scene.ray_cast(deps,origin,direction,distance=2)
 assert hit and obj==o,(o.name,obj.name if obj else None)
# Door must remain recessed from display panes, at every authored unit.
for shop in D['shops']:
 ob=next(o for o in meshes if o.name.startswith('Shop recessed door '+shop['id']))
 assert max((ob.matrix_world@v.co).y for v in ob.data.vertices)<D['front_y']-.30
report={'objects':len(meshes),'upper_windows':6,'checks':'finite metric meshes, packed maps, bounds, six visible window openings and three recessed door positions'}
(ROOT/'research/validation.json').write_text(json.dumps(report,indent=2));print(report)

# Fascia lettering must sit in front of its awning, not be hidden by the valance.
for ob in [o for o in meshes if o.name.startswith('Sign ')]:
 origin=ob.matrix_world@Vector((0,0,.8));direction=(ob.matrix_world.to_3x3()@Vector((0,0,-1))).normalized()
 hit,point,normal,index,found,matrix=bpy.context.scene.ray_cast(deps,origin,direction,distance=1)
 assert hit and found==ob,(ob.name,'obscured by',found.name if found else None)
print('All sign centres visible from their authored front')
