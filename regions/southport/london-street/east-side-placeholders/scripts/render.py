"""Review the placeholder run from the street and above."""
from pathlib import Path
import bpy
from mathutils import Vector
ROOT=Path(__file__).resolve().parents[1]
bpy.ops.wm.open_mainfile(filepath=str(ROOT/'models/east-side-placeholders.blend'))
s=bpy.context.scene
for name,position,target,scale in [('street',(-14,-60,6),(7.5,-60,4),40),('overview',(-25,-25,40),(18,-60,0),55)]:
 s.camera.location=position;s.camera.rotation_euler=(Vector(target)-s.camera.location).to_track_quat('-Z','Y').to_euler();s.camera.data.ortho_scale=scale
 s.render.filepath=str(ROOT/'renders'/(name+'.png'));bpy.ops.render.render(write_still=True)
