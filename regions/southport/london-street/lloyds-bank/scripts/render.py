from pathlib import Path
import bpy
from mathutils import Vector
ROOT=Path(__file__).resolve().parents[1]
bpy.ops.wm.open_mainfile(filepath=str(ROOT/'models/lloyds-bank.blend'))
s=bpy.context.scene
for name,pos,target,scale in [('cornice-prototype',(-4,-86.8,6),(8,-86.6,5.0),3.2),('window-prototype',(-4,-90,8),(8,-88.8,7.8),4.8),('street',(-10,-110,14),(17,-91,5),32),('anchor',(15,-65,14),(22,-89,5),42),('roof',(0,-62,42),(20,-91,5),42)]:
 s.camera.location=pos;s.camera.rotation_euler=(Vector(target)-s.camera.location).to_track_quat('-Z','Y').to_euler();s.camera.data.ortho_scale=scale
 s.render.filepath=str(ROOT/'renders'/(name+'.png'));bpy.ops.render.render(write_still=True)
