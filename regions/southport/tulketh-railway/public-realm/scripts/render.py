"""Bounded quarter plan and oblique; exported assembled views reviewed separately."""
from pathlib import Path
import bpy
from mathutils import Vector
ROOT=Path(__file__).resolve().parents[1]
bpy.ops.wm.open_mainfile(filepath=str(ROOT/'models/public-realm.blend'))
s=bpy.context.scene;s.camera.data.clip_end=5000
for name,pos,target,scale in [('plan',(-140,-390,900),(-140,-390,0),560),('oblique',(400,-900,650),(-140,-390,0),670)]:
 s.camera.location=pos;s.camera.rotation_euler=(Vector(target)-s.camera.location).to_track_quat('-Z','Y').to_euler();s.camera.data.ortho_scale=scale
 s.render.filepath=str(ROOT/'renders'/(name+'.png'));bpy.ops.render.render(write_still=True)
