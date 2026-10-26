from pathlib import Path
import bpy
from mathutils import Vector
ROOT=Path(__file__).resolve().parents[1];bpy.ops.wm.open_mainfile(filepath=str(ROOT/'models/pavilions.blend'))
s=bpy.context.scene
for name,target,pos,scale in [('north-front',(-150,-3,1.4),(-175,-3,7),23),('north-side',(-150,-3,1.4),(-173,-28,9),25),('north-roof',(-150,-3,1),(-150,-3,80),23),('south-front',(-230,-2,1.4),(-205,-2,7),23),('south-side',(-230,-2,1.4),(-210,22,9),24),('south-roof',(-230,-2,1),(-230,-2,80),23)]:
 s.camera.location=pos;s.camera.rotation_euler=(Vector(target)-s.camera.location).to_track_quat('-Z','Y').to_euler();s.camera.data.ortho_scale=scale;s.render.filepath=str(ROOT/'renders'/(name+'.png'));bpy.ops.render.render(write_still=True)
