from pathlib import Path
import os,sys
ROOT=Path(__file__).resolve().parents[1]
REPO=Path(os.environ['SOUTHPORT_REPO_ROOT'])
sys.path[:0]=[str(REPO/'regions/southport/pier/common'),str(REPO/'lib'),str(REPO/'tools')]
import bpy
from mathutils import Vector
bpy.ops.wm.open_mainfile(filepath=str(ROOT/'models/pier.blend'));s=bpy.context.scene
for name,pos,target,scale in [('overview',(70,-65,50),(30,10,3),105),('underneath',(15,60,-1),(25,20,3),65),('detail',(20,-13,9),(24,13,5),50)]:
 s.camera.location=pos;s.camera.rotation_euler=(Vector(target)-s.camera.location).to_track_quat('-Z','Y').to_euler();s.camera.data.ortho_scale=scale;s.render.filepath=str(ROOT/'renders'/f'{name}.png');bpy.ops.render.render(write_still=True)
