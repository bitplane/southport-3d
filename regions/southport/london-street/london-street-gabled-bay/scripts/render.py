"""Review street frontage and estimated rear roof envelope."""
from pathlib import Path
import bpy
from mathutils import Vector
ROOT=Path(__file__).resolve().parents[1]
bpy.ops.wm.open_mainfile(filepath=str(ROOT/'models/london-street-gabled-bay.blend'))
s=bpy.context.scene
for name,position,target,scale in [('overview',(35,-170,35),(-25,-119,5),48),('front',(40,-120,7),(-12,-120,5),32),('chapel',(-27,-185,10),(-27,-130,5),34),('roof',(-25,-125,65),(-25,-119,6),42),('rear',(-80,-95,25),(-28,-119,5),45)]:
 s.camera.location=position;s.camera.rotation_euler=(Vector(target)-s.camera.location).to_track_quat('-Z','Y').to_euler();s.camera.data.ortho_scale=scale
 s.render.filepath=str(ROOT/'renders'/(name+'.png'));bpy.ops.render.render(write_still=True)
