from pathlib import Path
import bpy
from mathutils import Vector
ROOT=Path(__file__).resolve().parents[1]
bpy.ops.wm.open_mainfile(filepath=str(ROOT/'models/st-georges-church.blend'))
s=bpy.context.scene
views=[('building',(117,29,36),(168,-30,22),59),
       ('front',(168,35,20),(168,-19,22),54),
       ('porch',(158,1,9),(168,-17,4.8),13),
       ('belfry',(150,5,26),(168,-20,19),15),
       ('spire',(147,6,39),(168,-20,35),30),
       ('side',(124,-36,12),(160,-37,5),36),
       ('roof',(127,-1,62),(168,-41,12),61),('rear',(205,-98,27),(168,-56,8),50)]
for name,pos,target,scale in views:
    c=s.camera;c.location=pos;c.rotation_euler=(Vector(target)-c.location).to_track_quat('-Z','Y').to_euler();c.data.ortho_scale=scale
    s.render.filepath=str(ROOT/'renders'/f'{name}.png');bpy.ops.render.render(write_still=True)
