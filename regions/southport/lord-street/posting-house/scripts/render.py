from pathlib import Path
import bpy
from mathutils import Vector
ROOT=Path(__file__).resolve().parents[1]
bpy.ops.wm.open_mainfile(filepath=str(ROOT/'models/posting-house.blend'))
s=bpy.context.scene
views=[('arcade-bases',(47,-17,1.7),(49,-23,.75),8),('building',(5,20,31),(49,-32,10),48),('front',(49,18,14),(49,-23,11),35),('roof',(18,-4,52),(49,-40,10),52),('gable',(43,0,24),(43,-22,18),13),('entrance',(48,-5,6),(48,-23,3.5),14),('rear',(18,-97,32),(49,-57,9),52)]
import sys
selected=sys.argv[sys.argv.index('--final')+1:] if '--final' in sys.argv else []
for name,pos,target,scale in views:
    if selected and name not in selected:continue
    c=s.camera;c.location=pos;c.rotation_euler=(Vector(target)-c.location).to_track_quat('-Z','Y').to_euler();c.data.ortho_scale=scale
    s.render.filepath=str(ROOT/'renders'/f'{name}.png');bpy.ops.render.render(write_still=True)
