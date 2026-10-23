from pathlib import Path
import bpy
from mathutils import Vector
ROOT=Path(__file__).resolve().parents[1]
bpy.ops.wm.open_mainfile(filepath=str(ROOT/'models/natwest.blend'))
s=bpy.context.scene
views=[('building',(-28,15,26),(18,-35,8),47),('front',(19,20,12),(19,-24,10),27),
       ('london',(-29,-37,13),(8,-37,9),34),('roof',(-12,0,48),(19,-37,8),43),
       ('entrance',(-3,-5,9),(10.5,-23.2,4),11),('gable',(27,0,16),(27,-23,15.3),9),
       ('balcony',(19,-5,10),(19,-23,8.5),8),
       ('kiosk',(32.1,-17.5,2.4),(32.6,-22.25,1.85),3.6),
       ('kiosk-oblique',(29.3,-18.5,3.6),(32.6,-22.25,1.9),3.6)]
import sys
selected=sys.argv[sys.argv.index('--final')+1:] if '--final' in sys.argv else []
for name,pos,target,scale in views:
    if selected and name not in selected:continue
    c=s.camera;c.location=pos;c.rotation_euler=(Vector(target)-c.location).to_track_quat('-Z','Y').to_euler();c.data.ortho_scale=scale
    s.render.filepath=str(ROOT/'renders'/f'{name}.png');bpy.ops.render.render(write_still=True)
