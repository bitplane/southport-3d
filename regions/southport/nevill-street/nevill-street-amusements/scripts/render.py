from pathlib import Path
import json,sys
import bpy
from mathutils import Vector
from plan import world
ROOT=Path(__file__).resolve().parents[1];D=json.loads((ROOT/'research/layout.json').read_text())
bpy.ops.wm.open_mainfile(filepath=str(ROOT/'models/nevill-street-amusements.blend'));s=bpy.context.scene
for name,pos,target,scale in [('front',(15,-100,16),(15,0,6),38),('corner',(90,-80,45),(19,15,6),55),('bath',(100,18,20),(30.775,18,6),46),('rear',(12,100,32),(12,21,6),49),('roof',(15,19,120),(15,19,0),49)]:
 s.camera.location=world(D,pos);s.camera.rotation_euler=(Vector(world(D,target))-s.camera.location).to_track_quat('-Z','Y').to_euler();s.camera.data.ortho_scale=scale;s.render.filepath=str(ROOT/'renders'/(name+'.png'));bpy.ops.render.render(write_still=True)
