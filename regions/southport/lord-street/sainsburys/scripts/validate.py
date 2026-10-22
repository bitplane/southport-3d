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
assert len([o for o in meshes if o.name.startswith('Window church wing brick arch')])==4
assert len([o for o in meshes if o.name.startswith('Canopy cast column')])==8
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
pts=[ob.matrix_world@v.co for ob in meshes for v in ob.data.vertices]
assert 106<min(p.x for p in pts)<111 and 150<max(p.x for p in pts)<158
assert -74<min(p.y for p in pts)<-65 and -19<max(p.y for p in pts)<-12
assert 16<max(p.z for p in pts)<18
report={'meshes':len(meshes),'shop_aperture_probes':probes,'checks':['Finite UV meshes and packed authored textures','9 projecting upper bays,4 wing arches,9 ground glazed openings,8 cast columns','Closed two hip roofs and flat roof deck','Unobscured storefront glazing','Registered bounded site envelope']}
(ROOT/'research/validation.json').write_text(json.dumps(report,indent=2)+'\n');print(report)
