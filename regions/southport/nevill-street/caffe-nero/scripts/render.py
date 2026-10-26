from pathlib import Path
import sys,bpy
from mathutils import Vector
R=Path(__file__).resolve().parents[1]
bpy.ops.wm.open_mainfile(filepath=str(R/'models/caffe-nero.blend'));s=bpy.context.scene
views=[('front',(-43.52,12,10),(-43.52,46,10),20),('oblique',(-59,24,16),(-43.52,49,9),23),('roof',(-61,84,36),(-43.3,59,10),34),('gallery',(-44,26,14.8),(-43.52,46,14.8),8),('shop',(-44,30,3.8),(-43.52,46,3.8),8)]
sel=sys.argv[sys.argv.index('--final')+1:] if '--final' in sys.argv else []
for n,pos,target,scale in views:
 if sel and n not in sel:continue
 c=s.camera;c.location=pos;c.rotation_euler=(Vector(target)-c.location).to_track_quat('-Z','Y').to_euler();c.data.ortho_scale=scale;s.render.filepath=str(R/'renders'/f'{n}.png');bpy.ops.render.render(write_still=True)
