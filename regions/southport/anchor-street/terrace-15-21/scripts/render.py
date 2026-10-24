from pathlib import Path
import sys,bpy
from mathutils import Vector
ROOT=Path(__file__).resolve().parents[1]
bpy.ops.wm.open_mainfile(filepath=str(ROOT/'models/terrace-15-21.blend'));s=bpy.context.scene
views=[('front',(91,-120,8),(94,-85,6),25),('east',(130,-93,16),(96,-77,6),32),('roof',(110,-107,45),(96,-76,4),32),('rear',(94,-45,17),(96,-76,6),29)]
selected=sys.argv[sys.argv.index('--final')+1:] if '--final' in sys.argv else []
for name,pos,target,scale in views:
 if selected and name not in selected:continue
 c=s.camera;c.location=pos;c.rotation_euler=(Vector(target)-c.location).to_track_quat('-Z','Y').to_euler();c.data.ortho_scale=scale
 s.render.filepath=str(ROOT/'renders'/f'{name}.png');bpy.ops.render.render(write_still=True)
