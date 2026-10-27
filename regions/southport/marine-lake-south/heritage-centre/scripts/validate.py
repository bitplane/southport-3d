from pathlib import Path
import math,os,sys,bpy
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(Path(os.environ['SOUTHPORT_REPO_ROOT'])/'tools'))
from coplanar import check_blender
bpy.ops.wm.open_mainfile(filepath=str(R/'models/heritage-centre.blend'))
obs=[o for o in bpy.data.collections['building'].all_objects if o.type=='MESH']
assert obs and all(o.data.polygons for o in obs)
for o in obs:
 assert o.data.uv_layers,o.name
 assert all(math.isfinite(c) for v in o.data.vertices for c in v.co),o.name
 o.data.calc_loop_triangles()
 for t in o.data.loop_triangles:
  a,b,c=[o.matrix_world@o.data.vertices[i].co for i in t.vertices]
  assert (b-a).cross(c-a).length>1e-10,o.name
# Main panels and fascia, roof, glazing, kiosk and joinery are individually
# covered; sign text, vent slots and discrete detail are checked separately.
check_blender([o for o in obs if o.name.startswith(('Shell ','Roof ','Glazing ','Joinery ','Kiosk ','Sign ','Fine '))])
print('Finite/nondegenerate meshes and same-facing coplanar surfaces checked for shell, roof, glazing, joinery, kiosk, signage and fine fittings.')
