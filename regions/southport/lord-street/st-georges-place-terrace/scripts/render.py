from pathlib import Path
import bpy
from mathutils import Vector
ROOT=Path(__file__).resolve().parents[1]
bpy.ops.wm.open_mainfile(filepath=str(ROOT/'models/st-georges-place-terrace.blend'))
s=bpy.context.scene
for name,pos,target,scale in [('building',(58,32,28),(90,-30,9),56),('front',(88,40,12),(89,-20,9),42),('bay',(84,5,12),(84,-20,8),17),('portal',(102,-8,4),(102,-20,2),9),('rear',(119,-90,32),(90,-39,8),55),('roof',(54,-61,65),(89,-33,11),57)]:
 c=s.camera;c.location=pos;c.rotation_euler=(Vector(target)-c.location).to_track_quat('-Z','Y').to_euler();c.data.ortho_scale=scale
 s.render.filepath=str(ROOT/'renders'/f'{name}.png');bpy.ops.render.render(write_still=True)
