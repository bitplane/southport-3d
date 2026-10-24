from pathlib import Path
import json,sys
import bpy
from mathutils import Vector
from plan import world
ROOT=Path(__file__).resolve().parents[1];D=json.loads((ROOT/'research/layout.json').read_text())
bpy.ops.wm.open_mainfile(filepath=str(ROOT/'models/nevill-street-3-9.blend'));s=bpy.context.scene
views=[('front',(8.4,-40,7),(8.4,0,6),20),('overview',(-14,-24,21),(8,5,6),28),('rear',(27,38,22),(8,8,6),32),('roof',(9,8,65),(9,8,0),28)]
for name,pos,target,scale in views:
 s.camera.location=world(D,pos);s.camera.rotation_euler=(Vector(world(D,target))-s.camera.location).to_track_quat('-Z','Y').to_euler();s.camera.data.ortho_scale=scale;s.render.filepath=str(ROOT/'renders'/(name+'.png'));bpy.ops.render.render(write_still=True)
