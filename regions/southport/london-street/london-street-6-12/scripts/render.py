"""Front, side, rear and roof inspection views."""
from pathlib import Path
import bpy
from mathutils import Vector

ROOT=Path(__file__).resolve().parents[1]
bpy.ops.wm.open_mainfile(filepath=str(ROOT/'models/london-street-6-12.blend'))
s=bpy.context.scene
views=[
 ('overview',(15,-79,20),(-19,-52,5.5),32),
 ('front',(17,-52,6),(-10,-52,5.7),25),
 ('shopfront',(8,-54,4),(-10,-54,2.5),20),
 ('upper-windows',(0,-55,8),(-10,-55,7.0),12),
 ('glebe-side',(-11,-83,12),(-20,-63,5.2),23),
 ('rear',(-48,-56,11),(-26,-52,5.7),26),
 ('roof',(-38,-73,31),(-20,-53,8),29),
]
for name,position,target,scale in views:
    camera=s.camera
    camera.location=position
    camera.rotation_euler=(Vector(target)-camera.location).to_track_quat('-Z','Y').to_euler()
    camera.data.ortho_scale=scale
    s.render.filepath=str(ROOT/'renders'/(name+'.png'))
    bpy.ops.render.render(write_still=True)
