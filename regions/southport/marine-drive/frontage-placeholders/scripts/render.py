"""Bounded quarter plan and oblique; exported assembled views reviewed separately."""
from pathlib import Path
import bpy
from mathutils import Vector
ROOT=Path(__file__).resolve().parents[1]
bpy.ops.wm.open_mainfile(filepath=str(ROOT/'models/frontage-placeholders.blend'))
s=bpy.context.scene;s.camera.data.clip_end=10000
for name,pos,target,scale in [('plan',(600,575,1800),(600,575,0),1700),('oblique',(-700,-500,1400),(600,575,0),1800),('bridge',(-220,120,220),(0,410,2),360),('fairway',(1150,500,350),(1330,860,2),400)]:
 s.camera.location=pos;s.camera.rotation_euler=(Vector(target)-s.camera.location).to_track_quat('-Z','Y').to_euler();s.camera.data.ortho_scale=scale
 s.render.filepath=str(ROOT/'renders'/(name+'.png'));bpy.ops.render.render(write_still=True)
