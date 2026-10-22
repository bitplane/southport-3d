from pathlib import Path
import bpy
from mathutils import Vector
ROOT=Path(__file__).resolve().parents[1];bpy.ops.wm.open_mainfile(filepath=str(ROOT/'models/prezzo.blend'))
s=bpy.context.scene
for name,pos,target,scale in [('corner',(17,4,24),(-20,-30,10),38),('lord-street',(-22,8,11),(-22,-25,10),28),('london-street',(20,-31,12),(-10,-31,10),25),('roof',(0,-10,38),(-21,-31,15),30)]:
 c=s.camera;c.location=pos;c.rotation_euler=(Vector(target)-c.location).to_track_quat('-Z','Y').to_euler();c.data.ortho_scale=scale;s.render.filepath=str(ROOT/'renders'/(name+'.png'));bpy.ops.render.render(write_still=True)
