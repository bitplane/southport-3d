"""Isolated massing plan and oblique; assembled ground is reviewed in the viewer."""
import os
from pathlib import Path
import bpy
from mathutils import Vector
ROOT=Path(__file__).resolve().parents[1]
bpy.ops.wm.open_mainfile(filepath=str(ROOT/'models/frontage-placeholders.blend'))
# Render isolated massing; the assembled published viewer supplies ground review.
s=bpy.context.scene
for name,pos,target,scale in [('plan',(-140,-150,400),(-140,-150,0),300),('oblique',(-330,-340,240),(-140,-145,0),300)]:
 s.camera.location=pos;s.camera.rotation_euler=(Vector(target)-s.camera.location).to_track_quat('-Z','Y').to_euler();s.camera.data.ortho_scale=scale
 s.render.filepath=str(ROOT/'renders'/(name+'.png'));bpy.ops.render.render(write_still=True)
