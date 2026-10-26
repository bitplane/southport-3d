import bpy,math
from pathlib import Path
R=Path(__file__).resolve().parents[1];bpy.ops.wm.open_mainfile(filepath=str(R/'models/canopy.blend'))
for o in bpy.context.scene.objects:
 if o.type!='MESH':continue
 assert o.data.uv_layers and all(math.isfinite(x) for v in o.data.vertices for x in v.co)
 o.data.calc_loop_triangles()
 for t in o.data.loop_triangles:
  a,b,c=[o.data.vertices[i].co for i in t.vertices];assert (b-a).cross(c-a).length>1e-10
print('Glazed canopy geometry checked; adjacent seam and visual review remain required')
