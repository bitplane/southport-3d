from pathlib import Path
import bpy,math,json
ROOT=Path(__file__).resolve().parents[1]
bpy.ops.wm.open_mainfile(filepath=str(ROOT/'models/prezzo.blend'))
meshes=[o for o in bpy.context.scene.objects if o.type=='MESH']
assert all(o.data.polygons and o.data.uv_layers for o in meshes)
assert all(math.isfinite(c) for o in meshes for v in o.data.vertices for c in v.co)
assert len([o for o in meshes if o.name.startswith('Window dormer')])==9
assert len([o for o in meshes if o.name.startswith('Sign ')])==6
assert len([o for o in meshes if o.name.startswith('Roof chimney')])==6
assert all(i.packed_file for i in bpy.data.images if i.source=='FILE')
points=[o.matrix_world@v.co for o in meshes for v in o.data.vertices]
assert min(p.x for p in points)>-33 and max(p.x for p in points)<-8
assert 20<max(p.z for p in points)<22
(ROOT/'research/validation.json').write_text(json.dumps({'objects':len(meshes),'checks':'finite metric geometry, UVs, packed maps, dormer/sign/stack counts, registered bounds'},indent=2))
print('Prezzo geometry validated',len(meshes),'meshes')

# A plausible window mesh is not enough: its glazing must not sit behind a solid wall.
from mathutils import Vector
bpy.context.view_layer.update();depsgraph=bpy.context.evaluated_depsgraph_get()
windows=[o for o in meshes if o.name.startswith('Window ')]
assert len(windows)==44,len(windows)
for o in windows:
 origin=o.matrix_world@Vector((.25,.20,1))
 direction=(o.matrix_world.to_3x3()@Vector((0,0,-1))).normalized()
 hit,point,normal,index,ob,matrix=bpy.context.scene.ray_cast(depsgraph,origin,direction,distance=2)
 assert hit and ob==o,(o.name,'glazing obstructed by',ob.name if ob else None)
print('All 44 window fronts visible from outside, including dormers')

# Roof-specific review guards: do not restore identical pot groups or UV axes.
recipe=json.loads((ROOT/'research/layout.json').read_text())
assert len([o for o in meshes if o.name.startswith('Pots ')])==3
for spec in recipe['chimneys']:
 ob=bpy.data.objects['Roof chimney '+spec['id']]
 assert abs(ob.rotation_euler.z-math.radians(spec['yaw_degrees']))<1e-5
 pot=bpy.data.objects.get('Pots '+spec['id'])
 assert bool(pot)==bool(spec['pots'])
 if pot:assert len(pot.data.vertices)==spec['pots']*8*12
roof=bpy.data.objects['Roof mansard'];uv=roof.data.uv_layers.active.data
for f in roof.data.polygons:
 if f.material_index:continue
 for li in f.loop_indices:
  z=roof.data.vertices[roof.data.loops[li].vertex_index].co.z
  expected=(z-recipe['base_z']-15.7)*math.hypot(1.8,2.6)/2.6/2.4
  assert abs(uv[li].uv.y-expected)<1e-5
print('Chimney orientation/pot groups and horizontal slate courses validated')
