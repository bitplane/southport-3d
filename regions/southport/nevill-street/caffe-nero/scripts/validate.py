import bpy,sys,os,math,json
from pathlib import Path
R=Path(__file__).resolve().parents[1]
bpy.ops.wm.open_mainfile(filepath=str(R/'models/caffe-nero.blend'))
obs=[o for o in bpy.context.scene.objects if o.type=='MESH']
for o in obs:
 assert o.data.uv_layers and o.data.polygons,o.name
 o.data.calc_loop_triangles()
 for t in o.data.loop_triangles:
  a,b,c=[o.matrix_world@o.data.vertices[i].co for i in t.vertices]
  assert all(math.isfinite(x) for v in (a,b,c) for x in v),o.name
  assert (b-a).cross(c-a).length>1e-10,(o.name,'degenerate')
sys.path.insert(0,str(Path(os.environ['SOUTHPORT_REPO_ROOT'])/'tools'))
from coplanar import check_blender
from coplanar import overlaps
tri=[];labels=[]
for o in obs:
 for t in o.data.loop_triangles:
  tri.append([tuple(o.matrix_world@o.data.vertices[i].co) for i in t.vertices]);labels.append(o.name)
errors=overlaps(tri,labels)
print('OVERLAP PAIRS',sorted(set((a,b) for a,b,_ in errors)),flush=True)
check_blender(obs)
print('All mesh families checked for finite, nondegenerate and same-facing coplanar geometry')
