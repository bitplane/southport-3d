from pathlib import Path
import bpy
ROOT=Path(__file__).resolve().parents[1]
bpy.ops.wm.open_mainfile(filepath=str(ROOT/'models/lord-street-377-385.blend'))
bpy.ops.object.select_all(action='DESELECT')
for o in bpy.context.scene.objects:o.select_set(o.type=='MESH')
bpy.ops.export_scene.gltf(filepath=str(ROOT/'models/lord-street-377-385.glb'),export_format='GLB',use_selection=True,export_tangents=True)
