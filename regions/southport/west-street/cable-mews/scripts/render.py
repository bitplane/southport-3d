from pathlib import Path
import bpy
from mathutils import Vector
R=Path(__file__).resolve().parents[1];bpy.ops.wm.open_mainfile(filepath=str(R/'models/cable-mews.blend'));s=bpy.context.scene
for name,pos,target,scale in [('street',(-42,110,9),(-70,111,6),24),('roof',(-51,91,26),(-70,112,5),27),('rear',(-91,132,23),(-70,112,6),27)]:
 s.camera.location=pos;s.camera.rotation_euler=(Vector(target)-s.camera.location).to_track_quat('-Z','Y').to_euler();s.camera.data.ortho_scale=scale;s.render.filepath=str(R/'renders'/(name+'.png'));bpy.ops.render.render(write_still=True)

# Street View camera approximates the recorded 2020 pano position and 90 degree field.
s.camera.data.type='PERSP';s.camera.data.lens=18;s.camera.location=(-52.3,110.4,4.15);s.camera.rotation_euler=(Vector((-70,110.4,8.3))-s.camera.location).to_track_quat('-Z','Y').to_euler();s.render.filepath=str(R/'renders'/'street-perspective.png');bpy.ops.render.render(write_still=True)
