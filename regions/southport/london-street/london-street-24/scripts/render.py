"""Review street frontage and estimated rear roof envelope."""
from pathlib import Path
import bpy
from mathutils import Vector
ROOT=Path(__file__).resolve().parents[1]
bpy.ops.wm.open_mainfile(filepath=str(ROOT/'models/london-street-24.blend'))
s=bpy.context.scene
for name,position,target,scale in [('overview',(8,-85,23),(-20,-104,5),24),('front',(12,-104,6.5),(-11.5,-104,4.5),16),('rear',(-52,-87,20),(-24,-104,5),26),('roof',(-26,-86,34),(-23,-104,5),26),('shop',(-1,-104,3.2),(-11.5,-104,2.6),10)]:
 s.camera.location=position;s.camera.rotation_euler=(Vector(target)-s.camera.location).to_track_quat('-Z','Y').to_euler();s.camera.data.ortho_scale=scale
 s.render.filepath=str(ROOT/'renders'/(name+'.png'));bpy.ops.render.render(write_still=True)
