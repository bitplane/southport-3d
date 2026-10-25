"""Bounded quarter plan and oblique; exported assembled views reviewed separately."""
from pathlib import Path
import bpy
from mathutils import Vector
ROOT=Path(__file__).resolve().parents[1]
bpy.ops.wm.open_mainfile(filepath=str(ROOT/'models/frontage-placeholders.blend'))
s=bpy.context.scene
for name,pos,target,scale in [('plan',(-310,-390,900),(-310,-390,0),830),('oblique',(-900,-900,700),(-310,-390,0),850)]:
 s.camera.location=pos;s.camera.rotation_euler=(Vector(target)-s.camera.location).to_track_quat('-Z','Y').to_euler();s.camera.data.ortho_scale=scale
 s.render.filepath=str(ROOT/'renders'/(name+'.png'));bpy.ops.render.render(write_still=True)
