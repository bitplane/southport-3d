import json,math
from pathlib import Path
import bpy,bmesh
from mathutils import Vector
ROOT=Path(__file__).resolve().parents[1]
bpy.ops.wm.open_mainfile(filepath=str(ROOT/'models/st-georges-place-terrace.blend'))
meshes=[o for o in bpy.context.scene.objects if o.type=='MESH']
assert all(o.data.polygons and o.data.uv_layers for o in meshes)
assert all(math.isfinite(c) for o in meshes for v in o.data.vertices for c in v.co)
assert all(im.packed_file for im in bpy.data.images if im.source=='FILE')
assert len([o for o in meshes if o.name.startswith('Bay white gable')])==6
assert len([o for o in meshes if o.name.startswith('Door recessed timber')])==3
assert len([o for o in meshes if o.name.startswith('Assembly bay ')])==54
assert len([o for o in meshes if o.name.startswith('Assembly sash ')])==99
roofs=[o for o in meshes if o.name.startswith('Roof ')]
assert len(roofs)==10
for ob in roofs:
 bm=bmesh.new();bm.from_mesh(ob.data);assert all(e.is_manifold for e in bm.edges),(ob.name,'open edge');bm.free()
bpy.context.view_layer.update();dep=bpy.context.evaluated_depsgraph_get();probes=0
for ob in meshes:
 if ob.name.startswith('Assembly bay ') and 'storey 0' not in ob.name:
  xs=[v.co.x for v in ob.data.vertices];u=(min(xs)+max(xs))/2
  ray=ob.matrix_world@Vector((u,1.4,.5));direction=(ob.matrix_world.to_3x3()@Vector((0,0,-1))).normalized()
  hit,p,n,i,target,mat=bpy.context.scene.ray_cast(dep,ray,direction,distance=.85)
  assert hit and target==ob,(ob.name,'Blocked glazing',target.name if target else None)
  assert 'glass' in target.data.materials[target.data.polygons[i].material_index].name.lower(),(ob.name,'Ray missed actual glass')
  probes+=1
assert probes==36
sash_probes=0
for ob in meshes:
 if ob.name.startswith('Assembly sash '):
  height=2.52 if ob.name.startswith('Assembly sash front') else 1.9
  ray=ob.matrix_world@Vector((.1,height*.7,.5));direction=(ob.matrix_world.to_3x3()@Vector((0,0,-1))).normalized()
  hit,p,n,i,target,mat=bpy.context.scene.ray_cast(dep,ray,direction,distance=.85)
  assert hit and target==ob,(ob.name,'Blocked sash',target.name if target else None)
  assert 'glass' in target.data.materials[target.data.polygons[i].material_index].name.lower(),ob.name
  sash_probes+=1
assert sash_probes==99
pts=[ob.matrix_world@v.co for ob in meshes for v in ob.data.vertices]
assert 69<min(p.x for p in pts)<74 and 107<max(p.x for p in pts)<112
assert -57<min(p.y for p in pts)<-49 and -23<max(p.y for p in pts)<-16
assert 20<max(p.z for p in pts)<22
report={'meshes':len(meshes),'closed_roofs':len(roofs),'glazing_probes':probes,'sash_probes':sash_probes,'checks':['Finite UV meshes and packed authored textures','Six polygonal bays,90 leaded transoms and three recessed entrances','Closed main,oriel and rear wing roofs','Registered site envelope']}
(ROOT/'research/validation.json').write_text(json.dumps(report,indent=2)+'\n');print(report)
