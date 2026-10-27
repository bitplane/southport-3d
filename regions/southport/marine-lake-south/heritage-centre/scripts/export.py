from pathlib import Path
import bpy
R=Path(__file__).resolve().parents[1]
bpy.ops.wm.open_mainfile(filepath=str(R/'models/heritage-centre.blend'))
bpy.ops.object.select_all(action='DESELECT')
for o in bpy.data.collections['building'].all_objects:
 if o.type=='MESH':o.select_set(True)
bpy.ops.export_scene.gltf(filepath=str(R/'models/heritage-centre.glb'),export_format='GLB',use_selection=True,export_tangents=True)
