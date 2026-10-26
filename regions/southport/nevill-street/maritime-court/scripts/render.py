from pathlib import Path
import bpy
from mathutils import Vector
from plan import world
ROOT=Path(__file__).resolve().parents[1]
bpy.ops.wm.open_mainfile(filepath=str(ROOT/'models/maritime-court.blend'));s=bpy.context.scene
for name,pos,target,scale in [('promenade',(23,-100,25),(23,0,12),57),('corner',(-65,-65,45),(20,18,11),72),('nevill',(-100,21,27),(0,21,12),53),('rear',(75,85,45),(22,21,12),67),('roof',(23,20,120),(23,20,0),58)]:
 s.camera.location=world(pos);s.camera.rotation_euler=(Vector(world(target))-s.camera.location).to_track_quat('-Z','Y').to_euler();s.camera.data.ortho_scale=scale;s.render.filepath=str(ROOT/'renders'/(name+'.png'));bpy.ops.render.render(write_still=True)
