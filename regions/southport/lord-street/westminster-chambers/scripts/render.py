from pathlib import Path
import bpy
from mathutils import Vector
R=Path(__file__).resolve().parents[1];bpy.ops.wm.open_mainfile(filepath=str(R/'models/westminster-chambers.blend'));s=bpy.context.scene
for name,pos,target,scale in [('corner',(-245,4,28),(-276,-36,9),38),('rear',(-303,-63,29),(-276,-36,9),38),('roof',(-272,-35,45),(-276,-36,5),35),('front',(-276,-10,9),(-276,-25,8),25),('front-full',(-276,-10,10.5),(-276,-25,9.5),30),('side',(-250,-36,9),(-266,-36,8),25)]:
 s.camera.location=pos;s.camera.rotation_euler=(Vector(target)-s.camera.location).to_track_quat('-Z','Y').to_euler();s.camera.data.ortho_scale=scale;s.render.filepath=str(R/'renders'/(name+'.png'));bpy.ops.render.render(write_still=True)
for name,position,target,lens in [('street',(-276,-1,1.8),(-276,-25,8.0),35),('oriel-close',(-273,-15,6.1),(-273,-25,6.1),42),('entrance-close',(-280,-17,2),(-280,-25,2.4),42)]:
 s.camera.data.type='PERSP';s.camera.data.lens=lens;s.camera.location=position;s.camera.rotation_euler=(Vector(target)-s.camera.location).to_track_quat('-Z','Y').to_euler();s.render.filepath=str(R/'renders'/(name+'.png'));bpy.ops.render.render(write_still=True)
