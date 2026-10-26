from pathlib import Path
import bpy,os
from mathutils import Vector
from plan import world
ROOT=Path(__file__).resolve().parents[1]
bpy.ops.wm.open_mainfile(filepath=str(ROOT/'models/funland.blend'));s=bpy.context.scene
views=[('front',(14,-100,4.8),(14,0,4),43),('north',(100,30,5),(29,30,4),68),('pier',(-90,32,5),(0,32,4),70),('rear',(16,140,5),(14,45,4),48),('roof',(14,30,150),(14,25,0),120),('context',(95,-100,85),(12,22,3),106)]
for name,pos,target,scale in views:
 s.camera.location=world(pos);s.camera.rotation_euler=(Vector(world(target))-s.camera.location).to_track_quat('-Z','Y').to_euler();s.camera.data.ortho_scale=scale;s.render.filepath=str(ROOT/'renders'/(name+'.png'));bpy.ops.render.render(write_still=True)
