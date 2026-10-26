from pathlib import Path
import json
import bpy
from mathutils import Vector
from plan import world
ROOT=Path(__file__).resolve().parents[1];D=json.loads((ROOT/'research/layout.json').read_text());bpy.ops.wm.open_mainfile(filepath=str(ROOT/'models/nevill-street-15.blend'));s=bpy.context.scene
for name,pos,target,scale in [('front',(6.5,-26,2.8),(6.5,0,3.6),17),('corner',(27,-18,16),(6.5,4,3),23),('rear',(22,30,20),(6.5,7,3),24),('roof',(6.5,7,60),(6.5,7,0),21)]:
 s.camera.location=world(D,pos);s.camera.rotation_euler=(Vector(world(D,target))-s.camera.location).to_track_quat('-Z','Y').to_euler();s.camera.data.ortho_scale=scale;s.render.filepath=str(ROOT/'renders'/(name+'.png'));bpy.ops.render.render(write_still=True)
