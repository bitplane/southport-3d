from pathlib import Path
import json
import bpy
from mathutils import Vector
from plan import world
ROOT=Path(__file__).resolve().parents[1];D=json.loads((ROOT/'research/layout.json').read_text())
bpy.ops.wm.open_mainfile(filepath=str(ROOT/'models/the-cloisters.blend'));s=bpy.context.scene
for name,pos,target,scale in [('front',(8,-90,9),(8,0,7),22),('corner',(-65,-80,38),(8,8,7),29),('church',(-90,9,15),(0,9,6),24),('rear',(40,85,35),(8,10,6),29),('roof',(8,9,100),(8,9,0),27)]:
 s.camera.location=world(D,pos);s.camera.rotation_euler=(Vector(world(D,target))-s.camera.location).to_track_quat('-Z','Y').to_euler();s.camera.data.ortho_scale=scale;s.render.filepath=str(ROOT/'renders'/(name+'.png'));bpy.ops.render.render(write_still=True)
