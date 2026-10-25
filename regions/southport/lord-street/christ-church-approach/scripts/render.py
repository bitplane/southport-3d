"""Side court and pedestrian link review views."""
from pathlib import Path
import bpy
from mathutils import Vector
ROOT=Path(__file__).resolve().parents[1]
bpy.ops.wm.open_mainfile(filepath=str(ROOT/'models/public-realm.blend'))
s=bpy.context.scene
for name,pos,target,scale in [('plan',(-105,-75,180),(-105,-75,0),190),('oblique',(-185,-190,110),(-118,-65,0),145),('garden',(-150,-83,28),(-123,-38,1),55)]:
 s.camera.location=pos;s.camera.rotation_euler=(Vector(target)-s.camera.location).to_track_quat('-Z','Y').to_euler();s.camera.data.ortho_scale=scale;s.render.filepath=str(ROOT/'renders'/(name+'.png'));bpy.ops.render.render(write_still=True)
