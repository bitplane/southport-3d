from pathlib import Path
import json,math
import bpy
from mathutils import Vector,Matrix
root=Path(__file__).resolve().parents[1]
bpy.ops.wm.open_mainfile(filepath=str(root/'models/post-office-10-18.blend'))
d=json.loads((root/'research/layout.json').read_text());w=d['width']
world=Matrix.Translation((*d['origin_site_xy'],d['base_z']))@Matrix.Rotation(math.radians(d['local_rotation_degrees']),4,'Z')
s=bpy.context.scene;c=s.camera
for name,pos,target,scale in [('front',(w/2,-45,11),(w/2,0,5.5),32),
                              ('corner',(w+18,-21,14),(w*.65,2,5.7),31),
                              ('north',(-16,-20,14),(w*.3,2,5.7),31),
                              ('roof',(w+15,-18,40),(w/2,4,7),38),
                              ('rear',(w/2,35,18),(w/2,5,6),32)]:
    c.location=world@Vector(pos);aim=world@Vector(target)
    c.rotation_euler=(aim-c.location).to_track_quat('-Z','Y').to_euler();c.data.ortho_scale=scale
    s.render.filepath=str(root/'renders'/f'{name}.png');bpy.ops.render.render(write_still=True)
