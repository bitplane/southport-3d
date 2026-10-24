"""Export-precision geometry, roof shells and real glazing apertures."""
import json,math,os,sys
from pathlib import Path
import bpy,bmesh
from mathutils import Vector
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(Path(os.environ['SOUTHPORT_REPO_ROOT'])/'tools'))
from coplanar import check_blender
bpy.ops.wm.open_mainfile(filepath=str(ROOT/'models/nevill-street-3-9.blend'))
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
bpy.context.view_layer.update();deps=bpy.context.evaluated_depsgraph_get();probes=0
for o in obs:
 if not o.get('window_probe'):continue
 origin,direction=o['window_probe'];hit,p,n,i,target,M=bpy.context.scene.ray_cast(deps,Vector(origin),Vector(direction),distance=1)
 assert hit and target.name.startswith('Glazing '),(o.name,target.name if target else None)
 probes+=1
assert probes==17,probes
check_blender([o for o in obs if o.name.startswith('Shell ')])
assert all(im.packed_file for im in bpy.data.images if im.source=='FILE')
report={'triangles':triangles,'window_probes':probes,'checks':['finite float32 meshes','nondegenerate triangles','closed outward roof slabs','17 unobscured upper windows','scoped coplanar shell check','packed source textures']}
(ROOT/'research/validation.json').write_text(json.dumps(report,indent=2)+'\n');print(report)
