"""Apply the reviewed buried footing depth to the existing baked checkpoint."""
import bpy
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
bpy.ops.wm.open_mainfile(filepath=str(ROOT/'models/london-square-exterior.blend'))
count=0
for ob in bpy.context.scene.objects:
    if 'continuous stepped platform' in ob.name:
        for vertex in ob.data.vertices:
            if abs(vertex.co.z)<1e-5:vertex.co.z=-.08;count+=1
        ob.data.update()
floor=bpy.data.objects.get('Inspection studio floor')
if floor:floor.location.z=-.003
bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'models/london-square-exterior.blend'))
print('FOOTING_CONTACT_CORRECTED',count)
