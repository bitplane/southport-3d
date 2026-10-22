"""Check flat plateau normals on the coat of arms without saving the scene."""
from pathlib import Path
import bpy,json
ROOT=Path(__file__).resolve().parents[1]
bpy.ops.wm.open_mainfile(filepath=str(ROOT/'models/london-square-exterior.blend'))
scene=bpy.context.scene
arms=next(o for o in scene.objects if o.name.startswith('Southport arms — traced continuous surface'))
fixed=0
for p in arms.data.polygons:
    z=[arms.data.vertices[i].co.z for i in p.vertices]
    if p.use_smooth and p.normal.z>.9999 and max(z)-min(z)<.00008:
        p.use_smooth=False;fixed+=1
for c in scene.collection.children:
    if c.name[:2] in ('00','02','03','99'):c.hide_render=True
scene.camera=bpy.data.objects['Obelisk coat of arms']
scene.cycles.samples=48
scene.render.resolution_x=1600;scene.render.resolution_y=1000
scene.render.filepath=str(ROOT/'renders/studies/arms-flat-plateaus.png')
bpy.ops.render.render(write_still=True)
(ROOT/'research/arms-normal-study.json').write_text(json.dumps({'flat_plateau_faces_changed':fixed,'height_tolerance_m':.00008,'minimum_normal_z':.9999},indent=2)+'\n')
print('ARMS_NORMAL_STUDY_COMPLETE',fixed,flush=True)
