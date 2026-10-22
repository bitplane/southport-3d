"""Review street frontage and estimated rear roof envelope."""
from pathlib import Path
import bpy
from mathutils import Vector
ROOT=Path(__file__).resolve().parents[1]
bpy.ops.wm.open_mainfile(filepath=str(ROOT/'models/london-street-20.blend'))
s=bpy.context.scene
for name,position,target,scale in [('overview',(8,-79,22),(-20,-92,6),23),('front',(12,-92,6.5),(-11.5,-92,6.5),18),('rear',(-50,-80,18),(-24,-92,5),26),('roof',(-30,-79,32),(-23,-92,5),26),('shop',(-1,-92,3.2),(-11.5,-92,2.6),10)]:
 s.camera.location=position;s.camera.rotation_euler=(Vector(target)-s.camera.location).to_track_quat('-Z','Y').to_euler();s.camera.data.ortho_scale=scale
 s.render.filepath=str(ROOT/'renders'/(name+'.png'));bpy.ops.render.render(write_still=True)
