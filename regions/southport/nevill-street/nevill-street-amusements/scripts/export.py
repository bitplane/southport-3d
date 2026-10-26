from pathlib import Path
import bpy
ROOT=Path(__file__).resolve().parents[1]
bpy.ops.wm.open_mainfile(filepath=str(ROOT/'models/nevill-street-amusements.blend'))
bpy.ops.object.select_all(action='DESELECT')
for o in bpy.context.scene.objects:
 if o.type=='MESH':o.select_set(True)
bpy.ops.export_scene.gltf(filepath=str(ROOT/'models/nevill-street-amusements.glb'),export_format='GLB',use_selection=True,export_tangents=True)
