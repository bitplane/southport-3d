"""Check the final editable scene after the render process has saved and exited."""
from pathlib import Path
import json
import bpy

ROOT=Path(__file__).resolve().parents[1]
path=ROOT/'models/london-square-exterior.blend'
bpy.ops.wm.open_mainfile(filepath=str(path))
scene=bpy.context.scene
assert scene.unit_settings.system=='METRIC' and scene.unit_settings.scale_length==1
assert scene.camera.name=='Ensemble from NW'
assert bpy.data.objects['Inspection studio floor'].hide_render
assert bpy.data.collections['99 Survey guides — hidden in renders'].hide_render
for c in scene.collection.children:
    if c.name[:2] in ('00','01','02','03','04'):assert not c.hide_render,c.name
feet=[]
for ob in scene.objects:
    if not ob.name.startswith('End elevation pilasters and panel frame'):continue
    z=[v.co.z for v in ob.data.vertices if abs(abs(v.co.y)-1.15)<1e-5]
    assert len(z)==8 and abs(min(z)-.58)<1e-5 and abs(max(z)-.74)<1e-5,ob.name
    feet.append({'object':ob.name,'base_m':min(z),'top_m':max(z)})
assert len(feet)==4,'Corrected end-frame feet missing from saved Blender file'
images=[i for i in bpy.data.images if i.source=='FILE']
assert len(images)==33 and all(i.packed_file for i in images),'Required texture not packed'
weathered={o.data.name for o in scene.objects if o.type=='MESH' and
           o.data.color_attributes.get('Exterior weathering') is not None}
assert len(weathered)==148,'Authored exterior colour data missing from saved scene'
pngs=list((ROOT/'renders').glob('[0-9][0-9]_*.png'))
assert len(pngs)==43 and path.stat().st_mtime_ns>max(p.stat().st_mtime_ns for p in pngs)
report={'status':'passed','corrected_end_frame_feet':feet,'packed_file_images':len(images),
        'weathered_unique_meshes':len(weathered),'metric_scale':1,
        'saved_after_all_43_numbered_pngs':True,'opening_camera':'Ensemble from NW',
        'inspection_floor_and_guides_hidden':True,'all_exterior_groups_visible':True}
(ROOT/'research/saved_scene_check.json').write_text(json.dumps(report,indent=2)+'\n')
print('SAVED_SCENE_VERIFIED',len(feet),'corrected frames',len(images),'packed images',flush=True)
