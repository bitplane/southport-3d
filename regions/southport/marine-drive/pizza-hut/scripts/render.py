from pathlib import Path
import os,sys,bpy
from mathutils import Vector
ROOT=Path(__file__).resolve().parents[1];bpy.ops.wm.open_mainfile(filepath=str(ROOT/'models/pizza-hut.blend'));s=bpy.context.scene
sys.path[:0]=[str(Path(os.environ['SOUTHPORT_REPO_ROOT'])/'lib'),str(Path(os.environ['SOUTHPORT_REPO_ROOT'])/'regions/southport/marine-drive/frontage-placeholders/scripts')]
from datum import grade
base=grade(-45.6,660.6)-.25
def point(p):
 x,y,z=p;X=17.4-y*17.4/20.8;Y=x*20.8/17.4
 return Vector((-55.41+.9936*X+.1128*Y,669.959+.1128*X-.9936*Y,base+z))
views=[('entrance-street',(8.7,-26,3.7),(8.7,0,2.6),24),('entrance-close',(7.7,-12,3.2),(7.7,0,2.0),11),('road-side',(-30,10,4.0),(0,10,2.5),26),('service', (8.7,48,4),(8.7,20.8,2.5),24),('roof',(-21,-18,36),(8.7,10.4,3),35)]
selected=sys.argv[sys.argv.index('--final')+1:] if '--final' in sys.argv else []
s.render.resolution_x=1600;s.render.resolution_y=1000
for name,pos,target,scale in views:
 if selected and name not in selected:continue
 c=s.camera;c.location=point(pos);c.rotation_euler=(point(target)-c.location).to_track_quat('-Z','Y').to_euler();c.data.ortho_scale=scale;s.render.filepath=str(ROOT/'renders'/f'{name}.png');bpy.ops.render.render(write_still=True)
