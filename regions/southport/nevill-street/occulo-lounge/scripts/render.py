from pathlib import Path
import sys,bpy
from mathutils import Vector
ROOT=Path(__file__).resolve().parents[1]
bpy.ops.wm.open_mainfile(filepath=str(ROOT/'models/occulo.blend'));s=bpy.context.scene
views=[('front',(-17.42,-25,9.5),(-17.42,47,9.5),22),('corner',(15,8,24),(-17,54,9.5),32),('nevill',(55,55,10),(-10,55,10),22),('roof',(0,80,55),(-17,55,14),29),('entrance',(-17.42,22,3.7),(-17.42,46.7,3.7),8.5),('capital',(-18,26,14.5),(-18,47,14.5),7)]
selected=sys.argv[sys.argv.index('--final')+1:] if '--final' in sys.argv else []
for name,pos,target,scale in views:
 if selected and name not in selected:continue
 c=s.camera;c.location=pos;c.rotation_euler=(Vector(target)-c.location).to_track_quat('-Z','Y').to_euler();c.data.ortho_scale=scale
 s.render.filepath=str(ROOT/'renders'/f'{name}.png');bpy.ops.render.render(write_still=True)
