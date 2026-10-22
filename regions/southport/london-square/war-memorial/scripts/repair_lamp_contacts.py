"""Apply the checkpoint0.3 lamp footing correction to an already baked scene."""
import bpy
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
bpy.ops.wm.open_mainfile(filepath=str(ROOT/'models/london-square-exterior.blend'))
plinths=[o for o in bpy.data.objects if o.name.startswith('Bromsgrove lamp stone plinth')]
assert len(plinths)==8
changed=0
for obj in plinths:
    for v in obj.data.vertices:
        if abs(v.co.z-.08)<.0001:v.co.z=-.01;changed+=1
    obj.data.update()
    obj['ground_contact']='Footing reaches 10 mm below provisional ground datum; no unsupported lower edge'
assert changed in (0,32),changed
bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'models/london-square-exterior.blend'))
print('LAMP_CONTACT_REPAIRED',len(plinths),'plinths;',changed,'vertices',flush=True)
