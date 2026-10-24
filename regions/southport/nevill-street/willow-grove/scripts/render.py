from pathlib import Path
import sys,bpy
from mathutils import Vector
ROOT=Path(__file__).resolve().parents[1]
bpy.ops.wm.open_mainfile(filepath=str(ROOT/'models/willow-grove.blend'));s=bpy.context.scene
views=[('lord',(29,18,8),(28,45,8),19),('nevill',(-18,74,10),(10,74,10),23),('roof',(53,110,57),(26,72,9),62),('stanley',(29,116,11),(32,95,9),24),('corner',(-16,14,24),(22,64,8),58)]
selected=sys.argv[sys.argv.index('--final')+1:] if '--final' in sys.argv else []
for name,pos,target,scale in views:
 if selected and name not in selected:continue
 c=s.camera;c.location=pos;c.rotation_euler=(Vector(target)-c.location).to_track_quat('-Z','Y').to_euler();c.data.ortho_scale=scale
 (ROOT/'renders').mkdir(exist_ok=True);s.render.filepath=str(ROOT/'renders'/f'{name}.png');bpy.ops.render.render(write_still=True)
