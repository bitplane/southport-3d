from pathlib import Path
import json,sys
import bpy
from mathutils import Vector
from plan import world
ROOT=Path(__file__).resolve().parents[1];D=json.loads((ROOT/'research/layout.json').read_text())
bpy.ops.wm.open_mainfile(filepath=str(ROOT/'models/nevill-street-16-22.blend'));s=bpy.context.scene
views=[('yard',(-25,20,8),(3,12.8,4),13),('front',(8,-38,12),(8,0,7),23),('overview',(-22,-29,24),(8,4,7),27),('rear',(-18,30,24),(8,6,7),29),('roof',(8,5.5,65),(8,5.5,0),22)]
selected=sys.argv[sys.argv.index('--final')+1:] if '--final' in sys.argv else []
for name,pos,target,scale in views:
 if selected and name not in selected:continue
 s.camera.location=world(D,pos);s.camera.rotation_euler=(Vector(world(D,target))-s.camera.location).to_track_quat('-Z','Y').to_euler();s.camera.data.ortho_scale=scale;s.render.filepath=str(ROOT/'renders'/(name+'.png'));bpy.ops.render.render(write_still=True)
