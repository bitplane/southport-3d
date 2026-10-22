from pathlib import Path
import bpy
from mathutils import Vector
ROOT=Path(__file__).resolve().parents[1];bpy.ops.wm.open_mainfile(filepath=str(ROOT/'models/public-realm.blend'));s=bpy.context.scene
for name,pos,target,scale in [('overview',(105,240,78),(51,296,2),88),('plan',(53,295,100),(53,295,2),88),('marine-crossing',(10,280,25),(32,302,2),38),('promenade-crossing',(76,267,28),(56,290,2),40)]:
 c=s.camera;c.location=pos;c.rotation_euler=(Vector(target)-c.location).to_track_quat('-Z','Y').to_euler();c.data.ortho_scale=scale;s.render.filepath=str(ROOT/'renders'/(name+'.png'));bpy.ops.render.render(write_still=True)
