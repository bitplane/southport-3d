from pathlib import Path
import sys,bpy
from mathutils import Vector
ROOT=Path(__file__).resolve().parents[1]
bpy.ops.wm.open_mainfile(filepath=str(ROOT/'models/coffee-king.blend'));s=bpy.context.scene
views=[('front',(-28.42,15,7),(-28.42,47,7),17),('corner',(-45,23,18),(-28.4,52,8),22),('roof',(-45,83,40),(-28.4,58,9),29),('entrance',(-33,35,3),(-29.5,47,3),8.7),('upper',(-28.4,26,11),(-28.4,47,11),9)]
selected=sys.argv[sys.argv.index('--final')+1:] if '--final' in sys.argv else []
for name,pos,target,scale in views:
 if selected and name not in selected:continue
 c=s.camera;c.location=pos;c.rotation_euler=(Vector(target)-c.location).to_track_quat('-Z','Y').to_euler();c.data.ortho_scale=scale
 s.render.filepath=str(ROOT/'renders'/f'{name}.png');bpy.ops.render.render(write_still=True)
