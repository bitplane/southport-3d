"""Review the front, Glebe side and stepped roofs."""
from pathlib import Path
import bpy
from mathutils import Vector
ROOT=Path(__file__).resolve().parents[1]
bpy.ops.wm.open_mainfile(filepath=str(ROOT/'models/london-street-14-16.blend'))
s=bpy.context.scene
for name,position,target,scale in [('overview',(8,-58,19),(-18,-75,5),22),('front',(12,-74.5,6),(-12,-74.5,5.5),15),('glebe',(-27,-53,12),(-19,-69,5),22),('roof',(-34,-61,28),(-19,-75,6),23),('shop',(0,-74.5,4),(-12,-74.5,2.3),13)]:
 s.camera.location=position;s.camera.rotation_euler=(Vector(target)-s.camera.location).to_track_quat('-Z','Y').to_euler();s.camera.data.ortho_scale=scale
 s.render.filepath=str(ROOT/'renders'/(name+'.png'));bpy.ops.render.render(write_still=True)
