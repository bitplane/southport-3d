from pathlib import Path
import bpy
from mathutils import Vector
ROOT=Path(__file__).resolve().parents[1]
bpy.ops.wm.open_mainfile(filepath=str(ROOT/'models/public-realm.blend'))
scene=bpy.context.scene
for name,position,target,scale in [
    ('lantern-head',(-76,-19,3.4),(-77.5,-16.8,3.8),1.3),
    ('christ-gardens',(-95,-85,75),(-103,4,0),90),
    ('christ-entrance',(-102,35,9),(-101,10,0),29),
    ('christ-side',(-64,-35,12),(-87,-15,0),38),
    ('st-georges-gardens',(205,-63,65),(185,4,0),90),
    ('st-georges-paths',(150,35,17),(169,5,0),43),
]:
    camera=scene.camera
    camera.location=position
    camera.rotation_euler=(Vector(target)-camera.location).to_track_quat('-Z','Y').to_euler()
    camera.data.ortho_scale=scale
    scene.render.filepath=str(ROOT/'renders'/(name+'.png'))
    bpy.ops.render.render(write_still=True)
