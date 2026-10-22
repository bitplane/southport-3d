from pathlib import Path
import bpy
from mathutils import Vector
ROOT=Path(__file__).resolve().parents[1]
bpy.ops.wm.open_mainfile(filepath=str(ROOT/'models/glebe-place.blend'))
s=bpy.context.scene
for name,pos,target,scale in [
 ('overview',(-5,-88,40),(-27,-61,0),46),
 ('mouth',(5,-74,15),(-9,-66.4,.7),17),
 ('parking',(-53,-74,20),(-36,-53,1),31),
 ('lane',(-5,-67,4),(-30,-66,1),24),
]:
    camera=s.camera
    camera.location=pos
    camera.rotation_euler=(Vector(target)-camera.location).to_track_quat('-Z','Y').to_euler()
    camera.data.ortho_scale=scale
    s.render.filepath=str(ROOT/'renders'/(name+'.png'))
    bpy.ops.render.render(write_still=True)
