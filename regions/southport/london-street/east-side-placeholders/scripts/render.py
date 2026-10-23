"""Review the placeholder run from the street and above."""
from pathlib import Path
import bpy
from mathutils import Vector
ROOT=Path(__file__).resolve().parents[1]
bpy.ops.wm.open_mainfile(filepath=str(ROOT/'models/east-side-placeholders.blend'))
s=bpy.context.scene
for name,position,target,scale in [('street',(-14,-60,6),(7.5,-60,4),40),('overview',(-25,-25,40),(18,-60,0),55)]:
 s.camera.location=position;s.camera.rotation_euler=(Vector(target)-s.camera.location).to_track_quat('-Z','Y').to_euler();s.camera.data.ortho_scale=scale
 s.render.filepath=str(ROOT/'renders'/(name+'.png'));bpy.ops.render.render(write_still=True)

# Perspective comparisons approximate the saved Street View poses. These are
# fitted review cameras, not claims of recovered survey/capture coordinates.
import math
s.render.resolution_x=1440;s.render.resolution_y=1000
for name,position,pitch,azimuth in [('myers-reference',(-2.09,-75.05,2.20),18,6.47),('kba-reference',(-1.41,-65.45,2.54),15,1.47)]:
 c=s.camera;c.data.type='PERSP';c.data.sensor_fit='HORIZONTAL';c.data.angle=math.radians(80)
 c.location=position
 p,a=math.radians(pitch),math.radians(azimuth)
 direction=Vector((math.cos(p)*math.cos(a),math.cos(p)*math.sin(a),math.sin(p)))
 c.rotation_euler=direction.to_track_quat('-Z','Y').to_euler()
 s.render.filepath=str(ROOT/'renders'/(name+'.png'));bpy.ops.render.render(write_still=True)
