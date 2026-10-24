from pathlib import Path
import sys,bpy
from mathutils import Vector
ROOT=Path(__file__).resolve().parents[1]
bpy.ops.wm.open_mainfile(filepath=str(ROOT/'models/lord-street-377-385.blend'));s=bpy.context.scene
views=[('corner',(-15,20,16),(15,54,7),34),('lord',(16,12,8),(16,45,8),24),('nevill',(-30,57,8),(9,57,8),33),('roof',(44,88,40),(16,57,10),35),('entrance',(0,33,4),(11,47,3),13),('capital',(-3,56,13),(9,57,11),8)]
selected=sys.argv[sys.argv.index('--final')+1:] if '--final' in sys.argv else []
for name,pos,target,scale in views:
 if selected and name not in selected:continue
 c=s.camera;c.location=pos;c.rotation_euler=(Vector(target)-c.location).to_track_quat('-Z','Y').to_euler();c.data.ortho_scale=scale
 s.render.filepath=str(ROOT/'renders'/f'{name}.png');bpy.ops.render.render(write_still=True)
