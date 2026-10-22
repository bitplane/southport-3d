from pathlib import Path
import bpy
from mathutils import Vector
ROOT=Path(__file__).resolve().parents[1]
bpy.ops.wm.open_mainfile(filepath=str(ROOT/'models/christ-church.blend'))
s=bpy.context.scene
for name,pos,target,scale in [('front',(-102,16,14),(-102,-27,11.8),33),('building',(-136,12,28),(-98,-41,9),51),('cafe',(-64,-2,17),(-99,-30,10),34),('tower',(-118,-4,20),(-102,-26,15),19),('side',(-142,-47,15),(-108,-43,7),35),('roof',(-135,-4,66),(-97,-45,7),65)]:
    c=s.camera;c.location=pos;c.rotation_euler=(Vector(target)-c.location).to_track_quat('-Z','Y').to_euler();c.data.ortho_scale=scale
    s.render.filepath=str(ROOT/'renders'/f'{name}.png');bpy.ops.render.render(write_still=True)
