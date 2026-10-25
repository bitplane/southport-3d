from pathlib import Path
import sys,bpy
from mathutils import Vector
ROOT=Path(__file__).resolve().parents[1]
bpy.ops.wm.open_mainfile(filepath=str(ROOT/'models/lakeland-leather.blend'));s=bpy.context.scene
views=[('front',(-37.1,10,7.4),(-37.1,46,7.4),18),('corner',(-48,24,18),(-37,51,8),23),('roof',(-25,87,40),(-37,61,8),34),('oriel',(-37.1,27,7.7),(-37.1,46,7.7),9),('shop',(-37.1,29,2.6),(-37.1,46,2.6),9)]
selected=sys.argv[sys.argv.index('--final')+1:] if '--final' in sys.argv else []
for name,pos,target,scale in views:
 if selected and name not in selected:continue
 c=s.camera;c.location=pos;c.rotation_euler=(Vector(target)-c.location).to_track_quat('-Z','Y').to_euler();c.data.ortho_scale=scale
 s.render.filepath=str(ROOT/'renders'/f'{name}.png');bpy.ops.render.render(write_still=True)
