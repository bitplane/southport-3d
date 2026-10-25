from pathlib import Path
import json,sys
import bpy
from mathutils import Vector
from plan import world
ROOT=Path(__file__).resolve().parents[1];D=json.loads((ROOT/'research/layout.json').read_text())
bpy.ops.wm.open_mainfile(filepath=str(ROOT/'models/nevill-street-11-13.blend'));s=bpy.context.scene
views=[('front',(4.7,-35,8),(4.7,0,7.7),20),('overview',(21,-27,23),(4.7,4,7),23),('rear',(21,33,23),(4.7,6,7),25),('roof',(4.7,5.5,65),(4.7,5.5,0),18)]
for name,pos,target,scale in views:
 s.camera.location=world(D,pos);s.camera.rotation_euler=(Vector(world(D,target))-s.camera.location).to_track_quat('-Z','Y').to_euler();s.camera.data.ortho_scale=scale;s.render.filepath=str(ROOT/'renders'/(name+'.png'));bpy.ops.render.render(write_still=True)
