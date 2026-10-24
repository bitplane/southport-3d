from pathlib import Path
import sys,bpy
from mathutils import Vector
ROOT=Path(__file__).resolve().parents[1]
bpy.ops.wm.open_mainfile(filepath=str(ROOT/'models/bijou-cinema.blend'));s=bpy.context.scene
views=[('front',(55,-55,7),(90,-55,4),17),('roof',(76,-85,35),(98,-57,4),27),('rear',(130,-65,13),(107,-57,5),18),('entrance',(77,-55,3),(89,-55,2.5),6)]
selected=sys.argv[sys.argv.index('--final')+1:] if '--final' in sys.argv else []
for name,pos,target,scale in views:
 if selected and name not in selected:continue
 c=s.camera;c.location=pos;c.rotation_euler=(Vector(target)-c.location).to_track_quat('-Z','Y').to_euler();c.data.ortho_scale=scale
 s.render.filepath=str(ROOT/'renders'/f'{name}.png');bpy.ops.render.render(write_still=True)
