import bpy,os,sys
from pathlib import Path
from mathutils import Vector
ROOT=Path(__file__).resolve().parents[1];REPO=Path(os.environ['SOUTHPORT_REPO_ROOT']);sys.path[:0]=[str(ROOT/'scripts'),str(REPO/'lib')]
from shapes import transform
bpy.ops.wm.open_mainfile(filepath=str(ROOT/'models/marine-way-bridge.blend'));s=bpy.context.scene
views={'overview':((60,-150,90),(78,0,20),185),'north':((80,180,35),(80,0,22),175),'west':((260,60,65),(95,0,24),170),'pylon-head':((65,-25,58),(103.8,0,49),25),'deck-detail':((54,-25,13),(64,0,7),35),'underside':((40,-38,3),(60,0,4),60)}
for name,(pos,target,scale)in views.items():
 s.camera.location=transform(pos);s.camera.rotation_euler=(Vector(transform(target))-s.camera.location).to_track_quat('-Z','Y').to_euler();s.camera.data.ortho_scale=scale;s.render.filepath=str(ROOT/'renders'/f'{name}.png');bpy.ops.render.render(write_still=True)
