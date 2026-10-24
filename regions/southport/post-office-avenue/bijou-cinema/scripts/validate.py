import bpy,json,math,os,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
bpy.ops.wm.open_mainfile(filepath=str(ROOT/'models/bijou-cinema.blend'))
obs=[o for o in bpy.context.scene.objects if o.type=='MESH'];total=0
for o in obs:
 assert o.data.polygons and o.data.uv_layers,o.name
 assert all(math.isfinite(c) for v in o.data.vertices for c in v.co),o.name
 o.data.calc_loop_triangles();total+=len(o.data.loop_triangles)
 for t in o.data.loop_triangles:
  a,b,c=[o.matrix_world@o.data.vertices[i].co for i in t.vertices]
  assert (b-a).cross(c-a).length>1e-10,(o.name,'degenerate')
sys.path.insert(0,str(Path(os.environ['SOUTHPORT_REPO_ROOT'])/'tools'))
from coplanar import check_blender
check_blender([o for o in obs if o.name.startswith('Wall ')])
(ROOT/'research/validation.json').write_text(json.dumps({'triangles':total,'objects':len(obs)},indent=2)+'\n')
