"""Review street frontage and estimated rear roof envelope."""
from pathlib import Path
import bpy
from mathutils import Vector
ROOT=Path(__file__).resolve().parents[1]
bpy.ops.wm.open_mainfile(filepath=str(ROOT/'models/london-street-18.blend'))
s=bpy.context.scene
for name,position,target,scale in [('overview',(8,-68,22),(-20,-85,6),23),('front',(12,-84,6.5),(-11.5,-84,6.5),18),('rear',(-50,-72,18),(-24,-85,5),26),('roof',(-30,-68,32),(-23,-85,5),26),('shop',(-1,-84,3.2),(-11.5,-84,2.6),10)]:
 s.camera.location=position;s.camera.rotation_euler=(Vector(target)-s.camera.location).to_track_quat('-Z','Y').to_euler();s.camera.data.ortho_scale=scale
 s.render.filepath=str(ROOT/'renders'/(name+'.png'));bpy.ops.render.render(write_still=True)
