from pathlib import Path
import bpy,json,sys
from mathutils import Vector
ROOT=Path(__file__).resolve().parents[1]
bpy.ops.wm.open_mainfile(filepath=str(ROOT/'models/burlington-buildings.blend'));s=bpy.context.scene
views=[('front',(47,-50,8),(47,45.5,8),30),('oblique',(4,-15,35),(47,57,8),44),('roof',(88,112,66),(47,59,8),45),('rear',(47,150,20),(47,64,8),36)]
selected=sys.argv[sys.argv.index('--final')+1:] if '--final' in sys.argv else []
for name,pos,target,scale in views:
 if selected and name not in selected:continue
 c=s.camera;c.location=pos;c.rotation_euler=(Vector(target)-c.location).to_track_quat('-Z','Y').to_euler();c.data.ortho_scale=scale
 (ROOT/'renders').mkdir(exist_ok=True);s.render.filepath=str(ROOT/'renders'/f'{name}.png');bpy.ops.render.render(write_still=True)
