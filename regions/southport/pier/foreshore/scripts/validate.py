from pathlib import Path
import bpy,math
r=Path(__file__).resolve().parents[1];bpy.ops.wm.open_mainfile(filepath=str(r/'models/foreshore.blend'))
for o in bpy.context.scene.objects:
 if o.type=='MESH':
  assert len(o.data.polygons)<60
  assert all(math.isfinite(c) for v in o.data.vertices for c in v.co)
  assert all(p.area>0 for p in o.data.polygons)
