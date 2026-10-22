from pathlib import Path
import bpy
from mathutils import Vector
ROOT=Path(__file__).resolve().parents[1];bpy.ops.wm.open_mainfile(filepath=str(ROOT/'models/terrace.blend'))
s=bpy.context.scene
for name,pos,target,scale in [('terrace',(-22,2,19),(-41,-29,6),32),('front',(-41,2,7),(-41,-25,6),23),('shopfronts',(-41,-7,4),(-41,-24,2.7),21),('roof',(-29,-12,30),(-41,-32,8),26),('sam-thai',(-34,-15,4),(-35.3,-23.6,3.0),7.5),('mamma-mia',(-39,-15,3.9),(-41.3,-23.6,3.0),7.3),('bugle-tap',(-45,-16,4.2),(-47.5,-23.6,3.0),7.8)]:
 c=s.camera;c.location=pos;c.rotation_euler=(Vector(target)-c.location).to_track_quat('-Z','Y').to_euler();c.data.ortho_scale=scale;s.render.filepath=str(ROOT/'renders'/(name+'.png'));bpy.ops.render.render(write_still=True)
