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
windows=[o for o in meshes if o.name.startswith('Window glazed shaft')];assert len(windows)==21
for o in windows:
 angle=json.loads((ROOT/'research/layout.json').read_text())['registration_radians']
 direction=Vector((-math.cos(angle),-math.sin(angle),0))
 origin=o.matrix_world@Vector((0,.1,0))-direction
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
# Both stone shoulders are lower than the centred curved glass crown.
front_inv=(reg@Matrix(((0,0,1,D['front_x']),(1,0,0,D['south_y']),(0,1,0,D['base_z']),(0,0,0,1)))).inverted()
baybase=[o for o in meshes if o.name.startswith('Trim curved spandrel 6')]
fascia=[o for o in meshes if o.name.startswith(('Sign Money Shop fascia','Shop yellow fascia backing','Trim fascia crown'))]
baybottom=min((front_inv@o.matrix_world@v.co).y for o in baybase for v in o.data.vertices)
fasciatop=max((front_inv@o.matrix_world@v.co).y for o in fascia for v in o.data.vertices)
assert baybottom>fasciatop+.01,('Curved bay intersects fascia',baybottom,fasciatop)
front=front_inv.inverted()
for direction in [Vector((-1,0,0)),Vector((1,0,0)),Vector((0,1,0))]:
 origin=front@Vector((1.01,1.4,-.12))
 hit,p,n,i,found,m=bpy.context.scene.ray_cast(deps,origin,(front.to_3x3()@direction).normalized(),distance=1.7)
 assert hit and found.name.startswith(('Shop entrance side return','Shop entrance soffit')),('Open entrance',tuple(direction))
cap=bpy.data.objects['Trim rounded terminal upper']
cap_u=[(front_inv@cap.matrix_world@v.co).x for v in cap.data.vertices]
assert min(cap_u)>1.1 and max(cap_u)<4.3
centres=[(front_inv@o.matrix_world.translation).x for o in windows]
assert min(centres)<1.6 and max(centres)>3.8
assert abs(sum(centres)/len(centres)-2.7)<.01
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
return_lights=[o for o in meshes if o.name.startswith('Shop inset return light')]
assert len(return_lights)==18
for o in return_lights:
 centre=sum((v.co for v in o.data.vertices),Vector())/len(o.data.vertices)
 direction=Vector((-math.cos(D['registration_radians']),-math.sin(D['registration_radians']),0))
 origin=o.matrix_world@centre-direction
 hit,p,n,i,found,m=bpy.context.scene.ray_cast(deps,origin,direction,distance=2)
 assert hit and found==o,(o.name,found.name if found else None)
report={'mesh_objects':len(meshes),'glazed_upper_panels':21,'checks':'Finite UV meshes; packed authored textures; unobscured three-storey glass; closed deck,rooflights and curvedcap; shared20boundary and geographic registration.'}
(ROOT/'research/validation.json').write_text(json.dumps(report,indent=2)+'\n');print(report)
