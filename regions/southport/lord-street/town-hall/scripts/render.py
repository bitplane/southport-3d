from pathlib import Path
import bpy,json,sys,os
from mathutils import Vector
ROOT=Path(__file__).resolve().parents[1];sys.path[:0]=[str(ROOT/'scripts'),str(Path(os.environ['SOUTHPORT_REPO_ROOT'])/'lib')]
from shapes import transform
D=json.loads((ROOT/'research/layout.json').read_text());bpy.ops.wm.open_mainfile(filepath=str(ROOT/'models/building.blend'));s=bpy.context.scene
views=[('front',(14,-100,10),(14,0,7.5),36),('oblique',(-55,-65,45),(14,18,7),65),('roof',(-25,80,90),(14,24,7),65),('north',(-100,26,12),(0,26,6),56),('arcade',(110,26,15),(28,26,6),56),('porch',(14,-35,7),(14,-1,5),15)]
selected=sys.argv[sys.argv.index('--final')+1:]if'--final'in sys.argv else[]
for n,pos,targ,scale in views:
 if selected and n not in selected:continue
 c=s.camera;c.location=transform(D,pos);target=Vector(transform(D,targ));c.rotation_euler=(target-c.location).to_track_quat('-Z','Y').to_euler();c.data.ortho_scale=scale;s.render.filepath=str(ROOT/'renders'/f'{n}.png');bpy.ops.render.render(write_still=True)
