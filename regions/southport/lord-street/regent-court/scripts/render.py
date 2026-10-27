from pathlib import Path
import bpy,sys
from mathutils import Vector
ROOT=Path(__file__).resolve().parents[1];bpy.ops.wm.open_mainfile(filepath=str(ROOT/'models/regent-court.blend'));s=bpy.context.scene
views=[('side-oblique',(449,5,55),(493,-23,16),58),('service',(535,-55,8),(491,-41,4),38),('shop-close',(492.15,5,3),(492.15,-9.6,2.4),8),('bay-close',(484,10,25),(484,-10.6,21),12),('street',(494,55,21),(494,-20,17),54),('rear',(494,-95,36),(494,-20,18),58),('roof',(450,-80,90),(494,-20,20),60)]
selected=sys.argv[sys.argv.index('--final')+1:] if '--final' in sys.argv else []
for name,pos,target,scale in views:
 if selected and name not in selected:continue
 pos=Vector(pos);target=Vector(target);s.camera.location=pos;s.camera.rotation_euler=(target-pos).to_track_quat('-Z','Y').to_euler();s.camera.data.ortho_scale=scale;s.render.filepath=str(ROOT/'renders'/f'{name}.png');bpy.ops.render.render(write_still=True)
