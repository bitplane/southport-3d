from pathlib import Path
import bpy,math,json
ROOT=Path(__file__).resolve().parents[1]
bpy.ops.wm.open_mainfile(filepath=str(ROOT/'models/prezzo.blend'))
meshes=[o for o in bpy.context.scene.objects if o.type=='MESH']
assert all(o.data.polygons and o.data.uv_layers for o in meshes)
assert all(math.isfinite(c) for o in meshes for v in o.data.vertices for c in v.co)
assert len([o for o in meshes if o.name.startswith('Window dormer')])==9
assert len([o for o in meshes if o.name.startswith('Sign ')])==12
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
assert len(windows)==71,len(windows)
for o in windows:
 origin=o.matrix_world@Vector((.25,.20,1))
 direction=(o.matrix_world.to_3x3()@Vector((0,0,-1))).normalized()
 hit,point,normal,index,ob,matrix=bpy.context.scene.ray_cast(depsgraph,origin,direction,distance=2)
 assert hit and ob==o,(o.name,'glazing obstructed by',ob.name if ob else None)
print('All 71 window fronts visible from outside, including dormers')

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
 assert f.normal.x>=-.001 and f.normal.y>=-.001, 'Unobserved rear hip slope restored'
 for li in f.loop_indices:
  z=roof.data.vertices[roof.data.loops[li].vertex_index].co.z
  expected=(z-recipe['base_z']-15.7)*math.hypot(1.8,2.6)/2.6/2.4
  assert abs(uv[li].uv.y-expected)<1e-5
print('Chimney orientation/pot groups and horizontal slate courses validated')

# Additional probes catch roof slopes crossing the lower dormer glazing.
for ob in windows:
 if 'dormer' not in ob.name:continue
 for xy in [(-.25,-.30),(.25,-.30),(-.25,.30),(.25,.30)]:
  hit,p,n,i,found,mat=bpy.context.scene.ray_cast(depsgraph,ob.matrix_world@Vector((*xy,1)),(ob.matrix_world.to_3x3()@Vector((0,0,-1))).normalized(),distance=2)
  assert hit and found==ob,(ob.name,xy,found.name if found else None)
for ob in [o for o in meshes if o.name.startswith('Sign ')]:
 hit,p,n,i,found,mat=bpy.context.scene.ray_cast(depsgraph,ob.matrix_world@Vector((0,0,.8)),(ob.matrix_world.to_3x3()@Vector((0,0,-1))).normalized(),distance=1.2)
 assert hit and found==ob,(ob.name,'sign obscured',found.name if found else None)
assert len([o for o in meshes if o.name.startswith('Cornice continuous')])==2
assert len([o for o in meshes if o.name.startswith('Stonework ')])==2
print('Lower dormer glazing, sign visibility and continuous cornice checks passed')

# London shop bays have distinct glazing registers; pilasters must not cross them.
for ob in [o for o in windows if 'shop-london' in o.name]:
 for x,y in [(-1.35,1.0),(1.35,1.0),(-1.35,-.85),(1.35,-.85)]:
  hit,p,n,i,found,mat=bpy.context.scene.ray_cast(depsgraph,ob.matrix_world@Vector((x,y,1)),(ob.matrix_world.to_3x3()@Vector((0,0,-1))).normalized(),distance=2)
  assert hit and found==ob,(ob.name,'bay edge obstructed',found.name if found else None)
for ob in [o for o in windows if o.name.startswith('Window lower ')]:
 hit,p,n,i,found,mat=bpy.context.scene.ray_cast(depsgraph,ob.matrix_world@Vector((.35,-1.475,1)),(ob.matrix_world.to_3x3()@Vector((0,0,-1))).normalized(),distance=2)
 assert hit and found.name.startswith('Dressings first floor inset'),(ob.name,'inset apron missing',found.name if found else None)
 assert (ob.matrix_world.inverted()@p).z<-.10,(ob.name,'apron is not recessed')
print('London glazing edges clear of pilasters; first-floor aprons genuinely recessed')

assert bpy.data.objects.get('Roof end gables')
for label in ['Lord flats','London inset']:
 ob=bpy.data.objects['Entrance recessed '+label]
 x=.9 if label=='Lord flats' else 1.1
 hit,p,n,i,found,mat=bpy.context.scene.ray_cast(depsgraph,ob.matrix_world@Vector((x,1.55,1)),(ob.matrix_world.to_3x3()@Vector((0,0,-1))).normalized(),distance=2)
 assert hit and found==ob,(label,'entrance hidden',found.name if found else None)
 assert (ob.matrix_world.inverted()@p).z<-.20

# The researched rear keeps open stair recesses and actual rear windows.
assert len([o for o in meshes if o.name.startswith('Envelope rear wing ')])==3
assert len([o for o in meshes if o.name.startswith('Envelope rear stair recess ')])==2
assert len([o for o in meshes if o.name.startswith('Envelope rear escape structure')])==2
assert bpy.data.objects.get('Envelope rear angular duct')
assert bpy.data.objects.get('Sign flats address')
assert min(p.y for p in points)>-46 and min(p.y for p in points)<-44
assert not bpy.data.objects.get('Envelope rear estimate')
assert not bpy.data.objects.get('Roof access enclosure')
print('Stepped rear wings, open escape assemblies, angular duct and flats address present')

hit,p,n,i,found,mat=bpy.context.scene.ray_cast(depsgraph,Vector((-16,-48,recipe['base_z']+17)),Vector((0,1,0)),distance=12)
assert hit and found.name=='Envelope rear east upper gable',('Open rear mansard end',found.name if found else None)
print('Rear mansard end closes above lower east wing')

for ob in [o for o in meshes if o.name.startswith(('Envelope rear wing ','Envelope rear stair recess '))]:
 uv=ob.data.uv_layers.active.data
 for face in ob.data.polygons:
  if abs(face.normal.y)>.5:continue
  for index in face.loop_indices:
   v=ob.data.vertices[ob.data.loops[index].vertex_index].co
   assert abs(uv[index].uv.y-v.y/1.8)<1e-5,(ob.name,'rear brick courses rotated')
print('Rear brick courses horizontal on both elevation and return faces')

# The gable/recess seam was previously a real 100 mm hole. Horizontal probes
# check its former band; a rising oblique probe checks the 300 mm soffit return.
for z in [15.02,15.05,15.08]:
 hit,p,n,i,found,mat=bpy.context.scene.ray_cast(depsgraph,Vector((-16,-50,recipe['base_z']+z)),Vector((0,1,0)),distance=13)
 assert hit and found.name=='Envelope rear east upper gable',('rear seam hole',z,found.name if found else None)
hit,p,n,i,found,mat=bpy.context.scene.ray_cast(depsgraph,Vector((-16,-44,recipe['base_z']+13)),Vector((0,5.2,2.02)).normalized(),distance=6)
assert hit and found.name=='Envelope rear east upper gable',('rear soffit open',found.name if found else None)
assert abs(p.z-recipe['base_z']-15.0)<1e-4,('rear soffit wrong height',tuple(p))
print('Rear gable seam and offset soffit closed to horizontal and oblique rays')
