"""Mechanical checks complement reference and assembled-export review."""
import json,math,os,sys
from pathlib import Path
import bpy,bmesh
from mathutils import Vector
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(Path(os.environ['SOUTHPORT_REPO_ROOT'])/'tools'))
from coplanar import check_blender
bpy.ops.wm.open_mainfile(filepath=str(ROOT/'models/nevill-street-11-13.blend'))
obs=[o for o in bpy.context.scene.objects if o.type=='MESH'];triangles=0
for o in obs:
 assert o.data.polygons and o.data.uv_layers,o.name
 assert all(math.isfinite(c) for v in o.data.vertices for c in v.co),o.name
 o.data.calc_loop_triangles();triangles+=len(o.data.loop_triangles)
 for t in o.data.loop_triangles:
  a,b,c=(o.matrix_world@o.data.vertices[i].co for i in t.vertices)
  assert (b-a).cross(c-a).length>1e-10,(o.name,'degenerate triangle')
 if o.get('closed_shell'):
  bm=bmesh.new();bm.from_mesh(o.data);bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=.00012)
  assert all(e.is_manifold for e in bm.edges),(o.name,'open roof shell')
  assert bm.calc_volume(signed=True)>0,(o.name,'inward roof');bm.free()
check_blender([o for o in obs if o.name.startswith(('Shell ','Architecture ','Glazing '))])
# Fine carvings and arrises are also checked. Only the decorative iron loops
# have welded intersections; native exported audit records their three tiny
# groups separately, rather than exempting the facade or all fine detail.
fine=[]
for o in obs:
 if not o.name.startswith('Fine '):continue
 mesh=o.data.copy();tmp=bpy.data.objects.new('Regression '+o.name,mesh);bm=bmesh.new();bm.from_mesh(mesh)
 remove=[f for f in bm.faces if mesh.materials[f.material_index].name=='Black painted wrought iron']
 bmesh.ops.delete(bm,geom=remove,context='FACES');bm.to_mesh(mesh);bm.free();fine.append(tmp)
check_blender([o for o in obs if o.name.startswith(('Shell ','Architecture ','Glazing '))]+fine)
for o in fine:
 mesh=o.data;bpy.data.objects.remove(o);bpy.data.meshes.remove(mesh)
# Openings must genuinely pass through street brick into separate glazing.
d=json.loads((ROOT/'research/layout.json').read_text());x,y,z=d['origin'];bpy.context.view_layer.update();deps=bpy.context.evaluated_depsgraph_get();probes=0
for u,w in d['first_windows']:
 q=u+w*.22;p=Vector((x+.0135*q+.45,y+q+.02087*.45,z+5.18));direction=Vector((-1,-.02087,0)).normalized();hit,point,n,i,o,M=bpy.context.scene.ray_cast(deps,p,direction,distance=1)
 assert hit and o.name.startswith('Glazing '),(u,o.name if o else None);probes+=1
assert all(im.packed_file for im in bpy.data.images if im.source=='FILE')
report={'triangles':triangles,'window_probes':probes,'checks':['finite float32 geometry','nondegenerate triangles','closed outward hip roof','real street window apertures','all architectural meshes and non-iron ornament overlap regression','packed authored textures'],'limitations':['Decorative iron-loop welds remain subject to the exported audit; three tiny self-overlap groups are recorded in review.json. Other architecture and ornament are checked together.']}
(ROOT/'research/validation.json').write_text(json.dumps(report,indent=2)+'\n');print(report)
