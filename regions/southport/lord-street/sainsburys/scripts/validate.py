"""Source geometry checks for open shop windows, roofs and registration."""
import json,math
from pathlib import Path
import bpy,bmesh
from mathutils import Vector
ROOT=Path(__file__).resolve().parents[1]
bpy.ops.wm.open_mainfile(filepath=str(ROOT/'models/sainsburys.blend'))
meshes=[o for o in bpy.context.scene.objects if o.type=='MESH']
assert all(o.data.polygons and o.data.uv_layers for o in meshes)
assert all(math.isfinite(c) for o in meshes for v in o.data.vertices for c in v.co)
assert all(im.packed_file for im in bpy.data.images if im.source=='FILE')
assert len([o for o in meshes if o.name.startswith('Window upper brick surround')])==9
assert len([o for o in meshes if o.name.startswith('Window church wing brick arch')])==10
assert len([o for o in meshes if o.name.startswith('Canopy cast column')])==10
assert len([o for o in meshes if o.name.startswith('Window shop glass')])==9
for name in ('Roof main front hip','Roof church wing hip','Roof main flat membrane'):
 ob=bpy.data.objects[name];bm=bmesh.new();bm.from_mesh(ob.data);assert all(e.is_manifold for e in bm.edges),(name,'open edge');bm.free()
bpy.context.view_layer.update();dep=bpy.context.evaluated_depsgraph_get();probes=0
for ob in meshes:
 if ob.name.startswith('Window shop glass'):
  # Upper left glazing segment avoids mullions, doors and information boards.
  ray=ob.matrix_world@Vector((-.95,3.4,.5));direction=(ob.matrix_world.to_3x3()@Vector((0,0,-1))).normalized()
  hit,p,n,i,target,mat=bpy.context.scene.ray_cast(dep,ray,direction,distance=1.2)
  assert hit and target.name.startswith('Window shop glass'),(ob.name,'Blocked shop aperture',target.name if target else None)
  probes+=1
# Continuous roof coverage: include the shorter wing's former open strip.
D=json.loads((ROOT/'research/layout.json').read_text())
from mathutils import Matrix
world=Matrix.Translation((*D['origin_site_xy'],D['base_z']))@Matrix.Rotation(math.radians(D['local_rotation_degrees']),4,'Z')
roof_probes=0
for x in [1+i*(D['width']-2)/20 for i in range(21)]:
 for y in [-D['depth']+1+i*(D['depth']-2)/30 for i in range(31)]+[-11.7,-11.3]:
  origin=world@Vector((x,y,25))
  hit,p,n,i,target,matrix=bpy.context.scene.ray_cast(dep,origin,Vector((0,0,-1)),distance=20)
  assert hit and p.z>=D['base_z']+D['rear_parapet']-.24,('roof opening',x,y,target.name if target else None,p.z if hit else None)
  roof_probes+=1
print('Continuous roof coverage:',roof_probes,'downward samples')
pts=[ob.matrix_world@v.co for ob in meshes for v in ob.data.vertices]
assert 106<min(p.x for p in pts)<111 and 150<max(p.x for p in pts)<158
assert -74<min(p.y for p in pts)<-65 and -19<max(p.y for p in pts)<-12
assert 16<max(p.z for p in pts)<18
report={'meshes':len(meshes),'shop_aperture_probes':probes,'checks':['Finite UV meshes and packed authored textures','9 projecting upper bays,5 front and5 return wing arches,9 ground glazed openings,10 cast columns','Closed two hip roofs and flat roof deck','Unobscured storefront glazing','Registered bounded site envelope']}
(ROOT/'research/validation.json').write_text(json.dumps(report,indent=2)+'\n');print(report)

# Every wall cap faces out; coincident coping undersides face the opposite way.
for name,low,high in [('north',0,D['rear_parapet']),('south',0,D['rear_parapet']),('rear',0,D['rear_parapet']),
                      ('stepped front lower',0,D['church_wing_parapet']),('stepped front upper',D['church_wing_parapet'],D['front_parapet'])]:
 ob=bpy.data.objects['Envelope '+name];caps=0
 for face in ob.data.polygons:
  # Boolean opening repair can leave microscopic float32 fragments; the
  # map audit retains them. This regression checks the wall's cap/skin faces.
  if face.area<1e-5:continue
  p=[ob.data.vertices[i].co for i in face.vertices]
  if all(abs(v.y-high)<1e-4 for v in p):assert face.normal.y>.99,(name,'Inward top cap');caps+=1
  if all(abs(v.y-low)<1e-4 for v in p):assert face.normal.y<-.99,(name,'Inward bottom cap')
  if all(abs(v.z)<1e-5 for v in p):assert face.normal.z>.99,(name,'Inward exterior skin')
 assert caps,(name,'Missing top cap')
print('Wall exterior skins and horizontal caps retain authored outward normals')

# Rays through each return arch and the ATM screen must reach recessed surfaces.
for ob in meshes:
 if ob.name.startswith('Window church side glazing'):
  ray=ob.matrix_world@Vector((0,7,.5));direction=(ob.matrix_world.to_3x3()@Vector((0,0,-1))).normalized()
  hit,p,n,i,target,mat=bpy.context.scene.ray_cast(dep,ray,direction,distance=1.2)
  assert hit and target.name.startswith('Window church side glazing'),('Blocked return opening',ob.name,target.name if target else None)
ob=bpy.data.objects['Fitting ATM dark screen']
centre=sum((v.co for v in ob.data.vertices),Vector())/len(ob.data.vertices)
ray=ob.matrix_world@(centre+Vector((0,0,.5)));direction=(ob.matrix_world.to_3x3()@Vector((0,0,-1))).normalized()
hit,p,n,i,target,mat=bpy.context.scene.ray_cast(dep,ray,direction,distance=1.2)
assert hit and target.name=='Fitting ATM dark screen',('ATM obstructed',target.name if target else None)
