from pathlib import Path
import os,sys
ROOT=Path(__file__).resolve().parents[1]
REPO=Path(os.environ['SOUTHPORT_REPO_ROOT'])
sys.path[:0]=[str(REPO/'regions/southport/pier/common'),str(REPO/'lib'),str(REPO/'tools')]
import bpy
from mathutils import Vector
bpy.ops.wm.open_mainfile(filepath=str(ROOT/'models/pier.blend'));s=bpy.context.scene
for name,pos,target,scale in [('overview',(45,-65,40),(45,0,2),105),('underneath',(45,-35,-1),(45,0,0),55),('detail',(63,-11,8),(60,0,6),19)]:
 s.camera.location=pos;s.camera.rotation_euler=(Vector(target)-s.camera.location).to_track_quat('-Z','Y').to_euler();s.camera.data.ortho_scale=scale;s.render.filepath=str(ROOT/'renders'/f'{name}.png');bpy.ops.render.render(write_still=True)
