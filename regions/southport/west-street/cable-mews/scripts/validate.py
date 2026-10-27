from pathlib import Path
import math,os,sys,bpy
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(Path(os.environ['SOUTHPORT_REPO_ROOT'])/'tools'))
from coplanar import check_blender
bpy.ops.wm.open_mainfile(filepath=str(R/'models/cable-mews.blend'))
obs=[o for o in bpy.context.scene.objects if o.type=='MESH']
for o in obs:
 assert o.data.polygons and o.data.uv_layers,o.name
 assert all(math.isfinite(c) for v in o.data.vertices for c in v.co),o.name
 o.data.calc_loop_triangles()
 for t in o.data.loop_triangles:
  a,b,c=[o.matrix_world@o.data.vertices[i].co for i in t.vertices];assert (b-a).cross(c-a).length>1e-10,o.name
check_blender([o for o in obs if o.name.startswith(('Shell ','Architecture ','Glazing ','Fine '))])
print('checked shell, architecture, fine trim and glazing for same-facing coplanar overlap; finite and nondegenerate meshes')
