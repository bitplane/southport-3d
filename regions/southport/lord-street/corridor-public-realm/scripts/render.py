from pathlib import Path
import bpy
from mathutils import Vector
ROOT=Path(__file__).resolve().parents[1]
bpy.ops.wm.open_mainfile(filepath=str(ROOT/'models/public-realm.blend'))
s=bpy.context.scene
for name,x,scale in [('duke',-660,330),('south',-380,390),('garden',-185,150),('central',-20,410),('north',405,400)]:
 for angle in ['plan','oblique']:
  target=Vector((x,15,0));pos=Vector((x,15,500)) if angle=='plan' else Vector((x-125,-225,260))
  s.camera.location=pos;s.camera.rotation_euler=(target-pos).to_track_quat('-Z','Y').to_euler();s.camera.data.ortho_scale=scale
  s.render.filepath=str(ROOT/'renders'/(name+'-'+angle+'.png'));bpy.ops.render.render(write_still=True)
