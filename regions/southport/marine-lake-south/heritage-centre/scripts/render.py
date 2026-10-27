import json
from pathlib import Path
import bpy
from mathutils import Vector
R=Path(__file__).resolve().parents[1];D=json.loads((R/'research/layout.json').read_text());(ox,oy)=D['origin_site_xy'];(ux,uy)=D['x_axis_site'];(vx,vy)=D['y_axis_site'];g=D['ground_datum_m']
def P(x,y,z):return (ox+ux*x+vx*y,oy+uy*x+vy*y,g+z)
bpy.ops.wm.open_mainfile(filepath=str(R/'models/heritage-centre.blend'));s=bpy.context.scene
for name,pos,target,scale in [('front',(0,40,1.7),(0,0,2.0),27),('front-oblique',(26,30,15),(0,0,2.4),33),('side',(35,2,11),(0,0,2),28),('rear',(-25,-30,16),(0,-2,2),34),('roof',(18,-24,30),(0,-1,2),30),('entry',(0,19,1.7),(0,6.5,2.6),11)]:
 s.camera.data.type='ORTHO';s.camera.location=P(*pos);s.camera.rotation_euler=(Vector(P(*target))-s.camera.location).to_track_quat('-Z','Y').to_euler();s.camera.data.ortho_scale=scale;s.render.filepath=str(R/'renders'/(name+'.png'));bpy.ops.render.render(write_still=True)
