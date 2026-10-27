from pathlib import Path
import json
import bpy
from mathutils import Vector
from plan import world
ROOT=Path(__file__).resolve().parents[1];D=json.loads((ROOT/'research/layout.json').read_text());bpy.ops.wm.open_mainfile(filepath=str(ROOT/'models/jacksons.blend'));s=bpy.context.scene
for name,pos,target,scale in [('front',(5,-26,5),(5,0,3.6),18),('corner',(-18,-18,13),(4,4,3),23),('rear',(22,30,20),(5,6,3),24),('roof',(5,5,60),(5,5,0),21)]:
 s.camera.location=world(D,pos);s.camera.rotation_euler=(Vector(world(D,target))-s.camera.location).to_track_quat('-Z','Y').to_euler();s.camera.data.ortho_scale=scale;s.render.filepath=str(ROOT/'renders'/(name+'.png'));bpy.ops.render.render(write_still=True)
# Pedestrian-height close comparison to the 2026 corner photograph.
s.camera.data.type='PERSP';s.camera.data.lens=32;s.camera.location=world(D,(-5.7,-7.7,1.8));s.camera.rotation_euler=(Vector(world(D,(2.6,0,2.8)))-s.camera.location).to_track_quat('-Z','Y').to_euler();s.render.filepath=str(ROOT/'renders/street.png');bpy.ops.render.render(write_still=True)
