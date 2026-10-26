from pathlib import Path
import json,math
import bpy
from mathutils import Vector
R=Path(__file__).resolve().parents[1];D=json.loads((R/'research/layout.json').read_text());X,Y,Z=D['origin'];W,L=D['width'],D['length']
def world(p):
 u,v,z=p;t=v/L;q=u/W
 return Vector((X+u+t*(2.189*(1-q)+.498*q),Y+v+(1-t)*2.862*(1-q)+t*(-.016+.694*q),Z+z))
bpy.ops.wm.open_mainfile(filepath=str(R/'models/former-bhs.blend'));s=bpy.context.scene
for name,pos,target,lens in [('chapel-oblique',(W+18,-36,12),(W*.55,0,8),35),('corner-return',(W+22,-18,12),(W,4,8),40),('corporation',(W+38,34,14),(W,34,6),38),('arcade',(-22,32,10),(0,33,7),40),('roof',(W+28,-28,38),(W*.5,17,9),40)]:
 s.camera.data.type='PERSP';s.camera.data.lens=lens;s.camera.location=world(pos);s.camera.rotation_euler=(world(target)-s.camera.location).to_track_quat('-Z','Y').to_euler();s.render.filepath=str(R/'renders'/(name+'.png'));bpy.ops.render.render(write_still=True)
