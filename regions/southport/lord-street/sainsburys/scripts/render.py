from pathlib import Path
import bpy,sys
from mathutils import Vector
ROOT=Path(__file__).resolve().parents[1]
bpy.ops.wm.open_mainfile(filepath=str(ROOT/'models/sainsburys.blend'))
s=bpy.context.scene
views=sys.argv[sys.argv.index('--final')+1:] if '--final' in sys.argv else []
for name,pos,target,scale in [('church-return',(185,-6,10),(151,-26,5),23),('atm',(164,-18,3),(152,-22,1.8),8),('building',(80,35,33),(130,-38,8),67),('front',(130,40,12),(130,-19,7),49),('canopy',(112,5,7),(131,-17,3.4),29),('windows',(119,9,13),(123,-19,9),21),('rear',(157,-110,28),(133,-65,7),52),('roof',(87,-83,70),(130,-43,10),69)]:
 if views and name not in views:continue
 c=s.camera;c.location=pos;c.rotation_euler=(Vector(target)-c.location).to_track_quat('-Z','Y').to_euler();c.data.ortho_scale=scale
 s.render.filepath=str(ROOT/'renders'/f'{name}.png');bpy.ops.render.render(write_still=True)
