"""Verify glass openings, closed roof/cap and the shared20 boundary."""
from pathlib import Path
import json,math,os
import bpy,bmesh
from mathutils import Vector,Matrix
ROOT=Path(__file__).resolve().parents[1]
bpy.ops.wm.open_mainfile(filepath=str(ROOT/'models/london-street-22.blend'))
meshes=[o for o in bpy.context.scene.objects if o.type=='MESH']
assert all(o.data.polygons and o.data.uv_layers for o in meshes)
assert all(math.isfinite(c) for o in meshes for v in o.data.vertices for c in v.co)
assert all(i.packed_file for i in bpy.data.images if i.source=='FILE')
bpy.context.view_layer.update();deps=bpy.context.evaluated_depsgraph_get()
windows=[o for o in meshes if o.name.startswith('Window glazed shaft')];assert len(windows)==3
for o in windows:
 origin=o.matrix_world@Vector((.2,0,1));direction=(o.matrix_world.to_3x3()@Vector((0,0,-1))).normalized()
 hit,p,n,i,found,m=bpy.context.scene.ray_cast(deps,origin,direction,distance=2)
 assert hit and found==o,(o.name,found.name if found else None)
for o in meshes:
 if o.name.startswith(('Roof rooflight glazing','Trim rounded terminal','Roof flat deck')):
  bm=bmesh.new();bm.from_mesh(o.data);assert all(e.is_manifold for e in bm.edges),o.name;bm.free()
D=json.loads((ROOT/'research/layout.json').read_text());p=D['registration_pivot'];reg=Matrix.Translation((*p,0))@Matrix.Rotation(D['registration_radians'],4,'Z')@Matrix.Translation((-p[0],-p[1],0))
points=[reg.inverted()@o.matrix_world@v.co for o in meshes for v in o.data.vertices]
assert min(v.y for v in points)>D['south_y']-.05
assert max(v.y for v in points)<D['north_y']+.05
assert min(v.x for v in points)>D['rear_x']-.05
assert 13.8<max(v.z for v in points)<14.2
repo=Path(os.environ['SOUTHPORT_REPO_ROOT']);nd=json.loads((repo/'regions/southport/london-street/london-street-20/research/layout.json').read_text())
for f in ['front_x','base_z','registration_pivot','registration_radians']:assert D[f]==nd[f],f
assert D['north_y']==nd['south_y']
# The south stone shoulder is lower than the off-centre glazed crown.
front_inv=(reg@Matrix(((0,0,1,D['front_x']),(1,0,0,D['south_y']),(0,1,0,D['base_z']),(0,0,0,1)))).inverted()
cap=bpy.data.objects['Trim rounded terminal upper']
cap_u=[(front_inv@cap.matrix_world@v.co).x for v in cap.data.vertices]
assert min(cap_u)>.80 and max(cap_u)>5.35
for o in windows:
 assert abs((front_inv@o.matrix_world.translation).x-2.995)<.01
# Side-wall end caps must terminate inside the rear wall, avoiding coplanar stripes.
for o in meshes:
 if o.name.startswith('Envelope party'):
  assert min((reg.inverted()@o.matrix_world@v.co).x for v in o.data.vertices)>D['rear_x']+.35
entrance=bpy.data.objects['Shop pale entrance leaf']
centre=sum((v.co for v in entrance.data.vertices),Vector())/len(entrance.data.vertices)
assert centre.x<1.1
origin=entrance.matrix_world@(centre+Vector((0,0,1)))
direction=(entrance.matrix_world.to_3x3()@Vector((0,0,-1))).normalized()
hit,p,n,i,found,m=bpy.context.scene.ray_cast(deps,origin,direction,distance=2)
assert hit and found==entrance,'Left recessed entrance must remain visible'
report={'mesh_objects':len(meshes),'glazed_upper_bays':3,'checks':'Finite UV meshes; packed authored textures; unobscured three-storey glass; closed deck,rooflights and curvedcap; shared20boundary and geographic registration.'}
(ROOT/'research/validation.json').write_text(json.dumps(report,indent=2)+'\n');print(report)
