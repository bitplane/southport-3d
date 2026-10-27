from pathlib import Path
import bpy,json,sys
from mathutils import Vector
ROOT=Path(__file__).resolve().parents[1];D=json.loads((ROOT/'research/layout.json').read_text());bpy.ops.wm.open_mainfile(filepath=str(ROOT/'models/building.blend'));s=bpy.context.scene
x,y=D['front_origin'];w=D['front_width'];depth=38 if D['kind']=='bank'else 26;cx=x+w/2
views=[('street',(cx,y-40,2),(cx,y,6.5),max(w+5,23)),('front',(cx,y-100,9),(cx,y,8),max(w+6,23)),('oblique',(cx-40,y-55,35),(cx,y+depth/3,7),max(w+10,depth+7)),('roof',(cx+25,y+depth+45,65),(cx,y+depth/2,7),max(w+15,depth+22)),('rear',(cx,y+depth+100,16),(cx,y+depth/2,7),max(w+8,depth+4))]
if D['kind']=='bank':
 t=(x+D['tower']['width']/2,y+D['tower']['depth']/2,D['floor_z']+12)
 views += [('tower-front-ne',(t[0]+19,t[1]-24,t[2]+18),t,14),('tower-front-sw',(t[0]-19,t[1]-24,t[2]+18),t,14),('tower-rear-ne',(t[0]+19,t[1]+24,t[2]+18),t,14),('tower-roof-neighbourhood',(t[0]+32,t[1]-40,t[2]+30),t,29),('tower-elevation',(t[0],y-80,12.4),(t[0],y,12.4),13.5),('adjoining-roof',(cx+26,y+34,38),(cx,y+4,10),25)]
selected=sys.argv[sys.argv.index('--final')+1:]if'--final'in sys.argv else[]
for name,pos,target,scale in views:
 if selected and name not in selected:continue
 c=s.camera;c.location=pos;c.rotation_euler=(Vector(target)-c.location).to_track_quat('-Z','Y').to_euler();c.data.ortho_scale=scale;(ROOT/'renders').mkdir(exist_ok=True);s.render.filepath=str(ROOT/'renders'/f'{name}.png');bpy.ops.render.render(write_still=True)
