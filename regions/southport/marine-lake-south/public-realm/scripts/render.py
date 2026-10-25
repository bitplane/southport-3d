"""Bounded plan and obliques; exported neighbourhood reviewed separately."""
from pathlib import Path
import bpy
from mathutils import Vector
ROOT=Path(__file__).resolve().parents[1]
bpy.ops.wm.open_mainfile(filepath=str(ROOT/'models/public-realm.blend'))
s=bpy.context.scene;s.camera.data.clip_end=10000
for name,pos,target,scale in [('plan',(-390,490,1800),(-390,490,0),1100),('oblique',(-1600,-900,1500),(-390,490,0),1300),('lido',(-800,50,300),(-400,390,1),480),('esplanade',(-1000,200,180),(-640,350,2),400)]:
 s.camera.location=pos;s.camera.rotation_euler=(Vector(target)-s.camera.location).to_track_quat('-Z','Y').to_euler();s.camera.data.ortho_scale=scale
 s.render.filepath=str(ROOT/'renders'/(name+'.png'));bpy.ops.render.render(write_still=True)
