from pathlib import Path
import json,sys
import bpy
from mathutils import Vector
from plan import world
ROOT=Path(__file__).resolve().parents[1];D=json.loads((ROOT/'research/layout.json').read_text())
bpy.ops.wm.open_mainfile(filepath=str(ROOT/'models/embassy-restaurant.blend'));s=bpy.context.scene
for name,pos,target,scale in [('front',(6,-45,13),(6,0,6),20),('corner',(-28,-32,22),(5,8,6),32),('stanley',(-42,16,15),(0,17,5),41),('roof',(6,17,80),(6,17,0),43)]:
 s.camera.location=world(D,pos);s.camera.rotation_euler=(Vector(world(D,target))-s.camera.location).to_track_quat('-Z','Y').to_euler();s.camera.data.ortho_scale=scale;s.render.filepath=str(ROOT/'renders'/(name+'.png'));bpy.ops.render.render(write_still=True)
