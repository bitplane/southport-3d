"""Test removal of overlapping parapet end stones; do not save the scene."""
from pathlib import Path
import bpy
ROOT=Path(__file__).resolve().parents[1]
bpy.ops.wm.open_mainfile(filepath=str(ROOT/'models/london-square-exterior.blend'))
scene=bpy.context.scene;changed=0
for ob in scene.objects:
    if 'flat parapet fascia' not in ob.name:continue
    verts=ob.data.vertices
    for start in range(0,len(verts),8):
        group=verts[start:start+8]
        xs=[v.co.x for v in group]
        if max(xs)-min(xs)<.31 and abs(sum(xs)/len(xs))>11.8:
            for v in group:
                yy=max(-2.108,min(2.108,v.co.y))
                if abs(yy-v.co.y)>1e-6:v.co.y=yy;changed+=1
for c in scene.collection.children:
    if c.name[:2] in ('00','01','03','99'):c.hide_render=True
floor=bpy.data.objects.get('Inspection studio floor')
if floor:floor.hide_render=False
scene.camera=bpy.data.objects['NE victory end'];scene.cycles.samples=48
scene.render.resolution_x=1600;scene.render.resolution_y=1000
scene.render.filepath=str(ROOT/'renders/studies/parapet-corner-joints.png')
bpy.ops.render.render(write_still=True)
print('PARAPET_CORNER_STUDY_COMPLETE',changed,flush=True)
